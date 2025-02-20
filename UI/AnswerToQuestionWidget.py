from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QInputDialog,
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QTextEdit, QApplication, QFrame, QMessageBox
)
from model.question_model import Question


class AnswerToQuestionWidget(QWidget):
    
    onSendAnswerClicked = QtCore.pyqtSignal(Question, list)

    def __init__(self, authorized_user, num_students=None):
        if num_students is None:
            num_students, ok = QInputDialog.getInt(None, "Numero di studenti", "Inserisci il numero di studenti:", min=1)
            if not ok:
                num_students = 10  
        self.num_students = num_students  
        super().__init__()
        self.authorized_user = authorized_user
        self.question = None
        self.answerEdits = []  

        self.__initUi()
        self.hide()

    def __initUi(self):
        
        self.teacher_answer_layout = QVBoxLayout()
        
        self.students_answers_layout = QVBoxLayout()

        scroll_vertical_layout = QVBoxLayout()
        scroll = QScrollArea()  
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_vertical_layout)
        scroll.setWidget(scroll_widget)
        
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        scroll_vertical_layout.addLayout(self.teacher_answer_layout)
        scroll_vertical_layout.addLayout(self.students_answers_layout)
        scroll_vertical_layout.addStretch()

        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(scroll)
        self.setLayout(lay)

    def replaceQuestion(self, question: Question, num_students=None):
        """Quando viene selezionata una nuova domanda, crea campi di risposta per un numero dinamico di studenti."""
        self.cleanup()
        self.question = question
        if num_students is not None:
            self.num_students = num_students  

        
        question_label = QLabel(question.domanda)
        question_label.setStyleSheet('''
            QLabel {
                font-size: 14px; 
                font-weight: bold;
            }
        ''')
        question_label.setWordWrap(True)
        self.teacher_answer_layout.addWidget(QLabel("Domanda"))
        self.teacher_answer_layout.addWidget(question_label)

        
        self.answerEdits = []  
        for i in range(self.num_students):
            student_label = QLabel(f"Risposta studente {i+1}:")
            student_label.setStyleSheet('''
                QLabel {
                    font-size: 12px; 
                    font-weight: bold;
                }
            ''')
            answer_edit = QTextEdit()
            answer_edit.setAcceptRichText(False)
            answer_edit.setPlaceholderText("Inserisci risposta")
            answer_edit.textChanged.connect(self.checkAllEdits)

            self.students_answers_layout.addWidget(student_label)
            self.students_answers_layout.addWidget(answer_edit)
            self.answerEdits.append(answer_edit)

        
        self.sendAnswerBtn = QPushButton("Invia risposte")
        self.sendAnswerBtn.setEnabled(False)
        self.sendAnswerBtn.clicked.connect(self.__onSendAnswerClicked)
        self.students_answers_layout.addWidget(self.sendAnswerBtn)

        if self.isHidden():
            self.show()

    def checkAllEdits(self):
        """Abilita il pulsante di invio solo se almeno una risposta è stata compilata."""
        any_filled = any(edit.toPlainText().strip() for edit in self.answerEdits)
        self.sendAnswerBtn.setEnabled(any_filled)

    def __onSendAnswerClicked(self):
        """Raccoglie tutte le risposte e le invia tramite il segnale."""
        answers = [edit.toPlainText().strip() for edit in self.answerEdits if edit.toPlainText().strip()]

        if len(answers) != self.num_students:
            QMessageBox.warning(self, "Errore", f"Devi inserire esattamente {self.num_students} risposte.")
            return

        self.onSendAnswerClicked.emit(self.question, answers)

    def cleanup(self, cleanup_callback=None):
        """Elimina tutti i widget dai layout e resetta la lista dei campi di risposta."""
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

        
        self.answerEdits = []

        
        QApplication.processEvents()

        
        if cleanup_callback:
            cleanup_callback()
