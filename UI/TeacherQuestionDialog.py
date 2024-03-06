from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from collection import extract_data


# Definizione di una finestra di dialogo per mostrare il testo della domanda
class QuestionDialog(QDialog):
    def __init__(self, question, answer_ready_event, students_answers_ready_event, load_callback):
        super().__init__()
        self.setWindowTitle("Dettaglio Domanda")
        self.resize(200, 100)

        self.answer_ready_event = answer_ready_event
        self.students_answers_ready_event = students_answers_ready_event

        self.load_callback = load_callback

        self.on_teacher_answer_ready_slot = lambda data: self.on_teacher_answer_ready(data)
        self.on_students_answers_ready_slot = lambda data: self.on_students_answers_ready(data)

        self.answer_ready_event.connect(self.on_teacher_answer_ready_slot)
        self.students_answers_ready_event.connect(self.on_students_answers_ready_slot)

        self.layout = QVBoxLayout()

        question_label = QLabel(question["document"])
        question_label.setWordWrap(True)
        self.layout.addWidget(question_label)

        self.teacher_answer_layout = QVBoxLayout()
        self.students_answers_layout = QVBoxLayout()

        self.teacher_answer_layout.addWidget(QLabel("Risposta docente"))
        self.students_answers_layout.addWidget(QLabel("Risposte studenti"))

        self.layout.addLayout(self.teacher_answer_layout)
        self.layout.addLayout(self.students_answers_layout)

        self.setLayout(self.layout)

        # Collega il segnale 'finished' del QDialog alla funzione che si occupa di eliminare i widget e il layout
        self.finished.connect(self.cleanup)

    @QtCore.pyqtSlot()
    def on_teacher_answer_ready(self, data):
        print("received", data)
        data_array = extract_data(data)
        print("data converted", data_array)

        for answer in data_array:
            answer_label = QLabel(answer["document"])
            answer_label.setWordWrap(True)
            self.teacher_answer_layout.addWidget(answer_label)

        self.load_callback()

        self.answer_ready_event.disconnect(self.on_teacher_answer_ready_slot)

    @QtCore.pyqtSlot()
    def on_students_answers_ready(self, data):
        print("received", data)
        data_array = extract_data(data)
        print("data converted", data_array)

        for answer in data_array:
            self.students_answers_layout.addWidget(QLabel(answer["student_id"]))

            answer_label = QLabel(answer["document"])
            answer_label.setWordWrap(True)
            self.students_answers_layout.addWidget(answer_label)

        self.load_callback()

        self.students_answers_ready_event.disconnect(self.on_students_answers_ready_slot)

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
