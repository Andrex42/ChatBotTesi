from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, \
    QListWidgetItem
from PyQt5 import QtCore

from UI.QuestionListWidget import QuestionListWidget
from collection import extract_data
from model.question_model import Question


class ArchivedDialog(QDialog):
    selectionChanged = QtCore.pyqtSignal(QListWidgetItem)

    def __init__(self, parent, archived_questions_ready_event):
        super().__init__(parent=parent)
        self.setWindowTitle("Archiviate")
        self.resize(800, 300)
        self.setModal(True)

        archived_questions_ready_event.connect(lambda questions: self.on_archived_questions_ready(questions))
        self.closeEvent = self.clear_list

        lay = QVBoxLayout()

        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.__archivedQuestionListWidget = QuestionListWidget(enable_checkbox=False)

        lay.addWidget(self.__archivedQuestionListWidget)

        self.setLayout(lay)

    @QtCore.pyqtSlot()
    def on_archived_questions_ready(self, data):
        print("[on_archived_questions_ready]", data)

        data_array = extract_data(data)
        print("data converted", data_array)

        data_array = sorted(data_array, key=lambda x: x['data_creazione'])

        for q in data_array:
            question = Question(
                q['id'],
                q['document'],
                q['id_docente'],
                q['categoria'],
                q['source'],
                q['archived'],
                q['data_creazione'],
            )

            self.__archivedQuestionListWidget.addQuestion(question, False)

    def clear_list(self, event):
        if self.__archivedQuestionListWidget:
            self.__archivedQuestionListWidget.clear()
            print("Clear success")
