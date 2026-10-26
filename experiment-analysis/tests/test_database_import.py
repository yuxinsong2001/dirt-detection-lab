"""Real input fixtures exercise provenance, isolation and import failure behavior."""
import csv
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiment_analysis import importing
from experiment_analysis.database import connect, counts

ROOT = Path(__file__).resolve().parents[1]


class DatabaseImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'module'
        self.db = Path(self.temp.name) / 'records.sqlite'
        names = ['data/reference/yolo26-official-benchmark-2026-10-24.json',
                 'reports/official/performance-n-s-2026-10-24/performance_summary.csv']
        names += [f'reports/official/yolo26{model}-v8.4.0/{name}.json'
                  for model in ('n', 's') for name in ('source', 'training_config', 'saved_metrics', 'checkpoint_metadata')]
        for name in names:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def run_import(self):
        return importing.import_records(self.root, self.db)

    def edit_json(self, relative, change):
        path = self.root / relative
        data = json.loads(path.read_text(encoding='utf-8'))
        change(data)
        path.write_text(json.dumps(data), encoding='utf-8')

    def test_real_data_and_repeated_import(self):
        result = self.run_import()
        self.assertEqual(result['totals'], dict(models=2, sources=3, evaluation_conditions=7, measurements=34, training_configs=2))
        self.assertEqual(set(self.run_import()['inserted'].values()), {0})
        con = connect(self.db)
        self.addCleanup(con.close)
        self.assertEqual(con.execute('PRAGMA foreign_keys').fetchone()[0], 1)
        self.assertEqual(con.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(), [])
        self.assertEqual(con.execute("SELECT COUNT(*) FROM evaluation_conditions WHERE purpose='latency' AND batch_size IS NULL AND precision IS NULL").fetchone()[0], 2)
        self.assertEqual(con.execute("SELECT COUNT(*) FROM measurements m JOIN evaluation_conditions c ON m.condition_id=c.id WHERE c.detection_mode='unverified' AND m.metric_name='map50_95' AND m.unit='ratio'").fetchone()[0], 2)
        self.assertEqual(sum(len(json.loads(r[0])) for r in con.execute('SELECT config_json FROM training_configs')), 226)
        # SQL acceptance check: accuracy and latency must share model, source and mode.
        selected = con.execute("""SELECT model.name, a.raw_value, l.raw_value FROM measurements a
        JOIN evaluation_conditions ac ON ac.id=a.condition_id
        JOIN sources s ON s.id=ac.source_id
        JOIN models model ON model.id=a.model_id
        JOIN measurements l ON l.model_id=a.model_id
        JOIN evaluation_conditions lc ON lc.id=l.condition_id AND lc.source_id=ac.source_id
          AND lc.detection_mode=ac.detection_mode AND lc.image_size_px=ac.image_size_px
        WHERE s.source_kind='published_transcription' AND ac.purpose='accuracy'
          AND ac.detection_mode='end_to_end' AND a.metric_name='map50_95' AND a.unit='percent'
          AND a.raw_value>=45 AND lc.purpose='latency' AND lc.hardware='NVIDIA T4'
          AND lc.backend='TensorRT10' AND l.metric_name='latency' AND l.unit='ms' AND l.raw_value<=3""").fetchall()
        self.assertEqual([tuple(row) for row in selected], [('YOLO26s', 47.8, 2.5)])
        self.assertIn('source_url', json.loads(con.execute("SELECT evidence_json FROM sources WHERE source_kind='published_transcription'").fetchone()[0]))

    def test_invalid_values_rejected_before_database_creation(self):
        relative = 'data/reference/yolo26-official-benchmark-2026-10-24.json'
        original = (self.root / relative).read_text(encoding='utf-8')
        for value in (True, -1, float('nan'), 101):
            (self.root / relative).write_text(original, encoding='utf-8')
            self.edit_json(relative, lambda data: data['models'][0].update(map50_95_e2e_pct=value))
            with self.assertRaises(ValueError): self.run_import()
            self.assertFalse(self.db.exists())

    def test_csv_disagreement(self):
        self.edit_json('data/reference/yolo26-official-benchmark-2026-10-24.json', lambda data: data['models'][0].update(map50_95_e2e_pct=41))
        with self.assertRaisesRegex(ValueError, 'CSV/JSON mismatch'): self.run_import()
        self.assertFalse(self.db.exists())

    def test_mode_and_units_rejected(self):
        relative = 'data/reference/yolo26-official-benchmark-2026-10-24.json'
        original = (self.root / relative).read_text(encoding='utf-8')
        for change in (dict(latency_head='standard'), dict(map_unit='ratio'), dict(timing_batch_size=True)):
            (self.root / relative).write_text(original, encoding='utf-8')
            self.edit_json(relative, lambda data: data.update(change))
            with self.assertRaises(ValueError): self.run_import()
        self.assertFalse(self.db.exists())

    def test_checkpoint_model_mismatch(self):
        self.edit_json('reports/official/yolo26s-v8.4.0/source.json', lambda data: data.update(asset_name='yolo26n.pt'))
        with self.assertRaisesRegex(ValueError, 'identity mismatch'): self.run_import()
        self.assertFalse(self.db.exists())

    def test_new_dated_source_coexists(self):
        self.run_import()
        self.edit_json('data/reference/yolo26-official-benchmark-2026-10-24.json', lambda data: data.update(accessed_date='2026-10-25'))
        path = self.root / 'reports/official/performance-n-s-2026-10-24/performance_summary.csv'
        path.write_text(path.read_text(encoding='utf-8-sig').replace('2026-10-24', '2026-10-25'), encoding='utf-8')
        result = self.run_import()
        self.assertEqual(result['inserted'], dict(models=0, sources=1, evaluation_conditions=5, measurements=12, training_configs=0))
        self.assertEqual(set(self.run_import()['inserted'].values()), {0})

    def test_mid_import_failure_rolls_back_schema_and_rows(self):
        original = importing.ensure_row
        def fail(connection, table, identity, values):
            if table == 'measurements': raise RuntimeError('injected failure')
            return original(connection, table, identity, values)
        with patch.object(importing, 'ensure_row', side_effect=fail):
            with self.assertRaisesRegex(RuntimeError, 'injected'): self.run_import()
        con = connect(self.db)
        self.assertEqual(con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(), [])
        self.assertEqual(con.execute('PRAGMA user_version').fetchone()[0], 0)
        con.close()
        self.assertEqual(self.run_import()['totals']['measurements'], 34)

    def test_conflicting_existing_metric_rolls_back(self):
        self.run_import()
        con = connect(self.db)
        con.execute('UPDATE measurements SET raw_value=0.123 WHERE id=1')
        before = counts(con)
        con.close()
        with self.assertRaisesRegex(ValueError, 'conflicts'): self.run_import()
        con = connect(self.db)
        self.assertEqual(counts(con), before)
        self.assertEqual(con.execute('SELECT raw_value FROM measurements WHERE id=1').fetchone()[0], 0.123)
        con.close()

    def test_failure_preserves_preexisting_snapshot(self):
        self.run_import()
        self.edit_json('data/reference/yolo26-official-benchmark-2026-10-24.json', lambda data: data.update(accessed_date='2026-10-25'))
        path = self.root / 'reports/official/performance-n-s-2026-10-24/performance_summary.csv'
        path.write_text(path.read_text(encoding='utf-8-sig').replace('2026-10-24', '2026-10-25'), encoding='utf-8')
        original = importing.ensure_row
        def fail(connection, table, identity, values):
            if table == 'measurements': raise RuntimeError('injected failure')
            return original(connection, table, identity, values)
        with patch.object(importing, 'ensure_row', side_effect=fail):
            with self.assertRaises(RuntimeError): self.run_import()
        con = connect(self.db)
        self.assertEqual(counts(con), dict(models=2, sources=3, evaluation_conditions=7, measurements=34, training_configs=2))
        self.assertEqual(con.execute("SELECT COUNT(*) FROM sources WHERE observed_date='2026-10-25'").fetchone()[0], 0)
        con.close()

    def test_unrelated_database_untouched(self):
        con = sqlite3.connect(self.db)
        con.execute('CREATE TABLE unrelated(value)')
        con.commit()
        con.close()
        with self.assertRaisesRegex(ValueError, 'Unrecognized'): self.run_import()
        con = sqlite3.connect(self.db)
        self.assertEqual(con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(), [('unrelated',)])
        con.close()


if __name__ == '__main__':
    unittest.main()
