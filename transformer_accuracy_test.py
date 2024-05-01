import os
import pprint
import logging
import pandas as pd
from colorama import Fore, Style
from collection import init_chroma_client, predict_vote

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

pp = pprint.PrettyPrinter(indent=4)  # PrettyPrinter makes dictionary output easier to read

export_folder = "export_accuracy_test"
df_risposte = pd.read_csv('training_data/risposte_test.csv')

risposte_dict = df_risposte.to_dict('records')

correct = 0
total = 0
error_tolerance = 2

init_chroma_client()

exported_count = len([name for name in os.listdir(export_folder) if name.endswith(".csv")])
exported_count += 1

for idx, item in enumerate(risposte_dict):  # per ogni risposta
    id_domanda = item['id_domanda']
    voto_giudice = item['label']

    print("")
    print("Domanda test:", item['title'])
    print("Risposta test:", item['text'])
    print("")

    voto_predetto = predict_vote(id_domanda, item['text'], export_folder, exported_count, voto_giudice)

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
print(f"Accuracy: {correct}/{total}", f"{Fore.GREEN if accuracy > 0.5 else Fore.RED}{Style.BRIGHT}{accuracy}{Style.RESET_ALL}")

# initial_threshold = 0.1
# # Soglia iniziale per i valori più bassi di num_distanze
# soglia_ridotta = initial_threshold
# num_distanze_minime = 2
#
#
# for i in range(10):
#     # Calcolo del numero di distanze
#     num_distanze = i
#
#     # Fattore di riduzione esponenziale
#     fattore_riduzione = 0.05  # Puoi regolare questo valore in base alla velocità di riduzione desiderata
#
#     # Calcolo della soglia ridotta in modo esponenziale solo per i valori più alti di num_distanze
#     if num_distanze > num_distanze_minime:
#         soglia_ridotta = initial_threshold * np.exp(-fattore_riduzione * (num_distanze - num_distanze_minime))
#
#     print(f"Soglia ({i}) ridotta:", soglia_ridotta)
