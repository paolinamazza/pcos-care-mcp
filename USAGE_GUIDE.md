# PCOS Care MCP - Usage Guide

Guida pratica all'utilizzo di tutti i 12 tools disponibili tramite Claude Desktop.

## 📋 Indice

1. [Symptom Tracking](#symptom-tracking)
2. [Cycle Tracking](#cycle-tracking)
3. [Pattern Analysis](#pattern-analysis)
4. [Medical Information (RAG)](#medical-information-rag)
5. [Utility](#utility)

---

## Symptom Tracking

### 1. `track_symptom` - Registra un sintomo

Registra un nuovo sintomo PCOS con intensità e note opzionali.

**Esempio conversazione:**
```
Tu: "Ho crampi abbastanza forti oggi, direi intensità 8"

Claude: [usa track_symptom]
{
  "symptom_type": "crampi",
  "intensity": 8,
  "notes": "Crampi forti"
}

→ Sintomo registrato con successo! ✅
  L'intensità alta suggerisce di considerare antidolorifici...
```

**Sintomi supportati:**
- `crampi` - Dolori mestruali
- `mal_di_testa` - Mal di testa/emicrania
- `acne` - Problemi pelle
- `gonfiore` - Ritenzione liquidi
- `stanchezza` - Fatica/sonnolenza
- `ansia` - Sintomi ansiosi
- `sbalzi_umore` - Variazioni umore
- `fame_nervosa` - Aumento appetito
- `dolore_seno` - Sensibilità seno

**Intensità:** 1-10 (1=lieve, 10=molto forte)

### 2. `get_recent_symptoms` - Visualizza sintomi recenti

Recupera lo storico degli ultimi sintomi registrati.

**Esempio conversazione:**
```
Tu: "Quali sintomi ho registrato negli ultimi giorni?"

Claude: [usa get_recent_symptoms]
{
  "limit": 10
}

→ Ultimi 10 sintomi:
  1. Crampi (intensità 8) - 2 giorni fa
  2. Mal di testa (intensità 6) - 3 giorni fa
  3. Gonfiore (intensità 5) - 5 giorni fa
  ...
```

### 3. `get_symptom_summary` - Statistiche sintomi

Genera un riepilogo statistico dei sintomi in un periodo.

**Esempio conversazione:**
```
Tu: "Dammi un riepilogo dei miei sintomi dell'ultimo mese"

Claude: [usa get_symptom_summary]
{
  "days": 30
}

→ Riepilogo ultimi 30 giorni:
  - Totale sintomi registrati: 24
  - Sintomo più frequente: crampi (12 volte)
  - Intensità media: 6.5/10
  - Insights: I crampi sono più frequenti nella settimana pre-mestruale
```

---

## Cycle Tracking

### 4. `track_cycle` - Registra ciclo mestruale

Registra l'inizio di un nuovo ciclo mestruale.

**Esempio conversazione:**
```
Tu: "Il ciclo mi è iniziato oggi con flusso medio"

Claude: [usa track_cycle]
{
  "start_date": "today",
  "flow_intensity": "medium"
}

→ Ciclo registrato! 📅
  Intensità flusso: medio
  ✅ Lunghezza nella norma (3-7 giorni)
```

**Intensità flusso supportate:**
- `spotting` - Spotting/perdite minime
- `light` - Flusso leggero
- `medium` - Flusso medio
- `heavy` - Flusso abbondante
- `very_heavy` - Flusso molto abbondante

### 5. `update_cycle_end` - Aggiorna fine ciclo

Aggiorna la data di fine di un ciclo già registrato.

**Esempio conversazione:**
```
Tu: "Il ciclo è finito oggi"

Claude: [prima recupera l'ID dell'ultimo ciclo, poi usa update_cycle_end]
{
  "cycle_id": 5,
  "end_date": "today"
}

→ Fine ciclo aggiornata! ✅
  Durata totale: 5 giorni
  ✅ Lunghezza nella norma
```

### 6. `get_cycle_history` - Storico cicli

Visualizza lo storico dei cicli mestruali.

**Esempio conversazione:**
```
Tu: "Mostrami gli ultimi cicli registrati"

Claude: [usa get_cycle_history]
{
  "limit": 6
}

→ Ultimi 6 cicli:
  1. 15/10 - 20/10 (5 giorni) - flusso medio
  2. 18/09 - 23/09 (5 giorni) - flusso heavy
  3. 22/08 - 26/08 (4 giorni) - flusso medio
  ...
```

### 7. `get_cycle_analytics` - Analytics e predizioni

Genera analytics avanzate sui cicli con predizione del prossimo.

**Esempio conversazione:**
```
Tu: "Quando dovrebbe arrivarmi il prossimo ciclo?"

Claude: [usa get_cycle_analytics]
{
  "months": 6
}

→ Analytics ultimi 6 mesi:
  - Totale cicli: 6
  - Lunghezza media: 5.2 giorni
  - Regolarità: 85/100 (ottima!)
  - Ciclo più corto: 4 giorni
  - Ciclo più lungo: 6 giorni

  🔮 Predizione prossimo ciclo: 18 novembre 2025

  Insights:
  ✅ Ottima regolarità - i tuoi cicli sono molto prevedibili!
  ✅ Lunghezza media nella norma
```

---

## Pattern Analysis

### 8. `analyze_symptom_cycle_correlation` - Correlazioni sintomi-ciclo

Analizza la correlazione tra sintomi e fasi del ciclo mestruale.

**Esempio conversazione:**
```
Tu: "C'è una correlazione tra i miei sintomi e il ciclo?"

Claude: [usa analyze_symptom_cycle_correlation]
{
  "months": 3
}

→ Analisi correlazione (ultimi 3 mesi):

  Sintomi analizzati: 45
  Cicli analizzati: 3

  Correlazioni trovate:
  - Crampi: 85% nella fase pre-mestruale
  - Mal di testa: 70% nella fase mestruale
  - Gonfiore: 60% nella fase pre-mestruale

  Insights:
  🔄 I crampi sono fortemente correlati alla fase pre-mestruale
  💡 Considera antidolorifici preventivi 2-3 giorni prima del ciclo
```

### 9. `analyze_symptom_trends` - Trend sintomi

Analizza i trend temporali di un sintomo specifico.

**Esempio conversazione:**
```
Tu: "I miei mal di testa stanno peggiorando?"

Claude: [usa analyze_symptom_trends]
{
  "symptom_type": "mal_di_testa",
  "days": 90
}

→ Trend mal di testa (ultimi 90 giorni):

  Frequenza: 12 episodi
  Intensità media: 6.5/10
  Trend: ↗️ In aumento del 15%

  Insights:
  ⚠️ L'intensità media è aumentata nell'ultimo mese
  💡 Considera di consultare un medico se il trend continua
```

### 10. `identify_patterns` - Identifica pattern ricorrenti

Identifica pattern ricorrenti nei sintomi in base alle fasi del ciclo.

**Esempio conversazione:**
```
Tu: "Ci sono pattern ricorrenti nei miei sintomi?"

Claude: [usa identify_patterns]
{
  "min_occurrences": 2
}

→ Pattern ricorrenti identificati:

  🔄 Pattern 1: Crampi in fase pre-mestruale
     Occorrenze: 5 volte
     Fase: late (2-3 giorni prima del ciclo)

  🔄 Pattern 2: Gonfiore in fase mid-ciclo
     Occorrenze: 4 volte
     Fase: mid (10-14 giorni del ciclo)

  🔄 Pattern 3: Stanchezza in fase mestruale
     Occorrenze: 3 volte
     Fase: early (primi giorni del ciclo)
```

---

## Medical Information (RAG)

### 11. `get_medical_info` - Q&A evidence-based su PCOS

Sistema RAG per domande mediche con citazioni da knowledge base.

**Esempio conversazione:**
```
Tu: "Quali alimenti dovrei evitare con la PCOS?"

Claude: [usa get_medical_info]
{
  "question": "Quali alimenti dovrei evitare con la PCOS?"
}

→ Risposta evidence-based:

Con la PCOS, è consigliabile limitare o evitare:

1. **Zuccheri semplici e carboidrati raffinati**
   - Dolci, bibite zuccherate, pane bianco, pasta raffinata
   - Aumentano rapidamente la glicemia e l'insulina

2. **Cibi ad alto indice glicemico**
   - Patate, riso bianco, corn flakes
   - Peggiorano la resistenza insulinica

3. **Prodotti industriali ultra-processati**
   - Snack confezionati, cibi pronti, fast food
   - Contengono grassi trans e additivi

4. **Latticini in eccesso** (per alcune persone)
   - Possono aumentare infiammazione e acne

**Fonti consultate:**
📚 "PCOS Nutrition Guide" - Principi dieta anti-infiammatoria
📚 "Managing Insulin Resistance" - Indice glicemico e PCOS
📚 "Lifestyle Modifications" - Raccomandazioni dietetiche evidence-based
```

**Knowledge Base copre:**
- PCOS basics (Rotterdam criteria)
- Sintomi comuni
- Nutrizione e dieta
- Lifestyle e esercizio
- Supplementi (inositol, vitamin D, omega-3)
- Trattamenti medici
- Fertilità e gravidanza
- Salute mentale
- Rischi a lungo termine

---

## Utility

### 12. `hello_pcos` - Test connessione

Tool di test per verificare che il server MCP sia connesso.

**Esempio conversazione:**
```
Tu: "Ciao!"

Claude: [usa hello_pcos]
{}

→ Ciao! 👋

  Benvenuta nel PCOS Care Assistant!

  Sono qui per aiutarti con:
  📊 Tracking sintomi PCOS
  📅 Monitoraggio ciclo mestruale
  🧠 Analisi pattern e insights
  📚 Informazioni mediche evidence-based

  Come posso aiutarti oggi?
```

---

## 💡 Tips per usare al meglio il sistema

### 1. **Tracking regolare**
Registra sintomi e cicli costantemente per analytics più accurate.

```
Tu (ogni giorno): "Oggi ho un po' di gonfiore, intensità 4"
Claude: [track_symptom] → ✅ Registrato!

Tu (ogni ciclo): "Il ciclo mi è iniziato oggi"
Claude: [track_cycle] → ✅ Registrato!
```

### 2. **Analisi periodiche**
Richiedi analytics e pattern ogni mese.

```
Tu (ogni mese): "Dammi un'analisi completa del mese scorso"
Claude:
  [get_symptom_summary]
  [get_cycle_analytics]
  [analyze_symptom_cycle_correlation]

→ Report completo mensile
```

### 3. **Linguaggio naturale**
Parla naturalmente - Claude capisce il contesto!

```
❌ Non serve: "usa track_symptom con crampi intensità 7"
✅ Dì semplicemente: "Ho crampi forti, tipo un 7/10"
```

### 4. **Combina domande**
Puoi chiedere più cose insieme.

```
Tu: "Ho crampi forti oggi. Come va il trend dei crampi
     nell'ultimo mese? E quando dovrebbe arrivarmi il prossimo ciclo?"

Claude:
  [track_symptom] → crampi registrati
  [analyze_symptom_trends] → trend crampi
  [get_cycle_analytics] → predizione prossimo ciclo
```

### 5. **Chiedi spiegazioni**
Per qualsiasi dubbio medico, usa il RAG system.

```
Tu: "Perché ho più sintomi prima del ciclo?"

Claude: [get_medical_info]
→ Spiegazione evidence-based con citazioni
```

---

## 🚨 Note Importanti

1. **Questo tool è per supporto e tracking, NON sostituisce il parere medico**
2. Per sintomi gravi o persistenti, consulta sempre un medico
3. Le predizioni del ciclo sono stime basate sui tuoi dati storici
4. Il RAG system usa fonti evidence-based ma non è consiglio medico personalizzato

---

## 📞 Supporto

Per problemi tecnici:
1. Controlla che Claude Desktop sia connesso (icona 🔌)
2. Verifica che il server sia in esecuzione
3. Consulta il README.md per troubleshooting

**Buon tracking! 🌸**
