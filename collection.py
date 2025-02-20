import csv
import hashlib
import time
from typing import Optional
import chromadb
import os
import sys
import numpy as np
from typing import List
from chromadb.utils import embedding_functions
from chromadb.config import Settings
from dotenv import load_dotenv
import pprint
import pandas as pd
import logging
from datetime import datetime
from colorama import Fore, Style
from model.answer_model import Answer
from model.question_model import Question
import openai

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

openai.api_key = 'KEY OPENAI PERSONALE'
extDataDir = os.getcwd()
if getattr(sys, 'frozen', False):
    extDataDir = sys._MEIPASS
load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))

pp = pprint.PrettyPrinter(indent=4) 

PRETRAINED_MODEL_NAME = os.getenv("PRETRAINED_MODEL_NAME")
if PRETRAINED_MODEL_NAME is None:
    raise ValueError("Pretrained model name not found in the environment variables.")

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=PRETRAINED_MODEL_NAME
)


chroma_client: chromadb.ClientAPI


def init_chroma_client():

    global chroma_client
    if 'chroma_client' not in globals():
        chroma_client = chromadb.PersistentClient(path="./chroma/data", settings=Settings(anonymized_telemetry=False))


def get_chroma_q_a_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    q_a_collection = chroma_client.get_or_create_collection(
        name="q_a",
        metadata={"hnsw:space": "cosine"},
        embedding_function=embedding_func)
    return q_a_collection


def get_chroma_questions_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    print("getting get_chroma_questions_collection")

    questions_collection = chroma_client.get_or_create_collection(
        name="questions",
        metadata={"hnsw:space": "cosine"},
        embedding_function=embedding_func
    )
    return questions_collection


