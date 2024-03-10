import chromadb
import os
import string
from dotenv import load_dotenv
import cohere
from cohere.responses.classify import Example
import pprint
import pandas as pd
import logging
import spacy
from halo import Halo
from datetime import datetime
from colorama import Fore, Style, init
from nltk.corpus import stopwords
from nltk.metrics import edit_distance
import chromadb.utils.embedding_functions as embedding_functions

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

load_dotenv()  # This loads environment variables from a .env file, which is good for sensitive info like API keys

pp = pprint.PrettyPrinter(indent=4)  # PrettyPrinter makes dictionary output easier to read

# Initializes the Cohere API key from the environment variables. Raises an error if the key isn't found.
COHERE_KEY = os.getenv("COHERE_KEY")
if COHERE_KEY is None:
    raise ValueError("Cohere API key not found in the environment variables.")


nlp = spacy.load("it_core_news_sm")
lemmatizer = nlp.get_pipe("lemmatizer")


# Initializes a CohereEmbeddingFunction, which is a specific function that generates embeddings
# using the Cohere model.
# These embeddings will be used to add and retrieve examples in the ChromaDB database.
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")
cohere_ef = embedding_functions.CohereEmbeddingFunction(api_key=COHERE_KEY,  model_name=os.getenv('COHERE_MODEL_NAME'))

remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
ita_stopwords = stopwords.words('italian')


def preprocess(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc])


chroma_client: chromadb.ClientAPI


def init_chroma_client():
    # Initializes the ChromaDB client with certain settings. These settings specify that the client should use DuckDB with Parquet for storage,
    # and it should store its data in a directory named 'database'.
    global chroma_client
    chroma_client = chromadb.PersistentClient(path="./chroma/data")


def get_chroma_q_a_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    # Gets or creates a ChromaDB collection named 'q_a', using the Cohere embedding function.
    # example_collection = chroma_client.get_or_create_collection(name="q_a", embedding_function=cohere_ef)
    # Gets or creates a ChromaDB collection named 'q_a',
    # using the SentenceTransformerEmbeddingFunction embedding function.
    q_a_collection = chroma_client.get_or_create_collection(name="q_a", embedding_function=sentence_transformer_ef)
    return q_a_collection


