import os

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from datasets import load_dataset
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')

# Frasi di esempio
corpus = [
    "Una ragazza si acconcia i capelli.",
    "Una ragazza si sta spazzolando i capelli.",
    "Il cane corre veloce nel parco.",
    "La pizza è il mio piatto preferito.",
    "Oggi è una giornata calda e soleggiata.",
    "La musica mi rilassa dopo una lunga giornata.",
    "Leggere un buon libro è un ottimo modo per rilassarsi.",
    "Mi piace fare lunghe passeggiate nella natura.",
    "Il mare ha un effetto calmante su di me.",
    "L'arte è una forma di espressione creativa.",
    "Mi piace cucinare piatti nuovi e sperimentare con ingredienti diversi.",
    "Lo yoga mi aiuta a mantenere la mente e il corpo in equilibrio.",
    "Viaggiare mi apre la mente e mi permette di scoprire nuove culture.",
    "Imparare una nuova lingua è una sfida stimolante.",
    "La tecnologia sta cambiando rapidamente il modo in cui viviamo.",
    "La sostenibilità ambientale è importante per il futuro del nostro pianeta.",
    "Il cambiamento climatico è una delle sfide più urgenti che dobbiamo affrontare.",
    "La politica è un argomento complesso che coinvolge molte questioni.",
    "La democrazia è un sistema di governo fondato sulla partecipazione dei cittadini.",
    "L'uguaglianza di genere è un obiettivo importante per raggiungere una società più giusta.",
    "L'istruzione è fondamentale per lo sviluppo individuale e sociale.",
    "La salute mentale è altrettanto importante quanto la salute fisica.",
    "L'esercizio fisico regolare contribuisce al benessere generale.",
    "Una dieta equilibrata è essenziale per una vita sana.",
    "La medicina moderna ha reso possibile la cura di molte malattie.",
    "La ricerca scientifica è fondamentale per il progresso della società.",
    "L'innovazione tecnologica ha trasformato molti aspetti della nostra vita quotidiana.",
    "Internet ha reso il mondo più connesso che mai.",
    "I social media hanno cambiato il modo in cui comunicamo e interagiamo.",
    "La privacy online è diventata una preoccupazione sempre più rilevante.",
    "La sicurezza informatica è cruciale nell'era digitale.",
    "La globalizzazione ha portato vantaggi ma anche sfide.",
    "Il commercio internazionale è un motore importante dell'economia globale.",
    "La diversità culturale arricchisce la nostra società.",
    "La migrazione può portare a nuove opportunità ma anche a tensioni.",
    "La pace è un obiettivo che tutti dovremmo perseguire.",
    "Il rispetto reciproco è fondamentale per una convivenza armoniosa.",
    "La tolleranza verso le differenze è un segno di maturità sociale.",
    "La giustizia è necessaria per garantire l'equità e la protezione dei diritti.",
    "Il rispetto per l'ambiente è fondamentale per preservare la nostra casa comune.",
    "La solidarietà è importante per sostenere coloro che sono in difficoltà.",
    "La gratitudine ci aiuta a riconoscere il valore delle piccole cose.",
    "L'amore è un sentimento potente che ci lega gli uni agli altri.",
    "L'amicizia è un legame speciale che ci porta gioia e sostegno.",
    "La famiglia è il nucleo fondamentale della società.",
    "Il lavoro di squadra è essenziale per raggiungere obiettivi comuni.",
    "La creatività ci permette di esprimere noi stessi in modi unici.",
    "La resilienza ci aiuta a superare le sfide e ad adattarci ai cambiamenti.",
    "La fiducia è la base delle relazioni interpersonali solide.",
    "La gentilezza è un atto semplice ma potente che può fare la differenza.",
    "La generosità ci rende più umani e ci unisce agli altri.",
    "La gratitudine ci aiuta a riconoscere il valore delle piccole cose.",
    "La pazienza è una virtù che ci permette di affrontare le difficoltà con calma.",
    "La determinazione è necessaria per perseguire i nostri obiettivi con impegno.",
    "La felicità è un viaggio, non una destinazione.",
    "La consapevolezza ci permette di vivere nel momento presente.",
    "La meditazione è una pratica che ci aiuta a coltivare la consapevolezza.",
    "Il benessere emotivo è fondamentale per una vita soddisfacente.",
    "La gratitudine ci aiuta a riconoscere il valore delle piccole cose.",
    "Il volontariato è un modo gratificante per dare indietro alla comunità.",
    "La resilienza ci aiuta a superare le sfide e ad adattarci ai cambiamenti.",
    "L'empatia ci permette di comprendere e condividere i sentimenti degli altri.",
    "La compassione ci spinge ad agire per alleviare il dolore degli altri.",
    "La solidarietà è importante per sostenere coloro che sono in difficoltà.",
    "La fiducia è la base delle relazioni interpersonali solide.",
    "La gentilezza è un atto semplice ma potente che può fare la differenza.",
    "La generosità ci rende più umani e ci unisce agli altri.",
    "La gratitudine ci aiuta a riconoscere il valore delle piccole cose.",
    "La pazienza è una virtù che ci permette di affrontare le difficoltà con calma.",
    "La determinazione è necessaria per perseguire i nostri obiettivi con impegno.",
    "La felicità è un viaggio, non una destinazione.",
    "La consapevolezza ci permette di vivere nel momento presente.",
    "La meditazione è una pratica che ci aiuta a coltivare la consapevolezza.",
    "Il benessere emotivo è fondamentale per una vita soddisfacente.",
    "La gratitudine ci aiuta a riconoscere il valore delle piccole cose.",
    "Il volontariato è un modo gratificante per dare indietro alla comunità.",
    "L'empatia ci permette di comprendere e condividere i sentimenti degli altri.",
    "La compassione ci spinge ad agire per alleviare il dolore degli altri.",
    "La solidarietà è importante per sostenere coloro che sono in difficoltà.",
    "La fiducia è la base delle relazioni interpersonali solide.",
    "La gentilezza è un atto semplice ma potente che può fare la differenza.",
    "La generosità ci rende più umani e ci unisce agli altri.",
    "La gratitudine ci aiuta a riconoscere il valore delle piccole cose.",
    "La pazienza è una virtù che ci permette di affrontare le difficoltà con calma.",
    "La determinazione è necessaria per perseguire i nostri obiettivi con impegno.",
    "La felicità è un viaggio, non una destinazione.",
    "La consapevolezza ci permette di vivere nel momento presente.",
    "La meditazione è una pratica che ci aiuta a coltivare la consapevolezza.",
    "Il benessere emotivo è fondamentale per una vita soddisfacente.",
    "La gratitudine ci aiuta a riconoscere il valore delle piccole cose.",
    "Il volontariato è un modo gratificante per dare indietro alla comunità.",
    "L'empatia ci permette di comprendere e condividere i sentimenti degli altri.",
    "La compassione ci spinge ad agire per alleviare il dolore degli altri.",
    "La solidarietà è importante per sostenere coloro che sono in difficoltà.",
    "La fiducia è la base delle relazioni interpersonali solide.",
    "La gentilezza è un atto semplice ma potente che può fare la differenza.",
    "La generosità ci rende più umani e ci unisce agli altri.",
    "La gratitudine ci aiuta a riconoscere il valore delle piccole cose.",
    "La pazienza è una virtù che ci permette di affrontare le difficoltà con calma.",
    "La determinazione è necessaria per perseguire i nostri obiettivi con impegno.",
    "La felicità è un viaggio, non una destinazione.",
    "La consapevolezza ci permette di vivere nel momento presente.",
    "La meditazione è una pratica che ci aiuta a coltivare la consapevolezza.",
    "Il benessere emotivo è fondamentale per una vita soddisfacente."
]


