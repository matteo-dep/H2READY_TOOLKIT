import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from numba import njit
import requests
import json

# ==========================================
# CONFIGURAZIONE PAGINA
# ==========================================
st.set_page_config(page_title="H2READY - Progettazione e Finanza", layout="wide")

# ==========================================
# MULTILINGUA E INTESTAZIONE
# ==========================================
LANG_OPTIONS = {"Italiano": "it", "English": "en", "Slovenščina": "sl"}
lang_choice = st.sidebar.selectbox("🌐 Lingua / Language / Jezik", list(LANG_OPTIONS.keys()))
LANG = LANG_OPTIONS[lang_choice]

# Dizionario Multilingua (i18n)
T = {
    "it": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.6: Analisi tecnica e finanziaria della produzione di idrogeno verde",
        "sb_target": "🎯 1. Target",
        "sb_target_h2": "Target Idrogeno (ton/anno)",
        "sb_zone": "Zona Climatica",
        "sb_mix": "⚖️ 2. Mix & Rete",
        "sb_quota_pv": "Mix: PV vs Eolico (%)",
        "sb_conn_type": "Tipo di Connessione",
        "sb_dist_grid": "Distanza Cabina (km)",
        "sb_bess": "🔋 3. Accumulo BESS",
        "sb_bess_strat": "Configurazione:",
        "sb_bess_limit": "Limite Batteria (x MW PV)",
        "sb_costs": "💶 4. Costi (CfD / CAPEX)",
        "sb_stocc": "🛢️ 5. Stoccaggio H2",
        "sb_comp": "🗜️ 6. Compressione",
        "sb_market": "💰 7. Mercato",
        "sb_price_h2": "Prezzo Vendita H2 (€/kg)",
        "sec1_title": "⚙️ Dati Impianto Idrogeno",
        "sec1_ely": "Taglia Elettrolizzatore",
        "sec2_title": "⚡ Generazione Rinnovabile e Accumulo (Contratti PPA/CfD)",
        "fin_title": "💶 Analisi Finanziaria e Ripartizione CAPEX",
        "fin_lcoh": "LCOH (Costo H2)",
        "fin_capex": "CAPEX Investimento",
        "fin_payback": "Tempo di Rientro",
        "btn_export": "🚀 Salva Risultati nel Database Centrale (Zapier)",
        "export_success": "✅ Dati inviati con successo al Database Centrale!",
        "export_error": "Inserisci il Codice ISTAT prima di inviare.",
        "input_istat": "Inserisci il Codice ISTAT del Comune (es. 030043):"
    },
    "en": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.6: Technical and financial analysis of green hydrogen production",
        "sb_target": "🎯 1. Target",
        "sb_target_h2": "Hydrogen Target (ton/year)",
        "sb_zone": "Climate Zone",
        "sb_mix": "⚖️ 2. Mix & Grid",
        "sb_quota_pv": "Mix: PV vs Wind (%)",
        "sb_conn_type": "Connection Type",
        "sb_dist_grid": "Grid Distance (km)",
        "sb_bess": "🔋 3. BESS Storage",
        "sb_bess_strat": "Configuration:",
        "sb_bess_limit": "Battery Limit (x MW PV)",
        "sb_costs": "💶 4. Costs (CfD / CAPEX)",
        "sb_stocc": "🛢️ 5. H2 Storage",
        "sb_comp": "🗜️ 6. Compression",
        "sb_market": "💰 7. Market",
        "sb_price_h2": "H2 Sale Price (€/kg)",
        "sec1_title": "⚙️ Hydrogen Plant Data",
        "sec1_ely": "Electrolyzer Size",
        "sec2_title": "⚡ Renewable Generation and Storage (PPA/CfD)",
        "fin_title": "💶 Financial Analysis and CAPEX Breakdown",
        "fin_lcoh": "LCOH (H2 Cost)",
        "fin_capex": "CAPEX Investment",
        "fin_payback": "Payback Period",
        "btn_export": "🚀 Save Results to Central Database (Zapier)",
        "export_success": "✅ Data successfully sent to Central Database!",
        "export_error": "Please enter the ISTAT Code before sending.",
        "input_istat": "Enter the Municipality ISTAT Code (e.g. 030043):"
    },
    "sl": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.6: Tehnična in finančna analiza proizvodnje zelenega vodika",
        "sb_target": "🎯 1. Cilj",
        "sb_target_h2": "Cilj vodika (ton/leto)",
        "sb_zone": "Podnebno območje",
        "sb_mix": "⚖️ 2. Mešanica in omrežje",
        "sb_quota_pv": "Mešanica: PV vs Veter (%)",
        "sb_conn_type": "Vrsta povezave",
        "sb_dist_grid": "Razdalja do omrežja (km)",
        "sb_bess": "🔋 3. Shranjevanje BESS",
        "sb_bess_strat": "Konfiguracija:",
        "sb_bess_limit": "Omejitev baterije (x MW PV)",
        "sb_costs": "💶 4. Stroški (CfD / CAPEX)",
        "sb_stocc": "🛢️ 5. Shranjevanje H2",
        "sb_comp": "🗜️ 6. Kompresija",
        "sb_market": "💰 7. Trg",
        "sb_price_h2": "Prodajna cena H2 (€/kg)",
        "sec1_title": "⚙️ Podatki o napravi za vodik",
        "sec1_ely": "Velikost elektrolizerja",
        "sec2_title": "⚡ Obnovljiva proizvodnja in shranjevanje (PPA/CfD)",
        "fin_title": "💶 Finančna analiza in razčlenitev CAPEX",
        "fin_lcoh": "LCOH (Strošek H2)",
        "fin_capex": "Investicija CAPEX",
        "fin_payback": "Doba vračila",
        "btn_export": "🚀 Shrani rezultate v centralno bazo (Zapier)",
        "export_success": "✅ Podatki so bili uspešno poslani v centralno bazo!",
        "export_error": "Pred pošiljanjem vnesite ISTAT kodo.",
        "input_istat": "Vnesite ISTAT kodo občine (npr. 030043):"
    }
}

