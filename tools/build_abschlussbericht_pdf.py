from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, FrameBreak, Frame, PageTemplate

OUT = "output/pdf/Abschlussbericht_DirtNet_IEEE_final.pdf"
ACCENT = colors.black

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleGreen", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=21, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=7))
styles.add(ParagraphStyle(name="SubTitle", parent=styles["Normal"], fontSize=9, leading=11, alignment=TA_CENTER, textColor=colors.black, spaceAfter=7))
styles.add(ParagraphStyle(name="H1G", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=ACCENT, alignment=TA_CENTER, spaceBefore=6, spaceAfter=4))
styles.add(ParagraphStyle(name="H2G", parent=styles["Heading2"], fontName="Helvetica-Oblique", fontSize=9, leading=11, textColor=colors.black, spaceBefore=5, spaceAfter=3))
styles.add(ParagraphStyle(name="BodyG", parent=styles["BodyText"], fontName="Times-Roman", fontSize=8.2, leading=9.6, spaceAfter=4, alignment=4))
styles.add(ParagraphStyle(name="SmallG", parent=styles["BodyText"], fontName="Times-Roman", fontSize=6.8, leading=8, textColor=colors.black))

def p(text, style="BodyG"):
    return Paragraph(text, styles[style])

def table(data, widths):
    max_width = 84*mm
    if sum(widths) > max_width:
        factor = max_width / sum(widths)
        widths = [x * factor for x in widths]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E6E6E6")), ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 7.6), ("LEADING", (0,0), (-1,-1), 9.2),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#777777")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t

def header_footer(canvas, doc):
    canvas.saveState(); w, h = A4
    canvas.setFont("Helvetica", 7); canvas.setFillColor(colors.black)
    canvas.drawCentredString(w/2, 10*mm, str(doc.page))
    canvas.restoreState()

