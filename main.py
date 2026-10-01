import streamlit as st
import json
from pathlib import Path
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle

#125 char only for tätigkeiten, 10 char datum, 100 char bemerkung

# Eingaben zwischenspeichern
SPEICHER_DATEI = Path(__file__).parent / "gespeicherte_eingaben.json"

FELDER = ["lehrlingName", "kalenderwoche", "vomDatum", "bisDatum", "gruppe", "trainer"]
for i in range(1, 6):
    FELDER += [f"datum{i}", f"trainer{i}", f"tätigkeit{i}", f"bemerkungen{i}"]

def eingabenSpeichern():
    daten = {feld: st.session_state.get(feld, "") for feld in FELDER}
    SPEICHER_DATEI.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")

def eingabenLöschen():
    SPEICHER_DATEI.unlink(missing_ok=True)
    for feld in FELDER:
        st.session_state[feld] = ""

# Gespeicherte Eingaben beim Start einmal laden
if "geladen" not in st.session_state:
    st.session_state["geladen"] = True
    if SPEICHER_DATEI.exists():
        gespeichert = json.loads(SPEICHER_DATEI.read_text(encoding="utf-8"))
        for feld in FELDER:
            st.session_state[feld] = gespeichert.get(feld, "")

col1, col2, col3 = st.columns([1,4,1])

# Titel
with col2:
    st.title("Ausbildungstagebuch")

col1, col2, col3, col4 = st.columns(4)

# Allgemeine Informationen
with col1:
    lehrlingName = st.text_input("Lehrling: ", key="lehrlingName")
with col2:
    kalenderwoche = st.text_input("Kalenderwoche: ", key="kalenderwoche")
with col3:
    vomDatum = st.text_input("Vom: ", max_chars=10, key="vomDatum")
with col4:
    bisDatum = st.text_input("Bis: ", max_chars=10, key="bisDatum")
col1, col2 = st.columns(2)
with col1:
    gruppe = st.text_input("Gruppe: ", key="gruppe")
with col2:
    trainer = st.text_input("Trainer/-in: ", key="trainer")

col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

# Tätigkeiten und Bemerkungen #1
with col1:
    datum1 = st.text_input("Datum #1: ", max_chars=10, key="datum1")
with col2:
    trainer1 = st.text_input("Trainer/-in #1: ", max_chars=12, key="trainer1")
with col3:
    tätigkeit1 = st.text_input("Tätigkeit #1: ", max_chars=125, key="tätigkeit1")
with col4:
    bemerkungen1 = st.text_input("Bemerkungen #1: ", max_chars=100, key="bemerkungen1")

# Tätigkeiten und Bemerkungen #2
with col1:
    datum2 = st.text_input("Datum #2: ", max_chars=10, key="datum2")
with col2:
    trainer2 = st.text_input("Trainer/-in #2: ", max_chars=12, key="trainer2")
with col3:
    tätigkeit2 = st.text_input("Tätigkeit #2: ", max_chars=125, key="tätigkeit2")
with col4:
    bemerkungen2 = st.text_input("Bemerkungen #2: ", max_chars=100, key="bemerkungen2")

# Tätigkeiten und Bemerkungen #3
with col1:
    datum3 = st.text_input("Datum #3: ", max_chars=10, key="datum3")
with col2:
    trainer3 = st.text_input("Trainer/-in #3: ", max_chars=12, key="trainer3")
with col3:
    tätigkeit3 = st.text_input("Tätigkeit #3: ", max_chars=125, key="tätigkeit3")
with col4:
    bemerkungen3 = st.text_input("Bemerkungen #3: ", max_chars=100, key="bemerkungen3")

# Tätigkeiten und Bemerkungen #4
with col1:
    datum4 = st.text_input("Datum #4: ", max_chars=10, key="datum4")
with col2:
    trainer4 = st.text_input("Trainer/-in #4: ", max_chars=12, key="trainer4")
with col3:
    tätigkeit4 = st.text_input("Tätigkeit #4: ", max_chars=125, key="tätigkeit4")