def get_chroma_questions_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    # Gets or creates a ChromaDB collection named 'questions', using the Cohere embedding function.
    # example_collection = chroma_client.get_or_create_collection(name="questions", embedding_function=cohere_ef)
    # Gets or creates a ChromaDB collection named 'questions',
    # using the SentenceTransformerEmbeddingFunction embedding function.
    questions_collection = chroma_client.get_or_create_collection(name="questions", embedding_function=sentence_transformer_ef)
    return questions_collection


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
                embeddings=sentence_transformer_ef([preprocess(item['text'])]),
                documents=[item['text']],  # aggiunge la domanda ai documenti
                metadatas=[{"id_docente": "docente.archeologia",
                            "categoria": item['label'],
                            "source": "internal__training",
                            "data_creazione": iso_format}],
                ids=[f"id_{index}"]
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
                embeddings=sentence_transformer_ef([preprocess(item['text'])]),
                documents=[item['text']],  # aggiunge la risposta ai documenti
                metadatas=[{"domanda": item['title'],
                            "id_autore": item['id_docente'],
                            "risultato": "Corretta",
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
                embeddings=sentence_transformer_ef([preprocess(item['text'])]),
                documents=[item['text']],  # aggiunge la risposta ai documenti
                metadatas=[{"domanda": item['title'],
                            "id_autore": "undefined",
                            "risultato": item['label'],
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


def generate_response(messages):
    spinner = Halo(text='Loading...', spinner='dots')  # Creates a loading animation
    spinner.start()

    co = cohere.Client(COHERE_KEY)  # Initializes the Cohere API client with your API key

    risultato = get_risultato_classification(messages, co)
    ambito = get_ambito_classification(messages, co)

    spinner.stop()  # Stops the loading animation after receiving the response

    mood_priority = {
        'Sbagliata': 1,
        'Corretta': 2
    }

    # Prints the user's mood, its priority level, and the responsible department
    print(
        f"\n{Fore.CYAN}Question Received: {Fore.WHITE}{Style.BRIGHT}{messages}{Style.RESET_ALL}"
        f"\n{Fore.GREEN}Mood Detected: {Fore.YELLOW}{Style.BRIGHT}{risultato}{Style.RESET_ALL}"
        f"\n{Fore.GREEN}Priority Level: {Fore.RED if mood_priority[risultato] == 1 else Fore.CYAN}{Style.BRIGHT}{mood_priority[risultato]}{Style.RESET_ALL}"
        f"\n{Fore.GREEN}Department to handle your request: {Fore.MAGENTA}{Style.BRIGHT}{ambito}{Style.RESET_ALL}"
    )

    print("_________________________________")

    return messages, risultato, ambito


def generate_response_full(data):
    spinner = Halo(text='Loading...', spinner='dots')  # Creates a loading animation
    spinner.start()

    co = cohere.Client(COHERE_KEY)  # Initializes the Cohere API client with your API key

    risultato = get_risultato_classification_full(data, co)
    #ambito = get_ambito_classification_full(data, co)

    spinner.stop()  # Stops the loading animation after receiving the response

    mood_priority = {
        'Sbagliata': 1,
        'Corretta': 2
    }

    # Prints the user's mood, its priority level, and the responsible department
    print(
        f"\n{Fore.CYAN}Question Received: {Fore.WHITE}{Style.BRIGHT}{data['text']}{Style.RESET_ALL}"
        #f"\n{Fore.GREEN}Mood Detected: {Fore.YELLOW}{Style.BRIGHT}{risultato}{Style.RESET_ALL}"
        #f"\n{Fore.GREEN}Priority Level: {Fore.RED if mood_priority[risultato] == 1 else Fore.CYAN}{Style.BRIGHT}{mood_priority[risultato]}{Style.RESET_ALL}"
        #f"\n{Fore.GREEN}Department to handle your request: {Fore.MAGENTA}{Style.BRIGHT}{ambito}{Style.RESET_ALL}"
    )

    print(
        f"{Fore.GREEN}Test Label: {Fore.YELLOW}{Style.BRIGHT}{data['label']}{Style.RESET_ALL}"
    )
    print(
        f"{Fore.GREEN}Result Detected: {Fore.YELLOW}{Style.BRIGHT}{risultato}{Style.RESET_ALL}"
    )

    if risultato == data['label']:
        print(
            f"{Fore.GREEN}Final Result: {Fore.GREEN}{Style.BRIGHT}[PASSED]{Style.RESET_ALL}"
        )
    else:
        print(
            f"{Fore.GREEN}Final Result: {Fore.RED}{Style.BRIGHT}[FAILED]{Style.RESET_ALL}"
        )


    print("_________________________________")

    return data['text'], risultato, "ambito"


# Two helper functions to get mood and department classification. They query examples from the ChromaDB collection,
# send a classification request to the Cohere API, and extract the prediction from the response.
def get_ambito_classification(messages, co):

    department_examples = []

    example_collection = get_chroma_q_a_collection()

    results = example_collection.query(
        query_texts=[messages],
        n_results=90
    )

    for doc, md in zip(results['documents'][0], results['metadatas'][0]):
        department_examples.append(Example(doc, md['ambito']))

    department_response = co.classify(
        model=os.getenv("COHERE_MODEL_NAME"),
        inputs=[messages],
        examples=department_examples
    )  # Sends the classification request to the Cohere model

    # Extracts the prediction from the response
    ambito = department_response.classifications[0].prediction
    return ambito


# Two helper functions to get mood and department classification. They query examples from the ChromaDB collection,
# send a classification request to the Cohere API, and extract the prediction from the response.
def get_ambito_classification_full(data, co):

    department_examples = []

    example_collection = get_chroma_q_a_collection()

    results = example_collection.query(
        query_texts=[data['text']],
        n_results=10,
        where={"domanda": data['title']}
    )

    for doc, md in zip(results['documents'][0], results['metadatas'][0]):
        department_examples.append(Example(doc, md['ambito']))

    department_response = co.classify(
        model=os.getenv("COHERE_MODEL_NAME"),
        inputs=[data['text']],
        examples=department_examples
    )  # Sends the classification request to the Cohere model

    # Extracts the prediction from the response
    ambito = department_response.classifications[0].prediction
    return ambito


def get_risultato_classification(messages, co):

    mood_examples = []

    example_collection = get_chroma_q_a_collection()

    results = example_collection.query(
        query_texts=[messages],
        n_results=90
    )

    for doc, md in zip(results['documents'][0], results['metadatas'][0]):
        mood_examples.append(Example(doc, md['risultato']))

    mood_response = co.classify(
        model=os.getenv("COHERE_MODEL_NAME"),
        inputs=[messages],
        examples=mood_examples
    )  # Sends the classification request to the Cohere model

    # Extracts the prediction from the response
    risultato = mood_response.classifications[0].prediction
    return risultato


def get_risultato_classification_full(data, co):

    mood_examples = []

    example_collection = get_chroma_q_a_collection()

    results = example_collection.query(
        query_embeddings=sentence_transformer_ef([preprocess(data['text'])]),
        n_results=20,
        where={"domanda": data['title']},
        include=["documents", "embeddings", "metadatas", "distances"]
    )

    print(f"{Fore.YELLOW}{Style.BRIGHT}Found {len(results['documents'][0])} similar documents{Style.RESET_ALL}:")

    for idx, doc in enumerate(results['documents'][0]):
        it_metadata = results['metadatas'][0][idx]
        it_distances = results['distances'][0][idx]
        print(f" - Doc {idx}: ({it_metadata['risultato']}) ({it_distances})", doc)

    correct_answers_results = example_collection.get(
        where={"$and": [{"domanda": data['title']}, {"risultato": "Corretta"}]}
    )

    # for doc, md in zip(results['documents'][0], results['metadatas'][0]):
    #     mood_examples.append(Example(doc, md['risultato']))

    min_distance = min(results['distances'][0])
    min_distance_index = results['distances'][0].index(min_distance)

    levenshtein_distance = edit_distance(data['text'], results['documents'][0][min_distance_index])

    print(f"\n{Fore.CYAN}Best similarity match{Style.RESET_ALL}:\n"
          f"\tCosine Distance: {results['distances'][0][min_distance_index]}"
          f"\tLevenshtein Distance: {levenshtein_distance}"
          f"\n\tRef. Result: {Fore.GREEN if results['metadatas'][0][min_distance_index]['risultato'] == 'Corretta' else Fore.RED}{results['metadatas'][0][min_distance_index]['risultato']}{Style.RESET_ALL}"
          f"\n\tDocument: {results['documents'][0][min_distance_index]}")

    return results['metadatas'][0][min_distance_index]['risultato']

    # if len(mood_examples) > 1:
    #     mood_response = co.classify(
    #         model=os.getenv("COHERE_MODEL_NAME"),
    #         inputs=[data['text']],
    #         examples=mood_examples
    #     )  # Sends the classification request to the Cohere model
#
    #     # Extracts the prediction from the response
    #     risultato = mood_response.classifications[0].prediction
#
    #     return risultato
    # elif len(mood_examples) == 1:
    #     return mood_examples[0].label
    # else:
    #     return "Non lo so"



















def encode(answer_text):
    print("encoding", answer_text)
    return cohere_ef([answer_text])


def get_collections():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    question_collection = chroma_client.get_or_create_collection(name="questions")
    q_a_collection = get_chroma_q_a_collection()

    return question_collection, q_a_collection


def get_question_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    question_collection = chroma_client.get_or_create_collection(name="questions")

    return question_collection


def get_teacher_answers_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    teacher_answers_collection = chroma_client.get_or_create_collection(name="teacher_answers", embedding_function=cohere_ef)

    return teacher_answers_collection


def get_student_answers_collection():
    if chroma_client is None:
        raise Exception("Chroma client not initialized")

    student_answers_collection = chroma_client.get_or_create_collection(name="student_answers", embedding_function=cohere_ef)

    return student_answers_collection


def extract_data(query_result):
    result = []
    for i, metadata in enumerate(query_result['metadatas']):
        data = {
            'id': query_result['ids'][i],
            'document': query_result['documents'][i]
        }
        for key, value in metadata.items():
            data[key] = value
        result.append(data)
    return result


def test_model():
    df_risposte = pd.read_csv('./training_data/risposte_test_archeologia_storia_arte.csv')

    risposte_dict = df_risposte.to_dict('records')

    correct = 0
    total = 0

    for id, item in enumerate(risposte_dict):  # per ogni risposta
        print("Domanda test:", item['title'])
        print(f"Risposta test:", item['text'])

        response, risultato, ambito = generate_response_full(item)

        if risultato == item['label']:
            correct += 1

        total += 1

    print("Accuracy:", correct / total)
