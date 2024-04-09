import os.path
from pathlib import Path

import pandas as pd

# Definizione delle domande e delle etichette
domande = [
    ("Quali sono le caratteristiche principali dell'arte egizia?", "Arte Egizia", "docente.archeologia"),
    ("Come si sono evolute le tecniche di costruzione nel periodo romano?", "Architettura Romana", "docente.archeologia"),
    ("Qual è l'importanza di Pompei per la comprensione della vita quotidiana nell'antica Roma?", "Vita Quotidiana Romana", "docente.archeologia"),
    ("In che modo l'arte greca ha influenzato quella romana?", "Influenza Greca nell'Arte Romana", "docente.archeologia"),
    ("Quali scoperte archeologiche hanno cambiato la nostra comprensione della preistoria?", "Scoperte Preistoriche", "docente.archeologia"),
    ("Come viene utilizzata la datazione al carbonio-14 in archeologia?", "Datazione al Carbonio-14", "docente.archeologia"),
    ("Quali sono le differenze tra l'arte paleocristiana e quella bizantina?", "Arte Paleocristiana vs Bizantina", "docente.archeologia"),
    ("Che ruolo ha avuto l'acquedotto nell'antica civiltà romana?", "Acquedotti Romani", "docente.archeologia"),
    ("Come interpretare le pitture rupestri del Paleolitico?", "Pitture Rupestri Paleolitiche", "docente.archeologia"),
    ("Quali sono stati gli impatti del Rinascimento sulla società europea?", "Impatti del Rinascimento", "docente.archeologia"),
    ("Cosa distingue l'architettura gotica da quella romanica?", "Architettura Gotica vs Romanica", "docente.archeologia"),
    ("In che modo gli scavi di Ercolano hanno contribuito alla nostra conoscenza dell'antichità?", "Scavi di Ercolano", "docente.archeologia"),
    ("Quali tecniche artistiche sono state utilizzate nell'antico Egitto per la realizzazione dei sarcofagi?", "Tecniche Artistiche Egizie", "docente.archeologia"),
    ("Come viene definito il periodo dell'arte barocca e quali sono le sue caratteristiche principali?", "Arte Barocca", "docente.archeologia"),
    ("Qual è il significato dei megaliti di Stonehenge?", "Stonehenge", "docente.archeologia"),
    ("Quali fattori hanno contribuito al declino dell'Impero Romano?", "Declino dell'Impero Romano", "docente.archeologia"),
    ("In che modo la ceramica fornisce informazioni sugli antichi popoli?", "Ceramica Antica", "docente.archeologia"),
    ("Come influenzava la religione l'arte nell'antico Egitto?", "Religione e Arte Egizia", "docente.archeologia"),
    ("Quali sono le principali differenze tra l'arte del Rinascimento e quella del Medioevo?", "Rinascimento vs Medioevo", "docente.archeologia"),
    ("Come venivano realizzati i mosaici bizantini e quale era il loro scopo?", "Mosaici Bizantini", "docente.archeologia"),
    ("In che modo la scoperta di Troia ha influenzato la comprensione dell'Iliade di Omero?", "Scoperta di Troia", "docente.archeologia"),
    ("Quali erano le principali funzioni dei castelli medievali?", "Castelli Medievali", "docente.archeologia"),
    ("Come si distinguono le varie fasi dell'arte greca antica?", "Fasi dell'Arte Greca", "docente.archeologia"),
    ("Quali tecniche venivano utilizzate per la fusione del bronzo nella statuaria greca?", "Fusione del Bronzo nella Statuaria Greca", "docente.archeologia"),
    ("Quali sono stati i principali centri culturali dell'arte rinascimentale?", "Centri Culturali del Rinascimento", "docente.archeologia"),
    ("In che modo l'analisi dei pigmenti aiuta a comprendere le tecniche pittoriche antiche?", "Analisi dei Pigmenti", "docente.archeologia"),
    ("Qual è stata l'importanza degli scavi di Mycenae per la comprensione della civiltà micenea?", "Scavi di Mycenae", "docente.archeologia"),
    ("Come si differenziano le tombe etrusche da quelle romane?", "Tombe Etrusche vs Romane", "docente.archeologia"),
    ("In che modo l'arte romana rifletteva la società e i valori dell'epoca?", "Arte Romana e Società", "docente.archeologia"),
    ("Quali sono le principali caratteristiche dell'architettura mesopotamica?", "Architettura Mesopotamica", "docente.archeologia"),
    ("Come veniva rappresentata la figura umana nell'arte cicladica?", "Arte Cicladica", "docente.archeologia"),
    ("Quali sono le principali fonti per lo studio della storia dell'arte dell'antica Grecia?", "Fonti Storiche dell'Arte Greca", "docente.archeologia"),
    ("Quali erano le funzioni sociali e religiose dell'arte nella società Maya?", "Arte Maya", "docente.archeologia"),
    ("In che modo le armi e gli strumenti vengono utilizzati per datare i siti archeologici?", "Datazione dei Siti Archeologici", "docente.archeologia"),
    ("Qual è il significato simbolico dei colori nell'arte egizia?", "Simbolismo dei Colori nell'Arte Egizia", "docente.archeologia"),
    ("Come l'uso dei materiali influenzava lo stile artistico nell'antichità?", "Materiali e Stile Artistico Antico", "docente.archeologia"),
    ("Quali sono le principali differenze tra l'architettura classica e quella neoclassica?", "Classica vs Neoclassica", "docente.archeologia"),
    ("Come venivano selezionati e utilizzati i siti per la costruzione dei templi greci?", "Costruzione dei Templi Greci", "docente.archeologia"),
    ("Qual è stato l'impatto dell'invenzione della stampa sull'arte e sulla cultura?", "Invenzione della Stampa", "docente.archeologia"),
    ("Come venivano realizzate e utilizzate le monete nell'antica Roma?", "Monete nell'Antica Roma", "docente.archeologia"),
    ("Qual è l'importanza dei ritrovamenti di Akrotiri per la comprensione della civiltà minoica?", "Ritrovamenti di Akrotiri", "docente.archeologia"),
    ("In che modo l'arte e l'architettura riflettono il potere e la religione nell'Impero Bizantino?", "Arte e Architettura Bizantina", "docente.archeologia"),
    ("Come l'analisi del DNA sta cambiando la nostra comprensione delle migrazioni antiche?", "Analisi del DNA e Migrazioni Antiche", "docente.archeologia"),
    ("Quali tecniche di conservazione sono utilizzate per preservare le opere d'arte antiche?", "Tecniche di Conservazione", "docente.archeologia"),
    ("In che modo l'arte dell'antico Egitto è stata influenzata dalla sua geografia?", "Influenza della Geografia sull'Arte Egizia", "docente.archeologia"),
    ("Quali erano le principali tecniche di scultura utilizzate nella Grecia antica?", "Tecniche di Scultura nella Grecia Antica", "docente.archeologia"),
    ("Come si sono sviluppate le città-stato nella Grecia antica e quale era il loro ruolo nella società?", "Città-Stato nella Grecia Antica", "docente.archeologia"),
    ("Quali fattori hanno influenzato lo sviluppo dell'architettura gotica?", "Sviluppo dell'Architettura Gotica", "docente.archeologia"),
    ("In che modo gli affreschi di Pompei ci forniscono informazioni sulla vita e l'arte dell'epoca?", "Affreschi di Pompei", "docente.archeologia"),
    ("Quali sono le principali caratteristiche delle sculture dell'arte romanica?", "Sculture dell'Arte Romanica", "docente.archeologia"),
    ("Come l'arte ha influenzato la politica nell'antica Grecia?", "Arte e Politica nell'Antica Grecia", "docente.archeologia"),
    ("Quali sono le tecniche di navigazione e mappatura utilizzate dalle antiche civiltà marinare?", "Navigazione e Mappatura Antiche", "docente.archeologia"),
    ("Come l'arte rupestre può essere interpretata per comprendere le culture preistoriche?", "Interpretazione dell'Arte Rupestre", "docente.archeologia"),
    ("Quali sono state le influenze culturali sull'arte della Mesopotamia?", "Influenze Culturali sull'Arte Mesopotamica", "docente.archeologia"),
    ("In che modo le tecniche di restauro moderne possono influenzare la percezione delle opere d'arte antiche?", "Tecniche di Restauro Moderne", "docente.archeologia"),
    ("Qual è stata l'importanza della Via della Seta per lo scambio culturale e artistico?", "Importanza della Via della Seta")
]

domande += [
    ("Quale innovazione nell'architettura romana ha permesso la costruzione di grandi spazi interni coperti?", "Architettura Romana", "docente.archeologia"),
    ("Qual è una differenza principale tra l'arte classica greco-romana e quella neoclassica?", "Classica vs Neoclassica", "docente.archeologia"),
    ("Quale metodo di datazione è comunemente utilizzato per determinare l'età di siti archeologici antichi?", "Datazione dei Siti Archeologici", "docente.archeologia"),
    ("Qual è stata una delle cause principali del declino dell'Impero Romano d'Occidente?", "Declino dell'Impero Romano", "docente.archeologia"),
    ("Qual era la tecnica predominante utilizzata dai Greci antichi per la fusione delle statue in bronzo?", "Fusione del Bronzo nella Statuaria Greca", "docente.archeologia"),
    ("Qual era la principale funzione delle monete nell'antica Roma?", "Monete nell'Antica Roma", "docente.archeologia"),
    ("Chi è accreditato per la scoperta del sito archeologico di Troia?", "Scoperta di Troia", "docente.archeologia")
]

