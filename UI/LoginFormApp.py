import os

from PyQt5.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QMainWindow
from users import STUDENTS, TEACHERS


class LoginFormApp(QWidget):
    def __init__(self, parent: QMainWindow):
        super(LoginFormApp, self).__init__(parent)

        self.main_window = parent

        
        self.main_window.setWindowTitle("Login")
        self.main_window.setGeometry(0, 0, 300, 150)  

        
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)

        
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

       
        username_label = QLabel("Username:")
        self.username_field = QLineEdit()

       
        password_label = QLabel("Password:")
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)

        
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)

        
        form_layout.addRow(username_label, self.username_field)
        form_layout.addRow(password_label, self.password_field)
        form_layout.addRow(login_button)

        
        central_widget.setLayout(form_layout)

        self.prefill_creds(os.getenv("PREFILL_CREDS"))

    def prefill_creds(self, type: str):
        if type == "teacher":
           
            self.password_field.setText("tesi123")
        elif type == "student":
            
            self.password_field.setText("tesi123")

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

    def login(self):
        
        username = self.username_field.text()
        password = self.password_field.text()

        authorized_user = self.check_login(username, password)

        if authorized_user is not None:
            print(authorized_user)
            if authorized_user["role"] == "student":
                from UI.student.StudentWindow import StudentWindow
                window = StudentWindow(self.main_window, authorized_user)
                window.show()
                
            elif authorized_user["role"] == "teacher":
                from UI.teacher.TeacherWindow import TeacherWindow
                window = TeacherWindow(self.main_window, authorized_user)
                window.show()
                
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password. Please try again.")
