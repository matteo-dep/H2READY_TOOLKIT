import streamlit as st
import numpy as np

# ==========================================
# 1. CONFIGURAZIONE E LINGUA
# ==========================================
st.set_page_config(page_title="H2READY - HRS Design Simulator", layout="wide")

LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_choice = st.sidebar.selectbox("🌐 Lingua / Language / Jezik", list(LANG_OPTIONS.keys()))
LANG = LANG_OPTIONS[lang_choice]

T = {
    "it": {
        "title": "🏗️ Simulatore di Design Tecno-Economico HRS",
        "intro": "Dimensionamento termodinamico, impiantistico e spaziale di una stazione di rifornimento a idrogeno.",
        "tab1": "1. Domanda e Profilo",
        "tab2": "2. Architettura Impianto",
        "tab3": "3. Risultati e Costi",
        "lbl_cars": "Auto (4.5 kg/cad)",
        "lbl_buses": "Autobus (30 kg/cad)",
        "lbl_trucks": "Camion Pesanti (50 kg/cad)",
        "lbl_window": "Finestra di Rifornimento (ore/giorno)",
        "lbl_cf": "Fattore di Utilizzo (%)",
        "lbl_source": "Fonte Idrogeno (Pressione Ingresso)",
        "src_elec": "Elettrolizzatore On-Site (20 bar)",
        "src_pipe": "Rete Pipeline (30 bar)",
        "src_tube": "Carro Bombolaio (Media 200 bar)",
        "lbl_routing": "Logica di Routing / Stoccaggio",
        "rout_casc": "Magazzino a Cascata (Overflow a 3 banchi)",
        "rout_boost": "Erogazione Diretta (Booster Compressor)",
        "lbl_dispenser": "Pressione Erogazione Finale",
        "disp_350": "350 bar (Bus/Camion HDV)",
        "disp_700": "700 bar (Auto/Camion HDV)",
        "btn_calc": "🚀 Calcola Dimensionamento HRS",
        "res_tech": "⚙️ Parametri Tecnici e Termodinamici",
        "res_capex": "💶 Stima Investimento (CAPEX)",
        "res_space": "📐 Vincoli Spaziali (DM 23/10/2018)"
    },
    # Versioni EN e SL omesse per brevità, riempite con fallback IT per il funzionamento
    "en": {"title": "🏗️ HRS Techno-Economic Design Simulator", "intro": "Thermodynamic and layout sizing.", "tab1": "1. Demand", "tab2": "2. Architecture", "tab3": "3. Results", "lbl_cars": "Cars", "lbl_buses": "Buses", "lbl_trucks": "Trucks", "lbl_window": "Refuel Window (h/day)", "lbl_cf": "Capacity Factor (%)", "lbl_source": "H2 Source", "src_elec": "On-Site Electrolyzer (20 bar)", "src_pipe": "Pipeline (30 bar)", "src_tube": "Tube Trailer (200 bar)", "lbl_routing": "Routing Logic", "rout_casc": "Cascade Storage", "rout_boost": "Booster Compressor", "lbl_dispenser": "Dispenser Pressure", "disp_350": "350 bar", "disp_700": "700 bar", "btn_calc": "🚀 Calculate HRS Sizing", "res_tech": "⚙️ Technical Parameters", "res_capex": "💶 CAPEX Estimation", "res_space": "📐 Spatial Constraints"},
    "sl": {"title": "🏗️ HRS Tehno-ekonomski simulator", "intro": "Termodinamično dimenzioniranje.", "tab1": "1. Povpraševanje", "tab2": "2. Arhitektura", "tab3": "3. Rezultati", "lbl_cars": "Avtomobili", "lbl_buses": "Avtobusi", "lbl_trucks": "Tovornjaki", "lbl_window": "Okno polnjenja (h/dan)", "lbl_cf": "Faktor izkoriščenosti (%)", "lbl_source": "Vir H2", "src_elec": "Elektrolizer (20 bar)", "src_pipe": "Cevovod (30 bar)", "src_tube": "Cisterna (200 bar)", "lbl_routing": "Logika usmerjanja", "rout_casc": "Kaskadno shranjevanje", "rout_boost": "Ojačevalni kompresor", "lbl_dispenser": "Tlak polnjenja", "disp_350": "350 bar", "disp_700": "700 bar", "btn_calc": "🚀 Izračunaj HRS", "res_tech": "⚙️ Tehnični parametri", "res_capex": "💶 Ocena CAPEX", "res_space": "📐 Prostorske omejitve"}
}
_t = T.get(LANG, T["it"])

