from PyQt5 import  QtGui, QtWidgets
import os
import json
from tkinter.filedialog import askdirectory
import sys
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
class CustomLineEdit(QLineEdit):

    clicked = pyqtSignal(int)

    def __init__(self,index, scene,scroll_layout):
        super().__init__()
        self.index = index
        self.scene = scene
        self.scroll_layout = scroll_layout
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self.index)
        rect = None
        for item in self.scene.items():
            if isinstance(item, QGraphicsRectItem):
                data = item.mapToScene(item.rect().topLeft())
                rect = f"{data.x(), data.y()}"
                if rect  == self.index:
                    item.setSelected(True)
                else:
                    item.setSelected(False)
            if isinstance(item,QGraphicsPolygonItem):
                coord = item.getCoordinates()
                print(f"{coord[0]}_{coord[1]}" , self.index)
                if f"{coord[0]}_{coord[1]}" == self.index:
                    item.setSelected(True)
                else:
                    item.setSelected(False)
    def focusInEvent(self, event):
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i).widget()
            if isinstance(item, CustomLineEdit):
                    line_edit = item
                    line_edit.focusOutEvent(QtGui.QFocusEvent(QtGui.QKeyEvent.FocusOut))
        super().focusInEvent(event)
        self.setStyleSheet("background-color: yellow")
    
    def focusOutEvent(self,event):
        super().focusOutEvent(event)
        self.setStyleSheet("")

