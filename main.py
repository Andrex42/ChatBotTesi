import sys
import argparse
# from document_similarity import get_letters_df, get_data_for_training, get_doc2vec

from PyQt5.QtWidgets import QApplication, QMainWindow
from UI.LoginFormApp import LoginFormApp


class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

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
