import csv
import hashlib
import time
from typing import Optional
import chromadb
import os
import sys
import numpy as np
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import pprint
import pandas as pd
import logging
from datetime import datetime
from colorama import Fore, Style
from model.answer_model import Answer
from model.question_model import Question

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

extDataDir = os.getcwd()
if getattr(sys, 'frozen', False):
    extDataDir = sys._MEIPASS
load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))

pp = pprint.PrettyPrinter(indent=4)  # PrettyPrinter makes dictionary output easier to read

PRETRAINED_MODEL_NAME = os.getenv("PRETRAINED_MODEL_NAME")
if PRETRAINED_MODEL_NAME is None:
    raise ValueError("Pretrained model name not found in the environment variables.")

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=PRETRAINED_MODEL_NAME
)


chroma_client: chromadb.ClientAPI


def init_chroma_client():
    # Initializes the ChromaDB client with certain settings. These settings specify that the client should use DuckDB with Parquet for storage,
    # and it should store its data in a directory named 'database'.
    global chroma_client
    if 'chroma_client' not in globals():
        chroma_client = chromadb.PersistentClient(path="./chroma/data")


def get_chroma_q_a_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    # Gets or creates a ChromaDB collection named 'q_a', using the Cohere embedding function.
    # example_collection = chroma_client.get_or_create_collection(name="q_a", embedding_function=cohere_ef)
    # Gets or creates a ChromaDB collection named 'q_a',
    # using the SentenceTransformerEmbeddingFunction embedding function.
    q_a_collection = chroma_client.get_or_create_collection(
        name="q_a",
        metadata={"hnsw:space": "cosine"},
        embedding_function=embedding_func)
    return q_a_collection


def get_chroma_questions_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    print("getting get_chroma_questions_collection")

    # Gets or creates a ChromaDB collection named 'questions', using the Cohere embedding function.
    # example_collection = chroma_client.get_or_create_collection(name="questions", embedding_function=cohere_ef)
    # Gets or creates a ChromaDB collection named 'questions',
    # using the SentenceTransformerEmbeddingFunction embedding function.
    questions_collection = chroma_client.get_or_create_collection(
        name="questions",
        metadata={"hnsw:space": "cosine"},
        embedding_function=embedding_func
    )
    return questions_collection


def generate_sha256_hash_from_text(text):
    # Create a SHA256 hash object
    sha256_hash = hashlib.sha256()
    # Update the hash object with the text encoded to bytes
    sha256_hash.update(text.encode('utf-8'))
    # Return the hexadecimal representation of the hash
    return sha256_hash.hexdigest()


def init_model_with_exports():
    init_chroma_client()

    export_data_directory = './export_data'

    files = os.listdir(export_data_directory)

    export_domande = []
    export_risposte = []

    for file in files:
        if not file.endswith(".csv"):
            continue

        if file.startswith("export_domande"):
            export_domande.append(os.path.join(export_data_directory, file))
        elif file.startswith("export_risposte"):
            export_risposte.append(os.path.join(export_data_directory, file))

    domande_collection = get_chroma_questions_collection()
    domande_collection_count = domande_collection.count()
    print(domande_collection_count, "documenti trovati in domande_collection")

    q_a_collection = get_chroma_q_a_collection()
    q_a_collection_count = q_a_collection.count()
    print(q_a_collection_count, "documenti trovati in q_a_collection")

    print("Initializing collections.")

    for file_domande in export_domande:
        # Reads the CSV data into pandas DataFrames.
        df_domande = pd.read_csv(file_domande)
        # Converts the DataFrames to lists of dictionaries.
        domande_dict = df_domande.to_dict('records')

        domande_collection_result = domande_collection.get(include=[])

        for idx, item in enumerate(domande_dict):
            id_domanda = item['id'] if not item['id'].startswith("id_") else generate_sha256_hash_from_text(item['id'])

            if id_domanda not in domande_collection_result['ids']:
                print(f"Adding question", idx, item['text'])

                domande_collection.add(
                    documents=[item['text']],  # aggiunge la domanda ai documenti
                    metadatas=[{"id_domanda": id_domanda,
                                "id_docente": item['id_docente'],
                                "categoria": item['label'],
                                "source": item['source'],
                                "archived": item['archived'],
                                "data_creazione": item['data_creazione']}],
                    ids=[id_domanda]
                )
            else:
                print(f"Question {idx} already existing.")

    for file_risposte in export_risposte:
        # Reads the CSV data into pandas DataFrames.
        df_risposte = pd.read_csv(file_risposte)
        # Converts the DataFrames to lists of dictionaries.
        risposte_dict = df_risposte.to_dict('records')

        q_a_collection_result = q_a_collection.get(include=[])

        for idx, item in enumerate(risposte_dict):
            id_domanda = item['id_domanda'] if not item['id_domanda'].startswith("id_") \
                else generate_sha256_hash_from_text(item['id_domanda'])

            id_risposta = item['id'] if not item['id'].startswith("id_") \
                else generate_sha256_hash_from_text(item['id'])

            if id_risposta not in q_a_collection_result['ids']:
                print(f"Adding answer", idx, item['text'])

                q_a_collection.add(
                    documents=[item['text']],  # aggiunge la risposta ai documenti
                    metadatas=[{"id_domanda": id_domanda,
                                "domanda": item['title'],
                                "id_docente": item['id_docente'],
                                "id_autore": item['id_autore'],
                                "voto_docente": int(item['label']),
                                "voto_predetto": int(item['voto_predetto']),
                                "voto_predetto_all": int(item['voto_predetto_all']),
                                "commento": item['commento'],
                                "source": item['source'],
                                "data_creazione": item['data_creazione']}],
                    ids=[id_risposta]
                )
            else:
                print(f"Answer {idx} already existing.")

    domande_collection_count = domande_collection.count()
    q_a_collection_count = q_a_collection.count()

    print(f"Collections initialized successfully. "
          f"{domande_collection_count} questions. "
          f"{q_a_collection_count} answers.")