risposte = [
    (
        "Quali sono le caratteristiche principali dell'arte egizia?",
        "docente.archeologia",
        "L'arte egizia è nota per le sue grandi costruzioni come piramidi e templi, l'uso di geroglifici e rappresentazioni stilizzate di figure umane e divinità, spesso con proporzioni canoniche e postura frontale.",
        4,
    ),
    (
        "Quali sono le caratteristiche principali dell'arte egizia?",
        "docente.archeologia",
        "L'arte egizia è principalmente famosa per i suoi dipinti astratti e l'uso prevalente del ferro nelle sculture.",
        1,
    ),
    (
        "Come si sono evolute le tecniche di costruzione nel periodo romano?",
        "docente.archeologia",
        "Le tecniche di costruzione romane hanno visto significativi progressi con l'introduzione del calcestruzzo, permettendo la creazione di strutture innovative come le cupole e gli acquedotti, che hanno migliorato l'architettura e l'ingegneria civile.",
        4,
    ),
    (
        "Come si sono evolute le tecniche di costruzione nel periodo romano?",
        "docente.archeologia",
        "Le tecniche di costruzione romane sono rimaste invariate dal periodo greco, focalizzandosi esclusivamente su elementi decorativi piuttosto che su innovazioni strutturali.",
        1,
    ),
    (
        "Qual è l'importanza di Pompei per la comprensione della vita quotidiana nell'antica Roma?",
        "docente.archeologia",
        "Pompei offre uno sguardo senza precedenti sulla vita quotidiana degli antichi Romani, grazie alla conservazione di edifici, affreschi e artefatti quotidiani, offrendo preziose informazioni sulle abitudini, la cultura e la società dell'epoca.",
        3,
    ),
    (
        "Qual è l'importanza di Pompei per la comprensione della vita quotidiana nell'antica Roma?",
        "docente.archeologia",
        "Pompei è rilevante principalmente per le sue rovine architettoniche che dimostrano l'uso avanzato del marmo, ignorando il contesto storico e sociale degli abitanti.",
        1,
    ),
    (
        "In che modo l'arte greca ha influenzato quella romana?",
        "docente.archeologia",
        "L'arte greca ha fortemente influenzato quella romana attraverso l'adozione di stili, tecniche e temi, come la rappresentazione del corpo umano e la mitologia, che i Romani hanno integrato e adattato alle loro esigenze culturali e politiche.",
        4,
    ),
    (
        "In che modo l'arte greca ha influenzato quella romana?",
        "docente.archeologia",
        "L'arte romana ha rigettato completamente l'influenza greca, sviluppando uno stile completamente indipendente focalizzato esclusivamente su temi astratti e geometrici.",
        0,
    ),
    (
        "Quali scoperte archeologiche hanno cambiato la nostra comprensione della preistoria?",
        "docente.archeologia",
        "La scoperta di siti come Lascaux in Francia e Altamira in Spagna, con le loro pitture rupestri, ha rivoluzionato la nostra comprensione dell'espressione artistica e culturale delle società preistoriche.",
        4,
    ),
    (
        "Quali scoperte archeologiche hanno cambiato la nostra comprensione della preistoria?",
        "docente.archeologia",
        "La scoperta delle piramidi egizie ha cambiato la nostra comprensione della preistoria, dimostrando che le società antiche erano esclusivamente focalizzate sulla costruzione di monumenti funerari.",
        0,
    ),
    (
        "Come viene utilizzata la datazione al carbonio-14 in archeologia?",
        "docente.archeologia",
        "La datazione al carbonio-14 è utilizzata per determinare l'età di materiali organici fino a circa 50.000 anni fa, fornendo una cronologia accurata per il sito o l'oggetto studiato.",
        4,
    ),
    (
        "Come viene utilizzata la datazione al carbonio-14 in archeologia?",
        "docente.archeologia",
        "La datazione al carbonio-14 viene utilizzata per determinare l'origine geografica degli oggetti antichi, identificando i luoghi esatti da cui provengono.",
        1,
    ),
    (
        "Quali sono le differenze tra l'arte paleocristiana e quella bizantina?",
        "docente.archeologia",
        "L'arte paleocristiana si concentra su simboli semplici e narrazioni bibliche in catacombe e altri luoghi di culto, mentre l'arte bizantina sviluppa uno stile più raffinato con l'uso di mosaici dorati, icone e una maggiore enfasi sulla spiritualità.",
        5,
    ),
    (
        "Quali sono le differenze tra l'arte paleocristiana e quella bizantina?",
        "docente.archeologia",
        "Non esistono differenze significative tra l'arte paleocristiana e quella bizantina; entrambe condividono gli stessi temi e tecniche senza variazioni nel tempo.",
        0,
    ),
    (
        "Che ruolo ha avuto l'acquedotto nell'antica civiltà romana?",
        "docente.archeologia",
        "Gli acquedotti hanno permesso il trasporto di acqua pulita nelle città, migliorando notevolmente la salute pubblica e sostenendo la crescita urbana.",
        5,
    ),
    (
        "Che ruolo ha avuto l'acquedotto nell'antica civiltà romana?",
        "docente.archeologia",
        "Gli acquedotti erano puramente decorativi, utilizzati come simboli di status senza una funzione pratica.",
        0,
    ),
    (
        "Come interpretare le pitture rupestri del Paleolitico?",
        "docente.archeologia",
        "Le pitture rupestri del Paleolitico sono interpretate come espressioni culturali che rappresentano la vita quotidiana, le credenze religiose e le conoscenze astronomiche delle società preistoriche.",
        4,
    ),
    (
        "Come interpretare le pitture rupestri del Paleolitico?",
        "docente.archeologia",
        "Le pitture rupestri del Paleolitico sono semplici decorazioni senza significato, realizzate per passare il tempo.",
        0,
    ),
    (
        "Quali sono stati gli impatti del Rinascimento sulla società europea?",
        "docente.archeologia",
        "Il Rinascimento ha promosso il rinascere dell'interesse per le arti, la scienza e l'umanesimo, influenzando profondamente la cultura, la politica e la religione in Europa.",
        3,
    ),
    (
        "Quali sono stati gli impatti del Rinascimento sulla società europea?",
        "docente.archeologia",
        "Il Rinascimento ha avuto poco impatto sulla società europea, rimanendo un fenomeno isolato senza influenze culturali o scientifiche.",
        0,
    ),
    (
        "Cosa distingue l'architettura gotica da quella romanica?",
        "docente.archeologia",
        "L'architettura gotica si distingue per l'uso di arcate a sesto acuto, volta a crociera e supporti snelli come i contrafforti volanti, rispetto alla massiccia semplicità e alle cupole semicircolari del romanico.",
        5,
    ),
    (
        "Cosa distingue l'architettura gotica da quella romanica?",
        "docente.archeologia",
        "L'architettura gotica e quella romanica non presentano differenze significative, condividendo gli stessi elementi stilistici e strutturali.",
        1,
    ),
    (
        "In che modo gli scavi di Ercolano hanno contribuito alla nostra conoscenza dell'antichità?",
        "docente.archeologia",
        "Gli scavi di Ercolano hanno fornito preziose informazioni sulla vita quotidiana romana, preservando edifici e oggetti coperti dalla cenere vulcanica, simili a Pompei ma meglio conservati.",
        4,
    ),
    (
        "In che modo gli scavi di Ercolano hanno contribuito alla nostra conoscenza dell'antichità?",
        "docente.archeologia",
        "Gli scavi di Ercolano non hanno offerto nuove informazioni sull'antichità, essendo una replica moderna di una città antica.",
        0,
    ),
    (
        "Quali tecniche artistiche sono state utilizzate nell'antico Egitto per la realizzazione dei sarcofagi?",
        "docente.archeologia",
        "Nell'antico Egitto, i sarcofagi erano realizzati con legno o pietra e decorati con pitture e incisioni che rappresentavano testi funerari e scene della vita dopo la morte, utilizzando tecniche avanzate di lavorazione.",
        5,
    ),
    (
        "Quali tecniche artistiche sono state utilizzate nell'antico Egitto per la realizzazione dei sarcofagi?",
        "docente.archeologia",
        "I sarcofagi egizi erano semplicemente scavati nel terreno senza alcuna decorazione o tecnica artistica, riflettendo pratiche di sepoltura primitive.",
        0,
    ),
    (
        "Come viene definito il periodo dell'arte barocca e quali sono le sue caratteristiche principali?",
        "docente.archeologia",
        "Il periodo barocco è definito dal dinamismo, dall'esuberanza e dalla ricchezza decorativa, caratterizzato dall'uso di contrasti forti, movimento, espressioni drammatiche e una tendenza verso la grandiosità in tutte le forme d'arte.",
        5,
    ),
    (
        "Come viene definito il periodo dell'arte barocca e quali sono le sue caratteristiche principali?",
        "docente.archeologia",
        "Il barocco si concentra principalmente sull'astrazione e la semplicità delle forme, preferendo linee pulite e un approccio minimalista all'arte.",
        0,
    ),
    (
        "Qual è il significato dei megaliti di Stonehenge?",
        "docente.archeologia",
        "Stonehenge è generalmente interpretato come un complesso preistorico usato per osservazioni astronomiche, cerimonie religiose o pratiche sociali rituali.",
        3,
    ),
    (
        "Qual è il significato dei megaliti di Stonehenge?",
        "docente.archeologia",
        "Stonehenge era un antico mercato per il commercio locale, dove le persone si incontravano per scambiare beni e servizi.",
        0,
    ),
    (
        "Quali fattori hanno contribuito al declino dell'Impero Romano?",
        "docente.archeologia",
        "Il declino dell'Impero Romano è stato causato da una combinazione di fattori interni come la corruzione, l'instabilità politica, l'eccessiva espansione e pressioni esterne da parte dei popoli barbarici.",
        4,
    ),
    (
        "Quali fattori hanno contribuito al declino dell'Impero Romano?",
        "docente.archeologia",
        "Il declino è stato principalmente il risultato dell'invasione degli alieni, che hanno soverchiato le legioni romane con tecnologia superiore.",
        0,
    ),
    (
        "In che modo la ceramica fornisce informazioni sugli antichi popoli?",
        "docente.archeologia",
        "La ceramica, con i suoi stili decorativi e le tecniche di produzione, offre preziose informazioni sulla vita quotidiana, le pratiche commerciali e le interazioni culturali degli antichi popoli.",
        4,
    ),
    (
        "In che modo la ceramica fornisce informazioni sugli antichi popoli?",
        "docente.archeologia",
        "La ceramica antica è utile esclusivamente per determinare i livelli di consumo di tè e caffè nelle antiche civiltà.",
        0,
    ),
    (
        "Come influenzava la religione l'arte nell'antico Egitto?",
        "docente.archeologia",
        "Nell'antico Egitto, la religione aveva un profondo impatto sull'arte, che era prevalentemente usata per scopi funerari o di culto, rappresentando divinità, riti religiosi e credenze nell'aldilà.",
        4,
    ),
    (
        "Come influenzava la religione l'arte nell'antico Egitto?",
        "docente.archeologia",
        "L'arte egizia era completamente laica e non era influenzata in alcun modo dalle pratiche religiose o spirituali dell'epoca.",
        0,
    ),
    (
        "Quali sono le principali differenze tra l'arte del Rinascimento e quella del Medioevo?",
        "docente.archeologia",
        "L'arte del Rinascimento segna un ritorno all'antichità classica, con un focus su prospettiva, anatomia umana e naturalismo, a differenza dell'arte medievale che era più orientata verso il simbolismo religioso e uno stile più stilizzato e astratto.",
        4,
    ),
    (
        "Quali sono le principali differenze tra l'arte del Rinascimento e quella del Medioevo?",
        "docente.archeologia",
        "Non ci sono differenze significative; l'arte del Rinascimento e quella medievale possono essere considerate strettamente intercambiabili in termini di stile e soggetto.",
        0,
    ),
    (
        "Come venivano realizzati i mosaici bizantini e quale era il loro scopo?",
        "docente.archeologia",
        "I mosaici bizantini erano realizzati con piccoli pezzi di vetro o pietra, detti tessere, per creare immagini elaborate con scopi decorativi e religiosi, spesso utilizzati nelle chiese per raccontare storie bibliche.",
        4,
    ),
    (
        "Come venivano realizzati i mosaici bizantini e quale era il loro scopo?",
        "docente.archeologia",
        "I mosaici bizantini erano principalmente disegni astratti usati per pavimentare le strade e non avevano significato o scopo oltre a quello pratico.",
        0,
    ),
    (
        "In che modo la scoperta di Troia ha influenzato la comprensione dell'Iliade di Omero?",
        "docente.archeologia",
        "La scoperta archeologica di Troia ha fornito una base storica all'Iliade di Omero, suggerendo che gli eventi descritti, sebbene mitologizzati, potrebbero avere un fondamento nella realtà.",
        4,
    ),
    (
        "In che modo la scoperta di Troia ha influenzato la comprensione dell'Iliade di Omero?",
        "docente.archeologia",
        "La scoperta di Troia ha dimostrato inequivocabilmente che l'Iliade era un resoconto accurato e dettagliato di eventi storici senza alcuna esagerazione o elemento mitologico.",
        1,
    ),
    (
        "Quali erano le principali funzioni dei castelli medievali?",
        "docente.archeologia",
        "I castelli medievali servivano come centri di amministrazione locale, residenze nobiliari e soprattutto come strutture difensive durante i periodi di conflitto.",
        3,
    ),
    (
        "Quali erano le principali funzioni dei castelli medievali?",
        "docente.archeologia",
        "I castelli medievali erano utilizzati esclusivamente come attrazioni turistiche per intrattenere la nobiltà, senza alcuna funzione pratica o militare.",
        0,
    ),
    (
        "Come si distinguono le varie fasi dell'arte greca antica?",
        "docente.archeologia",
        "Le fasi dell'arte greca antica si distinguono in arcaica, classica ed ellenistica, ognuna caratterizzata da specifici stili artistici, tecniche scultoree e temi rappresentativi.",
        4,
    ),
    (
        "Come si distinguono le varie fasi dell'arte greca antica?",
        "docente.archeologia",
        "L'arte greca antica è stata uniforme nel corso dei secoli, senza distinzioni o sviluppi significativi tra le varie fasi.",
        0,
    ),
    (
        "Quali tecniche venivano utilizzate per la fusione del bronzo nella statuaria greca?",
        "docente.archeologia",
        "La statuaria greca utilizzava la tecnica della fusione a cera persa per creare sculture in bronzo dettagliate e realistiche, permettendo grande precisione nei dettagli.",
        5,
    ),
    (
        "Quali tecniche venivano utilizzate per la fusione del bronzo nella statuaria greca?",
        "docente.archeologia",
        "Le sculture in bronzo greche erano create assemblando pezzi prefabbricati senza uso di tecniche di fusione, risultando in opere spesso grezze e poco dettagliate.",
        1,
    ),
    (
        "Quali sono stati i principali centri culturali dell'arte rinascimentale?",
        "docente.archeologia",
        "Firenze, Roma, e Venezia sono stati tra i principali centri culturali dell'arte rinascimentale, fungendo da fucine per l'innovazione artistica e la rinascita degli ideali classici.",
        5,
    ),
    (
        "Quali sono stati i principali centri culturali dell'arte rinascimentale?",
        "docente.archeologia",
        "I principali centri culturali dell'arte rinascimentale erano situati nell'Europa settentrionale, con Londra e Parigi che guidavano il movimento artistico.",
        1,
    ),
    (
        "In che modo l'analisi dei pigmenti aiuta a comprendere le tecniche pittoriche antiche?",
        "docente.archeologia",
        "L'analisi dei pigmenti permette di identificare i materiali utilizzati dagli artisti, fornendo informazioni sulle tecniche pittoriche, le pratiche di atelier e le rotte commerciali degli antichi.",
        4,
    ),
    (
        "In che modo l'analisi dei pigmenti aiuta a comprendere le tecniche pittoriche antiche?",
        "docente.archeologia",
        "L'analisi dei pigmenti è utile esclusivamente per determinare l'età di un'opera d'arte, senza fornire alcuna informazione sulle tecniche pittoriche utilizzate.",
        0,
    ),
    (
        "Qual è stata l'importanza degli scavi di Mycenae per la comprensione della civiltà micenea?",
        "docente.archeologia",
        "Gli scavi di Mycenae hanno rivelato ricchezze architettoniche e artefatti che illustrano la potenza e la complessità della civiltà micenea, confermando le descrizioni di Omero.",
        3,
    ),
    (
        "Qual è stata l'importanza degli scavi di Mycenae per la comprensione della civiltà micenea?",
        "docente.archeologia",
        "Gli scavi di Mycenae hanno dimostrato che la civiltà micenea era principalmente nomade, con scarse prove di insediamenti permanenti o strutture complesse.",
        0,
    ),
    (
        "Come si differenziano le tombe etrusche da quelle romane?",
        "docente.archeologia",
        "Le tombe etrusche erano spesso elaborate camere sotterranee con affreschi vivaci, mentre le tombe romane tendevano a essere più austere e meno decorate, riflettendo diverse pratiche e credenze funerarie.",
        4,
    ),
    (
        "Come si differenziano le tombe etrusche da quelle romane?",
        "docente.archeologia",
        "Le tombe etrusche e romane non differivano significativamente, poiché entrambe le culture preferivano la cremazione alla sepoltura.",
        0,
    ),
    (
        "In che modo l'arte romana rifletteva la società e i valori dell'epoca?",
        "docente.archeologia",
        "L'arte romana rifletteva la società e i valori dell'epoca attraverso la rappresentazione di temi legati al potere, all'autorità, agli dei e alla vita quotidiana, servendo come mezzo per la propaganda politica e l'espressione religiosa.",
        5,
    ),
    (
        "In che modo l'arte romana rifletteva la società e i valori dell'epoca?",
        "docente.archeologia",
        "L'arte romana era completamente astratta, evitando qualsiasi rappresentazione della società o dei valori dell'epoca, concentrata invece su forme geometriche pure.",
        0,
    ),
    (
        "Quali sono le principali caratteristiche dell'architettura mesopotamica?",
        "docente.archeologia",
        "Le principali caratteristiche dell'architettura mesopotamica includono l'uso di mattoni d'argilla, la costruzione di ziggurat come centri religiosi e la creazione di città-stato fortificate.",
        4,
    ),
    (
        "Quali sono le principali caratteristiche dell'architettura mesopotamica?",
        "docente.archeologia",
        "L'architettura mesopotamica è nota per l'uso estensivo del marmo e per le sue strutture mobili, che potevano essere facilmente spostate.",
        0,
    ),
    (
        "Come veniva rappresentata la figura umana nell'arte cicladica?",
        "docente.archeologia",
        "Nell'arte cicladica, la figura umana era rappresentata in forma stilizzata e schematica, con enfasi sulla simmetria e le proporzioni geometriche, spesso con braccia incrociate e volti privi di espressione.",
        4,
    ),
    (
        "Come veniva rappresentata la figura umana nell'arte cicladica?",
        "docente.archeologia",
        "La figura umana nell'arte cicladica era estremamente realistica e dettagliata, con un'enfasi sul realismo anatomico simile a quello dell'arte rinascimentale.",
        0,
    ),
    (
        "Quali sono le principali fonti per lo studio della storia dell'arte dell'antica Grecia?",
        "docente.archeologia",
        "Le principali fonti per lo studio dell'arte greca antica includono opere d'arte sopravvissute come sculture, vasi, edifici e affreschi, nonché testi antichi di autori come Pausania e Plinio il Vecchio.",
        4,
    ),
    (
        "Quali sono le principali fonti per lo studio della storia dell'arte dell'antica Grecia?",
        "docente.archeologia",
        "Le uniche fonti per lo studio dell'arte greca antica sono le rappresentazioni moderne e le ricostruzioni basate su interpretazioni artistiche contemporanee.",
        0,
    ),
    (
        "Quali erano le funzioni sociali e religiose dell'arte nella società Maya?",
        "docente.archeologia",
        "Nella società Maya, l'arte svolgeva molteplici funzioni sociali e religiose. Socialmente, l'arte era utilizzata per rappresentare lo status e il potere delle élite, attraverso monumentali strutture architettoniche e sculture che celebravano governanti e divinità. Religiosamente, l'arte era fondamentale per esprimere le credenze e i rituali della religione Maya, con raffigurazioni di divinità, cerimonie sacre e mitologia incise su monumenti, dipinti murali e ceramiche. Queste opere d'arte servivano anche come mezzo di comunicazione con gli dei e come strumento per garantire la continuità del mondo naturale e cosmico secondo il loro sistema di credenze.",
        5,
    ),
    (
        "Quali erano le funzioni sociali e religiose dell'arte nella società Maya?",
        "docente.archeologia",
        "Nella società Maya, l'arte era puramente decorativa, senza alcuna funzione sociale o religiosa, e veniva usata solo per abbellire gli ambienti abitativi.",
        0,
    ),
    (
        "In che modo le armi e gli strumenti vengono utilizzati per datare i siti archeologici?",
        "docente.archeologia",
        "Le armi e gli strumenti sono utilizzati per datare i siti archeologici attraverso la tipologia e la tecnologia di produzione, che possono indicare specifici periodi storici e culturali.",
        3,
    ),
    (
        "In che modo le armi e gli strumenti vengono utilizzati per datare i siti archeologici?",
        "docente.archeologia",
        "Le armi e gli strumenti antichi sono irrilevanti per la datazione dei siti archeologici, poiché non variano significativamente nel tempo.",
        0,
    ),
    (
        "Qual è il significato simbolico dei colori nell'arte egizia?",
        "docente.archeologia",
        "Nell'arte egizia, i colori avevano significati simbolici profondi, come il verde per la rinascita, il rosso per il caos o la distruzione, e il nero per la fertilità e la rigenerazione.",
        4,
    ),
    (
        "Qual è il significato simbolico dei colori nell'arte egizia?",
        "docente.archeologia",
        "I colori nell'arte egizia erano scelti casualmente, senza alcun significato simbolico o culturale.",
        0,
    ),
    (
        "Come l'uso dei materiali influenzava lo stile artistico nell'antichità?",
        "docente.archeologia",
        "L'uso di materiali come il marmo, il bronzo o l'argilla influenzava notevolmente lo stile artistico, determinando la tecnica, la forma e la durabilità dell'opera artistica.",
        4,
    ),
    (
        "Come l'uso dei materiali influenzava lo stile artistico nell'antichità?",
        "docente.archeologia",
        "L'uso dei materiali aveva un impatto minimo sullo stile artistico nell'antichità, con gli artisti che privilegiavano l'espressione personale rispetto alle proprietà dei materiali.",
        0,
    ),
    (
        "Quali sono le principali differenze tra l'architettura classica e quella neoclassica?",
        "docente.archeologia",
        "L'architettura classica si riferisce all'arte dell'antica Grecia e Roma, con l'uso di colonne doriche, ioniche e corinzie, mentre il neoclassicismo è una rivisitazione di questi stili nell'epoca moderna, enfatizzando la semplicità e la grandiosità.",
        4,
    ),
    (
        "Quali sono le principali differenze tra l'architettura classica e quella neoclassica?",
        "docente.archeologia",
        "Non ci sono differenze tra l'architettura classica e quella neoclassica; il termine 'neoclassico' è semplicemente un altro modo per descrivere l'architettura greca e romana.",
        0,
    ),
    (
        "Come venivano selezionati e utilizzati i siti per la costruzione dei templi greci?",
        "docente.archeologia",
        "I siti per i templi greci erano spesso scelti per il loro significato religioso o per la loro posizione prominente, come le alture, per dominare il paesaggio circostante.",
        4,
    ),
    (
        "Come venivano selezionati e utilizzati i siti per la costruzione dei templi greci?",
        "docente.archeologia",
        "I siti per i templi greci erano selezionati casualmente, senza particolare considerazione per la posizione o il significato.",
        0,
    ),
    (
        "Qual è stato l'impatto dell'invenzione della stampa sull'arte e sulla cultura?",
        "docente.archeologia",
        "L'invenzione della stampa ha rivoluzionato l'arte e la cultura facilitando la diffusione delle conoscenze, rendendo i libri più accessibili e promuovendo l'alfabetizzazione e la diffusione delle idee rinascimentali.",
        4,
    ),
    (
        "Qual è stato l'impatto dell'invenzione della stampa sull'arte e sulla cultura?",
        "docente.archeologia",
        "L'invenzione della stampa ha avuto poco impatto sull'arte e sulla cultura, rimanendo una curiosità tecnologica con scarse applicazioni pratiche.",
        0,
    ),
    (
        "Come venivano realizzate e utilizzate le monete nell'antica Roma?",
        "docente.archeologia",
        "Nell'antica Roma, le monete erano coniate in metallo prezioso e servivano come mezzo di scambio, standard di valore e strumento di propaganda politica, mostrando ritratti di imperatori o divinità.",
        4,
    ),
    (
        "Come venivano realizzate e utilizzate le monete nell'antica Roma?",
        "docente.archeologia",
        "Le monete nell'antica Roma erano principalmente di carta e usate solo per giochi e divertimenti, senza valore reale come moneta.",
        0,
    ),
    (
        "Qual è l'importanza dei ritrovamenti di Akrotiri per la comprensione della civiltà minoica?",
        "docente.archeologia",
        "I ritrovamenti di Akrotiri, con i suoi affreschi ben conservati e avanzate strutture urbane, offrono una visione unica sulla vita quotidiana, l'arte e l'architettura della civiltà minoica.",
        3,
    ),
    (
        "Qual è l'importanza dei ritrovamenti di Akrotiri per la comprensione della civiltà minoica?",
        "docente.archeologia",
        "Akrotiri è irrilevante per la comprensione della civiltà minoica, essendo un sito isolato che non riflette la cultura o le pratiche di quel popolo.",
        0,
    ),
    (
        "In che modo l'arte e l'architettura riflettono il potere e la religione nell'Impero Bizantino?",
        "docente.archeologia",
        "Nell'Impero Bizantino, l'arte e l'architettura riflettevano il potere e la religione attraverso la costruzione di imponenti chiese e mosaici che esprimevano la divinità dell'imperatore e la centralità del cristianesimo.",
        4,
    ),
    (
        "In che modo l'arte e l'architettura riflettono il potere e la religione nell'Impero Bizantino?",
        "docente.archeologia",
        "L'arte e l'architettura bizantine erano completamente secolari, evitando qualsiasi riferimento al potere imperiale o alla religione.",
        0,
    ),
    (
        "Come l'analisi del DNA sta cambiando la nostra comprensione delle migrazioni antiche?",
        "docente.archeologia",
        "L'analisi del DNA sta rivoluzionando la nostra comprensione delle migrazioni antiche, fornendo prove dirette dei movimenti dei popoli preistorici e delle loro interazioni genetiche con le popolazioni moderne.",
        4,
    ),
    (
        "Come l'analisi del DNA sta cambiando la nostra comprensione delle migrazioni antiche?",
        "docente.archeologia",
        "L'analisi del DNA non ha contribuito significativamente alla nostra comprensione delle migrazioni antiche, rimanendo una tecnologia troppo imprecisa per fornire informazioni affidabili.",
        0,
    ),
    (
        "Quali tecniche di conservazione sono utilizzate per preservare le opere d'arte antiche?",
        "docente.archeologia",
        "Per preservare le opere d'arte antiche, vengono utilizzate tecniche come la stabilizzazione ambientale, il restauro delicato e la digitalizzazione per prevenire ulteriori danni e perdite.",
        4,
    ),
    (
        "Quali tecniche di conservazione sono utilizzate per preservare le opere d'arte antiche?",
        "docente.archeologia",
        "Le opere d'arte antiche sono spesso ricoperte di vernice trasparente per preservarle, una tecnica moderna che garantisce la loro durata nel tempo senza necessità di altri interventi.",
        0,
    ),
    (
        "In che modo l'arte dell'antico Egitto è stata influenzata dalla sua geografia?",
        "docente.archeologia",
        "L'arte dell'antico Egitto è stata profondamente influenzata dalla geografia, in particolare dal Nilo, che ha portato a una forte enfasi sui temi della fertilità, della rinascita e dell'aldilà, riflettendo l'importanza del fiume per la sopravvivenza e la prosperità.",
        4,
    ),
    (
        "In che modo l'arte dell'antico Egitto è stata influenzata dalla sua geografia?",
        "docente.archeologia",
        "La geografia dell'Egitto, essendo principalmente desertica, ha impedito lo sviluppo dell'arte e della cultura, limitando le espressioni artistiche a semplici disegni rupestri.",
        0,
    ),
    (
        "Quali erano le principali tecniche di scultura utilizzate nella Grecia antica?",
        "docente.archeologia",
        "Nella Grecia antica, le principali tecniche di scultura includono il marmo, il bronzo e il terracotta. La scultura in marmo era spesso realizzata tramite l'uso di scalpelli e martelli per creare opere di grande dettaglio e precisione, come nel caso dei marmi del Partenone. Il bronzo consentiva una maggiore libertà di movimento e permetteva di creare opere più dinamiche e tridimensionali, attraverso la tecnica della fusione e della cesellatura. La terracotta, invece, permetteva la creazione di opere più piccole e dettagliate, spesso utilizzate per sculture decorative e vasi.",
        5,
    ),
    (
        "Quali erano le principali tecniche di scultura utilizzate nella Grecia antica?",
        "docente.archeologia",
        "Le sculture greche antiche erano principalmente fatte di legno e argilla, senza l'uso di tecniche avanzate, risultando in opere d'arte grossolane e poco dettagliate.",
        0,
    ),
    (
        "Come si sono sviluppate le città-stato nella Grecia antica e quale era il loro ruolo nella società?",
        "docente.archeologia",
        "Le città-stato della Grecia antica, o polis, erano centri indipendenti di attività politica, economica e culturale, che giocavano un ruolo cruciale nel promuovere lo sviluppo della democrazia, dell'arte e della filosofia.",
        4,
    ),
    (
        "Come si sono sviluppate le città-stato nella Grecia antica e quale era il loro ruolo nella società?",
        "docente.archeologia",
        "Le città-stato nella Grecia antica erano meramente simboliche e non avevano alcuna influenza reale sulla società o sullo sviluppo culturale dell'epoca.",
        0,
    ),
    (
        "Quali fattori hanno influenzato lo sviluppo dell'architettura gotica?",
        "docente.archeologia",
        "Lo sviluppo dell'architettura gotica è stato influenzato da un desiderio di maggiore altezza e luce nelle strutture, portando all'introduzione di innovazioni come gli archi a sesto acuto, le volte a crociera e i contrafforti volanti.",
        4,
    ),
    (
        "Quali fattori hanno influenzato lo sviluppo dell'architettura gotica?",
        "docente.archeologia",
        "L'architettura gotica è stata influenzata principalmente dall'esigenza di costruire strutture che potessero resistere a condizioni meteorologiche estreme, come neve e ghiaccio.",
        0,
    ),
    (
        "In che modo gli affreschi di Pompei ci forniscono informazioni sulla vita e l'arte dell'epoca?",
        "docente.archeologia",
        "Gli affreschi di Pompei forniscono una visione preziosa della vita quotidiana, delle mode, dei costumi e delle credenze degli antichi Romani, grazie alla loro straordinaria conservazione dopo l'eruzione del Vesuvio.",
        4,
    ),
    (
        "In che modo gli affreschi di Pompei ci forniscono informazioni sulla vita e l'arte dell'epoca?",
        "docente.archeologia",
        "Gli affreschi di Pompei sono considerati irrilevanti per la comprensione della vita e dell'arte dell'epoca, in quanto si ritiene che rappresentino esclusivamente immaginazione artistica senza basi nella realtà.",
        0,
    ),
    (
        "Quali sono le principali caratteristiche delle sculture dell'arte romanica?",
        "docente.archeologia",
        "Le sculture dell'arte romanica sono caratterizzate da un forte simbolismo religioso, forme stilizzate e un'espressione emotiva contenuta, spesso utilizzate come decorazione in chiese e cattedrali.",
        4,
    ),
    (
        "Quali sono le principali caratteristiche delle sculture dell'arte romanica?",
        "docente.archeologia",
        "Le sculture dell'arte romanica erano note per la loro estrema fedeltà al realismo naturale e per la rappresentazione dettagliata di scene quotidiane, ignorando temi religiosi o simbolici.",
        0,
    ),
    (
        "Come l'arte ha influenzato la politica nell'antica Grecia?",
        "docente.archeologia",
        "Nell'antica Grecia, l'arte era strettamente intrecciata con la politica, utilizzata per esaltare le virtù dei leader, celebrare le vittorie militari e esprimere ideali democratici, influenzando l'opinione pubblica e l'identità culturale.",
        4,
    ),
    (
        "Come l'arte ha influenzato la politica nell'antica Grecia?",
        "docente.archeologia",
        "L'arte nell'antica Grecia aveva poco o nessun impatto sulla politica, rimanendo una sfera completamente separata senza influenzare le decisioni politiche o la società.",
        0,
    ),
    (
        "Quali sono le tecniche di navigazione e mappatura utilizzate dalle antiche civiltà marinare?",
        "docente.archeologia",
        "Le antiche civiltà marinare utilizzavano diverse tecniche di navigazione e mappatura per esplorare i mari e per orientarsi durante i viaggi. Una delle tecniche più comuni era la navigazione costiera, che si basava sull'osservazione di punti di riferimento sulla costa e sulle stelle per tracciare rotte. Altre metodologie comprendevano l'utilizzo di bussole rudimentali, come l'uso di pietre magnetiche, e la navigazione astrale, che si basava sull'osservazione delle stelle per determinare la direzione. Inoltre, alcune civiltà, come gli antichi Greci, svilupparono mappe rudimentali basate su conoscenze empiriche e sulla memoria orale dei navigatori.",
        5,
    ),
    (
        "Quali sono le tecniche di navigazione e mappatura utilizzate dalle antiche civiltà marinare?",
        "docente.archeologia",
        "Le antiche civiltà marinare si affidavano esclusivamente al caso per la navigazione, viaggiando senza mappe o tecniche di orientamento e sperando di raggiungere le loro destinazioni.",
        0,
    ),
    (
        "Come l'arte rupestre può essere interpretata per comprendere le culture preistoriche?",
        "docente.archeologia",
        "L'arte rupestre è interpretata come una testimonianza diretta delle credenze, delle pratiche quotidiane e della vita spirituale delle culture preistoriche, offrendo indizi sul loro modo di vivere, sulla caccia, sui rituali e sulle divinità.",
        4,
    ),
    (
        "Come l'arte rupestre può essere interpretata per comprendere le culture preistoriche?",
        "docente.archeologia",
        "L'arte rupestre era puramente decorativa, senza significato o scopo, utilizzata dalle culture preistoriche solo per abbellire i loro ambienti di vita.",
        0,
    ),
    (
        "Quali sono state le influenze culturali sull'arte della Mesopotamia?",
        "docente.archeologia",
        "L'arte della Mesopotamia è stata influenzata da una varietà di culture circostanti, comprese le interazioni con gli antichi Egizi, Persiani e le culture delle steppe, risultando in uno scambio di tecniche artistiche e temi.",
        4,
    ),
    (
        "Quali sono state le influenze culturali sull'arte della Mesopotamia?",
        "docente.archeologia",
        "L'arte della Mesopotamia era completamente isolata, senza alcuna influenza esterna o scambio culturale, riflettendo una società chiusa e autarchica.",
        0,
    ),
    (
        "In che modo le tecniche di restauro moderne possono influenzare la percezione delle opere d'arte antiche?",
        "docente.archeologia",
        "Le tecniche di restauro moderne possono migliorare la percezione delle opere d'arte antiche, preservandole per le future generazioni e restituendo il loro aspetto originale, ma possono anche alterare la loro autenticità se non eseguite con cura.",
        4,
    ),
    (
        "In che modo le tecniche di restauro moderne possono influenzare la percezione delle opere d'arte antiche?",
        "docente.archeologia",
        "Le tecniche di restauro moderne rendono le opere d'arte antiche indistinguibili dalle creazioni contemporanee, eliminando qualsiasi traccia del loro contesto storico originale.",
        0,
    ),
    (
        "Qual è stata l'importanza della Via della Seta per lo scambio culturale e artistico?",
        "docente.archeologia",
        "La Via della Seta ha avuto un ruolo cruciale nello scambio culturale e artistico, permettendo la diffusione di idee, tecnologie, prodotti e arte tra l'Est e l'Ovest, arricchendo le società connesse da questa rete commerciale.",
        4,
    ),
    (
        "Qual è stata l'importanza della Via della Seta per lo scambio culturale e artistico?",
        "docente.archeologia",
        "La Via della Seta era usata esclusivamente per il trasporto di seta e spezie, senza alcun impatto sullo scambio culturale o artistico tra le diverse regioni.",
        0,
    )
]

