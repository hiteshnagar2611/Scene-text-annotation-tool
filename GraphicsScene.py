from PyQt5 import  QtGui, QtWidgets,QtCore
import os
import json
from tkinter.filedialog import askdirectory
import sys
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QGraphicsSceneMouseEvent
from GraphicsRectItem import GraphicsRectItem
from CustomLineEdit import CustomLineEdit
from shapely.geometry import LineString
class Cube(QGraphicsEllipseItem):
    def __init__(self, x, y, size=10):
        super().__init__(x - size / 2, y - size / 2, size, size)
        self.setBrush(QBrush(QColor(255, 0, 0)))
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)


class CustomPolygonItem(QGraphicsPolygonItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsPolygonItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(100)
        self.polygon = QPolygonF()

        # Size handlers
        self.size_handles = []
        self.size_handle_size = 10
        self.size_handle_pen = QPen(Qt.black)
        self.size_handle_brush = QBrush(Qt.red)

    def addPoint(self, pos):
        self.polygon.append(pos)
        self.setPolygon(self.polygon)
        self.updateSizeHandles()

    def setCoordinates(self,points):
        self.polygon = QPolygonF(points)
        self.setPolygon(self.polygon)

    def hoverEnterEvent(self, event):
        QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        QApplication.restoreOverrideCursor()
        super().hoverLeaveEvent(event)

    def paint(self, painter, option, widget=None):
        # Draw the polygon
        path = QPainterPath()
        path.addPolygon(self.polygon)

        painter.setRenderHint(QPainter.Antialiasing)

        if self.isSelected():
            painter.setBrush(QBrush(QColor(0, 255, 0, 20)))
        else:
            painter.setBrush(QBrush(QColor(255, 0, 0, 20)))

        # Draw the polygon
        painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(path)

        # Draw size handles
        painter.setRenderHint(QPainter.Antialiasing)
        if self.isSelected():
            painter.setBrush(QBrush(QColor(0, 255, 0, 255)))
        else:
            painter.setBrush(QBrush(QColor(255, 0, 0, 255)))
        painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for handle in self.size_handles:
            painter.drawEllipse(handle)

        # Draw the connecting line if the polygon has at least two points
        if len(self.polygon) >= 2:
            line = QLineF(self.polygon.first(), self.polygon.last())
            painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine))
            painter.drawLine(line)

    def shape(self):
        path = super().shape()
        # Check if polygon contains at least two points
        if len(self.polygon) >= 2:
            # Add line segment connecting first and last points
            line = QLineF(self.polygon.first(), self.polygon.last())
            path.moveTo(line.p1())
            path.lineTo(line.p2())
        return path

    def boundingRect(self):
        return self.shape().boundingRect()

    def getCoordinates(self):
        polygon_points = self.polygon.toPolygon()
        coordinates = [tuple([point.x(), point.y()]) for point in polygon_points]
        return coordinates
    
    def updateSizeHandles(self):
        self.prepareGeometryChange()
        self.size_handles = []

        for point in self.polygon:
            handle = QRectF(
                point.x() - self.size_handle_size / 2,
                point.y() - self.size_handle_size / 2,
                self.size_handle_size,
                self.size_handle_size
            )
            self.size_handles.append(handle)




class GraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, image,label_coordinates,coor_data,scroll_layout,rot,parent = None):
        super(GraphicsScene, self).__init__(parent)
        self._start = QtCore.QPointF()
        self._current_rect_item = None
        self.image = image
        self.label_c = label_coordinates
        self.coordinates_data = coor_data
        self.scroll_layout = scroll_layout
        self.rot = rot
        self.cubes = []
        self.currentItem = None
        self.polygons = []
        self.is_painting_activated = False
        self.zoom_factor = 1.0
    def mousePressEvent(self, event):
        if (not self.is_painting_activated and
    not isinstance(self.itemAt(event.scenePos(), QtGui.QTransform()), GraphicsRectItem) and
    not isinstance(self.itemAt(event.scenePos(), QtGui.QTransform()), CustomPolygonItem) and isinstance(self.itemAt(event.scenePos(), QtGui.QTransform()), QGraphicsPixmapItem)) :
            self._current_rect_item = GraphicsRectItem()
            self._current_rect_item.setBrush(QtCore.Qt.red)
            self._current_rect_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
            self.addItem(self._current_rect_item)
            self._start = event.scenePos()
            r = QtCore.QRectF(self._start, self._start)
            self._current_rect_item.setRect(r)
        elif self.is_painting_activated and event.button() == Qt.LeftButton:
            pos = event.scenePos()
            if self.currentItem is None:
                polygon = QPolygonF([pos])
                self.currentItem = CustomPolygonItem()
                self.currentItem.addPoint(pos)
                self.addItem(self.currentItem)
            else:
                self.currentItem.addPoint(pos)

        self.update()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._current_rect_item is not None and isinstance(self.itemAt(event.scenePos(), QtGui.QTransform()), QGraphicsPixmapItem):
            r = QtCore.QRectF(self._start, event.scenePos()).normalized()
            self._current_rect_item.setRect(r)
        super(GraphicsScene, self).mouseMoveEvent(event)
        self.update()
    def mouseReleaseEvent(self, event):

        self._current_rect_item = None
        for item in self.items():
            if isinstance(item, GraphicsRectItem):
                if item.rect().height()==0 and item.rect().width() == 0:
                    self.removeItem(item)
        rect = None
        self.update()
        for item in self.selectedItems():
            if isinstance(item, QGraphicsRectItem) and item.isSelected():
                data1 = item.mapToScene(item.rect().topLeft())
                data2 = item.mapToScene(item.rect().bottomRight())
                rect = f"{int(data1.x())}_{int(data1.y())}_{int(data2.x())}_{int(data2.y())}"
                self.rot.setText(str(int(2*item.rotation())))
                break
            elif isinstance(item,CustomPolygonItem) and item.isSelected():
                cor = item.getCoordinates()
                if len(cor) > 2:
                    key = str(cor)
                    rect = key
                    self.rot.setText(str(int(2*item.rotation())))
                    break
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i).widget()

            if isinstance(item, CustomLineEdit):
                if f"{item.index}" == rect:
                    line_edit = item
                    line_edit.focusInEvent(QtGui.QFocusEvent(QtGui.QKeyEvent.FocusIn))
                elif f"{item.index}" == rect:
                    line_edit = item
                    line_edit.focusInEvent(QtGui.QFocusEvent(QtGui.QKeyEvent.FocusIn))
                else:
                    line_edit = item
                    line_edit.focusOutEvent(QtGui.QFocusEvent(QtGui.QKeyEvent.FocusOut))
        super(GraphicsScene, self).mouseReleaseEvent(event)
    
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.matches(QKeySequence.Undo):
            if self.currentItem:
                self.currentItem.polygon = self.currentItem.polygon[:-1]
                self.currentItem.updateSizeHandles()