st.title(_t["title"])
st.markdown(_t["intro"])

# ==========================================
# 2. COSTANTI TERMODINAMICHE E DI PROGETTO
# ==========================================
R = 8.3144         # kJ/kgK
Cp = 14.5          # kJ/kgK
k = 1.41           # Rapporto calori specifici
eta_is = 0.60      # Rendimento isentropico
T_in = 293.15      # Temperatura ingresso (20°C in Kelvin)
n_stadi = 3        # Numero stadi compressione
OVERCAPACITY = 1.9 # Fattore di sovradimensionamento magazzino

# ==========================================
# 3. INTERFACCIA UTENTE (INPUTS)
# ==========================================
tab1, tab2, tab3 = st.tabs([_t["tab1"], _t["tab2"], _t["tab3"]])

with tab1:
    c1, c2, c3 = st.columns(3)
    n_auto = c1.number_input(_t["lbl_cars"], min_value=0, value=10, step=5)
    n_bus = c2.number_input(_t["lbl_buses"], min_value=0, value=5, step=1)
    n_camion = c3.number_input(_t["lbl_trucks"], min_value=0, value=20, step=5)
    
    st.divider()
    finestra_ore = st.slider(_t["lbl_window"], 1, 24, 8)
    fattore_utilizzo = st.slider(_t["lbl_cf"], 10, 100, 75) / 100.0

with tab2:
    c4, c5 = st.columns(2)
    fonte = c4.selectbox(_t["lbl_source"], ["Elettrolizzatore", "Pipeline", "Carro Bombolaio"])
    routing = c5.selectbox(_t["lbl_routing"], ["Cascata", "Booster"])
    dispenser = st.radio(_t["lbl_dispenser"], ["350 bar", "700 bar"])