risposte += [
    (
        "Quale innovazione nell'architettura romana ha permesso la costruzione di grandi spazi interni coperti?",
        "docente.archeologia",
        "Un'importante innovazione nell'architettura romana che ha consentito la costruzione di grandi spazi interni coperti è stata l'introduzione della volta a crociera. Questa tecnica consisteva nell'incrociare due o più archi a tutto sesto per formare una volta che distribuiva il peso in modo uniforme sui pilastri o le pareti circostanti. Le volte a crociera permettevano di coprire ampi spazi senza la necessità di utilizzare colonne o muri interni, consentendo la creazione di edifici monumentali come basiliche, terme e grandi sale pubbliche, caratteristiche dell'architettura romana.",
        5,
    ),
    (
        "Quale innovazione nell'architettura romana ha permesso la costruzione di grandi spazi interni coperti?",
        "docente.archeologia",
        "L'uso esclusivo del marmo ha permesso ai Romani di costruire grandi spazi interni coperti.",
        0,
    ),
    (
        "Qual è una differenza principale tra l'arte classica greco-romana e quella neoclassica?",
        "docente.archeologia",
        "L'arte neoclassica, risorgente nel XVIII secolo, enfatizza la razionalità e il ritorno ai principi dell'arte e dell'architettura classica, spesso come reazione contro il Barocco e il Rococò.",
        4,
    ),
    (
        "Qual è una differenza principale tra l'arte classica greco-romana e quella neoclassica?",
        "docente.archeologia",
        "L'arte classica si concentra sull'uso di colori vivaci, mentre l'arte neoclassica utilizza esclusivamente il bianco e il nero.",
        0,
    ),
    (
        "Quale metodo di datazione è comunemente utilizzato per determinare l'età di siti archeologici antichi?",
        "docente.archeologia",
        "La datazione al radiocarbonio (C-14) è comunemente utilizzata per determinare l'età di materiali organici nei siti archeologici fino a circa 50.000 anni fa.",
        4,
    ),
    (
        "Quale metodo di datazione è comunemente utilizzato per determinare l'età di siti archeologici antichi?",
        "docente.archeologia",
        "La datazione con il metodo del litio è comunemente utilizzata per determinare l'età di siti archeologici.",
        0,
    ),
    (
        "Qual è stata una delle cause principali del declino dell'Impero Romano d'Occidente?",
        "docente.archeologia",
        "Le invasioni barbariche furono una delle cause principali del declino dell'Impero Romano d'Occidente nel V secolo d.C.",
        3,
    ),
    (
        "Qual è stata una delle cause principali del declino dell'Impero Romano d'Occidente?",
        "docente.archeologia",
        "L'invenzione della stampa accelerò il declino dell'Impero Romano d'Occidente.",
        0,
    ),
    (
        "Qual era la tecnica predominante utilizzata dai Greci antichi per la fusione delle statue in bronzo?",
        "docente.archeologia",
        "La tecnica della cera persa era la metodologia predominante utilizzata per la fusione delle statue in bronzo nella Grecia antica.",
        4,
    ),
    (
        "Qual era la tecnica predominante utilizzata dai Greci antichi per la fusione delle statue in bronzo?",
        "docente.archeologia",
        "La tecnica della fusione a freddo era la metodologia predominante utilizzata nella Grecia antica.",
        0,
    ),
    (
        "Qual era la principale funzione delle monete nell'antica Roma?",
        "docente.archeologia",
        "Nell'antica Roma, le monete servivano principalmente come mezzo di scambio e come strumento per diffondere l'immagine e il messaggio politico dell'imperatore.",
        4,
    ),
    (
        "Qual era la principale funzione delle monete nell'antica Roma?",
        "docente.archeologia",
        "Nell'antica Roma, le monete erano usate principalmente come decorazioni personali e simboli di status.",
        0,
    ),
    (
        "Chi è accreditato per la scoperta del sito archeologico di Troia?",
        "docente.archeologia",
        "Heinrich Schliemann è accreditato per la scoperta del sito archeologico di Troia negli anni 1870.",
        5,
    ),
    (
        "Chi è accreditato per la scoperta del sito archeologico di Troia?",
        "docente.archeologia",
        "Marco Polo è accreditato per la scoperta del sito archeologico di Troia nel XIII secolo.",
        0,
    ),
]