with col4:
    bemerkungen4 = st.text_input("Bemerkungen #4: ", max_chars=100, key="bemerkungen4")

# Tätigkeiten und Bemerkungen #5
with col1:
    datum5 = st.text_input("Datum #5: ", max_chars=10, key="datum5")
with col2:
    trainer5 = st.text_input("Trainer/-in #5: ", max_chars=12, key="trainer5")
with col3:
    tätigkeit5 = st.text_input("Tätigkeit #5: ", max_chars=125, key="tätigkeit5")
with col4:
    bemerkungen5 = st.text_input("Bemerkungen #5: ", max_chars=100, key="bemerkungen5")

# PDF erstellen
def createPDF(lehrlingName, kalenderwoche, vomDatum, bisDatum, gruppe, trainer, datum1, trainer1, tätigkeit1, bemerkungen1, datum2, trainer2, tätigkeit2, bemerkungen2, datum3, trainer3, tätigkeit3, bemerkungen3, datum4, trainer4, tätigkeit4, bemerkungen4, datum5, trainer5, tätigkeit5, bemerkungen5) -> bytes:
    """Creates a simple PDF in memory and returns its bytes."""
    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    ausbildungstagebuchVorlage = ImageReader("imgs/ausbildungstagebuch_vorlage.png")

    c.drawImage(ausbildungstagebuchVorlage, 0, 0, width=landscape(A4)[0], height=landscape(A4)[1])

    c.setFont("Helvetica", 32)

    styles = getSampleStyleSheet()
    style = styles["Normal"]

    style.fontName = "Helvetica"
    style.fontSize = 14
    style.leading = 16

    #Liste(Index) für Allgemeine Info, Datum, Trainer, Tätigkeiten und Bemerkungen

    top_texts = [
        Paragraph(lehrlingName, style),
        Paragraph(kalenderwoche, style),
        Paragraph(vomDatum, style),
        Paragraph(bisDatum, style),
        Paragraph(gruppe, style),
        Paragraph(trainer, style)
    ]

    datum_texts = [
        Paragraph(datum1, style),
        Paragraph(datum2, style),
        Paragraph(datum3, style),
        Paragraph(datum4, style),
        Paragraph(datum5, style)
    ]

    trainer_texts = [
        Paragraph(trainer1, style),
        Paragraph(trainer2, style),
        Paragraph(trainer3, style),
        Paragraph(trainer4, style),
        Paragraph(trainer5, style)
    ]

    tätigkeit_texts = [
    Paragraph(tätigkeit1, style),
    Paragraph(tätigkeit2, style),
    Paragraph(tätigkeit3, style),
    Paragraph(tätigkeit4, style),
    Paragraph(tätigkeit5, style)
    ]

    bemerkung_texts = [
    Paragraph(bemerkungen1, style),
    Paragraph(bemerkungen2, style),
    Paragraph(bemerkungen3, style),
    Paragraph(bemerkungen4, style),
    Paragraph(bemerkungen5, style)
    ]

    #Debug-> showBoundary = 1 zeigt die Rahmen der Box

    # x, y position/koordinaten
    # width, height der Box
    lehrlingNameFrame = Frame(
        122, 455,    
        165, 30,
    )

    kalenderwocheFrame = Frame(
        422, 455,    
        30, 30,
    )

    vomDatumFrame = Frame(
        474, 455,    
        95, 30,
    )

    bisDatumFrame = Frame(
        594, 455,    
        95, 30,
    )

    gruppeFrame = Frame(
        122, 443,    
        165, 30,
    )

    trainerFrame = Frame(
        374, 443,    
        122, 30,
    )

    datumFrame1 = Frame(
        62, 388,   
        102, 31,    
    )

    datumFrame2 = Frame(
        62, 326,
        102, 31,
    )

    datumFrame3 = Frame(
        62, 264,
        102, 31,
    )

    datumFrame4 = Frame(
        62, 202,
        102, 31,
    )

    datumFrame5 = Frame(
        62, 140,
        102, 31,
    )

    trainerFrame1 = Frame(
        62, 358,
        102, 31,
    )

    trainerFrame2 = Frame(
        62, 296,
        102, 31,
    )

    trainerFrame3 = Frame(
        62, 234,
        102, 31,
    )

    trainerFrame4 = Frame(
        62, 172,
        102, 31,
    )

    trainerFrame5 = Frame(
        62, 110,
        102, 31,
    )

    tätigkeitFrame1 = Frame(
        165, 358,
        327, 62,
    )

    tätigkeitFrame2 = Frame(
        165, 296,
        327, 62,
    )

    tätigkeitFrame3 = Frame(
        165, 234,
        327, 62,
    )

    tätigkeitFrame4 = Frame(
        165, 172,
        327, 62,
    )

    tätigkeitFrame5 = Frame(
        165, 110,
        327, 62,
    )

    bemerkungFrame1 = Frame(
        492, 358,
        272, 62,
    )  

    bemerkungFrame2 = Frame(
        492, 296,
        272, 62,
    )

    bemerkungFrame3 = Frame(
        492, 234,
        272, 62,
    )

    bemerkungFrame4 = Frame(
        492, 172,
        272, 62,
    )

    bemerkungFrame5 = Frame(
        492, 110,
        272, 62,
    )

    lehrlingNameFrame.addFromList([top_texts[0]], c)
    kalenderwocheFrame.addFromList([top_texts[1]], c)
    vomDatumFrame.addFromList([top_texts[2]], c)
    bisDatumFrame.addFromList([top_texts[3]], c)
    gruppeFrame.addFromList([top_texts[4]], c)
    trainerFrame.addFromList([top_texts[5]], c)

    datumFrame1.addFromList([datum_texts[0]], c)
    datumFrame2.addFromList([datum_texts[1]], c)
    datumFrame3.addFromList([datum_texts[2]], c)
    datumFrame4.addFromList([datum_texts[3]], c)
    datumFrame5.addFromList([datum_texts[4]], c)

    trainerFrame1.addFromList([trainer_texts[0]], c)
    trainerFrame2.addFromList([trainer_texts[1]], c)
    trainerFrame3.addFromList([trainer_texts[2]], c)
    trainerFrame4.addFromList([trainer_texts[3]], c)
    trainerFrame5.addFromList([trainer_texts[4]], c)

    tätigkeitFrame1.addFromList([tätigkeit_texts[0]], c)
    tätigkeitFrame2.addFromList([tätigkeit_texts[1]], c)
    tätigkeitFrame3.addFromList([tätigkeit_texts[2]], c)
    tätigkeitFrame4.addFromList([tätigkeit_texts[3]], c)
    tätigkeitFrame5.addFromList([tätigkeit_texts[4]], c)

    bemerkungFrame1.addFromList([bemerkung_texts[0]], c)
    bemerkungFrame2.addFromList([bemerkung_texts[1]], c)
    bemerkungFrame3.addFromList([bemerkung_texts[2]], c)
    bemerkungFrame4.addFromList([bemerkung_texts[3]], c)
    bemerkungFrame5.addFromList([bemerkung_texts[4]], c)

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.read()

if st.button("Eingaben speichern für später", on_click=eingabenSpeichern):
    st.success("Eingaben gespeichert! Sie werden beim nächsten Start automatisch geladen.")

if st.button("Erstelle PDF (Download)"):
    pdf_bytes = createPDF(lehrlingName, kalenderwoche, vomDatum, bisDatum, gruppe, trainer, datum1, trainer1, tätigkeit1, bemerkungen1, datum2, trainer2, tätigkeit2, bemerkungen2, datum3, trainer3, tätigkeit3, bemerkungen3, datum4, trainer4, tätigkeit4, bemerkungen4, datum5, trainer5, tätigkeit5, bemerkungen5)
    st.success("PDF erfolgreich erstellt!")
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name="Ausbildungstagebuch_" + lehrlingName + "_" + kalenderwoche + "_" + vomDatum + "-" + bisDatum + ".pdf",
        mime="application/pdf",
        on_click=eingabenLöschen,
        use_container_width=True
        )