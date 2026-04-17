import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="H2READY TOOLKIT - Tool 2.1", layout="wide")

# --- INTESTAZIONE E CREDITI ---
st.title("📊 H2READY - Scouting Tool")

# Inserimento crediti e link sotto il titolo
st.caption("Questo codice è stato sviluppato all'interno del progetto **INTERREG H2Ready** da **Matteo De Piccoli - APE FVG**")
st.markdown("""
    <p style='font-size: 0.8rem; color: gray;'>
        🌐 Progetto: <a href='https://www.ita-slo.eu/en/h2ready' target='_blank'>Interreg H2Ready</a> | 
        🏠 Sito Ente: <a href='https://www.ape.fvg.it/' target='_blank'>APE FVG</a> | 
        📧 Contatto: <a href='mailto:matteo.depiccoli@ape.fvg.it'>matteo.depiccoli@ape.fvg.it</a>
    </p>
""", unsafe_allow_html=True)

st.divider()

# --- DIZIONARIO ATECO SPECIFICO (4 Cifre - Hard to Abate e RED III) ---
ATECO_DESCRIPTIONS = {
    '1910': 'Prodotti della cokeria (1000–1100°C)',
    '1920': 'Raffinazione di prodotti petroliferi (500–900°C)',
    '2011': 'Produzione di gas industriali - SMR (700–900°C)',
    '2012': 'Produzione di coloranti e pigmenti (600–1000°C)',
    '2013': 'Chimica inorganica di base (500–900°C)',
    '2014': 'Chimica organica di base - Cracking (700–1100°C)',
    '2015': 'Fabbricazione di fertilizzanti e composti azotati (700–900°C)',
    '2016': 'Materie plastiche primarie (700–1100°C)',
    '2311': 'Fabbricazione di vetro piano (~1500°C)',
    '2313': 'Fabbricazione di vetro cavo (~1500°C)',
    '2320': 'Fabbricazione di prodotti refrattari (1200–1600°C)',
    '2332': 'Fabbricazione di mattoni e tegole (900–1200°C)',
    '2351': 'Produzione di cemento (1400–1500°C)',
    '2352': 'Produzione di calce e gesso (900–1200°C)',
    '2410': 'Produzione di ferro, acciaio e ferroleghe (1200–1600°C)',
    '2431': 'Trafilatura a freddo (600–1000°C)',
    '2442': 'Produzione di alluminio e semilavorati (660–750°C)',
    '2443': 'Produzione di rame e semilavorati (1000–1200°C)',
    '2444': 'Produzione di altri metalli non ferrosi (400–1200°C)',
    '2451': 'Fusione di ghisa (1200–1400°C)',
    '2452': 'Fusione di acciaio (1400–1600°C)',
    '2453': 'Fusione di metalli leggeri (650–1650°C)',
    '2550': 'Fucinatura, stampaggio e profilatura metalli (900–1200°C)',
    '2561': 'Trattamento e rivestimento dei metalli (500–1100°C)',
    '2562': 'Lavorazioni meccaniche termiche (500–900°C)',
    '3511': 'Produzione energia elettrica da fonti fossili (600–1200°C)',
    '3530': 'Produzione di vapore industriale (500–900°C)',
    '3821': 'Trattamento rifiuti non pericolosi - Incenerimento (850–1100°C)',
    '3822': 'Trattamento rifiuti pericolosi - Incenerimento (1000–1200°C)',
    '3832': 'Recupero rottami metallici (600–1500°C)'
}

# --- DIZIONARIO ATECO MACRO (2 Cifre - Fallback) ---
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

