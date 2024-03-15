import os
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QListWidgetItem, QPushButton, QMessageBox

from UI.LeftSidebar import LeftSideBar
from UI.teacher.TeacherAddQuestionDialog import AddQuestionDialog
from UI.teacher.TeacherQuestionDetailsWidget import QuestionDetailsWidget

from collection import init_chroma_client, get_collections, get_chroma_q_a_collection, extract_data, \
    add_question_to_collection, get_similar_sentences, get_chroma_questions_collection
from model.answer_model import Answer
from model.question_model import Question


class Worker(QtCore.QObject):
    """
    Worker thread that handles the major program load. Allowing the gui to still be responsive.
    """
    def __init__(self, authorized_user, config):
        super(Worker, self).__init__()
        self.authorized_user = authorized_user
        self.config = config

    #QT signals - specify the method that the worker will be executing
    call_add_question = QtCore.pyqtSignal()

    questions_ready_event = QtCore.pyqtSignal(object)
    question_added_event = QtCore.pyqtSignal(Question)
    answer_voted_event = QtCore.pyqtSignal(Answer)
    archived_questions_event = QtCore.pyqtSignal(list)
    recalculated_unevaluated_answers_event = QtCore.pyqtSignal(object)
    q_a_ready_event = QtCore.pyqtSignal(object, object)
    unevaluated_answers_ids_ready_event = QtCore.pyqtSignal(list)
    unevaluated_answers_ids_update_ready_event = QtCore.pyqtSignal(list)

    @QtCore.pyqtSlot()
    def get_teacher_questions(self):
        start = time.time()

        init_chroma_client()

        question_collection, q_a_collection = get_collections()

        print("getting questions of teacher", self.authorized_user)

        query_result = question_collection.get(
            where={"$and": [{"id_docente": self.authorized_user['username']}, {"archived": False}]},
        )

        self.questions_ready_event.emit(query_result)

        self.getToEvaluateAnswersId()

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def add_question(self, categoria, question_text, ref_answer_text):
        start = time.time()

        # init_chroma_client()

        print("adding question", question_text, ref_answer_text)

        question = add_question_to_collection(self.authorized_user, categoria, question_text, ref_answer_text)

        if question:
            print("[add_question]", "question added", question)
            self.question_added_event.emit(question)

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def get_students_answers(self, question: Question):
        start = time.time()

        # init_chroma_client()

        q_a_collection = get_chroma_q_a_collection()

        print("getting answers for", question.id)

        USE_TRAIN_RESPONSES_DATA = os.getenv("USE_TRAIN_RESPONSES_DATA")

        if USE_TRAIN_RESPONSES_DATA == "true":
            query_result = q_a_collection.get(
                where={"id_domanda": question.id}
            )
        else:
            query_result = q_a_collection.get(
                where={"$and": [{"id_domanda": question.id}, {"id_autore": {"$ne": "undefined"}}]}
            )

        self.q_a_ready_event.emit(question, query_result)
        # print(query_result)
        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def assign_vote(self, answer: Answer, voto):
        start = time.time()

        init_chroma_client()

        id = answer.id

        q_a_collection = get_chroma_q_a_collection()

        print("updating answer with evaluation", answer)

        q_a_collection.update(
            ids=[id],
            metadatas=[{"id_domanda": answer.id_domanda,
                        "domanda": answer.domanda,
                        "id_docente": answer.id_docente,
                        "id_autore": answer.id_autore,
                        "voto_docente": voto,
                        "voto_predetto": answer.voto_predetto,
                        "commento": answer.commento,
                        "source": answer.source,
                        "data_creazione": answer.data_creazione}],
        )

        answer.voto_docente = voto

        self.answer_voted_event.emit(answer)

        self.getToEvaluateAnswersId()

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def getToEvaluateAnswersId(self, useUpdateEvent=False):
        start = time.time()

        init_chroma_client()

        q_a_collection = get_chroma_q_a_collection()

        answers_unevaluated = q_a_collection.get(
            where={"$and": [{"id_docente": self.authorized_user['username']}, {"voto_docente": -1}]},
            include=["metadatas"]
        )

        ids = [metadata["id_domanda"] for metadata in answers_unevaluated['metadatas']]

        if not useUpdateEvent:
            self.unevaluated_answers_ids_ready_event.emit(ids)
        else:
            self.unevaluated_answers_ids_update_ready_event.emit(ids)

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def archiveQuestions(self, domande: list[Question]):
        start = time.time()

        init_chroma_client()

        questions_collection = get_chroma_questions_collection()

        ids = [q.id for q in domande]
        metadatas = [{"id_domanda": q.id,
                      "id_docente": q.id_docente,
                      "categoria": q.categoria,
                      "source": q.source,
                      "archived": True,
                      "data_creazione": q.data_creazione} for q in domande]

        questions_collection.update(
            ids=ids,
            metadatas=metadatas
        )

        self.archived_questions_event.emit(domande)

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def recalc_question_unevaluated_answers_predictions(self, id_domanda: str):
        start = time.time()

        init_chroma_client()

        q_a_collection = get_chroma_q_a_collection()

        unevaluated_answers_result = q_a_collection.get(
            where={"$and": [{"id_domanda": id_domanda},
                            {"voto_docente": -1}]},
            include=["documents", "embeddings", "metadatas"]
        )

        if len(unevaluated_answers_result['ids']) > 0:
            voti_aggiornati = []

            for unevaluated_answers_array_index in range(len(unevaluated_answers_result['ids'])):
                curr_document = unevaluated_answers_result['documents'][unevaluated_answers_array_index]
                curr_embeddings = unevaluated_answers_result['embeddings'][unevaluated_answers_array_index]
                voto_ponderato = get_similar_sentences(id_domanda,
                                                       curr_document,
                                                       curr_embeddings)
                voti_aggiornati.append(voto_ponderato)

            print("[recalc_question_unevaluated_answers_predictions]", "voti aggiornati", voti_aggiornati)

            for i, metadata in enumerate(unevaluated_answers_result['metadatas']):
                metadata['voto_predetto'] = voti_aggiornati[i]

            q_a_collection.update(
                ids=unevaluated_answers_result['ids'],
                metadatas=unevaluated_answers_result['metadatas'],
            )

            print("voti predetti aggiornati")

            self.recalculated_unevaluated_answers_event.emit(voti_aggiornati)

        print(f'Execution time = {time.time() - start} seconds.')