def generate_sha256_hash_from_text(text):
    
    sha256_hash = hashlib.sha256()
    
    sha256_hash.update(text.encode('utf-8'))
    
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
        
        df_domande = pd.read_csv(file_domande)
        
        domande_dict = df_domande.to_dict('records')

        domande_collection_result = domande_collection.get(include=[])

        for idx, item in enumerate(domande_dict):
            id_domanda = item['id'] if not item['id'].startswith("id_") else generate_sha256_hash_from_text(item['id'])

            if id_domanda not in domande_collection_result['ids']:
                print(f"Adding question", idx, item['text'])

                domande_collection.add(
                    documents=[item['text']],  
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
        
        df_risposte = pd.read_csv(file_risposte)
        
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
                    documents=[item['text']], 
                    metadatas=[{"id_domanda": id_domanda,
                                "domanda": item['title'],
                                "id_docente": item['id_docente'],
                                "id_autore": item['id_autore'],
                                "voto_docente": int(item['label']),
                                "voto_predetto": int(item['voto_predetto']),
                                "voto_predetto_all": int(item['voto_predetto_all']),
                                "chat_gpt_rating": int(item['chat_gpt_rating']),
                                "use_as_ref": item.get('use_as_ref', False),
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


def calcola_voto_finale_ponderato(punteggi, voti):
    if len(punteggi) == 0:
        raise ValueError("I punteggi non possono essere vuoti")

    if punteggi[0] == 0 or len(punteggi) == 1:
        
        return voti[0]

    distanze = np.array(punteggi)
    initial_threshold = 0.1

    
    num_distanze = len(distanze)

    
    reduced_threshold = initial_threshold
    num_distanze_minime = 2

   
    fattore_riduzione = 0.1  

    
    if num_distanze > num_distanze_minime:
        reduced_threshold = initial_threshold * np.exp(-fattore_riduzione * (num_distanze - num_distanze_minime))

    
    pesi_modificati = np.exp(-distanze / reduced_threshold)

    
    pesi_modificati = pesi_modificati / np.sum(pesi_modificati)

    print(
        f"\t{Fore.LIGHTBLACK_EX}Reduced threshold: {reduced_threshold}"
    )

    print(
        f"\t{Fore.LIGHTBLACK_EX}Document distances weights modified: {pesi_modificati}"
    )

    if pesi_modificati[0] >= 0.9:
        
        voto_finale_ponderato = voti[0]
    else:
        
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

   
    if min_distance > reduction_end:
        return 1

    
    if min_distance < reduction_start:
        return score

    
    percentage_to_subtract = (min_distance - reduction_start) / (reduction_end - reduction_start)

    print(
        f"\t{Fore.LIGHTBLACK_EX}Percentage to subtract: {percentage_to_subtract}"
    )

    adjusted_result = max(score * (1 - percentage_to_subtract), 1)  

    return round(adjusted_result)  


def calc_jaccard_distance(embedding1, embedding2):
    
    set1 = set(np.where(embedding1 > 0)[0])
    set2 = set(np.where(embedding2 > 0)[0])
    jaccard_distance = 1 - len(set1.intersection(set2)) / len(set1.union(set2))

    return jaccard_distance

def get_chatgpt_rating(question_text, answer_text):
    """
    Valuta la risposta fornita in base alla domanda, restituendo un voto da 1 a 10.
    """
    prompt = f"Valuta la seguente risposta in base alla domanda associata su una scala da 1 a 10 senza fornire spiegazioni.\n\n" \
             f"Domanda: {question_text}\n" \
             f"Risposta: {answer_text}"
    print(f"Valutazione richiesta per la domanda: '{question_text}' e la risposta: '{answer_text}'")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": "Sei un valutatore imparziale che assegna un voto da 1 a 10 basato sulla qualità delle risposte in relazione alle domande."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=5,
            temperature=0.0
        )
        valutazione = response['choices'][0]['message']['content'].strip()
        
        
        if valutazione.lower().startswith("voto:"):
            valutazione = valutazione.split(":")[1].strip()
        
        return int(valutazione)
    except openai.error.OpenAIError as e:
        print(f"Errore nell'invio della richiesta a ChatGPT: {e}")
        return "Errore durante la richiesta"


def predict_vote_from_ref(id_domanda: str, teacher_username: str, sentence_to_compare_text, export_folder='', expected_vote=-1, questions_analyzed=None):
    if questions_analyzed is None:
        questions_analyzed = []

    results = get_ref_sentence(id_domanda, teacher_username, sentence_to_compare_text)

    accuracy_output_path = ''
    distances_output_path = ''

    if export_folder != '':
        accuracy_file_name = f"export_ref_only_accuracy_test.csv"
        distances_file_name = f"export_ref_only_distances_test.csv"

        
        accuracy_output_path = os.path.join(export_folder, accuracy_file_name)
        distances_output_path = os.path.join(export_folder, distances_file_name)

        if not os.path.exists(accuracy_output_path):
            
            with open(accuracy_output_path, mode='w', newline='', encoding='utf-8') as file:
                
                writer = csv.DictWriter(
                    file,
                    fieldnames=['q_short_id', 'question', 'answer', 'most_similar_answer', 'most_similar_answer_author_id', 'cosine_distance', 'jaccard_distance', 'combined_distance', 'most_similar_answer_vote', 'expected_vote', 'predicted_vote', 'result']
                )

                
                writer.writeheader()

        if not os.path.exists(distances_output_path):
            
            with open(distances_output_path, mode='w', newline='', encoding='utf-8') as file:
                
                writer = csv.DictWriter(
                    file,
                    fieldnames=['q_short_id', 'question', 'answer', 'similar_answer', 'similar_answer_author_id', 'cosine_distance', 'jaccard_distance', 'combined_distance', 'similar_answer_vote', 'expected_vote']
                )

                
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
                      encoding='utf-8') as file:  
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

        with open(accuracy_output_path, mode='a', newline='', encoding='utf-8') as file:  
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

        
        accuracy_output_path = os.path.join(export_folder, accuracy_file_name)
        distances_output_path = os.path.join(export_folder, distances_file_name)

        if not os.path.exists(accuracy_output_path):
            
            with open(accuracy_output_path, mode='w', newline='', encoding='utf-8') as file:
                
                writer = csv.DictWriter(
                    file,
                    fieldnames=['q_short_id', 'question', 'answer', 'most_similar_answer', 'most_similar_answer_author_id', 'cosine_distance', 'jaccard_distance', 'combined_distance', 'most_similar_answer_vote', 'expected_vote', 'predicted_vote', 'result']
                )

                
                writer.writeheader()

        if not os.path.exists(distances_output_path):
            
            with open(distances_output_path, mode='w', newline='', encoding='utf-8') as file:
                
                writer = csv.DictWriter(
                    file,
                    fieldnames=['q_short_id', 'question', 'answer', 'similar_answer', 'similar_answer_author_id', 'cosine_distance', 'jaccard_distance', 'combined_distance', 'similar_answer_vote', 'expected_vote']
                )

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
                      encoding='utf-8') as file:
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

        with open(accuracy_output_path, mode='a', newline='', encoding='utf-8') as file:  
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
                        {"voto_docente": {"$gt": -1}},
                        {"use_as_ref": True}]}, 
        include=["documents", "metadatas", "embeddings", "distances"]
    )

    print(f"\t{Fore.YELLOW}{Style.BRIGHT}Found {len(results['documents'][0])} similar documents{Style.RESET_ALL}:")

    return results