# --- LOGICA DI SCORING (Versione 6.2 - Neutralità Tecnologica & Termodinamica) ---
def get_base_score(row):
    ateco = str(row.get('codice ateco', '')).replace('.', '').strip()
    prefix = ateco[:2]
    testo_tecnico = (str(row.get('processo', '')) + " " + str(row.get('note', ''))).lower()
    
    # ---------------------------------------------------------
    # 1. SPRECO TERMODINAMICO E NON NECESSARI (Score 0)
    # ---------------------------------------------------------
    if prefix in ['35']: 
        return 0, "Produzione Energia/Vapore", "🔴 NON NECESSARIO: Spreco termodinamico. Elettrificare, usare pompe di calore o biomasse."
    if prefix in ['38']: 
        return 0, "Gestione Rifiuti", "🔴 NON NECESSARIO: Waste-to-Hydrogen possibile per produzione, ma spreco come consumo."
    if prefix in ['41', '42', '43'] or ateco.startswith('63'): 
        return 0, "Edilizia/Data Center", "🔴 NON NECESSARIO: Calore a bassa temp. / Elettricità pura. Elettrificazione diretta."
    if ateco.startswith('2011'): 
        return 0, "Produzione Gas (SMR)", "🔴 NON NECESSARIO COME INPUT: L'impianto inquina e va sostituito con elettrolisi."
    if ateco.startswith('2013') or ateco.startswith('1910'): 
        return 0, "Sottoprodotto Industriale", "🔴 NON NECESSARIO: Idrogeno di scarto (Cloro-soda/Cokeria), escluso da quote RED III."

    # ---------------------------------------------------------
    # 2. ASSOLUTAMENTE NECESSARIO (Feedstock / Agente Riducente)
    # ---------------------------------------------------------
    if ateco.startswith('2015') or ateco.startswith('2014') or ateco.startswith('1920'):
        if 'etilene' in testo_tecnico or 'plastica' in testo_tecnico:
            return 0, "Sottoprodotto Cracking", "🔴 NON NECESSARIO: H2 di scarto da Steam Cracking."
        return 5, "Chimica/Raffinazione (Feedstock)", "🟢 ASSOLUTAMENTE NECESSARIO: H2 richiesto chimicamente come materia prima. Obbligo RED III."
    
    if ateco.startswith('2410') and any(k in testo_tecnico for k in ['dri', 'riduzione diretta']):
        return 5, "Siderurgia (Ciclo DRI)", "🟢 ASSOLUTAMENTE NECESSARIO: H2 insostituibile come agente riducente per il minerale di ferro."

    # ---------------------------------------------------------
    # 3. NECESSARIO PER LIMITI FISICI (Calore Estremo)
    # ---------------------------------------------------------
    if ateco.startswith('2311') or ateco.startswith('2313'):
        return 4.5, "Fusione Vetro (Grandi Impianti)", "🟢 NECESSARIO: Difficile elettrificare forni fusori >80t/g per limiti fisici degli elettrodi."

    # ---------------------------------------------------------
    # 4. OPZIONALE / COMPETIZIONE (Calcinazione)
    # ---------------------------------------------------------
    if ateco in ['2351', '2352', '2320', '2332']:
        return 3, "Calcinazione (Cemento/Ceramica/Calce)", "🟡 OPZIONALE: Elevata competizione economica con Biometano e CSS (Combustibili Solidi Secondari)."

    # ---------------------------------------------------------
    # 5. ALERT ELETTRIFICAZIONE (Trattamenti Termici)
    # ---------------------------------------------------------
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

# --- GENERATORE DI TEMPLATE EXCEL (FASE 1) ---
def generate_template_fase1():
    output = BytesIO()
    cols = [
        "nome azienda", "Codice ateco", "dimensione", "fatturato [M€]", 
        "dipendenti", "ubicazione/consorzio", "vicinanza South H2 corridor", 
        "AIA (si/no)", "consumo energia stimato [MWh]", "processo", "note"
    ]
    example_data = [
        ["Fertilizzanti FVG S.p.A.", "20.15", "Grande", 250, 600, "Z.I. Aussa Corno", "SÌ", "SÌ", 150000, "Sintesi Ammoniaca", "Target RED III"],
        ["Vetreria Nord S.r.l.", "23.13", "Grande", 80, 150, "SÌ", "NO", "SÌ", 45000, "Forni fusori continui", ">100t/giorno"],
        ["Acciaierie Anomale", "24.99.00", "Grande", 120, 200, "NO", "SÌ", "SÌ", 80000, "Riscaldo metalli", "Codice anomalo per testare l'alert"],
        ["Elettronica S.r.l.", "26.01", "Media", 15, 40, "Z.I. Maniago", "NO", "NO", 5000, "Saldatura", "Uso di fornetti termici"],
    ]
    df_temp = pd.DataFrame(example_data, columns=cols)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_temp.to_excel(writer, index=False, sheet_name='Template_Screening')
    return output.getvalue()

# --- GENERATORE DI TEMPLATE EXCEL (FASE 2) ---
def generate_template_fase2():
    output = BytesIO()
    cols = [
        "nome azienda", "dimensione azienda", "codice ateco", "fabbisogno identificato [t/y]"
    ]
    example_data = [
        ["Fertilizzanti FVG S.p.A.", "Grande", "20.15", 4500.5],
        ["Vetreria Nord S.r.l.", "Grande", "23.13", 1250.0],
        ["Acciaierie Anomale", "Grande", "24.99.00", 2800.0]
    ]
    df_temp = pd.DataFrame(example_data, columns=cols)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_temp.to_excel(writer, index=False, sheet_name='Template_Fabbisogni')
    return output.getvalue()

# --- INTERFACCIA ---
st.title("🚀 H2READY Scouting Tool - Filtro Termodinamico & RED III")

