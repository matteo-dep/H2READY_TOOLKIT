import streamlit as st
import numpy as np
import os
import requests
import json

# ==========================================
# 1. CONFIGURAZIONE PAGINA E LINGUA
# ==========================================
st.set_page_config(page_title="H2READY TOOLKIT - Tool 2.8", layout="wide")

LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_choice = st.sidebar.selectbox("🌐 Lingua / Language / Jezik", list(LANG_OPTIONS.keys()))
LANG = LANG_OPTIONS[lang_choice]

# Dizionario per le label dell'interfaccia (Solo parte Tecnica)
T = {
    "it": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.8: Dimensionamento e Design Tecno-Economico HRS",
        "credits": "Sviluppato all'interno del progetto [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 GUIDA OPERATIVA (Leggi prima di iniziare)",
        "logic_title": "🧠 Analisi Metodologica e Standard di Progettazione",
        "instructions_md": """
### 🎯 Qual è il tuo obiettivo?
Questo strumento serve a dimensionare l'architettura tecnica e a stimare l'impatto economico di una **Stazione di Rifornimento a Idrogeno (HRS)** per mezzi pesanti nel territorio comunale.

**Istruzioni:**
1. Configura **tutti i parametri tecnici nella barra laterale sinistra**: seleziona la configurazione strategica dell'impianto, inserisci la flotta veicolare prevista e i vincoli di compressione.
2. Clicca sul grande bottone **'Avvia Dimensionamento Impiantistico'** qui sotto per generare il report tecno-economico unificato in tempo reale.
        """,
        "sb_config": "🏗️ Configurazione Strategica",
        "sb_tech": "⚡ Parametri Tecnici HRS",
        
        # Inputs Tecnici
        "lbl_conf_type": "Configurazione Impianto Obiettivo",
        "conf_c1": "HRS di Transito Puro (Flussi di passaggio autostradali)",
        "conf_c2": "HRS Hub Intermodale Multi-Mezzo (Porti/Interporti + Mezzi interni)",
        "conf_c3": "HRS Valley Strategica Integrata (Allacciamento tubo Snam / Industria)",
        "lbl_cars": "Auto private / flotta leggera (4.5 kg/pieno)",
        "lbl_buses": "Autobus TPL / Mezzi Speciali (30 kg/pieno)",
        "lbl_trucks": "Camion Pesanti a lungo raggio (50 kg/pieno)",
        "lbl_window": "Finestra di Rifornimento (ore/giorno)",
        "lbl_cf": "Fattore di Carico Stazione (Capacity Factor %)",
        "lbl_source": "Sorgente e Pressione di Ingresso H2",
        "lbl_routing": "Architettura di Compressione/Storage",
        "lbl_dispenser": "Pressione di Erogazione Finale",
        
        # Pulsanti e Risultati
        "btn_calc": "🚀 Avvia Dimensionamento Impiantistico HRS",
        "section_verdict": "⚖️ Architettura Impianto Selezionata",
        "section_tech": "⚙️ Dimensionamento Termodinamico e Impiantistico",
        "section_econ": "💶 Analisi Economica Parametrica (LCOH / CAPEX)",
        "section_space": "📐 Footprint Territoriale e Vincoli Legali (DM 2018)",
        
        # Profili
        "v_c1": "🟡 CONFIGURAZIONE 'HRS DI TRANSITO PURO': Ottimizzata per flussi autostradali di passaggio. L'approvvigionamento della molecola avviene dall'esterno tramite carro bombolaio.",
        "v_c2": "🟢 CONFIGURAZIONE 'HRS HUB INTERMODALE MULTI-MEZZO': Ottimizzata per porti o interporti. Include i consumi della flotta logistica residente interna (es. muletti, gru, manovre).",
        "v_c3": "🔵 CONFIGURAZIONE 'HRS VALLEY STRATEGICA INTEGRATA': Massimo livello di efficienza. Costi logistici minimizzati grazie al collegamento diretto alla condotta a tubo Snam o produzione in situ.",
        
        "input_id": "Inserisci il Codice Identificativo per l'esportazione (es. 030043):",
        "btn_export": "💾 Esporta Report nel Database Centrale",
        "export_success": "✅ Dati del design impiantistico trasmessi con successo!"
    },
    "en": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.8: HRS Sizing and Techno-Economic Design",
        "credits": "Developed within the [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) project by **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 OPERATIONAL GUIDE (Read before starting)",
        "logic_title": "🧠 Methodological Analysis and Engineering Standards",
        "instructions_md": """
### 🎯 What is your goal?
This tool sizes the technical architecture and estimates the economic impact of a **Hydrogen Refuelling Station (HRS)** for heavy duty vehicles.

**Instructions:**
1. Configure **all technical parameters in the left sidebar**: select the target architecture, input the fleet size, and compression constraints.
2. Click **'Avvia Dimensionamento Impiantistico'** below to generate the unified report.
        """,
        "sb_config": "🏗️ Strategic Configuration",
        "sb_tech": "⚡ HRS Technical Parameters",
        "lbl_conf_type": "Target Station Architecture",
        "conf_c1": "Pure Transit HRS (Highway corridor flows)",
        "conf_c2": "Intermodal Hub HRS (Ports/Interports + Material handling)",
        "conf_c3": "Strategic Valley HRS (Snam Pipeline connection / On-site)",
        "lbl_cars": "Private cars / light fleet (4.5 kg/refuel)",
        "lbl_buses": "PT Buses / Special Vehicles (30 kg/refuel)",
        "lbl_trucks": "Long-haul Heavy Trucks (50 kg/refuel)",
        "lbl_window": "Refuelling Window (hours/day)",
        "lbl_cf": "Station Load Factor (Capacity Factor %)",
        "lbl_source": "H2 Source and Inlet Pressure",
        "lbl_routing": "Compression/Storage Architecture",
        "lbl_dispenser": "Final Dispensing Pressure",
        "btn_calc": "🚀 Run Plant Sizing & Analysis",
        "section_verdict": "⚖️ Selected Station Architecture",
        "section_tech": "⚙️ Thermodynamic and Plant Sizing",
        "section_econ": "💶 Parametric Economic Analysis (CAPEX)",
        "section_space": "📐 Territorial Footprint and Legal Constraints",
        "v_c1": "🟡 'PURE TRANSIT HRS' CONFIGURATION: Optimized for highway transit. Tube-trailer supply selected (higher molecule logistics costs).",
        "v_c2": "🟢 'INTERMODAL HUB HRS' CONFIGURATION: Optimized for ports/interports. Covers heavy-duty handling equipment (forklifts, cranes).",
        "v_c3": "🔵 'STRATEGIC VALLEY HRS' CONFIGURATION: Maximum efficiency level. Minimal logistics costs enabled due to pipeline connection or industrial synergy.",
        "input_id": "Enter Identification Code for export (e.g. 030043):",
        "btn_export": "💾 Export Report to Central Database",
        "export_success": "✅ Plant design data transmitted successfully!"
    }
}

