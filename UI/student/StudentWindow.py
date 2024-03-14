from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QStackedWidget, QToolBar, \
    QWidgetAction, QSizePolicy, QMainWindow
from UI.LoginFormApp import LoginFormApp
from UI.student.StudentQuestionAnswersWidget import StudentQuestionAnswersWidget


class StudentWindow(QStackedWidget):
    def __init__(self, parent: QMainWindow, authorized_user):
        super(StudentWindow, self).__init__(parent)

        self.main_window = parent
        self.authorized_user = authorized_user

        self.activeWorkers: list[QtCore.QObject] = []

        self.main_window.setWindowTitle("Area Studente")
        self.main_window.resize(800, 500)

        self.__studentQuestionAnswersWidget = StudentQuestionAnswersWidget(authorized_user, self.__onCreatedThread)
        self.addWidget(self.__studentQuestionAnswersWidget)

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
        self.__currentUserUsernameLabel.setStyleSheet("QLabel {padding: 0px 0px 0px 5px;}")
        self.__currentUserUsernameLabel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.__currentUserUsernameAction.setDefaultWidget(self.__currentUserUsernameLabel)

        self.__logoutAction = QWidgetAction(self)
        self.__logoutButton = QPushButton("Logout")
        self.__logoutButton.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.__logoutAction.setDefaultWidget(self.__logoutButton)
        self.__logoutButton.clicked.connect(self.logout)

    def __setToolBar(self):
        self.studentToolBar = QToolBar()
        self.studentToolBar.setMovable(False)
        self.studentToolBar.addAction(self.__currentUserUsernameAction)
        self.studentToolBar.addAction(self.__logoutAction)

        self.main_window.addToolBar(self.studentToolBar)

    def logout(self):
        for worker in self.activeWorkers:
            thread = worker.thread()
            if thread is not None:
                thread.quit()
                thread.deleteLater()

        self.activeWorkers = []

        print("logout, workers", self.activeWorkers)
        self.main_window.removeToolBar(self.studentToolBar)

        window = LoginFormApp(self.main_window)
        window.show()

        self.close()