class TeacherQuestionAnswersWidget(QWidget):
    def __init__(self, authorized_user, onCreatedThread):
        super().__init__()

        self.authorized_user = authorized_user
        self.onCreatedWorker = onCreatedThread
        self.questions = []

        self.__initWorker()
        self.__initUi()
        self.__initQuestions()

    def __initUi(self):
        self.__leftSideBarWidget = LeftSideBar(self.authorized_user)
        self.__questionDetailsWidget = QuestionDetailsWidget(self.authorized_user, self.db_worker)

        mainWidget = QSplitter()
        mainWidget.addWidget(self.__leftSideBarWidget)
        mainWidget.addWidget(self.__questionDetailsWidget)

        mainWidget.setSizes([500, 500])
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

        self.add_question_dialog = AddQuestionDialog(
            parent=self,
            save_callback=self.save_callback
        )

        self.__leftSideBarWidget.on_add_question_clicked.connect(self.__onAddQuestionClicked)
        self.__leftSideBarWidget.changed.connect(self.__changedQuestion)
        self.__leftSideBarWidget.deleteRowsClicked.connect(self.__onArchiveQuestionsClicked)

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

    def __initWorker(self):
        self.config = {}
        self.db_worker = Worker(self.authorized_user, self.config)

        self.db_worker.questions_ready_event.connect(lambda data: self.on_questions_ready(data))
        self.db_worker.q_a_ready_event.connect(lambda question, result:
                                               self.on_question_details_ready(question, result))
        self.db_worker.unevaluated_answers_ids_ready_event.connect(lambda ids:
                                                                   self.unevaluated_answers_ids_ready(ids))
        self.db_worker.unevaluated_answers_ids_update_ready_event.connect(lambda ids:
                                                                          self.unevaluated_answers_ids_update_ready(ids))
        self.db_worker.question_added_event.connect(lambda question: self.on_question_added(question))
        self.db_worker.answer_voted_event.connect(lambda answer: self.on_answer_voted(answer))
        self.db_worker.recalculated_unevaluated_answers_event.connect(lambda votes: self.on_recalculated_unevaluated_answers(votes))
        self.db_worker.archived_questions_event.connect(lambda questions: self.on_archived_questions(questions))

        self.db_thread = QtCore.QThread()
        self.db_thread.start()

        self.db_thread.finished.connect(self.on_finished_thread)
        self.onCreatedWorker(self.db_worker)

        self.db_worker.moveToThread(self.db_thread)

    def save_callback(self, categoria, question_text, ref_answer_text):
        if self.db_worker is not None:
            self.db_worker.add_question(categoria, question_text, ref_answer_text)

    def on_finished_thread(self):
        self.db_worker.deleteLater()
        self.db_worker = None

    def __initQuestions(self):
        if self.db_worker is not None:
            self.db_worker.get_teacher_questions()

    def __getQuestionDetails(self, question: Question):
        if self.db_worker is not None:
            self.db_worker.get_students_answers(question)

    @QtCore.pyqtSlot()
    def on_questions_ready(self, data):
        print("[on_questions_ready]", data)
        data_array = extract_data(data)
        print("data converted", data_array)

        self.questions = data_array

    @QtCore.pyqtSlot()
    def on_question_details_ready(self, question: Question, result):
        print("[on_question_details_ready]", result)
        data_array = extract_data(result)
        print("data converted", data_array)

        self.__questionDetailsWidget.replaceQuestion(question, data_array)

    @QtCore.pyqtSlot()
    def unevaluated_answers_ids_ready(self, ids: list[str]):
        print("[unevaluated_answers_ids_ready]", ids)

        for q in self.questions:
            question = Question(
                q['id'],
                q['document'],
                q['id_docente'],
                q['categoria'],
                q['source'],
                q['archived'],
                q['data_creazione'],
            )
            self.__leftSideBarWidget.addQuestionToList(question, question.id in ids)

    @QtCore.pyqtSlot()
    def unevaluated_answers_ids_update_ready(self, ids: list[str]):
        print("[unevaluated_answers_ids_update_ready]", ids)
        self.__leftSideBarWidget.updateHasUnevaluated(ids)

    @QtCore.pyqtSlot()
    def on_question_added(self, question: Question):
        print("[on_question_added]", question)

        self.__leftSideBarWidget.addQuestionToList(question, False)

    @QtCore.pyqtSlot()
    def on_answer_voted(self, answer: Answer):
        print("[on_answer_voted]", answer)

        self.__questionDetailsWidget.onEvaluatedAnswer(answer)
        if self.db_worker is not None:
            self.db_worker.recalc_question_unevaluated_answers_predictions(answer.id_domanda)

    @QtCore.pyqtSlot()
    def on_recalculated_unevaluated_answers(self, votes: list):
        print("[on_recalculated_unevaluated_answers]", votes)
        self.__questionDetailsWidget.onRecalulatedVotes(votes)

    @QtCore.pyqtSlot()
    def on_archived_questions(self, archivedQuestions: list[Question]):
        print("[on_archived_questions]", archivedQuestions)
        self.__leftSideBarWidget.removeRows(archivedQuestions)

    def __changedQuestion(self, item: QListWidgetItem):
        if item:
            question: Question = item.data(Qt.UserRole)
            print("changed", question.id, question.domanda)
            self.__getQuestionDetails(question)
        else:
            print("reset")

    def __onAddQuestionClicked(self):
        self.add_question_dialog.show()

    def __onArchiveQuestionsClicked(self, id_lst: list[Question]):
        def showAreYouSureDialog():
            message = f'Stai per archiviare {len(id_lst)} domande. Sei sicuro?'
            closeMessageBox = QMessageBox(self)
            closeMessageBox.setWindowTitle('Archivia domande')
            closeMessageBox.setText(message)
            closeMessageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            reply = closeMessageBox.exec()
            # Cancel
            if reply == QMessageBox.Cancel or reply == QMessageBox.No:
                return True
            elif reply == QMessageBox.Yes:
                if self.db_worker is not None:
                    self.db_worker.archiveQuestions(id_lst)

        # for id in id_lst:
        #     print("delete question", id)
        showAreYouSureDialog()
