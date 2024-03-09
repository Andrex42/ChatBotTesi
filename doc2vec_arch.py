import pandas as pd
import chromadb
import nltk
import os
import re

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess
from chromadb import EmbeddingFunction, Documents, Embeddings
from chromadb.utils import embedding_functions
nltk.download('punkt')

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-mpnet-base-v2")


model: Doc2Vec


# Tokenizzazione e preparazione dei dati
def preprocess_text(text: str, remove_stopwords: bool) -> list[str]:
    """Funzione che pulisce il testo in input andando a
    - rimuovere i link
    - rimuovere i caratteri speciali
    - rimuovere i numeri
    - rimuovere le stopword
    - trasformare in minuscolo
    - rimuovere spazi bianchi eccessivi
    Argomenti:
        text (str): testo da pulire
        remove_stopwords (bool): rimuovere o meno le stopword
    Restituisce:
        str: testo pulito
    """
    # rimuovi link
    text = re.sub(r"http\S+", "", text)
    # rimuovi numeri e caratteri speciali
    text = re.sub("[^A-Za-z]+", " ", text)
    # rimuovere le stopword
    if remove_stopwords:
        # 1. crea token
        tokens = nltk.word_tokenize(text)
        # 2. controlla se è una stopword
        tokens = [w.lower().strip() for w in tokens if not w.lower() in stopwords.words("italian")]
        # restituisci una lista di token puliti
        return tokens


if os.path.exists("doc2vec_arch_model"):
    # Carica il modello esistente
    model = Doc2Vec.load("doc2vec_arch_model")
    print("Il modello è stato caricato dalla memoria.")
else:
    # Addestra un nuovo modello se non esiste già
    # (codice per addestrare il modello qui)
    print("Il modello non è presente. Eseguire l'addestramento.")
    # Carica il dataset delle risposte
    df = pd.read_csv('./training_data/risposte_archeologia_storia_arte.csv')
    df_test = pd.read_csv('./training_data/risposte_test_archeologia_storia_arte.csv')
    # TaggedDocument per ogni riga nel dataset di addestramento
    tagged_train_data = [TaggedDocument(words=row['text'],
                                        tags=[row['title'], row['label']]) for index, row in df.iterrows()]

    # Addestramento del modello Doc2Vec
    model = Doc2Vec(vector_size=100, window=5, min_count=1, workers=4, epochs=20)  # model = Doc2Vec(vector_size=200, window=5, min_count=5, workers=4, epochs=100)
    model.build_vocab(tagged_train_data)
    model.train(tagged_train_data, total_examples=model.corpus_count, epochs=model.epochs)
    model.save("doc2vec_arch_model")


client = chromadb.PersistentClient(path="./chroma_doc2vec/data")
collection = client.get_or_create_collection(name="sentences_collection", embedding_function=sentence_transformer_ef)

df = pd.read_csv('./training_data/risposte_archeologia_storia_arte.csv')
df_test = pd.read_csv('./training_data/risposte_test_archeologia_storia_arte.csv')

risposte_dict = df.to_dict('records')


print(collection.count(), "documenti trovati in example_collection")
print(len(risposte_dict), "risposte trovate nei dati di training")


if collection.count() < len(risposte_dict):
    metadatas: list = []
    documents: list = []
    embeddings: list = []
    ids: list = []

    start_index = collection.count() if collection.count() is not None else 0

    try:
        for id, data in enumerate(risposte_dict):
            cleaned = preprocess_text(data['text'], remove_stopwords=True)
            # print(' '.join(cleaned))
            metadatas.append({"domanda": data['title'], "risultato": data['label']})
            documents.append(data['text'])
            ids.append(f"id_{id + start_index}")

        collection.add(
            metadatas=metadatas,
            documents=documents,
            ids=ids
        )
        print("Data added to collection")
    except Exception as e:
        print("Add data to db failed : ", e)