story = [p("DirtNet: Visuelle Schmutz- und Objekterkennung<br/>für autonome Reinigungsroboter", "TitleGreen"),
         p("Shufang Tao (3824652) · Yuxin Song (3820779) · Yuyang Ren (3762594)", "SubTitle"),
         p("<b>Abstract—</b> Das Projekt untersucht die bodennahe Erkennung von Schmutz und typischen Bürogegenständen auf Basis der YOLO-Familie. Ausgehend von einer YOLOv3-Reproduktion wurde eine systematische Versuchsreihe bis zu YOLO11 durchgeführt. Die stärksten synthetischen Validierungsergebnisse werden auf realen Bildern deutlich unterschritten. Für die binäre Aufgabe wird deshalb YOLO11s als praxisnahes Modell empfohlen; für die Zehnklassenaufgabe bleibt das erste YOLO11m-Modell der belastbarste Ausgangspunkt."),
         p("<b>Index Terms—</b> Objekterkennung, DirtNet, YOLO11, autonome Reinigungsroboter, Domain Shift", "SmallG"), FrameBreak(),
         p("I. EINLEITUNG UND MOTIVATION", "H1G"),
         p("Autonome Reinigungsroboter müssen nicht nur Hindernisse erkennen, sondern auch kleine, unregelmäßige und kontrastarme Verschmutzungen lokalisieren. Schmutz besitzt keine stabile Form; Reflexionen und Bodenstrukturen erzeugen ähnliche Bildmuster, und die Kameraperspektive liegt nahe am Boden. Ziel des Projekts war eine reproduzierbare Detektionspipeline für <i>dirt</i> und Büroobjekte sowie die Untersuchung, wie Modellgröße, Auflösung, Optimierer und Datendomäne die Generalisierung beeinflussen."),
         p("II. LITERATUR UND GRUNDLAGEN", "H1G"),
         p("Die fachliche Referenz ist <i>DirtNet: Visual Dirt Detection for Autonomous Cleaning Robots</i> (ICRA 2020). Methodisch basiert die Implementierung auf Ultralytics YOLOv3 und YOLO11. Bewertet wird mit Precision, Recall, mAP@0.5 und mAP@0.5:0.95. Während mAP@0.5 grobe korrekte Lokalisierungen belohnt, reagiert mAP@0.5:0.95 stärker auf ungenaue Boxen. Für den Roboterbetrieb sind zusätzlich Laufzeit, Fehlalarmrate und der Anteil übersehener Verschmutzungen relevant."),
         p("III. KONZEPT, METHODEN UND IMPLEMENTIERUNG", "H1G"),
         p("Die Arbeit gliedert sich in eine binäre Aufgabe (<i>dirt</i> gegenüber <i>object</i>) und eine Zehnklassenaufgabe mit Schmutz sowie neun Büroobjektklassen. Für Multiclass wurden 860 synthetische Trainingsbilder mit 8.626 Instanzen, 296 synthetische Validierungsbilder mit 2.962 Instanzen und 80 ausschließlich zum Testen verwendete reale Bilder mit 644 Instanzen eingesetzt. Die Klassenverteilung ist unausgeglichen: <i>dirt</i> dominiert mit 5.161 Trainingsinstanzen, während <i>scissors</i> nur 114 Instanzen besitzt."),
         table([["Split","Bilder","Instanzen","Verwendung"],["Train (synthetisch)","860","8.626","Parameterlernen"],["Validation (synthetisch)","296","2.962","Checkpoint-Auswahl"],["test_real_new","80","644","unabhängiger Realtest"]],[50*mm,25*mm,30*mm,55*mm]), Spacer(1,3*mm),
         p("Die Daten wurden in YOLO-Annotationen konvertiert und über YAML-Dateien reproduzierbar eingebunden. Das formale Multiclass-Basismodell ist YOLO11m mit COCO-Vortraining, Eingabegröße 1024, Batchgröße 2, 30 Epochen, AMP und deterministischem Seed 0. Trainiert wurde auf einer RTX 3060 Laptop GPU mit 6 GB. Für die binären Endkandidaten wurden YOLO11s und YOLO11m bei 1280 Pixeln, SGD und 30 Epochen verglichen."),
         p("IV. EXPERIMENTE UND AUSWERTUNG", "H1G"), p("A. Binäre Detektion", "H2G"),
         p("Auf der Validierung erreicht YOLO11m 97,4 % Precision, 96,2 % Recall, 98,3 % mAP50 und 92,3 % mAP50-95. Auf dem unabhängigen Realtest kehrt sich die Rangfolge um: YOLO11s erzielt 80,6 % mAP50 und 56,2 % mAP50-95 bei etwa 10 ms Inferenzzeit, YOLO11m nur 77,8 % beziehungsweise 53,2 % bei 21,4 ms. YOLO11m ist präziser, übersieht aber mehr Ziele. Für den praktischen Einsatz wird daher YOLO11s empfohlen."),
         table([["Modell / Split","P","R","mAP50","mAP50-95","ms/Bild"],["YOLO11s / Realtest","0,781","0,772","0,806","0,562","10,0"],["YOLO11m / Realtest","0,835","0,704","0,778","0,532","21,4"]],[48*mm,20*mm,20*mm,25*mm,27*mm,24*mm]),
         p("B. Multiclass-Basismodell", "H2G"),
         p("Das YOLO11m-Basismodell benötigte rund 84,1 Minuten. Der beste Checkpoint entstand in Epoche 29 und erreicht auf der synthetischen Validierung 0,9535 Precision, 0,9305 Recall, 0,9608 mAP50 und 0,8136 mAP50-95. Auf realen Bildern fallen die Werte deutlich. Der mAP50-Rückgang beträgt 0,224, bei mAP50-95 sogar 0,260."),
         table([["Split","Precision","Recall","mAP50","mAP50-95"],["Synthetische Validierung","0,953","0,930","0,961","0,814"],["Realer Test","0,665","0,776","0,737","0,554"],["Absolute Abnahme","0,288","0,154","0,224","0,260"]],[55*mm,27*mm,27*mm,27*mm,30*mm]), Spacer(1,3*mm),
         p("Besonders robust sind <i>pens</i> (mAP50 0,986) und <i>scissors</i> (0,922). Schwach sind <i>other</i> (0,404), <i>rulers</i> (0,490) und <i>usb_sticks</i> (0,520). Für <i>dirt</i> werden 0,852 Precision, 0,706 Recall und 0,773 mAP50 gemessen; ungefähr 29 % der realen Schmutzinstanzen bleiben unerkannt."),
         p("C. Fine-Tuning, Modellgröße und Laufzeit", "H2G"),
         p("Ein zusätzliches AdamW-Fine-Tuning über 15 Epochen steigerte alle synthetischen Kennzahlen, verschlechterte auf dem Realtest aber Recall (0,776 auf 0,721) und mAP50 (0,737 auf 0,726). Das bestätigt, dass weitere Optimierung auf derselben synthetischen Verteilung das Domänenproblem nicht löst."),
         table([["Multiclass-Modell","P","R","mAP50","mAP50-95"],["Baseline, Realtest","0,665","0,776","0,737","0,554"],["Fine-Tuning, Realtest","0,726","0,721","0,726","0,557"]],[62*mm,25*mm,25*mm,27*mm,30*mm]), Spacer(1,3*mm),
         p("Bei YOLOv8 steigt der Validierungs-mAP50-95 mit der Modellgröße von 0,710 (Nano) über 0,796 (Small) auf 0,813 (Medium); zugleich steigt die Trainingszeit von 11,6 auf 169,7 Minuten. Mehr Kapazität hilft innerhalb der Validierungsdomäne, ist aber kein Ersatz für reale Trainingsdaten."),
         table([["YOLOv8","mAP50-95","Training"],["Nano","0,710","11,6 min"],["Small","0,796","78,6 min"],["Medium","0,813","169,7 min"]],[55*mm,45*mm,50*mm]), Spacer(1,3*mm),
         p("Das Multiclass-YOLO11m benötigt insgesamt etwa 33,2 ms pro Bild und erreicht damit ungefähr 30 FPS. Eine ruhige Kameraführung und kurze Stopps in Objektnähe verbesserten im Video-Demo die Stabilität; starke Drehungen erzeugten Bewegungsunschärfe."),
         p("D. Einordnung und Grenzen", "H2G"),
         p("Die zentrale Fehlerquelle ist der Domänenunterschied: reale Bilder enthalten schlechte Beleuchtung, Reflexionen, Sensorrauschen, Kratzer und Materialvarianten, die in den synthetischen Daten nicht ausreichend vorkommen. Zudem enthält der Realtest keine leeren Bodenbilder. Die Fehlalarmrate im kontinuierlichen Betrieb kann daher nicht belastbar angegeben werden. Die 80 Testbilder dürfen nicht für Training oder Hyperparameterwahl wiederverwendet werden, solange kein neuer unabhängiger Realtest vorliegt."),
         FrameBreak(), p("V. ZUSAMMENFASSUNG UND AUSBLICK", "H1G"),
         p("Das Projekt liefert eine reproduzierbare YOLO-Pipeline, umfangreiche Modellvergleiche und einen echtbildbasierten Generalisierungstest. Für die binäre Praxisanwendung ist YOLO11s der beste Kompromiss aus Recall, mAP und Geschwindigkeit. Für Multiclass bleibt das erste YOLO11m-Modell der empfohlene Baseline-Checkpoint; das Fine-Tuning wurde wegen schlechterer Realtest-Balance verworfen."),
         p("Die wichtigste nächste Maßnahme ist nicht ein größeres Modell, sondern ein getrenntes reales Trainings- und Validierungsset. Ergänzend sollten schwierige Negativbilder, mehr Beispiele schwacher Klassen, Beleuchtungs- und Rauschaugmentation, eine klarere Definition der Klasse <i>other</i> sowie schwellenwertabhängige Tests auf sauberen Böden aufgenommen werden."),
         p("REFERENCES", "H1G"),
         p("[1] Bormann et al.: <i>DirtNet: Visual Dirt Detection for Autonomous Cleaning Robots</i>, ICRA 2020.<br/>[2] Ultralytics YOLOv3 Community Implementation und Ultralytics YOLO11.<br/>[3] Projekt-Repository: https://github.com/ipa-robotics-courses/2026_p02_dirt_detection, Stand Commit 69bb7c9.<br/>[4] Interne Ergebnisdokumente: yolo11_final_experiment_summary.md, yolo11_multiclass_training_summary.md, yolo11_multiclass_real_test_analysis.md und yolo11_multiclass_finetuning_analysis.md.", "SmallG")]

