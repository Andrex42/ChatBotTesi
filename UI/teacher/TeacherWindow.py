from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QPushButton, QLabel, QSizePolicy, QStackedWidget, QToolBar, QWidgetAction
from UI.LoginFormApp import LoginFormApp
from UI.teacher.TeacherEditQuestionDialog import EditQuestionDialog
from UI.teacher.TeacherQuestionAnswersWidget import TeacherQuestionAnswersWidget
from UI.teacher.TeacherQuestionDialog import QuestionDialog


class TeacherWindow(QStackedWidget):
    def __init__(self, parent, authorized_user):
        super(TeacherWindow, self).__init__(parent)

        self.main_window = parent
        self.authorized_user = authorized_user

        self.activeWorkers: list[QtCore.QObject] = []

        self.main_window.setWindowTitle("Area Docente")

        self.__teacherQuestionAnswersWidget = TeacherQuestionAnswersWidget(authorized_user, self.__onCreatedThread)
        self.addWidget(self.__teacherQuestionAnswersWidget)

        self.__setActions()
        self.__setToolBar()

        self.main_window.resize(800, 500)
        self.main_window.setCentralWidget(self)

    def __onCreatedThread(self, worker):
        print("worker created", worker)
        self.activeWorkers.append(worker)

    def __setActions(self):
        # toolbar action
        self.__currentUserUsernameAction = QWidgetAction(self)
        self.__currentUserUsernameLabel = QLabel(self.authorized_user['username'])
        self.__currentUserUsernameLabel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.__currentUserUsernameAction.setDefaultWidget(self.__currentUserUsernameLabel)

        self.__logoutAction = QWidgetAction(self)
        self.__logoutButton = QPushButton("Logout")
        self.__logoutButton.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.__logoutAction.setDefaultWidget(self.__logoutButton)
        self.__logoutButton.clicked.connect(self.logout)

    def __setToolBar(self):
        aiTypeToolBar = QToolBar()
        aiTypeToolBar.setMovable(False)
        aiTypeToolBar.addAction(self.__currentUserUsernameAction)
        aiTypeToolBar.addAction(self.__logoutAction)

        self.main_window.addToolBar(aiTypeToolBar)

    def add_question(self, question_text):
        self.db_worker.add_question(question_text)


    def viewQuestion(self, question):
        def load_callback():
            print("ok, view question riuscito", question)

        self.dialog = QuestionDialog(
            self.authorized_user,
            question,
            self.db_worker.q_a_ready_event,
            load_callback)

        self.db_worker.get_students_answers(question["id"], question["document"])

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
        for worker in self.activeWorkers:
            thread = worker.thread()
            if thread is not None:
                thread.quit()
                thread.deleteLater()

        self.activeWorkers = []

        print("logout, workers", self.activeWorkers)

        window = LoginFormApp(self.main_window)
        window.show()

        self.close()