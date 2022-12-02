from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, Signal, Slot, QPointF, QPoint
from PySide6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis
from PySide6.QtGui import QPainter, QPen, QColor, QMouseEvent
from typing import Optional
from cue.audiocue import CueInfo


class ChartView (QChartView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._playCursor = 0.0
        self._startPos = 0.0
        self._endPos = 0.0
        self._moveInProgress = False
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMinimumWidth(800)
        self.setMouseTracking(True)

    def pointsEqual(self, p1: QPointF, p2: QPointF, delta: float) -> bool:
        return abs(p1.x() - p2.x()) <= abs(delta) and abs(p1.y() - p2.y()) <= abs(delta)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        delta = 10.0
        mousePos = QPointF(self.chart().mapToValue(event.localPos()).x(), event.localPos().y())
        startPointPos = QPointF(self.startPos, self.chart().mapToPosition(QPoint(self.startPos, 0.0)).y())
        leftButton = event.buttons() == Qt.MouseButton.LeftButton
        if not self._moveInProgress:
            if self.pointsEqual(mousePos, startPointPos, delta) and leftButton:
                self._moveInProgress = True
        else:
            if leftButton:
                serie = self.chart().series()[0]
                lastPoint = serie.points()[-1]
                if 0.0 <= mousePos.x() <= lastPoint.x():
                    self.startPos = mousePos.x()
            else:
                self._moveInProgress = False

    @property
    def playCursor(self) -> float:
        return self._playCursor

    @playCursor.setter
    def playCursor(self, value: float) -> None:
        self._playCursor = value
        self.viewport().update()

    @property
    def startPos(self) -> QPoint:
        return self._startPos

    @startPos.setter
    def startPos(self, value: QPoint) -> None:
        self._startPos = value
        self.viewport().update()

    def drawForeground(self, painter, rect):
        painter.save()
        penCursor = QPen(QColor('yellow'))
        penCursor.setWidth(2)
        painter.setPen(penCursor)
        p = self.chart().mapToPosition(QPointF(self.playCursor, 0.0))
        r = self.chart().plotArea()
        p1 = QPointF(p.x(), r.top())
        p2 = QPointF(p.x(), r.bottom())
        painter.drawLine(p1, p2)
        penLimit = QPen(QColor('red'))
        penLimit.setWidth(3)
        painter.setPen(penLimit)
        middle = (r.top() + r.bottom()) / 2.0
        startPoint = self.chart().mapToPosition(QPoint(self.startPos, middle))
        painter.drawEllipse(startPoint, 2.0, 2.0)
        penLimit.setWidth(1)
        p1 = QPointF(startPoint.x(), r.top())
        p2 = QPointF(startPoint.x(), r.bottom())
        painter.drawLine(p1, p2)
        painter.restore()


class Soundwidget(QWidget):

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        hBox = QHBoxLayout()
        self.chartView = ChartView()
        hBox.addWidget(self.chartView)
        self.setLayout(hBox)

    def setUp(self, serie: QLineSeries):
        chart = QChart()
        chart.legend().hide()
        chart.addSeries(serie)
        axisX = QValueAxis()
        lastPoint = serie.points()[-1]
        axisX.setRange(0.0, lastPoint.x())
        axisX.setLabelFormat('%.2fs')
        chart.setAxisX(axisX, serie)
        self.chartView.setChart(chart)
        self.chartView.setMaximumHeight(200)

    @Slot(list)
    def setSeries(self, points: list):
        serie = QLineSeries()
        for point in points:
            serie.append(point[0], point[1])
        self.setUp(serie)

    @Slot(CueInfo)
    def setPlayCursor(self, cueInfo: CueInfo) -> None:
        self.chartView.playCursor = cueInfo.elapsed / 1000.0
        
    
