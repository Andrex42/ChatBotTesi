from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QMessageBox, QPushButton, QVBoxLayout, QListWidget, QListWidgetItem, QHBoxLayout, \
    QLabel, QSizePolicy
from UI.LoginFormApp import LoginFormApp
from UI.TeacherEditQuestionDialog import EditQuestionDialog
from UI.TeacherQuestionDialog import QuestionDialog
from mock import MOCK_DATA
from collection import init_chroma_client, get_collections, extract_data, get_question_collection, get_teacher_answers_collection, get_student_answers_collection, populate_collections

import time


skip_db_creation = False


class Worker(QtCore.QObject):
    """
    Worker thread that handles the major program load. Allowing the gui to still be responsive.
    """
    def __init__(self, teacher_id, config):
        super(Worker, self).__init__()
        self.teacher_id = teacher_id
        self.config = config

    #QT signals - specify the method that the worker will be executing
    call_start_ml = QtCore.pyqtSignal()
    call_add_question = QtCore.pyqtSignal()

    questions_ready_event = QtCore.pyqtSignal(object)
    question_added_event = QtCore.pyqtSignal(object)
    answer_ready_event = QtCore.pyqtSignal(object)

    @QtCore.pyqtSlot()
    def start_ml(self):
        start = time.time()

        init_chroma_client()

        if not skip_db_creation:
            populate_collections()
            print("Database created")

        question_collection, teacher_answers_collection, student_answers_collection = get_collections()

        print("getting questions of teacher", self.teacher_id)

        query_result = question_collection.get(
            where={"teacher_id": self.teacher_id},
        )

        # query_result = question_collection.query(
        #     query_texts=["Quale può essere il futuro dell'intelligenza artificiale?"],
        #     n_results=10
        # )

        # print("# The most similar sentences computed by chroma")
        # print(query_result)
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
    def get_teacher_answer(self, question_id):
        start = time.time()

        # init_chroma_client()

        teacher_answers_collection = get_teacher_answers_collection()

        print("getting answers for", question_id)

        query_result = teacher_answers_collection.get(
            ids=[question_id],
            where={"teacher_id": self.teacher_id}
        )

        self.answer_ready_event.emit(query_result)
        # print(query_result)
        print(f'Execution time = {time.time() - start} seconds.')


class TeacherWindow(QWidget):
    def __init__(self, parent):
        super(TeacherWindow, self).__init__(parent)

        self.main_window = parent

        self.main_window.setWindowTitle("Area Docente")
        self.main_window.resize(800, 500)

        self.main_window.setCentralWidget(self)

        layout = QVBoxLayout()
        self.listWidget = QListWidget()

        # for question in MOCK_DATA:
        #     self.addQuestionToListWidget(question["value"])

        self.config = {}
        self.db_worker = Worker("docente.test1", self.config)
        self.db_worker.call_start_ml.connect(self.db_worker.start_ml)
        self.db_worker.questions_ready_event.connect(lambda data: self.on_questions_ready(data))
        self.db_worker.question_added_event.connect(lambda data: self.on_question_added(data))

        self.start_db_worker()

        self.addButton = QPushButton('Aggiungi Domanda')
        self.logoutButton = QPushButton('Logout')

        layout.addWidget(self.listWidget)
        layout.addWidget(self.addButton)
        layout.addWidget(self.logoutButton)

        self.setLayout(layout)

        self.logoutButton.clicked.connect(self.logout)

    @QtCore.pyqtSlot()
    def on_questions_ready(self, data):
        print("received", data)
        data_array = extract_data(data)
        print("data converted", data_array)

        for question in data_array:
            self.addQuestionToListWidget(question)

    @QtCore.pyqtSlot()
    def on_question_added(self, question):
        print("received", question)
        print(question)

        self.addQuestionToListWidget(question)

        self.add_question_thread.quit()

    def start_db_worker(self):
        self.db_thread = QtCore.QThread()
        self.db_thread.start()

        self.db_worker.moveToThread(self.db_thread)
        self.db_worker.call_start_ml.emit()

    def add_question(self, question_text):
        self.db_worker.add_question(question_text)

    def addQuestionToListWidget(self, question):
        itemWidget = QWidget()
        itemLayout = QHBoxLayout()

        questionLabel = QLabel(question["document"])
        questionLabel.setWordWrap(True)  # Abilita il wrapping del testo
        questionLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        buttonsContainer = QWidget()
        buttonsLayout = QHBoxLayout(buttonsContainer)

        viewButton = QPushButton('Visualizza')
        editButton = QPushButton('Modifica')
        deleteButton = QPushButton('Elimina')

        # Collegamento dei bottoni alle loro funzioni
        viewButton.clicked.connect(lambda checked, q=question: self.viewQuestion(q))
        editButton.clicked.connect(lambda checked, q=question: self.editQuestion(q))
        deleteButton.clicked.connect(lambda checked, q=question: self.confirmDelete(q))

        itemLayout.addWidget(questionLabel)
        itemLayout.addWidget(buttonsContainer)
        buttonsLayout.addWidget(viewButton)
        buttonsLayout.addWidget(editButton)
        buttonsLayout.addWidget(deleteButton)

        itemWidget.setLayout(itemLayout)

        listItem = QListWidgetItem(self.listWidget)
        listItem.setSizeHint(QtCore.QSize(itemWidget.sizeHint().width(), itemWidget.sizeHint().height() - 20))

        self.listWidget.setItemWidget(listItem, itemWidget)

    def viewQuestion(self, question):
        def load_callback():
            print("ok, view question riuscito", question)

        self.dialog = QuestionDialog(question, self.db_worker.answer_ready_event, load_callback)

        self.db_worker.get_teacher_answer(question["id"])

        self.dialog.show()

    def editQuestion(self, question):
        def save_callback(new_text):
            # Qui dovresti aggiornare la domanda effettivamente, per semplicità la stampiamo solo
            print(f"Nuova domanda: {new_text}")  # Aggiorna questa parte per modificare i dati effettivi

        self.dialog = EditQuestionDialog(question, save_callback)
        self.dialog.show()

    # Implementazione della conferma di eliminazione
    def confirmDelete(self, question):
        reply = QMessageBox.question(self, 'Elimina Domanda',
                                     "Sei sicuro di voler eliminare questa domanda?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            print(f"Domanda eliminata: {question}")  # Qui dovresti eliminare la domanda effettivamente

    def logout(self):
        window = LoginFormApp(self.main_window)
        window.show()

        # self.close()