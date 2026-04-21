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

# Dizionario per l'interfaccia
T = {
    "it": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.1: Scouting aziende HTA e RED III",
        "credits": "Sviluppato all'interno del progetto [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 GUIDA PER GLI ENTI (Leggi prima di iniziare)",
        "instructions_md": """
### 🎯 Qual è il tuo obiettivo?
Come referente dell'Ente, il tuo compito è **mappare le industrie del tuo territorio** per capire quali hanno *reale* necessità di passare all'idrogeno verde (es. acciaierie, vetrerie, chimica) e quali invece dovrebbero solo usare più energia elettrica. Non serve essere un ingegnere, il sistema farà i calcoli per te.

**Segui questi 3 passaggi:**

**🟢 FASE 1: Mappatura iniziale (Screening)**
1. Scarica il **Template 1** nella sezione sottostante.
2. Inserisci i dati base delle industrie locali (basta Nome, Codice ATECO e Dimensione). 
3. Carica il file completato nella sezione "FASE 1". Il simulatore applicherà un filtro termodinamico e ti restituirà l'elenco delle sole aziende "Idonee".

**🟡 FASE 2: Raccolta dei Fabbisogni**
1. Ora che sai chi sono le aziende idonee, contattale o stima il loro potenziale fabbisogno di idrogeno (in Tonnellate all'anno).
2. Scarica il **Template 2** nella sezione Fase 2, compila le tonnellate e caricalo.

**🔵 FASE 3: Invio al Master Database**
Una volta validato il file della Fase 2, inserisci il tuo **Codice Identificativo** in fondo alla pagina e clicca "Salva". I dati verranno usati per creare il Piano d'Azione (Action Plan) generale.
        """,
        "btn_template1": "📥 1. Scarica Template Screening (Fase 1)",
        "btn_template2": "📥 2. Scarica Template Fabbisogni (Fase 2)",
        "header_fase1": "📤 FASE 1: Caricamento e Analisi Termodinamica",
        "header_fase2": "📤 FASE 2: Consolidamento Fabbisogni",
        "input_istat": "Inserisci il Codice Identificativo (es. 030043):",
        "btn_export": "🚀 Salva Risultati nel Database Centrale",
        "export_success": "✅ Dati salvati con successo nel Master Database!"
    },
    "en": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.1: HTA and RED III Company Scouting",
        "credits": "Developed within the [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) project by **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 USER GUIDE (Read before starting)",
        "instructions_md": """
### 🎯 What is your goal?
Your task is to **map the industries in your area** to understand which ones have a *real* need to switch to green hydrogen (e.g., steelworks, glassworks, chemicals) and which ones should simply use electricity. You don't need to be an engineer; the system does the math for you.

**Follow these 3 steps:**

**🟢 PHASE 1: Initial Mapping (Screening)**
1. Download **Template 1** in the section below.
2. Enter the basic data of local industries (just Name, NACE Code, and Size). 
3. Upload the completed file in the "PHASE 1" section. The simulator will apply a thermodynamic filter and give you a list of only the "Eligible" companies.

**🟡 PHASE 2: Needs Consolidation**
1. Now that you know the eligible companies, contact them or estimate their potential hydrogen needs (in Tons per year).
2. Download **Template 2** in Phase 2, fill in the tonnage, and upload the file.

**🔵 PHASE 3: Send to Master Database**
Once the Phase 2 file is validated, enter your **Identification Code** at the bottom of the page and click "Save". The data will be used to create the general Action Plan.
        """,
        "btn_template1": "📥 1. Download Screening Template (Phase 1)",
        "btn_template2": "📥 2. Download Needs Template (Phase 2)",
        "header_fase1": "📤 PHASE 1: Upload and Thermodynamic Analysis",
        "header_fase2": "📤 PHASE 2: Needs Consolidation",
        "input_istat": "Enter the Identification Code (e.g. 030043):",
        "btn_export": "🚀 Save Results to Central Database",
        "export_success": "✅ Data successfully saved in the Master Database!"
    },
    "sl": {
        "title": "🚀 H2READY TOOLKIT - Orodje 2.1: Iskanje podjetij HTA in RED III",
        "credits": "Razvito v okviru projekta [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready), avtor **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 VODNIK ZA UPORABNIKE (Preberite pred začetkom)",
        "instructions_md": """
### 🎯 Kakšen je vaš cilj?
Vaša naloga je **kartiranje industrij na vašem območju**, da ugotovite, katere imajo *resnično* potrebo po prehodu na zeleni vodik (npr. jeklarne, steklarne, kemikalije) in katere bi morale preprosto uporabljati električno energijo. Ni vam treba biti inženir, sistem bo izračunal namesto vas.

**Sledite tem 3 korakom:**

**🟢 1. FAZA: Začetno kartiranje (Pregled)**
1. Prenesite **Predlogo 1** v spodnjem razdelku.
2. Vnesite osnovne podatke o lokalnih industrijah (samo Ime, Kodo ATECO/NACE in Velikost). 
3. Naložite izpolnjeno datoteko v razdelku "1. FAZA". Simulator bo uporabil termodinamični filter in vam vrnil seznam samo "Ustreznih" podjetij.

**🟡 2. FAZA: Zbiranje potreb**
1. Zdaj, ko poznate ustrezna podjetja, stopite v stik z njimi ali ocenite njihove potencialne potrebe po vodiku (v tonah na leto).
2. Prenesite **Predlogo 2** v razdelku 2. faza, vnesite tonažo in naložite datoteko.

**🔵 3. FAZA: Pošiljanje v glavno bazo podatkov**
Ko je datoteka 2. faze potrjena, na dnu strani vnesite svojo **Identifikacijsko kodo** in kliknite "Shrani". Podatki bodo uporabljeni za ustvarjanje splošnega Akcijskega načrta.
        """,
        "btn_template1": "📥 1. Prenesi predlogo za pregled (1. faza)",
        "btn_template2": "📥 2. Prenesi predlogo za potrebe (2. faza)",
        "header_fase1": "📤 1. FAZA: Nalaganje in termodinamična analiza",
        "header_fase2": "📤 2. FAZA: Konsolidacija potreb",
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

# ==========================================
# 3. ISTRUZIONI INIZIALI
# ==========================================
with st.expander(_t["instr_title"], expanded=True):
    st.markdown(_t["instructions_md"])

st.markdown("---")

# ==========================================
# 4. LOGICA DI CALCOLO E DIZIONARI ATECO
# ==========================================
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
    '23': 'Lavorazione di minerali non metalliferi (Vetro, Cemento, Ceramica)', '24': 'Metallurgia di base',
    '25': 'Fabbricazione di prodotti in metallo', '26': 'Computer e apparecchiature elettroniche',
    '27': 'Apparecchiature elettriche', '28': 'Macchinari e apparecchiature',
    '29': 'Autoveicoli e rimorchi', '30': 'Altri mezzi di trasporto',
    '31': 'Fabbricazione di mobili', '32': 'Altre industrie manifatturiere',
    '33': 'Riparazione e installazione macchine', '35': 'Energia elettrica, gas, vapore',
    '36': 'Raccolta e depurazione acque', '37': 'Gestione reti fognarie',
    '38': 'Trattamento e smaltimento rifiuti', '39': 'Risanamento e gestione rifiuti',
    '41': 'Costruzione di edifici', '42': 'Ingegneria civile', '43': 'Lavori di costruzione specializzati',
    '63': 'Servizi di informazione e Data Center'
}

