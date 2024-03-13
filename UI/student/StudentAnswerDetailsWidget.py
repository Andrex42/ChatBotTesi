from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from model.answer_model import Answer
from model.question_model import Question


class AnswerDetailsWidget(QWidget):

    def __init__(self, authorized_user):
        super().__init__()

        self.authorized_user = authorized_user

        self.__initUi()

    def __initUi(self):
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

        self.result_label = QLabel("")

        self.teacher_answer_layout.addWidget(QLabel("Domanda"))
        self.teacher_answer_layout.addWidget(self.question_label)
        self.teacher_answer_layout.addWidget(QLabel("Risposta"))
        self.teacher_answer_layout.addWidget(self.answer_label)
        self.teacher_answer_layout.addWidget(QLabel("Risultato"))
        self.teacher_answer_layout.addWidget(self.result_label)

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

        scroll_vertical_layout.addLayout(self.teacher_answer_layout)
        scroll_vertical_layout.addStretch()

        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(scroll)

        self.setLayout(lay)

    def replaceAnswer(self, question: Question, answer: Answer):
        self.question_label.setText(question.domanda)
        self.answer_label.setText(answer.risposta)
        self.result_label.setText("In attesa di valutazione" if answer.voto_docente == -1 else str(answer.voto_docente))

        if answer.voto_docente > -1 and answer.voto_docente >= 3:
            self.result_label.setStyleSheet('''
                                QLabel {
                                    font-size: 12px; 
                                    font-weight: bold;
                                    color: #32a852;
                                }
                            ''')
        else:
            self.result_label.setStyleSheet('''
                                QLabel {
                                    font-size: 12px; 
                                    font-weight: bold;
                                    color: #a83232;
                                }
                            ''')