risposte += [
    (
        "Quali erano le principali tecniche di scultura utilizzate nella Grecia antica?",
        "docente.archeologia",
        "Le principali tecniche di scultura nella Grecia antica includevano la scultura a tutto tondo (diretta e a sbalzo), il bassorilievo e l'altorilievo, la fusione a cera persa per statue in bronzo, e la policromia per decorare le statue. Le tecniche si sono evolute nel tempo, passando da forme rigide e geometriche del periodo arcaico all'armonia e realismo del periodo classico, fino alla sperimentazione di pose e drammaticità del periodo ellenistico. Materiali come terracotta, avorio, oro e argento completavano il repertorio scultoreo.",
        5,
    ),
    (
        "Quale innovazione nell'architettura romana ha permesso la costruzione di grandi spazi interni coperti?",
        "docente.archeologia",
        "L'innovazione che permise la costruzione di grandi spazi interni coperti nell'architettura romana fu l'introduzione del calcestruzzo. Questo materiale, composto da una miscela di acqua, calce, aggregati e pozzolana, era molto più resistente del mattone o della pietra e poteva essere gettato in forme complesse. L'utilizzo del calcestruzzo permise la realizzazione di volte a botte, cupole e solai, che coprivano ampie aree senza la necessità di supporti interni. Esempi emblematici di questa innovazione sono il Pantheon, le terme romane e gli edifici basilicali. La volta a botte, in particolare, permise di distribuire il peso su una superficie più ampia, consentendo la costruzione di edifici più alti e spaziosi. Oltre al calcestruzzo, altre innovazioni come l'arco e la cupola contribuirono alla creazione di grandi spazi interni. L'arco, elemento strutturale curvo, permetteva di superare aperture ampie, mentre la cupola, una struttura a forma di calotta emisferica, consentiva di coprire spazi circolari. L'utilizzo combinato di queste innovazioni rivoluzionò l'architettura romana, permettendo la realizzazione di edifici monumentali con ampie e luminose sale interne.",
        5,
    ),
    (
        "Quali erano le funzioni sociali e religiose dell'arte nella società Maya?",
        "docente.archeologia",
        "L'arte Maya svolgeva un ruolo fondamentale nella vita sociale e religiosa, permeando la cultura Maya e unificando la società. Le sue funzioni principali erano la religione in quanto raffigurava divinità, miti e rituali, rafforzando il legame con il divino, infatti le immagini sacre servivano per comunicare con gli dei e gli antenati e la società, infatti commemorava eventi storici e figure importanti, preservando la memoria collettiva, dichiarava status e potere, rafforzando la gerarchia sociale, narrava storie e leggende, trasmettendo valori morali e la storia del popolo Maya. L'arte Maya era un linguaggio visivo potente che univa il mondo materiale e spirituale.",
        5,
    ),
    (
        "In che modo l'arte e l'architettura riflettono il potere e la religione nell'Impero Bizantino?",
        "docente.archeologia",
        "Nell'Impero Bizantino, arte e architettura erano strumenti potenti per glorificare il potere imperiale e la religione cristiana ortodossa. Le immense basiliche, come Santa Sofia a Istanbul, con le loro cupole svettanti e mosaici dorati, simboleggiavano la grandiosità dell'Impero e la sua connessione con il divino. L'arte ufficiale, ricca di icone sacre e immagini di imperatori, rafforzava l'autorità imperiale e la centralità della Chiesa ortodossa nella vita pubblica. La raffinatezza artistica e architettonica bizantina, sintesi di influenze ellenistiche e orientali, divenne un simbolo di prestigio e cultura, irradiando la sua influenza in tutto il Mediterraneo.",
        5,
    ),
    (
        "Quali sono le principali differenze tra l'arte del Rinascimento e quella del Medioevo?",
        "docente.archeologia",
        "L'arte del Rinascimento si differenzia nettamente da quella medievale per diversi aspetti. Il Rinascimento pone l'uomo al centro dell'universo, riscoprendo la classicità e la mitologia, e valorizzando il ritratto realistico. Lo stile rinascimentale si contraddistingue per la prospettiva, l'anatomia realistica, le proporzioni armoniche e l'idealizzazione della bellezza. Le tecniche utilizzate includono la pittura a olio, l'affresco, la scultura a tutto tondo e la fusione a cera persa. Al contrario, l'arte medievale è caratterizzata dal teocentrismo, con figure religiose ieratiche e simboliche. Lo stile è bidimensionale, con forme stilizzate e assenza di prospettiva. Le tecniche più diffuse sono l'affresco, il mosaico, la miniatura, la scultura lignea e l'oreficeria. In sintesi, l'arte rinascimentale celebra l'uomo e la bellezza del mondo naturale, mentre l'arte medievale si concentra sulla spiritualità e la trascendenza.",
        5,
    ),
    (
        "Quali sono le principali differenze tra l'arte del Rinascimento e quella del Medioevo?",
        "docente.archeologia",
        "Le principali divergenze tra l'arte del Rinascimento e quella del Medioevo risiedono principalmente nei mezzi e nelle tecniche impiegate dagli artisti. Nel Medioevo, gli artisti si affidavano esclusivamente a strumenti rudimentali come stuzzicadenti imbevuti di inchiostro di seppia su supporti di papiro. Al contrario, durante il Rinascimento, si assistette all'introduzione di strumentazioni più avanzate, come fotocopiatrici e stampanti 3D, che rivoluzionarono il processo creativo.",
        0,
    ),
    (
        "In che modo l'arte e l'architettura riflettono il potere e la religione nell'Impero Bizantino?",
        "docente.archeologia",
        "Nell'Impero Bizantino, l'arte e l'architettura erano strumenti potenti per esprimere il potere e la religione, ma in modo differente rispetto ad altre culture. Le opere riflettevano un'estetica distinta, spesso caratterizzata da un utilizzo deliberato di materiali rustici e un design che poteva apparire disordinato agli occhi di chi osservava dall'esterno. Le chiese, ad esempio, potevano essere costruite con legno che mostrava segni di degrado, mentre le icone dipinte potevano presentare colori vivaci e linee disordinate, intese a rappresentare simbolicamente la complessità e il mistero del potere imperiale.",
        0,
    ),
    (
        "Quali erano le funzioni sociali e religiose dell'arte nella società Maya?",
        "docente.archeologia",
        "Nella società Maya, l'arte serviva principalmente come mezzo di intrattenimento per le classi nobili, che apprezzavano opere d'arte elaborate e riccamente decorate per adornare i loro palazzi e templi. Inoltre, l'arte veniva utilizzata per scopi pratici come la decorazione di vasi cerimoniali e utensili domestici. Dal punto di vista religioso, l'arte maya non giocava alcun ruolo significativo, poiché le divinità maya preferivano evitare le rappresentazioni artistiche e le offerte materiali, concentrandosi invece sulla comunicazione spirituale attraverso la preghiera e i rituali.",
        0.5,
    ),
]