def get_base_score(row):
    ateco = str(row.get('codice ateco', '')).replace('.', '').strip()
    prefix = ateco[:2]
    testo_tecnico = (str(row.get('processo', '')) + " " + str(row.get('note', ''))).lower()
    
    if prefix in ['35']: return 0, "Produzione Energia/Vapore", "🔴 NON NECESSARIO: Spreco termodinamico. Elettrificare, usare pompe di calore o biomasse."
    if prefix in ['38']: return 0, "Gestione Rifiuti", "🔴 NON NECESSARIO: Waste-to-Hydrogen possibile per produzione, ma spreco come consumo."
    if prefix in ['41', '42', '43'] or ateco.startswith('63'): return 0, "Edilizia/Data Center", "🔴 NON NECESSARIO: Calore a bassa temp. / Elettricità pura. Elettrificazione diretta."
    if ateco.startswith('2011'): return 0, "Produzione Gas (SMR)", "🔴 NON NECESSARIO COME INPUT: L'impianto inquina e va sostituito con elettrolisi."
    if ateco.startswith('2013') or ateco.startswith('1910'): return 0, "Sottoprodotto Industriale", "🔴 NON NECESSARIO: Idrogeno di scarto (Cloro-soda/Cokeria), escluso da quote RED III."

    if ateco.startswith('2015') or ateco.startswith('2014') or ateco.startswith('1920'):
        if 'etilene' in testo_tecnico or 'plastica' in testo_tecnico:
            return 0, "Sottoprodotto Cracking", "🔴 NON NECESSARIO: H2 di scarto da Steam Cracking."
        return 5, "Chimica/Raffinazione (Feedstock)", "🟢 ASSOLUTAMENTE NECESSARIO: H2 richiesto chimicamente come materia prima. Obbligo RED III."
    
    if ateco.startswith('2410') and any(k in testo_tecnico for k in ['dri', 'riduzione diretta']):
        return 5, "Siderurgia (Ciclo DRI)", "🟢 ASSOLUTAMENTE NECESSARIO: H2 insostituibile come agente riducente per il minerale di ferro."

    if ateco.startswith('2311') or ateco.startswith('2313'):
        return 4.5, "Fusione Vetro (Grandi Impianti)", "🟢 NECESSARIO: Difficile elettrificare forni fusori >80t/g per limiti fisici degli elettrodi."

    if ateco in ['2351', '2352', '2320', '2332']:
        return 3, "Calcinazione (Cemento/Ceramica/Calce)", "🟡 OPZIONALE: Elevata competizione economica con Biometano e CSS."

    trattamenti = ['2431', '2550', '2561', '2562']
    if any(ateco.startswith(c) for c in trattamenti):
        return 2, "Trattamenti Termici e Deformazione", "🟠 ALERT ELETTRIFICAZIONE: Valutare forni a induzione elettrica. H2 giustificato solo per tempra/atmosfera chimica."

    if prefix == '24':
        return 3.5, "Metallurgia / Fusione secondaria", "🟡 OPZIONALE: Valutare Forni Elettrici ad Arco (EAF) prima dell'Idrogeno."

    parole_chiave = ['metano', 'mw', 'forno', 'fusione', 'calore', 'termico', 'ossidazione', 'fiamme']
    if any(k in testo_tecnico for k in parole_chiave) and prefix in ['25', '26', '27', '28', '33']:
        return 1.5, "Processo termico generico", "🟠 ALERT ELETTRIFICAZIONE: Processo borderline, prioritizzare elettrificazione termica."

    return 0, "Non Classificato / Non Idoneo", "🔴 NON NECESSARIO: Processo assente o a bassa temperatura (elettrificabile)."

