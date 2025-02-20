from datetime import datetime
import openai  
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSpinBox, \
    QSizePolicy, QSpacerItem, QGraphicsOpacityEffect, QMessageBox

from model.answer_model import Answer
from model.question_model import Question
import sys
sys.path.append(r'C:\Users\andre\Desktop\ChatBotTesi')
from evaluation_criteria import evaluation_criteria

openai.api_key = 'KEY OPENAI PERSONALE'


class TeacherStudentAnswerPreviewItem(QWidget):
    def __init__(self, authorized_user, question: Question, answer: Answer, evaluated, assign_vote_clicked=None):
        super().__init__()

        self.authorized_user = authorized_user
        self.question = question
        self.answer = answer
        self.evaluated = evaluated
        self.assign_vote_clicked = assign_vote_clicked

        self.__initUi()

    def convert_datetime(self, datetime_str):
        datetime_obj = datetime.fromisoformat(datetime_str)
        return datetime_obj.strftime("%d/%m/%Y %H:%M")

    def __initUi(self):
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("answer_preview_item_container")
        self.setStyleSheet(''' 
                    #answer_preview_item_container {
                        background-color: rgba(0, 0, 0, 0.1);
                        border-radius: 20px;
                    }''')

        lay = QVBoxLayout()
        lay.setSpacing(0)

        label_id_studente = QLabel("Studente: " + self.answer.id_autore)
        label_id_studente.setStyleSheet(''' 
                                            QLabel {
                                                font-size: 12px; 
                                                font-weight: bold;
                                            }
                                        ''')

        label_data_risposta = QLabel(self.convert_datetime(self.answer.data_creazione))
        label_data_risposta.setStyleSheet(''' 
                                            QLabel {
                                                font-size: 10px; 
                                            }
                                        ''')
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.6) 
        label_data_risposta.setGraphicsEffect(opacity_effect)

        answer_label = QLabel(self.answer.risposta)
        answer_label.setWordWrap(True)

        risultatoLayoutV = QVBoxLayout()
        risultatoLayoutHTop = QHBoxLayout()
        risultatoLayoutHBottom = QHBoxLayout()

        if not self.evaluated:
            self.label_risultato_ref = QLabel(str(self.answer.voto_predetto))
            self.label_risultato = QLabel(str(self.answer.voto_predetto_all))

            policy = self.label_risultato_ref.sizePolicy()
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            self.label_risultato_ref.setSizePolicy(policy)

            policy = self.label_risultato.sizePolicy()
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            self.label_risultato.setSizePolicy(policy)

            if self.answer.voto_predetto >= 6:
                self.label_risultato_ref.setStyleSheet(''' 
                                    QLabel {
                                        font-size: 12px; 
                                        font-weight: bold;
                                        color: #32a852;
                                    }
                                ''')
            else:
                self.label_risultato_ref.setStyleSheet(''' 
                                    QLabel {
                                        font-size: 12px; 
                                        font-weight: bold;
                                        color: #a83232;
                                    }
                                ''')

            if self.answer.voto_predetto >= 6:
                self.label_risultato.setStyleSheet(''' 
                                    QLabel {
                                        font-size: 12px; 
                                        font-weight: bold;
                                        color: #32a852;
                                    }
                                ''')
            else:
                self.label_risultato.setStyleSheet(''' 
                                    QLabel {
                                        font-size: 12px; 
                                        font-weight: bold;
                                        color: #a83232;
                                    }
                                ''')

            
            self.label_chatgpt_voto = QLabel(str(self.answer.chat_gpt_rating)) 
            self.label_chatgpt_voto.setStyleSheet(''' 
                                                QLabel {
                                                    font-size: 12px;
                                                    font-weight: bold;
                                                    color: #4285F4;  /* Colore del voto di ChatGPT */
                                                }
                                            ''')

            self.votoCustomSpinBox = QSpinBox()
            self.votoCustomSpinBox.setValue(self.answer.voto_predetto)
            self.votoCustomSpinBox.setSingleStep(1)
            self.votoCustomSpinBox.setMinimum(1)
            self.votoCustomSpinBox.setMaximum(10)
            self.votoCustomSpinBox.setMinimumWidth(80)

            assegnaVotoBtn = QPushButton("Assegna voto")
            assegnaVotoBtn.setStyleSheet(''' 
                QPushButton {
                    margin-left: 10px;
                    min-width: 150px;  /* Imposta una larghezza minima */
                }''')

            assegnaVotoEUsaComeRefBtn = QPushButton("Assegna voto e usa come riferimento")
            assegnaVotoEUsaComeRefBtn.setStyleSheet(''' 
                QPushButton {
                    margin-left: 10px;
                    min-width: 250px;  /* Imposta una larghezza minima */
                }''')

            confermaVotoLayout = QHBoxLayout()

            lay.addWidget(label_id_studente)
            lay.addWidget(label_data_risposta)
            lay.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
            lay.addWidget(answer_label)
            lay.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

            risultatoLayoutHTop.addWidget(QLabel("Il voto predetto dalla tua risposta di riferimento è: "))
            risultatoLayoutHTop.addWidget(self.label_risultato_ref)

            risultatoLayoutHBottom.addWidget(QLabel("Il voto predetto da tutte le altre risposte valutate è: "))
            risultatoLayoutHBottom.addWidget(self.label_risultato)

            risultatoLayoutV.addLayout(risultatoLayoutHTop)
            risultatoLayoutV.addLayout(risultatoLayoutHBottom)
            lay.addLayout(risultatoLayoutV)

            lay.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

            
            help_button = QPushButton("Help")
            help_button.setStyleSheet(''' 
                QPushButton {
                    margin-left: 10px;
                    min-width: 150px;  /* Imposta una larghezza minima */
                }''')

            
            def show_help():
                try:
                   
                    motivations = self.get_chatgpt_motivations()

                    
                    QMessageBox.information(self, "Motivazioni", motivations)
                except Exception as e:
                    
                    QMessageBox.critical(self, "Errore", f"Errore nel recuperare le motivazioni: {str(e)}")

            
            help_button.clicked.connect(show_help)

            
            chatgpt_layout = QHBoxLayout()
            chatgpt_layout.setContentsMargins(0, 0, 0, 0)  
            chatgpt_layout.setSpacing(5)  
            chatgpt_layout.addWidget(QLabel("Il voto suggerito da ChatGpt è: "))
            chatgpt_layout.addWidget(self.label_chatgpt_voto)
            chatgpt_layout.addWidget(help_button)  

            lay.addLayout(chatgpt_layout)

            lay.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

            confermaVotoLayout.addWidget(self.votoCustomSpinBox)
            confermaVotoLayout.addWidget(assegnaVotoBtn)
            confermaVotoLayout.addWidget(assegnaVotoEUsaComeRefBtn)
            confermaVotoLayout.addStretch()

            lay.addLayout(confermaVotoLayout)

            assegnaVotoBtn.clicked.connect(self.__assignVoteClicked)
            assegnaVotoEUsaComeRefBtn.clicked.connect(self.__assignVoteAndUseAsRefClicked)
        else:
            label_risultato = QLabel(str(self.answer.voto_docente))
            policy = label_risultato.sizePolicy()
            policy.setHorizontalPolicy(QSizePolicy.Minimum)
            label_risultato.setSizePolicy(policy)

            if self.answer.voto_docente >= 6:
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
            lay.addWidget(label_data_risposta)
            lay.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
            lay.addWidget(answer_label)
            lay.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

            voto_finale_lbl = QLabel("Voto finale: ")
            risultatoLayoutHTop.addWidget(voto_finale_lbl)
            risultatoLayoutHTop.addWidget(label_risultato)
            suffix = QLabel("/10")
            risultatoLayoutHBottom.addWidget(suffix)
            lay.addLayout(risultatoLayoutV)

        self.setLayout(lay)

    def get_chatgpt_motivations(self):
        """
        Genera una spiegazione dettagliata delle motivazioni per il voto assegnato a una risposta, 
        utilizzando i criteri di valutazione.
        """
        prompt = (
            f"Domanda: {self.question}\n"
            f"Risposta: {self.answer.risposta}\n"
            f"Voto assegnato: {self.answer.chat_gpt_rating}\n\n"
            "Per favore, fornisci una spiegazione dettagliata e completa che illustri i motivi che giustificano il voto assegnato, "
            "analizzando i punti di forza e le debolezze della risposta in base ai seguenti criteri:\n"
            f"{evaluation_criteria}\n\n"
            "La tua spiegazione dovrebbe essere articolata e fornire esempi concreti per ciascun criterio."
        )


        
        system_message = f"""
        Sei un valutatore imparziale. Utilizza i seguenti criteri di valutazione per motivare il voto assegnato:

        {evaluation_criteria}
        """

        try:
           
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7  
            )

            
            motivations = response['choices'][0]['message']['content']
            print("Motivazione ottenuta da ChatGPT:", motivations)  
            return motivations

        except Exception as e:
            print("Errore nella generazione della motivazione:", e)
            return "Motivazione non disponibile"


    def __assignVoteClicked(self):
        if self.assign_vote_clicked:
            
            self.assign_vote_clicked(self.question, self.answer, self.votoCustomSpinBox.value())

    def __assignVoteAndUseAsRefClicked(self):
        if self.assign_vote_clicked:
            
            self.assign_vote_clicked(self.question, self.answer, self.votoCustomSpinBox.value(), use_as_ref=True)