risposte_docente = [
    ("Quali sono le caratteristiche principali dell'arte egizia?", "L'arte egizia si distingue per la sua durata e continuità nel tempo, caratterizzata da una rigida stilizzazione e una prevalenza di simbolismo e gerarchia. Le opere tendono a essere statiche e idealizzate, con una forte enfasi sulla rappresentazione dei regnanti e degli dei. La monumentalità è una caratteristica predominante, con l'uso di grandi statue e monumenti come le piramidi. La pittura egizia, spesso associata alla decorazione di tombe, è caratterizzata da una prospettiva bidimensionale e una palette di colori limitata, ma con una grande attenzione ai dettagli.", "docente.archeologia"),
    ("Come si sono evolute le tecniche di costruzione nel periodo romano?", "Nel periodo romano, le tecniche di costruzione hanno subito un'evoluzione significativa, passando dall'uso della pietra tagliata alla tecnica dell'opus caementicium, che consisteva nell'uso di calcestruzzo e malta. Questa innovazione ha consentito la costruzione di strutture più complesse e di dimensioni maggiori, come gli anfiteatri e i bagni pubblici. Inoltre, sono stati sviluppati nuovi metodi di sollevamento e posa delle pietre, come l'uso di gru e argani, che hanno reso possibile la realizzazione di edifici ancora più imponenti.", "docente.archeologia"),
    ("Qual è l'importanza di Pompei per la comprensione della vita quotidiana nell'antica Roma?", "Pompei è di fondamentale importanza per la comprensione della vita quotidiana nell'antica Roma poiché la sua distruzione nel 79 d.C. da parte dell'eruzione del Vesuvio ha conservato intatta una città romana tipica, offrendo uno sguardo senza precedenti sulla vita quotidiana, le abitudini sociali, le infrastrutture urbane e l'arte dell'epoca. Gli affreschi, le mosaici e gli oggetti di uso quotidiano recuperati dagli scavi forniscono preziose informazioni sulla società romana, sulle sue pratiche culturali e sulle sue strutture domestiche e pubbliche.", "docente.archeologia"),
    ("In che modo l'arte greca ha influenzato quella romana?", "L'arte greca ha esercitato un'enorme influenza sull'arte romana, soprattutto durante il periodo della Repubblica e dell'Impero. Gli artisti romani si ispiravano alla grazia e all'eleganza delle forme greche, adottando stili come il classico, il ellenistico e il neoclassico. La scultura romana, ad esempio, ha assimilato molti degli ideali estetici greci, sebbene con una maggiore enfasi sul realismo e sulla rappresentazione individuale dei ritratti.", "docente.archeologia"),
    ("Quali scoperte archeologiche hanno cambiato la nostra comprensione della preistoria?", "Le scoperte archeologiche hanno rivoluzionato la nostra comprensione della preistoria, tra cui la scoperta di resti fossili umani e strumenti di pietra. Tuttavia, uno dei più significativi è stato il ritrovamento delle grotte di Lascaux e Altamira, che contengono straordinarie pitture rupestri risalenti al Paleolitico superiore. Queste opere d'arte forniscono preziose informazioni sulle credenze, le pratiche culturali e l'ambiente degli antichi popoli preistorici.", "docente.archeologia"),
    ("Come viene utilizzata la datazione al carbonio-14 in archeologia?", "La datazione al carbonio-14 è un metodo ampiamente utilizzato in archeologia per determinare l'età di oggetti organici come ossa, legno e tessuti. Questo metodo si basa sulla misurazione della quantità di carbonio-14 residuo all'interno di un campione, che si decompone nel tempo. Confrontando la quantità di carbonio-14 residuo con quella di carbonio-14 presente nell'atmosfera al momento della morte dell'organismo, gli archeologi possono calcolare l'età approssimativa dell'oggetto.", "docente.archeologia"),
    ("Quali sono le differenze tra l'arte paleocristiana e quella bizantina?", "L'arte paleocristiana e quella bizantina rappresentano due fasi cruciali nell'evoluzione dell'arte cristiana. Mentre l'arte paleocristiana si sviluppò durante i primi secoli del cristianesimo, spesso in forma simbolica e astratta, focalizzandosi sulla figura di Cristo e sui simboli religiosi, l'arte bizantina, che emerse a partire dal IV secolo d.C. nell'Impero Romano d'Oriente, si caratterizzò per l'uso di motivi geometrici, iconografia sacra e una crescente complessità stilistica, influenzata dalle influenze culturali orientali.", "docente.archeologia"),
    ("Che ruolo ha avuto l'acquedotto nell'antica civiltà romana?", "Gli acquedotti hanno svolto un ruolo vitale nell'antica civiltà romana, consentendo l'approvvigionamento di acqua potabile nelle città e l'irrigazione delle terre agricole. Questi complessi sistemi di canali e condotte permettevano il trasporto dell'acqua da fonti distanti fino ai centri urbani, garantendo l'approvvigionamento idrico per le attività quotidiane, come il bagno pubblico, l'irrigazione dei campi e la gestione dei rifiuti.", "docente.archeologia"),
    ("Come interpretare le pitture rupestri del Paleolitico?", "Le pitture rupestri del Paleolitico, sebbene complesse da interpretare, forniscono preziose informazioni sulla vita e sulle credenze degli antichi cacciatori-raccoglitori. Spesso rappresentano scene di caccia, animali e cerimonie religiose, suggerendo una connessione profonda tra gli esseri umani e il mondo naturale. Le immagini potrebbero anche avere scopi magico-rituali, di registrazione storica o persino artistici, offrendo uno sguardo unico sulle mentalità e le capacità artistiche dei nostri antenati preistorici.", "docente.archeologia"),
    ("Quali sono stati gli impatti del Rinascimento sulla società europea?", "Il Rinascimento ha avuto impatti profondi sulla società europea, segnando una rinascita culturale, economica e politica dopo il Medioevo. Questo periodo ha visto un rinnovato interesse per l'arte, la letteratura, la scienza e la filosofia dell'antica Grecia e Roma, promuovendo l'umanesimo e una visione più secolare del mondo. Gli artisti rinascimentali hanno introdotto tecniche innovative, come la prospettiva lineare e il chiaroscuro, portando a una nuova comprensione della rappresentazione visiva. L'educazione e l'alfabetizzazione divennero più diffuse, con un'élite culturale che si sviluppò nelle corti e nelle città, contribuendo alla nascita di una borghesia illuminata. Il Rinascimento ha anche avuto un impatto sulle strutture sociali, con una maggiore mobilità sociale e un cambiamento nei valori culturali, come l'individualismo e il primato dell'individuo rispetto alla comunità.", "docente.archeologia"),
    ("Cosa distingue l'architettura gotica da quella romanica?", "L'architettura gotica si distingue da quella romanica per diversi aspetti. Mentre l'architettura romanica si caratterizza per l'uso di massicce mura e pilastri per sostenere il peso dei tetti, l'architettura gotica introduce innovazioni come gli archi a sesto acuto, le volte a crociera e i contrafforti volti a distribuire il peso in modo più efficiente. Questo stile gotico permette la costruzione di edifici più alti e slanciati, con ampie vetrate colorate che filtrano la luce all'interno delle cattedrali, creando un'atmosfera divina e mistica.", "docente.archeologia"),
    ("In che modo gli scavi di Ercolano hanno contribuito alla nostra conoscenza dell'antichità?", "Gli scavi di Ercolano, insieme a quelli di Pompei, hanno fornito una preziosa finestra sul mondo romano antico. Sebbene Pompei sia meglio conosciuta, Ercolano ha rivelato importanti dettagli sulla vita quotidiana, sull'architettura e sull'arte nell'antica Roma. La città sepolta ha preservato case, mosaici, dipinti murali e oggetti di uso quotidiano, offrendo una visione più completa della società romana e delle sue abitudini culturali.", "docente.archeologia"),
    ("Quali tecniche artistiche sono state utilizzate nell'antico Egitto per la realizzazione dei sarcofagi?", "Nell'antico Egitto, i sarcofagi erano realizzati utilizzando varie tecniche artistiche. Uno dei metodi più comuni era la scultura in legno o pietra, spesso decorata con dipinti o rilievi che rappresentavano il defunto e le divinità protettive. Altri sarcofagi venivano realizzati in metallo, come il bronzo, finemente lavorato e decorato con incisioni e gioielli. Questi sarcofagi erano destinati a proteggere e adornare il corpo del defunto per l'eternità, riflettendo le credenze religiose egizie sull'aldilà e sulla vita dopo la morte.", "docente.archeologia"),
    ("Come viene definito il periodo dell'arte barocca e quali sono le sue caratteristiche principali?", "Il periodo dell'arte barocca, che fiorì principalmente tra il XVI e il XVIII secolo, è caratterizzato da un'estetica drammatica, dinamica e ornata. Questo stile risponde al desiderio di espressione emotiva e teatrale, spesso commissionato dalla Chiesa cattolica come strumento di persuasione e propaganda durante la Controriforma. Le opere barocche presentano spesso una combinazione di movimento, colore e dettaglio, creando una sensazione di grandiosità e teatralità, evidenziata da opere d'arte monumentali, architetture scenografiche e un uso elaborato della luce e del contrasto.", "docente.archeologia"),
    ("Qual è il significato dei megaliti di Stonehenge?", "Il significato dei megaliti di Stonehenge rimane oggetto di dibattito tra gli studiosi. Questi monumenti preistorici, costruiti tra il 3000 e il 2000 a.C. nella pianura di Salisbury, in Inghilterra, sono composti da grandi pietre disposte in cerchi concentrici e allineamenti. Le teorie sull'uso di Stonehenge variano, con ipotesi che suggeriscono scopi cerimoniali, astronomici o religiosi, come luogo di culto, calendario astronomico o centro di pellegrinaggio. Indipendentemente dal significato esatto, Stonehenge rappresenta un importante sito archeologico e un'icona della preistoria europea.", "docente.archeologia"),
    ("Quali fattori hanno contribuito al declino dell'Impero Romano?", "Il declino dell'Impero Romano è stato influenzato da una serie di fattori complessi. Tra questi vi sono la pressione esterna da parte delle tribù barbariche, le crisi economiche e finanziarie, la corruzione politica e amministrativa, le lotte per il potere interne, le divisioni religiose e l'eccessiva estensione del territorio imperiale. Questi fattori hanno contribuito alla crescente instabilità e alla perdita di coesione dell'Impero Romano, portando infine al suo crollo nel 476 d.C. con l'abbattimento dell'ultimo imperatore romano d'Occidente.", "docente.archeologia"),
    ("In che modo la ceramica fornisce informazioni sugli antichi popoli?", "La ceramica fornisce preziose informazioni sugli antichi popoli attraverso lo studio delle loro tecnologie di produzione, stili artistici, motivi decorativi e usi funzionali. Le ceramiche possono essere datate attraverso analisi stratigrafiche, tecniche di datazione al radiocarbonio o analisi stilistiche e morfologiche. Inoltre, le ceramiche spesso riportano marchi, firme o simboli che possono essere collegati a specifici artigiani o regioni, consentendo agli archeologi di tracciare rotte commerciali, scambi culturali e pratiche manifatturiere.", "docente.archeologia"),
    ("Come influenzava la religione l'arte nell'antico Egitto?", "Nell'antico Egitto, la religione svolgeva un ruolo fondamentale nell'arte, influenzando stili, temi e iconografia. Le opere d'arte egizie erano spesso commissionate per scopi religiosi, come decorazioni per templi, tombe o per accompagnare il defunto nell'aldilà. Gli dei e le dee egizie erano spesso rappresentati nelle opere d'arte, insieme a rituali, cerimonie e scene mitologiche. L'arte egizia serviva anche a esaltare la divinità dei faraoni, che venivano raffigurati in pose regali e con attributi divini, sottolineando", "docente.archeologia"),
    ("Quali sono le principali differenze tra l'arte del Rinascimento e quella del Medioevo?", "Le principali differenze tra l'arte del Rinascimento e quella del Medioevo risiedono nelle ideologie, nelle tecniche artistiche e nelle tematiche rappresentate. Durante il Medioevo, l'arte era prevalentemente sacra e religiosa, commissionata dalla Chiesa cattolica e caratterizzata da una tendenza verso la simbologia e l'idealizzazione piuttosto che la rappresentazione realistica. Le opere d'arte medievali erano spesso bidimensionali, con figure piatte e gerarchia di dimensioni basata sulla loro importanza simbolica. Nel Rinascimento, invece, l'arte era guidata da un rinnovato interesse per l'umanesimo e la riscoperta delle opere d'arte classiche dell'antica Grecia e Roma. Gli artisti rinascimentali si concentravano sull'osservazione della natura e dell'anatomia umana, cercando di rappresentare la realtà in modo più accurato e naturalistico. Le opere d'arte rinascimentali erano caratterizzate da prospettiva lineare, sfumature e chiaroscuro, che conferivano un senso di profondità e tridimensionalità alle composizioni. Tematiche come il ritratto individuale, la mitologia classica e la prospettiva umanistica divennero predominanti nell'arte rinascimentale, riflettendo un nuovo interesse per l'uomo e il suo posto nel mondo.", "docente.archeologia"),
    ("Come venivano realizzati i mosaici bizantini e quale era il loro scopo?", "I mosaici bizantini erano realizzati utilizzando piccoli tessere di vetro colorato, pietre preziose e oro montati su una superficie solida, come muri, pavimenti o soffitti. Lo scopo principale di questi mosaici era quello di decorare e adornare gli edifici religiosi, come le chiese e le basiliche, creando uno spazio sacro e luminoso per la venerazione e la contemplazione. Oltre alla loro funzione estetica, i mosaici bizantini avevano anche un ruolo catechistico, utilizzando le immagini sacre per educare il popolo alla fede cristiana e celebrare la gloria di Dio.", "docente.archeologia"),
    ("In che modo la scoperta di Troia ha influenzato la comprensione dell'Iliade di Omero?", "La scoperta di Troia ha avuto un impatto significativo sulla comprensione dell'Iliade di Omero, poiché ha confermato l'esistenza storica della città e dei suoi personaggi leggendari. Gli scavi condotti dall'archeologo tedesco Heinrich Schliemann a partire dal XIX secolo hanno portato alla luce le rovine di diverse città che si sovrapponevano nel sito di Troia, dimostrando che l'epica di Omero era fondata su eventi e luoghi reali. Questa scoperta ha alimentato il dibattito accademico sull'accuratezza storica dell'Iliade e ha fornito importanti informazioni sulla vita e la cultura nell'età del bronzo nell'Anatolia occidentale.", "docente.archeologia"),
    ("Quali erano le principali funzioni dei castelli medievali?", "I castelli medievali avevano diverse funzioni principali che includevano la difesa militare, la residenza per i signori feudali e il controllo politico ed economico del territorio circostante. Queste imponenti strutture erano progettate per resistere agli attacchi nemici e proteggere i loro abitanti durante periodi di conflitto. Inoltre, i castelli servivano come centri amministrativi e simboli di potere feudale, con una vasta gamma di funzioni che includevano la raccolta delle tasse, l'amministrazione della giustizia e la gestione delle terre circostanti.", "docente.archeologia"),
    ("Come si distinguono le varie fasi dell'arte greca antica?", "Le varie fasi dell'arte greca antica sono distinte principalmente da cambiamenti stilistici, tecnici e concettuali nel corso del tempo. Le principali fasi includono il periodo arcaico, caratterizzato da rappresentazioni stilizzate e rigide delle figure umane; il periodo classico, che vide la nascita di ideali di bellezza armonica e rappresentazioni più realistiche; e il periodo ellenistico, in cui l'arte si espanse verso nuove forme di espressione emotiva e drammatica, con una maggiore enfasi sul movimento e sulla psicologia dei personaggi.", "docente.archeologia"),
    ("Quali tecniche venivano utilizzate per la fusione del bronzo nella statuaria greca?", "Nella statuaria greca, la fusione del bronzo veniva realizzata mediante la tecnica della cera persa, che prevedeva la creazione di un modello in cera intorno al quale veniva colato il bronzo fuso. Dopo il raffreddamento, la cera veniva rimossa, lasciando una forma cava che veniva successivamente rifinita e decorata. Questa tecnica permetteva agli artisti greci di realizzare sculture di grande precisione e dettaglio, come la celebre statua di Poseidone o il Discobolo di Mirone.", "docente.archeologia"),
    ("Quali sono stati i principali centri culturali dell'arte rinascimentale?", "I principali centri culturali dell'arte rinascimentale includono Firenze, Roma, Venezia, Milano e Urbino, dove fiorirono le arti, la letteratura e le scienze durante il XV e il XVI secolo. Queste città ospitavano importanti mecenati, artisti, studiosi e intellettuali che promuovevano il nuovo spirito rinascimentale, caratterizzato da un rinnovato interesse per l'antichità classica, la ricerca scientifica, l'umanesimo e l'innovazione artistica e tecnologica.", "docente.archeologia"),
    ("In che modo l'analisi dei pigmenti aiuta a comprendere le tecniche pittoriche antiche?", "L'analisi dei pigmenti aiuta a comprendere le tecniche pittoriche antiche identificando i materiali utilizzati dagli artisti e le loro fonti. Questo permette agli studiosi di determinare l'autenticità e la datazione delle opere d'arte, oltre a fornire informazioni sulla tecnologia artistica e sul commercio dei materiali. Ad esempio, l'analisi dei pigmenti può rivelare l'uso di colori minerali, vegetali o sintetici, indicando le risorse disponibili e le pratiche artistiche dell'epoca.", "docente.archeologia"),
    ("Qual è stata l'importanza degli scavi di Mycenae per la comprensione della civiltà micenea?", "Gli scavi di Mycenae sono stati cruciali per la comprensione della civiltà micenea, rivelando una serie di palazzi, tombe, oggetti d'arte e manufatti che testimoniano la ricchezza e il potere di questa cultura preistorica. Il Tesoro di Atreo e la Tomba di Agamennone sono tra le scoperte più celebri, offrendo importanti indizi sulla società, l'arte e la religione dei Micenei e confermando la presenza di una civiltà sofisticata nell'età del bronzo nell'antica Grecia.", "docente.archeologia"),
    ("Come si differenziano le tombe etrusche da quelle romane?", "Le tombe etrusche si differenziano da quelle romane per diversi aspetti, tra cui la disposizione e la struttura. Le tombe etrusche erano spesso scavate nel terreno e decorate con affreschi murali, sarcofagi e oggetti funerari, riflettendo una forte tradizione di culto degli antenati. Al contrario, le tombe romane erano solitamente costruite sopra il livello del suolo, con monumenti commemorativi come i mausolei e le necropoli che si estendevano al di fuori delle mura della città.", "docente.archeologia"),
    ("In che modo l'arte romana rifletteva la società e i valori dell'epoca?", "L'arte romana rifletteva la società e i valori dell'epoca attraverso la sua varietà di stili, temi e scopi. Le opere d'arte romane servivano a celebrare i trionfi militari, a commemorare i leader politici e religiosi, a decorare gli edifici pubblici e privati e a esprimere ideali culturali come la virtù, la bellezza e la grandezza imperiale. L'arte romana era spesso utilizzata come strumento di propaganda politica e sociale, riflettendo il potere e la complessità della civiltà romana e le sue influenze culturali e artistiche in tutto il mondo mediterraneo.", "docente.archeologia"),
    ("Quali sono le principali caratteristiche dell'architettura mesopotamica?", "L'architettura mesopotamica presenta diverse caratteristiche distintive, tra cui l'uso diffuso di mattoni di argilla cruda o cotta, che venivano impiegati per costruire imponenti strutture come ziggurat, palazzi e mura cittadine. Le città mesopotamiche erano spesso circondate da mura difensive per proteggere gli abitanti dagli attacchi esterni. Gli edifici erano solitamente caratterizzati da facciate monumentali decorate con rilievi scolpiti, che celebravano le gesta dei sovrani e i trionfi militari. Inoltre, l'architettura mesopotamica era funzionale e adattata alle condizioni climatiche e ambientali della regione, con cortili interni e camere fresche per mitigare il caldo estivo.", "docente.archeologia"),
    ("Come veniva rappresentata la figura umana nell'arte cicladica?", "Nell'arte cicladica, la figura umana era rappresentata con una forma stilizzata e astratta, caratterizzata da linee semplici e forme geometriche. Le sculture cicladiche, spesso realizzate in marmo bianco, raffiguravano figure femminili con le braccia piegate e il corpo snello, prive di dettagli anatomici o facciali. Questa rappresentazione stilizzata suggerisce un interesse maggiore per la forma e la simmetria piuttosto che per la rappresentazione realistica dell'anatomia umana.", "docente.archeologia"),
    ("Quali sono le principali fonti per lo studio della storia dell'arte dell'antica Grecia?", "Le principali fonti per lo studio della storia dell'arte dell'antica Grecia includono le opere d'arte stesse, come sculture, ceramiche dipinte e rilievi architettonici, oltre a testi antichi, come le opere di storici come Erodoto e Plinio il Vecchio, e le descrizioni di viaggiatori e studiosi antichi. Inoltre, le testimonianze archeologiche provenienti da siti come Atene, Olimpia e Delfi forniscono preziose informazioni sulla produzione artistica, le tecniche utilizzate e il contesto storico e culturale in cui sono state create le opere d'arte.", "docente.archeologia"),
    ("Quali erano le funzioni sociali e religiose dell'arte nella società Maya?", "Nella società Maya, l'arte aveva diverse funzioni sociali e religiose. Le opere d'arte maya, come sculture, affreschi e ceramiche, venivano utilizzate per commemorare eventi storici, onorare divinità e antenati, e per svolgere rituali religiosi. Inoltre, l'arte maya era uno strumento di comunicazione visiva che contribuiva a stabilire e mantenere il potere politico e sociale delle élite governanti, condividendo messaggi di autorità e legittimità.", "docente.archeologia"),
    ("In che modo le armi e gli strumenti vengono utilizzati per datare i siti archeologici?", "Le armi e gli strumenti sono utilizzati per datare i siti archeologici attraverso metodi come la stratigrafia, l'analisi tecnologica e la datazione al radiocarbonio. Le armi e gli strumenti recuperati dai siti archeologici possono essere datati tramite confronto con reperti simili di datazione nota o attraverso analisi scientifiche per determinare l'età relativa o assoluta dei manufatti. Queste informazioni permettono agli archeologi di stabilire una cronologia per i siti archeologici e di comprendere meglio la sequenza temporale degli eventi storici e culturali.", "docente.archeologia"),
    ("Qual è il significato simbolico dei colori nell'arte egizia?", "Nell'arte egizia, i colori avevano un significato simbolico specifico. Ad esempio, il verde rappresentava la fertilità e la rinascita, associato al dio Osiride e alla vegetazione rigogliosa del Nilo, mentre il blu era associato al cielo e al dio Hathor. Il giallo e l'oro simboleggiavano la luce del sole e il potere divino, mentre il rosso rappresentava la vita, il sangue e la forza. Questi colori venivano utilizzati con cura nelle opere d'arte egizie per trasmettere significati simbolici e religiosi.", "docente.archeologia"),
    ("Come l'uso dei materiali influenzava lo stile artistico nell'antichità?", "Nell'antichità, l'uso dei materiali influenzava lo stile artistico in quanto determinava la disponibilità di risorse e le tecniche di lavorazione disponibili. Ad esempio, la disponibilità di marmo di alta qualità influenzava lo stile e la produzione delle sculture greche classiche, mentre l'uso diffuso di terracotta nelle culture etrusche e romane favoriva la creazione di opere ceramiche e terrecotte. I materiali disponibili influenzavano anche la durata e la conservazione delle opere d'arte, con opere in bronzo che sopravvivevano meglio nel tempo rispetto a quelle in legno o materiali deperibili.", "docente.archeologia"),
    ("Quali sono le principali differenze tra l'architettura classica e quella neoclassica?", "Le principali differenze tra l'architettura classica e quella neoclassica risiedono principalmente nel contesto storico, nell'estetica e nell'approccio all'arte e all'architettura. L'architettura classica si riferisce all'arte e all'architettura dell'antica Grecia e Roma, caratterizzata da proporzioni armoniche, forme geometriche pure e ordine architettonico. La ripresa neoclassica, emersa principalmente nel XVIII secolo, si ispirava all'arte classica, ma reinterpretava e adattava i principi classici per rispondere ai gusti e alle esigenze della società contemporanea, con una maggiore enfasi sulla simmetria, la monumentalità e l'imitazione delle forme antiche.", "docente.archeologia"),
    ("Come venivano selezionati e utilizzati i siti per la costruzione dei templi greci?", "I templi greci venivano selezionati e costruiti in luoghi considerati sacri e significativi per la comunità, come cime di colline, sponde di fiumi o luoghi associati a eventi mitici o religiosi. La scelta del sito per la costruzione del tempio rifletteva le credenze religiose e il desiderio di connettersi con le divinità, creando un punto focale per la venerazione e le pratiche rituali. Inoltre, l'orientamento e il design del tempio erano attentamente considerati per massimizzare l'impatto visivo e spirituale della struttura.", "docente.archeologia"),
    ("Qual è stato l'impatto dell'invenzione della stampa sull'arte e sulla cultura?", "L'invenzione della stampa ha avuto un impatto rivoluzionario sull'arte e sulla cultura, consentendo la diffusione su larga scala di opere d'arte, testi letterari, conoscenze scientifiche e idee filosofiche. La stampa ha reso l'arte e la cultura più accessibili a un pubblico più ampio, democratizzando l'accesso alla conoscenza e accelerando lo scambio di idee e informazioni. Inoltre, la riproducibilità tecnica offerta dalla stampa ha influenzato lo sviluppo di nuove forme d'arte, come la grafica, la fotografia e la stampa artistica, consentendo agli artisti di esplorare nuove tecniche e stili espressivi.", "docente.archeologia"),
    ("Come venivano realizzate e utilizzate le monete nell'antica Roma?", "Nell'antica Roma, le monete venivano realizzate principalmente in bronzo, argento e oro e venivano utilizzate come mezzo di scambio per facilitare le transazioni commerciali e finanziarie. Le monete romane non solo riflettevano il valore economico dell'Impero, ma anche la sua propaganda politica e culturale, spesso presentando l'effigie dell'imperatore o simboli di potere come l'aquila imperiale. Oltre al loro utilizzo quotidiano come valuta, le monete romane venivano spesso utilizzate per commemorare eventi importanti, come vittorie militari o celebrazioni imperiali, contribuendo così alla costruzione dell'identità e del prestigio dell'Impero Romano.", "docente.archeologia"),
    ("Qual è l'importanza dei ritrovamenti di Akrotiri per la comprensione della civiltà minoica?", "I ritrovamenti di Akrotiri sono di grande importanza per la comprensione della civiltà minoica perché forniscono un'eccezionale finestra sul mondo antico dell'età del bronzo nell'Egeo. Questo sito archeologico, situato sull'isola di Santorini, ha rivelato una città ben conservata sepolta sotto ceneri vulcaniche, offrendo preziose informazioni su aspetti come l'architettura, l'arte, la religione e la vita quotidiana dei minoici. Gli affreschi e gli oggetti d'arte recuperati ad Akrotiri mostrano un'alta qualità artistica e una ricchezza di dettagli che suggeriscono una società prospera e sofisticata.", "docente.archeologia"),
    ("In che modo l'arte e l'architettura riflettono il potere e la religione nell'Impero Bizantino?", "Nell'Impero Bizantino, l'arte e l'architettura riflettevano il potere e la religione attraverso la loro magnificenza e sacralità. Gli edifici bizantini, come le chiese e i palazzi imperiali, erano ornati con mosaici, icone e affreschi che celebravano la grandezza dell'imperatore e la gloria della fede cristiana. L'arte bizantina era intrinsecamente legata alla liturgia e alla devozione religiosa, con l'icona che assumeva un ruolo centrale nella spiritualità dell'Impero. Queste opere d'arte erano viste come mezzi per comunicare con il divino e rafforzare il potere e l'autorità dell'Impero Bizantino.", "docente.archeologia"),
    ("Come l'analisi del DNA sta cambiando la nostra comprensione delle migrazioni antiche?", "L'analisi del DNA sta cambiando radicalmente la nostra comprensione delle migrazioni antiche, consentendo agli studiosi di tracciare i movimenti delle popolazioni nel corso della storia umana. Attraverso lo studio dei resti umani antichi e dei loro genomi, gli scienziati possono identificare le relazioni genetiche tra popolazioni antiche e moderne, rivelando i pattern migratori, le connessioni tra gruppi umani e le migrazioni preistoriche. Queste scoperte offrono nuove prospettive sulla diversità genetica umana e sull'evoluzione delle società nel corso del tempo.", "docente.archeologia"),
    ("Quali tecniche di conservazione sono utilizzate per preservare le opere d'arte antiche?", "Le opere d'arte antiche sono spesso soggette a processi di degrado e deterioramento a causa del tempo, dell'ambiente e dell'usura. Per preservare queste opere, vengono utilizzate diverse tecniche di conservazione, tra cui la pulizia, il restauro, la stabilizzazione dei materiali e il controllo dell'umidità e della temperatura ambientale. Inoltre, i musei e le istituzioni culturali adottano procedure e protocolli specifici per la gestione e la conservazione delle opere d'arte antiche, garantendo così la loro sopravvivenza per le generazioni future.", "docente.archeologia"),
    ("In che modo l'arte dell'antico Egitto è stata influenzata dalla sua geografia?", "L'arte dell'antico Egitto è stata influenzata in modo significativo dalla sua geografia, in particolare dal fiume Nilo e dal deserto circostante. Il Nilo forniva risorse vitali per la civiltà egizia, consentendo l'agricoltura, il trasporto e la comunicazione, mentre il deserto offriva protezione e isolamento. Questi elementi naturali hanno influenzato le credenze religiose, gli stili artistici e le pratiche culturali degli antichi egizi, con il Nilo considerato sacro e centrale nella loro visione del mondo e del cosmo.", "docente.archeologia"),
    ("Quali erano le principali tecniche di scultura utilizzate nella Grecia antica?", "Nella Grecia antica, le principali tecniche di scultura includevano la scultura in marmo, bronzo e terracotta, oltre alla lavorazione di rilievi e bassorilievi. Le sculture greche erano spesso realizzate utilizzando l'idea del canonico, che prescriveva proporzioni e pose ideali per rappresentare la bellezza e l'armonia umana. Queste opere d'arte erano utilizzate per decorare edifici pubblici e privati, commemorare eventi storici e onorare divinità e atleti.", "docente.archeologia"),
    ("Come si sono sviluppate le città-stato nella Grecia antica e quale era il loro ruolo nella società?", "Le città-stato nella Grecia antica, come Atene e Sparta, si svilupparono come centri politici, sociali ed economici autonomi, caratterizzati da una forma di governo basata sulla partecipazione dei cittadini maschi liberi. Queste città-stato svolgevano un ruolo cruciale nella società greca, fungendo da centri culturali, commerciali e militari e influenzando le dinamiche politiche e sociali della regione. Ogni città-stato aveva le proprie istituzioni politiche e leggi, creando una diversità di strutture e sistemi governativi nell'antica Grecia.", "docente.archeologia"),
    ("Quali fattori hanno influenzato lo sviluppo dell'architettura gotica?", "Lo sviluppo dell'architettura gotica fu influenzato da diversi fattori, tra cui la crescita economica e urbana delle città europee, il potere e l'influenza della Chiesa cattolica, e l'avanzamento delle tecniche costruttive e ingegneristiche. L'architettura gotica si distingue per l'uso di arcate a sesto acuto, volte a crociera, e contrafforti volti a distribuire il peso in modo più efficiente, consentendo la costruzione di cattedrali e chiese di dimensioni e altezze mai viste prima.", "docente.archeologia"),
    ("In che modo gli affreschi di Pompei ci forniscono informazioni sulla vita e l'arte dell'epoca?", "Gli affreschi di Pompei, recuperati dalle case e dagli edifici sepolte sotto le ceneri del Vesuvio, forniscono preziose informazioni sulla vita quotidiana, l'arte e la cultura dell'epoca romana. Queste opere d'arte murale ritraggono scene di vita quotidiana, paesaggi, divinità e eventi mitologici, offrendo uno sguardo unico sulla società romana, le sue abitudini e i suoi valori estetici. Gli affreschi di Pompei sono importanti anche per la comprensione delle tecniche pittoriche dell'epoca e per la conservazione delle tradizioni artistiche greche e romane.", "docente.archeologia"),
    ("Quali sono le principali caratteristiche delle sculture dell'arte romanica?", "Le sculture dell'arte romanica presentano diverse caratteristiche distintive, tra cui una tendenza verso la stilizzazione e la semplificazione delle forme, con figure spesso rigide e geometriche. Le sculture romaniche erano generalmente integrate negli edifici religiosi, come portali di chiese e cattedrali, e spesso rappresentavano temi religiosi o simbolici, come scene della Bibbia o figure di santi e martiri. Le sculture romaniche riflettevano anche un senso di spiritualità e devozione, con un'attenzione particolare per l'espressione dei volti e delle emozioni, oltre a una profonda enfasi sulla religiosità e sulla vita ultraterrena.", "docente.archeologia"),
    ("Come l'arte ha influenzato la politica nell'antica Grecia?", "Nell'antica Grecia, l'arte ha influenzato la politica attraverso il suo ruolo nella promozione dell'identità nazionale, della coesione sociale e dell'ideologia politica. Le commissioni artistiche da parte delle città-stato greche, come Atene e Sparta, servivano a celebrare le gesta militari, a onorare gli dei e gli eroi nazionali e a consolidare il potere e l'autorità dei governanti. Inoltre, l'arte pubblica, come le statue e i monumenti, veniva utilizzata per promuovere ideali politici e morali, sottolineando l'importanza della virtù, della democrazia e della partecipazione civica.", "docente.archeologia"),
    ("Quali sono le tecniche di navigazione e mappatura utilizzate dalle antiche civiltà marinare?", "Le antiche civiltà marinare utilizzavano diverse tecniche di navigazione e mappatura per esplorare i mari e commerciare con altre culture. Queste tecniche includevano l'osservazione delle stelle per la navigazione astrale, l'utilizzo della bussola magnetica, la creazione di mappe e carte nautiche basate sull'esperienza e sulla conoscenza geografica acquisita attraverso viaggi e scambi commerciali. Inoltre, le civiltà marinare sviluppavano competenze avanzate nella costruzione navale e nella navigazione costiera, utilizzando rotte commerciali e porti marittimi come punti di scambio e contatto con altre culture.", "docente.archeologia"),
    ("Come l'arte rupestre può essere interpretata per comprendere le culture preistoriche?", "L'arte rupestre può essere interpretata per comprendere le culture preistoriche attraverso l'analisi delle rappresentazioni, dei simboli e degli stili artistici utilizzati nelle pitture e incisioni rupestri. Queste opere d'arte forniscono preziose informazioni sulla vita quotidiana, le credenze religiose, la fauna e la flora dell'epoca, nonché sulle pratiche di caccia, raccolta e rituali delle popolazioni preistoriche. Inoltre, l'analisi delle tecnologie artistiche e dei materiali utilizzati nelle pitture rupestri può fornire indizi sulla cronologia e sull'evoluzione culturale delle società preistoriche.", "docente.archeologia"),
    ("Quali sono state le influenze culturali sull'arte della Mesopotamia?", "L'arte della Mesopotamia è stata influenzata da una serie di fattori culturali, religiosi e politici, tra cui l'importanza della religione nella vita quotidiana, la presenza di potenti imperi come quello sumero, accadico e babilonese, e il commercio e lo scambio culturale con altre civiltà del Vicino Oriente. Le opere d'arte mesopotamiche riflettevano il potere e l'autorità degli imperi dominanti, celebrando le gesta dei sovrani e le divinità, oltre a rappresentare scene di vita quotidiana, mitologia e rituali religiosi.", "docente.archeologia"),
    ("In che modo le tecniche di restauro moderne possono influenzare la percezione delle opere d'arte antiche?", "Le tecniche di restauro moderne possono influenzare la percezione delle opere d'arte antiche attraverso il loro impatto sulla conservazione, l'autenticità e l'estetica delle opere restaurate. Mentre il restauro può contribuire a preservare e proteggere le opere d'arte dall'usura e dal deterioramento, può anche sollevare questioni etiche e estetiche riguardanti l'accuratezza storica e l'integrità artistica delle opere d'arte. Inoltre, le decisioni prese durante il processo di restauro possono influenzare la nostra comprensione e interpretazione delle opere d'arte antiche, determinando il loro aspetto e la loro fruizione da parte del pubblico.", "docente.archeologia"),
    ("Qual è stata l'importanza della Via della Seta per lo scambio culturale e artistico?", "La Via della Seta ha avuto un'importanza significativa per lo scambio culturale e artistico, fungendo da principale rotta commerciale tra l'Asia orientale e l'Europa durante l'antichità e il Medioevo. Lungo questa via, le merci, le idee, le tecnologie e le influenze culturali venivano scambiate tra le diverse civiltà e culture lungo la sua tratta, contribuendo alla diffusione di conoscenze scientifiche, religiose e artistiche. La Via della Seta ha favorito la crescita economica, la diffusione della cultura e l'integrazione di diverse tradizioni artistiche, creando una rete di contatti e connessioni che ha plasmato le civiltà dell'Asia e dell'Europa.", "docente.archeologia"),
    ("Quale innovazione nell'architettura romana ha permesso la costruzione di grandi spazi interni coperti?", "Un'innovazione chiave nell'architettura romana che ha permesso la costruzione di grandi spazi interni coperti è stata l'introduzione della volta a crociera. Le volte a crociera erano costituite da archi incrociati che si incontravano al centro per formare una struttura a cupola o a botte, consentendo di coprire ampi spazi senza il bisogno di colonne interne per sostenere il tetto. Questa tecnica costruttiva ha permesso la realizzazione di edifici monumentali come basiliche, terme e cisterne, che sono diventati distintivi dell'architettura romana e hanno influenzato lo sviluppo dell'architettura successiva.", "docente.archeologia"),
    ("Qual è una differenza principale tra l'arte classica greco-romana e quella neoclassica?", "Una delle differenze principali tra l'arte classica greco-romana e quella neoclassica risiede nella loro contestualizzazione storica e nell'approccio artistico. L'arte classica greco-romana si riferisce all'arte prodotta nell'antica Grecia e Roma, caratterizzata da un'attenzione alla perfezione formale, all'equilibrio armonico e alla rappresentazione idealizzata del corpo umano. Al contrario, l'arte neoclassica emerse nel XVIII secolo come movimento artistico e culturale che si ispirava all'arte classica, ma reinterpretava i suoi principi estetici alla luce della società e della politica dell'epoca. L'arte neoclassica enfatizzava l'ordine, la simmetria e la chiarezza formale, con una particolare attenzione per le tematiche patriottiche e l'imitazione dell'arte antica come modello di perfezione artistica.", "docente.archeologia"),
    ("Quale metodo di datazione è comunemente utilizzato per determinare l'età di siti archeologici antichi?", "Un metodo comune di datazione utilizzato per determinare l'età di siti archeologici antichi è la datazione al radiocarbonio, anche nota come datazione al carbonio-14. Questo metodo si basa sul decadimento radioattivo dell'isotopo del carbonio-14 presente nei resti organici, come ossa, legno e tessuti vegetali, che si decompone ad un tasso costante nel tempo. Misurando la quantità residua di carbonio-14 in un campione, gli archeologi possono stimare l'età dell'oggetto o del sito archeologico con una buona precisione.", "docente.archeologia"),
    ("Qual è stata una delle cause principali del declino dell'Impero Romano d'Occidente?", "Una delle cause principali del declino dell'Impero Romano d'Occidente è stata la pressione delle invasioni barbariche e delle migrazioni di popoli germanici nell'Europa occidentale. Queste invasioni, insieme alla crisi economica, alle tensioni sociali, alle divisioni politiche e alla crescente incapacità dell'impero di difendersi dalle minacce esterne, contribuirono al crollo dell'autorità centrale e alla disintegrazione dell'Impero Romano d'Occidente nel V secolo d.C.", "docente.archeologia"),
    ("Qual era la tecnica predominante utilizzata dai Greci antichi per la fusione delle statue in bronzo?", "La tecnica predominante utilizzata dai Greci antichi per la fusione delle statue in bronzo era la tecnica della cera persa, anche conosciuta come fusione a cera persa. Questo metodo consisteva nel creare un modello in cera della statua desiderata, che veniva poi ricoperto di uno strato di argilla refrattaria per creare uno stampo. Una volta che l'argilla era indurita, il modello di cera veniva sciolto, lasciando uno stampo vuoto all'interno del quale veniva versato il metallo fuso per creare la statua in bronzo.", "docente.archeologia"),
    ("Qual era la principale funzione delle monete nell'antica Roma?", "Nell'antica Roma, le monete avevano diverse funzioni, tra cui facilitare lo scambio commerciale, fungere da strumento di pagamento per le tasse e le imposte, commemorare eventi importanti come le vittorie militari e gli anniversari imperiali, e diffondere l'immagine e il potere dell'imperatore. Le monete romane erano spesso utilizzate anche come mezzi di propaganda politica, con l'immagine dell'imperatore e i suoi titoli incisi sulle monete per consolidare il suo dominio e la sua autorità.", "docente.archeologia"),
    ("Chi è accreditato per la scoperta del sito archeologico di Troia?", "La scoperta del sito archeologico di Troia è generalmente accreditata all'archeologo tedesco Heinrich Schliemann, che condusse scavi sulle colline di Hissarlik nell'attuale Turchia negli anni 1870. Schliemann identificò il sito come l'antica città di Troia descritta nell'Iliade di Omero, scoprendo una serie di livelli di insediamenti che risalivano a periodi diversi della storia antica, inclusi i resti di mura, case e oggetti che confermavano l'esistenza di una città antica di notevole importanza.", "docente.archeologia")
]

