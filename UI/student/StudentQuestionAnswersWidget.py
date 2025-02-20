import os
import time

from typing import List

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QListWidgetItem, QMessageBox, QMainWindow, QProgressDialog

from UI.AnswerToQuestionWidget import AnswerToQuestionWidget
from UI.student.StudentAnswerDetailsWidget import AnswerDetailsWidget
from UI.student.StudentLeftSidebar import StudentLeftSideBar

from collection import init_chroma_client, get_collections, get_chroma_q_a_collection, extract_data, \
    extract_metadata_from_get_result, add_answers_to_collection

from model.answer_model import Answer
from model.question_model import Question
from users import RELATIONS


class RunnableTask(QtCore.QRunnable):
    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.task(*self.args, **self.kwargs)


class StudentWorker(QtCore.QObject):
    """
    Worker thread that handles the major program load. Allowing the gui to still be responsive.
    """
    finished = QtCore.pyqtSignal()

    def __init__(self, authorized_user, config, on_error):
        super(StudentWorker, self).__init__()
        self.authorized_user = authorized_user
        self.config = config
        self.on_error = on_error

    unanswered_questions_ready_event = QtCore.pyqtSignal(object)
    answered_questions_ready_event = QtCore.pyqtSignal(object)
    answer_added_event = QtCore.pyqtSignal(Question, Answer)
    answer_details_ready_event = QtCore.pyqtSignal(Question, Answer)

    @QtCore.pyqtSlot()
    def get_student_answers(self):
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
                    where={"$and": [{"id_docente": {"$in": related_teachers}}, {"archived": False}]}
                )

                answered_questions = None
            else:
                id_domanda_metadatas = extract_metadata_from_get_result(all_student_answers['metadatas'], "id_domanda")
                unanswered_questions = question_collection.get(
                    where={"$and": [{"id_docente": {"$in": related_teachers}},
                                    {"id_domanda": {"$nin": id_domanda_metadatas}},
                                    {"archived": False}]}
                )

                answered_questions = question_collection.get(
                    where={"$and": [{"id_docente": {"$in": related_teachers}},
                                    {"id_domanda": {"$in": id_domanda_metadatas}},
                                    {"archived": False}]}
                )

            print("domande assegnate allo studente (risposte)", answered_questions)
            print("domande assegnate allo studente (non risposte)", unanswered_questions)

            self.unanswered_questions_ready_event.emit(unanswered_questions)
            self.answered_questions_ready_event.emit(answered_questions)

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def get_student_answer(self, question: Question):
        start = time.time()

        q_a_collection = get_chroma_q_a_collection()

        print("getting answer by question", question.id)

        answer_result = q_a_collection.get(
            where={"$and": [{"id_autore": self.authorized_user['username']},
                            {"id_domanda": question.id}]}
        )

        answer_data_array = extract_data(answer_result)

        if len(answer_data_array):
            answer = Answer(
                answer_data_array[0]['id'],
                answer_data_array[0]['id_domanda'],
                answer_data_array[0]['domanda'],
                answer_data_array[0]['id_docente'],
                answer_data_array[0]['document'],
                answer_data_array[0]['id_autore'],
                int(answer_data_array[0]['voto_docente']),
                int(answer_data_array[0]['voto_predetto']),
                int(answer_data_array[0]['voto_predetto_all']),
                int(answer_data_array[0]['chat_gpt_rating']),
                answer_data_array[0]['use_as_ref'],
                answer_data_array[0]['commento'],
                answer_data_array[0]['source'],
                answer_data_array[0]['data_creazione'],
            )

            self.answer_details_ready_event.emit(question, answer)

        print(f'Execution time = {time.time() - start} seconds.')

    @QtCore.pyqtSlot()
    def add_answers(self, question: Question, answer_texts: List[str]):
        start = time.time()

        print(f"Aggiunta di {len(answer_texts)} risposte per la domanda: {question.id}")

        answers = add_answers_to_collection(self.authorized_user, question, responses=answer_texts)

        if answers:
            for answer in answers:
                print("[add_answers]", "Risposta aggiunta:", answer)
                self.answer_added_event.emit(question, answer)

        print(f'Execution time = {time.time() - start} seconds.')