def calculate_total_score(row):
    base, _, _ = get_base_score(row)
    if base == 0: return 0
    dim = str(row.get('dimensione', '')).strip().title()
    mult = 1.5 if dim == 'Grande' else (1.2 if dim == 'Media' else 1.0)
    score = base * mult
    if str(row.get('aia (si/no)', '')).lower() in ['sì', 'si', 'yes', 'y']: score += 2
    if "z.i." in str(row.get('ubicazione/consorzio', '')).lower() or str(row.get('ubicazione/consorzio', '')).lower() in ['sì', 'si', 'yes']: score += 3
    if str(row.get('vicinanza south h2 corridor', '')).lower() in ['sì', 'si', 'yes', 'y']: score += 3
    return round(score, 1)

def generate_template_fase1():
    output = BytesIO()
    cols = ["nome azienda", "Codice ateco", "dimensione", "fatturato [M€]", "dipendenti", "ubicazione/consorzio", "vicinanza South H2 corridor", "AIA (si/no)", "consumo energia stimato [MWh]", "processo", "note"]
    df_temp = pd.DataFrame([["Fertilizzanti FVG S.p.A.", "20.15", "Grande", 250, 600, "Z.I. Aussa Corno", "SÌ", "SÌ", 150000, "Sintesi Ammoniaca", "Target RED III"]], columns=cols)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df_temp.to_excel(writer, index=False)
    return output.getvalue()

def generate_template_fase2():
    output = BytesIO()
    cols = ["nome azienda", "dimensione azienda", "codice ateco", "fabbisogno identificato [t/y]"]
    df_temp = pd.DataFrame([["Fertilizzanti FVG S.p.A.", "Grande", "20.15", 4500.5]], columns=cols)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df_temp.to_excel(writer, index=False)
    return output.getvalue()

