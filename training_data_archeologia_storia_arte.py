import os.path
from pathlib import Path

import pandas as pd

# Definizione delle domande e delle etichette
domande = [
    ("Quali sono le caratteristiche principali dell'arte egizia?", "Arte Egizia"),
    ("Come si sono evolute le tecniche di costruzione nel periodo romano?", "Architettura Romana"),
    ("Qual è l'importanza di Pompei per la comprensione della vita quotidiana nell'antica Roma?", "Vita Quotidiana Romana"),
    ("In che modo l'arte greca ha influenzato quella romana?", "Influenza Greca nell'Arte Romana"),
    ("Quali scoperte archeologiche hanno cambiato la nostra comprensione della preistoria?", "Scoperte Preistoriche"),
    ("Come viene utilizzata la datazione al carbonio-14 in archeologia?", "Datazione al Carbonio-14"),
    ("Quali sono le differenze tra l'arte paleocristiana e quella bizantina?", "Arte Paleocristiana vs Bizantina"),
    ("Che ruolo ha avuto l'acquedotto nell'antica civiltà romana?", "Acquedotti Romani"),
    ("Come interpretare le pitture rupestri del Paleolitico?", "Pitture Rupestri Paleolitiche"),
    ("Quali sono stati gli impatti del Rinascimento sulla società europea?", "Impatti del Rinascimento"),
    ("Cosa distingue l'architettura gotica da quella romanica?", "Architettura Gotica vs Romanica"),
    ("In che modo gli scavi di Ercolano hanno contribuito alla nostra conoscenza dell'antichità?", "Scavi di Ercolano"),
    ("Quali tecniche artistiche sono state utilizzate nell'antico Egitto per la realizzazione dei sarcofagi?", "Tecniche Artistiche Egizie"),
    ("Come viene definito il periodo dell'arte barocca e quali sono le sue caratteristiche principali?", "Arte Barocca"),
    ("Qual è il significato dei megaliti di Stonehenge?", "Stonehenge"),
    ("Quali fattori hanno contribuito al declino dell'Impero Romano?", "Declino dell'Impero Romano"),
    ("In che modo la ceramica fornisce informazioni sugli antichi popoli?", "Ceramica Antica"),
    ("Come influenzava la religione l'arte nell'antico Egitto?", "Religione e Arte Egizia"),
    ("Quali sono le principali differenze tra l'arte del Rinascimento e quella del Medioevo?", "Rinascimento vs Medioevo"),
    ("Come venivano realizzati i mosaici bizantini e quale era il loro scopo?", "Mosaici Bizantini"),
    ("In che modo la scoperta di Troia ha influenzato la comprensione dell'Iliade di Omero?", "Scoperta di Troia"),
    ("Quali erano le principali funzioni dei castelli medievali?", "Castelli Medievali"),
    ("Come si distinguono le varie fasi dell'arte greca antica?", "Fasi dell'Arte Greca"),
    ("Quali tecniche venivano utilizzate per la fusione del bronzo nella statuaria greca?", "Fusione del Bronzo nella Statuaria Greca"),
    ("Quali sono stati i principali centri culturali dell'arte rinascimentale?", "Centri Culturali del Rinascimento"),
    ("In che modo l'analisi dei pigmenti aiuta a comprendere le tecniche pittoriche antiche?", "Analisi dei Pigmenti"),
    ("Qual è stata l'importanza degli scavi di Mycenae per la comprensione della civiltà micenea?", "Scavi di Mycenae"),
    ("Come si differenziano le tombe etrusche da quelle romane?", "Tombe Etrusche vs Romane"),
    ("In che modo l'arte romana rifletteva la società e i valori dell'epoca?", "Arte Romana e Società"),
    ("Quali sono le principali caratteristiche dell'architettura mesopotamica?", "Architettura Mesopotamica"),
    ("Come veniva rappresentata la figura umana nell'arte cicladica?", "Arte Cicladica"),
    ("Quali sono le principali fonti per lo studio della storia dell'arte dell'antica Grecia?", "Fonti Storiche dell'Arte Greca"),
    ("Quali erano le funzioni sociali e religiose dell'arte nella società Maya?", "Arte Maya"),
    ("In che modo le armi e gli strumenti vengono utilizzati per datare i siti archeologici?", "Datazione dei Siti Archeologici"),
    ("Qual è il significato simbolico dei colori nell'arte egizia?", "Simbolismo dei Colori nell'Arte Egizia"),
    ("Come l'uso dei materiali influenzava lo stile artistico nell'antichità?", "Materiali e Stile Artistico Antico"),
    ("Quali sono le principali differenze tra l'architettura classica e quella neoclassica?", "Classica vs Neoclassica"),
    ("Come venivano selezionati e utilizzati i siti per la costruzione dei templi greci?", "Costruzione dei Templi Greci"),
    ("Qual è stato l'impatto dell'invenzione della stampa sull'arte e sulla cultura?", "Invenzione della Stampa"),
    ("Come venivano realizzate e utilizzate le monete nell'antica Roma?", "Monete nell'Antica Roma"),
    ("Qual è l'importanza dei ritrovamenti di Akrotiri per la comprensione della civiltà minoica?", "Ritrovamenti di Akrotiri"),
    ("In che modo l'arte e l'architettura riflettono il potere e la religione nell'Impero Bizantino?", "Arte e Architettura Bizantina"),
    ("Come l'analisi del DNA sta cambiando la nostra comprensione delle migrazioni antiche?", "Analisi del DNA e Migrazioni Antiche"),
    ("Quali tecniche di conservazione sono utilizzate per preservare le opere d'arte antiche?", "Tecniche di Conservazione"),
    ("In che modo l'arte dell'antico Egitto è stata influenzata dalla sua geografia?", "Influenza della Geografia sull'Arte Egizia"),
    ("Quali erano le principali tecniche di scultura utilizzate nella Grecia antica?", "Tecniche di Scultura nella Grecia Antica"),
    ("Come si sono sviluppate le città-stato nella Grecia antica e quale era il loro ruolo nella società?", "Città-Stato nella Grecia Antica"),
    ("Quali fattori hanno influenzato lo sviluppo dell'architettura gotica?", "Sviluppo dell'Architettura Gotica"),
    ("In che modo gli affreschi di Pompei ci forniscono informazioni sulla vita e l'arte dell'epoca?", "Affreschi di Pompei"),
    ("Quali sono le principali caratteristiche delle sculture dell'arte romanica?", "Sculture dell'Arte Romanica"),
    ("Come l'arte ha influenzato la politica nell'antica Grecia?", "Arte e Politica nell'Antica Grecia"),
    ("Quali sono le tecniche di navigazione e mappatura utilizzate dalle antiche civiltà marinare?", "Navigazione e Mappatura Antiche"),
    ("Come l'arte rupestre può essere interpretata per comprendere le culture preistoriche?", "Interpretazione dell'Arte Rupestre"),
    ("Quali sono state le influenze culturali sull'arte della Mesopotamia?", "Influenze Culturali sull'Arte Mesopotamica"),
    ("In che modo le tecniche di restauro moderne possono influenzare la percezione delle opere d'arte antiche?", "Tecniche di Restauro Moderne"),
    ("Qual è stata l'importanza della Via della Seta per lo scambio culturale e artistico?", "Importanza della Via della Seta")
]