if os.path.exists("doc2vec_model"):
    # Carica il modello esistente
    model = Doc2Vec.load("doc2vec_model")
    print("Il modello è stato caricato dalla memoria.")
else:
    # Addestra un nuovo modello se non esiste già
    # (codice per addestrare il modello qui)
    print("Il modello non è presente. Eseguire l'addestramento.")

    # Carica il subset del dataset di Wikipedia in italiano
    wikipedia_dataset = load_dataset("wikipedia", "20220301.it")

    # Tokenizzazione e preparazione dei dati per Doc2Vec
    # tagged_data = [TaggedDocument(words=word_tokenize(sentence.lower()), tags=[str(i)]) for i, sentence in enumerate(corpus)]
    # Tokenizzazione dei testi
    tokenized_documents = []

    # Definisci il numero massimo di iterazioni
    max_iterazioni = 1000

    # Inizializza un contatore
    iterazioni = 0

    for documento in wikipedia_dataset['train']:
        iterazioni += 1
        testo_documento = documento['text']
        tokenized_text = word_tokenize(testo_documento.lower())  # Tokenizzazione e conversione in minuscolo
        tokenized_documents.append(tokenized_text)

        if iterazioni >= max_iterazioni:
            # Se sì, interrompi il ciclo
            break

    # Creazione degli oggetti TaggedDocument
    tagged_documents = [TaggedDocument(words=doc, tags=[str(i)]) for i, doc in enumerate(tokenized_documents)]

    # Addestramento del modello Doc2Vec
    model = Doc2Vec(vector_size=200, window=5, min_count=5, workers=4, epochs=100)
    model.build_vocab(tagged_documents)
    model.train(tagged_documents, total_examples=model.corpus_count, epochs=model.epochs)

    model.save("doc2vec_model")

# Calcolare la distanza tra gli embeddings
from scipy.spatial.distance import cosine

# Ottenere gli embeddings delle frasi
for i in range(0, 30):
    embedding_frase1 = model.infer_vector(word_tokenize(corpus[i].lower()))
    embedding_frase2 = model.infer_vector(word_tokenize(corpus[i+1].lower()))

    distanza = cosine(embedding_frase1, embedding_frase2)
    print(corpus[i], corpus[i+1], "Distanza tra gli embeddings:", distanza)


embedding_frase5 = model.infer_vector(word_tokenize("se sto pensando di mangiare un panzarotto, perchè non dovrei farlo?"))
embedding_frase6 = model.infer_vector(word_tokenize("quando penso al napoli della scorsa stagione, mi viene molta nostalgia"))

distanza = cosine(embedding_frase5, embedding_frase6)
print("Distanza tra gli embeddings:", distanza)