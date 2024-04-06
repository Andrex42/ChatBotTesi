import csv
import os
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QListWidgetItem, QMessageBox

from UI.LeftSidebar import LeftSideBar
from UI.teacher.TeacherAddQuestionDialog import AddQuestionDialog
from UI.teacher.TeacherStatsDialog import StatsDialog
from UI.teacher.TeacherQuestionDetailsWidget import QuestionDetailsWidget

from collection import init_chroma_client, get_collections, get_chroma_q_a_collection, extract_data, \
    add_question_to_collection, get_similar_sentences, get_chroma_questions_collection
from model.answer_model import Answer
from model.question_model import Question


class TeacherWorker(QtCore.QObject):
    """
    Worker thread that handles the major program load. Allowing the gui to still be responsive.
    """
    def __init__(self, authorized_user, config):
        super(TeacherWorker, self).__init__()
        self.authorized_user = authorized_user
        self.config = config

    #QT signals - specify the method that the worker will be executing
    call_add_question = QtCore.pyqtSignal()

    questions_ready_event = QtCore.pyqtSignal(object)
    question_added_event = QtCore.pyqtSignal(Question)
    answer_voted_event = QtCore.pyqtSignal(Answer)
    archived_questions_event = QtCore.pyqtSignal(list)
    exported_questions_event = QtCore.pyqtSignal(list)
    students_votes_ready_event = QtCore.pyqtSignal(list)
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
    def get_students_votes(self):
        start = time.time()

        # init_chroma_client()

        q_a_collection = get_chroma_q_a_collection()

        teacher_username = self.authorized_user['username']

        print("getting students votes for", teacher_username)

        USE_TRAIN_RESPONSES_DATA = os.getenv("USE_TRAIN_RESPONSES_DATA")

        if USE_TRAIN_RESPONSES_DATA == "true":
            result = q_a_collection.get(
                where={"$and": [{"id_docente": teacher_username},
                                {"id_autore": {"$ne": teacher_username}},
                                {"voto_docente": {"$gt": -1}}]},
                include=["metadatas"]
            )
        else:
            result = q_a_collection.get(
                where={"$and": [{"id_docente": teacher_username},
                                {"id_autore": {"$ne": "undefined"}},
                                {"id_autore": {"$ne": teacher_username}},
                                {"voto_docente": {"$gt": -1}}]},
                include=["metadatas"]
            )

        votes = [(metadata["id_autore"], metadata["voto_docente"], metadata["data_creazione"])
                 for metadata in result['metadatas']]

        self.students_votes_ready_event.emit(votes)
        # print(query_result)
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
    def exportQuestions(self, questions: list[Question]):
        start = time.time()

        init_chroma_client()

        q_a_collection = get_chroma_q_a_collection()

        # Determina il numero di esportazioni già effettuate
        export_count = len([name for name in os.listdir("export_data")
                            if name.startswith(f"export_domande_{self.authorized_user['username']}_")])

        # Incrementa il numero di esportazioni per ottenere il nome del file
        export_count += 1
        file_name = f"export_domande_{self.authorized_user['username']}_{export_count}.csv"

        # Percorso completo per il file CSV di output
        output_path = os.path.join("export_data", file_name)

        # Apri il file CSV in modalità di scrittura
        with open(output_path, mode='w', newline='', encoding='utf-8') as file:
            # Definisci il writer CSV
            writer = csv.DictWriter(file, fieldnames=['id', 'text', 'label', 'id_docente'])

            # Scrivi l'intestazione del CSV
            writer.writeheader()

            # Scrivi i dati delle domande nel file CSV
            for question in questions:
                writer.writerow({'id': question.id, 'text': question.domanda, 'label': question.categoria,
                                 'id_docente': question.id_docente})

        print(f"Il file CSV è stato generato con successo: {output_path}")

        print("getting answers for", self.authorized_user['username'])

        USE_TRAIN_RESPONSES_DATA = os.getenv("USE_TRAIN_RESPONSES_DATA")

        if USE_TRAIN_RESPONSES_DATA == "true":
            query_result = q_a_collection.get(
                where={"$and": [
                    {"id_docente": self.authorized_user['username']},
                    {"$or": [{'id_domanda': q.id} for q in questions]}
                ]}
            )
        else:
            query_result = q_a_collection.get(
                where={"$and": [
                    {"id_docente": self.authorized_user['username']},
                    {"id_autore": {"$ne": "undefined"}},
                    {"$or": [{'id_domanda': q.id} for q in questions]}
                ]}
            )

        print("[exportQuestions_answersReady]", query_result)
        data_array = extract_data(query_result)
        print("data converted", data_array)

        # Determina il numero di esportazioni già effettuate
        export_count = len([name for name in os.listdir("export_data")
                            if name.startswith(f"export_risposte_{self.authorized_user['username']}_")])

        # Incrementa il numero di esportazioni per ottenere il nome del file
        export_count += 1
        file_name = f"export_risposte_{self.authorized_user['username']}_{export_count}.csv"

        # Percorso completo per il file CSV di output
        output_path = os.path.join("export_data", file_name)

        # Apri il file CSV in modalità di scrittura
        with open(output_path, mode='w', newline='', encoding='utf-8') as file:
            # Definisci il writer CSV
            writer = csv.DictWriter(file, fieldnames=['id', 'id_domanda', 'title', 'id_docente', 'text', 'id_autore', 'label', 'voto_predetto', 'commento', 'source', 'data_creazione'])

            # Scrivi l'intestazione del CSV
            writer.writeheader()

            # Scrivi i dati delle domande nel file CSV
            for answer_dict in data_array:
                writer.writerow({
                    'id': answer_dict['id'],
                    'id_domanda': answer_dict['id_domanda'],
                    'title': answer_dict['domanda'],
                    'id_docente': answer_dict['id_docente'],
                    'text': answer_dict['document'],
                    'id_autore': answer_dict['id_autore'],
                    'label': answer_dict['voto_docente'],
                    'voto_predetto': answer_dict['voto_predetto'],
                    'commento': answer_dict['commento'],
                    'source': answer_dict['source'],
                    'data_creazione': answer_dict['data_creazione'],
                })

        print(f"Il file CSV è stato generato con successo: {output_path}")

        self.exported_questions_event.emit(questions)

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def recalc_question_unevaluated_answers_predictions(self, id_domanda: str):
        start = time.time()

        init_chroma_client()

        q_a_collection = get_chroma_q_a_collection()

        unevaluated_answers_result = q_a_collection.get(
            where={"$and": [{"id_domanda": id_domanda},
                            {"voto_docente": -1}]},
            include=["documents", "metadatas"]
        )

        if len(unevaluated_answers_result['ids']) > 0:
            voti_aggiornati = []

            for unevaluated_answers_array_index in range(len(unevaluated_answers_result['ids'])):
                curr_document = unevaluated_answers_result['documents'][unevaluated_answers_array_index]
                voto_ponderato = get_similar_sentences(id_domanda,
                                                       curr_document)
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

        self.stats_dialog = StatsDialog(
            parent=self,
            votes_ready_event=self.db_worker.students_votes_ready_event
        )

        self.__leftSideBarWidget.on_add_question_clicked.connect(self.__onAddQuestionClicked)
        self.__leftSideBarWidget.changed.connect(self.__changedQuestion)
        self.__leftSideBarWidget.deleteRowsClicked.connect(self.__onArchiveQuestionsClicked)
        self.__leftSideBarWidget.exportRowsClicked.connect(self.__onExportQuestionsClicked)

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

    def __initWorker(self):
        self.config = {}
        self.db_worker = TeacherWorker(self.authorized_user, self.config)

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
        self.db_worker.exported_questions_event.connect(lambda questions: self.on_exported_questions(questions))

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

    def open_stats_window(self):
        if self.db_worker is not None:
            self.db_worker.get_students_votes()
            self.stats_dialog.show()

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

    @QtCore.pyqtSlot()
    def on_exported_questions(self, exportedQuestions: list[Question]):
        print("[on_exported_questions]", exportedQuestions)

        def show_confirm():
            message = str(len(exportedQuestions)) + ' domande esportate con successo.'
            closeMessageBox = QMessageBox(self)
            closeMessageBox.setWindowTitle('Successo')
            closeMessageBox.setText(message)
            closeMessageBox.setStandardButtons(QMessageBox.Close)
            reply = closeMessageBox.exec()

        show_confirm()

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

    def __onExportQuestionsClicked(self, questions: list[Question]):
        for q in questions:
            print("export question", q)

        if self.db_worker is not None:
            self.db_worker.exportQuestions(questions)
