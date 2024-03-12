from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea

from UI.teacher.TeacherStudentAnswerPreviewItem import TeacherStudentAnswerPreviewItem
from model.question_model import Question


class QuestionDetailsWidget(QWidget):

    def __init__(self, authorized_user, db_worker):
        super().__init__()

        self.authorized_user = authorized_user
        self.db_worker = db_worker

        self.__initUi()

    def __initUi(self):
        # self.label = QLabel("")

        self.teacher_answer_layout = QVBoxLayout()

        self.question_label = QLabel("")
        self.question_label.setStyleSheet('''
                    QLabel {
                        font-size: 14px; 
                        font-weight: bold;
                    }
                ''')
        self.question_label.setWordWrap(True)

        self.answer_label = QLabel("")
        self.answer_label.setWordWrap(True)

        self.teacher_answer_layout.addWidget(QLabel("Domanda"))
        self.teacher_answer_layout.addWidget(self.question_label)
        self.teacher_answer_layout.addWidget(QLabel("Risposta di riferimento"))
        self.teacher_answer_layout.addWidget(self.answer_label)

        self.students_answers_layout = QVBoxLayout()

        self.students_answers_evaluated_layout = QVBoxLayout()
        self.students_answers_not_evaluated_layout = QVBoxLayout()

        risposte_studenti_label = QLabel("Risposte in attesa di valutazione")
        risposte_studenti_label.setStyleSheet('''
                    QLabel {
                        font-size: 12px; 
                        font-weight: bold;
                    }
                ''')
        self.students_answers_not_evaluated_layout.addWidget(risposte_studenti_label)

        risposte_studenti_label = QLabel("Risposte già valutate")
        risposte_studenti_label.setStyleSheet('''
                    QLabel {
                        font-size: 12px; 
                        font-weight: bold;
                    }
                ''')
        self.students_answers_evaluated_layout.addWidget(risposte_studenti_label)

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

        self.students_answers_layout.addLayout(self.students_answers_not_evaluated_layout)
        self.students_answers_layout.addLayout(self.students_answers_evaluated_layout)

        lay = QVBoxLayout()
        lay.addWidget(scroll)

        self.setLayout(lay)

    def replaceQuestion(self, question: Question, data_array):
        self.cleanup()

        self.question_label.setText(question.domanda)

        for answer in data_array:
            if answer["id_autore"] == self.authorized_user['username']:
                self.answer_label.setText(answer["document"])
            elif answer['voto_docente'] == -1:
                studentAnswerPreviewItemWidget = TeacherStudentAnswerPreviewItem(
                    self.db_worker, self.authorized_user, answer, False)
                self.students_answers_not_evaluated_layout.addWidget(studentAnswerPreviewItemWidget)
            else:
                studentAnswerPreviewItemWidget = TeacherStudentAnswerPreviewItem(
                    self.db_worker, self.authorized_user, answer, True)
                self.students_answers_evaluated_layout.addWidget(studentAnswerPreviewItemWidget)

    def cleanup(self):
        # Elimina tutti i widget dal layout tranne l'header della sezione
        while self.students_answers_not_evaluated_layout.count() > 1:
            item = self.students_answers_not_evaluated_layout.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        while self.students_answers_evaluated_layout.count() > 1:
            item = self.students_answers_evaluated_layout.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