domande += [
    ("Quale innovazione nell'architettura romana ha permesso la costruzione di grandi spazi interni coperti?", "Architettura Romana"),
    ("Qual è una differenza principale tra l'arte classica greco-romana e quella neoclassica?", "Classica vs Neoclassica"),
    ("Quale metodo di datazione è comunemente utilizzato per determinare l'età di siti archeologici antichi?", "Datazione dei Siti Archeologici"),
    ("Qual è stata una delle cause principali del declino dell'Impero Romano d'Occidente?", "Declino dell'Impero Romano"),
    ("Qual era la tecnica predominante utilizzata dai Greci antichi per la fusione delle statue in bronzo?", "Fusione del Bronzo nella Statuaria Greca"),
    ("Qual era la principale funzione delle monete nell'antica Roma?", "Monete nell'Antica Roma"),
    ("Chi è accreditato per la scoperta del sito archeologico di Troia?", "Scoperta di Troia")
]

risposte = [
    (
        "Quali sono le caratteristiche principali dell'arte egizia?",
        "L'arte egizia è nota per le sue grandi costruzioni come piramidi e templi, l'uso di geroglifici e rappresentazioni stilizzate di figure umane e divinità, spesso con proporzioni canoniche e postura frontale.",
        "Corretta",
    ),
    (
        "Quali sono le caratteristiche principali dell'arte egizia?",
        "L'arte egizia è principalmente famosa per i suoi dipinti astratti e l'uso prevalente del ferro nelle sculture.",
        "Sbagliata",
    ),
    (
        "Come si sono evolute le tecniche di costruzione nel periodo romano?",
        "Le tecniche di costruzione romane hanno visto significativi progressi con l'introduzione del calcestruzzo, permettendo la creazione di strutture innovative come le cupole e gli acquedotti, che hanno migliorato l'architettura e l'ingegneria civile.",
        "Corretta",
    ),
    (
        "Come si sono evolute le tecniche di costruzione nel periodo romano?",
        "Le tecniche di costruzione romane sono rimaste invariate dal periodo greco, focalizzandosi esclusivamente su elementi decorativi piuttosto che su innovazioni strutturali.",
        "Sbagliata",
    ),
    (
        "Qual è l'importanza di Pompei per la comprensione della vita quotidiana nell'antica Roma?",
        "Pompei offre uno sguardo senza precedenti sulla vita quotidiana degli antichi Romani, grazie alla conservazione di edifici, affreschi e artefatti quotidiani, offrendo preziose informazioni sulle abitudini, la cultura e la società dell'epoca.",
        "Corretta",
    ),
    (
        "Qual è l'importanza di Pompei per la comprensione della vita quotidiana nell'antica Roma?",
        "Pompei è rilevante principalmente per le sue rovine architettoniche che dimostrano l'uso avanzato del marmo, ignorando il contesto storico e sociale degli abitanti.",
        "Sbagliata",
    ),
    (
        "In che modo l'arte greca ha influenzato quella romana?",
        "L'arte greca ha fortemente influenzato quella romana attraverso l'adozione di stili, tecniche e temi, come la rappresentazione del corpo umano e la mitologia, che i Romani hanno integrato e adattato alle loro esigenze culturali e politiche.",
        "Corretta",
    ),
    (
        "In che modo l'arte greca ha influenzato quella romana?",
        "L'arte romana ha rigettato completamente l'influenza greca, sviluppando uno stile completamente indipendente focalizzato esclusivamente su temi astratti e geometrici.",
        "Sbagliata",
    ),
    (
        "Quali scoperte archeologiche hanno cambiato la nostra comprensione della preistoria?",
        "La scoperta di siti come Lascaux in Francia e Altamira in Spagna, con le loro pitture rupestri, ha rivoluzionato la nostra comprensione dell'espressione artistica e culturale delle società preistoriche.",
        "Corretta",
    ),
    (
        "Quali scoperte archeologiche hanno cambiato la nostra comprensione della preistoria?",
        "La scoperta delle piramidi egizie ha cambiato la nostra comprensione della preistoria, dimostrando che le società antiche erano esclusivamente focalizzate sulla costruzione di monumenti funerari.",
        "Sbagliata",
    ),
    (
        "Come viene utilizzata la datazione al carbonio-14 in archeologia?",
        "La datazione al carbonio-14 è utilizzata per determinare l'età di materiali organici fino a circa 50.000 anni fa, fornendo una cronologia accurata per il sito o l'oggetto studiato.",
        "Corretta",
    ),
    (
        "Come viene utilizzata la datazione al carbonio-14 in archeologia?",
        "La datazione al carbonio-14 viene utilizzata per determinare l'origine geografica degli oggetti antichi, identificando i luoghi esatti da cui provengono.",
        "Sbagliata",
    ),
    (
        "Quali sono le differenze tra l'arte paleocristiana e quella bizantina?",
        "L'arte paleocristiana si concentra su simboli semplici e narrazioni bibliche in catacombe e altri luoghi di culto, mentre l'arte bizantina sviluppa uno stile più raffinato con l'uso di mosaici dorati, icone e una maggiore enfasi sulla spiritualità.",
        "Corretta",
    ),
    (
        "Quali sono le differenze tra l'arte paleocristiana e quella bizantina?",
        "Non esistono differenze significative tra l'arte paleocristiana e quella bizantina; entrambe condividono gli stessi temi e tecniche senza variazioni nel tempo.",
        "Sbagliata",
    ),
    (
        "Che ruolo ha avuto l'acquedotto nell'antica civiltà romana?",
        "Gli acquedotti hanno permesso il trasporto di acqua pulita nelle città, migliorando notevolmente la salute pubblica e sostenendo la crescita urbana.",
        "Corretta",
    ),
    (
        "Che ruolo ha avuto l'acquedotto nell'antica civiltà romana?",
        "Gli acquedotti erano puramente decorativi, utilizzati come simboli di status senza una funzione pratica.",
        "Sbagliata",
    ),
    (
        "Come interpretare le pitture rupestri del Paleolitico?",
        "Le pitture rupestri del Paleolitico sono interpretate come espressioni culturali che rappresentano la vita quotidiana, le credenze religiose e le conoscenze astronomiche delle società preistoriche.",
        "Corretta",
    ),
    (
        "Come interpretare le pitture rupestri del Paleolitico?",
        "Le pitture rupestri del Paleolitico sono semplici decorazioni senza significato, realizzate per passare il tempo.",
        "Sbagliata",
    ),
    (
        "Quali sono stati gli impatti del Rinascimento sulla società europea?",
        "Il Rinascimento ha promosso il rinascere dell'interesse per le arti, la scienza e l'umanesimo, influenzando profondamente la cultura, la politica e la religione in Europa.",
        "Corretta",
    ),
    (
        "Quali sono stati gli impatti del Rinascimento sulla società europea?",
        "Il Rinascimento ha avuto poco impatto sulla società europea, rimanendo un fenomeno isolato senza influenze culturali o scientifiche.",
        "Sbagliata",
    ),
    (
        "Cosa distingue l'architettura gotica da quella romanica?",
        "L'architettura gotica si distingue per l'uso di arcate a sesto acuto, volta a crociera e supporti snelli come i contrafforti volanti, rispetto alla massiccia semplicità e alle cupole semicircolari del romanico.",
        "Corretta",
    ),
    (
        "Cosa distingue l'architettura gotica da quella romanica?",
        "L'architettura gotica e quella romanica non presentano differenze significative, condividendo gli stessi elementi stilistici e strutturali.",
        "Sbagliata",
    ),
    (
        "In che modo gli scavi di Ercolano hanno contribuito alla nostra conoscenza dell'antichità?",
        "Gli scavi di Ercolano hanno fornito preziose informazioni sulla vita quotidiana romana, preservando edifici e oggetti coperti dalla cenere vulcanica, simili a Pompei ma meglio conservati.",
        "Corretta",
    ),
    (
        "In che modo gli scavi di Ercolano hanno contribuito alla nostra conoscenza dell'antichità?",
        "Gli scavi di Ercolano non hanno offerto nuove informazioni sull'antichità, essendo una replica moderna di una città antica.",
        "Sbagliata",
    ),
    (
        "Quali tecniche artistiche sono state utilizzate nell'antico Egitto per la realizzazione dei sarcofagi?",
        "Nell'antico Egitto, i sarcofagi erano realizzati con legno o pietra e decorati con pitture e incisioni che rappresentavano testi funerari e scene della vita dopo la morte, utilizzando tecniche avanzate di lavorazione.",
        "Corretta",
    ),
    (
        "Quali tecniche artistiche sono state utilizzate nell'antico Egitto per la realizzazione dei sarcofagi?",
        "I sarcofagi egizi erano semplicemente scavati nel terreno senza alcuna decorazione o tecnica artistica, riflettendo pratiche di sepoltura primitive.",
        "Sbagliata",
    ),
    (
        "Come viene definito il periodo dell'arte barocca e quali sono le sue caratteristiche principali?",
        "Il periodo barocco è definito dal dinamismo, dall'esuberanza e dalla ricchezza decorativa, caratterizzato dall'uso di contrasti forti, movimento, espressioni drammatiche e una tendenza verso la grandiosità in tutte le forme d'arte.",
        "Corretta",
    ),
    (
        "Come viene definito il periodo dell'arte barocca e quali sono le sue caratteristiche principali?",
        "Il barocco si concentra principalmente sull'astrazione e la semplicità delle forme, preferendo linee pulite e un approccio minimalista all'arte.",
        "Sbagliata",
    ),
    (
        "Qual è il significato dei megaliti di Stonehenge?",
        "Stonehenge è generalmente interpretato come un complesso preistorico usato per osservazioni astronomiche, cerimonie religiose o pratiche sociali rituali.",
        "Corretta",
    ),
    (
        "Qual è il significato dei megaliti di Stonehenge?",
        "Stonehenge era un antico mercato per il commercio locale, dove le persone si incontravano per scambiare beni e servizi.",
        "Sbagliata",
    ),
    (
        "Quali fattori hanno contribuito al declino dell'Impero Romano?",
        "Il declino dell'Impero Romano è stato causato da una combinazione di fattori interni come la corruzione, l'instabilità politica, l'eccessiva espansione e pressioni esterne da parte dei popoli barbarici.",
        "Corretta",
    ),
    (
        "Quali fattori hanno contribuito al declino dell'Impero Romano?",
        "Il declino è stato principalmente il risultato dell'invasione degli alieni, che hanno soverchiato le legioni romane con tecnologia superiore.",
        "Sbagliata",
    ),
    (
        "In che modo la ceramica fornisce informazioni sugli antichi popoli?",
        "La ceramica, con i suoi stili decorativi e le tecniche di produzione, offre preziose informazioni sulla vita quotidiana, le pratiche commerciali e le interazioni culturali degli antichi popoli.",
        "Corretta",
    ),
    (
        "In che modo la ceramica fornisce informazioni sugli antichi popoli?",
        "La ceramica antica è utile esclusivamente per determinare i livelli di consumo di tè e caffè nelle antiche civiltà.",
        "Sbagliata",
    ),
    (
        "Come influenzava la religione l'arte nell'antico Egitto?",
        "Nell'antico Egitto, la religione aveva un profondo impatto sull'arte, che era prevalentemente usata per scopi funerari o di culto, rappresentando divinità, riti religiosi e credenze nell'aldilà.",
        "Corretta",
    ),
    (
        "Come influenzava la religione l'arte nell'antico Egitto?",
        "L'arte egizia era completamente laica e non era influenzata in alcun modo dalle pratiche religiose o spirituali dell'epoca.",
        "Sbagliata",
    ),
    (
        "Quali sono le principali differenze tra l'arte del Rinascimento e quella del Medioevo?",
        "L'arte del Rinascimento segna un ritorno all'antichità classica, con un focus su prospettiva, anatomia umana e naturalismo, a differenza dell'arte medievale che era più orientata verso il simbolismo religioso e uno stile più stilizzato e astratto.",
        "Corretta",
    ),
    (
        "Quali sono le principali differenze tra l'arte del Rinascimento e quella del Medioevo?",
        "Non ci sono differenze significative; l'arte del Rinascimento e quella medievale possono essere considerate strettamente intercambiabili in termini di stile e soggetto.",
        "Sbagliata",
    ),
    (
        "Come venivano realizzati i mosaici bizantini e quale era il loro scopo?",
        "I mosaici bizantini erano realizzati con piccoli pezzi di vetro o pietra, detti tessere, per creare immagini elaborate con scopi decorativi e religiosi, spesso utilizzati nelle chiese per raccontare storie bibliche.",
        "Corretta",
    ),
    (
        "Come venivano realizzati i mosaici bizantini e quale era il loro scopo?",
        "I mosaici bizantini erano principalmente disegni astratti usati per pavimentare le strade e non avevano significato o scopo oltre a quello pratico.",
        "Sbagliata",
    ),
    (
        "In che modo la scoperta di Troia ha influenzato la comprensione dell'Iliade di Omero?",
        "La scoperta archeologica di Troia ha fornito una base storica all'Iliade di Omero, suggerendo che gli eventi descritti, sebbene mitologizzati, potrebbero avere un fondamento nella realtà.",
        "Corretta",
    ),
    (
        "In che modo la scoperta di Troia ha influenzato la comprensione dell'Iliade di Omero?",
        "La scoperta di Troia ha dimostrato inequivocabilmente che l'Iliade era un resoconto accurato e dettagliato di eventi storici senza alcuna esagerazione o elemento mitologico.",
        "Sbagliata",
    ),
    (
        "Quali erano le principali funzioni dei castelli medievali?",
        "I castelli medievali servivano come centri di amministrazione locale, residenze nobiliari e soprattutto come strutture difensive durante i periodi di conflitto.",
        "Corretta",
    ),
    (
        "Quali erano le principali funzioni dei castelli medievali?",
        "I castelli medievali erano utilizzati esclusivamente come attrazioni turistiche per intrattenere la nobiltà, senza alcuna funzione pratica o militare.",
        "Sbagliata",
    ),
    (
        "Come si distinguono le varie fasi dell'arte greca antica?",
        "Le fasi dell'arte greca antica si distinguono in arcaica, classica ed ellenistica, ognuna caratterizzata da specifici stili artistici, tecniche scultoree e temi rappresentativi.",
        "Corretta",
    ),
    (
        "Come si distinguono le varie fasi dell'arte greca antica?",
        "L'arte greca antica è stata uniforme nel corso dei secoli, senza distinzioni o sviluppi significativi tra le varie fasi.",
        "Sbagliata",
    ),
    (
        "Quali tecniche venivano utilizzate per la fusione del bronzo nella statuaria greca?",
        "La statuaria greca utilizzava la tecnica della fusione a cera persa per creare sculture in bronzo dettagliate e realistiche, permettendo grande precisione nei dettagli.",
        "Corretta",
    ),
    (
        "Quali tecniche venivano utilizzate per la fusione del bronzo nella statuaria greca?",
        "Le sculture in bronzo greche erano create assemblando pezzi prefabbricati senza uso di tecniche di fusione, risultando in opere spesso grezze e poco dettagliate.",
        "Sbagliata",
    ),
    (
        "Quali sono stati i principali centri culturali dell'arte rinascimentale?",
        "Firenze, Roma, e Venezia sono stati tra i principali centri culturali dell'arte rinascimentale, fungendo da fucine per l'innovazione artistica e la rinascita degli ideali classici.",
        "Corretta",
    ),
    (
        "Quali sono stati i principali centri culturali dell'arte rinascimentale?",
        "I principali centri culturali dell'arte rinascimentale erano situati nell'Europa settentrionale, con Londra e Parigi che guidavano il movimento artistico.",
        "Sbagliata",
    ),
    (
        "In che modo l'analisi dei pigmenti aiuta a comprendere le tecniche pittoriche antiche?",
        "L'analisi dei pigmenti permette di identificare i materiali utilizzati dagli artisti, fornendo informazioni sulle tecniche pittoriche, le pratiche di atelier e le rotte commerciali degli antichi.",
        "Corretta",
    ),
    (
        "In che modo l'analisi dei pigmenti aiuta a comprendere le tecniche pittoriche antiche?",
        "L'analisi dei pigmenti è utile esclusivamente per determinare l'età di un'opera d'arte, senza fornire alcuna informazione sulle tecniche pittoriche utilizzate.",
        "Sbagliata",
    ),
    (
        "Qual è stata l'importanza degli scavi di Mycenae per la comprensione della civiltà micenea?",
        "Gli scavi di Mycenae hanno rivelato ricchezze architettoniche e artefatti che illustrano la potenza e la complessità della civiltà micenea, confermando le descrizioni di Omero.",
        "Corretta",
    ),
    (
        "Qual è stata l'importanza degli scavi di Mycenae per la comprensione della civiltà micenea?",
        "Gli scavi di Mycenae hanno dimostrato che la civiltà micenea era principalmente nomade, con scarse prove di insediamenti permanenti o strutture complesse.",
        "Sbagliata",
    ),
    (
        "Come si differenziano le tombe etrusche da quelle romane?",
        "Le tombe etrusche erano spesso elaborate camere sotterranee con affreschi vivaci, mentre le tombe romane tendevano a essere più austere e meno decorate, riflettendo diverse pratiche e credenze funerarie.",
        "Corretta",
    ),
    (
        "Come si differenziano le tombe etrusche da quelle romane?",
        "Le tombe etrusche e romane non differivano significativamente, poiché entrambe le culture preferivano la cremazione alla sepoltura.",
        "Sbagliata",
    ),
    (
        "In che modo l'arte romana rifletteva la società e i valori dell'epoca?",
        "L'arte romana rifletteva la società e i valori dell'epoca attraverso la rappresentazione di temi legati al potere, all'autorità, agli dei e alla vita quotidiana, servendo come mezzo per la propaganda politica e l'espressione religiosa.",
        "Corretta",
    ),
    (
        "In che modo l'arte romana rifletteva la società e i valori dell'epoca?",
        "L'arte romana era completamente astratta, evitando qualsiasi rappresentazione della società o dei valori dell'epoca, concentrata invece su forme geometriche pure.",
        "Sbagliata",
    ),
    (
        "Quali sono le principali caratteristiche dell'architettura mesopotamica?",
        "Le principali caratteristiche dell'architettura mesopotamica includono l'uso di mattoni d'argilla, la costruzione di ziggurat come centri religiosi e la creazione di città-stato fortificate.",
        "Corretta",
    ),
    (
        "Quali sono le principali caratteristiche dell'architettura mesopotamica?",
        "L'architettura mesopotamica è nota per l'uso estensivo del marmo e per le sue strutture mobili, che potevano essere facilmente spostate.",
        "Sbagliata",
    ),
    (
        "Come veniva rappresentata la figura umana nell'arte cicladica?",
        "Nell'arte cicladica, la figura umana era rappresentata in forma stilizzata e schematica, con enfasi sulla simmetria e le proporzioni geometriche, spesso con braccia incrociate e volti privi di espressione.",
        "Corretta",
    ),
    (
        "Come veniva rappresentata la figura umana nell'arte cicladica?",
        "La figura umana nell'arte cicladica era estremamente realistica e dettagliata, con un'enfasi sul realismo anatomico simile a quello dell'arte rinascimentale.",
        "Sbagliata",
    ),
    (
        "Quali sono le principali fonti per lo studio della storia dell'arte dell'antica Grecia?",
        "Le principali fonti per lo studio dell'arte greca antica includono opere d'arte sopravvissute come sculture, vasi, edifici e affreschi, nonché testi antichi di autori come Pausania e Plinio il Vecchio.",
        "Corretta",
    ),
    (
        "Quali sono le principali fonti per lo studio della storia dell'arte dell'antica Grecia?",
        "Le uniche fonti per lo studio dell'arte greca antica sono le rappresentazioni moderne e le ricostruzioni basate su interpretazioni artistiche contemporanee.",
        "Sbagliata",
    ),
    (
        "Quali erano le funzioni sociali e religiose dell'arte nella società Maya?",
        "Nella società Maya, l'arte aveva funzioni sociali e religiose significative, servendo come mezzo per documentare eventi storici, esprimere credenze cosmologiche e celebrare l'élite al potere.",
        "Corretta",
    ),
    (
        "Quali erano le funzioni sociali e religiose dell'arte nella società Maya?",
        "Nella società Maya, l'arte era puramente decorativa, senza alcuna funzione sociale o religiosa, e veniva usata solo per abbellire gli ambienti abitativi.",
        "Sbagliata",
    ),
    (
        "In che modo le armi e gli strumenti vengono utilizzati per datare i siti archeologici?",
        "Le armi e gli strumenti sono utilizzati per datare i siti archeologici attraverso la tipologia e la tecnologia di produzione, che possono indicare specifici periodi storici e culturali.",
        "Corretta",
    ),
    (
        "In che modo le armi e gli strumenti vengono utilizzati per datare i siti archeologici?",
        "Le armi e gli strumenti antichi sono irrilevanti per la datazione dei siti archeologici, poiché non variano significativamente nel tempo.",
        "Sbagliata",
    ),
    (
        "Qual è il significato simbolico dei colori nell'arte egizia?",
        "Nell'arte egizia, i colori avevano significati simbolici profondi, come il verde per la rinascita, il rosso per il caos o la distruzione, e il nero per la fertilità e la rigenerazione.",
        "Corretta",
    ),
    (
        "Qual è il significato simbolico dei colori nell'arte egizia?",
        "I colori nell'arte egizia erano scelti casualmente, senza alcun significato simbolico o culturale.",
        "Sbagliata",
    ),
    (
        "Come l'uso dei materiali influenzava lo stile artistico nell'antichità?",
        "L'uso di materiali come il marmo, il bronzo o l'argilla influenzava notevolmente lo stile artistico, determinando la tecnica, la forma e la durabilità dell'opera artistica.",
        "Corretta",
    ),
    (
        "Come l'uso dei materiali influenzava lo stile artistico nell'antichità?",
        "L'uso dei materiali aveva un impatto minimo sullo stile artistico nell'antichità, con gli artisti che privilegiavano l'espressione personale rispetto alle proprietà dei materiali.",
        "Sbagliata",
    ),
    (
        "Quali sono le principali differenze tra l'architettura classica e quella neoclassica?",
        "L'architettura classica si riferisce all'arte dell'antica Grecia e Roma, con l'uso di colonne doriche, ioniche e corinzie, mentre il neoclassicismo è una rivisitazione di questi stili nell'epoca moderna, enfatizzando la semplicità e la grandiosità.",
        "Corretta",
    ),
    (
        "Quali sono le principali differenze tra l'architettura classica e quella neoclassica?",
        "Non ci sono differenze tra l'architettura classica e quella neoclassica; il termine 'neoclassico' è semplicemente un altro modo per descrivere l'architettura greca e romana.",
        "Sbagliata",
    ),
    (
        "Come venivano selezionati e utilizzati i siti per la costruzione dei templi greci?",
        "I siti per i templi greci erano spesso scelti per il loro significato religioso o per la loro posizione prominente, come le alture, per dominare il paesaggio circostante.",
        "Corretta",
    ),
    (
        "Come venivano selezionati e utilizzati i siti per la costruzione dei templi greci?",
        "I siti per i templi greci erano selezionati casualmente, senza particolare considerazione per la posizione o il significato.",
        "Sbagliata",
    ),
    (
        "Qual è stato l'impatto dell'invenzione della stampa sull'arte e sulla cultura?",
        "L'invenzione della stampa ha rivoluzionato l'arte e la cultura facilitando la diffusione delle conoscenze, rendendo i libri più accessibili e promuovendo l'alfabetizzazione e la diffusione delle idee rinascimentali.",
        "Corretta",
    ),
    (
        "Qual è stato l'impatto dell'invenzione della stampa sull'arte e sulla cultura?",
        "L'invenzione della stampa ha avuto poco impatto sull'arte e sulla cultura, rimanendo una curiosità tecnologica con scarse applicazioni pratiche.",
        "Sbagliata",
    ),
    (
        "Come venivano realizzate e utilizzate le monete nell'antica Roma?",
        "Nell'antica Roma, le monete erano coniate in metallo prezioso e servivano come mezzo di scambio, standard di valore e strumento di propaganda politica, mostrando ritratti di imperatori o divinità.",
        "Corretta",
    ),
    (
        "Come venivano realizzate e utilizzate le monete nell'antica Roma?",
        "Le monete nell'antica Roma erano principalmente di carta e usate solo per giochi e divertimenti, senza valore reale come moneta.",
        "Sbagliata",
    ),
    (
        "Qual è l'importanza dei ritrovamenti di Akrotiri per la comprensione della civiltà minoica?",
        "I ritrovamenti di Akrotiri, con i suoi affreschi ben conservati e avanzate strutture urbane, offrono una visione unica sulla vita quotidiana, l'arte e l'architettura della civiltà minoica.",
        "Corretta",
    ),
    (
        "Qual è l'importanza dei ritrovamenti di Akrotiri per la comprensione della civiltà minoica?",
        "Akrotiri è irrilevante per la comprensione della civiltà minoica, essendo un sito isolato che non riflette la cultura o le pratiche di quel popolo.",
        "Sbagliata",
    ),
    (
        "In che modo l'arte e l'architettura riflettono il potere e la religione nell'Impero Bizantino?",
        "Nell'Impero Bizantino, l'arte e l'architettura riflettevano il potere e la religione attraverso la costruzione di imponenti chiese e mosaici che esprimevano la divinità dell'imperatore e la centralità del cristianesimo.",
        "Corretta",
    ),
    (
        "In che modo l'arte e l'architettura riflettono il potere e la religione nell'Impero Bizantino?",
        "L'arte e l'architettura bizantine erano completamente secolari, evitando qualsiasi riferimento al potere imperiale o alla religione.",
        "Sbagliata",
    ),
    (
        "Come l'analisi del DNA sta cambiando la nostra comprensione delle migrazioni antiche?",
        "L'analisi del DNA sta rivoluzionando la nostra comprensione delle migrazioni antiche, fornendo prove dirette dei movimenti dei popoli preistorici e delle loro interazioni genetiche con le popolazioni moderne.",
        "Corretta",
    ),
    (
        "Come l'analisi del DNA sta cambiando la nostra comprensione delle migrazioni antiche?",
        "L'analisi del DNA non ha contribuito significativamente alla nostra comprensione delle migrazioni antiche, rimanendo una tecnologia troppo imprecisa per fornire informazioni affidabili.",
        "Sbagliata",
    ),
    (
        "Quali tecniche di conservazione sono utilizzate per preservare le opere d'arte antiche?",
        "Per preservare le opere d'arte antiche, vengono utilizzate tecniche come la stabilizzazione ambientale, il restauro delicato e la digitalizzazione per prevenire ulteriori danni e perdite.",
        "Corretta",
    ),
    (
        "Quali tecniche di conservazione sono utilizzate per preservare le opere d'arte antiche?",
        "Le opere d'arte antiche sono spesso ricoperte di vernice trasparente per preservarle, una tecnica moderna che garantisce la loro durata nel tempo senza necessità di altri interventi.",
        "Sbagliata",
    ),
    (
        "In che modo l'arte dell'antico Egitto è stata influenzata dalla sua geografia?",
        "L'arte dell'antico Egitto è stata profondamente influenzata dalla geografia, in particolare dal Nilo, che ha portato a una forte enfasi sui temi della fertilità, della rinascita e dell'aldilà, riflettendo l'importanza del fiume per la sopravvivenza e la prosperità.",
        "Corretta",
    ),
    (
        "In che modo l'arte dell'antico Egitto è stata influenzata dalla sua geografia?",
        "La geografia dell'Egitto, essendo principalmente desertica, ha impedito lo sviluppo dell'arte e della cultura, limitando le espressioni artistiche a semplici disegni rupestri.",
        "Sbagliata",
    ),
    (
        "Quali erano le principali tecniche di scultura utilizzate nella Grecia antica?",
        "Le tecniche di scultura nella Grecia antica includevano la lavorazione del marmo e del bronzo, con l'uso della tecnica della cera persa per le sculture in bronzo, che permetteva una maggiore dettagliatezza e realismo.",
        "Corretta",
    ),
    (
        "Quali erano le principali tecniche di scultura utilizzate nella Grecia antica?",
        "Le sculture greche antiche erano principalmente fatte di legno e argilla, senza l'uso di tecniche avanzate, risultando in opere d'arte grossolane e poco dettagliate.",
        "Sbagliata",
    ),
    (
        "Come si sono sviluppate le città-stato nella Grecia antica e quale era il loro ruolo nella società?",
        "Le città-stato della Grecia antica, o polis, erano centri indipendenti di attività politica, economica e culturale, che giocavano un ruolo cruciale nel promuovere lo sviluppo della democrazia, dell'arte e della filosofia.",
        "Corretta",
    ),
    (
        "Come si sono sviluppate le città-stato nella Grecia antica e quale era il loro ruolo nella società?",
        "Le città-stato nella Grecia antica erano meramente simboliche e non avevano alcuna influenza reale sulla società o sullo sviluppo culturale dell'epoca.",
        "Sbagliata",
    ),
    (
        "Quali fattori hanno influenzato lo sviluppo dell'architettura gotica?",
        "Lo sviluppo dell'architettura gotica è stato influenzato da un desiderio di maggiore altezza e luce nelle strutture, portando all'introduzione di innovazioni come gli archi a sesto acuto, le volte a crociera e i contrafforti volanti.",
        "Corretta",
    ),
    (
        "Quali fattori hanno influenzato lo sviluppo dell'architettura gotica?",
        "L'architettura gotica è stata influenzata principalmente dall'esigenza di costruire strutture che potessero resistere a condizioni meteorologiche estreme, come neve e ghiaccio.",
        "Sbagliata",
    ),
    (
        "In che modo gli affreschi di Pompei ci forniscono informazioni sulla vita e l'arte dell'epoca?",
        "Gli affreschi di Pompei forniscono una visione preziosa della vita quotidiana, delle mode, dei costumi e delle credenze degli antichi Romani, grazie alla loro straordinaria conservazione dopo l'eruzione del Vesuvio.",
        "Corretta",
    ),
    (
        "In che modo gli affreschi di Pompei ci forniscono informazioni sulla vita e l'arte dell'epoca?",
        "Gli affreschi di Pompei sono considerati irrilevanti per la comprensione della vita e dell'arte dell'epoca, in quanto si ritiene che rappresentino esclusivamente immaginazione artistica senza basi nella realtà.",
        "Sbagliata",
    ),
    (
        "Quali sono le principali caratteristiche delle sculture dell'arte romanica?",
        "Le sculture dell'arte romanica sono caratterizzate da un forte simbolismo religioso, forme stilizzate e un'espressione emotiva contenuta, spesso utilizzate come decorazione in chiese e cattedrali.",
        "Corretta",
    ),
    (
        "Quali sono le principali caratteristiche delle sculture dell'arte romanica?",
        "Le sculture dell'arte romanica erano note per la loro estrema fedeltà al realismo naturale e per la rappresentazione dettagliata di scene quotidiane, ignorando temi religiosi o simbolici.",
        "Sbagliata",
    ),
    (
        "Come l'arte ha influenzato la politica nell'antica Grecia?",
        "Nell'antica Grecia, l'arte era strettamente intrecciata con la politica, utilizzata per esaltare le virtù dei leader, celebrare le vittorie militari e esprimere ideali democratici, influenzando l'opinione pubblica e l'identità culturale.",
        "Corretta",
    ),
    (
        "Come l'arte ha influenzato la politica nell'antica Grecia?",
        "L'arte nell'antica Grecia aveva poco o nessun impatto sulla politica, rimanendo una sfera completamente separata senza influenzare le decisioni politiche o la società.",
        "Sbagliata",
    ),
    (
        "Quali sono le tecniche di navigazione e mappatura utilizzate dalle antiche civiltà marinare?",
        "Le antiche civiltà marinare utilizzavano l'astronomia per la navigazione, identificando stelle e costellazioni per orientarsi in mare, e creavano mappe rudimentali basate su osservazioni costiere e la direzione dei venti.",
        "Corretta",
    ),
    (
        "Quali sono le tecniche di navigazione e mappatura utilizzate dalle antiche civiltà marinare?",
        "Le antiche civiltà marinare si affidavano esclusivamente al caso per la navigazione, viaggiando senza mappe o tecniche di orientamento e sperando di raggiungere le loro destinazioni.",
        "Sbagliata",
    ),
    (
        "Come l'arte rupestre può essere interpretata per comprendere le culture preistoriche?",
        "L'arte rupestre è interpretata come una testimonianza diretta delle credenze, delle pratiche quotidiane e della vita spirituale delle culture preistoriche, offrendo indizi sul loro modo di vivere, sulla caccia, sui rituali e sulle divinità.",
        "Corretta",
    ),
    (
        "Come l'arte rupestre può essere interpretata per comprendere le culture preistoriche?",
        "L'arte rupestre era puramente decorativa, senza significato o scopo, utilizzata dalle culture preistoriche solo per abbellire i loro ambienti di vita.",
        "Sbagliata",
    ),
    (
        "Quali sono state le influenze culturali sull'arte della Mesopotamia?",
        "L'arte della Mesopotamia è stata influenzata da una varietà di culture circostanti, comprese le interazioni con gli antichi Egizi, Persiani e le culture delle steppe, risultando in uno scambio di tecniche artistiche e temi.",
        "Corretta",
    ),
    (
        "Quali sono state le influenze culturali sull'arte della Mesopotamia?",
        "L'arte della Mesopotamia era completamente isolata, senza alcuna influenza esterna o scambio culturale, riflettendo una società chiusa e autarchica.",
        "Sbagliata",
    ),
    (
        "In che modo le tecniche di restauro moderne possono influenzare la percezione delle opere d'arte antiche?",
        "Le tecniche di restauro moderne possono migliorare la percezione delle opere d'arte antiche, preservandole per le future generazioni e restituendo il loro aspetto originale, ma possono anche alterare la loro autenticità se non eseguite con cura.",
        "Corretta",
    ),
    (
        "In che modo le tecniche di restauro moderne possono influenzare la percezione delle opere d'arte antiche?",
        "Le tecniche di restauro moderne rendono le opere d'arte antiche indistinguibili dalle creazioni contemporanee, eliminando qualsiasi traccia del loro contesto storico originale.",
        "Sbagliata",
    ),
    (
        "Qual è stata l'importanza della Via della Seta per lo scambio culturale e artistico?",
        "La Via della Seta ha avuto un ruolo cruciale nello scambio culturale e artistico, permettendo la diffusione di idee, tecnologie, prodotti e arte tra l'Est e l'Ovest, arricchendo le società connesse da questa rete commerciale.",
        "Corretta",
    ),
    (
        "Qual è stata l'importanza della Via della Seta per lo scambio culturale e artistico?",
        "La Via della Seta era usata esclusivamente per il trasporto di seta e spezie, senza alcun impatto sullo scambio culturale o artistico tra le diverse regioni.",
        "Sbagliata",
    )
]