# ==========================================
# 5. SEZIONE UPLOAD - FASE 1
# ==========================================
st.header(_t["header_fase1"])
uploaded_file_1 = st.file_uploader("Carica il database di screening (.xlsx o .csv)", type=["xlsx", "csv"], key="fase1")

if uploaded_file_1:
    try:
        df = pd.read_csv(uploaded_file_1) if uploaded_file_1.name.endswith('.csv') else pd.read_excel(uploaded_file_1)
        df.columns = df.columns.str.strip().str.lower()
        
        results = df.apply(lambda r: get_base_score(r), axis=1)
        df['base_score'] = [res[0] for res in results]
        df['profilo'] = [res[1] for res in results]
        df['esito'] = [res[2] for res in results]
        
        df['score'] = df.apply(calculate_total_score, axis=1)
        df['tier'] = df['score'].apply(lambda s: "Tier 1 (Alta Priorità)" if s >= 7 else ("Tier 2 (Media/Alert)" if s > 0 else "Non Idoneo"))
        df_idonee = df[df['score'] > 0].sort_values(by='score', ascending=False)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Aziende Analizzate", len(df))
        c2.metric("Semaforo Verde (Tier 1)", len(df[df['score'] >= 7]))
        c3.metric("Alert Elettrificazione (Tier 2)", len(df[(df['score'] > 0) & (df['score'] < 7)]))
        c4.metric("Spreco Termodinamico", len(df[df['score'] == 0]))

        st.markdown("### 🏢 Cruscotto Aziendale - Analisi Termodinamica")
        if not df_idonee.empty:
            st.dataframe(df_idonee[['nome azienda', 'codice ateco', 'score', 'tier', 'profilo', 'esito']], use_container_width=True)
        else:
            st.info("Nessuna azienda idonea trovata.")
    except Exception as e:
        st.error(f"Errore: {e}")

st.info("💡 Non hai ancora i dati? Scarica qui il formato corretto per lo screening:")
st.download_button(_t["btn_template1"], generate_template_fase1(), "template_screening_HTA.xlsx")

st.markdown("---")

# ==========================================
# 6. SEZIONE UPLOAD - FASE 2 ED EXPORT
# ==========================================
st.header(_t["header_fase2"])
uploaded_file_2 = st.file_uploader("Carica il database Fabbisogni (.xlsx o .csv)", type=["xlsx", "csv"], key="fase2")

if uploaded_file_2:
    try:
        df2 = pd.read_csv(uploaded_file_2) if uploaded_file_2.name.endswith('.csv') else pd.read_excel(uploaded_file_2)
        df2.columns = df2.columns.str.strip().str.lower()
        st.success("✅ Dati Fabbisogni validati correttamente!")
        st.dataframe(df2, use_container_width=True)
        
        col_target = 'fabbisogno identificato [t/y]'
        if col_target in df2.columns:
            totale_h2 = df2[col_target].sum()
            n_aziende = len(df2[df2[col_target] > 0])
            nomi_aziende = "; ".join(df2['nome azienda'].astype(str).tolist())
            st.metric("Fabbisogno Totale Aggregato", f"{totale_h2:,.1f} ton/anno")

            # EXPORT DATA
            st.divider()
            st.subheader("🔗 Esportazione Dati")
            id_identificativo = st.text_input(_t["input_istat"])
            
            if st.button(_t["btn_export"]):
                if not id_identificativo:
                    st.error("Inserisci il Codice Identificativo prima di inviare.")
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
                        if response.status_code in [200, 201]:
                            st.success(_t["export_success"])
                            st.balloons()
                        else:
                            st.error(f"Errore Google (Codice {response.status_code})")
                    except Exception as e:
                        st.error(f"Errore: {e}")
    except Exception as e:
        st.error(f"Errore: {e}")

st.info("💡 Usa questo template per mappare i fabbisogni quantitativi (ton/anno):")
st.download_button(_t["btn_template2"], generate_template_fase2(), "template_fabbisogni_HTA.xlsx")

# ==========================================
# 7. DESCRIZIONE LOGICA (DA FILE ESTERNO .MD)
# ==========================================
st.divider()
nome_file_logica = f"logic_HTA_{LANG}.md"

if os.path.exists(nome_file_logica):
    with open(nome_file_logica, "r", encoding="utf-8") as f:
        st.markdown(f.read())
else:
    st.caption(f"ℹ️ Suggerimento: Crea il file '{nome_file_logica}' nella cartella per visualizzare qui la spiegazione della logica termodinamica.")
