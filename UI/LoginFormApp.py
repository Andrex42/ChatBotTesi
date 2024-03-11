import os

from PyQt5.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from users import STUDENTS, TEACHERS


class LoginFormApp(QWidget):
    def __init__(self, parent):
        super(LoginFormApp, self).__init__(parent)

        self.main_window = parent

        # Set the window properties (title and initial size)
        self.main_window.setWindowTitle("Login Form")
        self.main_window.setGeometry(100, 100, 300, 150)  # (x, y, width, height)

        # Create a central widget for the main window
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)

        # Create a QFormLayout to arrange the widgets
        form_layout = QFormLayout()

        # Create QLabel and QLineEdit widgets for username
        username_label = QLabel("Username:")
        self.username_field = QLineEdit()

        # Create QLabel and QLineEdit widgets for password
        password_label = QLabel("Password:")
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)

        # Create a QPushButton for login
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)

        # Add widgets to the form layout
        form_layout.addRow(username_label, self.username_field)
        form_layout.addRow(password_label, self.password_field)
        form_layout.addRow(login_button)

        # Set the layout for the central widget
        central_widget.setLayout(form_layout)

        self.prefill_creds(os.getenv("PREFILL_CREDS"))

    def prefill_creds(self, type: str):
        if type == "teacher":
            self.username_field.setText("docente.archeologia")
            self.password_field.setText("docente123")
        elif type == "student":
            self.username_field.setText("studente.archeologia")
            self.password_field.setText("studente123")

    def check_login(self, username, password):
        authorized_user = None

        student = next((s for s in STUDENTS if s["username"] == username), None)

        if student is not None and student["password"] == password:
            authorized_user = {
                "username": username,
                "role": "student"
            }
        else:
            teacher = next((s for s in TEACHERS if s["username"] == username), None)
            if teacher is not None and teacher["password"] == password:
                authorized_user = {
                    "username": username,
                    "role": "teacher"
                }

        return authorized_user

        # Check if the username and password are valid (for demonstration purposes)
        # if username == "docente" and password == "123456":
        #     QMessageBox.information(self, "Login Successful", "Welcome, " + username + "!")
        # elif username == "studente" and password == "123456":
        #     QMessageBox.information(self, "Login Successful", "Welcome, " + username + "!")

    def login(self):
        # Retrieve the username and password entered by the user
        username = self.username_field.text()
        password = self.password_field.text()

        authorized_user = self.check_login(username, password)

        if authorized_user is not None:
            print(authorized_user)
            if authorized_user["role"] == "student":
                from UI.StudentWindow import StudentWindow
                window = StudentWindow(self.main_window, authorized_user)
                window.show()
                # self.close()
            elif authorized_user["role"] == "teacher":
                from UI.TeacherWindow import TeacherWindow
                window = TeacherWindow(self.main_window, authorized_user)
                window.show()
                # self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password. Please try again.")