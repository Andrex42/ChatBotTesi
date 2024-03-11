import time

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QLineEdit, QDoubleSpinBox

from collection import init_chroma_client, get_collections, get_chroma_q_a_collection


class Worker(QtCore.QObject):
    """
    Worker thread that handles the major program load. Allowing the gui to still be responsive.
    """
    def __init__(self, authorized_user, config):
        super(Worker, self).__init__()
        self.authorized_user = authorized_user
        self.config = config

    answer_added_event = QtCore.pyqtSignal(object)

    @QtCore.pyqtSlot()
    def start_ml(self, answer, voto):
        start = time.time()

        init_chroma_client()

        id = answer['id']

        q_a_collection = get_chroma_q_a_collection()

        print("updating answer with evaluation", answer)

        q_a_collection.update(
            ids=[id],
            metadatas=[{"id_domanda": answer['id_domanda'],
                        "domanda": answer['domanda'],
                        "id_docente": answer['id_docente'],
                        "id_autore": answer['id_autore'],
                        "voto_docente": voto,
                        "voto_predetto": answer['voto_predetto'],
                        "commento": answer['commento'],
                        "source": answer['source'],
                        "data_creazione": answer['data_creazione']}],
        )

        print(f'Execution time = {time.time() - start} seconds.')


class TeacherStudentAnswerPreviewItem(QWidget):
    def __init__(self, authorized_user, answer, evaluated):
        super().__init__()

        self.authorized_user = authorized_user
        self.answer = answer
        self.evaluated = evaluated

        self.__initUi()
        self.__initWorker()

    def __initUi(self):
        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        label_id_studente = QLabel("Studente: " + self.answer["id_autore"])
        label_id_studente.setStyleSheet('''
                                            QLabel {
                                                font-size: 12px; 
                                                font-weight: bold;
                                            }
                                        ''')

        answer_label = QLabel(self.answer["document"])
        answer_label.setWordWrap(True)

        risultatoLayout = QHBoxLayout()
        risultatoLayout.setSpacing(0)
        risultatoLayout.setContentsMargins(0, 0, 0, 0)

        if not self.evaluated:
            label_risultato = QLabel(str(self.answer["voto_predetto"]))
            if self.answer["voto_predetto"] >= 3:
                label_risultato.setStyleSheet('''
                                    QLabel {
                                        font-size: 12px; 
                                        font-weight: bold;
                                        color: #32a852;
                                    }
                                ''')
            else:
                label_risultato.setStyleSheet('''
                                    QLabel {
                                        font-size: 12px; 
                                        font-weight: bold;
                                        color: #a83232;
                                    }
                                ''')

            self.votoCustomSpinBox = QDoubleSpinBox()
            self.votoCustomSpinBox.setValue(self.answer["voto_predetto"])
            self.votoCustomSpinBox.setMinimum(0)
            self.votoCustomSpinBox.setMaximum(5)

            assegnaVotoBtn = QPushButton("Assegna voto")

            confermaVotoLayout = QHBoxLayout()
            confermaVotoLayout.setSpacing(0)
            confermaVotoLayout.setContentsMargins(0, 0, 0, 0)

            lay.addWidget(label_id_studente)
            lay.addWidget(answer_label)
            risultatoLayout.addWidget(QLabel("Risultato predetto: "))
            risultatoLayout.addWidget(label_risultato)
            lay.addLayout(risultatoLayout)
            confermaVotoLayout.addWidget(self.votoCustomSpinBox)
            confermaVotoLayout.addWidget(assegnaVotoBtn)
            lay.addLayout(confermaVotoLayout)

            assegnaVotoBtn.clicked.connect(self.__assignVote)
        else:
            label_risultato = QLabel(str(self.answer["voto_docente"]))
            if self.answer["voto_docente"] >= 3:
                label_risultato.setStyleSheet('''
                                                QLabel {
                                                    font-size: 12px; 
                                                    font-weight: bold;
                                                    color: #32a852;
                                                }
                                            ''')
            else:
                label_risultato.setStyleSheet('''
                                                QLabel {
                                                    font-size: 12px; 
                                                    font-weight: bold;
                                                    color: #a83232;
                                                }
                                            ''')

            lay.addWidget(label_id_studente)
            lay.addWidget(answer_label)
            risultatoLayout.addWidget(QLabel("Voto finale: "))
            risultatoLayout.addWidget(label_risultato)
            lay.addLayout(risultatoLayout)

        self.setLayout(lay)

    def __initWorker(self):
        self.config = {}
        self.db_worker = Worker(self.authorized_user, self.config)

        self.db_thread = QtCore.QThread()
        self.db_thread.start()

        self.db_worker.moveToThread(self.db_thread)

    def __assignVote(self):
        self.db_worker.start_ml(self.answer, self.votoCustomSpinBox.value())
