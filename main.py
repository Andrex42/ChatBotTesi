import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDesktopWidget
from UI.LoginFormApp import LoginFormApp

from collection import init_model, init_model_with_exports, check_answer_records


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

    Returns
    -------
    Np.array
        The tfidf vector representation of the text
    """
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = Application(app)
    window.center()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
