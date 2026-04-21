# Dizionario per l'interfaccia (Istruzioni e Label)
T = {
    "it": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.1: Scouting aziende HTA e RED III",
        "credits": "Sviluppato all'interno del progetto [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) da **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 GUIDA PER I COMUNI E LOGICA (Leggi prima di iniziare)",
        "instructions_md": """
### 🎯 Qual è il tuo obiettivo?
Come referente dell'Ente, il tuo compito è **mappare le industrie del tuo territorio** per capire quali hanno *reale* necessità di passare all'idrogeno verde (es. acciaierie, vetrerie, chimica) e quali invece dovrebbero solo usare più energia elettrica. Non serve essere un ingegnere, il sistema farà i calcoli per te.

**Segui questi 3 passaggi:**

**🟢 FASE 1: Mappatura iniziale (Screening)**
1. Scarica il **Template 1** tramite il bottone qui sotto.
2. Inserisci i dati base delle industrie locali (basta Nome, Codice ATECO e Dimensione). 
3. Carica il file completato nella sezione "FASE 1". Il simulatore applicherà un filtro termodinamico e ti restituirà l'elenco delle sole aziende "Idonee".

**🟡 FASE 2: Raccolta dei Fabbisogni**
1. Ora che sai chi sono le aziende idonee, contattale o stima il loro potenziale fabbisogno di idrogeno (in Tonnellate all'anno).
2. Scarica il **Template 2**, compila le tonnellate e carica il file nella "FASE 2".

**🔵 FASE 3: Invio al Master Database**
Una volta validato il file della Fase 2, inserisci il tuo **Codice Identificativo** in fondo alla pagina e clicca "Salva". I dati verranno usati per creare il Piano d'Azione (Action Plan) generale.

---
### 🧠 Come ragiona il simulatore (Logica Termodinamica)
Il tool non si limita a cercare chi usa genericamente "alte temperature". Legge le prime 4 cifre del codice ATECO e applica uno scoring scientifico:
* **🔴 Spreco Termodinamico (Scartate):** Processi a bassa temperatura, edilizia o produzione di vapore. L'idrogeno qui è inefficace: l'azienda dovrebbe usare pompe di calore o elettrificazione diretta.
* **🟠 Alert Elettrificazione (Tier 2):** Processi termici generici (es. forni per trattamenti termici) dove tecnologie alternative (es. forni elettrici a induzione) sono spesso più efficienti.
* **🟢 Assolutamente Necessario (Tier 1):** L'idrogeno è chimicamente insostituibile (es. come agente riducente per l'acciaio o materia prima nei fertilizzanti) o ci sono limiti fisici all'elettrificazione (es. grandi forni fusori continui per il vetro).
Il punteggio base viene poi aumentato (Bonus) se l'azienda è di grandi dimensioni o si trova vicino a infrastrutture strategiche come il *South H2 Corridor*.
        """,
        "btn_template1": "📥 1. Scarica Template Screening (Fase 1)",
        "btn_template2": "📥 2. Scarica Template Fabbisogni (Fase 2)",
        "header_fase1": "📤 FASE 1: Caricamento e Analisi Termodinamica",
        "header_fase2": "📤 FASE 2: Consolidamento Fabbisogni (Export per Action Plan)",
        "input_istat": "Inserisci il Codice Identificativo (es. 030043):",
        "btn_export": "🚀 Salva Risultati nel Database Centrale",
        "export_success": "✅ Dati salvati con successo nel Master Database!"
    },
    "en": {
        "title": "🚀 H2READY TOOLKIT - Tool 2.1: HTA and RED III Company Scouting",
        "credits": "Developed within the [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready) project by **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 USER GUIDE AND LOGIC (Read before starting)",
        "instructions_md": """
### 🎯 What is your goal?
Your task is to **map the industries in your area** to understand which ones have a *real* need to switch to green hydrogen (e.g., steelworks, glassworks, chemicals) and which ones should simply use electricity. You don't need to be an engineer; the system does the math for you.

**Follow these 3 steps:**

**🟢 PHASE 1: Initial Mapping (Screening)**
1. Download **Template 1** using the button below.
2. Enter the basic data of local industries (just Name, NACE Code, and Size). 
3. Upload the completed file in the "PHASE 1" section. The simulator will apply a thermodynamic filter and give you a list of only the "Eligible" companies.

**🟡 PHASE 2: Needs Consolidation**
1. Now that you know the eligible companies, contact them or estimate their potential hydrogen needs (in Tons per year).
2. Download **Template 2**, fill in the tonnage, and upload the file in "PHASE 2".

**🔵 PHASE 3: Send to Master Database**
Once the Phase 2 file is validated, enter your **Identification Code** at the bottom of the page and click "Save". The data will be used to create the general Action Plan.

---
### 🧠 How the simulator thinks (Thermodynamic Logic)
The tool doesn't just look for "high temperatures". It reads the NACE code and applies a scientific scoring system:
* **🔴 Thermodynamic Waste (Discarded):** Low-temp processes, construction, or steam production. Hydrogen is inefficient here: direct electrification or heat pumps should be used.
* **🟠 Electrification Alert (Tier 2):** Generic thermal processes where alternative technologies (e.g., electric induction furnaces) are often more efficient.
* **🟢 Absolutely Necessary (Tier 1):** Hydrogen is chemically irreplaceable (e.g., reducing agent in steel or feedstock in fertilizers) or there are physical limits to electrification (e.g., huge continuous glass melting furnaces).
The base score is then boosted if the company is large or located near strategic infrastructures like the *South H2 Corridor*.
        """,
        "btn_template1": "📥 1. Download Screening Template (Phase 1)",
        "btn_template2": "📥 2. Download Needs Template (Phase 2)",
        "header_fase1": "📤 PHASE 1: Upload and Thermodynamic Analysis",
        "header_fase2": "📤 PHASE 2: Needs Consolidation (Export for Action Plan)",
        "input_istat": "Enter the Identification Code (e.g. 030043):",
        "btn_export": "🚀 Save Results to Central Database",
        "export_success": "✅ Data successfully saved in the Master Database!"
    },
    "sl": {
        "title": "🚀 H2READY TOOLKIT - Orodje 2.1: Iskanje podjetij HTA in RED III",
        "credits": "Razvito v okviru projekta [INTERREG H2Ready](https://www.ita-slo.eu/en/h2ready), avtor **Matteo De Piccoli - [APE FVG](https://www.ape.fvg.it/)**",
        "instr_title": "📖 VODNIK ZA UPORABNIKE IN LOGIKA (Preberite pred začetkom)",
        "instructions_md": """
### 🎯 Kakšen je vaš cilj?
Vaša naloga je **kartiranje industrij na vašem območju**, da ugotovite, katere imajo *resnično* potrebo po prehodu na zeleni vodik (npr. jeklarne, steklarne, kemikalije) in katere bi morale preprosto uporabljati električno energijo. Ni vam treba biti inženir, sistem bo izračunal namesto vas.

**Sledite tem 3 korakom:**

**🟢 1. FAZA: Začetno kartiranje (Pregled)**
1. Prenesite **Predlogo 1** s spodnjim gumbom.
2. Vnesite osnovne podatke o lokalnih industrijah (samo Ime, Kodo ATECO/NACE in Velikost). 
3. Naložite izpolnjeno datoteko v razdelku "1. FAZA". Simulator bo uporabil termodinamični filter in vam vrnil seznam samo "Ustreznih" podjetij.

**🟡 2. FAZA: Zbiranje potreb**
1. Zdaj, ko poznate ustrezna podjetja, stopite v stik z njimi ali ocenite njihove potencialne potrebe po vodiku (v tonah na leto).
2. Prenesite **Predlogo 2**, vnesite tonažo in naložite datoteko v "2. FAZI".

**🔵 3. FAZA: Pošiljanje v glavno bazo podatkov**
Ko je datoteka 2. faze potrjena, na dnu strani vnesite svojo **Identifikacijsko kodo** in kliknite "Shrani". Podatki bodo uporabljeni za ustvarjanje splošnega Akcijskega načrta.

---
### 🧠 Kako deluje simulator (Termodinamična logika)
Orodje ne išče zgolj "visokih temperatur". Prebere kodo NACE in uporabi znanstveni sistem točkovanja:
* **🔴 Termodinamična izguba (Zavrnjeno):** Nizkotemperaturni procesi ali proizvodnja pare. Vodik je tu neučinkovit: uporabiti bi bilo treba neposredno elektrifikacijo ali toplotne črpalke.
* **🟠 Opozorilo za elektrifikacijo (Tier 2):** Generični toplotni procesi, kjer so alternativne tehnologije (npr. električne indukcijske peči) pogosto učinkovitejše.
* **🟢 Absolutno nujno (Tier 1):** Vodik je kemično nenadomestljiv (npr. reducent pri jeklu) ali pa obstajajo fizične omejitve za elektrifikacijo (velike peči za taljenje stekla).
Osnovna ocena se nato poveča, če je podjetje veliko ali se nahaja blizu strateške infrastrukture (npr. *South H2 Corridor*).
        """,
        "btn_template1": "📥 1. Prenesi predlogo za pregled (1. faza)",
        "btn_template2": "📥 2. Prenesi predlogo za potrebe (2. faza)",
        "header_fase1": "📤 1. FAZA: Nalaganje in termodinamična analiza",
        "header_fase2": "📤 2. FAZA: Konsolidacija potreb (Izvoz za akcijski načrt)",
        "input_istat": "Vnesite identifikacijsko kodo (npr. 030043):",
        "btn_export": "🚀 Shrani rezultate v centralno bazo",
        "export_success": "✅ Podatki so uspešno shranjeni v glavno bazo!"
    }
}
_t = T[LANG]