def init_model():
    init_chroma_client()

    # Reads the CSV data into pandas DataFrames.
    df_domande = pd.read_csv('./training_data/domande_archeologia_storia_arte.csv')
    df_risposte = pd.read_csv('./training_data/risposte_archeologia_storia_arte.csv')
    df_risposte_docente = pd.read_csv('./training_data/risposte_docente_archeologia_storia_arte.csv')

    # Converts the DataFrames to lists of dictionaries.
    domande_dict = df_domande.to_dict('records')
    risposte_dict = df_risposte.to_dict('records')
    risposte_docente_dict = df_risposte_docente.to_dict('records')

    domande_collection = get_chroma_questions_collection()
    domande_collection_count = domande_collection.count()

    print(domande_collection_count, "documenti trovati in domande_collection")
    print(len(domande_dict), "domande trovate nei dati di training")

    q_a_collection = get_chroma_q_a_collection()
    q_a_collection_count = q_a_collection.count()

    print(q_a_collection_count, "documenti trovati in q_a_collection")
    print(len(risposte_dict) + len(risposte_docente_dict), "risposte trovate nei dati di training")

    limit_add = None

    # If the number of examples in the collection is less than the number of examples in the questions data,
    # adds the examples to the collection.
    if domande_collection_count < len(domande_dict):
        for idx, item in enumerate(domande_dict[domande_collection_count:]):
            index = domande_collection_count + idx
            print("\nAdding question", index, item)

            # Ottieni la data e l'ora correnti
            now = datetime.now()
            # Converti in formato ISO 8601
            iso_format = now.isoformat()

            domande_collection.add(
                documents=[item['text']],  # aggiunge la domanda ai documenti
                metadatas=[{"id_domanda": item['id'],
                            "id_docente": item['id_docente'],
                            "categoria": item['label'],
                            "source": "internal__training",
                            "archived": False,
                            "data_creazione": iso_format}],
                ids=[item['id']]
            )

            if limit_add == idx:
                break

    # If the number of examples in the collection is less than the number of examples in the q_a data,
    # adds the examples to the collection.
    if q_a_collection_count < len(risposte_docente_dict):
        for idx, item in enumerate(risposte_docente_dict[q_a_collection_count:]):
            index = q_a_collection_count + idx
            print("\nAdding risposta docente", index, item)

            # Ottieni la data e l'ora correnti
            now = datetime.now()
            # Converti in formato ISO 8601
            iso_format = now.isoformat()

            q_a_collection.add(
                documents=[item['text']],  # aggiunge la risposta ai documenti
                metadatas=[{"id_domanda": item['id_domanda'],
                            "domanda": item['title'],
                            "id_docente": item['id_docente'],
                            "id_autore": item['id_docente'],
                            "voto_docente": 10,
                            "voto_predetto": -1,
                            "voto_predetto_all": -1,
                            "commento": "undefined",
                            "source": "internal__training",
                            "data_creazione": iso_format}],
                ids=[f"id_{index}"]
            )

            if limit_add is not None and limit_add == idx:
                break

    q_a_collection_count = q_a_collection.count()

    # If the number of examples in the collection is less than the number of examples in the q_a data,
    # adds the examples to the collection.

    if q_a_collection_count < (len(risposte_docente_dict) + len(risposte_dict)):
        for idx, item in enumerate(risposte_dict[(q_a_collection_count - len(risposte_docente_dict)):]):
            index = q_a_collection_count + idx
            print("\nAdding risposta", index, item)

            # Ottieni la data e l'ora correnti
            now = datetime.now()
            # Converti in formato ISO 8601
            iso_format = now.isoformat()

            q_a_collection.add(
                documents=[item['text']],  # aggiunge la risposta ai documenti
                metadatas=[{"id_domanda": item['id_domanda'],
                            "domanda": item['title'],
                            "id_docente": item['id_docente'],
                            "id_autore": "undefined",
                            "voto_docente": int(item['label']),  # voto del docente che va da 1 a 10
                            "voto_predetto": -1,  # voto non disponibile per i dati di addestramento, default -1
                            "voto_predetto_all": -1,  # voto non disponibile per i dati di addestramento, default -1
                            "commento": "undefined",
                            "source": "internal__training",
                            "data_creazione": iso_format}],
                ids=[f"id_{index}"]
            )

            if limit_add is not None and limit_add == idx:
                break