class StudentQuestionAnswersWidget(QWidget):
    def __init__(self, parent: QMainWindow, authorized_user, onCreatedThread):
        super().__init__()

        self.authorized_user = authorized_user
        self.onCreatedWorker = onCreatedThread

        self.__initWorker()
        self.__initUi(parent)
        self.__initQuestions()

    def __initUi(self, parent: QMainWindow):
        self.__leftSideBarWidget = StudentLeftSideBar(self.authorized_user)
        self.__answerToQuestionWidget = AnswerToQuestionWidget(self.authorized_user)
        self.__answerDetailsWidget = AnswerDetailsWidget(self.authorized_user)

        self.loading_dialog = QProgressDialog(self)
        self.loading_dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.loading_dialog.setRange(0, 0)
        self.loading_dialog.setCancelButton(None)
        self.hide_loading_dialog()

        lay = QVBoxLayout()
        lay.addWidget(self.__answerToQuestionWidget)
        lay.addWidget(self.__answerDetailsWidget)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__rightSideWidget = QWidget()
        self.__rightSideWidget.setLayout(lay)
        self.__rightSideWidget.hide()

        mainWidget = QSplitter()
        mainWidget.addWidget(self.__leftSideBarWidget)
        mainWidget.addWidget(self.__rightSideWidget)

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

        self.__leftSideBarWidget.unansweredSelectionChanged.connect(self.__unansweredQuestionSelectionChanged)
        self.__leftSideBarWidget.answeredSelectionChanged.connect(self.__answeredQuestionSelectionChanged)
        self.__leftSideBarWidget.tabSelectionChanged.connect(self.__tabSelectionChanged)

        self.__answerToQuestionWidget.onSendAnswerClicked.connect(self.__onSendAnswerClicked)

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
        self.db_worker = StudentWorker(
            self.authorized_user,
            self.config,
            lambda error_text: self.show_error_dialog(error_text))

        self.db_worker.finished.connect(self.on_finished_thread)

        self.db_worker.unanswered_questions_ready_event.connect(lambda data: self.on_unanswered_questions_ready(data))
        self.db_worker.answered_questions_ready_event.connect(lambda data: self.on_answered_questions_ready(data))
        self.db_worker.answer_added_event.connect(lambda question, answer: self.on_answer_added(question, answer))
        self.db_worker.answer_details_ready_event.connect(lambda question, answer: self.on_answer_details_ready(question, answer))

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        self.onCreatedWorker(self.db_worker)

    def on_finished_thread(self):
        self.db_worker.deleteLater()
        self.db_worker = None

    def __initQuestions(self):
        if self.db_worker is not None:
            task = RunnableTask(self.db_worker.get_student_answers)
            self.threadpool.start(task)

    @QtCore.pyqtSlot()
    def on_unanswered_questions_ready(self, data):
        print("on_unanswered_questions_ready", "received", data)
        data_array = extract_data(data)
        print("on_unanswered_questions_ready", "data converted", data_array)

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

            self.__leftSideBarWidget.addQuestionToUnansweredList(question)

        if len(data_array):
            self.__leftSideBarWidget.selectUnansweredListItem(0)
            self.__rightSideWidget.show()

    @QtCore.pyqtSlot()
    def on_answered_questions_ready(self, data):
        print("on_answered_questions_ready", "received", data)
        data_array = extract_data(data)
        print("on_answered_questions_ready", "data converted", data_array)

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

            self.__leftSideBarWidget.addQuestionToAnsweredList(question)

    @QtCore.pyqtSlot()
    def on_answer_added(self, question: Question, answer: Answer):
        """Aggiorna l'interfaccia quando una risposta viene aggiunta."""
        print("[on_answer_added]", answer)
        self.__leftSideBarWidget.moveQuestionToAnsweredList(question)

        if not hasattr(self, "answers_saved"):
            self.answers_saved = 0  

        self.answers_saved += 1  

        
        if self.answers_saved == self.total_answers:
            self.hide_loading_dialog()
            self.answers_saved = 0  

            def show_confirm():
                message = f'Tutte le {self.total_answers} risposte sono state inviate correttamente.'
                closeMessageBox = QMessageBox(self)
                closeMessageBox.setWindowTitle('Risposte inviate con successo')
                closeMessageBox.setText(message)
                closeMessageBox.setStandardButtons(QMessageBox.Close)
                closeMessageBox.show()

            show_confirm()


    @QtCore.pyqtSlot()
    def on_answer_details_ready(self, question: Question, answer: Answer):
        print("[on_answer_details_ready]", answer)
        self.__answerDetailsWidget.replaceAnswer(question, answer)

    def __unansweredQuestionSelectionChanged(self, item: QListWidgetItem):
        if item:
            question: Question = item.data(Qt.UserRole)
            print("changed", question.id, question.domanda)
            # avvisa l'utente che potrebbe perdere i progressi fatti # TODO
            self.__answerToQuestionWidget.replaceQuestion(question)
        else:
            print("reset")

    def show_loading_dialog(self):
        self.loading_dialog.exec()

    def hide_loading_dialog(self):
        self.loading_dialog.cancel()

    def __onSendAnswerClicked(self, question: Question, answers: list):
        print("Domanda:", question)
        print("Risposte ricevute:", answers)

        if not answers:
            print("Errore: devono esserci almeno una risposta.")
            return

        if self.db_worker is not None:
            self.answers_saved = 0  
            self.total_answers = len(answers)  
            task = RunnableTask(self.db_worker.add_answers, question, answers)
            self.threadpool.start(task)

            self.show_loading_dialog()



    def __answeredQuestionSelectionChanged(self, item: QListWidgetItem):
        if item:
            question: Question = item.data(Qt.UserRole)
            print("changed", question.id, question.domanda)
            self.__getAnswerDetails(question)
        else:
            print("reset")

    def __tabSelectionChanged(self, tabName: str):
        print(tabName, "changed")
        if tabName == "Da rispondere":
            self.__answerDetailsWidget.hide()
            if self.__leftSideBarWidget.getUnansweredRowCount() > 0:
                self.__rightSideWidget.show()
                self.__answerToQuestionWidget.show()
            else:
                self.__answerToQuestionWidget.hide()
                self.__rightSideWidget.hide()
        elif tabName == "Già risposte":
            self.__answerToQuestionWidget.hide()

            if self.__leftSideBarWidget.getCurrentAnsweredListItem() < 0:
                self.__leftSideBarWidget.selectAnsweredListItem(0)

            if self.__leftSideBarWidget.getAnsweredRowCount() > 0:
                self.__rightSideWidget.show()
                self.__answerDetailsWidget.show()
            else:
                self.__answerDetailsWidget.hide()
                self.__rightSideWidget.hide()

    def __getAnswerDetails(self, question: Question):
        if self.db_worker is not None:
            task = RunnableTask(self.db_worker.get_student_answer, question)
            self.threadpool.start(task)
