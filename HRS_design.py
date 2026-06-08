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

# Dizionario Interfaccia
T = {
    "it": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.8: Dimensionamento e Design Tecno-Economico HRS",
        "credits": "Sviluppato all'interno del progetto [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 GUIDA OPERATIVA (Leggi prima di iniziare)",
        "logic_title": "🧠 Analisi Metodologica e Standard di Progettazione",
        "instructions_md": """
### 🎯 Qual è il tuo obiettivo?
Questo strumento serve a dimensionare l'architettura tecnica e a stimare l'impatto economico di una **Stazione di Rifornimento a Idrogeno (HRS)** per mezzi pesanti.

**Istruzioni:**
1. Configura **tutti i parametri tecnici ed economici nella barra laterale sinistra**.
2. Clicca sul bottone **'Avvia Dimensionamento Impiantistico'** qui sotto per generare il report tecno-economico unificato, inclusivo del calcolo del Break-Even Point.
        """,
        "sb_config": "🏗️ Configurazione Strategica",
        "sb_tech": "⚡ Parametri Tecnici HRS",
        "sb_econ": "💸 Parametri Economici",
        "lbl_conf_type": "Configurazione Impianto Obiettivo",
        "lbl_cars": "Auto private / flotta leggera (4.5 kg/pieno)",
        "lbl_buses": "Autobus TPL / Mezzi Speciali (30 kg/pieno)",
        "lbl_trucks": "Camion Pesanti a lungo raggio (50 kg/pieno)",
        "lbl_window": "Finestra di Rifornimento (ore/giorno)",
        "lbl_cf": "Fattore di Carico Stazione (Capacity Factor %)",
        "lbl_source": "Sorgente e Pressione di Ingresso H2",
        "lbl_routing": "Architettura di Compressione/Storage",
        "lbl_dispenser": "Pressione di Erogazione Finale",
        "btn_calc": "🚀 Avvia Dimensionamento Impiantistico HRS",
        "input_id": "Codice Identificativo per esportazione (es. 030043):"
    }
}
_t = T.get(LANG, T["it"]) # Fallback italiano per brevità

# ==========================================
# 2. INTESTAZIONE PRINCIPALE
# ==========================================
st.title(_t["title"])
st.markdown(_t["credits"])
st.divider()

with st.expander(_t["instr_title"], expanded=True):
    st.markdown(_t["instructions_md"])

