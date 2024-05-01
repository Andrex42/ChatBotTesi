from collections import defaultdict

from PyQt5 import QtCore
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPainter, QPalette, QColor, QBrush
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QMessageBox, QPushButton, QFrame

from UI.teacher.TeacherStudentAnswerPreviewItem import TeacherStudentAnswerPreviewItem
from model.answer_model import Answer
from model.question_model import Question


class RunnableTask(QtCore.QRunnable):
    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.task(*self.args, **self.kwargs)


class QuestionDetailsWidget(QWidget):

    def __init__(self, authorized_user, threadpool, db_worker):
        super().__init__()

        self.authorized_user = authorized_user
        self.threadpool = threadpool
        self.db_worker = db_worker
        self.id_domanda = None

        self.__initUi()
        self.hide()

    def __initUi(self):
        # self.label = QLabel("")
        teacher_question_container = QWidget(self)
        teacher_question_container.setObjectName("teacher_container")  # Setta un ID per il container
        teacher_question_container.setStyleSheet('''
            #teacher_container {
                background-color: rgba(52, 143, 235, 0.1);
                border-radius: 20px;
            }''')

        self.teacher_answer_layout = QVBoxLayout(teacher_question_container)

        self.question_label = QLabel("-")
        self.question_label.setStyleSheet('''
                    QLabel {
                        font-size: 14px; 
                        font-weight: bold;
                    }
                ''')
        self.question_label.setWordWrap(True)

        self.answer_label = QLabel("-")
        self.answer_label.setWordWrap(True)

        self.btnRecalc = QPushButton("Ricalcola")

        task = RunnableTask(self.db_worker.recalc_question_unevaluated_answers_predictions, self.id_domanda)
        self.btnRecalc.clicked.connect(lambda: self.threadpool.start(task))

        lbl = QLabel("DOMANDA")
        lbl.setStyleSheet('''
                    QLabel {
                        font-size: 12px; 
                        font-weight: 300;
                    }
                ''')
        self.teacher_answer_layout.addWidget(lbl)
        self.teacher_answer_layout.addWidget(self.question_label)

        lbl = QLabel("RISPOSTA DI RIFERIMENTO")
        lbl.setStyleSheet('''
                            QLabel {
                                font-size: 12px; 
                                font-weight: 300;
                            }
                        ''')
        self.teacher_answer_layout.addWidget(lbl)
        self.teacher_answer_layout.addWidget(self.answer_label)

        self.students_answers_layout = QVBoxLayout()

        self.students_answers_evaluated_layout = QVBoxLayout()
        self.students_answers_not_evaluated_layout = QVBoxLayout()

        risposte_studenti_label = QLabel("RISPOSTE DEGLI STUDENTI IN ATTESA DI VALUTAZIONE")
        risposte_studenti_label.setStyleSheet('''
                    QLabel {
                        font-size: 12px; 
                        font-weight: 300;
                    }
                ''')
        self.students_answers_not_evaluated_layout.insertSpacing(10, 20)
        self.students_answers_not_evaluated_layout.addWidget(risposte_studenti_label)
        #self.students_answers_not_evaluated_layout.addWidget(self.btnRecalc)

        risposte_studenti_label = QLabel("RISPOSTE DEGLI STUDENTI GIÀ VALUTATE")
        risposte_studenti_label.setStyleSheet('''
                    QLabel {
                        font-size: 12px; 
                        font-weight: 300;
                    }
                ''')
        self.students_answers_evaluated_layout.insertSpacing(10, 20)
        self.students_answers_evaluated_layout.addWidget(risposte_studenti_label)

        scroll_vertical_layout = QVBoxLayout()
        scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_widget = QWidget()

        scroll_widget.setLayout(scroll_vertical_layout)
        scroll.setWidget(scroll_widget)
        # Scroll Area Properties
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        scroll_vertical_layout.addWidget(teacher_question_container)
        scroll_vertical_layout.addLayout(self.students_answers_layout)
        scroll_vertical_layout.addStretch()

        self.students_answers_layout.addLayout(self.students_answers_not_evaluated_layout)
        self.students_answers_layout.addLayout(self.students_answers_evaluated_layout)

        lay = QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(scroll)

        self.setLayout(lay)

    def create_unevaluated_chart(self):
        chart_container = QWidget()
        chart_container.setObjectName("unevaluated_chart")
        lay = QVBoxLayout(chart_container)
        lay.setContentsMargins(0, 0, 0, 0)

        self.unevaluated_chart = QChart()
        self.unevaluated_chart.setMinimumHeight(300)
        self.unevaluated_chart.setMaximumHeight(350)
        self.unevaluated_chart.legend().hide()
        self.unevaluated_chart.setAnimationOptions(QChart.SeriesAnimations)

        self._chart_view = QChartView(self.unevaluated_chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)

        rgb_bg = self.palette().color(QPalette.Window).getRgb()
        current_theme = self.is_dark_or_light(rgb_bg[0], rgb_bg[1], rgb_bg[2])
        print("Palette iniziale", rgb_bg, current_theme)

        if current_theme == "dark":
            self._chart_view.chart().setTheme(QChart.ChartTheme(2))
            self._chart_view.chart().setBackgroundBrush(QBrush(QColor(225, 225, 225, 25)))
        else:
            self._chart_view.chart().setTheme(QChart.ChartTheme(0))
            self._chart_view.chart().setBackgroundBrush(QBrush(QColor(0, 0, 0, 15)))

        #_chart_view.chart().setBackgroundVisible(False)

        lay.addWidget(self._chart_view)

        return chart_container

    def create_evaluated_chart(self):
        chart_container = QWidget()
        chart_container.setObjectName("evaluated_chart")
        lay = QVBoxLayout(chart_container)
        lay.setContentsMargins(0, 0, 0, 0)

        self.evaluated_chart = QChart()
        self.evaluated_chart.setMinimumHeight(300)
        self.evaluated_chart.setMaximumHeight(350)
        self.evaluated_chart.legend().hide()
        self.evaluated_chart.setAnimationOptions(QChart.SeriesAnimations)

        self._chart_view2 = QChartView(self.evaluated_chart)
        self._chart_view2.setRenderHint(QPainter.Antialiasing)
        # _chart_view2.chart().setBackgroundVisible(False)

        rgb_bg = self.palette().color(QPalette.Window).getRgb()
        current_theme = self.is_dark_or_light(rgb_bg[0], rgb_bg[1], rgb_bg[2])
        print("Palette iniziale", rgb_bg, current_theme)

        if current_theme == "dark":
            self._chart_view2.chart().setTheme(QChart.ChartTheme(2))
            self._chart_view2.chart().setBackgroundBrush(QBrush(QColor(225, 225, 225, 25)))
        else:
            self._chart_view2.chart().setTheme(QChart.ChartTheme(0))
            self._chart_view2.chart().setBackgroundBrush(QBrush(QColor(0, 0, 0, 15)))

        lay.addWidget(self._chart_view2)

        return chart_container

    def populateUnevaluatedChart(self, not_evaluated_answers: list[Answer]):
        def count_predictions(answers: list[Answer]) -> dict:
            occorrenze = defaultdict(int)

            for voto in range(1, 11):
                occorrenze[str(voto)] = 0

            for answer in answers:
                voto_predetto_all = answer.voto_predetto_all
                if voto_predetto_all >= 1 and voto_predetto_all <= 10:
                    occorrenze[str(voto_predetto_all)] += 1

            return occorrenze

        self.unevaluated_chart.removeAllSeries()

        frequences = []
        counted_predictions = count_predictions(not_evaluated_answers)

        # counted_predictions["1"] = 2
        # counted_predictions["7"] = 5

        for key, value in counted_predictions.items():
            series = QBarSeries()
            curr_set = QBarSet(str(key))
            curr_set << value
            frequences.append(value)
            series.append(curr_set)

            series.setLabelsVisible(True)
            series.labelsPosition()
            self.unevaluated_chart.addSeries(series)

        #create axis
        self.axisX = QBarCategoryAxis()
        self.axisX.setLabelsVisible(True)
        self.axisX.append(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.axisX.setTitleText("Voti")

        num_ticks = 4
        self.axisY = QValueAxis()
        self.axisY.setLabelsVisible(True)
        self.axisY.setMin(0)
        self.axisY.setMax(max(frequences))
        self.axisY.setTickCount(num_ticks)
        self.axisY.setLabelFormat("%.0f")
        self.axisY.setTitleText("Frequenze")

        # bild the chart
        self.unevaluated_chart.createDefaultAxes()
        self.unevaluated_chart.setAxisX(self.axisX)
        # series.attachAxis(self.axisX)

        self.unevaluated_chart.setAxisY(self.axisY)
        # series.attachAxis(self.axisY)

    def populateEvaluatedChart(self, evaluated_answers: list[Answer]):
        def count_votes(answers: list[Answer]) -> dict:
            occorrenze = defaultdict(int)

            for voto in range(1, 11):
                occorrenze[str(voto)] = 0

            for answer in answers:
                voto_docente = answer.voto_docente
                if voto_docente >= 1 and voto_docente <= 10:
                    occorrenze[str(voto_docente)] += 1

            return occorrenze

        self.evaluated_chart.removeAllSeries()

        frequences = []
        counted_votes = count_votes(evaluated_answers)

        for key, value in counted_votes.items():
            series = QBarSeries()
            curr_set = QBarSet(str(key))
            curr_set << value
            frequences.append(value)
            series.append(curr_set)

            series.setLabelsVisible(True)
            series.labelsPosition()
            self.evaluated_chart.addSeries(series)

        #create axis
        self.axisX = QBarCategoryAxis()
        self.axisX.setLabelsVisible(True)
        self.axisX.append(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.axisX.setTitleText("Voti")

        num_ticks = 4

        self.axisY = QValueAxis()
        self.axisY.setLabelsVisible(True)
        self.axisY.setMin(0)
        self.axisY.setMax(max(frequences))
        self.axisY.setTickCount(num_ticks)
        self.axisY.setLabelFormat("%.0f")
        self.axisY.setTitleText("Frequenze")

        # bild the chart
        self.evaluated_chart.createDefaultAxes()
        self.evaluated_chart.setAxisX(self.axisX)

        self.evaluated_chart.setAxisY(self.axisY)

    def replaceQuestion(self, question: Question, data_array):
        self.cleanup()

        self.id_domanda = question.id
        self.question_label.setText(question.domanda)

        not_evaluated_answers = []
        not_evaluated_answers_count = 0
        evaluated_answers = []
        evaluated_answers_count = 0

        unevaluated_chart_added = False
        evaluated_chart_added = False

        for answer_dict in data_array:
            answer = Answer(
                answer_dict['id'],
                answer_dict['id_domanda'],
                answer_dict['domanda'],
                answer_dict['id_docente'],
                answer_dict['document'],
                answer_dict['id_autore'],
                int(answer_dict['voto_docente']),
                int(answer_dict['voto_predetto']),
                int(answer_dict['voto_predetto_all']),
                answer_dict['commento'],
                answer_dict['source'],
                answer_dict['data_creazione'],
            )

            if answer.id_autore == self.authorized_user['username']:
                self.answer_label.setText(answer.risposta)
            elif answer.voto_docente == -1:
                if not unevaluated_chart_added:
                    # creo l'istogramma con le frequenze di voti predetti a partire da tutte le risposte
                    self.students_answers_not_evaluated_layout.addWidget(self.create_unevaluated_chart())
                    unevaluated_chart_added = True

                studentAnswerPreviewItemWidget = TeacherStudentAnswerPreviewItem(
                    self.threadpool,
                    self.db_worker,
                    self.authorized_user,
                    question,
                    answer,
                    False
                )
                self.students_answers_not_evaluated_layout.addWidget(studentAnswerPreviewItemWidget)
                not_evaluated_answers_count += 1
                not_evaluated_answers.append(answer)
            else:
                if not evaluated_chart_added:
                    # creo l'istogramma con le frequenze di voti assegnati dal docente
                    self.students_answers_evaluated_layout.addWidget(self.create_evaluated_chart())
                    evaluated_chart_added = True

                studentAnswerPreviewItemWidget = TeacherStudentAnswerPreviewItem(
                    self.threadpool,
                    self.db_worker,
                    self.authorized_user,
                    question,
                    answer,
                    True
                )
                self.students_answers_evaluated_layout.addWidget(studentAnswerPreviewItemWidget)
                evaluated_answers_count += 1
                evaluated_answers.append(answer)

        not_evaluated_empty_state_label = QLabel("Non sono presenti risposte in attesa di valutazione")
        not_evaluated_empty_state_label.setObjectName("not_evaluated_empty_state")
        evaluated_empty_state_label = QLabel("Non sono presenti risposte già valutate")
        evaluated_empty_state_label.setObjectName("evaluated_empty_state")

        if not_evaluated_answers_count == 0:
            self.students_answers_not_evaluated_layout.addWidget(not_evaluated_empty_state_label)
        else:
            self.populateUnevaluatedChart(not_evaluated_answers)

        if evaluated_answers_count == 0:
            self.students_answers_evaluated_layout.addWidget(evaluated_empty_state_label)
        else:
            self.populateEvaluatedChart(evaluated_answers)

        if self.isHidden():
            self.show()

    def onRecalulatedVotes(self, votes: list[float]):
        teacherStudentAnswerPreviewItemIndex = 0
        for not_evaluated_item_index in range(self.students_answers_not_evaluated_layout.count()):
            item = self.students_answers_not_evaluated_layout.itemAt(not_evaluated_item_index)
            widget = item.widget()
            if isinstance(widget, TeacherStudentAnswerPreviewItem):
                widget.label_risultato.setText(str(votes[teacherStudentAnswerPreviewItemIndex]))
                # widget.votoCustomSpinBox.setValue(votes[teacherStudentAnswerPreviewItemIndex])
                teacherStudentAnswerPreviewItemIndex += 1

    def onEvaluatedAnswer(self, question: Question, answer: Answer):
        def show_confirm():
            message = 'Voto assegnato correttamente.'
            closeMessageBox = QMessageBox(self)
            closeMessageBox.setWindowTitle('Successo')
            closeMessageBox.setText(message)
            closeMessageBox.setStandardButtons(QMessageBox.Close)
            reply = closeMessageBox.exec()

        show_confirm()

    def changeEvent(self, event):
        if event.type() == QEvent.ApplicationPaletteChange or event.type() == QEvent.PaletteChange:
            self.handlePaletteChange()

    def is_dark_or_light(self, r, g, b):
        brightness = (r + g + b) / 3
        threshold = 127
        # Se la luminosità è inferiore alla soglia, il colore è scuro, altrimenti è chiaro
        return "dark" if brightness < threshold else "light"

    def handlePaletteChange(self):
        # Operazioni da eseguire quando cambia la palette dell'applicazione
        rgb_bg = self.palette().color(QPalette.Window).getRgb()
        current_theme = self.is_dark_or_light(rgb_bg[0], rgb_bg[1], rgb_bg[2])
        print("Palette cambiata", rgb_bg, current_theme)

        try:
            if current_theme == "dark":
                self._chart_view.chart().setTheme(QChart.ChartTheme(2))
                self._chart_view.chart().setBackgroundBrush(QBrush(QColor(225, 225, 225, 25)))
                self._chart_view2.chart().setTheme(QChart.ChartTheme(2))
                self._chart_view2.chart().setBackgroundBrush(QBrush(QColor(225, 225, 225, 25)))
            else:
                self._chart_view.chart().setTheme(QChart.ChartTheme(0))
                self._chart_view.chart().setBackgroundBrush(QBrush(QColor(0, 0, 0, 15)))
                self._chart_view2.chart().setTheme(QChart.ChartTheme(0))
                self._chart_view2.chart().setBackgroundBrush(QBrush(QColor(0, 0, 0, 15)))
        except AttributeError:
            pass

    def cleanup(self):
        # Elimina tutti i widget dal layout tranne l'header della sezione
        while self.students_answers_not_evaluated_layout.count() > 2:
            item = self.students_answers_not_evaluated_layout.takeAt(2)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        while self.students_answers_evaluated_layout.count() > 2:
            item = self.students_answers_evaluated_layout.takeAt(2)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
