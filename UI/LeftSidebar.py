from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidgetItem, QPushButton, QHBoxLayout, QSpacerItem, \
    QSizePolicy, QCheckBox

from UI.QuestionListWidget import QuestionListWidget
from model.question_model import Question


class LeftSideBar(QWidget):

    on_add_question_clicked = QtCore.pyqtSignal()
    changed = QtCore.pyqtSignal(QListWidgetItem)
    deleteRowsClicked = QtCore.pyqtSignal(list)
    questionUpdated = QtCore.pyqtSignal(str, str)

    def __init__(self, authorized_user):
        super().__init__()

        self.authorized_user = authorized_user

        self.__initUi()

    def __initUi(self):
        self.__addBtn = QPushButton("Aggiungi")
        self.__archiveBtn = QPushButton("Archivia")
        self.__saveBtn = QPushButton("Esporta")

        self.__addBtn.clicked.connect(self.__addClicked)
        self.__archiveBtn.clicked.connect(self.__archiveClicked)
        # self.__saveBtn.clicked.connect(self.__saveClicked)

        self.__allCheckBox = QCheckBox('Seleziona tutto')
        self.__allCheckBox.stateChanged.connect(self.__stateChanged)

        lay = QHBoxLayout()
        lay.addWidget(self.__allCheckBox)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__archiveBtn)
        lay.addWidget(self.__saveBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__toggleButton(False)

        navWidget = QWidget()
        navWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(navWidget)

        topWidget = QWidget()
        topWidget.setLayout(lay)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__questionListWidget = QuestionListWidget()
        self.__questionListWidget.changed.connect(self.changed)
        self.__questionListWidget.checked.connect(self.__checked)
        self.__questionListWidget.questionUpdated.connect(self.questionUpdated)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__questionListWidget)

        self.setLayout(lay)

    def addQuestionToList(self, question: Question):
        self.__questionListWidget.addQuestion(question)

    def __addClicked(self):
        self.on_add_question_clicked.emit()

    def __archiveClicked(self):
        # get the ID of row, not actual index (because list is in a stacked form)
        rows = self.__questionListWidget.getCheckedRowsIds()
        self.deleteRowsClicked.emit(rows)
        self.__allCheckBox.setChecked(False)

    def removeRows(self, rows):
        for row in rows:
            self.__questionListWidget.removeQuestion(row)

    def __toggleButton(self, f):
        self.__archiveBtn.setEnabled(f)
        self.__saveBtn.setEnabled(f)

    def __stateChanged(self, f):
        self.__questionListWidget.toggleState(f)
        self.__toggleButton(f)

    def __checked(self, ids):
        f = len(ids) > 0
        self.__toggleButton(f)