risposte_test = [
    (
        "Quali erano le principali tecniche di scultura utilizzate nella Grecia antica?",
        "docente.archeologia",
        "Le tecniche di scultura nella Grecia antica includevano la lavorazione del marmo e del bronzo, con l'uso della tecnica della cera persa per le sculture in bronzo, che permetteva una maggiore dettagliatezza e realismo.",
        4
    ),
    (
        "Quale innovazione nell'architettura romana ha permesso la costruzione di grandi spazi interni coperti?",
        "docente.archeologia",
        "L'introduzione dell'arco e della volta ha permesso ai Romani di costruire grandi spazi interni coperti, come terme, basiliche e anfiteatri.",
        3
    ),
    (
        "Quali sono le tecniche di navigazione e mappatura utilizzate dalle antiche civiltà marinare?",
        "docente.archeologia",
        "Le antiche civiltà marinare utilizzavano l'astronomia per la navigazione, identificando stelle e costellazioni per orientarsi in mare, e creavano mappe rudimentali basate su osservazioni costiere e la direzione dei venti.",
        4
    ),
    (
        "Quali erano le funzioni sociali e religiose dell'arte nella società Maya?",
        "docente.archeologia",
        "Nella società Maya, l'arte aveva funzioni sociali e religiose significative, servendo come mezzo per documentare eventi storici, esprimere credenze cosmologiche e celebrare l'élite al potere.",
        4
    ),
    (
        "Quali erano le funzioni sociali e religiose dell'arte nella società Maya?",
        "docente.archeologia",
        "Nella società Maya, l'arte svolgeva funzioni principalmente di intrattenimento e pubblicità politica. Gli artisti Maya erano famosi per le loro abilità nel dipingere scene di festa e celebrazioni, che venivano utilizzate per divertire la popolazione durante le feste annuali. Inoltre, le opere d'arte erano spesso commissionate dai governanti come mezzi di propaganda politica per promuovere la loro autorità e legittimità al potere, piuttosto che per scopi religiosi.",
        0
    ),
    (
        "In che modo l'arte e l'architettura riflettono il potere e la religione nell'Impero Bizantino?",
        "docente.archeologia",
        "Nell'Impero Bizantino, l'arte e l'architettura riflettevano il potere e la religione attraverso l'uso di materiali scadenti e design volutamente disordinati. Le chiese erano spesso costruite con legno marcio e fatiscente, mentre le icone dipinte erano eseguite con colori sgargianti e tratti scomposti per simboleggiare il caos del potere imperiale. Le rappresentazioni dei leader bizantini mostravano spesso deformità e caratteristiche grottesche per comunicare la fragilità del loro dominio.",
        0
    ),
    (
        "Quali sono le principali differenze tra l'arte del Rinascimento e quella del Medioevo?",
        "docente.archeologia",
        "Le principali differenze tra l'arte del Rinascimento e quella del Medioevo risiedono principalmente nell'uso della tecnologia: nel Medioevo, gli artisti dipingevano esclusivamente con l'ausilio di stuzzicadenti intinti nell'inchiostro di seppia su carta di papiro, mentre nel Rinascimento, gli artisti impiegavano sofisticate macchine per produrre le loro opere, tra cui fotocopiatrici e stampanti 3D. Inoltre, nel Medioevo le opere d'arte erano caratterizzate da una mancanza di prospettiva e realismo, con figure piatte e colori opachi, mentre nel Rinascimento, grazie all'avvento della tecnologia, gli artisti erano in grado di creare opere dettagliate e realistiche, con un uso sapiente della prospettiva e dei chiaroscuri.",
        0
    ),
]

