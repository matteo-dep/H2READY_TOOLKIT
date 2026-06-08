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

# Dizionario per le label dell'interfaccia
T = {
    "it": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.8: Valutazione Nodo Logistico e HRS",
        "credits": "Sviluppato all'interno del progetto [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 GUIDA OPERATIVA (Leggi prima di iniziare)",
        "logic_title": "🧠 Criteri di Screening e Analisi Metodologica",
        "instructions_md": """
### 🎯 Qual è il tuo obiettivo?
Questo strumento serve a identificare l'idoneità infrastrutturale del tuo Comune e a determinare quale specifica configurazione di Stazione di Rifornimento a Idrogeno (HRS) sia giustificata.

**Istruzioni:**
1. Configura **tutti i parametri nella barra laterale sinistra**: inserisci i dati di screening della Fase 1, i criteri abilitanti della Fase 2 e le stime sui veicoli commerciali.
2. Clicca sul grande bottone **'Avvia Analisi e Dimensionamento'** qui sotto per generare il report tecno-economico unificato in tempo reale.
        """,
        "sb_fase1": "📋 FASE 1: Screening Infrastrutturale",
        "sb_fase2": "🤝 FASE 2: Criteri Abilitanti",
        "sb_tech": "⚡ FASE 3: Parametri Tecnici HRS",
        
        # Domande Fase 1
        "q_tent": "Corridoi Europei Core (TEN-T) attigui",
        "q_auto": "Interconnessione Autostradale Diretta (Caselli)",
        "q_afir": "Copertura rete europea (Tratta scoperta AFIR <100km)",
        "q_tgm": "Intensità del Flusso Pesante Stradale (TGM > 3.000 camion)",
        "q_var": "Varianti e Pianificazioni Strategiche (es. SS354/Murlis)",
        "q_hub": "Presenza di Hub Merci Principali (Porti/Interporti <5km)",
        "q_hdv": "Logistica Heavy-Duty a grande volume (Treni 750m / Ro-Ro)",
        "q_ret": "Aree Retroportuali e di Stoccaggio merci",
        "q_ferr": "Linee ferroviarie isolate e vincoli strutturali (Diesel)",
        "q_snam": "Dorsale PCI (South H2 Corridor) nel territorio",
        "q_hta": "Sinergia Distrettuale Industriale Hard-to-Abate",
        
        # Domande Fase 2
        "g_acc": "Accordi di Filiera e Logistica Integrata (+5)",
        "g_joint": "Propensione al Joint Procurement Transfrontaliero (+5)",
        "g_pums": "Pianificazione della Mobilità Merci - PUMS/PAESC (+3)",
        "g_stor": "Disponibilità di Aree per Storage ad Alta Pressione (+4)",
        "g_cap": "Capacity Building Tecnico-Amministrativo (+3)",
        
        # Inputs Tecnici
        "lbl_cars": "Auto private / flotta leggera (4.5 kg/pieno)",
        "lbl_buses": "Autobus TPL / Mezzi Speciali (30 kg/pieno)",
        "lbl_trucks": "Camion Pesanti a lungo raggio (50 kg/pieno)",
        "lbl_window": "Finestra di Rifornimento (ore/giorno)",
        "lbl_cf": "Fattore di Carico Stazione (Capacity Factor %)",
        "lbl_source": "Sorgente e Pressione di Ingresso H2",
        "lbl_routing": "Architettura di Compressione/Storage",
        "lbl_dispenser": "Pressione di Erogazione Finale",
        
        # Pulsanti e Risultati
        "btn_calc": "🚀 Avvia Analisi e Dimensionamento HRS",
        "section_scores": "📊 Esito dello Screening e Punteggi Totali",
        "section_verdict": "⚖️ Verdetto Ammissibilità Tecnica",
        "section_tech": "⚙️ Dimensionamento Termodinamico e Impiantistico",
        "section_econ": "💶 Analisi Economica Parametrica (LCOH / CAPEX)",
        "section_space": "📐 Footprint Territoriale e Vincoli Legali (DM 2018)",
        
        # Verdetti
        "v_nogo": "🔴 NON IDONEO H2 (Score < 25): Il territorio non ha la massa critica stradale o logistica richiesta. Deviare la pianificazione esclusivamente verso colonnine elettriche rapide BEV.",
        "v_c1": "🟡 CONFIGURAZIONE 'HRS DI TRANSITO PURO': Sbloccato il design autostradale per flussi di passaggio. Approvvigionamento standard impostato via carro bombolaio (costi molecola maggiori).",
        "v_c2": "🟢 CONFIGURAZIONE 'HRS HUB INTERMODALE MULTI-MEZZO': Sbloccato il calcolo per la domanda residente (muletti, gru, manovre). Ottima stabilità finanziaria protetta dai consumi interni.",
        "v_c3": "🔵 CONFIGURAZIONE 'HRS VALLEY STRATEGICA INTEGRATA': Massimo livello. Abilitato l'azzeramento dei costi di trasporto stradale della molecola grazie all'allacciamento via tubo o produzione in situ.",
        
        "input_id": "Inserisci il Codice Identificativo per l'esportazione (es. 030043):",
        "btn_export": "💾 Esporta Report nel Database Centrale",
        "export_success": "✅ Dati del nodo logistico trasmessi con successo!"
    },
    "en": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.8: Logistics Node Evaluation and HRS",
        "credits": "Developed within the [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) project by **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 OPERATIONAL GUIDE (Read before starting)",
        "logic_title": "🧠 Screening Criteria and Methodological Analysis",
        "instructions_md": """
### 🎯 What is your goal?
This tool evaluates the infrastructural suitability of your Municipality and determines which specific Hydrogen Refuelling Station (HRS) configuration is justified.

**Instructions:**
1. Configure **all parameters in the left sidebar**: enter Phase 1 screening data, Phase 2 enabling criteria, and Phase 3 commercial vehicle estimates.
2. Click **'Avvia Analisi e Dimensionamento'** below to generate the unified techno-economic report in real-time.
        """,
        "sb_fase1": "📋 PHASE 1: Infrastructure Screening",
        "sb_fase2": "🤝 PHASE 2: Enabling Criteria",
        "sb_tech": "⚡ PHASE 3: HRS Technical Parameters",
        "q_tent": "Core European Corridors (TEN-T) nearby",
        "q_auto": "Direct Highway Connection (Exits)",
        "q_afir": "European network coverage (AFIR gap <100km)",
        "q_tgm": "Heavy Road Traffic Intensity (TGM > 3,000 trucks)",
        "q_var": "Strategic Bypass Roads / Planned Variants",
        "q_hub": "Presence of Main Freight Hubs (<5km)",
        "q_hdv": "Heavy-Duty High-Volume Logistics (750m trains / Ro-Ro)",
        "q_ret": "Hinterland & Freight Storage Areas",
        "q_ferr": "Isolated Rail Lines & Physical Constraints (Diesel)",
        "q_snam": "PCI Pipeline Backbone (South H2 Corridor)",
        "q_hta": "Hard-to-Abate Industrial District Synergy",
        "g_acc": "Supply Chain & Integrated Logistics Agreements (+5)",
        "g_joint": "Cross-Border Joint Procurement Willingness (+5)",
        "g_pums": "Freight Mobility Planning - PUMS/PAESC (+3)",
        "g_stor": "Availability of High-Pressure Storage Areas (+4)",
        "g_cap": "Technical-Administrative Capacity Building (+3)",
        "lbl_cars": "Private cars / light fleet (4.5 kg/refuel)",
        "lbl_buses": "PT Buses / Special Vehicles (30 kg/refuel)",
        "lbl_trucks": "Long-haul Heavy Trucks (50 kg/refuel)",
        "lbl_window": "Refuelling Window (hours/day)",
        "lbl_cf": "Station Load Factor (Capacity Factor %)",
        "lbl_source": "H2 Source and Inlet Pressure",
        "lbl_routing": "Compression/Storage Architecture",
        "lbl_dispenser": "Final Dispensing Pressure",
        "btn_calc": "🚀 Run Analysis & HRS Sizing",
        "section_scores": "📊 Screening Output and Total Scores",
        "section_verdict": "⚖️ Technical Eligibility Verdict",
        "section_tech": "⚙️ Thermodynamic and Plant Sizing",
        "section_econ": "💶 Parametric Economic Analysis (LCOH / CAPEX)",
        "section_space": "📐 Territorial Footprint and Legal Constraints",
        "v_nogo": "🔴 NOT ELIGIBLE H2 (Score < 25): The area lacks critical mass. Pivot to BEV fast charging instead.",
        "v_c1": "🟡 'PURE TRANSIT HRS' CONFIGURATION: Highway station unlocked. Tube-trailer supply selected (higher molecule costs).",
        "v_c2": "🟢 'INTERMODAL HUB HRS' CONFIGURATION: Resident demand activated (forklifts, cranes). High financial stability.",
        "v_c3": "🔵 'STRATEGIC VALLEY HRS' CONFIGURATION: Maximum level. Zero transport costs enabled due to pipeline connection or on-site production.",
        "input_id": "Enter Identification Code for export (e.g. 030043):",
        "btn_export": "💾 Export Report to Central Database",
        "export_success": "✅ Logistics node data transmitted successfully!"
    }
}

