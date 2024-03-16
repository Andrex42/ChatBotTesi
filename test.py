from torch.nn.functional import pairwise_distance
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

import torch


# Funzione per eseguire il pooling medio tenendo conto della maschera di attenzione
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output.last_hidden_state  # Gli embeddings dei token sono nell'ultimo stato nascosto
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# Frasi di esempio da confrontare
sentences = ["Il Rinascimento ha avuto impatti profondi sulla società europea, segnando una rinascita culturale, economica e politica dopo il Medioevo, inoltre ha visto un rinnovato interesse per l'arte, la letteratura, la scienza e la filosofia dell'antica Grecia e Roma, promuovendo l'umanesimo e una visione più secolare del mondo. Ci sono state nuove tecniche innovative, ad esempio la prospettiva lineare e il chiaroscuro. Il Rinascimento ha anche avuto un impatto sulle strutture sociali, con più mobilità sociale e un cambiamento nei valori culturali.",
             "Il Rinascimento ha avuto impatti profondi sulla società europea, segnando una rinascita culturale, economica e politica dopo il Medioevo. Questo periodo ha visto un rinnovato interesse per l'arte, la letteratura, la scienza e la filosofia dell'antica Grecia e Roma, promuovendo l'umanesimo e una visione più secolare del mondo. Gli artisti rinascimentali hanno introdotto tecniche innovative, come la prospettiva lineare e il chiaroscuro, portando a una nuova comprensione della rappresentazione visiva. L'educazione e l'alfabetizzazione divennero più diffuse, con un'élite culturale che si sviluppò nelle corti e nelle città, contribuendo alla nascita di una borghesia illuminata. Il Rinascimento ha anche avuto un impatto sulle strutture sociali, con una maggiore mobilità sociale e un cambiamento nei valori culturali, come l'individualismo e il primato dell'individuo rispetto alla comunità."]

# Caricamento del tokenizer e del modello
model_name = 'nickprock/sentence-bert-base-italian-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Tokenizzazione delle frasi
encoded_inputs = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

# Calcolo degli embeddings delle frasi
with torch.no_grad():
    model_output = model(**encoded_inputs)

# Esecuzione del pooling medio
sentence_embeddings = mean_pooling(model_output, encoded_inputs['attention_mask'])

# Calcolo della distanza euclidea tra gli embeddings delle frasi
euclidean_distances = pairwise_distance(sentence_embeddings, sentence_embeddings)

# Calcolo della distanza di coseno tra gli embeddings delle frasi
cosine_distances = 1 - cosine_similarity(sentence_embeddings, sentence_embeddings)

# Converti la matrice delle distanze di coseno in un tensore PyTorch
cosine_distances_tensor = torch.tensor(cosine_distances)

# Stampa delle distanze euclidee
print("Euclidean distances:")
print(euclidean_distances)

# Stampa delle distanze di coseno
print("Cosine distances:")
print(cosine_distances_tensor)

## Importing necessary libraries
#from sentence_transformers import SentenceTransformer
#from sklearn.metrics.pairwise import cosine_similarity
#
## List of sentences to be processed
#sentences = [
#    "Il gatto in strada incontra un cane",
#    "L'italia è il paese che amo, disse berlusconi in televisione.",
#    "Roma è la capitale di italia.",
#    "Un cane mangia dalla ciotola ma la ciotola è vuota.",
#    "Il gatto nella strada incontra un cane bianco",
#    "Il gatto in strada incontra un cane"
#]
#
## Initializing the Sentence Transformer model using BERT with mean-tokens pooling
#model = SentenceTransformer('nickprock/sentence-bert-base-italian-uncased')
#
## Encoding the sentences to obtain their embeddings
#sentence_embeddings = model.encode([s.lower() for s in sentences])
#
## Calculating the cosine similarity between the first sentence embedding and the rest of the embeddings
## The result will be a list of similarity scores between the first sentence and each of the other sentences
#similarity_scores = cosine_similarity([sentence_embeddings[0]], sentence_embeddings[1:])
#
#print("Similarity score between the sentences:")
#print(len(similarity_scores))
#print(similarity_scores)


def calcola_voto_finale_ponderato(punteggi, voti):
    if len(punteggi) == 0:
        raise ValueError("I punteggi non possono essere vuoti")

    if punteggi[0] == 0 or len(punteggi) == 1:
        return voti[0]

    # Calcola l'inverso di ciascun punteggio
    inversi = [1 / punteggio for punteggio in punteggi]

    # Calcola la somma totale degli inversi
    somma_totale_inversi = sum(inversi)

    # Calcola il peso di ciascun punteggio in base all'inverso
    pesi = [inverso / somma_totale_inversi for inverso in inversi]
    print("pesi", pesi)

    if pesi[0] >= 0.9:
        voto_finale_ponderato = voti[0]
    else:
        # Calcola il voto finale ponderato come la somma dei prodotti dei voti per i loro pesi corrispondenti
        voto_finale_ponderato = sum(voto * peso for voto, peso in zip(voti, pesi))

    return voto_finale_ponderato

punteggi = [1.336338996887207, 18.963150024414062, 28.92270851135254]
voti = [5, 4, 0]
print("voto ponderato", calcola_voto_finale_ponderato(punteggi, voti))