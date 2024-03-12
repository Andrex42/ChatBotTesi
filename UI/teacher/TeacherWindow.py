from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QPushButton, QLabel, QSizePolicy, QStackedWidget, QToolBar, QWidgetAction
from UI.LoginFormApp import LoginFormApp
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

    # Implementazione della conferma di eliminazione
    def confirmDelete(self, question):
        reply = QMessageBox.question(self, 'Elimina Domanda',
                                     "Sei sicuro di voler eliminare questa domanda?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            print(f"Domanda eliminata: {question}")  # TODO: Qui dovresti eliminare la domanda effettivamente

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