import datetime
import statistics
from PyQt5.QtCore import Qt, QPointF, QDateTime, QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QHBoxLayout, QListWidget, \
    QListWidgetItem, QSplitter
from PyQt5 import QtCore
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis


class StatsDialog(QDialog):
    def __init__(self, parent, votes_ready_event):
        super().__init__(parent=parent)
        self.setWindowTitle("Statistiche")
        self.resize(800, 300)
        self.setModal(True)

        votes_ready_event.connect(lambda votes: self.on_students_votes_ready(votes))

        mainWidget = QSplitter()
        mainWidget.setSizes([300, 500])
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setHandleWidth(2)
        mainWidget.setStyleSheet(
            '''
            QSplitter::handle:horizontal
            {
                background: #CCC;
                height: 1px;
            }
            ''')

        # horizontal_layout = QHBoxLayout()

        self.students_avg_list = QListWidget()
        self.students_avg_list.currentItemChanged.connect(self.changed)
        self.students_avg_list.setStyleSheet("QListWidget { padding: 5px; } QListWidget::item { margin: 5px; }")

        mainWidget.addWidget(self.students_avg_list)

        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_container = QWidget()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_container)

        self.scroll_layout = QHBoxLayout(self.scroll_container)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)

        self.create_chart()

        mainWidget.addWidget(self.scroll_area)

        # self.scroll_vertical_layout = QVBoxLayout()
        # scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        # scroll.setFrameShape(QFrame.NoFrame)
#
        # scroll_widget = QWidget()
#
        # scroll_widget.setLayout(self.scroll_vertical_layout)
        # scroll.setWidget(scroll_widget)
        # # Scroll Area Properties
        # scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # scroll.setWidgetResizable(True)
#
        # lay = QVBoxLayout()
        # lay.setContentsMargins(0, 0, 0, 0)
        # lay.addWidget(scroll)

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)


    def create_chart(self):
        self.chart_container = QWidget()                                          # +++
        lay = QVBoxLayout(self.chart_container)                                   # +++
        lay.setContentsMargins(0, 0, 0, 0)                             # +++

        self.scroll_layout.addWidget(self.chart_container)                        # +++
        self.chart_container.setMinimumWidth(800)

        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)

        lay.addWidget(self._chart_view)

    def convert_datetime(self, datetime_str):
        # Converte la stringa datetime nel formato desiderato
        datetime_obj = QDateTime.fromString(datetime_str, "yyyy-MM-ddTHH:mm:ss.zzzzzz")
        return datetime_obj.toString("dd/MM/yyyy HH:mm")

    def changed(self, item: QListWidgetItem):
        self.chart.removeAllSeries()

        try:
            self.chart.removeAxis(self.date_axis)
            self.chart.removeAxis(self.value_axis)
        except AttributeError:
            print("no axis to remove")
            pass

        if item:
            student_data = item.data(Qt.UserRole)
            print("changed", student_data)
            series = QLineSeries()

            for key, votes_and_dates in student_data.items():
                self.chart.setTitle(key)
                self.chart_container.setMinimumWidth(len(votes_and_dates) * 20)

                for x in votes_and_dates:
                    date = x[1]
                    vote = x[0]
                    series.append(QPointF(datetime.datetime.fromisoformat(date).timestamp() * 1000, vote))

            self.chart.addSeries(series)

            num_ticks = 4

            self.date_axis = QDateTimeAxis()
            self.date_axis.setTickCount(num_ticks)
            self.date_axis.setFormat("dd/MM/yyyy HH:mm")
            self.chart.addAxis(self.date_axis, Qt.AlignBottom)
            series.attachAxis(self.date_axis)

            self.value_axis = QValueAxis()
            self.value_axis.setMin(0.0)
            self.value_axis.setMax(5.0)
            self.chart.addAxis(self.value_axis, Qt.AlignLeft)
            series.attachAxis(self.value_axis)

        else:
            print("reset")

    @QtCore.pyqtSlot()
    def on_students_votes_ready(self, data):
        print("[on_students_votes_ready]", data)

        grouped = {}

        for entry in data:
            key = entry[0]
            vote = entry[1]
            date = entry[2]

            if key not in grouped:
                grouped[key] = []

            grouped[key].append([vote, date])

        # Ordina l'array di valori per data crescente
        for key in grouped:
            grouped[key] = sorted(grouped[key], key=lambda x: x[1])

        res = [{key: votes_and_dates} for key, votes_and_dates in grouped.items()]
        print(res)

        for key, votes_and_dates in grouped.items():
            votes = [x[0] for x in votes_and_dates]
            item = QListWidgetItem()
            widget = QLabel(key + " - Risposte: " + str(len(votes)) + " Media: " + str(round(statistics.mean(votes), 3)))
            item.setData(Qt.UserRole, {key: votes_and_dates})
            item.setSizeHint(QSize(widget.sizeHint().width(), 50))

            self.students_avg_list.addItem(item)
            self.students_avg_list.setItemWidget(item, widget)
            #
            #self.scroll_vertical_layout.addWidget(lbl)

        #self.scroll_vertical_layout.addStretch()