# Semplificazione per la lingua Slovena usando l'Inglese come fallback se non dichiarata del tutto
if LANG == "sl":
    _t = T["en"]
    _t["title"] = "🚀 H2READY TOOLKIT - Orodje 2.8: Ocenjevanje logističnega vozlišča in HRS"
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
# 3. BARRA LATERALE SINISTRA (INPUT VARIABILI)
# ==========================================
with st.sidebar:
    # --- MENÙ FASE 1 ---
    with st.expander(_t["sb_fase1"], expanded=True):
        f1_tent = st.checkbox(_t["q_tent"], value=True)
        f1_auto = st.checkbox(_t["q_auto"], value=True)
        f1_afir = st.checkbox(_t["q_afir"], value=False)
        f1_tgm = st.checkbox(_t["q_tgm"], value=True)
        f1_var = st.checkbox(_t["q_var"], value=False)
        f1_hub = st.checkbox(_t["q_hub"], value=False)
        f1_hdv = st.checkbox(_t["q_hdv"], value=False)
        f1_ret = st.checkbox(_t["q_ret"], value=False)
        f1_ferr = st.checkbox(_t["q_ferr"], value=False)
        f1_snam = st.checkbox(_t["q_snam"], value=False)
        f1_hta = st.checkbox(_t["q_hta"], value=False)

    # --- MENÙ FASE 2 ---
    with st.expander(_t["sb_fase2"], expanded=False):
        f2_acc = st.checkbox(_t["g_acc"], value=False)
        f2_joint = st.checkbox(_t["g_joint"], value=False)
        f2_pums = st.checkbox(_t["g_pums"], value=False)
        f2_stor = st.checkbox(_t["g_stor"], value=False)
        f2_cap = st.checkbox(_t["g_cap"], value=False)

    # --- MENÙ PARAMETRI TECNICI ---
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
# 4. BOTTONE DI CALCOLO E ARCHITETTURA UNICA
# ==========================================
btn_calcolo = st.button(_t["btn_calc"], type="primary", use_container_width=True)

