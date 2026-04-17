import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
import json

# ==========================================
# CONFIGURAZIONE PAGINA E LINGUA
# ==========================================
st.set_page_config(page_title="DSS Mobilità - Gap Analysis", layout="wide")

LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_choice = st.sidebar.selectbox("🌐 Lingua / Language / Jezik", list(LANG_OPTIONS.keys()))
LANG = LANG_OPTIONS[lang_choice]

# ==========================================
# DIZIONARIO MULTILINGUA (i18n)
# ==========================================
T = {
    "it": {
        "title": "🚗 H2READY: Simulatore Strategico di Flotta",
        "subtitle": "Integrazione del database Excel con curve di proiezione tecnologica (2024-2035)",
        "credits": "Sviluppato all'interno del progetto **INTERREG H2Ready** da **Matteo De Piccoli - APE FVG**",
        "expander_readme": "ℹ️ Leggi Istruzioni, Logiche e Assunzioni del Simulatore",
        "sb_db": "📂 Caricamento Database",
        "sb_mission": "1. Parametri di Missione",
        "sb_veicolo": "Tipo Veicolo",
        "veicoli": ["Automobile", "Autobus Urbano", "Autobus Extraurbano", "Camion Pesante"],
        "sb_km": "Percorrenza Giornaliera (km)",
        "sb_days": "Giorni Operativi Annui",
        "sb_window": "Finestra max per Ricarica (Ore)",
        "sb_fleet": "2. Dimensionamento Flotta",
        "sb_n_units": "Numero di veicoli da sostituire",
        "sb_env": "3. Condizioni Ambientali",
        "sb_oro": "Orografia del percorso",
        "orografie": ["Pianura", "Collinare", "Montagna"],
        "sb_winter": "Clima Invernale Rigido (< 0°C)",
        "sb_costs": "4. Costi Energetici Iniziali (2024)",
        "sb_tech": "5. Proiezioni Tecnologiche",
        "verdict_title": "📋 Verdetto di Fattibilità Operativa",
        "verdict_bev": "### 🟢 VERDETTO IMMEDIATO: VANTAGGIO ASSOLUTO BEV (Elettrico)",
        "verdict_h2": "### 🔵 L'IDROGENO È LA SCELTA STRATEGICA MIGLIORE",
        "verdict_bev_ok": "### 🟢 L'ELETTRICO (BEV) È FATTIBILE E PIÙ ECONOMICO",
        "analysis_limits": "### 🚦 Analisi dei Limiti Fisici Elettrici (BEV)",
        "gap_title": "💰 Strategia Incentivi & Gap Analysis",
        "macro_title": "🏢 F. Analisi Macro: Transizione Flotta Intera",
        "btn_export": "🚀 Salva Risultati nel Database Centrale",
        "input_istat": "Inserisci il Codice ISTAT del Comune (es. 030043):",
        "export_success": "✅ Dati della flotta inviati con successo!",
        "export_error": "Inserisci l'identificativo prima di inviare."
    },
    "en": {
        "title": "🚗 H2READY: Strategic Fleet Simulator",
        "subtitle": "Excel database integration with technological projection curves (2024-2035)",
        "credits": "Developed within the **INTERREG H2Ready** project by **Matteo De Piccoli - APE FVG**",
        "expander_readme": "ℹ️ Read Instructions, Logic, and Simulator Assumptions",
        "sb_db": "📂 Database Upload",
        "sb_mission": "1. Mission Parameters",
        "sb_veicolo": "Vehicle Type",
        "veicoli": ["Car", "Urban Bus", "Extra-urban Bus", "Heavy Truck"],
        "sb_km": "Daily Mileage (km)",
        "sb_days": "Annual Operating Days",
        "sb_window": "Max Charging Window (Hours)",
        "sb_fleet": "2. Fleet Sizing",
        "sb_n_units": "Number of vehicles to replace",
        "sb_env": "3. Environmental Conditions",
        "sb_oro": "Route Orography",
        "orografie": ["Flat", "Hilly", "Mountain"],
        "sb_winter": "Harsh Winter Climate (< 0°C)",
        "sb_costs": "4. Initial Energy Costs (2024)",
        "sb_tech": "5. Technological Projections",
        "verdict_title": "📋 Operational Feasibility Verdict",
        "verdict_bev": "### 🟢 IMMEDIATE VERDICT: ABSOLUTE BEV ADVANTAGE (Electric)",
        "verdict_h2": "### 🔵 HYDROGEN IS THE BEST STRATEGIC CHOICE",
        "verdict_bev_ok": "### 🟢 ELECTRIC (BEV) IS FEASIBLE AND CHEAPER",
        "analysis_limits": "### 🚦 Electric Physical Limits Analysis (BEV)",
        "gap_title": "💰 Incentive Strategy & Gap Analysis",
        "macro_title": "🏢 F. Macro Analysis: Full Fleet Transition",
        "btn_export": "🚀 Save Results to Central Database",
        "input_istat": "Enter Municipality ISTAT Code (e.g. 030043):",
        "export_success": "✅ Fleet data sent successfully!",
        "export_error": "Please enter the ID before sending."
    },
    "sl": {
        "title": "🚗 H2READY: Strateški simulator voznega parka",
        "subtitle": "Integracija baze podatkov Excel s krivuljami tehnoloških projekcij (2024-2035)",
        "credits": "Razvito v okviru projekta **INTERREG H2Ready**, avtor **Matteo De Piccoli - APE FVG**",
        "expander_readme": "ℹ️ Preberite navodila, logiko in predpostavke simulatorja",
        "sb_db": "📂 Nalaganje baze podatkov",
        "sb_mission": "1. Parametri misije",
        "sb_veicolo": "Vrsta vozila",
        "veicoli": ["Avtomobil", "Mestni avtobus", "Medkrajevni avtobus", "Težko tovorno vozilo"],
        "sb_km": "Dnevna kilometrina (km)",
        "sb_days": "Letni delovni dnevi",
        "sb_window": "Največje okno za polnjenje (ure)",
        "sb_fleet": "2. Dimenzioniranje voznega parka",
        "sb_n_units": "Število vozil za zamenjavo",
        "sb_env": "3. Okoljski pogoji",
        "sb_oro": "Orografija poti",
        "orografie": ["Ravnina", "Gričevje", "Gore"],
        "sb_winter": "Ostro zimsko podnebje (< 0°C)",
        "sb_costs": "4. Začetni stroški energije (2024)",
        "sb_tech": "5. Tehnološke projekcije",
        "verdict_title": "📋 Razsodba o operativni izvedljivosti",
        "verdict_bev": "### 🟢 TAKOJŠNJA RAZSODBA: ABSOLUTNA PREDNOST BEV (Električno)",
        "verdict_h2": "### 🔵 VODIK JE NAJBOLJŠA STRATEŠKA IZBIRA",
        "verdict_bev_ok": "### 🟢 ELEKTRIČNO (BEV) JE IZVEDLJIVO IN CENEJŠE",
        "analysis_limits": "### 🚦 Analiza električnih fizičnih omejitev (BEV)",
        "gap_title": "💰 Strategija spodbud in analiza vrzeli",
        "macro_title": "🏢 F. Makro analiza: Celoten prehod voznega parka",
        "btn_export": "🚀 Shrani rezultate v centralno bazo",
        "input_istat": "Vnesite ISTAT kodo občine (npr. 030043):",
        "export_success": "✅ Podatki o voznem parku so bili uspešno poslani!",
        "export_error": "Pred pošiljanjem vnesite identifikator."
    }
}

