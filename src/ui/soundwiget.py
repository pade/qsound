from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtCharts import QChartView, QChart, QLineSeries
from PySide6.QtGui import QPainter
from typing import Optional


class Soundwidget(QWidget):

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        hBox = QHBoxLayout()
        self.chartView = QChartView()
        self.chartView.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chartView.setMinimumWidth(800)
        hBox.addWidget(self.chartView)
        self.setLayout(hBox)

    def setUp(self, serie: QLineSeries):
        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.addSeries(serie)
        self.chart.createDefaultAxes()
        self.chartView.setChart(self.chart)
        self.chartView.setMaximumHeight(200)

    @Slot(list)
    def setSeries(self, points: list):
        serie = QLineSeries()
        for point in points:
            serie.append(point[0], point[1])
        self.setUp(serie)
    
