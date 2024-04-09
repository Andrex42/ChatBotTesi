import pprint
import logging

import numpy as np
import pandas as pd
from colorama import Fore, Style
from halo import Halo
from collection import init_chroma_client, get_similar_sentences

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

pp = pprint.PrettyPrinter(indent=4)  # PrettyPrinter makes dictionary output easier to read

df_risposte = pd.read_csv('training_data/risposte_test.csv')

risposte_dict = df_risposte.to_dict('records')

correct = 0
total = 0

spinner = Halo(text='Loading...', spinner='dots')  # Creates a loading animation
spinner.start()

init_chroma_client()

for idx, item in enumerate(risposte_dict):  # per ogni risposta
    id_domanda = item['id_domanda']
    voto_giudice = item['label']

    print("")
    print("Domanda test:", item['title'])
    print("Risposta test:", item['text'])

    voto_predetto = get_similar_sentences(id_domanda, item['text'])

    print(
        f"{Fore.GREEN}Test Label: {Fore.YELLOW}{Style.BRIGHT}{voto_giudice}{Style.RESET_ALL}"
    )
    print(
        f"{Fore.GREEN}Final Score: {Fore.YELLOW}{Style.BRIGHT}{voto_predetto}{Style.RESET_ALL}"
    )

    if abs(voto_predetto - voto_giudice) <= 1:
        correct += 1

        print(
            f"{Fore.LIGHTBLACK_EX}Final Result: {Fore.GREEN}{Style.BRIGHT}[PASSED]{Style.RESET_ALL}"
        )
    else:
        print(
            f"{Fore.BLACK}Result: {Fore.RED}{Style.BRIGHT}[FAILED]{Style.RESET_ALL}"
        )

    total += 1

spinner.stop()  # Stops the loading animation after receiving the response

print("")
print("Accuracy:", correct / total)

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