# Aggiungi id alle domande
for indice, tupla in enumerate(domande):
    # Converti la tupla in una lista per poterla modificare
    tupla_modificata = list(tupla)
    # Aggiungi il nuovo elemento alla lista
    tupla_modificata.insert(0, f"id_{indice}")
    # Assegna la lista modificata alla tupla originale
    domande[indice] = tuple(tupla_modificata)

# Aggiungi id domande alle risposte
for indice, tupla in enumerate(risposte):
    # Converti la tupla in una lista per poterla modificare
    tupla_modificata = list(tupla)

    for indice_domanda, tupla_domanda in enumerate(domande):
        if tupla_domanda[1] == tupla[0]:
            # Aggiungi il nuovo elemento alla lista
            tupla_modificata.insert(0, tupla_domanda[0])
            break

    # Assegna la lista modificata alla tupla originale
    risposte[indice] = tuple(tupla_modificata)

# Aggiungi id domande alle risposte
for indice, tupla in enumerate(risposte_docente):
    # Converti la tupla in una lista per poterla modificare
    tupla_modificata = list(tupla)

    for indice_domanda, tupla_domanda in enumerate(domande):
        if tupla_domanda[1] == tupla[0]:
            # Aggiungi il nuovo elemento alla lista
            tupla_modificata.insert(0, tupla_domanda[0])
            break

    # Assegna la lista modificata alla tupla originale
    risposte_docente[indice] = tuple(tupla_modificata)

