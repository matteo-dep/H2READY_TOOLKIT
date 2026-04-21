import streamlit as st
import pandas as pd
from io import BytesIO
import requests
import json
import os

# ==========================================
# 1. CONFIGURAZIONE PAGINA E LINGUA
# ==========================================
st.set_page_config(page_title="H2READY TOOLKIT - Tool 2.1", layout="wide")

LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_choice = st.sidebar.selectbox("🌐 Lingua / Language / Jezik", list(LANG_OPTIONS.keys()))
LANG = LANG_OPTIONS[lang_choice]

# Dizionario per l'interfaccia (Solo istruzioni operative e label)
T = {
    "it": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.1: Scouting aziende HTA e RED III",
        "credits": "Sviluppato all'interno del progetto [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 GUIDA OPERATIVA (Leggi prima di iniziare)",
        "instructions_md": """
### 🎯 Qual è il tuo obiettivo?
Come referente dell'Ente, il tuo compito è **mappare le industrie del tuo territorio** per capire quali hanno *reale* necessità di passare all'idrogeno verde (es. acciaierie, vetrerie, chimica).

**Segui questi 3 passaggi:**

**🟢 FASE 1: Screening Iniziale**
Carica il file di screening nella sezione dedicata. Il simulatore filtrerà le aziende idonee. Se non hai il file, scarica il template subito sotto l'area di caricamento.

**🟡 FASE 2: Consolidamento Fabbisogni**
Inserisci le stime dei fabbisogni (tonnellate/anno) delle aziende risultate idonee. Anche qui, trovi il template dedicato sotto l'uploader.

**🔵 FASE 3: Esportazione**
Inserisci il tuo **Codice Identificativo** in fondo alla pagina e clicca "Salva" per inviare i dati al database centrale.
        """,
        "info_template1": "💡 Se non hai ancora i dati di screening, usa questo modello. **Attenzione: i dati vanno caricati mantenendo esattamente questo formato (stessi nomi delle colonne e struttura).**",
        "info_template2": "💡 Usa questo modello per consolidare le tonnellate di idrogeno necessarie. **Attenzione: i dati vanno caricati rispettando rigorosamente il formato di questo template.**",
        "btn_template1": "📥 Scarica Template Screening (Fase 1)",
        "btn_template2": "📥 Scarica Template Fabbisogni (Fase 2)",
        "header_fase1": "📤 FASE 1: Caricamento e Analisi Termodinamica",
        "header_fase2": "📤 FASE 2: Consolidamento Fabbisogni",
        "input_id": "Inserisci il Codice Identificativo (es. 030043):",
        "btn_export": "🚀 Salva Risultati nel Database Centrale",
        "export_success": "✅ Dati salvati con successo nel Master Database!"
    },
    "en": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.1: HTA and RED III Company Scouting",
        "credits": "Developed within the [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) project by **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 OPERATIONAL GUIDE (Read before starting)",
        "instructions_md": """
### 🎯 What is your goal?
As an Entity representative, your task is to **map the industries in your area** to understand which ones have a *real* need for green hydrogen.

**Follow these 3 steps:**

**🟢 PHASE 1: Initial Screening**
Upload the screening file in the dedicated section. If you don't have the file, download the template below the upload area.

**🟡 PHASE 2: Needs Consolidation**
Enter the estimated needs (tons/year) for the eligible companies. The template is available below the uploader.

**🔵 PHASE 3: Export**
Enter your **Identification Code** at the bottom of the page and click "Save".
        """,
        "info_template1": "💡 If you don't have the screening data yet, use this template. **Warning: data must be uploaded keeping exactly this format (same column names and structure).**",
        "info_template2": "💡 Use this template to consolidate hydrogen tons. **Warning: data must be uploaded strictly following the format of this template.**",
        "btn_template1": "📥 Download Screening Template (Phase 1)",
        "btn_template2": "📥 Download Needs Template (Phase 2)",
        "header_fase1": "📤 PHASE 1: Upload and Analysis",
        "header_fase2": "📤 PHASE 2: Needs Consolidation",
        "input_id": "Enter the Identification Code (e.g. 030043):",
        "btn_export": "🚀 Save Results to Central Database",
        "export_success": "✅ Data successfully saved!"
    },
    "sl": {
        "title": "🚀 H2READY TOOLKIT - Orodje 2.1: Iskanje podjetij HTA in RED III",
        "credits": "Razvito v okviru projekta [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready), avtor **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 OPERATIVNI VODNIK (Preberite pred začetkom)",
        "instructions_md": """
### 🎯 Kakšen je vaš cilj?
Kot predstavnik organa je vaša naloga **kartiranje industrij na vašem območju**, da ugotovite, katere imajo *resnično* potrebo po zelenem vodiku.

**Sledite tem 3 korakom:**

**🟢 1. FAZA: Začetni pregled**
Naložite datoteko za pregled v namenski razdelek. Če datoteke nimate, prenesite predlogo pod območjem za nalaganje.

**🟡 2. FAZA: Konsolidacija potreb**
Vnesite ocenjene potrebe (tone/leto) za ustrezna podjetja. Predloga je na voljo pod nalagalnikom.

**🔵 3. FAZA: Izvoz**
Na dnu strani vnesite svojo **Identifikacijsko kodo** in kliknite "Shrani".
        """,
        "info_template1": "💡 Če še nimate podatkov za pregled, uporabite to predlogo. **Opozorilo: podatke je treba naložiti v natančno tem formatu (enaka imena stolpcev in struktura).**",
        "info_template2": "💡 Uporabite to predlogo za konsolidacijo ton vodika. **Opozorilo: podatke naložite strogo v skladu s formatom te predloge.**",
        "btn_template1": "📥 Prenesi predlogo za pregled (1. faza)",
        "btn_template2": "📥 Prenesi predlogo za potrebe (2. faza)",
        "header_fase1": "📤 1. FAZA: Nalaganje in analiza",
        "header_fase2": "📤 2. FAZA: Konsolidacija potreb",
        "input_id": "Vnesite identifikacijsko kodo (npr. 030043):",
        "btn_export": "🚀 Shrani rezultate v centralno bazo",
        "export_success": "✅ Podatki so uspešno shranjeni!"
    }
}
_t = T[LANG]

