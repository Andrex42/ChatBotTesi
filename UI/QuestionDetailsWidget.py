from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidgetItem, QPushButton, QHBoxLayout, QScrollArea


class QuestionDetailsWidget(QWidget):

    def __init__(self, authorized_user):
        super().__init__()

        self.authorized_user = authorized_user

        self.__initUi()

    def __initUi(self):
        # self.label = QLabel("")

        self.teacher_answer_layout = QVBoxLayout()
        self.students_answers_layout = QVBoxLayout()

        scroll_vertical_layout = QVBoxLayout()
        scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_vertical_layout)
        scroll.setWidget(scroll_widget)
        # Scroll Area Properties
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        scroll_vertical_layout.addLayout(self.teacher_answer_layout)
        scroll_vertical_layout.addLayout(self.students_answers_layout)
        scroll_vertical_layout.addStretch()

        lay = QVBoxLayout()
        lay.addWidget(scroll)

        self.setLayout(lay)

    def replaceQuestion(self, question, data_array):
        self.cleanup()
        id, title = question['id'], question['document']

        question_label = QLabel(title)
        question_label.setStyleSheet('''
            QLabel {
                font-size: 14px; 
                font-weight: bold;
            }
        ''')
        question_label.setWordWrap(True)

        self.teacher_answer_layout.addWidget(QLabel("Domanda"))
        self.teacher_answer_layout.addWidget(question_label)

        risposte_studenti_label = QLabel("Risposte già corrette")
        risposte_studenti_label.setStyleSheet('''
            QLabel {
                font-size: 12px; 
                font-weight: bold;
            }
        ''')
        self.students_answers_layout.addWidget(risposte_studenti_label)

        for answer in data_array:
            answer_label = QLabel(answer["document"])
            answer_label.setWordWrap(True)

            if answer["id_autore"] == self.authorized_user['username']:
                self.teacher_answer_layout.addWidget(QLabel("Risposta di riferimento"))
                self.teacher_answer_layout.addWidget(answer_label)
            else:
                label_id_studente = QLabel("Studente: " + answer["id_autore"])
                label_id_studente.setStyleSheet('''
                    QLabel {
                        font-size: 12px; 
                        font-weight: bold;
                    }
                ''')
                self.students_answers_layout.addWidget(label_id_studente)
                self.students_answers_layout.addWidget(answer_label)

                label_risultato = QLabel(str(answer["voto_docente"]))
                if answer["voto_docente"] >= 3:
                    label_risultato.setStyleSheet('''
                        QLabel {
                            font-size: 12px; 
                            font-weight: bold;
                            color: #32a852;
                        }
                    ''')
                else:
                    label_risultato.setStyleSheet('''
                        QLabel {
                            font-size: 12px; 
                            font-weight: bold;
                            color: #a83232;
                        }
                    ''')
                self.students_answers_layout.addWidget(label_risultato)

    def cleanup(self):
        print()
        # Elimina tutti i widget dal layout
        while self.teacher_answer_layout.count():
            item = self.teacher_answer_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        while self.students_answers_layout.count():
            item = self.students_answers_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