# Aggiungi id domande alle risposte
for indice, tupla in enumerate(risposte_test):
    # Converti la tupla in una lista per poterla modificare
    tupla_modificata = list(tupla)

    for indice_domanda, tupla_domanda in enumerate(domande):
        if tupla_domanda[1] == tupla[0]:
            # Aggiungi il nuovo elemento alla lista
            tupla_modificata.insert(0, tupla_domanda[0])
            break

    # Assegna la lista modificata alla tupla originale
    risposte_test[indice] = tuple(tupla_modificata)

# Creazione del DataFrame
df_domande = pd.DataFrame(domande, columns=['id', 'text', 'label', 'id_docente'])
df_risposte = pd.DataFrame(risposte, columns=['id_domanda', 'title', 'id_docente', 'text', 'label'])
df_risposte_docente = pd.DataFrame(risposte_docente, columns=['id_domanda', 'title', 'text', 'id_docente'])
df_risposte_test = pd.DataFrame(risposte_test, columns=['id_domanda', 'title', 'id_docente', 'text', 'label'])

# Salvataggio del DataFrame come CSV
training_data_folder_path = Path("./training_data")
training_data_folder_path.mkdir(parents=True, exist_ok=True)

csv_domande_file_path = os.path.join(training_data_folder_path, "domande_archeologia_storia_arte.csv")
df_domande.to_csv(csv_domande_file_path, index=False)

csv_risposte_file_path = os.path.join(training_data_folder_path, "risposte_archeologia_storia_arte.csv")
df_risposte.to_csv(csv_risposte_file_path, index=False)

csv_risposte_docente_file_path = os.path.join(training_data_folder_path, "risposte_docente_archeologia_storia_arte.csv")
df_risposte_docente.to_csv(csv_risposte_docente_file_path, index=False)

csv_risposte_test_file_path = os.path.join(training_data_folder_path, "risposte_test.csv")
df_risposte_test.to_csv(csv_risposte_test_file_path, index=False)
