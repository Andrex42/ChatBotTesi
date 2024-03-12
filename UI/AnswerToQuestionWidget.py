from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidgetItem, QPushButton, QHBoxLayout, QScrollArea, \
    QTextEdit, QApplication


class AnswerToQuestionWidget(QWidget):

    onSendAnswerClicked = QtCore.pyqtSignal(object, str)

    def __init__(self, authorized_user):
        super().__init__()

        self.authorized_user = authorized_user
        self.question = None

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

    def replaceQuestion(self, question):
        self.cleanup()

        self.question = question

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

        answer_label = QLabel("Rispondi")
        answer_label.setStyleSheet('''
            QLabel {
                font-size: 12px; 
                font-weight: bold;
            }
        ''')

        self.answerTextEdit = QTextEdit()
        self.sendAnswerBtn = QPushButton("Invia risposta")
        self.sendAnswerBtn.setEnabled(False)

        self.answerTextEdit.textChanged.connect(self.checkTextEdit)
        self.sendAnswerBtn.clicked.connect(self.__onSendAnswerClicked)

        self.students_answers_layout.addWidget(answer_label)
        self.students_answers_layout.addWidget(self.answerTextEdit)
        self.students_answers_layout.addWidget(self.sendAnswerBtn)

    def checkTextEdit(self):
        # Controlla se il QTextEdit contiene del testo
        if self.answerTextEdit.toPlainText():
            self.sendAnswerBtn.setEnabled(True)
        else:
            self.sendAnswerBtn.setEnabled(False)

    def __onSendAnswerClicked(self):
        # Controlla se il QTextEdit contiene del testo
        if self.answerTextEdit.toPlainText():
            self.onSendAnswerClicked.emit(self.question, self.answerTextEdit.toPlainText())

    def cleanup(self, cleanup_callback=None):
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

        # Esegue un ciclo degli eventi per assicurarsi che i widget vengano eliminati
        QApplication.processEvents()

        # Chiamare la callback se è stata fornita
        if cleanup_callback:
            cleanup_callback()
