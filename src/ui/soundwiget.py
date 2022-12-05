from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, Signal, Slot, QPointF, QPoint, QRect, QSize
from PySide6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis
from PySide6.QtGui import QPainter, QPen, QColor, QMouseEvent
from typing import Optional
from cue.audiocue import CueInfo


class ChartView (QChartView):

    changedStart = Signal(float, name='changedStart')
    changedEnd = Signal(float, name='changedEnd')
    unselectedColor = QColor(160, 160, 160)
    unselectedColorWithTransparency = QColor(160, 160, 160, 120)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._playCursor = 0.0
        self._startPos = 0.0
        self._endPos = 0.0
        self._moveInProgress = {'start': False, 'end': False}
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMinimumWidth(800)
        self.setMaximumHeight(200)
        self.setMouseTracking(True)

    def setChart(self, chart: QChart, start: float, end: float) -> None:
        super().setChart(chart)
        self.startPos = start
        self.endPos = end

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        delta = 10.0
        mousePos = event.localPos()
        startPointPos = self.chart().mapToPosition(QPointF(self.startPos, 0.0))
        endPointPos = self.chart().mapToPosition(QPointF(self.endPos, 0.0))
        leftButton = event.buttons() == Qt.MouseButton.LeftButton
        r = self.chart().plotArea()
        if not self._moveInProgress['start']:
            if abs(mousePos.x() - startPointPos.x()) < delta and leftButton:
                self._moveInProgress['start'] = True
        else:
            if leftButton:
                if r.left() <= mousePos.x() < (endPointPos.x() - delta):
                    self.startPos = (self.chart().mapToValue(mousePos)).x()
            else:
                self.changedStart.emit(self.startPos)
                self._moveInProgress['start'] = False

        if not self._moveInProgress['end']:
            if abs(mousePos.x() - endPointPos.x()) < delta and leftButton:
                self._moveInProgress['end'] = True
        else:
            if leftButton:
                if (startPointPos.x() + delta) <= mousePos.x() <= r.right():
                    self.endPos = (self.chart().mapToValue(mousePos)).x()
            else:
                self.changedEnd.emit(self.endPos)
                self._moveInProgress['end'] = False

    @property
    def playCursor(self) -> float:
        return self._playCursor

    @playCursor.setter
    def playCursor(self, value: float) -> None:
        self._playCursor = value
        self.viewport().update()

    @property
    def startPos(self) -> float:
        return self._startPos

    @startPos.setter
    def startPos(self, value: float) -> None:
        self._startPos = value
        self.changedStart.emit(self.startPos)
        self.viewport().update()

    @property
    def endPos(self) -> float:
        return self._endPos

    @endPos.setter
    def endPos(self, value: float) -> None:
        self._endPos = value
        self.viewport().update()

    def drawForeground(self, painter: QPainter, rect):
        painter.save()
        self.drawPlayCursor(painter)
        self.drawStartPos(painter)
        self.drawEndPos(painter)
        painter.restore()

    def drawPlayCursor(self, painter: QPainter):
        if self.playCursor != 0.0:
            pen = QPen(QColor('yellow'))
            pen.setWidth(2)
            painter.setPen(pen)
            p = self.chart().mapToPosition(QPointF(self.playCursor, 0.0))
            r = self.chart().plotArea()
            p1 = QPointF(p.x(), r.top())
            p2 = QPointF(p.x(), r.bottom())
            painter.drawLine(p1, p2)

    def drawStartPos(self, painter: QPainter):
        pen = QPen(self.unselectedColor)
        pen.setWidth(3)
        painter.setPen(pen)
        r = self.chart().plotArea()
        middle = (r.top() + r.bottom()) / 2.0
        startPoint = self.chart().mapToPosition(QPointF(self.startPos, middle))
        painter.fillRect(
            QRect(
                QPoint(r.left(), r.top()),
                QSize(startPoint.x() - r.left(), r.height())
            ),
            self.unselectedColorWithTransparency
        )
        painter.drawEllipse(startPoint, 2.0, 2.0)

    def drawEndPos(self, painter: QPainter):
        pen = QPen(self.unselectedColor)
        pen.setWidth(3)
        painter.setPen(pen)
        r = self.chart().plotArea()
        middle = (r.top() + r.bottom()) / 2.0
        endPoint = self.chart().mapToPosition(QPointF(self.endPos, middle))
        painter.fillRect(
            QRect(
                QPoint(endPoint.x(), r.top()),
                QSize(abs(r.right() - endPoint.x()), r.height())
            ),
            self.unselectedColorWithTransparency
        )
        painter.drawEllipse(endPoint, 2.0, 2.0)


class Soundwidget(QWidget):

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        hBox = QHBoxLayout()
        self.chartView = ChartView()
        hBox.addWidget(self.chartView)
        self.setLayout(hBox)

    def setUp(self, serie: QLineSeries, startPos: float, endPos: float):
        chart = QChart()
        chart.legend().hide()
        chart.addSeries(serie)
        axisX = QValueAxis()
        lastPoint = serie.points()[-1]
        axisX.setRange(0.0, lastPoint.x())
        axisX.setLabelFormat('%.2fs')
        chart.setAxisX(axisX, serie)
        self.chartView.setChart(chart, startPos, endPos)

    @Slot(list)
    def setSeries(self, points: list, startPos: float, endPos: float):
        serie = QLineSeries()
        for point in points:
            serie.append(point[0], point[1])
        self.setUp(serie, startPos, endPos)

    @Slot(CueInfo)
    def setPlayCursor(self, cueInfo: CueInfo) -> None:
        self.chartView.playCursor = cueInfo.elapsed / 1000.0
        
    
