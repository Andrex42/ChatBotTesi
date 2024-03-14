from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QColorConstants
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QListWidget, \
    QApplication

from model.question_model import Question


class QuestionItemWidget(QWidget):
    btnClicked = QtCore.pyqtSignal(QListWidgetItem)
    questionUpdated = QtCore.pyqtSignal(str, str)

    def __init__(self, question: Question, item: QListWidgetItem, isTeacher: bool):
        super().__init__()
        self.__item = item
        self.__id = question.id
        self.__isTeacher = isTeacher
        self.__initUi(question)

    def __initUi(self, question: Question):
        self.__topicLbl = QLabel(question.categoria + " (" + question.id_docente + ")"
                                 if not self.__isTeacher else question.categoria)

        palette = self.__topicLbl.palette()
        color = palette.color(QPalette.Text)
        color.setAlpha(127)
        palette.setColor(QPalette.Text, color)
        self.__topicLbl.setPalette(palette)
        self.__questionLbl = QLabel(question.domanda)

        lay = QVBoxLayout()
        lay.addWidget(self.__topicLbl)
        lay.addWidget(self.__questionLbl)
        lay.setSpacing(2)
        lay.setContentsMargins(0, 0, 0, 0)

        leftWidget = QWidget()
        leftWidget.setLayout(lay)

        editButton = QPushButton('rename')
        editButton.setToolTip('Rename')

        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(editButton)
        self.__btnWidget = QWidget()
        self.__btnWidget.setLayout(lay)
        self.__btnWidget.setVisible(False)

        lay = QVBoxLayout()
        lay.addWidget(self.__btnWidget)
        lay.setAlignment(Qt.AlignCenter | Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        rightWidget = QWidget()
        rightWidget.setLayout(lay)

        lay = QHBoxLayout()
        lay.addWidget(leftWidget)
        lay.addWidget(rightWidget)

        self.setLayout(lay)


class QuestionListWidget(QListWidget):
    changed = QtCore.pyqtSignal(QListWidgetItem)
    checked = QtCore.pyqtSignal(list)
    questionUpdated = QtCore.pyqtSignal(str, str)

    def __init__(self, *args, **kwargs):
        self.enable_checkbox = True
        if 'enable_checkbox' in kwargs:
            self.enable_checkbox = kwargs['enable_checkbox']
            del kwargs['enable_checkbox']

        super().__init__(*args, **kwargs)

        self.__initUi()

    def __initUi(self):
        self.itemClicked.connect(self.__clicked)
        self.currentItemChanged.connect(self.changed)

    def addQuestion(self, question: Question, isTeacher: bool):
        item = QListWidgetItem()

        if self.enable_checkbox:
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)

        widget = QuestionItemWidget(question, item, isTeacher)
        widget.questionUpdated.connect(self.questionUpdated)
        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.UserRole, question)
        self.insertItem(0, item)
        self.setItemWidget(item, widget)

    def removeQuestion(self, question):
        rowToRemove = -1

        for x in range(self.count()):
            questionRow: Question = self.item(x).data(Qt.UserRole)
            if questionRow.id == question.id:
                rowToRemove = x
                break

        if rowToRemove > -1:
            self.takeItem(rowToRemove)

    def __clicked(self, item):
        potentialChkBoxWidgetInItem = QApplication.widgetAt(self.cursor().pos())
        if isinstance(potentialChkBoxWidgetInItem, QWidget) and potentialChkBoxWidgetInItem.children():
            if isinstance(potentialChkBoxWidgetInItem.children()[0], QuestionItemWidget):
                if item.listWidget().itemWidget(item) is not None:
                    if item.checkState() == Qt.Checked:
                        item.setCheckState(Qt.Unchecked)
                    else:
                        item.setCheckState(Qt.Checked)
                    self.checked.emit(self.getCheckedRowsIds())

    def toggleState(self, state):
        for i in range(self.count()):
            item = self.item(i)
            state = Qt.CheckState(state)
            if item.checkState() != state:
                item.setCheckState(state)

    def getCheckedRowsIds(self):
        return self.__getFlagRows(Qt.Checked, is_id=True)

    def removeCheckedRows(self):
        self.__removeFlagRows(Qt.Checked)

    def removeUncheckedRows(self):
        self.__removeFlagRows(Qt.Unchecked)

    def __removeFlagRows(self, flag):
        flag_lst = self.__getFlagRows(flag)
        flag_lst = reversed(flag_lst)
        for i in flag_lst:
            self.takeItem(i)

    def getUncheckedRowsIds(self):
        return self.__getFlagRows(Qt.Unchecked, is_id=True)

    def __getFlagRows(self, flag: Qt.CheckState, is_id: bool = False):
        flag_lst = []
        for i in range(self.count()):
            item = self.item(i)
            if item.checkState() == flag:
                token = item.data(Qt.UserRole) if is_id else i
                flag_lst.append(token)

        return flag_lst
