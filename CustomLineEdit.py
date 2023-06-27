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

    def __init__(self, index):
        super().__init__()
        self.index = index

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self.index)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.setStyleSheet("background-color: yellow")
    
    def focusOutEvent(self,event):
        super().focusOutEvent(event)
        self.setStyleSheet("")

