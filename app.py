import sys, os

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDesktopWidget
from UI.LoginFormApp import LoginFormApp

from collection import init_model, init_model_with_exports, check_answer_records


try:
    base_path = sys._MEIPASS
    os.chdir(base_path)
except Exception:
    pass



class Application(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setup_ui()

        init_model_with_exports()
        # init_model()
        # check_answer_records()
        # test_model()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def __beforeClose(self):
        message = "Vuoi uscire dall'applicazione?"
        closeMessageBox = QMessageBox(self)
        closeMessageBox.setWindowTitle('Chiudi applicazione')
        closeMessageBox.setText(message)
        closeMessageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        reply = closeMessageBox.exec()
        # Cancel
        if reply == QMessageBox.Cancel:
            return True
        elif reply == QMessageBox.Yes:
            self.app.quit()

    def closeEvent(self, e):
        f = self.__beforeClose()
        if f:
            e.ignore()
        else:
            return super().closeEvent(e)

    def setup_ui(self):
        login_widget = LoginFormApp(self)


def main():
    """Main function
    """
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = Application(app)

    # setup stylesheet
    # apply_stylesheet(app, theme='dark_blue.xml')
    app.setStyleSheet('''
        QPushButton {
            color: white;
            background-color: #4682b4;
            border-width: 0px;
            border-style: solid;
            margin: 0;
            padding-top: 5px;
            padding-bottom: 5px;
            padding-left: 10px;
            padding-right: 10px;
            border-radius: 4px;
            /* outline: none; */
            /* min-width: 40px; */
        }
        
        QPushButton:disabled {
            color: white;
            background-color: #1c3448;
        }
        
        QLineEdit {
            border-radius: 4px;
            padding-top: 5px;
            padding-bottom: 5px;
            padding-left: 10px;
            padding-right: 10px;
        }
        
        QTextEdit, QPlainTextEdit {
            border-radius:4px; 
            background-color: palette(base);
            padding-top: 5px;
            padding-bottom: 5px;
            padding-left: 10px;
            padding-right: 10px;
        }
        
        QSpinBox,
        QSpinBox:editable,
        QSpinBox:hover,
        QSpinBox:pressed {
          border: none;
          border-radius: 4px;
          background-color: rgba(0, 0, 0, 0.2);
          padding: 5px 4px 4px 4px;
        }
        QSpinBox:focus {
          border: none;
          border-bottom: 2px solid #4682b4;
          border-radius: 4px;
          background-color: rgba(0, 0, 0, 0.2);
          padding: 5px 4px 4px 4px;
        }
        QSpinBox:disabled {
          border: none;
          border-bottom: 2px solid #999999;
          border-radius: 0;
          background-color: rgba(0, 0, 0, 0.1);
          padding: 5px 15px 4px 4px;
        }
        QSpinBox::up-button {
          subcontrol-origin: border;
          subcontrol-position: top right;
          border: none;
          border-radius: 4px;
          padding: 5px;
          background-color: #4682b4;
          margin-top: 1px;
          width: 18px;
        }
        QSpinBox::up-button:disabled,
        QSpinBox::up-button:off {
          background-color: rgba(70, 130, 180, .3);
        }
        QSpinBox::down-button {
          subcontrol-origin: border;
          subcontrol-position: bottom right;
          border: none;
          border-radius: 4px;
          padding: 5px;
          background-color: #4682b4;
          width: 18px;
        }
        QSpinBox::down-button:disabled,
        QSpinBox::down-button:off  {
          background-color: rgba(70, 130, 180, .3);
        }
        QSpinBox::up-arrow {
          image: url("resources/icons/chevron-up.svg");
        }
        QSpinBox::up-arrow:disabled,
        QSpinBox::up-arrow:off {
          image: url("resources/icons/chevron-up.svg");
        }
        QSpinBox::down-arrow {
          image: url("resources/icons/chevron-down.svg");
        }
        QSpinBox::down-arrow:disabled,
        QSpinBox::down-arrow:off {
          image: url("resources/icons/chevron-down.svg");
        }
        ''')

    window.center()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
