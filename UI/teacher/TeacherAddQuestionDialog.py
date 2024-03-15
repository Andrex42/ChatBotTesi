from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit


class AddQuestionDialog(QDialog):
    def __init__(self, parent, save_callback):
        super().__init__(parent=parent)
        self.setWindowTitle("Aggiungi Domanda")
        self.resize(400, 300)
        self.setModal(True)

        self.save_callback = save_callback

        layout = QVBoxLayout()
        self.categoriaLineEdit = QLineEdit()
        self.categoriaLineEdit.setPlaceholderText("Inserisci categoria")
        self.questionTextEdit = QTextEdit()
        self.questionTextEdit.setAcceptRichText(False)
        self.questionTextEdit.setPlaceholderText("Inserisci domanda")
        self.questionTextEdit.setFocus()
        self.answerTextEdit = QTextEdit()
        self.answerTextEdit.setAcceptRichText(False)
        self.answerTextEdit.setPlaceholderText("Inserisci risposta di riferimento")
        self.saveButton = QPushButton('Salva')
        self.saveButton.setEnabled(False)

        layout.addWidget(QLabel('Aggiungi una nuova domanda'))
        layout.addWidget(self.categoriaLineEdit)
        layout.addWidget(self.questionTextEdit)
        layout.addWidget(self.answerTextEdit)
        layout.addWidget(self.saveButton)

        self.setLayout(layout)

        self.categoriaLineEdit.textChanged.connect(self.checkTextEdit)
        self.questionTextEdit.textChanged.connect(self.checkTextEdit)
        self.answerTextEdit.textChanged.connect(self.checkTextEdit)
        self.saveButton.clicked.connect(self.save)

    def checkTextEdit(self):
        # Controlla se il QTextEdit contiene del testo
        if self.categoriaLineEdit.text() and self.questionTextEdit.toPlainText() and self.answerTextEdit.toPlainText():
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)

    def save(self):
        self.save_callback(
            self.categoriaLineEdit.text(),
            self.questionTextEdit.toPlainText(),
            self.answerTextEdit.toPlainText())
        self.accept()
