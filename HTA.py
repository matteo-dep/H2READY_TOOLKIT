import streamlit as st
import pandas as pd
from io import BytesIO

# ==========================================
# 1. CONFIGURAZIONE PAGINA E LINGUA
# ==========================================
st.set_page_config(page_title="H2READY TOOLKIT - Tool 2.1", layout="wide")

# Dizionario delle lingue disponibili
LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_choice = st.sidebar.selectbox("🌐 Lingua / Language / Jezik", list(LANG_OPTIONS.keys()))
LANG = LANG_OPTIONS[lang_choice]

# ==========================================
# 2. DIZIONARIO DELLE TRADUZIONI (i18n)
# ==========================================
T = {
    "it": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.1: Filtro Termodinamico & RED III",
        "credits": "Questo codice è stato sviluppato all'interno del progetto **INTERREG H2Ready** da **Matteo De Piccoli - APE FVG**",
        "instructions_title": "📖 ISTRUZIONI E METODOLOGIA (Leggi prima di iniziare)",
        "instructions_text": """
        ### 1. Come funziona il Tool e i Codici ATECO/NACE
        Il motore logico analizza i codici ATECO incrociandoli con la **Direttiva Europea RED III** e con le **leggi della termodinamica**. Non si limita a cercare chi usa genericamente "alte temperature", ma individua dove l'idrogeno è **chimicamente insostituibile**.
        ### 2. FASE 1: Screening Iniziale
        Scarica il **Template 1 (Screening)** tramite il bottone qui sotto e compilalo. 
        * 🔴 **Colonne Obbligatorie:** `nome azienda`, `Codice ateco`, `dimensione`.
        ### 3. FASE 2: Mappatura Fabbisogni
        Usa il **Template 2 (Fabbisogni)** per inserire i dati quantitativi. Questo file è fondamentale per generare l'Action Plan.
        """,
        "btn_template_1": "📥 1. Scarica Template Screening (Fase 1)",
        "btn_template_2": "📥 2. Scarica Template Fabbisogni (Fase 2)",
        "fase1_header": "📤 FASE 1: Caricamento e Analisi Termodinamica",
        "fase1_desc": "Carica qui il file di screening per ottenere la valutazione di idoneità.",
        "fase2_header": "📤 FASE 2: Consolidamento Fabbisogni (Export per Action Plan)",
        "fase2_desc": "Carica qui il Template 2 compilato per l'Action Plan.",
        "upload_msg_1": "Carica il database di screening (.xlsx o .csv)",
        "upload_msg_2": "Carica il database Fabbisogni (.xlsx o .csv)",
        "metrics": ["Aziende Analizzate", "Semaforo Verde (Tier 1)", "Alert Elettrificazione (Tier 2)", "Spreco Termodinamico (Scartate)"],
        "cols_fase1": ["nome azienda", "codice ateco", "dimensione", "fatturato [M€]", "dipendenti", "ubicazione/consorzio", "vicinanza South H2 corridor", "AIA (si/no)", "consumo energia stimato [MWh]", "processo", "note"],
        "cols_fase2": ["nome azienda", "dimensione azienda", "codice ateco", "fabbisogno identificato [t/y]"],
        "esiti": {
            "spreco": "🔴 NON NECESSARIO: Spreco termodinamico. Elettrificare, usare pompe di calore o biomasse.",
            "assoluto": "🟢 ASSOLUTAMENTE NECESSARIO: H2 richiesto chimicamente come materia prima/agente riducente.",
            "limiti": "🟢 NECESSARIO: Difficile elettrificare per limiti fisici.",
            "opzionale": "🟡 OPZIONALE: Elevata competizione economica con Biometano e CSS.",
            "alert": "🟠 ALERT ELETTRIFICAZIONE: Valutare forni elettrici/induzione prima dell'Idrogeno."
        }
    },
    "en": {
        "title": "🚀 H2READY Scouting Tool - Thermodynamic Filter & RED III",
        "credits": "This code was developed within the **INTERREG H2Ready** project by **Matteo De Piccoli - APE FVG**",
        "instructions_title": "📖 INSTRUCTIONS AND METHODOLOGY (Read before starting)",
        "instructions_text": """
        ### 1. How the Tool and NACE Codes work
        The logic engine analyzes NACE codes crossing them with the **European RED III Directive** and **thermodynamic laws**. It identifies where hydrogen is **chemically irreplaceable**.
        ### 2. PHASE 1: Initial Screening
        Download the **Template 1 (Screening)** using the button below and fill it out. 
        * 🔴 **Mandatory Columns:** `company name`, `NACE code`, `size`.
        ### 3. PHASE 2: Needs Mapping
        Use **Template 2 (Needs)** to enter quantitative data. This file is essential to generate the Action Plan.
        """,
        "btn_template_1": "📥 1. Download Screening Template (Phase 1)",
        "btn_template_2": "📥 2. Download Needs Template (Phase 2)",
        "fase1_header": "📤 PHASE 1: Upload and Thermodynamic Analysis",
        "fase1_desc": "Upload the screening file here to get the suitability assessment.",
        "fase2_header": "📤 PHASE 2: Needs Consolidation (Export for Action Plan)",
        "fase2_desc": "Upload the filled Template 2 here for the Action Plan.",
        "upload_msg_1": "Upload the screening database (.xlsx or .csv)",
        "upload_msg_2": "Upload the Needs database (.xlsx or .csv)",
        "metrics": ["Analyzed Companies", "Green Light (Tier 1)", "Electrification Alert (Tier 2)", "Thermodynamic Waste (Discarded)"],
        "cols_fase1": ["company name", "nace code", "size", "turnover [M€]", "employees", "location/consortium", "proximity to South H2 corridor", "IED (yes/no)", "estimated energy consumption [MWh]", "process", "notes"],
        "cols_fase2": ["company name", "company size", "nace code", "identified need [t/y]"],
        "esiti": {
            "spreco": "🔴 NOT NECESSARY: Thermodynamic waste. Electrify, use heat pumps or biomass.",
            "assoluto": "🟢 ABSOLUTELY NECESSARY: H2 required chemically as feedstock/reducing agent.",
            "limiti": "🟢 NECESSARY: Difficult to electrify due to physical limits.",
            "opzionale": "🟡 OPTIONAL: High economic competition with Biomethane and SRF.",
            "alert": "🟠 ELECTRIFICATION ALERT: Evaluate electric/induction furnaces before Hydrogen."
        }
    },
    "sl": {
        "title": "🚀 H2READY Orodje za Pregled - Termodinamični filter in RED III",
        "credits": "To kodo je v okviru projekta **INTERREG H2Ready** razvil **Matteo De Piccoli - APE FVG**",
        "instructions_title": "📖 NAVODILA IN METODOLOGIJA (Preberite pred začetkom)",
        "instructions_text": """
        ### 1. Kako deluje orodje in kode NACE
        Logični motor analizira kode NACE tako, da jih primerja z **Evropsko direktivo RED III** in **zakoni termodinamike**. Prepozna, kje je vodik **kemično nenadomestljiv**.
        ### 2. FAZA 1: Začetni pregled
        Prenesite **Predlogo 1 (Pregled)** s spodnjim gumbom in jo izpolnite. 
        * 🔴 **Obvezni stolpci:** `ime podjetja`, `koda nace`, `velikost`.
        ### 3. FAZA 2: Kartiranje potreb
        Za vnos kvantitativnih podatkov uporabite **Predlogo 2 (Potrebe)**. Ta datoteka je ključna za izdelavo Akcijskega načrta.
        """,
        "btn_template_1": "📥 1. Prenesi predlogo za pregled (Faza 1)",
        "btn_template_2": "📥 2. Prenesi predlogo za potrebe (Faza 2)",
        "fase1_header": "📤 FAZA 1: Nalaganje in Termodinamična analiza",
        "fase1_desc": "Tukaj naložite datoteko s pregledom, da dobite oceno primernosti.",
        "fase2_header": "📤 FAZA 2: Konsolidacija potreb (Izvoz za akcijski načrt)",
        "fase2_desc": "Tukaj naložite izpolnjeno Predlogo 2 za Akcijski načrt.",
        "upload_msg_1": "Naložite bazo podatkov za pregled (.xlsx ali .csv)",
        "upload_msg_2": "Naložite bazo podatkov o potrebah (.xlsx ali .csv)",
        "metrics": ["Analizirana podjetja", "Zelena luč (Tier 1)", "Opozorilo o elektrifikaciji (Tier 2)", "Termodinamični odpadek (Zavrnjeno)"],
        "cols_fase1": ["ime podjetja", "koda nace", "velikost", "promet [M€]", "zaposleni", "lokacija/konzorcij", "bližina South H2 corridor", "IED (da/ne)", "ocenjena poraba energije [MWh]", "proces", "opombe"],
        "cols_fase2": ["ime podjetja", "velikost podjetja", "koda nace", "identificirana potreba [t/y]"],
        "esiti": {
            "spreco": "🔴 NI POTREBNO: Termodinamični odpadek. Elektrificirajte, uporabite toplotne črpalke ali biomaso.",
            "assoluto": "🟢 NUJNO POTREBNO: H2 je kemično potreben kot surovina/reducent.",
            "limiti": "🟢 POTREBNO: Težko elektrificirati zaradi fizičnih omejitev.",
            "opzionale": "🟡 NEOBVEZNO: Velika gospodarska konkurenca z biometanom in trdnimi alternativnimi gorivi.",
            "alert": "🟠 OPOZORILO O ELEKTRIFIKACIJI: Ocenite električne/indukcijske peči pred vodikom."
        }
    }
}

