from gensim.models import Word2Vec
from scipy.spatial.distance import cosine
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')

# Corpus di testo
corpus = [
    "Questo è un esempio di corpus di testo.",
    "Puoi sostituire questo con il tuo corpus di testo.",
    "Assicurati che il testo sia ben tokenizzato e pulito.",
    "Una frase che una ragazza può dire mentre acconcia i propri capelli",
    "Si sta come d'autunno le foglie sugli alberi",
    "spazzolando i cavalli questi si sbizzarriscono"
]

# Tokenizzazione del corpus di testo
tokenized_corpus = [word_tokenize(sentence.lower()) for sentence in corpus]

# Addestramento del modello Word2Vec
model = Word2Vec(sentences=tokenized_corpus, vector_size=100, window=5, min_count=1, workers=4)

# Salvataggio del modello addestrato
model.save("model.bin")

# Frasi di esempio
frase1 = "Una ragazza si acconcia i capelli"
frase2 = "Una ragazza si sta spazzolando i capelli"
frase3 = "Questo è un esempio di corpus di testo"

# Tokenizzazione delle frasi
tokenized_frase1 = frase1.lower().split()
tokenized_frase2 = frase2.lower().split()

# Creazione del modello Word2Vec
# (Qui assumo che tu abbia già un modello preaddestrato, altrimenti puoi addestrarne uno sui tuoi dati)
# Assicurati di avere la dimensione di embedding corretta e il modello preaddestrato adeguato
# Carica il tuo modello Word2Vec al posto di 'model.bin'
model = Word2Vec.load("model.bin")

# Calcola l'embedding medio per ciascuna frase
embedding_frase1 = sum([model.wv[word] for word in tokenized_frase1]) / len(tokenized_frase1)
embedding_frase2 = sum([model.wv[word] for word in tokenized_frase2]) / len(tokenized_frase2)

# Calcola la distanza tra gli embeddings
distanza = cosine(embedding_frase1, embedding_frase2)
print("Distanza tra gli embeddings:", distanza)