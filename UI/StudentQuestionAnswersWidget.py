import os
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QListWidgetItem

from UI.AnswerToQuestionWidget import AnswerToQuestionWidget
from UI.StudentLeftSidebar import StudentLeftSideBar

from collection import init_chroma_client, get_collections, get_chroma_q_a_collection, add_answer_to_collection, \
    extract_data, extract_metadata_from_get_result
from users import RELATIONS


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

    unanswered_questions_ready_event = QtCore.pyqtSignal(object)
    answered_questions_ready_event = QtCore.pyqtSignal(object)
    answer_added_event = QtCore.pyqtSignal(object)
    q_a_ready_event = QtCore.pyqtSignal(object, object)

    @QtCore.pyqtSlot()
    def start_ml(self):
        start = time.time()

        init_chroma_client()

        question_collection, q_a_collection = get_collections()

        print("getting questions of student", self.authorized_user)

        related_teachers = next((r[self.authorized_user['username']] for r in RELATIONS
                                 if self.authorized_user['username'] in r), None)

        if related_teachers is not None and len(related_teachers) > 0:
            print("related_teachers", related_teachers)

            all_student_answers = q_a_collection.get(
                where={"$and": [{"id_autore": self.authorized_user['username']},
                                {"id_docente": {"$in": related_teachers}}]}
            )

            print("risposte dello studente", all_student_answers)
            print("metadatas", all_student_answers['metadatas'])

            if len(all_student_answers['documents']) == 0:
                unanswered_questions = question_collection.get(
                    where={"id_docente": {"$in": related_teachers}}
                )

                answered_questions = None
            else:
                id_domanda_metadatas = extract_metadata_from_get_result(all_student_answers['metadatas'], "id_domanda")
                unanswered_questions = question_collection.get(
                    where={"$and": [{"id_docente": {"$in": related_teachers}},
                                    {"id_domanda": {"$nin": id_domanda_metadatas}}]}
                )

                answered_questions = question_collection.get(
                    where={"$and": [{"id_docente": {"$in": related_teachers}},
                                    {"id_domanda": {"$in": id_domanda_metadatas}}]}
                )



            # all_student_questions = question_collection.get(
            #     where={"id_docente": {"$in": related_teachers}},
            # )

            # print("domande assegnate allo studente (risposte e non risposte)", all_student_questions)
            print("domande assegnate allo studente (risposte)", answered_questions)
            print("domande assegnate allo studente (non risposte)", unanswered_questions)

            self.unanswered_questions_ready_event.emit(unanswered_questions)
            self.answered_questions_ready_event.emit(answered_questions)

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def add_answer(self, question: object, answer: str):
        start = time.time()

        # init_chroma_client()

        question_collection, q_a_collection = get_collections()

        print("adding answer", answer)


        add_answer_to_collection(self.authorized_user, question, answer)
        # question_collection.add(
        #     documents=[question],
        #     metadatas=[{"teacher_id": self.teacher_id}],
        # )

        # query_result = question_collection.query(
        #     query_texts=["Quale può essere il futuro dell'intelligenza artificiale?"],
        #     n_results=10
        # )

        # print("# The most similar sentences computed by chroma")
        # print(query_result)
        self.answer_added_event.emit(answer)
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


class StudentQuestionAnswersWidget(QWidget):
    def __init__(self, authorized_user):
        super().__init__()

        self.authorized_user = authorized_user

        self.__initUi()
        self.__initWorker()
        self.__initQuestions()

    def __initUi(self):
        self.__leftSideBarWidget = StudentLeftSideBar(self.authorized_user)
        self.__answerToQuestionWidget = AnswerToQuestionWidget(self.authorized_user)

        lay = QVBoxLayout()
        lay.addWidget(self.__answerToQuestionWidget)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        answerToQuestionWidget = QWidget()
        answerToQuestionWidget.setLayout(lay)

        mainWidget = QSplitter()
        mainWidget.addWidget(self.__leftSideBarWidget)
        mainWidget.addWidget(answerToQuestionWidget)

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

        self.__leftSideBarWidget.unansweredSelectionChanged.connect(self.__unansweredQuestionSelectionChanged)
        self.__leftSideBarWidget.answeredSelectionChanged.connect(self.__answeredQuestionSelectionChanged)
        self.__leftSideBarWidget.questionUpdated.connect(self.__updatedQuestion)

        self.__answerToQuestionWidget.onSendAnswerClicked.connect(self.__onSendAnswerClicked)

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

    def __initWorker(self):
        self.config = {}
        self.db_worker = Worker(self.authorized_user, self.config)

        self.db_worker.call_start_ml.connect(self.db_worker.start_ml)
        self.db_worker.unanswered_questions_ready_event.connect(lambda data: self.on_unanswered_questions_ready(data))
        self.db_worker.answered_questions_ready_event.connect(lambda data: self.on_answered_questions_ready(data))
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
    def on_unanswered_questions_ready(self, data):
        print("received", data)
        data_array = extract_data(data)
        print("data converted", data_array)

        for question in data_array:
            self.__leftSideBarWidget.addQuestionToUnansweredList(question)

    @QtCore.pyqtSlot()
    def on_answered_questions_ready(self, data):
        print("received", data)
        data_array = extract_data(data)
        print("data converted", data_array)

        for question in data_array:
            self.__leftSideBarWidget.addQuestionToAnsweredList(question)

    @QtCore.pyqtSlot()
    def on_question_details_ready(self, question, result):
        print("received", result)
        data_array = extract_data(result)
        print("data converted", data_array)

        # self.__questionDetailsWidget.replaceQuestion(question, data_array) TODO

    def __unansweredQuestionSelectionChanged(self, item: QListWidgetItem):
        if item:
            question = item.data(Qt.UserRole)
            id, title = question['id'], question['document']
            print("changed", id, title)
            # Inserisci un controllo nel caso in cui si sia inserita una risposta, se una risposta è presente,
            # avvisa l'utente che potrebbe perdere i progressi fatti # TODO
            self.__answerToQuestionWidget.replaceQuestion(question)
        else:
            # self.__browser.resetChatWidget(0) TODO
            print("reset")

    def __onSendAnswerClicked(self, question: object, answer: str):
        print("Domanda", question)
        print("Risposta", answer)
        self.db_worker.add_answer(question, answer)

    def __answeredQuestionSelectionChanged(self, item: QListWidgetItem):
        if item:
            question = item.data(Qt.UserRole)
            id, title = question['id'], question['document']
            print("changed", id, title)
            self.__getQuestionDetails(question)
        else:
            # self.__browser.resetChatWidget(0) TODO
            print("reset")

    def __updatedQuestion(self, id, title=None):
        if title:
            # DB.updateConv(id, title)
            print("update question", id, title)