with st.expander(_t["logic_title"], expanded=False):
    nome_file_logica = f"logic_logistica_{LANG}.md"
    if os.path.exists(nome_file_logica):
        with open(nome_file_logica, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.caption("ℹ️ File di analisi metodologica estesa caricato esternamente.")

st.markdown("---")

# ==========================================
# 3. BARRA LATERALE SINISTRA (INPUT)
# ==========================================
with st.sidebar:
    with st.expander(_t["sb_config"], expanded=True):
        config_scelta = st.selectbox(_t["lbl_conf_type"], [
            "HRS di Transito Puro (Flussi autostradali)", 
            "HRS Hub Intermodale Multi-Mezzo", 
            "HRS Valley Strategica Integrata"
        ])

    with st.expander(_t["sb_tech"], expanded=True):
        n_auto = st.slider(_t["lbl_cars"], 0, 100, 10, step=5)
        n_bus = st.slider(_t["lbl_buses"], 0, 50, 5, step=1)
        n_camion = st.slider(_t["lbl_trucks"], 0, 150, 30, step=5)
        finestra_ore = st.slider(_t["lbl_window"], 1, 24, 8)
        capacity_factor = st.slider(_t["lbl_cf"], 10, 100, 75) / 100.0
        fonte_h2 = st.selectbox(_t["lbl_source"], ["Elettrolizzatore (20 bar)", "Pipeline Snam (30 bar)", "Carro Bombolaio (200 bar)"])
        routing_logic = st.selectbox(_t["lbl_routing"], ["Magazzino a Cascata (3 banchi)", "Booster Compressor (Diretta)"])
        dispenser_press = st.radio(_t["lbl_dispenser"], ["350 bar (Bus)", "700 bar (Camion/Auto)"])
        
    with st.expander(_t["sb_econ"], expanded=True):
        costo_energia = st.number_input("Costo Elettricità (€/kWh)", min_value=0.05, max_value=0.50, value=0.15, step=0.01)
        costo_molecola_in = st.number_input("Costo Acquisto/Produzione H2 (€/kg)", min_value=1.0, max_value=20.0, value=6.0, step=0.5)
        wacc = st.slider("Costo del Capitale (WACC %)", 1, 15, 6) / 100.0
        anni_vita = st.slider("Vita Utile Impianto (Anni)", 5, 30, 15)

# ==========================================
# 4. MOTORE DI CALCOLO E REPORT
# ==========================================
if st.button(_t["btn_calc"], type="primary", use_container_width=True):
    
    # --- 1. DOMANDA ---
    fabbisogno_teorico = (n_auto * 4.5) + (n_bus * 30) + (n_camion * 50)
    fabbisogno_reale_kg_giorno = fabbisogno_teorico * capacity_factor
    
    if fabbisogno_reale_kg_giorno == 0:
        st.error("Inserisci almeno un veicolo commerciale.")
        st.stop()
        
    # --- 2. TERMODINAMICA ---
    Cp = 14.5; k_ad = 1.41; eta_is = 0.60; T_in = 293.15; stadi = 3; overcap = 1.9
    P_inlet = 20 if "Elettrolizzatore" in fonte_h2 else (30 if "Pipeline" in fonte_h2 else 200)
    P_disp = 350 if "350 bar" in dispenser_press else 700
    P_stoccaggio = P_disp + 150 
    
    if "Cascata" in routing_logic:
        eta_el = 0.88; fat_usabilita = 0.91; costo_storage_kg = 1092; ore_lavoro = 20
    else:
        eta_el = 0.92; fat_usabilita = 0.95; costo_storage_kg = 968; ore_lavoro = finestra_ore

    portata_kg_s = fabbisogno_reale_kg_giorno / (ore_lavoro * 3600)
    stoccaggio_fisico_kg = (fabbisogno_reale_kg_giorno * overcap) / fat_usabilita

    beta_tot = P_stoccaggio / P_inlet
    beta_st = beta_tot ** (1 / stadi)
    T_out = T_in * (beta_st ** ((k_ad - 1) / k_ad))
    lav_is = Cp * (T_out - T_in)
    lav_reale = (lav_is / eta_is) * stadi
    
    potenza_kW = (lav_reale * portata_kg_s) / eta_el
    consumo_kwh_kg = lav_reale / 3600 / eta_el

    # --- 3. OUTPUT: TECNICA E TEMPI ---
    st.header("⚙️ Dimensionamento Impianto e Velocità Erogazione")
    velocita_g_s = 60 if P_disp == 700 else 120
    tempo_camion = (50 * 1000) / velocita_g_s / 60
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Domanda Nominale", f"{fabbisogno_reale_kg_giorno:,.1f} kg/giorno")
    c2.metric("Stoccaggio Fisico", f"{stoccaggio_fisico_kg:,.0f} kg")
    c3.metric("Potenza Compressore", f"{potenza_kW:,.1f} kW")
    c4.metric("Consumo Compressione", f"{consumo_kwh_kg:,.2f} kWh/kg")
    
    st.info(f"⏱️ **Standard SAE J2601:** La velocità di rifornimento alla pompa è limitata a **{velocita_g_s} g/s**. Un pieno per un Camion Pesante (50 kg) richiederà in media **{tempo_camion:.1f} minuti**, indipendentemente dalla grandezza del compressore.")

    # --- 4. OUTPUT: ECONOMIA (CAPEX e OPEX) ---
    st.header("💶 Analisi Finanziaria (CAPEX e OPEX)")
    
    capex_storage = stoccaggio_fisico_kg * costo_storage_kg
    capex_comp = potenza_kW * 2500
    capex_disp = 200000 * (1.3 if P_disp == 700 else 1.0)
    capex_chiller = 120000 if P_disp == 700 else 60000
    capex_tot = (capex_storage + capex_comp + capex_disp + capex_chiller) * 1.25 # +25% civili
    
    opex_fisso = capex_tot * 0.04
    opex_energia = consumo_kwh_kg * fabbisogno_reale_kg_giorno * 365 * costo_energia
    opex_totale = opex_fisso + opex_energia

    co1, co2, co3 = st.columns(3)
    co1.metric("CAPEX Totale (Chiavi in Mano)", f"€ {capex_tot:,.0f}")
    co2.metric("OPEX Fisso (O&M, 4% CAPEX)", f"€ {opex_fisso:,.0f} / anno")
    co3.metric(f"OPEX Elettrico ({costo_energia} €/kWh)", f"€ {opex_energia:,.0f} / anno")

    # --- 5. BREAK-EVEN POINT (LCOH) ---
    st.header("🎯 Break-Even Point (Prezzo minimo alla pompa)")
    # Capital Recovery Factor (CRF)
    crf = (wacc * (1 + wacc)**anni_vita) / (((1 + wacc)**anni_vita) - 1)
    capex_annuo = capex_tot * crf
    costo_annuo_molecola = fabbisogno_reale_kg_giorno * 365 * costo_molecola_in
    
    break_even_price = (capex_annuo + opex_totale + costo_annuo_molecola) / (fabbisogno_reale_kg_giorno * 365)
    
    st.success(f"Per coprire il rientro dell'investimento ({anni_vita} anni al {wacc*100}%), i costi operativi e il costo di acquisto dell'idrogeno, il prezzo minimo di vendita alla pompa deve essere di **{break_even_price:.2f} €/kg**.")
    
    # --- 6. FOOTPRINT ---
    area_netta = (stoccaggio_fisico_kg * 0.15) + (potenza_kW * 0.5)
    st.warning(f"📐 **Vincolo DM 23/10/2018:** Superficie minima lotto (con distanze di sicurezza): **{area_netta * 9.5:,.0f} m²**.")