def check_answer_records():
    init_chroma_client()

    # Reads the CSV data into pandas DataFrames.
    df_risposte = pd.read_csv('./training_data/risposte_archeologia_storia_arte.csv')
    df_risposte_docente = pd.read_csv('./training_data/risposte_docente_archeologia_storia_arte.csv')

    # Converts the DataFrames to lists of dictionaries.
    risposte_dict = df_risposte.to_dict('records')
    risposte_docente_dict = df_risposte_docente.to_dict('records')

    q_a_collection = get_chroma_q_a_collection()
    q_a_collection_count = q_a_collection.count()

    risposte_docente_result = q_a_collection.get(
        where={"id_autore": {"$ne": "undefined"}}
    )

    ok = True

    print("len(risposte_docente_result['documents'])", len(risposte_docente_result['documents']))
    print("len(risposte_docente_dict)", len(risposte_docente_dict))

    if len(risposte_docente_result['documents']) == len(risposte_docente_dict):
        for idx, item in enumerate(risposte_docente_dict):
            if item['text'] not in risposte_docente_result['documents']:
                print(item['text'], "non trovato")
                ok = False

    risposte_result = q_a_collection.get(
        where={"id_autore": "undefined"}
    )

    print("len(risposte_result['documents'])", len(risposte_result['documents']))
    print("len(risposte_dict)", len(risposte_dict))

    if len(risposte_result['documents']) == len(risposte_dict):
        for idx, item in enumerate(risposte_dict):
            if item['text'] not in risposte_result['documents']:
                print(item['text'], "non trovato")
                ok = False

    print("check_answer_records", ok)


def calcola_voto_finale_ponderato(punteggi, voti):
    if len(punteggi) == 0:
        raise ValueError("I punteggi non possono essere vuoti")

    if punteggi[0] == 0 or len(punteggi) == 1:
        # Se il primo punteggio è 0, abbiamo trovato una risposta identica, restituisci quindi il suo voto
        # Se invece è presente solo una risposta, restituisci il suo voto
        # (è, ad esempio, il caso dove il confronto avviene solo con la risposta di riferimento del docente)
        return voti[0]

    distanze = np.array(punteggi)
    initial_threshold = 0.1

    # Calcolo del numero di distanze
    num_distanze = len(distanze)

    # Soglia iniziale per i valori più bassi di num_distanze
    reduced_threshold = initial_threshold
    num_distanze_minime = 2

    # Fattore di riduzione esponenziale
    fattore_riduzione = 0.1  # Puoi regolare questo valore in base alla velocità di riduzione desiderata

    # Calcolo della soglia ridotta in modo esponenziale solo per i valori più alti di num_distanze
    if num_distanze > num_distanze_minime:
        reduced_threshold = initial_threshold * np.exp(-fattore_riduzione * (num_distanze - num_distanze_minime))

    # Calcolo dei pesi modificati utilizzando una funzione di esponenziazione
    pesi_modificati = np.exp(-distanze / reduced_threshold)

    # Normalizzazione dei pesi in modo che la somma sia uguale a 1
    pesi_modificati = pesi_modificati / np.sum(pesi_modificati)

    print(
        f"\t{Fore.LIGHTBLACK_EX}Reduced threshold: {reduced_threshold}"
    )

    print(
        f"\t{Fore.LIGHTBLACK_EX}Document distances weights modified: {pesi_modificati}"
    )

    if pesi_modificati[0] >= 0.9:
        # Se il primo è almeno il 90% rispetto agli altri, assegna il suo voto
        voto_finale_ponderato = voti[0]
    else:
        # Calcola il voto finale ponderato come la somma dei prodotti dei voti per i loro pesi corrispondenti
        voto_finale_ponderato = sum(voto * peso for voto, peso in zip(voti, pesi_modificati))

    return voto_finale_ponderato


