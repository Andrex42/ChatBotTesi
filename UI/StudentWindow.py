from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QListWidget
from UI.LoginFormApp import LoginFormApp
from mock import MOCK_DATA


class StudentWindow(QWidget):
    def __init__(self, parent):
        super(StudentWindow, self).__init__(parent)

        self.main_window = parent

        self.main_window.setWindowTitle("Area Studente")
        self.main_window.resize(800, 500)

        self.main_window.setCentralWidget(self)

        layout = QVBoxLayout()

        self.unansweredLabel = QLabel("Domande senza risposta:")
        self.unansweredList = QListWidget()
        self.answeredLabel = QLabel("Domande con risposta:")
        self.answeredList = QListWidget()
        self.logoutButton = QPushButton('Logout')

        for question in MOCK_DATA:
            self.unansweredList.addItem(question["value"])  # Simula che tutte le domande non hanno risposta

        layout.addWidget(self.unansweredLabel)
        layout.addWidget(self.unansweredList)
        layout.addWidget(self.answeredLabel)
        layout.addWidget(self.answeredList)
        layout.addWidget(self.logoutButton)

        self.setLayout(layout)

        self.logoutButton.clicked.connect(self.logout)

    def logout(self):
        window = LoginFormApp(self.main_window)
        window.show()

        # self.close()
