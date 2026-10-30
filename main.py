import streamlit as st
import json
from datetime import date, timedelta
from pathlib import Path
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle

SPEICHER_DATEI = Path(__file__).parent / "gespeicherte_eingaben.json"

FELDER = ["lehrlingName", "kalenderwoche", "vomDatum", "bisDatum", "gruppe", "trainer"]
for i in range(1, 6):
    FELDER += [f"datum{i}", f"trainer{i}", f"tätigkeit{i}", f"bemerkungen{i}"]

TRAINER_FELDER = ["trainer"] + [f"trainer{i}" for i in range(1, 6)]

def eingabenSpeichern():
    daten = {feld: st.session_state.get(feld) or "" for feld in FELDER}
    SPEICHER_DATEI.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")

def eingabenLöschen():
    SPEICHER_DATEI.unlink(missing_ok=True)
    for feld in FELDER:
        st.session_state[feld] = None if feld in TRAINER_FELDER else ""

TRAINER_DATEI = Path(__file__).parent / "trainer.json"

def trainerLaden():
    if TRAINER_DATEI.exists():
        return sorted(json.loads(TRAINER_DATEI.read_text(encoding="utf-8")), key=str.lower)
    return []

def trainerRegistrieren():
    name = st.session_state.get("neuerTrainer", "").strip()
    if not name:
        st.session_state["trainerMeldung"] = ("warning", "Bitte einen Namen eingeben.")
        return
    if len(name) > 12:
        st.session_state["trainerMeldung"] = ("warning", "Der Name darf höchstens 12 Zeichen lang sein (passt sonst nicht ins PDF).")
        return
    trainerListe = trainerLaden()
    if name.lower() in (t.lower() for t in trainerListe):
        st.session_state["trainerMeldung"] = ("warning", f"{name} ist bereits registriert.")
        return
    trainerListe.append(name)
    TRAINER_DATEI.write_text(json.dumps(sorted(trainerListe, key=str.lower), ensure_ascii=False, indent=2), encoding="utf-8")
    st.session_state["neuerTrainer"] = ""
    st.session_state["trainerMeldung"] = ("success", f"{name} wurde registriert!")

def trainerEntfernen():
    name = st.session_state.get("trainerZumEntfernen")
    if not name:
        st.session_state["trainerMeldung"] = ("warning", "Bitte einen Trainer/eine Trainerin auswählen.")
        return
    trainerListe = [t for t in trainerLaden() if t != name]
    TRAINER_DATEI.write_text(json.dumps(trainerListe, ensure_ascii=False, indent=2), encoding="utf-8")
    st.session_state["trainerZumEntfernen"] = None
    st.session_state["trainerMeldung"] = ("success", f"{name} wurde entfernt!")

def kalenderwocheGeändert():
    eingabe = st.session_state.get("kalenderwoche", "").strip()
    if not eingabe:
        for feld in ["vomDatum", "bisDatum"] + [f"datum{i}" for i in range(1, 6)]:
            st.session_state[feld] = ""
        return
    if not eingabe.isdigit():
        return
    woche = int(eingabe)
    heute = date.today()
    montage = []
    for jahr in (heute.year - 1, heute.year, heute.year + 1):
        try:
            montage.append(date.fromisocalendar(jahr, woche, 1))
        except ValueError:
            pass
    if not montage:
        st.session_state["kwMeldung"] = f"KW {woche} gibt es nicht."
        return
    montag = min(montage, key=lambda m: abs(m - heute))
    st.session_state["vomDatum"] = montag.strftime("%d.%m.%Y")
    st.session_state["bisDatum"] = (montag + timedelta(days=4)).strftime("%d.%m.%Y")
    for i in range(1, 6):
        st.session_state[f"datum{i}"] = (montag + timedelta(days=i - 1)).strftime("%d.%m")

if "geladen" not in st.session_state:
    st.session_state["geladen"] = True
    if SPEICHER_DATEI.exists():
        gespeichert = json.loads(SPEICHER_DATEI.read_text(encoding="utf-8"))
        for feld in FELDER:
            wert = gespeichert.get(feld, "")
            st.session_state[feld] = (wert or None) if feld in TRAINER_FELDER else wert

col1, col2, col3 = st.columns([1,4,1])

with col2:
    st.title("Ausbildungstagebuch")

trainerListe = trainerLaden()

with st.expander("Trainer/-innen verwalten"):
    st.text_input("Name des Trainers/der Trainerin: ", max_chars=12, key="neuerTrainer")
    st.button("Registrieren", on_click=trainerRegistrieren)
    if trainerListe:
        st.selectbox("Trainer/-in entfernen: ", trainerListe, index=None, key="trainerZumEntfernen", placeholder="Auswählen...")
        st.button("Entfernen", on_click=trainerEntfernen)
    if "trainerMeldung" in st.session_state:
        art, text = st.session_state.pop("trainerMeldung")
        getattr(st, art)(text)