_t = T[LANG]

st.title(_t["title"])

# ==========================================
# DATASET & PESI (NORD/SUD)
# ==========================================
PV_WEIGHTS_NORD = {'Lombardia orientale, area Brescia_NORD': 0.2956, 'Veneto centrale, area Padova_NORD': 0.2313, 'Emilia-Romagna orientale, area Ferrara,pianura_NORD': 0.2213, 'Piemonte meridionale, area Cuneo_NORD': 0.1874, 'Friuli-Venezia Giulia, area Udine_NORD': 0.0644}
PV_WEIGHTS_SUD = {'Puglia, area Lecce_SUD': 0.3241, 'Sicilia interna, area Caltanissetta,Enna_SUD': 0.2117, 'Lazio meridionale, area Latina_SUD': 0.1982, 'Sardegna, area Oristano,Campidano_SUD': 0.1330, 'Campania interna, area Benevento_SUD': 0.1330}
WIND_WEIGHTS_NORD = {'Crinale savonese entroterra ligure_NORD': 0.6020, 'Appennino emiliano, area Monte Cimone_NORD': 0.2239, 'Piemonte sud-occidentale , Cuneese_NORD': 0.0945, 'Veneto orientale , Delta del Po_NORD': 0.0647, 'Valle d’Aosta , area alpina_NORD': 0.0149}
WIND_WEIGHTS_SUD = {'Puglia, area Foggia,Daunia_SUD': 0.3093, 'Sicilia occidentale, area Trapani_SUD': 0.2267, 'Campania, area Benevento,Avellino_SUD': 0.1950, 'Basilicata, area Melfi,Potenza_SUD': 0.1489, 'Calabria, area Crotone,Catanzaro_SUD': 0.1201}