if btn_calcolo:
    # --- CALCOLO PUNTEGGI STRATEGICI FASE 1 ---
    score_C1 = 0
    score_C2 = 0
    score_C3 = 0
    
    if f1_tent: score_C1 += 5
    if f1_auto: score_C1 += 4
    if f1_afir: score_C1 += 3
    if f1_tgm: 
        score_C1 += 5
        score_C2 += 2
    if f1_var: score_C1 += 3
    if f1_hub: score_C2 += 5
    if f1_hdv: score_C2 += 4
    if f1_ret: score_C2 += 3
    if f1_ferr:
        score_C2 += 3
        score_C3 += 1
    if f1_snam: score_C3 += 5
    if f1_hta: score_C3 += 5
    
    # --- CALCOLO PUNTEGGI ABILITANTI FASE 2 ---
    score_fase2 = 0
    if f2_acc: score_fase2 += 5
    if f2_joint: score_fase2 += 5
    if f2_pums: score_fase2 += 3
    if f2_stor: score_fase2 += 4
    if f2_cap: score_fase2 += 3
    
    # Totale combinato per percorso
    tot_C1 = score_C1 + score_fase2
    tot_C2 = score_C2 + score_fase2
    tot_C3 = score_C3 + score_fase2
    punteggio_complessivo = max(tot_C1, tot_C2, tot_C3)

    # --- OUTPUT SEZIONE 1: SCORECARD ---
    st.header(_t["section_scores"])
    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Score C1 (Transito Veloce)", f"{tot_C1} pt")
    sc2.metric("Score C2 (Hub Intermodale)", f"{tot_C2} pt")
    sc3.metric("Score C3 (Distretto/Dorsale)", f"{tot_C3} pt")
    sc4.metric("Punteggio di Picco", f"{punteggio_complessivo} pt", delta="Idoneo" if punteggio_complessivo >= 25 else "Escluso")

    # --- OUTPUT SEZIONE 2: VERDETTO AMMISSIBILITÀ ---
    st.header(_t["section_verdict"])
    profilo_design = "NON IDONEO"
    
    if punteggio_complessivo < 25:
        st.error(_t["v_nogo"])
        profilo_design = "NON IDONEO"
    else:
        # Trova la configurazione impiantistica in base al percorso dominante
        if punteggio_complessivo == tot_C3:
            st.info(_t["v_c3"])
            profilo_design = "VALLEY STRATEGICA"
        elif punteggio_complessivo == tot_C2:
            st.success(_t["v_c2"])
            profilo_design = "HUB INTERMODALE"
        else:
            st.warning(_t["v_c1"])
            profilo_design = "TRANSITO PURO"

    st.markdown("---")

    # --- SE PROFILO IDONEO -> AVVIA PROGETTAZIONE IMPIANTO ---
    if profilo_design != "NON IDONEO":
        # 1. Modulo di Calcolo della Domanda
        fabbisogno_teorico = (n_auto * 4.5) + (n_bus * 30) + (n_camion * 50)
        fabbisogno_reale_kg_giorno = fabbisogno_teorico * capacity_factor
        
        # 2. Parametri Termodinamici Fissi
        R_gas = 8.3144; Cp = 14.5; k_ad = 1.41; eta_isentropico = 0.60; T_ingresso = 293.15; stadi = 3; overcapacity_factor = 1.9
        
        # Pressioni in bar
        P_inlet = 20 if "Elettrolizzatore" in fonte_h2 else (30 if "Pipeline" in fonte_h2 else 200)
        P_dispensazione = 350 if "350 bar" in dispenser_press else 700
        P_stoccaggio_max = P_dispensazione + 150 # Margine tampone
        
        # Logiche di usabilità e tempistiche in base alla topologia scelta
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

        # 3. Equazioni di Compressione Multistadio Inter-refrigerata
        beta_tot = P_stoccaggio_max / P_inlet
        beta_singolo_stadio = beta_tot ** (1 / stadi)
        T_scarico_stadio = T_ingresso * (beta_singolo_stadio ** ((k_ad - 1) / k_ad))
        lavoro_isentropico = Cp * (T_scarico_stadio - T_ingresso) # kJ/kg
        lavoro_reale_refrigerato = (lavoro_isentropico / eta_isentropico) * stadi
        
        potenza_reale_kW = lavoro_reale_refrigerato * portata_kg_s
        potenza_elettrica_nominale_kW = potenza_reale_kW / efficienza_motore
        consumo_specifico_kwh_kg = lavoro_reale_refrigerato / 3600 / efficienza_motore

        # --- OUTPUT SEZIONE 3: TECNICA ---
        st.header(_t["section_tech"])
        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Domanda Aggregata alla Pompa", f"{fabbisogno_reale_kg_giorno:,.1f} kg/giorno")
        t2.metric("Stoccaggio Fisico Necessario", f"{stoccaggio_fisico_kg:,.0f} kg")
        t3.metric("Potenza Compressione Richiesta", f"{potenza_elettrica_nominale_kW:,.1f} kW")
        t4.metric("Consumo Energia Compressione", f"{consumo_specifico_kwh_kg:,.2f} kWh/kg")
        
        st.caption(f"ℹ️ **Configurazione Impianto:** Rapporto di compressione totale pari a {beta_tot:.1f}. Temperatura di scarico interstadio stimata a {T_scarico_stadio - 273.15:.1f} °C. Sistema di pre-raffreddamento forzato impostato a {'-40 °C (SAE J2601 - max 60g/s)' if P_dispensazione==700 else '-20 °C (max 120g/s)'}.")

        # --- OUTPUT SEZIONE 4: ECONOMICA ---
        st.header(_t["section_econ"])
        # Calcolo CAPEX parametrico
        costo_serbatoi = stoccaggio_fisico_kg * costo_storage_unitario
        costo_macchinario_compressione = potenza_elettrica_nominale_kW * 2500
        costo_dispenser = 200000 * (1.3 if P_dispensazione == 700 else 1.0)
        costo_refrigerazione = 120000 if P_dispensazione == 700 else 60000
        
        capex_base = costo_serbatoi + costo_macchinario_compressione + costo_dispenser + costo_refrigerazione
        capex_finito_opere_civili = capex_base * 1.25 # +25% per l'allestimento del cantiere
        
        # Ottimizzazione costi molecola in base al profilo strategico sbloccato
        costo_base_molecola = 14.0
        if profilo_design == "VALLEY STRATEGICA": costo_base_molecola = 9.5 # Vantaggio tubo o sinergia industriale
        elif profilo_design == "HUB INTERMODALE": costo_base_molecola = 12.0 # Economia di scala interna

        ec1, ec2, ec3 = st.columns(3)
        ec1.metric("CAPEX Modulo Stoccaggio", f"€ {costo_serbatoi:,.0f}")
        ec2.metric("CAPEX Modulo Compressione", f"€ {costo_macchinario_compressione:,.0f}")
        ec3.metric("CAPEX Totale Chiavi in Mano", f"€ {capex_finito_opere_civili:,.0f}")

        # --- OUTPUT SEZIONE 5: REQUISITI SPAZIALI ---
        st.header(_t["section_space"])
        area_macchinari_netta = (stoccaggio_fisico_kg * 0.15) + (potenza_elettrica_nominale_kW * 0.5)
        area_legale_con_vincoli = area_macchinari_netta * 9.5 # Fattore moltiplicativo DM 23 ottobre 2018
        
        st.warning(f"⚠️ **Vincolo Decreto Ministeriale 23/10/2018:** L'ingombro dei componenti fisici richiede circa {area_macchinari_netta:,.1f} m². Per garantire le distanze di sicurezza stradali, interne e verso confini pubblici di terzi, l'Ente deve identificare un lotto di terreno con una superficie minima di **{area_legale_con_vincoli:,.0f} m²**.")

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
                    "T28_PUNTEGGIO_SCORECARD": int(punteggio_complessivo),
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
                        st.error(f"Errore di sincronizzazione (Codice {response.status_code})")
                except Exception as e:
                    st.error(f"Errore durante l'invio HTTP: {e}")
