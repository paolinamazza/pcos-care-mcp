"""
PCOS Knowledge Base - FASE 3
Documenti evidence-based su PCOS per il sistema RAG
"""

# Knowledge base strutturata per RAG
PCOS_DOCUMENTS = [
    # === BASICS ===
    {
        "id": "pcos_001",
        "category": "basics",
        "title": "Cos'è la PCOS",
        "content": """
La Sindrome dell'Ovaio Policistico (PCOS) è un disturbo ormonale comune che colpisce
le donne in età riproduttiva. È una delle cause più comuni di infertilità femminile.
La PCOS è caratterizzata da:
- Irregolarità mestruali (cicli assenti, irregolari o prolungati)
- Livelli elevati di androgeni (ormoni maschili)
- Ovaie policistiche visibili all'ecografia
Per diagnosticare la PCOS si utilizzano i criteri di Rotterdam:
almeno 2 su 3 di questi criteri devono essere presenti.
        """,
        "source": "Rotterdam ESHRE/ASRM-Sponsored PCOS consensus workshop group, 2004"
    },

    # === SYMPTOMS ===
    {
        "id": "pcos_002",
        "category": "symptoms",
        "title": "Sintomi comuni della PCOS",
        "content": """
I sintomi più comuni della PCOS includono:
- Irregolarità mestruali: cicli che durano più di 35 giorni, meno di 8 cicli all'anno
- Irsutismo: crescita eccessiva di peli su viso, petto, schiena
- Acne severa o persistente, soprattutto su viso, petto e schiena superiore
- Alopecia androgenetica: diradamento dei capelli sul cuoio capelluto
- Aumento di peso, specialmente nella zona addominale
- Pelle grassa
- Macchie scure della pelle (acanthosis nigricans), spesso sul collo e sotto le ascelle
- Difficoltà a perdere peso
- Affaticamento cronico
- Sbalzi d'umore, ansia, depressione
        """,
        "source": "Mayo Clinic PCOS Guidelines, 2023"
    },

    {
        "id": "pcos_003",
        "category": "symptoms",
        "title": "Irregolarità mestruali nella PCOS",
        "content": """
Le irregolarità mestruali sono uno dei sintomi più evidenti della PCOS:
- Oligomenorrea: cicli mestruali che si verificano a intervalli superiori a 35 giorni
- Amenorrea: assenza di mestruazioni per 3 o più mesi consecutivi
- Menorragia: sanguinamento mestruale eccessivo o prolungato
- Spotting irregolare tra i cicli
Queste irregolarità sono causate dall'anovulazione (mancata ovulazione) dovuta
allo squilibrio ormonale. La lunghezza normale del ciclo è tra 21-35 giorni.
        """,
        "source": "American College of Obstetricians and Gynecologists, 2023"
    },

    # === NUTRITION ===
    {
        "id": "pcos_004",
        "category": "nutrition",
        "title": "Dieta per la PCOS - Principi generali",
        "content": """
La dieta gioca un ruolo fondamentale nella gestione della PCOS:
- Privilegiare alimenti a basso indice glicemico per migliorare la sensibilità insulinica
- Aumentare l'assunzione di fibre (verdure, legumi, cereali integrali)
- Includere proteine magre ad ogni pasto (pesce, pollo, legumi, tofu)
- Preferire grassi sani: omega-3 (pesce, noci, semi di lino), olio d'oliva, avocado
- Limitare zuccheri raffinati e carboidrati semplici
- Ridurre latticini e alimenti processati
- Mangiare piccoli pasti frequenti per stabilizzare la glicemia
- Bere molta acqua (almeno 2 litri al giorno)
Una dieta anti-infiammatoria può aiutare a ridurre i sintomi della PCOS.
        """,
        "source": "Journal of Clinical Endocrinology & Metabolism, 2023"
    },

    {
        "id": "pcos_005",
        "category": "nutrition",
        "title": "Alimenti da favorire con PCOS",
        "content": """
Alimenti consigliati per chi ha la PCOS:
- Verdure a foglia verde: spinaci, cavolo riccio, bietole
- Verdure crucifere: broccoli, cavolfiore, cavoli
- Bacche: mirtilli, fragole, lamponi (ricche di antiossidanti)
- Pesce grasso: salmone, sgombro, sardine (omega-3)
- Noci e semi: mandorle, noci, semi di chia, semi di lino
- Legumi: lenticchie, ceci, fagioli neri
- Cereali integrali: quinoa, riso integrale, avena
- Proteine magre: pollo, tacchino, tofu, tempeh
- Grassi sani: avocado, olio d'oliva extra vergine
- Spezie anti-infiammatorie: curcuma, zenzero, cannella
        """,
        "source": "Academy of Nutrition and Dietetics, 2023"
    },

    {
        "id": "pcos_006",
        "category": "nutrition",
        "title": "Alimenti da evitare con PCOS",
        "content": """
Alimenti da limitare o evitare se si ha la PCOS:
- Zuccheri raffinati: dolci, bibite zuccherate, caramelle
- Carboidrati raffinati: pane bianco, pasta bianca, prodotti da forno
- Cibi fritti e fast food
- Carni lavorate: salumi, salsicce, bacon
- Latticini ad alto contenuto di grassi (per alcune donne)
- Alcol (può influenzare i livelli ormonali)
- Caffeina in eccesso (può aumentare i livelli di cortisolo)
- Alimenti processati con additivi e conservanti
- Grassi trans e oli idrogenati
Ridurre questi alimenti può aiutare a migliorare i sintomi e la sensibilità insulinica.
        """,
        "source": "Endocrine Society Clinical Practice Guidelines, 2023"
    },

    # === LIFESTYLE ===
    {
        "id": "pcos_007",
        "category": "lifestyle",
        "title": "Esercizio fisico e PCOS",
        "content": """
L'attività fisica regolare è fondamentale per gestire la PCOS:
- Aiuta a migliorare la sensibilità insulinica
- Favorisce la perdita di peso (anche il 5-10% può migliorare i sintomi)
- Riduce il rischio di diabete tipo 2
- Migliora l'umore e riduce ansia e depressione
Raccomandazioni:
- Almeno 150 minuti di attività moderata a settimana (es. camminata veloce)
- O 75 minuti di attività intensa (es. corsa, HIIT)
- Esercizi di forza 2-3 volte a settimana
- Combinare cardio e pesi per risultati ottimali
- Yoga e pilates possono aiutare con stress e flessibilità
L'importante è trovare un'attività che ti piace per mantenerla nel tempo.
        """,
        "source": "American College of Sports Medicine, 2023"
    },

    {
        "id": "pcos_008",
        "category": "lifestyle",
        "title": "Gestione dello stress nella PCOS",
        "content": """
Lo stress può peggiorare i sintomi della PCOS aumentando il cortisolo:
Tecniche di gestione dello stress:
- Meditazione mindfulness (10-20 minuti al giorno)
- Respirazione diaframmatica
- Yoga
- Journaling
- Tempo nella natura
- Hobby creativi
- Sonno di qualità (7-9 ore per notte)
- Supporto sociale: parlare con amici, famiglia o gruppi di supporto
- Terapia cognitivo-comportamentale (CBT)
Lo stress cronico può influenzare negativamente gli ormoni, quindi
la gestione dello stress è una parte importante del trattamento della PCOS.
        """,
        "source": "Psychoneuroendocrinology Journal, 2023"
    },

    {
        "id": "pcos_009",
        "category": "lifestyle",
        "title": "Sonno e PCOS",
        "content": """
Un sonno di qualità è essenziale per la gestione della PCOS:
- Le donne con PCOS hanno maggior rischio di disturbi del sonno e apnea notturna
- La privazione di sonno peggiora la resistenza insulinica
- Il sonno insufficiente aumenta l'appetito e la voglia di cibi malsani
Consigli per migliorare il sonno:
- Mantieni un orario regolare (stessa ora di addormentamento e risveglio)
- Evita schermi 1-2 ore prima di dormire (luce blu)
- Crea una routine rilassante serale
- Mantieni la camera fresca (18-20°C)
- Evita caffeina dopo le 14:00
- Non mangiare pasti pesanti prima di dormire
- Considera integratori di magnesio (consulta il medico)
Se russi o ti senti sempre stanca, parla con il medico di possibile apnea notturna.
        """,
        "source": "Sleep Medicine Reviews, 2023"
    },

    # === SUPPLEMENTS ===
    {
        "id": "pcos_010",
        "category": "supplements",
        "title": "Integratori utili per PCOS",
        "content": """
Alcuni integratori possono aiutare a gestire i sintomi della PCOS
(IMPORTANTE: consultare sempre il medico prima di iniziare):
- Inositolo (Myo-inositolo + D-chiro-inositolo): migliora sensibilità insulinica e ovulazione
- Vitamina D: molte donne con PCOS sono carenti
- Omega-3: riduce infiammazione e migliora profilo lipidico
- Magnesio: supporta la sensibilità insulinica e il sonno
- Berberina: può migliorare la sensibilità insulinica (simile alla metformina)
- N-acetilcisteina (NAC): antiossidante che può migliorare ovulazione
- Acido alfa-lipoico: antiossidante che migliora sensibilità insulinica
- Cromo: può aiutare con il controllo glicemico
- Cannella: può migliorare sensibilità insulinica
Dosaggi e interazioni devono essere discussi con un professionista sanitario.
        """,
        "source": "Evidence-Based Complementary and Alternative Medicine, 2023"
    },

    # === MEDICAL TREATMENT ===
    {
        "id": "pcos_011",
        "category": "treatment",
        "title": "Trattamenti medici per PCOS",
        "content": """
Il trattamento della PCOS è personalizzato in base ai sintomi:
1. Contraccettivi orali (pillola):
   - Regolano il ciclo mestruale
   - Riducono androgeni (migliorano acne e irsutismo)

2. Metformina:
   - Migliora sensibilità insulinica
   - Può aiutare con perdita di peso e regolarità mestruale

3. Anti-androgeni (es. Spironolattone):
   - Riducono irsutismo e acne

4. Clomifene o Letrozolo:
   - Stimolano ovulazione per chi cerca gravidanza

5. Trattamenti cosmetici:
   - Laser o elettrolisi per irsutismo
   - Farmaci topici per acne

Il trattamento dovrebbe sempre includere modifiche dello stile di vita
(dieta ed esercizio) come base.
        """,
        "source": "European Society of Human Reproduction and Embryology, 2023"
    },

    # === FERTILITY ===
    {
        "id": "pcos_012",
        "category": "fertility",
        "title": "PCOS e fertilità",
        "content": """
La PCOS è una delle cause principali di infertilità, ma molte donne
con PCOS possono concepire con il giusto supporto:
- L'anovulazione (mancata ovulazione) è il problema principale
- Perdere il 5-10% del peso corporeo può ripristinare l'ovulazione naturalmente
- Farmaci per l'induzione dell'ovulazione: Clomifene citrato, Letrozolo
- Metformina può aiutare a migliorare la fertilità
- Iniezioni di gonadotropine per casi più complessi
- IVF (fecondazione in vitro) come opzione per casi resistenti
- Monitoraggio dell'ovulazione con test o ecografie
Consultare uno specialista della fertilità (ginecologo endocrinologo
o specialista in medicina riproduttiva) se cerchi gravidanza da oltre 12 mesi.
        """,
        "source": "Fertility and Sterility Journal, 2023"
    },

    # === LONG-TERM HEALTH ===
    {
        "id": "pcos_013",
        "category": "complications",
        "title": "Rischi a lungo termine della PCOS",
        "content": """
Le donne con PCOS hanno rischio aumentato di alcune condizioni:
- Diabete tipo 2: fino al 50% delle donne con PCOS sviluppa pre-diabete o diabete entro i 40 anni
- Malattie cardiovascolari: rischio aumentato di ipertensione e colesterolo alto
- Sindrome metabolica
- Apnea notturna
- Tumore endometriale: il rischio aumenta se non si hanno mestruazioni regolari
- Depressione e ansia
- Steatosi epatica non alcolica (NAFLD)
IMPORTANTE: Questi rischi possono essere significativamente ridotti con:
- Mantenimento di peso sano
- Dieta equilibrata
- Esercizio regolare
- Controlli medici regolari
- Gestione tempestiva dei sintomi
        """,
        "source": "Journal of Clinical Endocrinology & Metabolism, 2023"
    },

    # === MENTAL HEALTH ===
    {
        "id": "pcos_014",
        "category": "mental_health",
        "title": "PCOS e salute mentale",
        "content": """
La PCOS ha un impatto significativo sulla salute mentale:
- Le donne con PCOS hanno tassi più alti di depressione e ansia
- L'immagine corporea può essere compromessa (peso, acne, irsutismo)
- Lo stress della infertilità può essere significativo
- Le fluttuazioni ormonali influenzano l'umore
Strategie di supporto:
- Terapia psicologica (CBT è particolarmente efficace)
- Gruppi di supporto per PCOS
- Mindfulness e meditazione
- Esercizio fisico (migliora umore e riduce ansia)
- Parlare apertamente con partner, famiglia, amici
- Considerare farmaci antidepressivi se necessario (con supervisione medica)
Non esitare a chiedere aiuto professionale - la salute mentale è
importante quanto quella fisica nella gestione della PCOS.
        """,
        "source": "Journal of Behavioral Health, 2023"
    },

    # === CYCLE TRACKING ===
    {
        "id": "pcos_015",
        "category": "tracking",
        "title": "Importanza del tracking con PCOS",
        "content": """
Monitorare i sintomi e il ciclo mestruale è fondamentale con la PCOS:
Cosa tracciare:
- Ciclo mestruale: data inizio e fine, durata, intensità flusso
- Sintomi fisici: crampi, gonfiore, mal di testa, affaticamento, acne
- Umore e sintomi emotivi: ansia, depressione, irritabilità
- Peso corporeo
- Dieta e attività fisica
- Sonno
Benefici del tracking:
- Identificare pattern e trigger dei sintomi
- Valutare l'efficacia dei trattamenti
- Fornire informazioni utili al medico
- Prevedere il prossimo ciclo (se regolare)
- Monitorare ovulazione se cerchi gravidanza
- Rilevare irregolarità o cambiamenti preoccupanti
App e strumenti digitali possono rendere il tracking più facile e organizzato.
        """,
        "source": "Digital Health Technology Guidelines, 2023"
    }
]


def get_all_documents():
    """Restituisce tutti i documenti della knowledge base"""
    return PCOS_DOCUMENTS


def get_documents_by_category(category: str):
    """
    Filtra documenti per categoria

    Args:
        category: Categoria da filtrare (basics, symptoms, nutrition, etc.)

    Returns:
        Lista di documenti filtrati
    """
    return [doc for doc in PCOS_DOCUMENTS if doc["category"] == category]


def get_document_by_id(doc_id: str):
    """
    Recupera un documento specifico per ID

    Args:
        doc_id: ID del documento

    Returns:
        Documento o None se non trovato
    """
    for doc in PCOS_DOCUMENTS:
        if doc["id"] == doc_id:
            return doc
    return None


def get_categories():
    """Restituisce tutte le categorie disponibili"""
    return list(set(doc["category"] for doc in PCOS_DOCUMENTS))
