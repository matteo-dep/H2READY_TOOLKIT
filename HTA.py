import streamlit as st
import pandas as pd
import plotly.express as px
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

# Dizionario per l'interfaccia (Istruzioni e Label)
T = {
    "it": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.1: Scouting aziende HTA e RED III",
        "credits": "Sviluppato all'interno del progetto [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 ISTRUZIONI E METODOLOGIA",
        "btn_template1": "📥 1. Scarica Template Screening (Fase 1)",
        "btn_template2": "📥 2. Scarica Template Fabbisogni (Fase 2)",
        "header_fase1": "📤 FASE 1: Caricamento e Analisi Termodinamica",
        "header_fase2": "📤 FASE 2: Consolidamento Fabbisogni (Export per Action Plan)",
        "input_istat": "Inserisci il Codice ISTAT del Comune (es. 030043):",
        "btn_export": "🚀 Salva Risultati nel Database Centrale",
        "export_success": "✅ Dati salvati con successo nel Master Database!"
    },
    "en": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.1: HTA and RED III Company Scouting",
        "credits": "Developed within the [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) project by **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 INSTRUCTIONS AND METHODOLOGY",
        "btn_template1": "📥 1. Download Screening Template (Phase 1)",
        "btn_template2": "📥 2. Download Needs Template (Phase 2)",
        "header_fase1": "📤 PHASE 1: Upload and Thermodynamic Analysis",
        "header_fase2": "📤 PHASE 2: Needs Consolidation (Export for Action Plan)",
        "input_istat": "Enter Municipality ISTAT Code (e.g. 030043):",
        "btn_export": "🚀 Save Results to Central Database",
        "export_success": "✅ Data successfully saved in the Master Database!"
    },
    "sl": {
        "title": "🚀 H2READY TOOLKIT - Orodje 2.1: Iskanje podjetij HTA in RED III",
        "credits": "Razvito v okviru projekta [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready), avtor **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 NAVODILA IN METODOLOGIJA",
        "btn_template1": "📥 1. Prenesi predlogo za pregled (1. faza)",
        "btn_template2": "📥 2. Prenesi predlogo za potrebe (2. faza)",
        "header_fase1": "📤 1. FAZA: Nalaganje in termodinamična analiza",
        "header_fase2": "📤 2. FAZA: Konsolidacija potreb (Izvoz za akcijski načrt)",
        "input_istat": "Vnesite ISTAT kodo občine (npr. 030043):",
        "btn_export": "🚀 Shrani rezultate v centralno bazo",
        "export_success": "✅ Podatki so uspešno shranjeni v glavno bazo!"
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

# --- DIZIONARI ATECO (Invariati) ---
ATECO_DESCRIPTIONS = {
    '1910': 'Prodotti della cokeria (1000–1100°C)', '1920': 'Raffinazione di prodotti petroliferi (500–900°C)',
    '2011': 'Produzione di gas industriali - SMR (700–900°C)', '2012': 'Produzione di coloranti e pigmenti (600–1000°C)',
    '2013': 'Chimica inorganica di base (500–900°C)', '2014': 'Chimica organica di base - Cracking (700–1100°C)',
    '2015': 'Fabbricazione di fertilizzanti e composti azotati (700–900°C)', '2016': 'Materie plastiche primarie (700–1100°C)',
    '2311': 'Fabbricazione di vetro piano (~1500°C)', '2313': 'Fabbricazione di vetro cavo (~1500°C)',
    '2320': 'Fabbricazione di prodotti refrattari (1200–1600°C)', '2332': 'Fabbricazione di mattoni e tegole (900–1200°C)',
    '2351': 'Produzione di cemento (1400–1500°C)', '2352': 'Produzione di calce e gesso (900–1200°C)',
    '2410': 'Produzione di ferro, acciaio e ferroleghe (1200–1600°C)', '2431': 'Trafilatura a freddo (600–1000°C)',
    '2442': 'Produzione di alluminio e semilavorati (660–750°C)', '2443': 'Produzione di rame e semilavorati (1000–1200°C)',
    '2444': 'Produzione di altri metalli non ferrosi (400–1200°C)', '2451': 'Fusione di ghisa (1200–1400°C)',
    '2452': 'Fusione di acciaio (1400–1600°C)', '2453': 'Fusione di metalli leggeri (650–1650°C)',
    '2550': 'Fucinatura, stampaggio e profilatura metalli (900–1200°C)', '2561': 'Trattamento e rivestimento dei metalli (500–1100°C)',
    '2562': 'Lavorazioni meccaniche termiche (500–900°C)', '3511': 'Produzione energia elettrica da fonti fossili (600–1200°C)',
    '3530': 'Produzione di vapore industriale (500–900°C)', '3821': 'Trattamento rifiuti non pericolosi - Incenerimento (850–1100°C)',
    '3822': 'Trattamento rifiuti pericolosi - Incenerimento (1000–1200°C)', '3832': 'Recupero rottami metallici (600–1500°C)'
}

MACRO_ATECO_DESCRIPTIONS = {
    '10': 'Industrie alimentari', '11': 'Industria delle bevande', '13': 'Industrie tessili',
    '14': 'Abbigliamento', '15': 'Articoli in pelle e cuoio', '16': 'Industria del legno',
    '17': 'Fabbricazione di carta', '18': 'Stampa e riproduzione', '19': 'Cokeria e Raffinazione',
    '20': 'Fabbricazione di prodotti chimici', '21': 'Prodotti farmaceutici', '22': 'Gomma e materie plastiche',
    '23': 'Minerali non metalliferi', '24': 'Metallurgia di base', '25': 'Prodotti in metallo'
}

# --- LOGICA DI CALCOLO (Invariata) ---
def get_base_score(row):
    ateco = str(row.get('codice ateco', '')).replace('.', '').strip()
    prefix = ateco[:2]
    testo_tecnico = (str(row.get('processo', '')) + " " + str(row.get('note', ''))).lower()
    
    if prefix in ['35', '38', '41', '42', '43'] or ateco.startswith('63'): 
        return 0, "Non Idoneo", "🔴 NON NECESSARIO: Elettrificazione diretta possibile."
    
    if ateco.startswith('2015') or ateco.startswith('2014') or ateco.startswith('1920'):
        return 5, "Chimica/Raffinazione (Feedstock)", "🟢 ASSOLUTAMENTE NECESSARIO: Obbligo RED III."
    
    if ateco.startswith('2410'): return 5, "Siderurgia", "🟢 ASSOLUTAMENTE NECESSARIO"
    if ateco.startswith('2311') or ateco.startswith('2313'): return 4.5, "Vetro", "🟢 NECESSARIO"
    
    return 0, "Non Classificato", "🔴 Non Idoneo"

def calculate_total_score(row):
    base, _, _ = get_base_score(row)
    if base == 0: return 0
    dim = str(row.get('dimensione', '')).strip().title()
    mult = 1.5 if dim == 'Grande' else (1.2 if dim == 'Media' else 1.0)
    score = base * mult
    return round(score, 1)

# --- GENERATORI TEMPLATE (Invariati) ---
def generate_template_fase1():
    output = BytesIO()
    cols = ["nome azienda", "Codice ateco", "dimensione", "fatturato [M€]", "dipendenti", "ubicazione/consorzio", "vicinanza South H2 corridor", "AIA (si/no)", "consumo energia stimato [MWh]", "processo", "note"]
    df_temp = pd.DataFrame([["Esempio Spa", "20.15", "Grande", 100, 200, "Sì", "Sì", "Sì", 50000, "Ammoniaca", "RED III"]], columns=cols)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df_temp.to_excel(writer, index=False)
    return output.getvalue()

def generate_template_fase2():
    output = BytesIO()
    cols = ["nome azienda", "dimensione azienda", "codice ateco", "fabbisogno identificato [t/y]"]
    df_temp = pd.DataFrame([["Esempio Spa", "Grande", "20.15", 1500.0]], columns=cols)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df_temp.to_excel(writer, index=False)
    return output.getvalue()

# ==========================================
# 3. INTERFACCIA E LOGICA
# ==========================================

with st.expander(_t["instr_title"], expanded=True):
    st.write("Segui la Fase 1 per lo screening e la Fase 2 per quantificare i fabbisogni.")
    st.download_button(_t["btn_template1"], generate_template_fase1(), "template_screening.xlsx")
    st.download_button(_t["btn_template2"], generate_template_fase2(), "template_fabbisogni.xlsx")

st.header(_t["header_fase1"])
uploaded_file_1 = st.file_uploader("Upload Fase 1", type=["xlsx", "csv"], key="f1")

if uploaded_file_1:
    df = pd.read_excel(uploaded_file_1) if uploaded_file_1.name.endswith('.xlsx') else pd.read_csv(uploaded_file_1)
    df.columns = df.columns.str.strip().str.lower()
    df['score'] = df.apply(calculate_total_score, axis=1)
    st.dataframe(df)

# --- FASE 2 E EXPORT ---
st.header(_t["header_fase2"])
uploaded_file_2 = st.file_uploader("Upload Fase 2", type=["xlsx", "csv"], key="f2")

if uploaded_file_2:
    df2 = pd.read_excel(uploaded_file_2) if uploaded_file_2.name.endswith('.xlsx') else pd.read_csv(uploaded_file_2)
    df2.columns = df2.columns.str.strip().str.lower()
    
    st.success("✅ Dati caricati!")
    st.dataframe(df2, use_container_width=True)
    
    col_target = 'fabbisogno identificato [t/y]'
    if col_target in df2.columns:
        totale_h2 = df2[col_target].sum()
        n_aziende = len(df2[df2[col_target] > 0])
        nomi_aziende = "; ".join(df2['nome azienda'].astype(str).tolist())
        st.metric("Fabbisogno Totale Aggregato", f"{totale_h2:,.1f} ton/anno")

        st.divider()
        st.subheader("🔗 Esportazione Dati")
        id_istat = st.text_input(_t["input_istat"])
        
        if st.button(_t["btn_export"]):
            if not id_istat:
                st.error("Inserisci l'ID Comune!")
            else:
                payload = {
                    "ID_ISTAT": id_istat,
                    "T21_N_AZIENDE_IDONEE": n_aziende,
                    "T21_NOMI_AZIENDE": nomi_aziende,
                    "T21_FABBISOGNO_H2_TON_ANNO": round(totale_h2, 2)
                }
                
                # IL TUO URL GOOGLE SCRIPT
                GOOGLE_URL = "https://script.google.com/macros/s/AKfycbwpP0x0hBnhOadXA43IieWg9EusAuhaafpyeXpyaStssDd7Qo-jwnuOttAllzz8r5JS/exec"
                
                try:
                    response = requests.post(GOOGLE_URL, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
                    if response.status_code in [200, 201]:
                        st.success(_t["export_success"])
                        st.balloons()
                    else:
                        st.error(f"Errore Google (Codice {response.status_code})")
                except Exception as e:
                    st.error(f"Errore di connessione: {e}")