_t = T[LANG] # Alias veloce per accedere al dizionario della lingua scelta

# ==========================================
# 3. INTERFACCIA PRINCIPALE
# ==========================================
st.title(_t["title"])
st.caption(_t["credits"])
st.markdown("""
    <p style='font-size: 0.8rem; color: gray;'>
        🌐 Progetto: <a href='https://www.ita-slo.eu/en/h2ready' target='_blank'>Interreg H2Ready</a> | 
        🏠 Sito Ente: <a href='https://www.ape.fvg.it/' target='_blank'>APE FVG</a> | 
        📧 Contatto: <a href='mailto:matteo.depiccoli@ape.fvg.it'>matteo.depiccoli@ape.fvg.it</a>
    </p>
""", unsafe_allow_html=True)
st.divider()

# --- LOGICA DI SCORING MULTILINGUA ---
def get_base_score(row, lang):
    # Standardizzazione chiavi: cerchiamo la chiave indipendentemente dalla lingua
    ateco_key = [c for c in row.index if 'ateco' in c.lower() or 'nace' in c.lower()][0]
    proc_key = [c for c in row.index if 'process' in c.lower() or 'proces' in c.lower()][0]
    note_key = [c for c in row.index if 'not' in c.lower() or 'opomb' in c.lower()][0]

    ateco = str(row.get(ateco_key, '')).replace('.', '').strip()
    prefix = ateco[:2]
    testo_tecnico = (str(row.get(proc_key, '')) + " " + str(row.get(note_key, ''))).lower()
    
    esiti = T[lang]['esiti']

    if prefix in ['35', '38', '41', '42', '43'] or ateco.startswith('63') or ateco.startswith('2011') or ateco.startswith('2013') or ateco.startswith('1910'):
        return 0, "Non Idoneo", esiti['spreco']
    
    if ateco.startswith('2015') or ateco.startswith('2014') or ateco.startswith('1920'):
        if 'etilene' in testo_tecnico or 'plastica' in testo_tecnico or 'ethylene' in testo_tecnico:
            return 0, "Non Idoneo", esiti['spreco']
        return 5, "Feedstock", esiti['assoluto']
    
    if ateco.startswith('2410') and any(k in testo_tecnico for k in ['dri', 'riduzione diretta', 'direct reduction', 'redukcija']):
        return 5, "DRI", esiti['assoluto']

    if ateco.startswith('2311') or ateco.startswith('2313'):
        return 4.5, "Fusione/Melting", esiti['limiti']

    if ateco in ['2351', '2352', '2320', '2332']:
        return 3, "Calcinazione/Calcination", esiti['opzionale']

    trattamenti = ['2431', '2550', '2561', '2562']
    if any(ateco.startswith(c) for c in trattamenti) or prefix == '24':
        return 2, "Trattamenti Termici/Heat Treat", esiti['alert']

    parole_chiave = ['metano', 'methane', 'mw', 'forno', 'furnace', 'peč', 'fusione', 'melting', 'calore', 'heat']
    if any(k in testo_tecnico for k in parole_chiave) and prefix in ['25', '26', '27', '28', '33']:
        return 1.5, "Processo termico generico", esiti['alert']

    return 0, "Non Idoneo", esiti['spreco']