def trainerAuswahl(label, key):
    optionen = list(trainerListe)
    aktuell = st.session_state.get(key)
    if aktuell and aktuell not in optionen:
        optionen = sorted(optionen + [aktuell], key=str.lower)
    return st.selectbox(label, optionen, index=None, key=key, placeholder="Auswählen oder eintippen...", accept_new_options=True) or ""

col1, col2, col3, col4 = st.columns(4)

with col1:
    lehrlingName = st.text_input("Lehrling: ", key="lehrlingName")
with col2:
    kalenderwoche = st.text_input("Kalenderwoche: ", key="kalenderwoche", on_change=kalenderwocheGeändert, help="KW eingeben und Enter drücken, die Daten werden automatisch ausgefüllt.")
    if "kwMeldung" in st.session_state:
        st.warning(st.session_state.pop("kwMeldung"))
with col3:
    vomDatum = st.text_input("Vom: ", max_chars=10, key="vomDatum")
with col4:
    bisDatum = st.text_input("Bis: ", max_chars=10, key="bisDatum")
col1, col2 = st.columns(2)
with col1:
    gruppe = st.text_input("Gruppe: ", key="gruppe")
with col2:
    trainer = trainerAuswahl("Trainer/-in: ", "trainer")

col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

with col1:
    datum1 = st.text_input("Datum #1: ", max_chars=10, key="datum1")
with col2:
    trainer1 = trainerAuswahl("Trainer/-in #1: ", "trainer1")
with col3:
    tätigkeit1 = st.text_input("Tätigkeit #1: ", max_chars=125, key="tätigkeit1")
with col4:
    bemerkungen1 = st.text_input("Bemerkungen #1: ", max_chars=100, key="bemerkungen1")

with col1:
    datum2 = st.text_input("Datum #2: ", max_chars=10, key="datum2")
with col2:
    trainer2 = trainerAuswahl("Trainer/-in #2: ", "trainer2")
with col3:
    tätigkeit2 = st.text_input("Tätigkeit #2: ", max_chars=125, key="tätigkeit2")
with col4:
    bemerkungen2 = st.text_input("Bemerkungen #2: ", max_chars=100, key="bemerkungen2")

with col1:
    datum3 = st.text_input("Datum #3: ", max_chars=10, key="datum3")
with col2:
    trainer3 = trainerAuswahl("Trainer/-in #3: ", "trainer3")
with col3:
    tätigkeit3 = st.text_input("Tätigkeit #3: ", max_chars=125, key="tätigkeit3")
with col4:
    bemerkungen3 = st.text_input("Bemerkungen #3: ", max_chars=100, key="bemerkungen3")

with col1:
    datum4 = st.text_input("Datum #4: ", max_chars=10, key="datum4")
with col2:
    trainer4 = trainerAuswahl("Trainer/-in #4: ", "trainer4")
with col3:
    tätigkeit4 = st.text_input("Tätigkeit #4: ", max_chars=125, key="tätigkeit4")
with col4:
    bemerkungen4 = st.text_input("Bemerkungen #4: ", max_chars=100, key="bemerkungen4")

with col1:
    datum5 = st.text_input("Datum #5: ", max_chars=10, key="datum5")
with col2:
    trainer5 = trainerAuswahl("Trainer/-in #5: ", "trainer5")
with col3:
    tätigkeit5 = st.text_input("Tätigkeit #5: ", max_chars=125, key="tätigkeit5")
with col4:
    bemerkungen5 = st.text_input("Bemerkungen #5: ", max_chars=100, key="bemerkungen5")

def createPDF(lehrlingName, kalenderwoche, vomDatum, bisDatum, gruppe, trainer, datum1, trainer1, tätigkeit1, bemerkungen1, datum2, trainer2, tätigkeit2, bemerkungen2, datum3, trainer3, tätigkeit3, bemerkungen3, datum4, trainer4, tätigkeit4, bemerkungen4, datum5, trainer5, tätigkeit5, bemerkungen5) -> bytes:
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
        82, 388,   
        102, 31,    
    )

    datumFrame2 = Frame(
        82, 326,
        102, 31,
    )

    datumFrame3 = Frame(
        82, 264,
        102, 31,
    )

    datumFrame4 = Frame(
        82, 202,
        102, 31,
    )

    datumFrame5 = Frame(
        82, 140,
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

@st.dialog("Alle Eingaben löschen?")
def löschenBestätigen():
    st.write("Alle Felder und die gespeicherten Eingaben werden gelöscht. Registrierte Trainer/-innen bleiben erhalten.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ja, alles löschen", type="primary", on_click=eingabenLöschen, use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Abbrechen", use_container_width=True):
            st.rerun()

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

st.divider()
if st.button("Alle Eingaben löschen", use_container_width=True):
    löschenBestätigen()