# ==========================================
# FUNZIONI SUPPORTO
# ==========================================
def _serie_pesata(df, pesi_colonne, scala=1.0, clip_upper=1.0):
    serie = sum(pd.to_numeric(df[col], errors='coerce').fillna(0.0) * peso for col, peso in pesi_colonne.items())
    return (serie / scala).clip(lower=0.0, upper=clip_upper).astype(float)

@st.cache_data
def carica_profili(file_pv, file_wind):
    try:
        df_pv = pd.read_csv(file_pv)
        df_wind = pd.read_csv(file_wind)
        return _serie_pesata(df_pv, PV_WEIGHTS_NORD, 1000.0).values[:8760], _serie_pesata(df_pv, PV_WEIGHTS_SUD, 1000.0).values[:8760], \
               _serie_pesata(df_wind, WIND_WEIGHTS_NORD).values[:8760], _serie_pesata(df_wind, WIND_WEIGHTS_SUD).values[:8760], False
    except:
        t = np.arange(8760)
        return np.clip(np.sin(t*np.pi/12),0,1)*0.8, np.clip(np.sin(t*np.pi/12),0,1)*0.9, np.random.rand(8760)*0.5, np.random.rand(8760)*0.7, True

@njit
def simula_h2_plant(pv, wind, ely_mw, batt_mwh, eff_batt=0.90):
    ore = 8760
    ely_usage, batt_soc = np.zeros(ore), np.zeros(ore)
    soc = batt_mwh * 0.2
    sqrt_eff = np.sqrt(eff_batt)
    for t in range(ore):
        avail = pv[t] + wind[t]
        if avail >= ely_mw:
            ely_usage[t] = ely_mw
            charge = min(avail - ely_mw, (batt_mwh - soc) / sqrt_eff)
            soc += charge * sqrt_eff
        else:
            discharge = min(ely_mw - avail, soc * sqrt_eff)
            soc -= discharge / sqrt_eff
            ely_usage[t] = avail + discharge
        batt_soc[t] = soc
    return ely_usage, batt_soc

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.header(_t["sb_target"])
target_h2_kg = st.sidebar.number_input(_t["sb_target_h2"], 10, 1000000, 1000) * 1000
regione = st.sidebar.selectbox(_t["sb_zone"], ["Nord Italia", "Sud Italia / Isole"])

st.sidebar.header(_t["sb_mix"])
quota_pv_pct = st.sidebar.slider(_t["sb_quota_pv"], 0, 100, 50)
tipo_connessione = st.sidebar.radio(_t["sb_conn_type"], ["ON-GRID", "OFF-GRID"])
distanza_rete_km = st.sidebar.slider(_t["sb_dist_grid"], 0.1, 20.0, 2.0) if tipo_connessione == "ON-GRID" else 0.0

st.sidebar.header(_t["sb_bess"])
strategia_batt = st.sidebar.radio(_t["sb_bess_strat"], ["No", "Yes"])
limite_batt_pv = st.sidebar.slider(_t["sb_bess_limit"], 0.0, 5.0, 3.0)

st.sidebar.header(_t["sb_costs"])
cfd_pv = st.sidebar.slider("CfD PV (€/MWh)", 30.0, 120.0, 60.0)
cfd_wind = st.sidebar.slider("CfD Wind (€/MWh)", 30.0, 150.0, 80.0)
capex_ely = st.sidebar.slider("CAPEX Ely (€/kW)", 500, 2000, 1000)
capex_batt = st.sidebar.slider("CAPEX BESS (€/kWh)", 100, 500, 150)

st.sidebar.header(_t["sb_stocc"])
perc_stoccaggio = st.sidebar.slider("Volume (% Prod. Annua)", 0.0, 50.0, 1.0)
capex_stocc_kg = st.sidebar.slider("CAPEX Storage (€/kg)", 100, 1500, 600)