def adjust_score(distances, score, reduction_start=0.06, reduction_end=0.6) -> int:
    """
        Corregge il punteggio basato sulla distanza minima da un punto di riferimento,
        applicando una riduzione proporzionale all'interno di un intervallo definito.

        Parametri:
        - distances (list[float]): Una lista di distanze, dove il primo elemento è considerato
          la distanza minima per la correzione del punteggio.
        - score (float): Il punteggio originale da correggere basato sulla distanza minima.
        - reduction_start (float, opzionale): La distanza a partire dalla quale iniziare la riduzione
          del punteggio. Default a 0.06.
        - reduction_end (float, opzionale): La distanza oltre la quale il punteggio viene ridotto a 1.
          Default a 0.6.

        Restituisce:
        - int: Il punteggio corretto, arrotondato all'intero più vicino.

        Solleva:
        - ValueError: Se `distances` è vuoto oppure se `reduction_start` è minore di 0 o maggiore di `reduction_end`.

        Note:
        - La funzione calcola una percentuale di riduzione basata sulla posizione della distanza
          minima rispetto all'intervallo definito da `reduction_start` e `reduction_end`.
        - Per distanze inferiori a `reduction_start`, il punteggio rimane invariato. Per distanze
          superiori a `reduction_end`, il punteggio viene impostato a 0. Per distanze intermedie,
          il punteggio viene ridotto proporzionalmente.
        """

    if len(distances) == 0:
        raise ValueError("Le distanze non possono essere vuote")

    min_distance = distances[0]

    if reduction_start < 0 or reduction_start > reduction_end:
        raise ValueError("Valori di riduzione non validi")

    # Se la distanza minima è maggiore di 0.6, il punteggio diventa 1 (voto minimo)
    if min_distance > reduction_end:
        return 1

    # Se la distanza minima è sotto la soglia di riduzione iniziale, il punteggio rimane invariato
    if min_distance < reduction_start:
        return score

    # Calcola la percentuale da sottrarre basata sulla distanza
    percentage_to_subtract = (min_distance - reduction_start) / (reduction_end - reduction_start)

    print(
        f"\t{Fore.LIGHTBLACK_EX}Percentage to subtract: {percentage_to_subtract}"
    )

    adjusted_result = max(score * (1 - percentage_to_subtract), 1)  # valore ridotto dalla percentuale, 1 se la riduzione è totale

    return round(adjusted_result)  # arrotondamento all'intero più vicino


def calc_jaccard_distance(embedding1, embedding2):
    # Calcola la similarità coseno tra gli embeddings dei documenti
    # cos_sim = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    #print("Cosine Similarity:", cos_sim)

    # Calcola la distanza di Jaccard tra le rappresentazioni binarie degli embeddings
    set1 = set(np.where(embedding1 > 0)[0])
    set2 = set(np.where(embedding2 > 0)[0])
    jaccard_distance = 1 - len(set1.intersection(set2)) / len(set1.union(set2))

    return jaccard_distance


