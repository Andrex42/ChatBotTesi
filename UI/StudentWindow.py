from PyQt5.QtWidgets import QLabel, QPushButton, QStackedWidget, QToolBar, \
    QWidgetAction, QSizePolicy, QAction, QMessageBox
from UI.LoginFormApp import LoginFormApp
from UI.StudentQuestionAnswersWidget import StudentQuestionAnswersWidget


class StudentWindow(QStackedWidget):
    def __init__(self, parent, authorized_user):
        super(StudentWindow, self).__init__(parent)

        self.main_window = parent
        self.authorized_user = authorized_user

        self.main_window.setWindowTitle("Area Studente")
        self.main_window.resize(800, 500)

        self.__studentQuestionAnswersWidget = StudentQuestionAnswersWidget(authorized_user)
        self.addWidget(self.__studentQuestionAnswersWidget)

        self.__setActions()
        self.__setToolBar()

        self.main_window.resize(800, 500)
        self.main_window.setCentralWidget(self)

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

    def logout(self):
        window = LoginFormApp(self.main_window)
        window.show()

        # self.close()
