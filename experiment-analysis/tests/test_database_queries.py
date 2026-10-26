"""Query real imported records and adversarial condition combinations."""
import contextlib
import hashlib
import io
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiment_analysis.cli import query_main
from experiment_analysis.importing import import_records
from experiment_analysis.queries import filter_models, list_models, model_details, open_readonly

ROOT = Path(__file__).resolve().parents[1]


class DatabaseQueryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.db = self.base / 'records.sqlite'
        import_records(ROOT, self.db)

    def select(self, **kwargs):
        return filter_models(self.db, **dict(min_map=45, max_latency_ms=3, **kwargs))

    def change(self, sql, params=()):
        with contextlib.closing(sqlite3.connect(self.db)) as con, con:
            con.execute(sql, params)

    def test_list_and_source_aware_details(self):
        self.assertEqual([r['name'] for r in list_models(self.db)], ['YOLO26n', 'YOLO26s'])
        details = model_details(self.db, 'YOLO26s')
        self.assertEqual(len(details['measurements']), 17)
        self.assertEqual(len(details['sources']), 2)
        config = details['training_configs'][0]
        self.assertEqual(config['source_kind'], 'checkpoint')
        self.assertEqual(len(config['config']), 113)
        self.assertEqual(config['config']['epochs'], 70)
        raw = [r for r in details['measurements'] if r['metric_name'] == 'map50_95' and r['source_kind'] == 'checkpoint'][0]
        self.assertEqual((raw['raw_value'], raw['unit'], raw['detection_mode']), (0.47769, 'ratio', 'unverified'))
        self.assertTrue(all(s['input_manifest'] and s['evidence'] for s in details['sources']))

    def test_expected_filter_and_nulls(self):
        rows = self.select()
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual((row['model'], row['map50_95_pct'], row['latency_ms']), ('YOLO26s', 47.8, 2.5))
        self.assertEqual(row['source_date'], '2026-10-24')
        self.assertEqual(row['unknown_conditions'], ['batch_size', 'precision'])
        self.assertEqual(row['backend'], 'TensorRT10')
        self.assertTrue(row['source_key'] and row['source_url'] and row['timing_scope'])

    def test_no_matches_and_device_isolation(self):
        self.assertEqual(filter_models(self.db, min_map=99, max_latency_ms=3), [])
        self.assertEqual(self.select(device='cpu'), [])
        cpu = filter_models(self.db, min_map=45, max_latency_ms=100, device='cpu')
        self.assertEqual(cpu[0]['latency_ms'], 87.2)
        self.assertIn('hardware', cpu[0]['unknown_conditions'])

    def test_standard_and_unverified_never_substitute(self):
        self.assertEqual(self.select(mode='standard'), [])
        self.change("UPDATE measurements SET raw_value=10 WHERE unit='percent' AND condition_id IN (SELECT id FROM evaluation_conditions WHERE detection_mode='end_to_end')")
        self.assertEqual(self.select(), [])  # Neither standard scores nor checkpoint scores can rescue this.

    def test_source_isolation(self):
        self.change("UPDATE evaluation_conditions SET source_id=(SELECT id FROM sources WHERE source_kind='checkpoint' LIMIT 1) WHERE purpose='latency' AND backend='TensorRT10'")
        self.assertEqual(self.select(), [])

    def test_image_size_isolation(self):
        self.change("UPDATE evaluation_conditions SET image_size_px=1280 WHERE purpose='latency'")
        self.assertEqual(self.select(), [])

    def test_mode_isolation(self):
        self.change("UPDATE evaluation_conditions SET detection_mode='standard' WHERE purpose='latency'")
        self.assertEqual(self.select(), [])

    def test_dates_and_source_key_are_explicit(self):
        # Add a second real evidence snapshot through the importer.
        fixture = self.base / 'module'
        with contextlib.closing(sqlite3.connect(self.db)) as con, con:
            manifests = [json.loads(row[0]) for row in con.execute('SELECT input_manifest_json FROM sources')]
        paths = [entry['path'] for manifest in manifests for entry in manifest]
        paths += ['reports/official/performance-n-s-2026-10-24/performance_summary.csv']
        for relative in paths:
            target = fixture / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        ref = fixture / 'data/reference/yolo26-official-benchmark-2026-10-24.json'
        doc = json.loads(ref.read_text(encoding='utf-8'))
        doc['accessed_date'] = '2026-10-25'
        ref.write_text(json.dumps(doc), encoding='utf-8')
        csv = fixture / paths[-1]
        csv.write_text(csv.read_text(encoding='utf-8-sig').replace('2026-10-24','2026-10-25'), encoding='utf-8')
        import_records(fixture, self.db)
        self.assertEqual(len(self.select()), 2)  # No implicit latest-source choice.
        chosen = self.select(source_date='2026-10-25')
        self.assertEqual(len(chosen), 1)
        self.assertEqual(self.select(source_key=chosen[0]['source_key']), chosen)
        self.assertEqual(self.select(source_date='2026-10-26'), [])

    def test_invalid_thresholds(self):
        for minimum in (-1, 101, float('nan'), float('inf'), True, '45'):
            with self.assertRaises(ValueError): filter_models(self.db, min_map=minimum, max_latency_ms=3)
        for maximum in (0, -1, float('nan'), float('inf'), True):
            with self.assertRaises(ValueError): filter_models(self.db, min_map=45, max_latency_ms=maximum)
        with self.assertRaises(ValueError): self.select(source_date='tomorrow')

    def test_missing_or_unrelated_database(self):
        missing = self.base / 'absent.sqlite'
        with self.assertRaises(ValueError): list_models(missing)
        self.assertFalse(missing.exists())
        unrelated = self.base / 'unrelated.sqlite'
        with contextlib.closing(sqlite3.connect(unrelated)) as con, con: con.execute('CREATE TABLE other(x)')
        with self.assertRaises(ValueError): list_models(unrelated)

    def test_model_not_found_and_parameter_binding(self):
        with self.assertRaisesRegex(ValueError, 'not found'): model_details(self.db, "' OR 1=1 --")
        self.assertEqual(self.select(source_key="' OR 1=1 --"), [])

    def test_readonly_and_unchanged_bytes(self):
        before = hashlib.sha256(self.db.read_bytes()).hexdigest()
        with open_readonly(self.db) as con:
            with self.assertRaises(sqlite3.OperationalError): con.execute('DELETE FROM models')
        list_models(self.db)
        model_details(self.db, 'YOLO26s')
        self.select()
        self.assertEqual(hashlib.sha256(self.db.read_bytes()).hexdigest(), before)

    def test_cli_commands_and_clear_failure(self):
        for command in (['list'], ['show', 'YOLO26s'], ['filter','--min-map','45','--max-latency-ms','3']):
            output = io.StringIO()
            with contextlib.redirect_stdout(output): query_main(['--database',str(self.db),*command])
            self.assertTrue(json.loads(output.getvalue()))
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                query_main(['--database',str(self.db),'filter','--min-map','-1','--max-latency-ms','3'])
        self.assertEqual(error.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