def predict_vote_from_ref(id_domanda: str, teacher_username: str, sentence_to_compare_text, export_folder='', expected_vote=-1, questions_analyzed=None):
    if questions_analyzed is None:
        questions_analyzed = []

    results = get_ref_sentence(id_domanda, teacher_username, sentence_to_compare_text)

    accuracy_output_path = ''
    distances_output_path = ''

    if export_folder != '':
        accuracy_file_name = f"export_ref_only_accuracy_test.csv"
        distances_file_name = f"export_ref_only_distances_test.csv"

        # Percorso completo per il file CSV di output
        accuracy_output_path = os.path.join(export_folder, accuracy_file_name)
        distances_output_path = os.path.join(export_folder, distances_file_name)

        if not os.path.exists(accuracy_output_path):
            # Apri il file CSV in modalità di scrittura
            with open(accuracy_output_path, mode='w', newline='', encoding='utf-8') as file:
                # Definisci il writer CSV
                writer = csv.DictWriter(
                    file,
                    fieldnames=['q_short_id', 'question', 'answer', 'most_similar_answer', 'most_similar_answer_author_id', 'cosine_distance', 'jaccard_distance', 'combined_distance', 'most_similar_answer_vote', 'expected_vote', 'predicted_vote', 'result']
                )

                # Scrivi l'intestazione del CSV
                writer.writeheader()

        if not os.path.exists(distances_output_path):
            # Apri il file CSV in modalità di scrittura
            with open(distances_output_path, mode='w', newline='', encoding='utf-8') as file:
                # Definisci il writer CSV
                writer = csv.DictWriter(
                    file,
                    fieldnames=['q_short_id', 'question', 'answer', 'similar_answer', 'similar_answer_author_id', 'cosine_distance', 'jaccard_distance', 'combined_distance', 'similar_answer_vote', 'expected_vote']
                )

                # Scrivi l'intestazione del CSV
                writer.writeheader()

    distances = [round(abs(x), 3) for x in results['distances'][0]]

    #sentence_to_compare_embeddings = SentencesEmbeddingFunction().__call__([sentence_to_compare_text])
    sentence_to_compare_embeddings = embedding_func.__call__([sentence_to_compare_text])
    embedding1 = np.array(sentence_to_compare_embeddings[0])

    similar_dict_list = []

    for idx, doc in enumerate(results['documents'][0]):
        it_metadata = results['metadatas'][0][idx]
        it_distance = distances[idx]

        embedding2 = np.array(results['embeddings'][0][idx])
        jaccard_distance = calc_jaccard_distance(embedding1, embedding2)
        cos_similarity = 1 - distances[idx]

        # Combinazione delle metriche: media pesata della similarità coseno e della distanza di Jaccard
        combined_sim = (cos_similarity + (1 - jaccard_distance)) / 2
        combined_distance = 1 - combined_sim

        similar_dict_list.append({
            "document": doc,
            "metadata": it_metadata,
            "cosine_distance": it_distance,
            "jaccard_distance": jaccard_distance,
            "combined_distance": combined_distance
        })

        print(
            f"\t - Doc {idx}: ({it_metadata['id_autore']}) Cosine Distance: {it_distance} | Jaccard Distance: {jaccard_distance} | Combined Distance: {combined_distance} | Vote: {it_metadata['voto_docente']}",
            "'" + doc + "'")

        if distances_output_path != '':
            with open(distances_output_path, mode='a', newline='',
                      encoding='utf-8') as file:  # Apri il file in modalità di aggiunta (append)
                writer = csv.writer(file)

                writer.writerow([
                    f'Q{len(questions_analyzed)}',
                    it_metadata['domanda'],
                    sentence_to_compare_text,
                    doc,
                    it_metadata['id_autore'],
                    round(it_distance, 3),
                    round(jaccard_distance, 3),
                    round(combined_distance, 3),
                    it_metadata['voto_docente'],
                    expected_vote
                ])

    # Sort by increasing combined distance
    similar_dict_list = sorted(similar_dict_list, key=lambda x: x['combined_distance'])

    best_similar = similar_dict_list[0]

    print(f"\n\t{Fore.CYAN}Ref similarity match{Style.RESET_ALL}:\n"
          f"\t\tCosine Distance: {best_similar['cosine_distance']}"
          f"\t\tJaccard Distance: {best_similar['jaccard_distance']}"
          f"\n\t\tRef. Result: {Fore.GREEN if best_similar['metadata']['voto_docente'] >= 6 else Fore.RED}{best_similar['metadata']['voto_docente']}{Style.RESET_ALL}"
          f"\n\t\tDocument: {best_similar['document']}"
          f"\n\t\tAuthor: {best_similar['metadata']['id_autore']}\n")

    voti = [x['metadata']['voto_docente'] for x in similar_dict_list]
    combined_distances = [x['combined_distance'] for x in similar_dict_list]

    final_score = adjust_score(combined_distances, voti[0])

    print("")

    if accuracy_output_path != '':
        error_tolerance = 1

        ACCURACY_TEST_ERROR_TOLERANCE = os.getenv("ACCURACY_TEST_ERROR_TOLERANCE")
        if ACCURACY_TEST_ERROR_TOLERANCE is not None:
            error_tolerance = int(ACCURACY_TEST_ERROR_TOLERANCE)

        with open(accuracy_output_path, mode='a', newline='', encoding='utf-8') as file:  # Apri il file in modalità di aggiunta (append)
            writer = csv.writer(file)

            writer.writerow([
                f"Q{questions_analyzed.index(best_similar['metadata']['domanda']) + 1}",
                best_similar['metadata']['domanda'],
                sentence_to_compare_text,
                best_similar['document'],
                best_similar['metadata']['id_autore'],
                round(best_similar['cosine_distance'], 3),
                round(best_similar['jaccard_distance'], 3),
                round(best_similar['combined_distance'], 3),
                best_similar['metadata']['voto_docente'],
                expected_vote,
                final_score,
                "PASSED" if abs(final_score - expected_vote) <= error_tolerance else "FAILED"
            ])

    return final_score