risposte += [
    (
        "Quale innovazione nell'architettura romana ha permesso la costruzione di grandi spazi interni coperti?",
        "L'introduzione dell'arco e della volta ha permesso ai Romani di costruire grandi spazi interni coperti, come terme, basiliche e anfiteatri.",
        "Corretta",
    ),
    (
        "Quale innovazione nell'architettura romana ha permesso la costruzione di grandi spazi interni coperti?",
        "L'uso esclusivo del marmo ha permesso ai Romani di costruire grandi spazi interni coperti.",
        "Sbagliata",
    ),
    (
        "Qual è una differenza principale tra l'arte classica greco-romana e quella neoclassica?",
        "L'arte neoclassica, risorgente nel XVIII secolo, enfatizza la razionalità e il ritorno ai principi dell'arte e dell'architettura classica, spesso come reazione contro il Barocco e il Rococò.",
        "Corretta",
    ),
    (
        "Qual è una differenza principale tra l'arte classica greco-romana e quella neoclassica?",
        "L'arte classica si concentra sull'uso di colori vivaci, mentre l'arte neoclassica utilizza esclusivamente il bianco e il nero.",
        "Sbagliata",
    ),
    (
        "Quale metodo di datazione è comunemente utilizzato per determinare l'età di siti archeologici antichi?",
        "La datazione al radiocarbonio (C-14) è comunemente utilizzata per determinare l'età di materiali organici nei siti archeologici fino a circa 50.000 anni fa.",
        "Corretta",
    ),
    (
        "Quale metodo di datazione è comunemente utilizzato per determinare l'età di siti archeologici antichi?",
        "La datazione con il metodo del litio è comunemente utilizzata per determinare l'età di siti archeologici.",
        "Sbagliata",
    ),
    (
        "Qual è stata una delle cause principali del declino dell'Impero Romano d'Occidente?",
        "Le invasioni barbariche furono una delle cause principali del declino dell'Impero Romano d'Occidente nel V secolo d.C.",
        "Corretta",
    ),
    (
        "Qual è stata una delle cause principali del declino dell'Impero Romano d'Occidente?",
        "L'invenzione della stampa accelerò il declino dell'Impero Romano d'Occidente.",
        "Sbagliata",
    ),
    (
        "Qual era la tecnica predominante utilizzata dai Greci antichi per la fusione delle statue in bronzo?",
        "La tecnica della cera persa era la metodologia predominante utilizzata per la fusione delle statue in bronzo nella Grecia antica.",
        "Corretta",
    ),
    (
        "Qual era la tecnica predominante utilizzata dai Greci antichi per la fusione delle statue in bronzo?",
        "La tecnica della fusione a freddo era la metodologia predominante utilizzata nella Grecia antica.",
        "Sbagliata",
    ),
    (
        "Qual era la principale funzione delle monete nell'antica Roma?",
        "Nell'antica Roma, le monete servivano principalmente come mezzo di scambio e come strumento per diffondere l'immagine e il messaggio politico dell'imperatore.",
        "Corretta",
    ),
    (
        "Qual era la principale funzione delle monete nell'antica Roma?",
        "Nell'antica Roma, le monete erano usate principalmente come decorazioni personali e simboli di status.",
        "Sbagliata",
    ),
    (
        "Chi è accreditato per la scoperta del sito archeologico di Troia?",
        "Heinrich Schliemann è accreditato per la scoperta del sito archeologico di Troia negli anni 1870.",
        "Corretta",
    ),
    (
        "Chi è accreditato per la scoperta del sito archeologico di Troia?",
        "Marco Polo è accreditato per la scoperta del sito archeologico di Troia nel XIII secolo.",
        "Sbagliata",
    ),
]

# Creazione del DataFrame
df_domande = pd.DataFrame(domande, columns=['text', 'label'])
df_risposte = pd.DataFrame(risposte, columns=['title', 'text', 'label'])

# Salvataggio del DataFrame come CSV
training_data_folder_path = Path("./training_data")
training_data_folder_path.mkdir(parents=True, exist_ok=True)

csv_domande_file_path = os.path.join(training_data_folder_path, "domande_archeologia_storia_arte.csv")
df_domande.to_csv(csv_domande_file_path, index=False)

csv_risposte_file_path = os.path.join(training_data_folder_path, "risposte_archeologia_storia_arte.csv")
df_risposte.to_csv(csv_risposte_file_path, index=False)
