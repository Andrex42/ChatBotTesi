import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from UI.LoginFormApp import LoginFormApp

from collection import init_model, check_answer_records, test_model


class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

        init_model()
        # check_answer_records()
        # test_model()

        # # A message to inform the user that they can type 'quit' to end the conversation.
        # print("Type 'quit' at any time to end the conversation.")
#
        # # An infinite loop that prompts the user for input, generates a response, and adds the response to the ChromaDB collection.
        # # The loop breaks when the user types 'quit'.
        # while True:
        #     input_text = input("You: ")
#
        #     if input_text.lower() == "quit":
        #         print("Goodbye!")
        #         break  # This breaks the infinite loop, ending the script.
#
        #     response, risultato, ambito = generate_response(input_text)
#
        #     example_collection = get_chroma_cohere_collection()
#
        #     # Adds the response to the ChromaDB collection.
        #     index = example_collection.count() if example_collection.count() is not None else 0
        #     example_collection.add(
        #         documents=[response],
        #         metadatas=[{"ambito": ambito,
        #                     "risultato": risultato}],
        #         ids=[f"id_{index}"]
        #     )

    def __beforeClose(self):
        message = 'The window will be closed. Would you like to continue running this app in the background?'
        closeMessageBox = QMessageBox(self)
        closeMessageBox.setWindowTitle('Wait!')
        closeMessageBox.setText(message)
        closeMessageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        reply = closeMessageBox.exec()
        # Cancel
        if reply == QMessageBox.Cancel:
            return True
        else:
            # Yes
            if reply == QMessageBox.Yes:
                self.close()
            # No
            elif reply == QMessageBox.No:
                self.main_window.app.quit()

    def closeEvent(self, e):
        f = self.__beforeClose()
        if f:
            e.ignore()
        else:
            return super().closeEvent(e)

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
    app.setQuitOnLastWindowClosed(False)

    window = Application()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