def predict_vote(id_domanda: str, sentence_to_compare_text, export_folder='', expected_vote=-1, questions_analyzed=None):
    if questions_analyzed is None:
        questions_analyzed = []

    results = get_similar_sentences(id_domanda, sentence_to_compare_text)

    accuracy_output_path = ''
    distances_output_path = ''

    if export_folder != '':
        accuracy_file_name = f"export_accuracy_test.csv"
        distances_file_name = f"export_distances_test.csv"

        # Percorso completo per il file CSV di output
        accuracy_output_path = os.path.join(export_folder, accuracy_file_name)
        distances_output_path = os.path.join(export_folder, distances_file_name)

        if not os.path.exists(accuracy_output_path):
            # Apri il file CSV in modalità di scrittura
            with open(accuracy_output_path, mode='w', newline='', encoding='utf-8') as file:
                # Definisci il writer CSV
                writer = csv.DictWriter(
                    file,
                    fieldnames=['q_short_id', 'question', 'answer', 'most_similar_answer', 'most_similar_answer_author_id', 'cosine_distance', 'jaccard_distance', 'combined_distance', 'most_similar_answer_vote', 'expected_vote', 'predicted_vote', 'result']
                )

                # Scrivi l'intestazione del CSV
                writer.writeheader()

        if not os.path.exists(distances_output_path):
            # Apri il file CSV in modalità di scrittura
            with open(distances_output_path, mode='w', newline='', encoding='utf-8') as file:
                # Definisci il writer CSV
                writer = csv.DictWriter(
                    file,
                    fieldnames=['q_short_id', 'question', 'answer', 'similar_answer', 'similar_answer_author_id', 'cosine_distance', 'jaccard_distance', 'combined_distance', 'similar_answer_vote', 'expected_vote']
                )

                # Scrivi l'intestazione del CSV
                writer.writeheader()

    distances = [round(abs(x), 3) for x in results['distances'][0]]

    sentence_to_compare_embeddings = embedding_func.__call__([sentence_to_compare_text])
    embedding1 = np.array(sentence_to_compare_embeddings[0])

    similar_dict_list = []

    for idx, doc in enumerate(results['documents'][0]):
        it_metadata = results['metadatas'][0][idx]
        it_distance = distances[idx]

        embedding2 = np.array(results['embeddings'][0][idx])
        jaccard_distance = calc_jaccard_distance(embedding1, embedding2)
        cos_similarity = 1 - distances[idx]

        # Combinazione delle metriche: media pesata della similarità coseno e della distanza di Jaccard
        combined_sim = (cos_similarity + (1 - jaccard_distance)) / 2
        combined_distance = 1 - combined_sim

        similar_dict_list.append({
            "document": doc,
            "metadata": it_metadata,
            "cosine_distance": it_distance,
            "jaccard_distance": jaccard_distance,
            "combined_distance": combined_distance
        })

        print(
            f"\t - Doc {idx}: ({it_metadata['id_autore']}) Cosine Distance: {it_distance} | Jaccard Distance: {jaccard_distance} | Combined Distance: {combined_distance} | Vote: {it_metadata['voto_docente']}",
            "'" + doc + "'")

        if distances_output_path != '':
            with open(distances_output_path, mode='a', newline='',
                      encoding='utf-8') as file:  # Apri il file in modalità di aggiunta (append)
                writer = csv.writer(file)

                writer.writerow([
                    f'Q{len(questions_analyzed)}',
                    it_metadata['domanda'],
                    sentence_to_compare_text,
                    doc,
                    it_metadata['id_autore'],
                    round(it_distance, 3),
                    round(jaccard_distance, 3),
                    round(combined_distance, 3),
                    it_metadata['voto_docente'],
                    expected_vote
                ])

    # Sort by increasing combined distance
    similar_dict_list = sorted(similar_dict_list, key=lambda x: x['combined_distance'])

    best_similar = similar_dict_list[0]

    print(f"\n\t{Fore.CYAN}Best similarity match{Style.RESET_ALL}:\n"
          f"\t\tCosine Distance: {best_similar['cosine_distance']}"
          f"\t\tJaccard Distance: {best_similar['jaccard_distance']}"
          f"\n\t\tRef. Result: {Fore.GREEN if best_similar['metadata']['voto_docente'] >= 6 else Fore.RED}{best_similar['metadata']['voto_docente']}{Style.RESET_ALL}"
          f"\n\t\tDocument: {best_similar['document']}"
          f"\n\t\tAuthor: {best_similar['metadata']['id_autore']}\n")

    voti = [x['metadata']['voto_docente'] for x in similar_dict_list]
    combined_distances = [x['combined_distance'] for x in similar_dict_list]

    voto_ponderato = round(calcola_voto_finale_ponderato(combined_distances, voti), 1)

    print(
        f"\t{Fore.LIGHTBLACK_EX}Weighted avg: {Fore.YELLOW}{Style.BRIGHT}{voto_ponderato}{Style.RESET_ALL}"
    )

    final_score = adjust_score(combined_distances, voto_ponderato)

    print("")

    if accuracy_output_path != '':
        error_tolerance = 1

        ACCURACY_TEST_ERROR_TOLERANCE = os.getenv("ACCURACY_TEST_ERROR_TOLERANCE")
        if ACCURACY_TEST_ERROR_TOLERANCE is not None:
            error_tolerance = int(ACCURACY_TEST_ERROR_TOLERANCE)

        with open(accuracy_output_path, mode='a', newline='', encoding='utf-8') as file:  # Apri il file in modalità di aggiunta (append)
            writer = csv.writer(file)

            writer.writerow([
                f"Q{questions_analyzed.index(best_similar['metadata']['domanda']) + 1}",
                best_similar['metadata']['domanda'],
                sentence_to_compare_text,
                best_similar['document'],
                best_similar['metadata']['id_autore'],
                round(best_similar['cosine_distance'], 3),
                round(best_similar['jaccard_distance'], 3),
                round(best_similar['combined_distance'], 3),
                best_similar['metadata']['voto_docente'],
                expected_vote,
                final_score,
                "PASSED" if abs(final_score - expected_vote) <= error_tolerance else "FAILED"
            ])

    return final_score