st.sidebar.header(_t["sb_comp"])
profilo_comp = st.sidebar.selectbox("Tipo", ["Standard (500 bar)", "Booster (700 bar)"])
inc_comp, cons_comp = (0.24, 2.23) if "Standard" in profilo_comp else (0.42, 4.11)

st.sidebar.header(_t["sb_market"])
prezzo_h2 = st.sidebar.slider(_t["sb_price_h2"], 2.0, 20.0, 8.0)

# ==========================================
# LOGICA DI CALCOLO
# ==========================================
p_n, p_s, w_n, w_s, fallback = carica_profili("dataset_fotovoltaico_produzione.csv", "dataset_eolico_produzione.csv")
arr_pv, arr_wind = (p_n, w_n) if regione == "Nord Italia" else (p_s, w_s)

eff_sistema = 55.0 + cons_comp
ely_b, batt_b = (0.6, 6.0) if strategia_batt == "Yes" else (1.0, 0.0)

res_base, _ = simula_h2_plant(arr_pv*(quota_pv_pct/100), arr_wind*(1-quota_pv_pct/100), ely_b, batt_b)
molt = ((target_h2_kg * eff_sistema)/1000.0) / np.sum(res_base) if np.sum(res_base) > 0 else 0

taglia_pv, taglia_wind, taglia_ely = (quota_pv_pct/100)*molt, (1-quota_pv_pct/100)*molt, ely_b*molt
taglia_batt = min(batt_b * molt, taglia_pv * limite_batt_pv)

ely_usage, batt_soc = simula_h2_plant(arr_pv*taglia_pv, arr_wind*taglia_wind, taglia_ely, taglia_batt)

prod_pv_gwh = np.sum(arr_pv*taglia_pv) / 1000
prod_wind_gwh = np.sum(arr_wind*taglia_wind) / 1000
energia_assorbita = np.sum(ely_usage)
energia_sprecata = (np.sum(arr_pv*taglia_pv) + np.sum(arr_wind*taglia_wind)) - energia_assorbita

# Finanza analitica
WACC, VITA = 0.05, 20
CRF = (WACC * (1+WACC)**VITA) / ((1+WACC)**VITA - 1)

c_ely = taglia_ely * 1000 * capex_ely
c_batt = taglia_batt * 1000 * capex_batt
c_stocc = (target_h2_kg * perc_stoccaggio/100) * capex_stocc_kg
c_comp = (inc_comp * target_h2_kg) / CRF
c_grid = 0.0
taglia_connessione = taglia_pv + taglia_wind
if tipo_connessione == "ON-GRID":
    c_grid = (730000 + 300000*distanza_rete_km) if taglia_connessione > 6 else (8000 + 155000*distanza_rete_km)

capex_tot = c_ely + c_batt + c_stocc + c_comp + c_grid
opex_en = (np.sum(arr_pv*taglia_pv)*cfd_pv) + (np.sum(arr_wind*taglia_wind)*cfd_wind)
opex_maint = capex_tot * 0.03
lcoh = (opex_en + opex_maint + (capex_tot * CRF)) / target_h2_kg
ricavi = target_h2_kg * prezzo_h2
payback = capex_tot / (ricavi - opex_en - opex_maint) if (ricavi - opex_en - opex_maint) > 0 else 99

# ==========================================
# INTERFACCIA GRAFICA
# ==========================================

st.subheader(_t["sec1_title"])
t1, t2, t3, t4 = st.columns(4)
t1.metric(_t["sec1_ely"], f"{taglia_ely:,.1f} MW", f"Eff: {eff_sistema:.1f} kWh/kg")
t2.metric("Funzionamento Annuo", f"{(energia_assorbita/taglia_ely):,.0f} h/y")
t3.metric("Stoccaggio H2 (Massa)", f"{(target_h2_kg * perc_stoccaggio/100)/1000:,.1f} ton")
t4.metric("Consumo Suolo PV", f"{taglia_pv/0.7:,.1f} ha")

st.markdown("---")

