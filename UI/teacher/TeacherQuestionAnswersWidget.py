import csv
import os
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QListWidgetItem, QMessageBox, QMainWindow, QProgressDialog
from colorama import Fore, Style

from UI.LeftSidebar import LeftSideBar
from UI.teacher.TeacherAddQuestionDialog import AddQuestionDialog
from UI.teacher.TeacherArchivedDialog import ArchivedDialog
from UI.teacher.TeacherStatsDialog import StatsDialog
from UI.teacher.TeacherQuestionDetailsWidget import QuestionDetailsWidget
from collection import init_chroma_client, get_collections, get_chroma_q_a_collection, extract_data, \
    add_question_to_collection, predict_vote, predict_vote_from_ref, get_chroma_questions_collection
from model.answer_model import Answer
from model.question_model import Question


class RunnableTask(QtCore.QRunnable):
    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.task(*self.args, **self.kwargs)


class TeacherWorker(QtCore.QObject):
    """
    Worker thread that handles the major program load. Allowing the gui to still be responsive.
    """
    finished = QtCore.pyqtSignal()

    def __init__(self, authorized_user, config, on_error):
        super(TeacherWorker, self).__init__()
        self.authorized_user = authorized_user
        self.config = config
        self.on_error = on_error

    archived_questions_ready_event = QtCore.pyqtSignal(object)
    questions_ready_event = QtCore.pyqtSignal(object)
    question_added_event = QtCore.pyqtSignal(Question)
    answer_voted_event = QtCore.pyqtSignal(Question, Answer)
    archived_questions_event = QtCore.pyqtSignal(list)
    exported_questions_event = QtCore.pyqtSignal(list)
    students_votes_ready_event = QtCore.pyqtSignal(list)
    recalculated_unevaluated_answers_event = QtCore.pyqtSignal()
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

        question = add_question_to_collection(
            self.authorized_user,
            categoria,
            question_text,
            ref_answer_text,
            error_callback=self.on_error,
            fake_add=os.getenv("FAKE_ADD").lower() == "true")

        if question is not None:
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

        USE_TRAIN_RESPONSES_DATA = os.getenv("USE_TRAIN_RESPONSES_DATA").lower()

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
    def get_archived_questions(self):
        start = time.time()

        init_chroma_client()

        question_collection = get_chroma_questions_collection()

        print("getting archived questions of teacher", self.authorized_user)

        query_result = question_collection.get(
            where={"$and": [{"id_docente": self.authorized_user['username']}, {"archived": True}]},
        )

        self.archived_questions_ready_event.emit(query_result)

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def get_students_answers(self, question: Question):
        def check_need_recalc(qr):
            if qr is not None:
                for i, metadata in enumerate(qr['metadatas']):
                    if metadata['voto_docente'] == -1 and (metadata['voto_predetto'] == -1 or metadata['voto_predetto_all'] == -1):
                        return True
            return False

        start = time.time()

        # init_chroma_client()

        q_a_collection = get_chroma_q_a_collection()

        print("getting answers for", question.id)

        USE_TRAIN_RESPONSES_DATA = os.getenv("USE_TRAIN_RESPONSES_DATA").lower()

        if USE_TRAIN_RESPONSES_DATA == "true":
            query_result = q_a_collection.get(
                where={"id_domanda": question.id}
            )
        else:
            query_result = q_a_collection.get(
                where={"$and": [{"id_domanda": question.id}, {"id_autore": {"$ne": "undefined"}}]}
            )

        if check_need_recalc(query_result):
            self.recalc_question_unevaluated_answers_predictions_with_ref(question.id, question.id_docente)

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
    def assign_vote(self, question: Question, answer: Answer, voto: int, use_as_ref=False):
        start = time.time()

        init_chroma_client()

        id = answer.id

        print("updating answer with evaluation", answer)

        fake_add = os.getenv("FAKE_ADD").lower() == "true"

        if not fake_add:
            print(
                f"WARNING: {Fore.YELLOW}{Style.BRIGHT}FAKE ADD {fake_add}{Style.RESET_ALL}"
            )

            q_a_collection = get_chroma_q_a_collection()

            q_a_collection.update(
                ids=[id],
                metadatas=[{"id_domanda": answer.id_domanda,
                            "domanda": answer.domanda,
                            "id_docente": answer.id_docente,
                            "id_autore": answer.id_autore,
                            "voto_docente": voto,
                            "voto_predetto": answer.voto_predetto,
                            "voto_predetto_all": answer.voto_predetto_all,
                            "use_as_ref": use_as_ref,
                            "commento": answer.commento,
                            "source": answer.source,
                            "data_creazione": answer.data_creazione}],
            )
        else:
            time.sleep(1)

        answer.voto_docente = voto

        self.answer_voted_event.emit(question, answer)

        # ottiene le risposte che richiedono attenzione da parte del docente
        self.getToEvaluateAnswersId(useUpdateEvent=True)

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

        fake_add = os.getenv("FAKE_ADD").lower() == "true"

        if not fake_add:
            print(
                f"WARNING: {Fore.YELLOW}{Style.BRIGHT}FAKE ADD {fake_add}{Style.RESET_ALL}"
            )

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
        else:
            time.sleep(1)

        self.archived_questions_event.emit(domande)

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def exportQuestions(self, questions: list[Question]):
        if len(questions) == 0:
            return

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
            writer = csv.DictWriter(
                file,
                fieldnames=['id', 'text', 'label', 'id_docente', 'source', 'archived', 'data_creazione']
            )

            # Scrivi l'intestazione del CSV
            writer.writeheader()

            # Scrivi i dati delle domande nel file CSV
            for question in questions:
                writer.writerow({
                    'id': question.id,
                    'text': question.domanda,
                    'label': question.categoria,
                    'id_docente': question.id_docente,
                    'source': question.source,
                    'archived': question.archived,
                    'data_creazione': question.data_creazione,
                })

        print(f"Il file CSV è stato generato con successo: {output_path}")

        print("getting answers for", self.authorized_user['username'])

        USE_TRAIN_RESPONSES_DATA = os.getenv("USE_TRAIN_RESPONSES_DATA").lower()

        if USE_TRAIN_RESPONSES_DATA == "true":
            query_result = q_a_collection.get(
                where={"$and": [
                    {"id_docente": self.authorized_user['username']},
                    {"$or": [{'id_domanda': q.id} for q in questions]} if len(questions) > 1
                    else {'id_domanda': questions[0].id}
                ]}
            )
        else:
            query_result = q_a_collection.get(
                where={"$and": [
                    {"id_docente": self.authorized_user['username']},
                    {"id_autore": {"$ne": "undefined"}},
                    {"$or": [{'id_domanda': q.id} for q in questions]} if len(questions) > 1
                    else {'id_domanda': questions[0].id}
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
            writer = csv.DictWriter(file, fieldnames=['id', 'id_domanda', 'title', 'id_docente', 'text', 'id_autore', 'label', 'voto_predetto', 'voto_predetto_all', 'use_as_ref', 'commento', 'source', 'data_creazione'])

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
                    'voto_predetto_all': answer_dict['voto_predetto_all'],
                    'use_as_ref': answer_dict['use_as_ref'],
                    'commento': answer_dict['commento'],
                    'source': answer_dict['source'],
                    'data_creazione': answer_dict['data_creazione'],
                })

        print(f"Il file CSV è stato generato con successo: {output_path}")

        self.exported_questions_event.emit(questions)

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def recalc_question_unevaluated_answers_predictions(self, question: Question):
        start = time.time()

        init_chroma_client()

        q_a_collection = get_chroma_q_a_collection()

        unevaluated_answers_result = q_a_collection.get(
            where={"$and": [{"id_domanda": question.id},
                            {"voto_docente": -1}]},
            include=["documents", "metadatas"]
        )

        if len(unevaluated_answers_result['ids']) > 0:
            voti_all_aggiornati = []

            for unevaluated_answers_array_index in range(len(unevaluated_answers_result['ids'])):
                curr_document = unevaluated_answers_result['documents'][unevaluated_answers_array_index]
                predicted_vote = predict_vote(question.id,
                                              curr_document)
                voti_all_aggiornati.append(predicted_vote)

            print("[recalc_question_unevaluated_answers_predictions]", "voti all aggiornati", voti_all_aggiornati)

            for i, metadata in enumerate(unevaluated_answers_result['metadatas']):
                metadata['voto_predetto_all'] = voti_all_aggiornati[i]

            fake_add = os.getenv("FAKE_ADD").lower() == "true"

            if not fake_add:
                print(
                    f"WARNING: {Fore.YELLOW}{Style.BRIGHT}FAKE ADD {fake_add}{Style.RESET_ALL}"
                )

                q_a_collection.update(
                    ids=unevaluated_answers_result['ids'],
                    metadatas=unevaluated_answers_result['metadatas'],
                )
            else:
                time.sleep(1)

            print("voti predetti da tutte le risposte aggiornati")

        # riottiene le risposte degli studenti alla domanda,
        # sostituisce al termine la vista aggiornando i dati e gli istogrammi
        self.get_students_answers(question)

        self.recalculated_unevaluated_answers_event.emit()  # mostra finestra di dialogo con conferma

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def recalc_question_unevaluated_answers_predictions_with_ref(self, id_domanda: str, teacher_username: str) -> object:
        start = time.time()

        init_chroma_client()

        q_a_collection = get_chroma_q_a_collection()

        unevaluated_answers_result = q_a_collection.get(
            where={"$and": [{"id_domanda": id_domanda},
                            {"voto_docente": -1}]},
            include=["documents", "metadatas"]
        )

        voti_ref_aggiornati = []
        voti_all_aggiornati = []

        if len(unevaluated_answers_result['ids']) > 0:
            for unevaluated_answers_array_index in range(len(unevaluated_answers_result['ids'])):
                curr_document = unevaluated_answers_result['documents'][unevaluated_answers_array_index]
                predicted_vote_from_ref = predict_vote_from_ref(id_domanda,
                                                                teacher_username,
                                                                curr_document)
                predicted_vote_from_all = predict_vote(id_domanda,
                                                       curr_document)

                voti_ref_aggiornati.append(predicted_vote_from_ref)
                voti_all_aggiornati.append(predicted_vote_from_all)

            print("[recalc_question_unevaluated_answers_predictions_with_ref]", "voti ref aggiornati", voti_ref_aggiornati)
            print("[recalc_question_unevaluated_answers_predictions_with_ref]", "voti all aggiornati", voti_all_aggiornati)

            for i, metadata in enumerate(unevaluated_answers_result['metadatas']):
                metadata['voto_predetto'] = voti_ref_aggiornati[i]
                metadata['voto_predetto_all'] = voti_all_aggiornati[i]

            fake_add = os.getenv("FAKE_ADD").lower() == "true"

            if not fake_add:
                print(
                    f"WARNING: {Fore.YELLOW}{Style.BRIGHT}FAKE ADD {fake_add}{Style.RESET_ALL}"
                )

                q_a_collection.update(
                    ids=unevaluated_answers_result['ids'],
                    metadatas=unevaluated_answers_result['metadatas'],
                )
            else:
                time.sleep(1)

            print("voti predetti aggiornati")

        print(f'Execution time = {time.time() - start} seconds.')

        return {
            'ref': voti_ref_aggiornati,
            'all': voti_all_aggiornati
        }


class TeacherQuestionAnswersWidget(QWidget):
    def __init__(self, parent: QMainWindow, authorized_user, onCreatedThread):
        super().__init__()

        self.authorized_user = authorized_user
        self.onCreatedWorker = onCreatedThread
        self.questions = []

        self.__initWorker()
        self.__initUi(parent)
        self.__initQuestions()

    def __initUi(self, parent: QMainWindow):
        self.loading_dialog = QProgressDialog(self)
        self.loading_dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.loading_dialog.setRange(0, 0)
        self.loading_dialog.setCancelButton(None)
        self.hide_loading_dialog()

        self.__leftSideBarWidget = LeftSideBar(self.authorized_user)
        self.__questionDetailsWidget = QuestionDetailsWidget(
            self.authorized_user,
            self.threadpool,
            self.db_worker,
            self.loading_dialog
        )

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

        self.archived_dialog = ArchivedDialog(
            parent=self,
            archived_questions_ready_event=self.db_worker.archived_questions_ready_event
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

    def show_error_dialog(self, error_text):
        self.hide_loading_dialog()

        message = error_text
        closeMessageBox = QMessageBox(self)
        closeMessageBox.setWindowTitle('Errore')
        closeMessageBox.setText(message)
        closeMessageBox.setStandardButtons(QMessageBox.Close)
        closeMessageBox.exec()

    def __initWorker(self):
        self.config = {}
        self.db_worker = TeacherWorker(
            self.authorized_user,
            self.config,
            lambda error_text: self.show_error_dialog(error_text))

        self.db_worker.finished.connect(self.on_finished_thread)

        self.db_worker.questions_ready_event.connect(lambda data: self.on_questions_ready(data))
        self.db_worker.q_a_ready_event.connect(lambda question, result:
                                               self.on_question_details_ready(question, result))
        self.db_worker.unevaluated_answers_ids_ready_event.connect(lambda ids:
                                                                   self.unevaluated_answers_ids_ready(ids))
        self.db_worker.unevaluated_answers_ids_update_ready_event.connect(lambda ids:
                                                                          self.unevaluated_answers_ids_update_ready(ids))
        self.db_worker.question_added_event.connect(lambda question: self.on_question_added(question))
        self.db_worker.answer_voted_event.connect(lambda question, answer: self.on_answer_voted(question, answer))
        self.db_worker.recalculated_unevaluated_answers_event.connect(self.on_recalculated_unevaluated_answers)
        self.db_worker.archived_questions_event.connect(lambda questions: self.on_archived_questions(questions))
        self.db_worker.exported_questions_event.connect(lambda questions: self.on_exported_questions(questions))

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        self.onCreatedWorker(self.db_worker)

    def save_callback(self, categoria, question_text, ref_answer_text):
        if self.db_worker is not None:
            task = RunnableTask(self.db_worker.add_question, categoria, question_text, ref_answer_text)
            self.threadpool.start(task)

            self.show_loading_dialog()

    def on_finished_thread(self):
        self.db_worker.deleteLater()
        self.db_worker = None

    def __initQuestions(self):
        if self.db_worker is not None:
            task = RunnableTask(self.db_worker.get_teacher_questions)
            self.threadpool.start(task)

    def __getQuestionDetails(self, question: Question):
        if self.db_worker is not None:
            task = RunnableTask(self.db_worker.get_students_answers, question)
            self.threadpool.start(task)

    @QtCore.pyqtSlot()
    def on_questions_ready(self, data):
        print("[on_questions_ready]", data)
        data_array = extract_data(data)
        print("data converted", data_array)

        data_array = sorted(data_array, key=lambda x: x['data_creazione'])

        self.questions = data_array

    def open_stats_window(self):
        if self.db_worker is not None:
            task = RunnableTask(self.db_worker.get_students_votes)
            self.threadpool.start(task)

            self.stats_dialog.show()

    def open_archived_window(self):
        if self.db_worker is not None:
            task = RunnableTask(self.db_worker.get_archived_questions)
            self.threadpool.start(task)

            self.archived_dialog.show()

    @QtCore.pyqtSlot()
    def on_question_details_ready(self, question: Question, result):
        print("[on_question_details_ready]", result)
        data_array = extract_data(result)
        print("data converted", data_array)

        self.__questionDetailsWidget.replaceQuestion(question, data_array)

    @QtCore.pyqtSlot()
    def unevaluated_answers_ids_ready(self, ids: list[str]):
        print("[unevaluated_answers_ids_ready]", ids)

        self.__leftSideBarWidget.blockListSignals()

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

        self.__leftSideBarWidget.unblockListSignals()

    @QtCore.pyqtSlot()
    def unevaluated_answers_ids_update_ready(self, ids: list[str]):
        print("[unevaluated_answers_ids_update_ready]", ids)
        self.__leftSideBarWidget.updateHasUnevaluated(ids)

    @QtCore.pyqtSlot()
    def on_question_added(self, question: Question):
        print("[on_question_added]", question)
        self.hide_loading_dialog()

        def show_confirm():
            message = 'Domanda inserita correttamente. Da questo momento in poi gli studenti potranno inserire la propria risposta.'
            closeMessageBox = QMessageBox(self)
            closeMessageBox.setWindowTitle('Domanda inserita con successo')
            closeMessageBox.setText(message)
            closeMessageBox.setStandardButtons(QMessageBox.Close)
            closeMessageBox.exec()

        show_confirm()
        self.add_question_dialog.clearInputs()

        self.__leftSideBarWidget.addQuestionToList(question, False)

    @QtCore.pyqtSlot()
    def on_answer_voted(self, question: Question, answer: Answer):
        print("[on_answer_voted]", answer)

        if self.db_worker is not None:
            task = RunnableTask(self.db_worker.recalc_question_unevaluated_answers_predictions, question)
            self.threadpool.start(task)

    @QtCore.pyqtSlot()
    def on_recalculated_unevaluated_answers(self):
        print("[on_recalculated_unevaluated_answers]")
        self.hide_loading_dialog()

        def show_confirm():
            message = 'Voto assegnato correttamente.'
            closeMessageBox = QMessageBox(self)
            closeMessageBox.setWindowTitle('Successo')
            closeMessageBox.setText(message)
            closeMessageBox.setStandardButtons(QMessageBox.Close)
            reply = closeMessageBox.show()

        show_confirm()

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
                    task = RunnableTask(self.db_worker.archiveQuestions, id_lst)
                    self.threadpool.start(task)

        # for id in id_lst:
        #     print("delete question", id)
        showAreYouSureDialog()

    def __onExportQuestionsClicked(self, questions: list[Question]):
        for q in questions:
            print("export question", q)

        if self.db_worker is not None:
            task = RunnableTask(self.db_worker.exportQuestions, questions)
            self.threadpool.start(task)

    def show_loading_dialog(self):
        self.loading_dialog.exec()

    def hide_loading_dialog(self):
        self.loading_dialog.cancel()