def get_similar_sentences(id_domanda: str, sentence_to_compare_text: str):
    q_a_collection = get_chroma_q_a_collection()

    results = q_a_collection.query(
        query_texts=[sentence_to_compare_text],
        n_results=10,
        where={"$and": [{"id_domanda": id_domanda},
                        {"voto_docente": {"$gt": -1}}]},  # seleziona solo le risposte valutate dal docente
        include=["documents", "metadatas", "embeddings", "distances"]
    )

    print(f"\t{Fore.YELLOW}{Style.BRIGHT}Found {len(results['documents'][0])} similar documents{Style.RESET_ALL}:")

    return results


def get_ref_sentence(id_domanda: str, teacher_username: str, sentence_to_compare_text: str):
    q_a_collection = get_chroma_q_a_collection()

    # seleziona solo la risposta di riferimento del docente
    results = q_a_collection.query(
        query_texts=[sentence_to_compare_text],
        n_results=1,
        where={"$and": [{"id_domanda": id_domanda},
                        {"id_autore": teacher_username}]},
        include=["documents", "metadatas", "embeddings", "distances"]
    )

    print(f"\t{Fore.YELLOW}{Style.BRIGHT}Found {len(results['documents'][0])} ref document for {id_domanda}{Style.RESET_ALL}:")

    return results


