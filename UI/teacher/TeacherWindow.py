from PyQt5 import QtCore
from PyQt5.QtWidgets import QPushButton, QLabel, QSizePolicy, QStackedWidget, QToolBar, QWidgetAction, QMainWindow, \
    QWidget, QDesktopWidget
from UI.LoginFormApp import LoginFormApp
from UI.teacher.TeacherQuestionAnswersWidget import TeacherQuestionAnswersWidget


class TeacherWindow(QStackedWidget):
    def __init__(self, parent: QMainWindow, authorized_user):
        super(TeacherWindow, self).__init__(parent)

        self.main_window = parent
        self.authorized_user = authorized_user

        self.activeWorkers: list[QtCore.QObject] = []

        self.main_window.setWindowTitle("Area Docente")

        self.__teacherQuestionAnswersWidget = TeacherQuestionAnswersWidget(parent, authorized_user, self.__onCreatedThread)
        self.addWidget(self.__teacherQuestionAnswersWidget)

        self.__setActions()
        self.__setToolBar()

       
        screen_geometry = QDesktopWidget().screenGeometry()

        
        window_width = screen_geometry.width() // 1.33
        window_height = screen_geometry.height() // 1.33
        self.main_window.resize(int(window_width), int(window_height))

        self.main_window.center()

        self.main_window.setCentralWidget(self)

    def __onCreatedThread(self, worker):
        print("worker created", worker)
        self.activeWorkers.append(worker)

    def __setActions(self):
       
        self.__currentUserUsernameAction = QWidgetAction(self)
        self.__currentUserUsernameLabel = QLabel(self.authorized_user['username'])
        self.__currentUserUsernameLabel.setStyleSheet("QLabel {padding: 0px 0px 0px 5px;}")
        self.__currentUserUsernameLabel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.__currentUserUsernameAction.setDefaultWidget(self.__currentUserUsernameLabel)

        self.__statsAction = QWidgetAction(self)
        self.__statsButton = QPushButton("Statistiche")
        self.__statsButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.__statsButton.setStyleSheet('''
            QPushButton {
                margin-right: 3px;
                margin-top: 3px;
                margin-bottom: 3px;
            }''')
        self.__statsAction.setDefaultWidget(self.__statsButton)
        self.__statsButton.clicked.connect(self.open_stats)

        self.__archivedAction = QWidgetAction(self)
        self.__archivedButton = QPushButton("Archiviate")
        self.__archivedButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.__archivedButton.setStyleSheet('''
            QPushButton {
                margin-right: 3px;
                margin-top: 3px;
                margin-bottom: 3px;
            }''')
        self.__archivedAction.setDefaultWidget(self.__archivedButton)
        self.__archivedButton.clicked.connect(self.open_archived)

        self.__logoutAction = QWidgetAction(self)
        self.__logoutButton = QPushButton("Logout")
        self.__logoutButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.__logoutButton.setStyleSheet('''
            QPushButton {
                margin-right: 10px;
                margin-top: 3px;
                margin-bottom: 3px;
            }''')
        self.__logoutAction.setDefaultWidget(self.__logoutButton)
        self.__logoutButton.clicked.connect(self.logout)

    def __setToolBar(self):
        self.teacherToolBar = QToolBar()
        self.teacherToolBar.setMovable(False)
        self.teacherToolBar.addAction(self.__currentUserUsernameAction)
        spacer = QWidget() 
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.teacherToolBar.addWidget(spacer)
        self.teacherToolBar.addAction(self.__archivedAction)
        self.teacherToolBar.addAction(self.__statsAction)
        self.teacherToolBar.addAction(self.__logoutAction)

        self.main_window.addToolBar(self.teacherToolBar)

    def open_stats(self):
        self.__teacherQuestionAnswersWidget.open_stats_window()

    def open_archived(self):
        self.__teacherQuestionAnswersWidget.open_archived_window()

    def logout(self):
        

        self.activeWorkers = []

        print("logout, workers", self.activeWorkers)
        self.main_window.removeToolBar(self.teacherToolBar)

        window = LoginFormApp(self.main_window)
        window.main_window.center()
        window.show()

        self.close()
