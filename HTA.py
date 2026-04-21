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
# Dizionario per l'interfaccia (Istruzioni e Label)
T = {
    "it": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.1: Scouting aziende HTA e RED III",
        "credits": "Sviluppato all'interno del progetto [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 GUIDA PER I COMUNI E LOGICA (Leggi prima di iniziare)",
        "instructions_md": """
### 🎯 Qual è il tuo obiettivo?
Come referente dell'Ente, il tuo compito è **mappare le industrie del tuo territorio** per capire quali hanno *reale* necessità di passare all'idrogeno verde (es. acciaierie, vetrerie, chimica) e quali invece dovrebbero solo usare più energia elettrica. Non serve essere un ingegnere, il sistema farà i calcoli per te.

**Segui questi 3 passaggi:**

**🟢 FASE 1: Mappatura iniziale (Screening)**
1. Scarica il **Template 1** tramite il bottone qui sotto.
2. Inserisci i dati base delle industrie locali (basta Nome, Codice ATECO e Dimensione). 
3. Carica il file completato nella sezione "FASE 1". Il simulatore applicherà un filtro termodinamico e ti restituirà l'elenco delle sole aziende "Idonee".

**🟡 FASE 2: Raccolta dei Fabbisogni**
1. Ora che sai chi sono le aziende idonee, contattale o stima il loro potenziale fabbisogno di idrogeno (in Tonnellate all'anno).
2. Scarica il **Template 2**, compila le tonnellate e carica il file nella "FASE 2".

**🔵 FASE 3: Invio al Master Database**
Una volta validato il file della Fase 2, inserisci il tuo **Codice Identificativo** in fondo alla pagina e clicca "Salva". I dati verranno usati per creare il Piano d'Azione (Action Plan) generale.

---
### 🧠 Come ragiona il simulatore (Logica Termodinamica)
Il tool non si limita a cercare chi usa genericamente "alte temperature". Legge le prime 4 cifre del codice ATECO e applica uno scoring scientifico:
* **🔴 Spreco Termodinamico (Scartate):** Processi a bassa temperatura, edilizia o produzione di vapore. L'idrogeno qui è inefficace: l'azienda dovrebbe usare pompe di calore o elettrificazione diretta.
* **🟠 Alert Elettrificazione (Tier 2):** Processi termici generici (es. forni per trattamenti termici) dove tecnologie alternative (es. forni elettrici a induzione) sono spesso più efficienti.
* **🟢 Assolutamente Necessario (Tier 1):** L'idrogeno è chimicamente insostituibile (es. come agente riducente per l'acciaio o materia prima nei fertilizzanti) o ci sono limiti fisici all'elettrificazione (es. grandi forni fusori continui per il vetro).
Il punteggio base viene poi aumentato (Bonus) se l'azienda è di grandi dimensioni o si trova vicino a infrastrutture strategiche come il *South H2 Corridor*.
        """,
        "btn_template1": "📥 1. Scarica Template Screening (Fase 1)",
        "btn_template2": "📥 2. Scarica Template Fabbisogni (Fase 2)",
        "header_fase1": "📤 FASE 1: Caricamento e Analisi Termodinamica",
        "header_fase2": "📤 FASE 2: Consolidamento Fabbisogni (Export per Action Plan)",
        "input_istat": "Inserisci il Codice Identificativo (es. 030043):",
        "btn_export": "🚀 Salva Risultati nel Database Centrale",
        "export_success": "✅ Dati salvati con successo nel Master Database!"
    },
    "en": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.1: HTA and RED III Company Scouting",
        "credits": "Developed within the [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) project by **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 USER GUIDE AND LOGIC (Read before starting)",
        "instructions_md": """
### 🎯 What is your goal?
Your task is to **map the industries in your area** to understand which ones have a *real* need to switch to green hydrogen (e.g., steelworks, glassworks, chemicals) and which ones should simply use electricity. You don't need to be an engineer; the system does the math for you.

**Follow these 3 steps:**

**🟢 PHASE 1: Initial Mapping (Screening)**
1. Download **Template 1** using the button below.
2. Enter the basic data of local industries (just Name, NACE Code, and Size). 
3. Upload the completed file in the "PHASE 1" section. The simulator will apply a thermodynamic filter and give you a list of only the "Eligible" companies.

**🟡 PHASE 2: Needs Consolidation**
1. Now that you know the eligible companies, contact them or estimate their potential hydrogen needs (in Tons per year).
2. Download **Template 2**, fill in the tonnage, and upload the file in "PHASE 2".

**🔵 PHASE 3: Send to Master Database**
Once the Phase 2 file is validated, enter your **Identification Code** at the bottom of the page and click "Save". The data will be used to create the general Action Plan.

---
### 🧠 How the simulator thinks (Thermodynamic Logic)
The tool doesn't just look for "high temperatures". It reads the NACE code and applies a scientific scoring system:
* **🔴 Thermodynamic Waste (Discarded):** Low-temp processes, construction, or steam production. Hydrogen is inefficient here: direct electrification or heat pumps should be used.
* **🟠 Electrification Alert (Tier 2):** Generic thermal processes where alternative technologies (e.g., electric induction furnaces) are often more efficient.
* **🟢 Absolutely Necessary (Tier 1):** Hydrogen is chemically irreplaceable (e.g., reducing agent in steel or feedstock in fertilizers) or there are physical limits to electrification (e.g., huge continuous glass melting furnaces).
The base score is then boosted if the company is large or located near strategic infrastructures like the *South H2 Corridor*.
        """,
        "btn_template1": "📥 1. Download Screening Template (Phase 1)",
        "btn_template2": "📥 2. Download Needs Template (Phase 2)",
        "header_fase1": "📤 PHASE 1: Upload and Thermodynamic Analysis",
        "header_fase2": "📤 PHASE 2: Needs Consolidation (Export for Action Plan)",
        "input_istat": "Enter the Identification Code (e.g. 030043):",
        "btn_export": "🚀 Save Results to Central Database",
        "export_success": "✅ Data successfully saved in the Master Database!"
    },
    "sl": {
        "title": "🚀 H2READY TOOLKIT - Orodje 2.1: Iskanje podjetij HTA in RED III",
        "credits": "Razvito v okviru projekta [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready), avtor **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 VODNIK ZA UPORABNIKE IN LOGIKA (Preberite pred začetkom)",
        "instructions_md": """
### 🎯 Kakšen je vaš cilj?
Vaša naloga je **kartiranje industrij na vašem območju**, da ugotovite, katere imajo *resnično* potrebo po prehodu na zeleni vodik (npr. jeklarne, steklarne, kemikalije) in katere bi morale preprosto uporabljati električno energijo. Ni vam treba biti inženir, sistem bo izračunal namesto vas.

**Sledite tem 3 korakom:**

**🟢 1. FAZA: Začetno kartiranje (Pregled)**
1. Prenesite **Predlogo 1** s spodnjim gumbom.
2. Vnesite osnovne podatke o lokalnih industrijah (samo Ime, Kodo ATECO/NACE in Velikost). 
3. Naložite izpolnjeno datoteko v razdelku "1. FAZA". Simulator bo uporabil termodinamični filter in vam vrnil seznam samo "Ustreznih" podjetij.

**🟡 2. FAZA: Zbiranje potreb**
1. Zdaj, ko poznate ustrezna podjetja, stopite v stik z njimi ali ocenite njihove potencialne potrebe po vodiku (v tonah na leto).
2. Prenesite **Predlogo 2**, vnesite tonažo in naložite datoteko v "2. FAZI".

**🔵 3. FAZA: Pošiljanje v glavno bazo podatkov**
Ko je datoteka 2. faze potrjena, na dnu strani vnesite svojo **Identifikacijsko kodo** in kliknite "Shrani". Podatki bodo uporabljeni za ustvarjanje splošnega Akcijskega načrta.

---
### 🧠 Kako deluje simulator (Termodinamična logika)
Orodje ne išče zgolj "visokih temperatur". Prebere kodo NACE in uporabi znanstveni sistem točkovanja:
* **🔴 Termodinamična izguba (Zavrnjeno):** Nizkotemperaturni procesi ali proizvodnja pare. Vodik je tu neučinkovit: uporabiti bi bilo treba neposredno elektrifikacijo ali toplotne črpalke.
* **🟠 Opozorilo za elektrifikacijo (Tier 2):** Generični toplotni procesi, kjer so alternativne tehnologije (npr. električne indukcijske peči) pogosto učinkovitejše.
* **🟢 Absolutno nujno (Tier 1):** Vodik je kemično nenadomestljiv (npr. reducent pri jeklu) ali pa obstajajo fizične omejitve za elektrifikacijo (velike peči za taljenje stekla).
Osnovna ocena se nato poveča, če je podjetje veliko ali se nahaja blizu strateške infrastrukture (npr. *South H2 Corridor*).
        """,
        "btn_template1": "📥 1. Prenesi predlogo za pregled (1. faza)",
        "btn_template2": "📥 2. Prenesi predlogo za potrebe (2. faza)",
        "header_fase1": "📤 1. FAZA: Nalaganje in termodinamična analiza",
        "header_fase2": "📤 2. FAZA: Konsolidacija potreb (Izvoz za akcijski načrt)",
        "input_istat": "Vnesite identifikacijsko kodo (npr. 030043):",
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
# 3. INTERFACCIA E ISTRUZIONI
# ==========================================
with st.expander(_t["instr_title"], expanded=True):
    # Questa riga "magica" stampa tutto il papiro di istruzioni dettagliate (Step 1, 2, 3)
    st.markdown(_t["instructions_md"])
    
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