_t = T[LANG]

# --- INTESTAZIONE ---
st.title(_t["title"])
st.caption(_t["credits"])
st.markdown(_t["subtitle"])

# --- FUNZIONE DI PULIZIA DATI ---
def clean_val(x):
    if pd.isna(x) or str(x).strip() == "": 
        return 0.0
    s = str(x).replace('€', '').replace('%', '').replace(' ', '').replace(',', '.')
    s = s.replace('[', '').replace(']', '')
    try:
        return float(s)
    except ValueError:
        return 0.0  

# --- FUNZIONE INTERPOLAZIONE ---
def interpolate(year, y_2024, y_2030):
    if year <= 2024: return y_2024
    if year >= 2030: return y_2030
    return y_2024 + (y_2030 - y_2024) * ((year - 2024) / (2030 - 2024))

# --- MENU A TENDINA DA FILE ESTERNO (DINAMICO PER LINGUA) ---
nome_file_md = f"README_mezzi_{LANG}.md"
if os.path.exists(nome_file_md):
    with st.expander(_t["expander_readme"]):
        with open(nome_file_md, "r", encoding="utf-8") as f:
            st.markdown(f.read())
else:
    st.info(f"💡 Info: {nome_file_md} not found.")

# ==========================================
# 1. INTERFACCIA UTENTE (SIDEBAR) 
# ==========================================