with st.expander("📖 ISTRUZIONI E METODOLOGIA (Leggi prima di iniziare)", expanded=True):
    st.markdown("""
    ### 1. Come funziona il Tool e i Codici ATECO
    Il motore logico analizza i codici ATECO incrociandoli con la **Direttiva Europea RED III** e con le **leggi della termodinamica**. Non si limita a cercare chi usa genericamente "alte temperature", ma individua dove l'idrogeno è **chimicamente insostituibile** (es. acciaierie DRI, fertilizzanti) e dove invece rappresenta uno spreco energetico rispetto alla diretta elettrificazione.
    
    **Nota sui Codici ATECO:** Il tool legge solo le prime 4 cifre del codice (la *Classe*), ignorando le ultime due. ATTENZIONE: Noto il nome dell'azienda con semplici ricerche online è possibile recuperare facilmente la dimensione aziendale, il codice ATECO e il fatturato aziendale.
    
    ### 2. FASE 1: Screening Iniziale
    Scarica il **Template 1 (Screening)** tramite il bottone qui sotto e compilalo. 
    * 🔴 **Colonne Obbligatorie:** `nome azienda`, `Codice ateco`, `dimensione`.
    * 🟢 **Colonne di Approfondimento:** Compilare `processo` e `note` permette al tool di intercettare falsi positivi o keyword specifiche (es. "altoforno").
    """)
    
    template_bin_1 = generate_template_fase1()
    st.download_button(
        label="📥 1. Scarica Template Screening (Fase 1)",
        data=template_bin_1, file_name="template_screening_h2ready.xlsx", mime="application/vnd.ms-excel"
    )

    st.markdown("""
    ### 3. FASE 2: Mappatura Fabbisogni (Per Action Plan)
    Una volta identificate le aziende idonee tramite la Fase 1, usa il **Template 2 (Fabbisogni)** per inserire i dati quantitativi. 
    Questo file è **fondamentale**: i dati caricati in questo formato verranno processati dal sistema centrale (via Zapier) per generare il **Piano d'Azione (Action Plan)** definitivo del Comune.
    """)
    
    template_bin_2 = generate_template_fase2()
    st.download_button(
        label="📥 2. Scarica Template Fabbisogni (Fase 2)",
        data=template_bin_2, file_name="template_fabbisogni_h2ready.xlsx", mime="application/vnd.ms-excel"
    )

    st.markdown("""
    ### 4. Gli Esiti Termodinamici
    * 🟢 **Assolutamente Necessario:** H2 come materia prima o Agente Riducente.
    * 🟢 **Necessario (Limiti Fisici):** Grandi forni fusori difficili da elettrificare.
    * 🟡 **Opzionale / Competizione:** Competizione economica con Biometano e CSS.
    * 🟠 **Alert Elettrificazione:** Tecnologie come l'induzione elettrica sono più efficienti dell'H2.
    * 🔴 **Spreco Termodinamico:** Produzione di vapore o energia di rete. L'idrogeno qui è uno spreco.
    """)

st.markdown("---")

# ==========================================
# SEZIONE UPLOAD - FASE 1
# ==========================================
st.header("📤 FASE 1: Caricamento e Analisi Termodinamica")
st.write("Carica qui il file di screening per ottenere la valutazione di idoneità delle aziende mappate.")
uploaded_file_1 = st.file_uploader("Carica il database di screening (.xlsx o .csv)", type=["xlsx", "csv"], key="fase1")

