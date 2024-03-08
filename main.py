import sys
import argparse
# from document_similarity import get_letters_df, get_data_for_training, get_doc2vec

from PyQt5.QtWidgets import QApplication, QMainWindow
from UI.LoginFormApp import LoginFormApp

from collection import init_model, generate_response, get_chroma_cohere_collection


class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setup_ui()

        init_model()

        # A message to inform the user that they can type 'quit' to end the conversation.
        print("Type 'quit' at any time to end the conversation.")

        # An infinite loop that prompts the user for input, generates a response, and adds the response to the ChromaDB collection.
        # The loop breaks when the user types 'quit'.
        while True:
            input_text = input("You: ")

            if input_text.lower() == "quit":
                print("Goodbye!")
                break  # This breaks the infinite loop, ending the script.

            response, risultato, ambito = generate_response(input_text)

            example_collection = get_chroma_cohere_collection()

            # Adds the response to the ChromaDB collection.
            index = example_collection.count() if example_collection.count() is not None else 0
            example_collection.add(
                documents=[response],
                metadatas=[{"ambito": ambito,
                            "risultato": risultato}],
                ids=[f"id_{index}"]
            )

            # {"domanda": item['title'],
            #                             "risultato": item['label'],
            #                             "ambito": df_department[int(id/2)]['label']}



    def setup_ui(self):
        login_widget = LoginFormApp(self)


def main():
    """Main function

    Returns
    -------
    Np.array
        The tfidf vector representation of the text
    """
    app = QApplication(sys.argv)
    window = Application()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description="Execute the distance similarity")
    # PARSER.add_argument("-dist", "--distance", help="euclidean or cosine.")
    # PARSER.add_argument(
    #     "-p", "--path", help="Pickle path to the letters dict.")
    # PARSER.add_argument(
    #     "-t", "--target", help="The target letter year.")
    # PARSER.add_argument(
    #     "-n", "--number", help="The number of letters to return.")
    # PARSER.add_argument(
    #     "-pre", "--pretrained", help="The pretrained model to use in transformers.")

    # ARGS = PARSER.parse_args()

    main()
