from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit


class EditQuestionDialog(QDialog):
    def __init__(self, question_text, save_callback):
        super().__init__()
        self.setWindowTitle("Modifica Domanda")
        self.resize(300, 100)

        self.save_callback = save_callback

        layout = QVBoxLayout()
        self.questionInput = QLineEdit(question_text)
        saveButton = QPushButton('Salva')

        layout.addWidget(QLabel('Modifica il testo della domanda:'))
        layout.addWidget(self.questionInput)
        layout.addWidget(saveButton)

        self.setLayout(layout)

        saveButton.clicked.connect(self.save)

    def save(self):
        self.save_callback(self.questionInput.text())
        self.accept()