def get_ref_sentence(id_domanda: str, teacher_username: str, sentence_to_compare_text: str):
    q_a_collection = get_chroma_q_a_collection()

    
    results = q_a_collection.query(
        query_texts=[sentence_to_compare_text],
        n_results=1,
        where={"$and": [{"id_domanda": id_domanda},
                        {"id_autore": teacher_username}]},
        include=["documents", "metadatas", "embeddings", "distances"]
    )

    print(f"\t{Fore.YELLOW}{Style.BRIGHT}Found {len(results['documents'][0])} ref document for {id_domanda}{Style.RESET_ALL}:")

    return results


def add_answers_to_collection(authenticated_user, question: Question, responses: List[str]):
    now = datetime.now().isoformat()

    if not responses:
        print("Nessuna risposta fornita")
        return []

    print(f"Inserendo {len(responses)} risposte nel database...")

    q_a_collection = get_chroma_q_a_collection()
    answers = []

    for i, answer_text in enumerate(responses):
        student_id = "studente.archeologia" if i == 0 else f"studente{i}.archeologia"
        id_risposta = generate_sha256_hash_from_text(f"{question.id}_{student_id}_{answer_text[:10]}")

        
        chatgpt_rating = get_chatgpt_rating(question.domanda, answer_text)
        print(f"Voto ChatGPT per la risposta {i}: {chatgpt_rating}")  

        try:
            q_a_collection.add(
                documents=[answer_text],
                metadatas=[{
                    "id_domanda": question.id,
                    "domanda": question.domanda,
                    "id_docente": question.id_docente,
                    "id_autore": student_id,
                    "voto_docente": -1,
                    "voto_predetto": -1,
                    "voto_predetto_all": -1,
                    "chat_gpt_rating": chatgpt_rating,  
                    "use_as_ref": False,
                    "commento": "undefined",
                    "source": "application",
                    "data_creazione": now
                }],
                ids=[id_risposta]
            )

            print(f"Risposta {id_risposta} salvata con rating ChatGPT: {chatgpt_rating}")  

            update_chatgpt_rating(id_risposta)

            answers.append(Answer(
                id=id_risposta,
                id_domanda=question.id,
                domanda=question.domanda,
                id_docente=question.id_docente,
                risposta=answer_text.strip(),
                id_autore=student_id,
                voto_docente=-1,
                voto_predetto=-1,
                voto_predetto_all=-1,
                chat_gpt_rating=chatgpt_rating,  
                use_as_ref=False,
                commento="undefined",
                source="application",
                data_creazione=now,
            ))

        except ValueError as e:
            print(f"Errore durante l'inserimento della risposta: {e}")

    return answers


def update_chatgpt_rating(answer_id):
    q_a_collection = get_chroma_q_a_collection()

    
    answer_data = q_a_collection.get(ids=[answer_id], include=["documents", "metadatas"])

    if not answer_data['documents']:
        print(f"Errore: Nessuna risposta trovata con ID {answer_id}")
        return

    
    question_text = answer_data['metadatas'][0]['domanda']
    answer_text = answer_data['documents'][0]

    
    chatgpt_rating = get_chatgpt_rating(question_text, answer_text)
    print(f"Nuovo voto ChatGPT: {chatgpt_rating}")  

    
    q_a_collection.update(
        ids=[answer_id],
        metadatas=[{"chat_gpt_rating": chatgpt_rating}]
    )

    print(f"Voto aggiornato per la risposta {answer_id}: ChatGPT {chatgpt_rating}")



def add_question_to_collection(authenticated_user, categoria: str, question_text: str,
                               ref_answer_text: str, error_callback=None, fake_add=False) -> Optional[Question]:

    
    now = datetime.now()
    
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
                documents=[question_text],  
                metadatas=[{"id_domanda": id_domanda,
                            "id_docente": authenticated_user['username'],
                            "categoria": categoria,
                            "source": "application",
                            "archived": False,
                            "data_creazione": iso_format}],
                ids=[id_domanda]
            )

            q_a_collection.add(
                documents=[ref_answer_text],  
                metadatas=[{"id_domanda": id_domanda,
                            "domanda": question_text,
                            "id_docente": authenticated_user['username'],
                            "id_autore": authenticated_user['username'],
                            "voto_docente": 10,
                            "voto_predetto": -1,
                            "voto_predetto_all": -1,
                            "chat_gpt_rating" : -1,
                            "use_as_ref": True,  
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
    
    metadata_values = []

    
    for item in data:
        for sub_item in item:
            
            if key in sub_item:
                metadata_values.append(sub_item[key])

    
    return metadata_values


def extract_metadata_from_get_result(data, key):
    
    metadata_values = []

    
    for item in data:
        print("item", item)
        
        if key in item:
            metadata_values.append(item[key])

    
    return metadata_values
