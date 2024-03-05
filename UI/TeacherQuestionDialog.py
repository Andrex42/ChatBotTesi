from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel


# Definizione di una finestra di dialogo per mostrare il testo della domanda
class QuestionDialog(QDialog):
    def __init__(self, question_text):
        super().__init__()
        self.setWindowTitle("Dettaglio Domanda")
        self.resize(200, 100)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(question_text))

        self.setLayout(layout)
