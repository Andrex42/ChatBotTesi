from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget
from collection import extract_data


from model.question_model import Question


class QuestionDialog(QDialog):
    def __init__(self, authorized_user, question: Question, q_a_ready_event, load_callback):
        super().__init__()
        self.setWindowTitle("Dettaglio Domanda")
        self.setMinimumSize(500, 300)
        self.resize(500, 300)

        self.dialog_main_layout = QVBoxLayout()

        self.teacher_answer_layout = QVBoxLayout()
        self.dialog_main_layout.addLayout(self.teacher_answer_layout)

        
        question_label = QLabel(question.domanda)
        question_label.setWordWrap(True)
        self.teacher_answer_layout.addWidget(question_label)
        self.teacher_answer_layout.addWidget(QLabel("Risposta di riferimento"))

        scroll_vertical_layout = QVBoxLayout()

        scroll = QScrollArea()  
        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_vertical_layout)

        scroll.setWidget(scroll_widget)

        
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        self.authorized_user = authorized_user
        self.q_a_ready_event = q_a_ready_event
        self.load_callback = load_callback

        self.on_q_a_ready_slot = lambda data: self.on_q_a_ready(data)
        self.q_a_ready_event.connect(self.on_q_a_ready_slot)

        self.students_answers_layout = QVBoxLayout()

        self.students_answers_layout.addWidget(QLabel("Risposte studenti"))

        scroll_vertical_layout.addLayout(self.students_answers_layout)

        scroll_vertical_layout.addStretch()

        self.dialog_main_layout.addWidget(scroll)
        self.setLayout(self.dialog_main_layout)

        
        self.finished.connect(self.cleanup)

    @QtCore.pyqtSlot()
    def on_q_a_ready(self, data):
        print("received", data)
        data_array = extract_data(data)
        print("data converted", data_array)

        for answer in data_array:
            answer_label = QLabel(answer["document"])
            answer_label.setWordWrap(True)

            if answer["id_autore"] == self.authorized_user['username']:
                self.teacher_answer_layout.addWidget(answer_label)
            else:
                self.students_answers_layout.addWidget(QLabel(answer["id_autore"]))
                self.students_answers_layout.addWidget(answer_label)
                self.students_answers_layout.addWidget(QLabel(str(answer["voto_docente"])))

        self.load_callback()

        self.q_a_ready_event.disconnect(self.on_q_a_ready_slot)

    def cleanup(self):
        print("cleanup dialog")

        
        while self.dialog_main_layout.count():
            item = self.dialog_main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

       
        self.dialog_main_layout = None