with st.sidebar:
    st.header(_t["sb_db"])
    NOME_FILE_EXCEL = "Comparison H2 elc FF.xlsx"
    if not os.path.exists(NOME_FILE_EXCEL):
        st.error(f"File '{NOME_FILE_EXCEL}' non trovato.")
        st.stop()
    
    xl = pd.ExcelFile(NOME_FILE_EXCEL, engine='openpyxl')
    
    st.header(_t["sb_mission"])
    # Mappatura dei tipi veicolo per la lingua
    veicolo_scelto = st.selectbox(_t["sb_veicolo"], _t["veicoli"])
    # Ritrasformiamo in IT per la logica Excel interna
    idx_v = _t["veicoli"].index(veicolo_scelto)
    tipo_veicolo = ["Automobile", "Autobus Urbano", "Autobus Extraurbano", "Camion Pesante"][idx_v]

    km_giornalieri = st.slider(_t["sb_km"], 10, 1000, 150 if tipo_veicolo == "Automobile" else 250, 10)
    giorni_operativi = st.slider(_t["sb_days"], 200, 365, 300, 5)
    tempo_inattivita = st.slider(_t["sb_window"], 0.5, 12.0, 5.0, 0.5)
    
    st.header(_t["sb_fleet"])
    n_veicoli = st.slider(_t["sb_n_units"], 1, 500, 10)

    st.header(_t["sb_env"])
    oro_scelta = st.selectbox(_t["sb_oro"], _t["orografie"])
    idx_o = _t["orografie"].index(oro_scelta)
    orografia = ["Pianura", "Collinare", "Montagna"][idx_o]

    inverno_rigido = st.checkbox(_t["sb_winter"])
    
    st.header(_t["sb_costs"])
    p_in_benzina = st.number_input("Benzina (€/l)", value=1.90, format="%.2f") if tipo_veicolo == "Automobile" else 0.0
    p_in_diesel = st.number_input("Diesel (€/l)", value=1.80, format="%.2f")
    p_in_el_rete = st.number_input("Elettricità Rete (€/kWh)", value=0.31, format="%.3f")
    p_in_el_fv = st.number_input("Elettricità FV (€/kWh)", value=0.24, format="%.3f")
    p_in_h2_rete = st.number_input("H2 da Rete (€/kg)", value=20.00, format="%.2f")
    p_in_h2_fv = st.number_input("H2 Autoprodotto (€/kg)", value=15.00, format="%.2f")

    st.header(_t["sb_tech"])
    anno_acquisto = st.slider("Anno", 2024, 2035, 2024)
    anni_utilizzo = st.slider("Ciclo di Vita (Anni)", 5, 30, 10) 