# ==========================================
# 2. INTESTAZIONE E CREDITI
# ==========================================
st.title(_t["title"])
st.markdown(_t["credits"])
st.markdown("""
    <p style='font-size: 0.8rem; color: gray;'>
        🌐 Progetto: <a href='https://www.ita-slo.eu/en/h2ready' target='_blank'>Interreg H2Ready</a> | 
        🏠 Sito Ente: <a href='https://www.ape.fvg.it/' target='_blank'>APE FVG</a> | 
        📧 Contatto: <a href='mailto:matteo.depiccoli@ape.fvg.it'>matteo.depiccoli@ape.fvg.it</a>
    </p>
""", unsafe_allow_html=True)
st.divider()

# ==========================================
# 3. ISTRUZIONI INIZIALI
# ==========================================
# ==========================================
# 3. ISTRUZIONI E LOGICA (MENU A TENDINA)
# ==========================================
with st.expander(_t["instr_title"], expanded=True):
    # 1. Stampa le istruzioni operative (i 3 step) dal dizionario
    st.markdown(_t["instructions_md"])
    
    st.markdown("---") # Riga separatrice
    
    # 2. Carica la spiegazione del funzionamento (Logica) dal file .md
    nome_file_logica = f"logic_HTA_{LANG}.md"
    if os.path.exists(nome_file_logica):
        with open(nome_file_logica, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.caption(f"ℹ️ File di logica ({nome_file_logica}) non trovato nella cartella.")

st.markdown("---")
# --- FUNZIONI DI SUPPORTO ---
def generate_template_fase1():
    output = BytesIO()
    cols = ["nome azienda", "Codice ateco", "dimensione", "fatturato [M€]", "dipendenti", "ubicazione/consorzio", "vicinanza South H2 corridor", "AIA (si/no)", "consumo energia stimato [MWh]", "processo", "note"]
    df_temp = pd.DataFrame([["Esempio Spa", "24.10", "Grande", 100, 200, "Sì", "Sì", "Sì", 50000, "Ciclo DRI", "RED III"]], columns=cols)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df_temp.to_excel(writer, index=False)
    return output.getvalue()

def generate_template_fase2():
    output = BytesIO()
    cols = ["nome azienda", "dimensione azienda", "codice ateco", "fabbisogno identificato [t/y]"]
    df_temp = pd.DataFrame([["Esempio Spa", "Grande", "24.10", 1500.0]], columns=cols)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df_temp.to_excel(writer, index=False)
    return output.getvalue()

# ==========================================
# 4. FASE 1: SCREENING + DOWNLOAD TEMPLATE 1
# ==========================================
st.header(_t["header_fase1"])
uploaded_file_1 = st.file_uploader("Carica database Fase 1", type=["xlsx", "csv"], key="fase1")

if uploaded_file_1:
    st.success("✅ File Fase 1 caricato con successo!")
    # Qui andrà integrata la tua logica dei punteggi se presente

st.info(_t["info_template1"])
st.download_button(_t["btn_template1"], generate_template_fase1(), "template_screening.xlsx")

st.markdown("---")

# ==========================================
# 5. FASE 2: FABBISOGNI + DOWNLOAD TEMPLATE 2
# ==========================================
st.header(_t["header_fase2"])
uploaded_file_2 = st.file_uploader("Carica database Fase 2", type=["xlsx", "csv"], key="fase2")

n_aziende = 0
totale_h2 = 0.0
nomi_aziende = ""

if uploaded_file_2:
    try:
        df2 = pd.read_excel(uploaded_file_2) if uploaded_file_2.name.endswith('.xlsx') else pd.read_csv(uploaded_file_2)
        df2.columns = df2.columns.str.strip().str.lower()
        st.success("✅ Dati Fabbisogni caricati!")
        st.dataframe(df2, use_container_width=True)
        
        col_target = 'fabbisogno identificato [t/y]'
        if col_target in df2.columns:
            totale_h2 = df2[col_target].sum()
            n_aziende = len(df2[df2[col_target] > 0])
            nomi_aziende = "; ".join(df2['nome azienda'].astype(str).tolist())
            st.metric("Fabbisogno Totale Aggregato", f"{totale_h2:,.1f} ton/anno")
    except Exception as e:
        st.error(f"Errore: {e}")

st.info(_t["info_template2"])
st.download_button(_t["btn_template2"], generate_template_fase2(), "template_fabbisogni.xlsx")

# ==========================================
# 6. ESPORTAZIONE (Codice Identificativo)
# ==========================================
st.divider()
st.subheader("🔗 Esportazione Dati")
id_identificativo = st.text_input(_t["input_id"])

if st.button(_t["btn_export"]):
    if not id_identificativo:
        st.error("Inserisci il Codice Identificativo!")
    else:
        payload = {
            "ID_ISTAT": id_identificativo,
            "T21_N_AZIENDE_IDONEE": n_aziende,
            "T21_NOMI_AZIENDE": nomi_aziende,
            "T21_FABBISOGNO_H2_TON_ANNO": round(totale_h2, 2)
        }
        GOOGLE_URL = "https://script.google.com/macros/s/AKfycbwpP0x0hBnhOadXA43IieWg9EusAuhaafpyeXpyaStssDd7Qo-jwnuOttAllzz8r5JS/exec"
        try:
            response = requests.post(GOOGLE_URL, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                st.success(_t["export_success"])
                st.balloons()
        except:
            st.error("Errore di connessione.")

# ==========================================
# 7. LOGICA DEL CODICE (CARICATA DA .MD)
# ==========================================
st.divider()
nome_file_logica = f"logic_HTA_{LANG}.md"

if os.path.exists(nome_file_logica):
    with open(nome_file_logica, "r", encoding="utf-8") as f:
        st.markdown(f.read())
else:
    st.caption(f"ℹ️ File di logica ({nome_file_logica}) non trovato nella cartella.")
