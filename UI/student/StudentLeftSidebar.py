from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidgetItem, QHBoxLayout, QSpacerItem, QSizePolicy, QTabWidget

from UI.QuestionListWidget import QuestionListWidget


class StudentLeftSideBar(QWidget):

    unansweredSelectionChanged = QtCore.pyqtSignal(QListWidgetItem)
    answeredSelectionChanged = QtCore.pyqtSignal(QListWidgetItem)
    tabSelectionChanged = QtCore.pyqtSignal(str)

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
        self.__unansweredQuestionListWidget.changed.connect(self.unansweredSelectionChanged)

        self.__answeredQuestionListWidget = QuestionListWidget(enable_checkbox=False)
        self.__answeredQuestionListWidget.changed.connect(self.answeredSelectionChanged)

        tabWidget = QTabWidget()
        tabWidget.addTab(self.__unansweredQuestionListWidget, "Da rispondere")
        tabWidget.addTab(self.__answeredQuestionListWidget, "Già risposte")

        tabWidget.currentChanged.connect(lambda index: self.tabSelectionChanged.emit(tabWidget.tabText(index)))

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(tabWidget)

        self.setLayout(lay)

    def addQuestionToUnansweredList(self, question):
        self.__unansweredQuestionListWidget.addQuestion(question)

    def addQuestionToAnsweredList(self, question):
        self.__answeredQuestionListWidget.addQuestion(question)

    def moveQuestionToAnsweredList(self, question):
        self.__unansweredQuestionListWidget.removeQuestion(question)
        self.__answeredQuestionListWidget.addQuestion(question)

    def selectUnansweredListItem(self, index: int):
        if index < self.__unansweredQuestionListWidget.count():
            self.__unansweredQuestionListWidget.setCurrentRow(index)

    def selectAnsweredListItem(self, index: int):
        if index < self.__answeredQuestionListWidget.count():
            self.__answeredQuestionListWidget.setCurrentRow(index)

    def getCurrentAnsweredListItem(self) -> int:
        return self.__answeredQuestionListWidget.currentRow()
