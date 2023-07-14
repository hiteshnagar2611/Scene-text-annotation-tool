from PyQt5 import  QtGui, QtWidgets,QtCore
import os
import json
from tkinter.filedialog import askdirectory
import sys
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from GraphicsRectItem import GraphicsRectItem
from CustomLineEdit import CustomLineEdit

class GraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, image,label_coordinates,coor_data,scroll_layout,parent = None):
        super(GraphicsScene, self).__init__(parent)
        self._start = QtCore.QPointF()
        self._current_rect_item = None
        self.background_image = QPixmap(image)
        self.image = image
        # self.index = 0
        self.setSceneRect(0,0,self.background_image.width(),self.background_image.height())
        self.label_c = label_coordinates
        self.coordinates_data = coor_data
        self.scroll_layout = scroll_layout

    # def mouseDoubleClickEvent(self, event):
    #     if self.itemAt(event.scenePos(), QtGui.QTransform()) is None:
    #         self._current_rect_item = GraphicsRectItem()
    #         self._current_rect_item.setBrush(QtCore.Qt.red)
    #         self._current_rect_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
    #         self.addItem(self._current_rect_item)
    #         self._start = event.scenePos()
    #         r = QtCore.QRectF(self._start, self._start)
    #         self._current_rect_item.setRect(r)
    #         # self.index += 1
    #         # self._current_rect_item.index = (self._start)
         
    #     super(GraphicsScene, self).mouseDoubleClickEvent(event)
    #     self.update()

    def mouseMoveEvent(self, event):
        if self._current_rect_item is not None:
            r = QtCore.QRectF(self._start, event.scenePos()).normalized()
            self._current_rect_item.setRect(r)
            # self._current_rect_item.index = (self._start)
        super(GraphicsScene, self).mouseMoveEvent(event)
        self.update()
    def mouseReleaseEvent(self, event):

        self._current_rect_item = None
        self.add_list()
        for item in self.items():
            if isinstance(item, GraphicsRectItem):
                if item.rect().height()==0 and item.rect().width() == 0:
                    self.removeItem(item)
        rect = None
        self.update()
        for item in self.selectedItems():
            if isinstance(item, QGraphicsRectItem) and item.isSelected():
                data = item.mapToScene(item.rect().topLeft())
                rect = f"Rec:- {data.x(), data.y()}"
                break

        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i).widget()

            if isinstance(item, CustomLineEdit):
                if f"Rec:- {item.index}" == rect:
                    line_edit = item
                    line_edit.focusInEvent(QtGui.QFocusEvent(QtGui.QKeyEvent.FocusIn))
                else:
                    line_edit = item
                    line_edit.focusOutEvent(QtGui.QFocusEvent(QtGui.QKeyEvent.FocusOut))
        super(GraphicsScene, self).mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        # if (event.button() == Qt.RightButton):
        if self.itemAt(event.scenePos(), QtGui.QTransform()) is None:
            self._current_rect_item = GraphicsRectItem()
            self._current_rect_item.setBrush(QtCore.Qt.red)
            self._current_rect_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
            self.addItem(self._current_rect_item)
            self._start = event.scenePos()
            r = QtCore.QRectF(self._start, self._start)
            self._current_rect_item.setRect(r)
        # else:
        self.update()
        return super().mousePressEvent(event)
    def drawBackground(self, painter: QPainter, rect: 'QRectF'):
        # Call the base implementation to draw the default background
        super().drawBackground(painter, rect)
        
        # Draw custom background image
        painter.drawImage(rect, QImage(self.image))
        self.update()

    def keyPressEvent(self, event):
            if event.key() == Qt.Key_Delete:
                data = None
                for item in self.selectedItems():
                    if isinstance(item, GraphicsRectItem):
                        rect = item.mapToScene(item.rect().topLeft())
                        data = f"{rect.x(), rect.y()}"
                        found_in_layout = False
                        for i in range(self.scroll_layout.count()):
                            text = self.scroll_layout.itemAt(i).widget()
                            if isinstance(text, CustomLineEdit):
                                if text.index == data:
                                    found_in_layout = True
                                    break
                        if not found_in_layout:
                            self.removeItem(item)
        
    def add_list(self):
        self.label_c.clear()
        # self.save_coordinates_to_json()
        for i,item in enumerate(self.items()):
            if isinstance(item,GraphicsRectItem):
                rect = item.mapToScene(item.rect().topLeft())
                self.label_c.addItem(f"Rec:- {rect.x(),rect.y()}")
                if self.image in self.coordinates_data:
                    data = {
                        'x': rect.x(),
                        'y': rect.y(),
                        'width': item.rect().width(),
                        'height': item.rect().height()
                    }
                    self.coordinates_data[self.image][i] = data


    