def evaluate_model():
    correct = 0
    total = 0

    for idx, dt in df_test.iterrows():
        try:
            cleaned = preprocess_text(dt['text'], remove_stopwords=True)
            # print(' '.join(cleaned))

            res = collection.query(
                query_texts=[dt['text']],
                n_results=1,
                include=['distances', 'embeddings', 'documents', 'metadatas'],
                where={"domanda": dt['title']}
            )

            if res['metadatas'][0][0]['risultato'] == dt['label']:
                correct += 1
            else:
                print("confronto", res['documents'][0][0])
                print("con", dt['text'])
                print("train result was", res['metadatas'][0][0]['risultato'], "response was", dt['label'])
                print("")
                print("")

            total += 1

            # print("Query", "\n--------------")
            # print(dt['text'])
            # print("Result", "\n--------------")
            # print(res['documents'][0][0])
            # # print("Vector", "\n--------------")
            # # print(res['embeddings'][0][0])
            # print("")
            # print("")
            # print("Complete Response", "\n-------------------------")
            # print(res)

        except Exception as e:
            print("Vector search failed : ", e)

    return correct / total


accuracy = evaluate_model()
print("Accuracy:", accuracy)



# import os
# from nltk.tokenize import word_tokenize
# from gensim.models.doc2vec import Doc2Vec, TaggedDocument
# from gensim.utils import simple_preprocess
# import pandas as pd
# import nltk
# nltk.download('punkt')
#
#
# # Tokenizzazione e preparazione dei dati
# def preprocess_text(text):
#     return simple_preprocess(text)
#
#
# # Valutazione del modello
# def evaluate_model(model, test_data):
#     correct = 0
#     total = 0
#
#     for tagged_doc in test_data:
#         inferred_vector = model.infer_vector(tagged_doc.words)
#         most_similar_tags = model.dv.most_similar([inferred_vector], topn=1)
#         if most_similar_tags[0][0] == tagged_doc.tags[0]:
#             correct += 1
#         else:
#             print(most_similar_tags)
#             print("Most similar", most_similar_tags, "different from", tagged_doc)
#         total += 1
#     accuracy = correct / total
#     print("Accuracy:", accuracy)
#
#
# if os.path.exists("doc2vec_arch_model"):
#     # Carica il modello esistente
#     model = Doc2Vec.load("doc2vec_arch_model")
#     print("Il modello è stato caricato dalla memoria.")
#
#     df_test = pd.read_csv('./training_data/risposte_test_archeologia_storia_arte.csv')
#
#     # TaggedDocument per ogni riga nel dataset di test
#     tagged_test_data = [TaggedDocument(words=preprocess_text(row['text']),
#                                        tags=[row['title'], row['label']]) for index, row in df_test.iterrows()]
#
#     # Valuta il modello sui dati di test
#     evaluate_model(model, tagged_test_data)
# else:
#     # Addestra un nuovo modello se non esiste già
#     # (codice per addestrare il modello qui)
#     print("Il modello non è presente. Eseguire l'addestramento.")
#
#     # Carica il dataset delle risposte
#     df = pd.read_csv('./training_data/risposte_archeologia_storia_arte.csv')
#     df_test = pd.read_csv('./training_data/risposte_test_archeologia_storia_arte.csv')
#
#     # TaggedDocument per ogni riga nel dataset di addestramento
#     tagged_train_data = [TaggedDocument(words=preprocess_text(row['text']),
#                                         tags=[row['title'], row['label']]) for index, row in df.iterrows()]
#
#     # TaggedDocument per ogni riga nel dataset di test
#     tagged_test_data = [TaggedDocument(words=preprocess_text(row['text']),
#                                        tags=[row['title'], row['label']]) for index, row in df_test.iterrows()]
#
#     print(tagged_test_data[0].tags)
#
#     # Addestramento del modello Doc2Vec
#     model = Doc2Vec(vector_size=100, window=5, min_count=1, workers=4, epochs=20)  # model = Doc2Vec(vector_size=200, window=5, min_count=5, workers=4, epochs=100)
#     model.build_vocab(tagged_train_data)
#     model.train(tagged_train_data, total_examples=model.corpus_count, epochs=model.epochs)
#
#     # model.save("doc2vec_arch_model")
#
#     # Valuta il modello sui dati di test
#     evaluate_model(model, tagged_test_data)