# (Logica di calcolo uguale alla tua...)
km_annui = km_giornalieri * giorni_operativi
total_km_life = km_annui * anni_utilizzo
fossile_name = "Benzina" if tipo_veicolo == "Automobile" else "Diesel"
bev_name = "Elettrico autoprodotto"
h2_name = "Idrogeno autoprodotto"

# --- ESTRAZIONE DATI EXCEL ---
target_str = {"Automobile": "AUTO", "Camion Pesante": "CAMION", "Autobus Urbano": "AUTOBUS URBANO", "Autobus Extraurbano": "AUTOBUS EXTRAURBANO"}[tipo_veicolo]
nome_foglio = next((f for f in xl.sheet_names if f.upper() == target_str), xl.sheet_names[0])
df_raw = pd.read_excel(xl, sheet_name=nome_foglio, header=None)

dati = []
tecs = ["Benzina", "Diesel", "Elettrico rete", "Elettrico autoprodotto", "Idrogeno Grigio", "Idrogeno rete", "Idrogeno autoprodotto"]
for i in range(2, min(30, len(df_raw))): 
    nome = str(df_raw.iloc[i, 1]).strip()
    if nome in tecs:
        dati.append({
            "Tecnologia": nome, 
            "Autonomia": clean_val(df_raw.iloc[i, 3]),
            "Consumo": clean_val(df_raw.iloc[i, 4]),
            "Eta": clean_val(df_raw.iloc[i, 9]),
            "OPEX_Maint_km": clean_val(df_raw.iloc[i, 22]),
            "CAPEX": clean_val(df_raw.iloc[i, 25])
        })
df_abs = pd.DataFrame(dati)

# --- MOTORE DI CALCOLO ---
mult_env = {"Pianura": 1.0, "Collinare": 1.25, "Montagna": 1.45}[orografia] * (1.25 if inverno_rigido else 1.0)
conv_factors = {"Benzina": 8.76, "Diesel": 9.91, "Idrogeno": 33.33, "Elettrico": 1.0}
f_emiss = {"Benzina": 0.33, "Diesel": 0.307, "Elettrico rete": 0.215, "Elettrico autoprodotto": 0.055, "Idrogeno Grigio": 0.330, "Idrogeno rete": 0.387, "Idrogeno autoprodotto": 0.090}
c_emiss = {"Automobile": {"Fossile": 6000, "BEV": 12000, "H2": 14000}, "Autobus Urbano": {"Fossile": 50000, "BEV": 85000, "H2": 95000}, "Autobus Extraurbano": {"Fossile": 50000, "BEV": 85000, "H2": 95000}, "Camion Pesante": {"Fossile": 60000, "BEV": 110000, "H2": 125000}}

m_bev_auto = interpolate(anno_acquisto, 1.0, 1.40)
m_h2_auto = interpolate(anno_acquisto, 1.0, 1.15)
fabbisogno_kwh = km_giornalieri * df_abs[df_abs['Tecnologia'] == 'Elettrico rete']['Consumo'].values[0] * mult_env * 1.15
fc_kw_stima = {"Automobile": 100, "Autobus Urbano": 200, "Autobus Extraurbano": 200, "Camion Pesante": 300}[tipo_veicolo]
delta_batt_capex = fabbisogno_kwh * (interpolate(anno_acquisto, 210, 100) - 210)
delta_fc_capex = fc_kw_stima * (interpolate(anno_acquisto, 330, 210) - 330)

