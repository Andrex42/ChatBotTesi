from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, \
    QApplication

from UI.dot_widget import DotWidget
from model.question_model import Question


class QuestionItemWidget(QWidget):
    def __init__(self, question: Question, item: QListWidgetItem, isTeacher: bool, hasUnevaluatedAnswers: bool):
        super().__init__()
        self.__item = item
        self.__id = question.id
        self.__isTeacher = isTeacher
        self.__hasUnevaluatedAnswers = hasUnevaluatedAnswers
        self.__initUi(question)

    def convert_datetime(self, datetime_str):
        datetime_obj = datetime.fromisoformat(datetime_str)
        return datetime_obj.strftime("%d/%m/%Y %H:%M")

    def __initUi(self, question: Question):
        upper_label_text = question.categoria + " (" + question.id_docente + ")" \
            if not self.__isTeacher else question.categoria
        upper_label_text += f" - {self.convert_datetime(question.data_creazione)}"
        self.__topicLbl = QLabel(upper_label_text)

        palette = self.__topicLbl.palette()
        color = palette.color(QPalette.Text)
        color.setAlpha(127)
        palette.setColor(QPalette.Text, color)
        self.__topicLbl.setPalette(palette)
        self.__questionLbl = QLabel(question.domanda)

        lay = QVBoxLayout()
        lay.addWidget(DotWidget(8))
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.leftWidget = QWidget()
        self.leftWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.__topicLbl)
        lay.addWidget(self.__questionLbl)
        lay.setSpacing(2)
        lay.setContentsMargins(0, 0, 0, 0)

        rightWidget = QWidget()
        rightWidget.setLayout(lay)

        self.leftWidget.setStyleSheet("background-color: transparent;")
        rightWidget.setStyleSheet("background-color: transparent;")

        lay = QHBoxLayout()
        lay.addWidget(self.leftWidget)
        lay.addWidget(rightWidget)
        lay.addStretch()

        if self.__hasUnevaluatedAnswers:
            self.leftWidget.show()
        else:
            self.leftWidget.hide()

        self.setLayout(lay)


class QuestionListWidget(QListWidget):
    changed = QtCore.pyqtSignal(QListWidgetItem)
    checked = QtCore.pyqtSignal(list)

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

    def addQuestion(self, question: Question, isTeacher: bool, hasUnevaluatedAnswers: bool = False):
        item = QListWidgetItem()

        if self.enable_checkbox:
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)

        widget = QuestionItemWidget(question, item, isTeacher, hasUnevaluatedAnswers)
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

    def updateHasUnevaluated(self, ids: list[str]):
        for x in range(self.count()):
            row = self.item(x)
            rowWidget = self.itemWidget(row)
            questionRow: Question = row.data(Qt.UserRole)
            if questionRow.id in ids:
                if isinstance(rowWidget, QuestionItemWidget):
                    rowWidget.leftWidget.show()
            else:
                if isinstance(rowWidget, QuestionItemWidget):
                    rowWidget.leftWidget.hide()

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
