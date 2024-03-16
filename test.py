from torch.nn.functional import pairwise_distance
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

import torch

use_sentence_bert_base_italian_uncased = True

if use_sentence_bert_base_italian_uncased:
    # Funzione per eseguire il pooling medio tenendo conto della maschera di attenzione
    def mean_pooling(model_output, attention_mask):
        token_embeddings = model_output.last_hidden_state  # Gli embeddings dei token sono nell'ultimo stato nascosto
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    # Frasi di esempio da confrontare
    sentences = ["Il Rinascimento ha avuto impatti profondi sulla società europea, segnando una rinascita culturale, economica e politica dopo il Medioevo, inoltre ha visto un rinnovato interesse per l'arte, la letteratura, la scienza e la filosofia dell'antica Grecia e Roma, promuovendo l'umanesimo e una visione più secolare del mondo. Ci sono state nuove tecniche innovative, ad esempio la prospettiva lineare e il chiaroscuro. Il Rinascimento ha anche avuto un impatto sulle strutture sociali, con più mobilità sociale e un cambiamento nei valori culturali.",
                 "Il Rinascimento ha avuto impatti profondi sulla società europea, segnando una rinascita culturale, economica e politica dopo il Medioevo. Questo periodo ha visto un rinnovato interesse per l'arte, la letteratura, la scienza e la filosofia dell'antica Grecia e Roma, promuovendo l'umanesimo e una visione più secolare del mondo. Gli artisti rinascimentali hanno introdotto tecniche innovative, come la prospettiva lineare e il chiaroscuro, portando a una nuova comprensione della rappresentazione visiva. L'educazione e l'alfabetizzazione divennero più diffuse, con un'élite culturale che si sviluppò nelle corti e nelle città, contribuendo alla nascita di una borghesia illuminata. Il Rinascimento ha anche avuto un impatto sulle strutture sociali, con una maggiore mobilità sociale e un cambiamento nei valori culturali, come l'individualismo e il primato dell'individuo rispetto alla comunità.",
                 "Il Rinascimento ha avuto pochi impatti sulla società europea, modificando poco o nulla la cultura, l'economia e la politica dopo il medioevo. L'arte ha visto poco interesse, così come la letteratura, la scienza e la filosofia dell'antica Grecia e Roma."]

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
else:
    import torch.nn.functional as F

    # Mean Pooling - Take average of all tokens
    def mean_pooling(model_output, attention_mask):
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


    # Encode text
    def encode(texts):
        # Tokenize sentences
        encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings
        with torch.no_grad():
            model_output = model(**encoded_input, return_dict=True)

        # Perform pooling
        embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

        # Normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)

        return embeddings


    # Sentences we want sentence embeddings for
    query = "Il Rinascimento ha avuto impatti profondi sulla società europea, segnando una rinascita culturale, economica e politica dopo il Medioevo, inoltre ha visto un rinnovato interesse per l'arte, la letteratura, la scienza e la filosofia dell'antica Grecia e Roma, promuovendo l'umanesimo e una visione più secolare del mondo. Ci sono state nuove tecniche innovative, ad esempio la prospettiva lineare e il chiaroscuro. Il Rinascimento ha anche avuto un impatto sulle strutture sociali, con più mobilità sociale e un cambiamento nei valori culturali."
    docs = ["Il Rinascimento ha avuto impatti profondi sulla società europea, segnando una rinascita culturale, economica e politica dopo il Medioevo. Questo periodo ha visto un rinnovato interesse per l'arte, la letteratura, la scienza e la filosofia dell'antica Grecia e Roma, promuovendo l'umanesimo e una visione più secolare del mondo. Gli artisti rinascimentali hanno introdotto tecniche innovative, come la prospettiva lineare e il chiaroscuro, portando a una nuova comprensione della rappresentazione visiva. L'educazione e l'alfabetizzazione divennero più diffuse, con un'élite culturale che si sviluppò nelle corti e nelle città, contribuendo alla nascita di una borghesia illuminata. Il Rinascimento ha anche avuto un impatto sulle strutture sociali, con una maggiore mobilità sociale e un cambiamento nei valori culturali, come l'individualismo e il primato dell'individuo rispetto alla comunità.",
            "Il Rinascimento ha avuto pochi impatti sulla società europea, modificando poco o nulla la cultura, l'economia e la politica dopo il medioevo. L'arte ha visto poco interesse, così come la letteratura, la scienza e la filosofia dell'antica Grecia e Roma."]

    # Load model from HuggingFace Hub
    tokenizer = AutoTokenizer.from_pretrained("SeyedAli/Multilingual-Text-Semantic-Search-Siamese-BERT-V1")
    model = AutoModel.from_pretrained("SeyedAli/Multilingual-Text-Semantic-Search-Siamese-BERT-V1")

    # Encode query and docs
    query_emb = encode(query)
    doc_emb = encode(docs)

    # Compute dot score between query and all document embeddings
    scores = torch.mm(query_emb, doc_emb.transpose(0, 1))[0].cpu().tolist()

    # Combine docs & scores
    doc_score_pairs = list(zip(docs, scores))

    # Sort by decreasing score
    doc_score_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)

    # Output passages & scores
    for doc, score in doc_score_pairs:
        print(score, doc)