res = []
for idx, r in df_abs.iterrows():
    t = r['Tecnologia']
    cat = 'BEV' if 'Elettrico' in t else ('H2' if 'Idrogeno' in t else 'Fossile')
    if t == "Benzina": p_sim = p_in_benzina * interpolate(anno_acquisto, 1.0, 1.1)
    elif t == "Diesel": p_sim = p_in_diesel * interpolate(anno_acquisto, 1.0, 1.1)
    elif t == "Elettrico rete": p_sim = p_in_el_rete * interpolate(anno_acquisto, 1.0, 0.9)
    elif t == "Elettrico autoprodotto": p_sim = p_in_el_fv * interpolate(anno_acquisto, 1.0, 0.9)
    elif t == "Idrogeno Grigio": p_sim = p_in_h2_rete * interpolate(anno_acquisto, 1.0, 0.8)
    elif t == "Idrogeno rete": p_sim = p_in_h2_rete * interpolate(anno_acquisto, 1.0, 0.6)
    elif t == "Idrogeno autoprodotto": p_sim = p_in_h2_fv * interpolate(anno_acquisto, 1.0, 0.7)
    else: p_sim = 0.0

    aut_ev = r['Autonomia'] * (m_bev_auto if cat=='BEV' else (m_h2_auto if cat=='H2' else 1.0))
    e_prod = c_emiss[tipo_veicolo][cat] / 1000.0
    e_fuel = (r['Consumo'] * mult_env * total_km_life * f_emiss[t]) / 1000.0 
    
    divisore = conv_factors["Elettrico"]
    if "Benzina" in t: divisore = conv_factors["Benzina"]
    elif "Diesel" in t: divisore = conv_factors["Diesel"]
    elif "Idrogeno" in t: divisore = conv_factors["Idrogeno"]

    consumo_naturale = (r['Consumo'] * mult_env) / divisore
    fuel_cost = (consumo_naturale * total_km_life) * p_sim
    mnt_cost = r['OPEX_Maint_km'] * total_km_life
    if cat == 'BEV': cpx = max(0, r['CAPEX'] + delta_batt_capex)
    elif cat == 'H2': cpx = max(0, r['CAPEX'] + delta_fc_capex)
    else: cpx = r['CAPEX']
    
    res.append({
        "Tecnologia": t, 
        "Categoria_Base": "Elettrico (BEV)" if cat == 'BEV' else ("Idrogeno (FCEV)" if cat == 'H2' else t),
        "Autonomia": aut_ev, "Consumo": r['Consumo'], "Eta": r['Eta'] * 100 if r['Eta'] < 2 else r['Eta'],
        "E_Produzione": e_prod, "E_Carburante": e_fuel,
        "Costo_Veicolo": cpx, "Costo_Manutenzione": mnt_cost, "Costo_Carburante": fuel_cost,
        "TCO_Totale": cpx + mnt_cost + fuel_cost,
        "Consumo_Naturale": consumo_naturale
    })
df_final = pd.DataFrame(res)

# ==========================================
# 4. DASHBOARD E VERDETTO
# ==========================================
tco_fossile = df_final[df_final['Tecnologia'] == fossile_name]['TCO_Totale'].values[0]
tco_bev = df_final[df_final['Tecnologia'] == bev_name]['TCO_Totale'].values[0]
tco_h2 = df_final[df_final['Tecnologia'] == h2_name]['TCO_Totale'].values[0]

densita_batt = interpolate(anno_acquisto, 0.16, 0.256)
tempo_ric = fabbisogno_kwh / (1000 if (anno_acquisto >= 2028 and tipo_veicolo != "Automobile") else 150)
peso_batt = fabbisogno_kwh / densita_batt
lim_peso = {"Automobile": 400, "Autobus Urbano": 3000, "Autobus Extraurbano": 4000, "Camion Pesante": 4500}[tipo_veicolo]
peso_netto_perso = peso_batt if tipo_veicolo == "Automobile" else max(0, peso_batt - interpolate(anno_acquisto, 2000, 4000))

sem_peso = "🟢 OK" if peso_netto_perso <= lim_peso * 0.7 else ("🟡 ATTENZIONE" if peso_netto_perso <= lim_peso else "🔴 CRITICO")
sem_tempo = "🟢 OK" if tempo_ric <= tempo_inattivita * 0.8 else ("🟡 ATTENZIONE" if tempo_ric <= tempo_inattivita else "🔴 CRITICO")

