from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QMessageBox, QPushButton, QHBoxLayout, QFrame

from UI.teacher.TeacherStudentAnswerPreviewItem import TeacherStudentAnswerPreviewItem
from model.answer_model import Answer
from model.question_model import Question


class QuestionDetailsWidget(QWidget):

    def __init__(self, authorized_user, db_worker):
        super().__init__()

        self.authorized_user = authorized_user
        self.db_worker = db_worker
        self.id_domanda = None

        self.__initUi()
        self.hide()

    def __initUi(self):
        # self.label = QLabel("")
        teacher_question_container = QWidget(self)
        teacher_question_container.setObjectName("teacher_container")  # Setta un ID per il container
        teacher_question_container.setStyleSheet('''
            #teacher_container {
                background-color: rgba(52, 143, 235, 0.1);
                border-radius: 20px;
            }''')

        self.teacher_answer_layout = QVBoxLayout(teacher_question_container)

        self.question_label = QLabel("-")
        self.question_label.setStyleSheet('''
                    QLabel {
                        font-size: 14px; 
                        font-weight: bold;
                    }
                ''')
        self.question_label.setWordWrap(True)

        self.answer_label = QLabel("-")
        self.answer_label.setWordWrap(True)

        self.btnRecalc = QPushButton("Ricalcola")
        self.btnRecalc.clicked.connect(lambda:
                                       self.db_worker.recalc_question_unevaluated_answers_predictions(self.id_domanda))

        lbl = QLabel("DOMANDA")
        lbl.setStyleSheet('''
                    QLabel {
                        font-size: 12px; 
                        font-weight: 300;
                    }
                ''')
        self.teacher_answer_layout.addWidget(lbl)
        self.teacher_answer_layout.addWidget(self.question_label)

        lbl = QLabel("RISPOSTA DI RIFERIMENTO")
        lbl.setStyleSheet('''
                            QLabel {
                                font-size: 12px; 
                                font-weight: 300;
                            }
                        ''')
        self.teacher_answer_layout.addWidget(lbl)
        self.teacher_answer_layout.addWidget(self.answer_label)

        self.students_answers_layout = QVBoxLayout()

        self.students_answers_evaluated_layout = QVBoxLayout()
        self.students_answers_not_evaluated_layout = QVBoxLayout()

        risposte_studenti_label = QLabel("RISPOSTE DEGLI STUDENTI IN ATTESA DI VALUTAZIONE")
        risposte_studenti_label.setStyleSheet('''
                    QLabel {
                        font-size: 12px; 
                        font-weight: 300;
                    }
                ''')
        self.students_answers_not_evaluated_layout.insertSpacing(10, 20)
        self.students_answers_not_evaluated_layout.addWidget(risposte_studenti_label)
        #self.students_answers_not_evaluated_layout.addWidget(self.btnRecalc)

        risposte_studenti_label = QLabel("RISPOSTE DEGLI STUDENTI GIÀ VALUTATE")
        risposte_studenti_label.setStyleSheet('''
                    QLabel {
                        font-size: 12px; 
                        font-weight: 300;
                    }
                ''')
        self.students_answers_evaluated_layout.insertSpacing(10, 20)
        self.students_answers_evaluated_layout.addWidget(risposte_studenti_label)

        scroll_vertical_layout = QVBoxLayout()
        scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_widget = QWidget()

        scroll_widget.setLayout(scroll_vertical_layout)
        scroll.setWidget(scroll_widget)
        # Scroll Area Properties
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        scroll_vertical_layout.addWidget(teacher_question_container)
        scroll_vertical_layout.addLayout(self.students_answers_layout)
        scroll_vertical_layout.addStretch()

        self.students_answers_layout.addLayout(self.students_answers_not_evaluated_layout)
        self.students_answers_layout.addLayout(self.students_answers_evaluated_layout)

        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(scroll)

        self.setLayout(lay)

    def replaceQuestion(self, question: Question, data_array):
        self.cleanup()

        self.id_domanda = question.id
        self.question_label.setText(question.domanda)

        for answer_dict in data_array:
            answer = Answer(
                answer_dict['id'],
                answer_dict['id_domanda'],
                answer_dict['domanda'],
                answer_dict['id_docente'],
                answer_dict['document'],
                answer_dict['id_autore'],
                answer_dict['voto_docente'],
                answer_dict['voto_predetto'],
                answer_dict['commento'],
                answer_dict['source'],
                answer_dict['data_creazione'],
            )

            if answer.id_autore == self.authorized_user['username']:
                self.answer_label.setText(answer.risposta)
            elif answer.voto_docente == -1:
                studentAnswerPreviewItemWidget = TeacherStudentAnswerPreviewItem(
                    self.db_worker, self.authorized_user, answer, False)
                self.students_answers_not_evaluated_layout.addWidget(studentAnswerPreviewItemWidget)
            else:
                studentAnswerPreviewItemWidget = TeacherStudentAnswerPreviewItem(
                    self.db_worker, self.authorized_user, answer, True)
                self.students_answers_evaluated_layout.addWidget(studentAnswerPreviewItemWidget)

        if self.isHidden():
            self.show()

    def onRecalulatedVotes(self, votes: list[float]):
        teacherStudentAnswerPreviewItemIndex = 0
        for not_evaluated_item_index in range(self.students_answers_not_evaluated_layout.count()):
            item = self.students_answers_not_evaluated_layout.itemAt(not_evaluated_item_index)
            widget = item.widget()
            if isinstance(widget, TeacherStudentAnswerPreviewItem):
                widget.label_risultato.setText(str(votes[teacherStudentAnswerPreviewItemIndex]))
                widget.votoCustomSpinBox.setValue(votes[teacherStudentAnswerPreviewItemIndex])
                teacherStudentAnswerPreviewItemIndex += 1

    def onEvaluatedAnswer(self, answer: Answer):
        def show_confirm():
            message = 'Voto assegnato correttamente.'
            closeMessageBox = QMessageBox(self)
            closeMessageBox.setWindowTitle('Successo')
            closeMessageBox.setText(message)
            closeMessageBox.setStandardButtons(QMessageBox.Close)
            reply = closeMessageBox.exec()

        show_confirm()

        for not_evaluated_item_index in range(self.students_answers_not_evaluated_layout.count()):
            item = self.students_answers_not_evaluated_layout.itemAt(not_evaluated_item_index)
            widget = item.widget()
            if isinstance(widget, TeacherStudentAnswerPreviewItem):
                print(widget)
                if widget.answer.id == answer.id:
                    widget.deleteLater()
                    break

        studentAnswerPreviewItemWidget = TeacherStudentAnswerPreviewItem(
            self.db_worker, self.authorized_user, answer, True)
        self.students_answers_evaluated_layout.addWidget(studentAnswerPreviewItemWidget)

    def cleanup(self):
        # Elimina tutti i widget dal layout tranne l'header della sezione
        while self.students_answers_not_evaluated_layout.count() > 2:
            item = self.students_answers_not_evaluated_layout.takeAt(2)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        while self.students_answers_evaluated_layout.count() > 2:
            item = self.students_answers_evaluated_layout.takeAt(2)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