def calculate_total_score(row):
    base, _, _ = get_base_score(row, LANG)
    if base == 0: return 0
    
    dim_key = [c for c in row.index if 'dimen' in c.lower() or 'size' in c.lower() or 'velikost' in c.lower()][0]
    aia_key = [c for c in row.index if 'aia' in c.lower() or 'ied' in c.lower()][0]
    ubic_key = [c for c in row.index if 'ubic' in c.lower() or 'locat' in c.lower() or 'lokac' in c.lower()][0]
    south_h2_key = [c for c in row.index if 'south' in c.lower()][0]

    dim = str(row.get(dim_key, '')).strip().lower()
    mult = 1.5 if dim in ['grande', 'large', 'velika'] else (1.2 if dim in ['media', 'medium', 'srednja'] else 1.0)
    score = base * mult
    
    yes_words = ['sì', 'si', 'yes', 'y', 'da']
    if str(row.get(aia_key, '')).lower() in yes_words: score += 2
    if "z.i." in str(row.get(ubic_key, '')).lower() or str(row.get(ubic_key, '')).lower() in yes_words: score += 3
    if str(row.get(south_h2_key, '')).lower() in yes_words: score += 3
    
    return round(score, 1)

# --- GENERATORI TEMPLATE (Dinamicizzati per lingua) ---
def generate_template_fase1(lang):
    output = BytesIO()
    cols = T[lang]["cols_fase1"]
    # Esempi tradotti/adattati
    example_data = [
        ["Fertilizzanti FVG S.p.A.", "20.15", "Grande", 250, 600, "Z.I. Aussa Corno", "SI", "SI", 150000, "Sintesi Ammoniaca", "Target RED III"],
        ["Vetreria Nord S.r.l.", "23.13", "Grande", 80, 150, "SI", "NO", "SI", 45000, "Forni fusori", ">100t/giorno"],
    ]
    df_temp = pd.DataFrame(example_data, columns=cols)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_temp.to_excel(writer, index=False, sheet_name='Template_Screening')
    return output.getvalue()

