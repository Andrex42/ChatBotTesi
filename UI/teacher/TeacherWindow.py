from PyQt5 import QtCore
from PyQt5.QtWidgets import QPushButton, QLabel, QSizePolicy, QStackedWidget, QToolBar, QWidgetAction, QMainWindow, \
    QWidget
from UI.LoginFormApp import LoginFormApp
from UI.teacher.TeacherQuestionAnswersWidget import TeacherQuestionAnswersWidget


class TeacherWindow(QStackedWidget):
    def __init__(self, parent: QMainWindow, authorized_user):
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
        self.__currentUserUsernameLabel.setStyleSheet("QLabel {padding: 0px 0px 0px 5px;}")
        self.__currentUserUsernameLabel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.__currentUserUsernameAction.setDefaultWidget(self.__currentUserUsernameLabel)

        self.__logoutAction = QWidgetAction(self)
        self.__logoutButton = QPushButton("Logout")
        self.__logoutButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.__logoutAction.setDefaultWidget(self.__logoutButton)
        self.__logoutButton.clicked.connect(self.logout)

    def __setToolBar(self):
        self.teacherToolBar = QToolBar()
        self.teacherToolBar.setMovable(False)
        self.teacherToolBar.addAction(self.__currentUserUsernameAction)
        spacer = QWidget()  # Widget fittizio per creare uno spazio vuoto
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.teacherToolBar.addWidget(spacer)
        self.teacherToolBar.addAction(self.__logoutAction)

        self.main_window.addToolBar(self.teacherToolBar)

    def logout(self):
        for worker in self.activeWorkers:
            thread = worker.thread()
            if thread is not None:
                thread.quit()
                thread.deleteLater()

        self.activeWorkers = []

        print("logout, workers", self.activeWorkers)
        self.main_window.removeToolBar(self.teacherToolBar)

        window = LoginFormApp(self.main_window)
        window.show()

        self.close()
