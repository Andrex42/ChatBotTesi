import datetime
import os
import pprint
import logging
import pandas as pd
from colorama import Fore, Style
from collection import init_chroma_client, predict_vote_from_ref, predict_vote

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

pp = pprint.PrettyPrinter(indent=4) 

export_folder = "export_accuracy_test"
df_risposte = pd.read_csv('training_data/risposte_test.csv')

risposte_dict = df_risposte.to_dict('records')


init_chroma_client()


def test_ref_answer_predictions():
    correct = 0
    total = 0
    error_tolerance = 1

    ACCURACY_TEST_ERROR_TOLERANCE = os.getenv("ACCURACY_TEST_ERROR_TOLERANCE")
    if ACCURACY_TEST_ERROR_TOLERANCE is not None:
        error_tolerance = int(ACCURACY_TEST_ERROR_TOLERANCE)

    questions_analyzed = []

    for idx, item in enumerate(risposte_dict):  
        id_domanda = item['id_domanda']
        voto_giudice = item['label']

        if item['title'] not in questions_analyzed:
            questions_analyzed.append(item['title'])

        print("")
        print("Domanda test:", item['title'])
        print("Risposta test:", item['text'])
        print("")

        voto_predetto = predict_vote_from_ref(id_domanda,
                                              item['id_docente'],
                                              item['text'],
                                              test_export_folder,
                                              voto_giudice,
                                              questions_analyzed)

        print(
            f"\t{Fore.GREEN}Test Label: {Fore.YELLOW}{Style.BRIGHT}{voto_giudice}{Style.RESET_ALL}"
        )
        print(
            f"\t{Fore.GREEN}Predicted Vote: {Fore.YELLOW}{Style.BRIGHT}{voto_predetto}{Style.RESET_ALL}"
        )

        if abs(voto_predetto - voto_giudice) <= error_tolerance:
            correct += 1

            print(
                f"\t{Fore.BLACK}Result: {Fore.GREEN}{Style.BRIGHT}[PASSED]{Style.RESET_ALL}"
            )
        else:
            print(
                f"\t{Fore.BLACK}Result: {Fore.RED}{Style.BRIGHT}[FAILED]{Style.RESET_ALL}"
            )

        total += 1

    accuracy = correct / total

    print("")
    print(f"Test exported successfully: {test_export_folder}")
    print(f"Accuracy: {correct}/{total}", f"{Fore.GREEN if accuracy > 0.5 else Fore.RED}{Style.BRIGHT}{accuracy}{Style.RESET_ALL}")


def test_multi_answers_predictions():
    correct = 0
    total = 0
    error_tolerance = 1

    ACCURACY_TEST_ERROR_TOLERANCE = os.getenv("ACCURACY_TEST_ERROR_TOLERANCE")
    if ACCURACY_TEST_ERROR_TOLERANCE is not None:
        error_tolerance = int(ACCURACY_TEST_ERROR_TOLERANCE)

    questions_analyzed = []

    for idx, item in enumerate(risposte_dict):  
        id_domanda = item['id_domanda']
        voto_giudice = item['label']

        if item['title'] not in questions_analyzed:
            questions_analyzed.append(item['title'])

        print("")
        print("Domanda test:", item['title'])
        print("Risposta test:", item['text'])
        print("")

        voto_predetto = predict_vote(id_domanda, item['text'], test_export_folder, voto_giudice, questions_analyzed)

        print(
            f"\t{Fore.GREEN}Test Label: {Fore.YELLOW}{Style.BRIGHT}{voto_giudice}{Style.RESET_ALL}"
        )
        print(
            f"\t{Fore.GREEN}Predicted Vote: {Fore.YELLOW}{Style.BRIGHT}{voto_predetto}{Style.RESET_ALL}"
        )

        if abs(voto_predetto - voto_giudice) <= error_tolerance:
            correct += 1

            print(
                f"\t{Fore.BLACK}Result: {Fore.GREEN}{Style.BRIGHT}[PASSED]{Style.RESET_ALL}"
            )
        else:
            print(
                f"\t{Fore.BLACK}Result: {Fore.RED}{Style.BRIGHT}[FAILED]{Style.RESET_ALL}"
            )

        total += 1

    accuracy = correct / total

    print("")
    print(f"Test exported successfully: {test_export_folder}")
    print(f"Accuracy: {correct}/{total}", f"{Fore.GREEN if accuracy > 0.5 else Fore.RED}{Style.BRIGHT}{accuracy}{Style.RESET_ALL}")


try:
    list_dir = os.listdir(export_folder)
    test_folders_count = sum(os.path.isdir(os.path.join(export_folder, el)) for el in list_dir)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    test_folder = f"test_{timestamp}"
    test_export_folder = os.path.join(export_folder, test_folder)
    os.mkdir(test_export_folder)

    test_multi_answers_predictions()
    test_ref_answer_predictions()

except OSError as e:
    print("Si è verificato un errore:", e)