# ==========================================
# 4. MOTORE TERMODINAMICO ED ECONOMICO
# ==========================================
if st.button(_t["btn_calc"], use_container_width=True):
    with tab3:
        # --- A. CALCOLO DOMANDA ---
        fab_teorico = (n_auto * 4.5) + (n_bus * 30) + (n_camion * 50)
        fab_reale_kg_day = fab_teorico * fattore_utilizzo
        
        if fab_reale_kg_day == 0:
            st.error("Inserisci almeno un veicolo.")
            st.stop()
            
        # --- B. PARAMETRI DI INGRESSO E USCITA ---
        P_in = 20 if fonte == "Elettrolizzatore" else (30 if fonte == "Pipeline" else 200)
        P_erogazione = 350 if dispenser == "350 bar" else 700
        P_out = P_erogazione + 150 # Margine di sicurezza stoccaggio
        
        # --- C. ROUTING LOGIC (CASCATA vs BOOSTER) ---
        if routing == "Cascata":
            eta_el = 0.88
            usable_factor = 0.91
            costo_stoccaggio_kg = 1092
            # Il compressore a cascata lavora lentamente nelle 24h (assumiamo 20h per O&M)
            portata_massica_kg_s = fab_reale_kg_day / (20 * 3600)
        else: # Booster
            eta_el = 0.92
            usable_factor = 0.95
            costo_stoccaggio_kg = 968
            # Il booster lavora SOLO durante la finestra di rifornimento
            portata_massica_kg_s = fab_reale_kg_day / (finestra_ore * 3600)

        # Dimensionamento Stoccaggio Fisico
        stoccaggio_necessario_kg = (fab_reale_kg_day * OVERCAPACITY) / usable_factor

        # --- D. TERMODINAMICA DEL COMPRESSORE ---
        beta_totale = P_out / P_in
        beta_stadio = beta_totale ** (1 / n_stadi)
        
        # Temperatura e Salto Termico (per stadio)
        T_out = T_in * (beta_stadio ** ((k - 1) / k))
        delta_T = T_out - T_in
        
        # Lavoro ed Energia
        L_is = Cp * delta_T # kJ/kg
        L_i_reale = L_is / eta_is # kJ/kg
        Lavoro_totale_kJ_kg = L_i_reale * n_stadi
        
        # Potenza in kW
        P_effettiva_kW = Lavoro_totale_kJ_kg * portata_massica_kg_s
        P_nominale_kW = P_effettiva_kW / eta_el
        
        # Consumo Elettrico Specifico del solo compressore (kWh/kg)
        consumo_comp_kwh_kg = Lavoro_totale_kJ_kg / 3600 / eta_el
        
        # --- E. STIMA CAPEX ---
        # Costi parametrici stimati
        capex_storage = stoccaggio_necessario_kg * costo_stoccaggio_kg
        capex_compressor = P_nominale_kW * 2500 # Stima 2500 €/kW per compressori H2
        capex_dispenser = 200000 * (1 if dispenser == "350 bar" else 1.3)
        capex_chiller = 120000 if dispenser == "700 bar" else 60000
        
        capex_totale = (capex_storage + capex_compressor + capex_dispenser + capex_chiller) * 1.25 # +25% opere civili

        # --- OUTPUT RISULTATI ---
        st.subheader(_t["res_tech"])
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Domanda Giornaliera", f"{fab_reale_kg_day:,.1f} kg")
        col2.metric("Capacità Stoccaggio", f"{stoccaggio_necessario_kg:,.0f} kg")
        col3.metric("Rapporto Compressione (β)", f"{beta_totale:.1f}")
        col4.metric("Potenza Compressore", f"{P_nominale_kW:,.1f} kW")
        
        with st.expander("Dettagli Termodinamici e di Erogazione"):
            st.markdown(f"""
            * **Lavoro Isentropico Specifico:** {Lavoro_totale_kJ_kg:,.1f} kJ/kg
            * **Consumo Specifico di Compressione:** {consumo_comp_kwh_kg:,.2f} kWh/kg
            * **Temperatura di Scarico (Inter-stage):** {T_out - 273.15:.1f} °C (Necessita inter-cooling)
            * **Pre-cooling SAE J2601:** L'erogazione a {dispenser} richiede raffreddamento forzato a {'-40 °C (flusso max 60 g/s)' if dispenser == '700 bar' else '-20 °C (flusso max 120 g/s)'}.
            """)

        st.subheader(_t["res_capex"])
        c_c1, c_c2, c_c3 = st.columns(3)
        c_c1.metric("CAPEX Stoccaggio", f"€ {capex_storage:,.0f}")
        c_c2.metric("CAPEX Compressore", f"€ {capex_compressor:,.0f}")
        c_c3.metric("CAPEX Impianto Totale", f"€ {capex_totale:,.0f}")
        
        st.subheader(_t["res_space"])
        footprint_macchinari = (stoccaggio_necessario_kg * 0.15) + (P_nominale_kW * 0.5) # m2 approssimativi
        footprint_legale = footprint_macchinari * 9 # Moltiplicatore 8-10x per DM 2018
        
        st.warning(f"""
        **Normativa Sicurezza Antincendio (DM 23 Ottobre 2018):**
        L'ingombro fisico dei macchinari è stimato in circa **{footprint_macchinari:,.0f} m²**. Tuttavia, per rispettare le distanze di sicurezza interne (es. 15m tra elementi pericolosi) ed esterne (es. 30m dai confini pubblici), l'area territoriale necessaria per l'HRS sarà di almeno **{footprint_legale:,.0f} m²**.
        """)
