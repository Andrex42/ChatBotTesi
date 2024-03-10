import os
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSplitter, QListWidgetItem

from UI.LeftSidebar import LeftSideBar
from UI.QuestionDetailsWidget import QuestionDetailsWidget

from collection import init_chroma_client, get_collections, get_chroma_q_a_collection, extract_data


class Worker(QtCore.QObject):
    """
    Worker thread that handles the major program load. Allowing the gui to still be responsive.
    """
    def __init__(self, authorized_user, config):
        super(Worker, self).__init__()
        self.authorized_user = authorized_user
        self.config = config

    #QT signals - specify the method that the worker will be executing
    call_start_ml = QtCore.pyqtSignal()
    call_add_question = QtCore.pyqtSignal()

    questions_ready_event = QtCore.pyqtSignal(object)
    question_added_event = QtCore.pyqtSignal(object)
    q_a_ready_event = QtCore.pyqtSignal(object, object)

    @QtCore.pyqtSlot()
    def start_ml(self):
        start = time.time()

        init_chroma_client()

        question_collection, q_a_collection = get_collections()

        print("getting questions of teacher", self.authorized_user)

        query_result = question_collection.get(
            where={"id_docente": self.authorized_user['username']},
        )

        self.questions_ready_event.emit(query_result)
        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def add_question(self, question):
        start = time.time()

        # init_chroma_client()

        question_collection, teacher_answers_collection, student_answers_collection = get_collections()

        print("adding question", question)

        question_collection.add(
            documents=[question],
            metadatas=[{"teacher_id": self.teacher_id}],
        )

        # query_result = question_collection.query(
        #     query_texts=["Quale può essere il futuro dell'intelligenza artificiale?"],
        #     n_results=10
        # )

        # print("# The most similar sentences computed by chroma")
        # print(query_result)
        self.question_added_event.emit(question)
        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def get_students_answers(self, question):
        start = time.time()

        # init_chroma_client()

        q_a_collection = get_chroma_q_a_collection()

        id, title = question['id'], question['document']

        print("getting answers for", title)

        USE_TRAIN_RESPONSES_DATA = os.getenv("USE_TRAIN_RESPONSES_DATA")

        if USE_TRAIN_RESPONSES_DATA == "true":
            query_result = q_a_collection.get(
                where={"domanda": title}
            )
        else:
            query_result = q_a_collection.get(
                where={"$and": [{"domanda": title}, {"id_autore": {"$ne": "undefined"}}]}
            )

        self.q_a_ready_event.emit(question, query_result)
        # print(query_result)
        print(f'Execution time = {time.time() - start} seconds.')


class TeacherQuestionAnswersWidget(QWidget):
    def __init__(self, authorized_user):
        super().__init__()

        self.authorized_user = authorized_user

        self.__initUi()
        self.__initWorker()
        self.__initQuestions()

    def __initUi(self):
        self.__leftSideBarWidget = LeftSideBar(self.authorized_user)
        self.__questionDetailsWidget = QuestionDetailsWidget(self.authorized_user)

        lay = QVBoxLayout()
        lay.addWidget(self.__questionDetailsWidget)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        questionDetailsWidget = QWidget()
        questionDetailsWidget.setLayout(lay)

        mainWidget = QSplitter()
        mainWidget.addWidget(self.__leftSideBarWidget)
        mainWidget.addWidget(questionDetailsWidget)

        mainWidget.setSizes([100, 500, 400])
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setHandleWidth(2)
        mainWidget.setStyleSheet(
            '''
            QSplitter::handle:horizontal
            {
                background: #CCC;
                height: 1px;
            }
            ''')

        self.__leftSideBarWidget.added.connect(self.__addedQuestion)
        self.__leftSideBarWidget.changed.connect(self.__changedQuestion)
        self.__leftSideBarWidget.deleted.connect(self.__deletedQuestion)
        self.__leftSideBarWidget.questionUpdated.connect(self.__updatedQuestion)

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

    def __initWorker(self):
        self.config = {}
        self.db_worker = Worker(self.authorized_user, self.config)

        self.db_worker.call_start_ml.connect(self.db_worker.start_ml)
        self.db_worker.questions_ready_event.connect(lambda data: self.on_questions_ready(data))
        self.db_worker.q_a_ready_event.connect(lambda question, result: self.on_question_details_ready(question, result))
        # self.db_worker.question_added_event.connect(lambda data: self.on_question_added(data))

        self.db_thread = QtCore.QThread()
        self.db_thread.start()

        self.db_worker.moveToThread(self.db_thread)

    def __initQuestions(self):
        self.db_worker.call_start_ml.emit()

    def __getQuestionDetails(self, question):
        self.db_worker.get_students_answers(question)

    @QtCore.pyqtSlot()
    def on_questions_ready(self, data):
        print("received", data)
        data_array = extract_data(data)
        print("data converted", data_array)

        for question in data_array:
            self.__leftSideBarWidget.addQuestionToList(question)

    @QtCore.pyqtSlot()
    def on_question_details_ready(self, question, result):
        print("received", result)
        data_array = extract_data(result)
        print("data converted", data_array)

        self.__questionDetailsWidget.replaceQuestion(question, data_array)

    def __changedQuestion(self, item: QListWidgetItem):
        if item:
            question = item.data(Qt.UserRole)
            id, title = question['id'], question['document']
            print("changed", id, title)
            self.__getQuestionDetails(question)
        else:
            # self.__browser.resetChatWidget(0) TODO
            print("reset")

    def __addedQuestion(self):
        # cur_id = DB.insertConv(LangClass.TRANSLATIONS['New Chat'])
        # self.__browser.resetChatWidget(cur_id) TODO
        #self.__leftSideBarWidget.addToList(cur_id)
        # self.__lineEdit.setFocus()
        print("add question")

    def __updatedQuestion(self, id, title=None):
        if title:
            # DB.updateConv(id, title)
            print("update question", id, title)

    def __deletedQuestion(self, id_lst):
        for id in id_lst:
            # DB.deleteConv(id)
            print("delete question", id)