if uploaded_file_1:
    try:
        df = pd.read_csv(uploaded_file_1) if uploaded_file_1.name.endswith('.csv') else pd.read_excel(uploaded_file_1)
        df.columns = df.columns.str.strip().str.lower()
        
        # Estrazione dei 3 valori (Base Score, Profilo, Esito Termodinamico)
        results = df.apply(lambda r: get_base_score(r), axis=1)
        df['base_score'] = [res[0] for res in results]
        df['profilo'] = [res[1] for res in results]
        df['esito'] = [res[2] for res in results]
        
        df['score'] = df.apply(calculate_total_score, axis=1)
        df['tier'] = df['score'].apply(lambda s: "Tier 1 (Alta Priorità)" if s >= 7 else ("Tier 2 (Media/Alert)" if s > 0 else "Non Idoneo"))
        
        df_idonee = df[df['score'] > 0].sort_values(by='score', ascending=False)

        # KPI
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Aziende Analizzate", len(df))
        c2.metric("Semaforo Verde (Tier 1)", len(df[df['score'] >= 7]))
        c3.metric("Alert Elettrificazione (Tier 2)", len(df[(df['score'] > 0) & (df['score'] < 7)]))
        c4.metric("Spreco Termodinamico (Scartate)", len(df[df['score'] == 0]))

        st.markdown("### 🏢 Cruscotto Aziendale - Analisi Termodinamica")
        if not df_idonee.empty:
            cols_per_row = 2 
            for i in range(0, len(df_idonee), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(df_idonee):
                        row = df_idonee.iloc[i + j]
                        with cols[j]:
                            # Intestazione Visiva
                            if "Tier 1" in row['tier']: 
                                st.success(f"### 🏭 {row['nome azienda']}")
                            else: 
                                st.warning(f"### 🏭 {row['nome azienda']}")
                            
                            st.write(f"🏆 **Score Complessivo:** {row['score']} / 15")
                            st.write(f"📏 **Dimensione Aziendale:** {str(row.get('dimensione', 'N/D')).title()}")
                            
                            # --- LOGICA A CASCATA PER DIZIONARIO ATECO ---
                            codice_originale = str(row.get('codice ateco', 'N/D'))
                            codice_pulito = codice_originale.replace('.', '').strip()[:4]
                            
                            if codice_pulito in ATECO_DESCRIPTIONS:
                                descrizione_estesa = ATECO_DESCRIPTIONS[codice_pulito]
                                st.write(f"⚙️ **ATECO {codice_originale}:** *{descrizione_estesa}*")
                            else:
                                # Fallback a 2 cifre
                                codice_macro = codice_pulito[:2]
                                descrizione_macro = MACRO_ATECO_DESCRIPTIONS.get(codice_macro, "Settore economico generico")
                                st.write(f"⚙️ **ATECO {codice_originale} (Divisione {codice_macro}):** *{descrizione_macro}*")
                                st.warning("⚠️ **Codice ATECO non compreso nel database prioritario per l'idrogeno.** Ti suggeriamo di verificare il codice o assicurarti di aver dettagliato correttamente il processo termico nelle note.")
                            
                            processo_dichiarato = str(row.get('processo', '')).strip()
                            if processo_dichiarato.lower() != 'nan' and processo_dichiarato:
                                st.write(f"🔥 **Processo Dichiarato:** {processo_dichiarato}")
                            
                            # --- ESITO TERMODINAMICO ---
                            st.markdown(f"**💡 Esito Termodinamico:**")
                            esito_txt = row['esito']
                            if '🟢' in esito_txt: st.info(esito_txt)
                            elif '🟡' in esito_txt: st.warning(esito_txt)
                            elif '🟠' in esito_txt: st.error(esito_txt) 
                            
                            note_txt = str(row.get('note', '')).strip()
                            if note_txt.lower() != 'nan' and note_txt:
                                st.caption(f"📝 Note aggiuntive: {note_txt}")
                            st.markdown("---")
        else:
            st.info("Nessuna azienda idonea. Tutti i processi analizzati risultano più adatti all'elettrificazione diretta.")

        with st.expander("📂 Esplora il Database Completo (Inclusi gli scartati)"):
            st.dataframe(df[['nome azienda', 'codice ateco', 'score', 'tier', 'profilo', 'esito']].sort_values(by='score', ascending=False), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Errore: Assicurati che le colonne siano corrette. Dettaglio tecnico: {e}")

# ==========================================
# SEZIONE UPLOAD - FASE 2 (EXPORT ZAPIER)
# ==========================================
st.markdown("---")
st.header("📤 FASE 2: Consolidamento Fabbisogni (Export per Action Plan)")
st.info("Carica qui il **Template 2 (Fabbisogni)** compilato con le stime in tonnellate/anno (t/y). Questo modulo estrarrà i dati formattati per l'invio automatico al Database Centrale dei Piani d'Azione.")

uploaded_file_2 = st.file_uploader("Carica il database Fabbisogni (.xlsx o .csv)", type=["xlsx", "csv"], key="fase2")

if uploaded_file_2:
    try:
        df2 = pd.read_csv(uploaded_file_2) if uploaded_file_2.name.endswith('.csv') else pd.read_excel(uploaded_file_2)
        
        st.success("✅ Dati Fabbisogni validati correttamente! Le informazioni sottostanti sono pronte per generare l'Action Plan.")
        
        # Mostra i dati per conferma utente
        st.dataframe(df2, use_container_width=True, hide_index=True)
        
        # Calcolo aggregato veloce
        if 'fabbisogno identificato [t/y]' in df2.columns:
            totale_h2 = df2['fabbisogno identificato [t/y]'].sum()
            st.metric("Fabbisogno Totale Aggregato", f"{totale_h2:,.1f} ton/anno")
            
    except Exception as e:
        st.error(f"Errore nella lettura del file Fabbisogni. Dettaglio tecnico: {e}")