def generate_template_fase2(lang):
    output = BytesIO()
    cols = T[lang]["cols_fase2"]
    example_data = [
        ["Fertilizzanti FVG S.p.A.", "Grande", "20.15", 4500.5],
        ["Vetreria Nord S.r.l.", "Grande", "23.13", 1250.0],
    ]
    df_temp = pd.DataFrame(example_data, columns=cols)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_temp.to_excel(writer, index=False, sheet_name='Template_Fabbisogni')
    return output.getvalue()


with st.expander(_t["instructions_title"], expanded=True):
    st.markdown(_t["instructions_text"])
    
    st.download_button(label=_t["btn_template_1"], data=generate_template_fase1(LANG), file_name=f"template_screening_h2ready_{LANG}.xlsx", mime="application/vnd.ms-excel")
    st.download_button(label=_t["btn_template_2"], data=generate_template_fase2(LANG), file_name=f"template_fabbisogni_h2ready_{LANG}.xlsx", mime="application/vnd.ms-excel")

st.markdown("---")

# ==========================================
# UPLOAD FASE 1
# ==========================================
st.header(_t["fase1_header"])
st.write(_t["fase1_desc"])
uploaded_file_1 = st.file_uploader(_t["upload_msg_1"], type=["xlsx", "csv"], key="fase1")

if uploaded_file_1:
    try:
        df = pd.read_csv(uploaded_file_1) if uploaded_file_1.name.endswith('.csv') else pd.read_excel(uploaded_file_1)
        # Normalizza intestazioni del file caricato per renderle insensibili al maiuscolo
        df.columns = df.columns.str.strip().str.lower()
        
        results = df.apply(lambda r: get_base_score(r, LANG), axis=1)
        df['base_score'] = [res[0] for res in results]
        df['profilo'] = [res[1] for res in results]
        df['esito'] = [res[2] for res in results]
        df['score'] = df.apply(calculate_total_score, axis=1)
        df['tier'] = df['score'].apply(lambda s: "Tier 1" if s >= 7 else ("Tier 2" if s > 0 else "Non Idoneo"))
        
        df_idonee = df[df['score'] > 0].sort_values(by='score', ascending=False)

        # KPI Metrics Localizzati
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(_t["metrics"][0], len(df))
        c2.metric(_t["metrics"][1], len(df[df['score'] >= 7]))
        c3.metric(_t["metrics"][2], len(df[(df['score'] > 0) & (df['score'] < 7)]))
        c4.metric(_t["metrics"][3], len(df[df['score'] == 0]))

        st.markdown(f"### 🏢 Cruscotto Aziendale")
        if not df_idonee.empty:
            for i in range(0, len(df_idonee), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(df_idonee):
                        row = df_idonee.iloc[i + j]
                        with cols[j]:
                            nome_key = [c for c in row.index if 'nome' in c.lower() or 'name' in c.lower() or 'ime' in c.lower()][0]
                            if "Tier 1" in row['tier']: st.success(f"### 🏭 {row[nome_key]}")
                            else: st.warning(f"### 🏭 {row[nome_key]}")
                            
                            st.write(f"🏆 **Score:** {row['score']} / 15")
                            st.markdown(f"**💡 Esito / Outcome:**")
                            if '🟢' in row['esito']: st.info(row['esito'])
                            elif '🟡' in row['esito']: st.warning(row['esito'])
                            else: st.error(row['esito']) 
                            st.markdown("---")
        else:
            st.info("No suitable companies found.")

    except Exception as e:
        st.error(f"Errore / Error: {e}")

# ==========================================
# UPLOAD FASE 2
# ==========================================
st.markdown("---")
st.header(_t["fase2_header"])
st.info(_t["fase2_desc"])

uploaded_file_2 = st.file_uploader(_t["upload_msg_2"], type=["xlsx", "csv"], key="fase2")

if uploaded_file_2:
    try:
        df2 = pd.read_csv(uploaded_file_2) if uploaded_file_2.name.endswith('.csv') else pd.read_excel(uploaded_file_2)
        st.success("✅ Dati validati / Data validated!")
        st.dataframe(df2, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Errore / Error: {e}")