def add_answer_to_collection(authenticated_user, question: Question, answer_text: str,
                             error_callback=None, fake_add=False):
    # effettua una predizione del voto a partire dalla risposta di riferimento data dal docente
    predicted_vote_from_ref = predict_vote_from_ref(question.id, question.id_docente, answer_text)
    predicted_vote_from_all = predict_vote(question.id, answer_text)

    # Ottieni la data e l'ora correnti
    now = datetime.now()
    # Converti in formato ISO 8601
    iso_format = now.isoformat()

    id_risposta = generate_sha256_hash_from_text(f"{question.id}_{authenticated_user['username']}")

    if not fake_add:
        print(
            f"WARNING: {Fore.YELLOW}{Style.BRIGHT}FAKE ADD {fake_add}{Style.RESET_ALL}"
        )

        q_a_collection = get_chroma_q_a_collection()

        try:
            q_a_collection.add(
                documents=[answer_text],  # aggiunge la risposta ai documenti
                metadatas=[{"id_domanda": question.id,
                            "domanda": question.domanda,
                            "id_docente": question.id_docente,
                            "id_autore": authenticated_user['username'],
                            "voto_docente": -1,
                            "voto_predetto": predicted_vote_from_ref,
                            "voto_predetto_all": predicted_vote_from_all,
                            "commento": "undefined",
                            "source": "application",
                            "data_creazione": iso_format}],
                ids=[id_risposta]
            )
        except ValueError:
            if error_callback is not None:
                error_callback("Errore durante l'inserimento della risposta.")

            return None
    else:
        time.sleep(3)

    answer = Answer(
        id_risposta,
        question.id,
        question.domanda,
        question.id_docente,
        answer_text,
        authenticated_user['username'],
        -1,
        predicted_vote_from_ref,
        predicted_vote_from_all,
        "undefined",
        "application",
        iso_format,
    )

    return answer


def add_question_to_collection(authenticated_user, categoria: str, question_text: str,
                               ref_answer_text: str, error_callback=None, fake_add=False) -> Optional[Question]:

    # Ottieni la data e l'ora correnti
    now = datetime.now()
    # Converti in formato ISO 8601
    iso_format = now.isoformat()

    id_domanda = generate_sha256_hash_from_text(f"{authenticated_user['username']}_q_{iso_format}")
    id_risposta = generate_sha256_hash_from_text(f"{authenticated_user['username']}_a_{iso_format}")

    if not fake_add:
        print(
            f"\t{Fore.YELLOW}{Style.BRIGHT}FAKE ADD {fake_add}{Style.RESET_ALL}"
        )

        questions_collection = get_chroma_questions_collection()
        q_a_collection = get_chroma_q_a_collection()

        try:
            questions_collection.add(
                documents=[question_text],  # aggiunge la domanda ai documenti
                metadatas=[{"id_domanda": id_domanda,
                            "id_docente": authenticated_user['username'],
                            "categoria": categoria,
                            "source": "application",
                            "archived": False,
                            "data_creazione": iso_format}],
                ids=[id_domanda]
            )

            q_a_collection.add(
                documents=[ref_answer_text],  # aggiunge la risposta ai documenti
                metadatas=[{"id_domanda": id_domanda,
                            "domanda": question_text,
                            "id_docente": authenticated_user['username'],
                            "id_autore": authenticated_user['username'],
                            "voto_docente": 10,
                            "voto_predetto": -1,
                            "voto_predetto_all": -1,
                            "commento": "undefined",
                            "source": "application",
                            "data_creazione": iso_format}],
                ids=[id_risposta]
            )
        except ValueError:
            if error_callback is not None:
                error_callback("Errore durante l'inserimento della domanda.")

            return None
    else:
        time.sleep(3)

    question = Question(
        id_domanda,
        question_text,
        authenticated_user['username'],
        categoria,
        "application",
        False,
        iso_format,
    )

    return question


def get_collections():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    print("getting collections")

    question_collection = get_chroma_questions_collection()
    q_a_collection = get_chroma_q_a_collection()

    return question_collection, q_a_collection


def extract_data(query_result):
    result = []

    if query_result is not None:
        for i, metadata in enumerate(query_result['metadatas']):
            data = {
                'id': query_result['ids'][i],
                'document': query_result['documents'][i] if query_result['documents'] is not None else None,
                'embeddings': query_result['embeddings'][i] if query_result['embeddings'] is not None else None
            }
            for key, value in metadata.items():
                data[key] = value
            result.append(data)

    return result


def extract_metadata_from_query_result(data, key):
    # Inizializza una lista vuota per i valori di status
    metadata_values = []

    # Itera attraverso i dati per trovare tutte le occorrenze del valore 'key'
    for item in data:
        for sub_item in item:
            # Se la chiave è presente nell'elemento corrente, aggiungi il suo valore alla lista dei valori di status
            if key in sub_item:
                metadata_values.append(sub_item[key])

    # Restituisci la lista dei valori di status
    return metadata_values


def extract_metadata_from_get_result(data, key):
    # Inizializza una lista vuota per i valori di status
    metadata_values = []

    # Itera attraverso i dati per trovare tutte le occorrenze del valore 'key'
    for item in data:
        print("item", item)
        # Se la chiave è presente nell'elemento corrente, aggiungi il suo valore alla lista dei valori di status
        if key in item:
            metadata_values.append(item[key])

    # Restituisci la lista dei valori di status
    return metadata_values
