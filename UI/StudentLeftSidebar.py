from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidgetItem, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget

from UI.QuestionListWidget import QuestionListWidget


class StudentLeftSideBar(QWidget):

    changed = QtCore.pyqtSignal(QListWidgetItem)
    questionUpdated = QtCore.pyqtSignal(str, str)

    def __init__(self, authorized_user):
        super().__init__()

        self.authorized_user = authorized_user

        self.__initUi()

    def __initUi(self):
        lay = QHBoxLayout()
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.setContentsMargins(0, 0, 0, 0)

        navWidget = QWidget()
        navWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(navWidget)

        topWidget = QWidget()
        topWidget.setLayout(lay)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__unansweredQuestionListWidget = QuestionListWidget(enable_checkbox=False)
        self.__unansweredQuestionListWidget.changed.connect(self.changed)

        self.__answeredQuestionListWidget = QuestionListWidget(enable_checkbox=False)
        #self.__answeredQuestionListWidget.changed.connect(self.changed)

        tabWidget = QTabWidget()
        tabWidget.addTab(self.__unansweredQuestionListWidget, "Da rispondere")
        tabWidget.addTab(self.__answeredQuestionListWidget, "Già risposte")

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(tabWidget)

        self.setLayout(lay)

    def addQuestionToUnansweredList(self, question):
        self.__unansweredQuestionListWidget.addQuestion(question)

    def addQuestionToAnsweredList(self, question):
        self.__answeredQuestionListWidget.addQuestion(question)

    def addToList(self, id):
        self.__unansweredQuestionListWidget.addQuestion('New Chat', id)
        self.__convListWidget.setCurrentRow(0)

