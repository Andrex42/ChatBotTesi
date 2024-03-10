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
        # menu action
        self.__exitAction = QAction('Exit', self)
        self.__exitAction.triggered.connect(self.__beforeClose)

        self.__aboutAction = QAction('About...', self)
        #self.__aboutAction.triggered.connect(self.__showAboutDialog)

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

    def __beforeClose(self):
        message = 'The window will be closed. Would you like to continue running this app in the background?'
        closeMessageBox = QMessageBox(self)
        closeMessageBox.setWindowTitle('Wait!')
        closeMessageBox.setText(message)
        closeMessageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        reply = closeMessageBox.exec()
        # Cancel
        if reply == QMessageBox.Cancel:
            return True
        else:
            # Yes
            if reply == QMessageBox.Yes:
                self.close()
            # No
            elif reply == QMessageBox.No:
                self.main_window.app.quit()

    def logout(self):
        window = LoginFormApp(self.main_window)
        window.show()

        # self.close()