doc = BaseDocTemplate(OUT, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=14*mm, bottomMargin=16*mm, title="Abschlussbericht DirtNet", author="Shufang Tao, Yuxin Song, Yuyang Ren")
w, h = A4; gap = 5*mm; usable = w-32*mm; col = (usable-gap)/2
title_frame = Frame(16*mm, h-70*mm, usable, 55*mm, id="title", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
lower_h = h-86*mm
first_left = Frame(16*mm, 16*mm, col, lower_h, id="first_left", leftPadding=0, rightPadding=2*mm, topPadding=0, bottomPadding=0)
first_right = Frame(16*mm+col+gap, 16*mm, col, lower_h, id="first_right", leftPadding=2*mm, rightPadding=0, topPadding=0, bottomPadding=0)
left = Frame(16*mm, 16*mm, col, h-30*mm, id="left", leftPadding=0, rightPadding=2*mm, topPadding=0, bottomPadding=0)
right = Frame(16*mm+col+gap, 16*mm, col, h-30*mm, id="right", leftPadding=2*mm, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="First", frames=[title_frame, first_left, first_right], onPage=header_footer, autoNextPageTemplate="IEEE"), PageTemplate(id="IEEE", frames=[left,right], onPage=header_footer)])
doc.build(story)
print(OUT)