st.subheader(_t["sec2_title"])
r1, r2, r3, r4 = st.columns(4)
r1.metric("PV Installato (MW)", f"{taglia_pv:,.1f} MW")
r2.metric("Energia PV Acquistata", f"{prod_pv_gwh:,.2f} GWh/y")
r3.metric("Eolico Installato (MW)", f"{taglia_wind:,.1f} MW")
r4.metric("Energia Eolico Acquistata", f"{prod_wind_gwh:,.2f} GWh/y")

# --- GRAFICO 8760 ---
st.markdown("---")
st.markdown("### ⏱️ Profilo Operativo Orario (Simulazione 8760h)")
df_8760 = pd.DataFrame({'PV': arr_pv*taglia_pv, 'Eolico': arr_wind*taglia_wind, 'Ely': ely_usage, 'SOC': batt_soc})
fig_8760 = make_subplots(specs=[[{"secondary_y": True}]])
fig_8760.add_trace(go.Scattergl(y=df_8760['PV'], name="PV (MW)", line=dict(color='#FFC107', width=1)), secondary_y=False)
fig_8760.add_trace(go.Scattergl(y=df_8760['Eolico'], name="Eolico (MW)", line=dict(color='#03A9F4', width=1)), secondary_y=False)
fig_8760.add_trace(go.Scattergl(y=df_8760['Ely'], name="Assorbimento Totale (MW)", line=dict(color='#D32F2F', width=2)), secondary_y=False)
fig_8760.add_trace(go.Scattergl(y=df_8760['SOC'], name="BESS SOC (MWh)", line=dict(color='#4CAF50', dash='dash')), secondary_y=True)
st.plotly_chart(fig_8760, use_container_width=True)

# --- ANALISI FINANZIARIA ---
st.markdown("---")
st.subheader(_t["fin_title"])
f1, f2, f3, f4 = st.columns(4)
f1.metric(_t["fin_lcoh"], f"€ {lcoh:.2f} / kg")
f2.metric(_t["fin_capex"], f"€ {capex_tot/1e6:.2f} MLN")
f3.metric(_t["fin_payback"], f"{payback:.1f} Anni" if payback < 50 else "In Perdita")
f4.metric("Ricavi Annuali", f"€ {ricavi/1e6:.2f} MLN/y")

# ==========================================
# EXPORT ZAPIER
# ==========================================
st.markdown("---")
st.header("🔗 Esportazione Dati")
st.info("Invia i risultati del dimensionamento al Master Database.")

# Input dell'ID Progetto
istat_comune = st.text_input(_t["input_istat"])

if st.button(_t["btn_export"]):
    if not istat_comune:
        st.error(_t["export_error"])
    else:
        # 1. Creazione del Payload (Pacchetto dati) con i nomi ESATTI delle colonne Master
        payload = {
            "ID_ISTAT": istat_comune,
            "T26_TAGLIA_ELETTROLIZZATORE_MW": round(taglia_ely, 2),
            "T26_TAGLIA_FER_INSTALLATA_MW": round(taglia_pv + taglia_wind, 2),
            "T26_CAPACITA_BESS_MWH": round(taglia_batt, 2),
            "T26_CAPEX_TOTALE_MLN": round(capex_tot / 1e6, 2),
            "T26_LCOH_EURO_KG": round(lcoh, 2),
            "T26_PAYBACK_ANNI": round(payback, 1) if payback < 99 else "N/A"
        }
        
        # 2. Inserisci qui l'URL del Webhook generato da Zapier
        ZAPIER_WEBHOOK_URL = "INCOLLA_QUI_IL_TUO_URL_DI_ZAPIER"
        
        try:
            response = requests.post(ZAPIER_WEBHOOK_URL, data=json.dumps(payload))
            if response.status_code == 200:
                st.success(_t["export_success"])
                st.balloons()
            else:
                st.error(f"Errore Zapier (Codice {response.status_code})")
        except Exception as e:
            st.error(f"Errore di connessione: {e}")
