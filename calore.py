import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================================================
# DSS COMUNI - Tool 2.4: Confronto sistemi di riscaldamento (H2 / Elc / FF)
# Versione STANDALONE: tutti i dati sono incorporati nel codice.
# Non è più necessario il file "Comparison H2 elc FF.xlsx".
#
# I valori derivano dal foglio "CALORE" del file originale:
#  - efficienza/COP, consumo vettore, energia primaria, emissioni WtT/TtW,
#    emissioni di costruzione, manutenzione e CAPEX di ciascuna tecnologia.
# Sono escluse, come nell'originale, le righe "Effetto Joule" e "Geotermica".
#
# NOTA (correzione): nella versione legata all'Excel le emissioni di
# costruzione delle due pompe di calore venivano risolte male da una ricerca
# per nome (2000 e 1200 kg). Qui usiamo il valore corretto di tabella: 1400 kg.
# ==========================================================================

st.set_page_config(page_title="DSS Comuni: Riscaldamento", page_icon="🔥", layout="wide")
st.title("🔥 DSS Comuni: Analisi Sistemi di Riscaldamento")

if os.path.exists("ReadMe_calore.md"):
    with st.expander("ℹ️ Leggi Istruzioni, Limiti e Assunzioni"):
        with open("ReadMe_calore.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())

# ==========================================================================
# 1. DATI INCORPORATI
# ==========================================================================
# Ogni tecnologia: valori "base" tratti dal foglio CALORE (fabbisogno base 10.000 kWh/y).
# I calcoli scalano questi valori in proporzione al fabbisogno scelto dall'utente.
#   eta_cop       : η o COP di riferimento (per le PdC è sostituito dallo slider COP)
#   consumo_base  : consumo del vettore [kWh/y] al fabbisogno base
#   en_prim_base  : energia primaria [kWh] al fabbisogno base
#   wtt_base      : emissioni Well-to-Tank (filiera) [kgCO2/y] al base
#   ttw_base      : emissioni Tank-to-Wheel (camino) [kgCO2/y] al base
#   constr        : emissioni di costruzione del sistema [kgCO2] (totale, poi spalmate)
#   maint         : manutenzione [€/anno]
#   capex         : investimento iniziale [€]
#   fuel_key      : chiave del prezzo del vettore (vedi FUELS)
#   is_pdc        : True per le pompe di calore (usano lo slider COP)
TECHNOLOGIES = [
    {"name": "Caldaia a Gasolio [Gasolio]",            "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 12771.392082, "wtt_base": 444.305319,  "ttw_base": 2962.035457, "constr": 1200, "maint": 225.0,        "capex": 3500,  "fuel_key": "diesel",        "is_pdc": False},
    {"name": "Caldaia a Metano [CH4]",                 "eta_cop": 1.0, "consumo_base": 10000.000000, "en_prim_base": 10989.010989, "wtt_base": 575.000000,  "ttw_base": 2050.000000, "constr": 950,  "maint": 200.0,        "capex": 2750,  "fuel_key": "metano",        "is_pdc": False},
    {"name": "Stufa a Pellet [Pellet]",                "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 13071.895425, "wtt_base": 422.222222,  "ttw_base": 0.000000,    "constr": 650,  "maint": 300.0,        "capex": 3000,  "fuel_key": "pellet",        "is_pdc": False},
    {"name": "PdC rete [Elc da rete]",                 "eta_cop": 3.0, "consumo_base": 3333.333333,  "en_prim_base": 6666.666667,  "wtt_base": 716.666667,  "ttw_base": 0.000000,    "constr": 1400, "maint": 150.0,        "capex": 11500, "fuel_key": "elc_rete",      "is_pdc": True},
    {"name": "PdC autoprodotta [Elc autoprodotta]",    "eta_cop": 3.0, "consumo_base": 3333.333333,  "en_prim_base": 3703.703704,  "wtt_base": 183.333333,  "ttw_base": 0.000000,    "constr": 1400, "maint": 150.0,        "capex": 11500, "fuel_key": "elc_auto",      "is_pdc": True},
    {"name": "Caldaia a idrogeno [H2 grigio]",         "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 15873.015873, "wtt_base": 3667.033370, "ttw_base": 0.000000,    "constr": 1200, "maint": 509.090909,   "capex": 7000,  "fuel_key": "h2_grigio",     "is_pdc": False},
    {"name": "Caldaia a idrogeno [H2 elettrolisi rete]","eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 40404.040404, "wtt_base": 4300.430043, "ttw_base": 0.000000,    "constr": 1200, "maint": 509.090909,   "capex": 7000,  "fuel_key": "h2_rete",       "is_pdc": False},
    {"name": "Caldaia a idrogeno [H2 verde auto]",     "eta_cop": 0.9, "consumo_base": 11111.111111, "en_prim_base": 17921.146953, "wtt_base": 1000.100010, "ttw_base": 0.000000,    "constr": 1200, "maint": 509.090909,   "capex": 7000,  "fuel_key": "h2_verde_auto", "is_pdc": False},
]

# Prezzi dei vettori: l'utente modifica il valore "in natura" (€/l, €/kg, ...).
# prezzo_kwh = valore_natura * factor.  (factor = €/kWh ÷ valore_natura del foglio)
FUELS = {
    "diesel":        {"label": "Gasolio",                   "natura": 1.8,  "unit": "€/l",     "factor": 0.10097848148559},
    "metano":        {"label": "Metano",                    "natura": 0.95, "unit": "€/Sm³",   "factor": 0.10427528675703},
    "pellet":        {"label": "Pellet",                    "natura": 4.5,  "unit": "€/sacco", "factor": 0.01360544217687},
    "elc_rete":      {"label": "Elettricità da rete",       "natura": 0.31, "unit": "€/kWh",   "factor": 1.0},
    "elc_auto":      {"label": "Elettricità autoprodotta",  "natura": 0.24, "unit": "€/kWh",   "factor": 1.0},
    "h2_grigio":     {"label": "Idrogeno grigio",           "natura": 2.0,  "unit": "€/kg",    "factor": 0.03000300030003},
    "h2_rete":       {"label": "Idrogeno da rete",          "natura": 20.0, "unit": "€/kg",    "factor": 0.03000300030003},
    "h2_verde_auto": {"label": "Idrogeno verde autoprod.",  "natura": 15.0, "unit": "€/kg",    "factor": 0.03000300030003},
}

DEFAULT_FABBISOGNO = 10000   # kWh termici/anno
DEFAULT_LIFETIME = 20        # anni
DEFAULT_COP = 3.0            # COP PdC Aria-Acqua

# ==========================================================================
# 2. SIDEBAR - PARAMETRI
# ==========================================================================
st.sidebar.header("⚡ Costi e Parametri")

prezzi_kwh = {}
for key, f in FUELS.items():
    user_val = st.sidebar.number_input(f"{f['label']} [{f['unit']}]", value=float(f["natura"]), format="%.3f")
    prezzi_kwh[key] = user_val * f["factor"]

user_cop = st.sidebar.number_input("COP Pompa di Calore", value=DEFAULT_COP, step=0.1)
user_fabbisogno = st.sidebar.slider("Fabbisogno Termico [kWh/y]", 2000, 50000, DEFAULT_FABBISOGNO, 1000)
user_lifetime = st.sidebar.slider("Vita Utile (y)", 1, 30, DEFAULT_LIFETIME, 1)

# ==========================================================================
# 3. MOTORE DI CALCOLO
# ==========================================================================
def calcola(t):
    eta = user_cop if t["is_pdc"] else t["eta_cop"]
    if eta == 0:
        eta = 1.0
    consumo_vettore = user_fabbisogno / eta
    cb = t["consumo_base"] if t["consumo_base"] > 0 else 1.0
    fattore_scala = consumo_vettore / cb

    en_primaria = t["en_prim_base"] * fattore_scala
    wtt_annuo = consumo_vettore * (t["wtt_base"] / cb)
    ttw_annuo = consumo_vettore * (t["ttw_base"] / cb)
    costruz_annuo = t["constr"] / user_lifetime

    fuel_annuo = consumo_vettore * prezzi_kwh.get(t["fuel_key"], 0.10)
    maint_annuo = t["maint"]
    capex_annuo = t["capex"] / user_lifetime

    return {
        "Tecnologia": t["name"],
        "En_Primaria": en_primaria,
        "Eta_Attiva": eta,
        "WtT_Annuo": wtt_annuo,
        "TtW_Annuo": ttw_annuo,
        "Costruz_Annuo": costruz_annuo,
        "Emiss_Tot_Annue": wtt_annuo + ttw_annuo + costruz_annuo,
        "Fuel_Annuo": fuel_annuo,
        "Maint_Annuo": maint_annuo,
        "CAPEx_Annuo": capex_annuo,
        "Costo_Annuo_Tot": fuel_annuo + maint_annuo + capex_annuo,
    }

df_clean = pd.DataFrame([calcola(t) for t in TECHNOLOGIES])
ordine_tecnologie = df_clean["Tecnologia"].tolist()[::-1]

# ==========================================================================
# 4. GRAFICI
# ==========================================================================
st.divider()

st.subheader(f"1. Energia Primaria Richiesta per soddisfare il fabbisogno pari a {user_fabbisogno} [kWh/y]")
fig1 = px.bar(df_clean, y="Tecnologia", x="En_Primaria", color="Tecnologia", orientation='h',
              category_orders={"Tecnologia": ordine_tecnologie})
fig1.update_yaxes(autorange="reversed", title_text=""); fig1.update_xaxes(title_text="")
fig1.update_layout(showlegend=False, height=400)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("2. Efficienza della Macchina (η / COP)")
fig2 = px.bar(df_clean, y="Tecnologia", x="Eta_Attiva", color="Tecnologia", orientation='h',
              text_auto='.2f', category_orders={"Tecnologia": ordine_tecnologie})
fig2.update_yaxes(autorange="reversed", title_text=""); fig2.update_xaxes(title_text="")
fig2.update_layout(showlegend=False, height=400)
st.plotly_chart(fig2, use_container_width=True)

st.subheader(f"3. Impronta Carbonica ANNUA [kg CO2/y] (costruzione spalmata in {user_lifetime} anni)")
df_em = df_clean.melt(id_vars="Tecnologia", value_vars=['WtT_Annuo', 'TtW_Annuo', 'Costruz_Annuo'],
                      var_name="Fase", value_name="E")
df_em["Fase"] = df_em["Fase"].replace({'WtT_Annuo': 'WtT (Filiera)', 'TtW_Annuo': 'TtW (Camino)',
                                       'Costruz_Annuo': f'Costruzione (spalmata in {user_lifetime} y)'})
fig3 = px.bar(df_em, y="Tecnologia", x="E", color="Fase", orientation='h', barmode='stack',
              category_orders={"Tecnologia": ordine_tecnologie},
              color_discrete_sequence=["#8B4513", "#CD5C5C", "#A9A9A9"])
fig3.update_yaxes(autorange="reversed", title_text=""); fig3.update_xaxes(title_text="")
fig3.update_layout(height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title_text=""))
st.plotly_chart(fig3, use_container_width=True)

st.subheader(f"4. Costo ANNUO (TCO/y) [€/y] (acquisto spalmato in {user_lifetime} anni)")
df_c = df_clean.melt(id_vars="Tecnologia", value_vars=['CAPEx_Annuo', 'Maint_Annuo', 'Fuel_Annuo'],
                     var_name="V", value_name="Eur")
df_c["V"] = df_c["V"].replace({'CAPEx_Annuo': f'CAPEx (spalmato in {user_lifetime} y)',
                              'Maint_Annuo': 'Manutenzione', 'Fuel_Annuo': 'Vettore Energetico'})
fig4 = px.bar(df_c, y="Tecnologia", x="Eur", color="V", orientation='h', barmode='stack',
              category_orders={"Tecnologia": ordine_tecnologie},
              color_discrete_sequence=["#0068C9", "#FFA421", "#FF4B4B"])
fig4.update_yaxes(autorange="reversed", title_text=""); fig4.update_xaxes(title_text="")
fig4.update_layout(height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title_text=""))
st.plotly_chart(fig4, use_container_width=True)

st.subheader("📋 Riepilogo Dati")
st.dataframe(
    df_clean[["Tecnologia", "En_Primaria", "Eta_Attiva", "Emiss_Tot_Annue", "Costo_Annuo_Tot"]].style.format(
        {"En_Primaria": "{:,.0f}", "Eta_Attiva": "{:.2f}", "Emiss_Tot_Annue": "{:,.0f}", "Costo_Annuo_Tot": "€ {:,.0f}"}),
    use_container_width=True
)
