from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from collection import extract_data


# Definizione di una finestra di dialogo per mostrare il testo della domanda
class QuestionDialog(QDialog):
    def __init__(self, question, answer_ready_event, load_callback):
        super().__init__()
        self.setWindowTitle("Dettaglio Domanda")
        self.resize(200, 100)

        self.answer_ready_event = answer_ready_event
        self.load_callback = load_callback

        self.on_finish_slot = lambda data: self.on_finish(data)
        self.answer_ready_event.connect(self.on_finish_slot)

        self.layout = QVBoxLayout()
        question_label = QLabel(question["document"])
        question_label.setWordWrap(True)
        self.layout.addWidget(question_label)

        self.setLayout(self.layout)

        # Collega il segnale 'finished' del QDialog alla funzione che si occupa di eliminare i widget e il layout
        self.finished.connect(self.cleanup)

    @QtCore.pyqtSlot()
    def on_finish(self, data):
        print("received", data)
        data_array = extract_data(data)
        print("data converted", data_array)

        for answer in data_array:
            answer_label = QLabel(answer["document"])
            answer_label.setWordWrap(True)
            self.layout.addWidget(answer_label)

        self.load_callback()

        self.answer_ready_event.disconnect(self.on_finish_slot)

    def cleanup(self):
        print("cleanup dialog")

        # Elimina tutti i widget dal layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Elimina il layout dal QDialog
        self.layout = None