if LANG == "sl":
    _t = T["en"]
    _t["title"] = "🚀 H2READY TOOLKIT - Orodje 2.8: Tehnično dimenzioniranje vodikovih črpalk HRS"
else:
    _t = T[LANG]

# ==========================================
# 2. INTESTAZIONE PRINCIPALE
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

with st.expander(_t["instr_title"], expanded=True):
    st.markdown(_t["instructions_md"])

with st.expander(_t["logic_title"], expanded=False):
    nome_file_logica = f"logic_logistica_{LANG}.md"
    if os.path.exists(nome_file_logica):
        with open(nome_file_logica, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.caption(f"ℹ️ File di analisi metodologica estesa '{nome_file_logica}' caricato esternamente.")

st.markdown("---")

# ==========================================
# 3. BARRA LATERALE SINISTRA (INPUT TECNICI DIRETTI)
# ==========================================
with st.sidebar:
    # --- SELEZIONE PROFILO ---
    with st.expander(_t["sb_config"], expanded=True):
        config_scelta = st.selectbox(_t["lbl_conf_type"], [_t["conf_c1"], _t["conf_c2"], _t["conf_c3"]])

    # --- PARAMETRI TECNICI ---
    with st.expander(_t["sb_tech"], expanded=True):
        n_auto = st.slider(_t["lbl_cars"], 0, 100, 10, step=5)
        n_bus = st.slider(_t["lbl_buses"], 0, 50, 5, step=1)
        n_camion = st.slider(_t["lbl_trucks"], 0, 150, 30, step=5)
        finestra_ore = st.slider(_t["lbl_window"], 1, 24, 8)
        capacity_factor = st.slider(_t["lbl_cf"], 10, 100, 75) / 100.0
        fonte_h2 = st.selectbox(_t["lbl_source"], ["Elettrolizzatore (20 bar)", "Pipeline Snam (30 bar)", "Carro Bombolaio (200 bar)"])
        routing_logic = st.selectbox(_t["lbl_routing"], ["Magazzino a Cascata (3 banchi)", "Booster Compressor (Diretta)"])
        dispenser_press = st.radio(_t["lbl_dispenser"], ["350 bar (Bus)", "700 bar (Camion/Auto)"])

# ==========================================
# 4. BOTTONE DI CALCOLO E REPORT UNIFICATO
# ==========================================
btn_calcolo = st.button(_t["btn_calc"], type="primary", use_container_width=True)

if btn_calcolo:
    # --- MAPPA PROFILO SELEZIONATO PER LOGICA COSTI ---
    if config_scelta == _t["conf_c3"]:
        profilo_design = "VALLEY STRATEGICA"
    elif config_scelta == _t["conf_c2"]:
        profilo_design = "HUB INTERMODALE"
    else:
        profilo_design = "TRANSITO PURO"

    # --- OUTPUT SEZIONE 1: ARCHITETTURA ---
    st.header(_t["section_verdict"])
    if profilo_design == "VALLEY STRATEGICA":
        st.info(_t["v_c3"])
    elif profilo_design == "HUB INTERMODALE":
        st.success(_t["v_c2"])
    else:
        st.warning(_t["v_c1"])

    # --- 1. MODULO DI CALCOLO DELLA DOMANDA ---
    fabbisogno_teorico = (n_auto * 4.5) + (n_bus * 30) + (n_camion * 50)
    fabbisogno_reale_kg_giorno = fabbisogno_teorico * capacity_factor
    
    if fabbisogno_reale_kg_giorno == 0:
        st.error("Inserisci almeno un veicolo commerciale per effettuare il dimensionamento.")
        st.stop()
        
    # --- 2. PARAMETRI TERMODINAMICI FISSI ---
    Cp = 14.5; k_ad = 1.41; eta_isentropico = 0.60; T_ingresso = 293.15; stadi = 3; overcapacity_factor = 1.9
    
    # Pressioni in bar
    P_inlet = 20 if "Elettrolizzatore" in fonte_h2 else (30 if "Pipeline" in fonte_h2 else 200)
    P_dispensazione = 350 if "350 bar" in dispenser_press else 700
    P_stoccaggio_max = P_dispensazione + 150 # Margine tampone
    
    # Logiche di usabilità e tempistiche in base all'architettura di compressione
    if "Cascata" in routing_logic:
        efficienza_motore = 0.88
        fattore_usabilita = 0.91
        costo_storage_unitario = 1092
        ore_lavoro_compressore = 20 # Funzionamento lento continuo nelle 24h
    else: # Booster
        efficienza_motore = 0.92
        fattore_usabilita = 0.95
        costo_storage_unitario = 968
        ore_lavoro_compressore = finestra_ore # Lavora forzato solo nella finestra di picco

    # Calcolo Portata di picco e Dimensionamento Serbatoi
    portata_kg_s = fabbisogno_reale_kg_giorno / (ore_lavoro_compressore * 3600)
    stoccaggio_fisico_kg = (fabbisogno_reale_kg_giorno * overcapacity_factor) / fattore_usabilita

    # --- 3. EQUAZIONI DI COMPRESSIONE MULTISTADIO INTER-REFRIGERATA ---
    beta_tot = P_stoccaggio_max / P_inlet
    beta_singolo_stadio = beta_tot ** (1 / stadi)
    T_scarico_stadio = T_ingresso * (beta_singolo_stadio ** ((k_ad - 1) / k_ad))
    lavoro_isentropico = Cp * (T_scarico_stadio - T_ingresso) # kJ/kg
    lavoro_reale_refrigerato = (lavoro_isentropico / eta_isentropico) * stadi
    
    potenza_reale_kW = lavoro_reale_refrigerato * portata_kg_s
    potenza_elettrica_nominale_kW = potenza_reale_kW / efficienza_motore
    consumo_specifico_kwh_kg = lavoro_reale_refrigerato / 3600 / efficienza_motore

    # --- OUTPUT SEZIONE 2: TECNICA ---
    st.header(_t["section_tech"])
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Domanda alla Pompa", f"{fabbisogno_reale_kg_giorno:,.1f} kg/giorno")
    t2.metric("Stoccaggio Fisico Richiesto", f"{stoccaggio_fisico_kg:,.0f} kg")
    t3.metric("Potenza Compressione Nominale", f"{potenza_elettrica_nominale_kW:,.1f} kW")
    t4.metric("Consumo Energia Compressione", f"{consumo_specifico_kwh_kg:,.2f} kWh/kg")
    
    st.caption(f"ℹ️ **Parametri di Processo:** Rapporto di compressione totale pari a {beta_tot:.1f}. Temperatura di scarico interstadio stimata a {T_scarico_stadio - 273.15:.1f} °C. Sistema di pre-raffreddamento forzato impostato a {'-40 °C (SAE J2601 - per rifornimento veloce a 700 bar)' if P_dispensazione==700 else '-20 °C (erogazione standard a 350 bar)'}.")

    # --- OUTPUT SEZIONE 3: ECONOMICA ---
    st.header(_t["section_econ"])
    # Calcolo CAPEX parametrico
    costo_serbatoi = stoccaggio_fisico_kg * costo_storage_unitario
    costo_macchinario_compressione = potenza_elettrica_nominale_kW * 2500
    costo_dispenser = 200000 * (1.3 if P_dispensazione == 700 else 1.0)
    costo_refrigerazione = 120000 if P_dispensazione == 700 else 60000
    
    capex_base = costo_serbatoi + costo_macchinario_compressione + costo_dispenser + costo_refrigerazione
    capex_finito_opere_civili = capex_base * 1.25 # +25% per l'allestimento del cantiere e sicurezza
    
    ec1, ec2, ec3 = st.columns(3)
    ec1.metric("CAPEX Modulo Stoccaggio", f"€ {costo_serbatoi:,.0f}")
    ec2.metric("CAPEX Modulo Compressione", f"€ {costo_macchinario_compressione:,.0f}")
    ec3.metric("CAPEX Totale Chiavi in Mano", f"€ {capex_finito_opere_civili:,.0f}")

    # --- OUTPUT SEZIONE 4: REQUISITI SPAZIALI ---
    st.header(_t["section_space"])
    area_macchinari_netta = (stoccaggio_fisico_kg * 0.15) + (potenza_elettrica_nominale_kW * 0.5)
    area_legale_con_vincoli = area_macchinari_netta * 9.5 # Fattore moltiplicativo DM 23 ottobre 2018
    
    st.warning(f"⚠️ **Vincolo Decreto Ministeriale 23/10/2018 (Antincendio):** L'ingombro dei componenti fisici richiede circa {area_macchinari_netta:,.1f} m². Per garantire le distanze di sicurezza stradali, interne (15 metri tra elementi pericolosi) e verso confini pubblici di terzi (30 metri), l'Ente deve identificare un lotto di terreno con una superficie minima reale di **{area_legale_con_vincoli:,.0f} m²**.")

    # --- SEZIONE ESPORTAZIONE DATI IN FONDO AL FOGLIO ---
    st.divider()
    st.subheader("🔗 Invio e Consolidamento Master Database")
    id_comune_logistica = st.text_input(_t["input_id"], key="id_log")
    
    if st.button(_t["btn_export"]):
        if not id_comune_logistica:
            st.error("Inserisci il codice identificativo comunale prima di procedere al salvataggio.")
        else:
            payload_logistica = {
                "ID_ISTAT": id_comune_logistica,
                "T28_PROFILO_ARCHITETTURA": profilo_design,
                "T28_PUNTEGGIO_SCORECARD": 999, # Flag per indicare inserimento diretto senza questionario
                "T28_CAPACITA_KG_GIORNO": round(fabbisogno_reale_kg_giorno, 1),
                "T28_POTENZA_COMPRESSORE_KW": round(potenza_elettrica_nominale_kW, 1),
                "T28_STOCCAGGIO_FISICO_KG": round(stoccaggio_fisico_kg, 0),
                "T28_CAPEX_COMPLESSIVO_EURO": round(capex_finito_opere_civili, 0),
                "T28_SUPERFICIE_MINIMA_M2": round(area_legale_con_vincoli, 0)
            }
            GOOGLE_URL = "https://script.google.com/macros/s/AKfycbwpP0x0hBnhOadXA43IieWg9EusAuhaafpyeXpyaStssDd7Qo-jwnuOttAllzz8r5JS/exec"
            try:
                headers = {'Content-Type': 'application/json'}
                response = requests.post(GOOGLE_URL, data=json.dumps(payload_logistica), headers=headers, allow_redirects=True)
                if response.status_code in [200, 201]:
                    st.success(_t["export_success"])
                    st.balloons()
                else:
                    st.error(f"Errore di sincronizzazione con il foglio centrale (Codice {response.status_code})")
            except Exception as e:
                st.error(f"Errore durante l'invio HTTP: {e}")
