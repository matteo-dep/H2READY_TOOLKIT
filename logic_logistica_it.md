## 5. Motore di Calcolo: Dimensionamento Fisico ed Economico (Modello a Scatola Bianca)

Al fine di garantire la massima trasparenza e aderenza agli standard ingegneristici, il simulatore non utilizza valori forfettari, ma calcola dinamicamente l'architettura della stazione attraverso un motore termodinamico e finanziario. Di seguito viene esplicitata la logica di calcolo ("scatola bianca") utilizzata dall'algoritmo.

### A. Portata del Compressore vs. Velocità di Rifornimento
È fondamentale distinguere tra la capacità dell'impianto di "ricaricare se stesso" e la velocità con cui l'idrogeno viene iniettato nel veicolo:
* **La Portata del Compressore (kg/ora):** Viene dimensionata dal software in base al fabbisogno giornaliero e alla finestra temporale di lavoro. Rappresenta la fatica meccanica per prelevare il gas dalla sorgente (es. carro bombolaio a 200 bar) e spingerlo fino alla pressione di stoccaggio (es. 500 o 900 bar).
* **La Velocità di Erogazione (g/s):** È svincolata dal compressore ed è governata esclusivamente dal protocollo di sicurezza mondiale **SAE J2601**. Il simulatore impone un tetto massimo di erogazione pari a **120 g/s** per le erogazioni a 350 bar (Bus/Camion HDV) e un limite più stringente di **60 g/s** per i 700 bar (a causa del violento innalzamento termico). Di conseguenza, il tempo fisico per effettuare il pieno di un mezzo pesante da 50 kg richiederà sempre un tempo incomprimibile stimabile dal software (es. circa 14 minuti a 700 bar).

### B. Struttura dei Costi di Investimento (CAPEX)
Il costo totale d'impianto (CAPEX) restituito dal simulatore è la somma maggiorata di quattro moduli fondamentali:
1. **Modulo di Stoccaggio:** Moltiplica i chilogrammi di serbatoi fisici necessari per un costo parametrico di mercato (stimato in 1.092 €/kg per i magazzini a cascata o 968 €/kg per i sistemi a pressione costante). Il volume dei serbatoi include sempre un fattore di sovradimensionamento di sicurezza (1.9x).
2. **Modulo di Compressione:** Prende la potenza elettrica reale (kW), derivata dal calcolo del lavoro isentropico multistadio inter-refrigerato, e le applica un costo specifico per l'idrogeno (circa 2.500 €/kW).
3. **Erogazione e Pre-Raffreddamento (Chiller):** Ai costi fissi del dispenser (200.000 €) vengono aggiunti i costi del sistema di refrigerazione forzata, che raddoppiano (120.000 €) se l'utente seleziona l'erogazione a 700 bar, la quale richiede idrogeno ghiacciato a -40 °C per non usurare i serbatoi in fibra di carbonio del veicolo.
4. **Opere Civili e Sicurezza:** Il totale impiantistico viene maggiorato di un +25% per coprire scavi, fondazioni, muri parafiamma e allacciamenti elettrici.

### C. Costi Operativi (OPEX)
Il software suddivide i costi di gestione annui in due macro-categorie visibili all'utente:
* **OPEX Fisso (O&M):** Calcolato forfettariamente come il 4% annuo del CAPEX. Copre la manutenzione specialistica programmata, la taratura delle valvole di sicurezza, il personale e gli affitti.
* **OPEX Variabile (Costo Elettrico):** Rappresenta il consumo dei compressori e dei chiller. Il tool estrae l'assorbimento specifico in kWh per ogni kg compresso e lo moltiplica per i volumi annui e per il costo dell'energia elettrica impostato dall'utente (es. 0.15 €/kWh).

### D. Calcolo del Break-Even Point (Prezzo Minimo alla Pompa)
Per fornire uno strumento di pianificazione reale alle Pubbliche Amministrazioni, il tool include un modulo di calcolo per il "Levelized Cost of Hydrogen" (LCOH). Questo rappresenta il prezzo di pareggio a cui la stazione deve vendere l'idrogeno al cliente finale per non generare perdite finanziarie.

L'algoritmo calcola la rata di ammortamento annuale dell'impianto applicando il Costo del Capitale (WACC) sulla vita utile dell'infrastruttura, attraverso la formula del fattore di recupero del capitale (CRF):

$$CRF = \frac{r \cdot (1 + r)^n}{(1 + r)^n - 1}$$

Dove $r$ è il WACC e $n$ gli anni di vita utile. 
Il Break-Even Point (€/kg) viene poi ricavato sommando la quota CAPEX annualizzata all'OPEX annuo totale e al costo di acquisto all'ingrosso della molecola di idrogeno, dividendo il tutto per i chilogrammi totali erogati in un anno.