st.subheader(_t["verdict_title"])
esito_finale = ""
if tipo_veicolo in ["Autobus Urbano", "Automobile"] and km_giornalieri <= 200:
    st.success(_t["verdict_bev"])
    esito_finale = "BEV"
else:
    vince_h2 = "🔴 CRITICO" in sem_peso or "🔴 CRITICO" in sem_tempo or tco_h2 < (tco_bev * 0.9)
    if vince_h2: 
        st.error(_t["verdict_h2"])
        esito_finale = "H2"
    else: 
        st.success(_t["verdict_bev_ok"])
        esito_finale = "BEV"

st.markdown(_t["analysis_limits"])
c1, c2, c3 = st.columns(3)
c1.metric("Peso Batteria", f"{peso_batt:,.0f} kg", sem_peso, delta_color="inverse")
c2.metric("Tempo Ricarica", f"{tempo_ric:.1f} h", sem_tempo, delta_color="inverse")
c3.metric("Delta Costo H2 vs BEV", f"€ {tco_h2 - tco_bev:,.0f}")

# (Qui vanno tutti i tuoi grafici originali...)
# [Grafici TCO, LCA, Consumi ometti per spazio ma restano nel tuo file]

# ==========================================
# 6. ANALISI DI FLOTTA E EXPORT
# ==========================================
st.divider()
st.header(_t["macro_title"])
row_bev = df_final[df_final['Tecnologia'] == bev_name].iloc[0]
row_h2 = df_final[df_final['Tecnologia'] == h2_name].iloc[0]
cons_annuo_h2_kg = row_h2['Consumo_Naturale'] * km_annui * n_veicoli
fabbisogno_tot_ton = cons_annuo_h2_kg / 1000

# Delta TCO Totale vs Fossile (per la flotta)
delta_tco_flotta = (tco_h2 - tco_fossile) * n_veicoli if esito_finale == "H2" else (tco_bev - tco_fossile) * n_veicoli
# Emissioni evitate (Flotta)
emiss_fossile = (df_final[df_final['Tecnologia'] == fossile_name]['E_Produzione'].values[0] + df_final[df_final['Tecnologia'] == fossile_name]['E_Carburante'].values[0]) * n_veicoli
emiss_scelta = (row_h2['E_Produzione'] + row_h2['E_Carburante']) * n_veicoli if esito_finale == "H2" else (row_bev['E_Produzione'] + row_bev['E_Carburante']) * n_veicoli
evitate = emiss_fossile - emiss_scelta

# --- SEZIONE EXPORT ---
st.divider()
st.header("🔗 Esportazione Dati")
istat_comune = st.text_input(_t["input_istat"])

if st.button(_t["btn_export"]):
    if not istat_comune:
        st.error(_t["export_error"])
    else:
        payload = {
            "ID_ISTAT": istat_comune,
            "T22_N_VEICOLI_ANALIZZATI": n_veicoli,
            "T22_ESITO_PREVALENTE": esito_finale,
            "T22_FABBISOGNO_H2_TON_ANNO": round(fabbisogno_tot_ton, 2),
            "T22_DELTA_TCO_EURO": round(delta_tco_flotta, 0),
            "T22_EMISSIONI_EVITATE_TCO2": round(evitate, 1)
        }
        
        # USA IL TUO URL GOOGLE SCRIPT (lo stesso degli altri tool)
        GOOGLE_URL = "INCOLLA_QUI_IL_TUO_URL_DI_GOOGLE_APPS_SCRIPT"
        
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(GOOGLE_URL, data=json.dumps(payload), headers=headers, allow_redirects=True)
            if response.status_code in [200, 201]:
                st.success(_t["export_success"])
                st.balloons()
            else:
                st.error(f"Errore Google (Codice {response.status_code})")
        except Exception as e:
            st.error(f"Errore: {e}")
