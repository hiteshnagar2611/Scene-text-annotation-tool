# Importing necessary modules or classes may be required
from PyQt5 import QtWidgets,QtGui,QtCore
import os
import json
import glob
from tkinter.filedialog import askdirectory
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from GraphicsScene import GraphicsScene,CustomPolygonItem
from GraphicsScene import GraphicsScene,CustomPolygonItem
from GraphicsRectItem import GraphicsRectItem
from CustomLineEdit import CustomLineEdit
import shutil
from PIL import Image, ImageDraw
from shapely.geometry import Polygon
import traceback
import math


class AnimatedButton1(QPushButton):
    def __init__(self, parent=None):
        super(AnimatedButton1, self).__init__(parent)
        self.defaultText = "Save"
        self.savedText = "Saved"
        self.animationDuration = 200  # Duration in milliseconds
        self.clicked.connect(self.animateSave)

        # Move the connections to the __init__ method
        # self.clicked.connect(self.save_coordinates_to_json)
        # self.clicked.connect(self.save_image_inside_rectangle)

    def animateSave(self):
        self.setText(self.savedText)
        self.setStyleSheet("background-color: green")
        self.setEnabled(False)
        QTimer.singleShot(self.animationDuration, self.revertSave)

    def revertSave(self):
        self.setText(self.defaultText)
        self.setStyleSheet("")
        self.setEnabled(True)

class AnimatedButton2(QPushButton):
    def __init__(self, parent=None):
        super(AnimatedButton2, self).__init__(parent)
        self.defaultText = "Delete"
        self.deletedText = "Deleted"
        self.animationDuration = 200  # Duration in milliseconds
        self.clicked.connect(self.animateDelete)

    def animateDelete(self):
        self.setText(self.deletedText)
        self.setStyleSheet("background-color: red")
        self.setEnabled(False)
        QTimer.singleShot(self.animationDuration, self.revertDelete)

    def revertDelete(self):
        self.setText(self.defaultText)
        self.setStyleSheet("")
        self.setEnabled(True)



class MainWindow(QWidget):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.current_image_index = 0
        self.selected_index = 0
        self.image_paths = []
        self.drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.coordinates_data = {}
        self.num_rec = 0
        self.text_data = {}
        self.message_box = QMessageBox()
        self.image_path = ""
        self.model_activate = False
        self.coordinates_lodaded = False


        self.button_prev = QPushButton("Previous")
        self.button_prev.clicked.connect(self.button_click_prev)
        self.button_prev.setFixedSize(self.size().width()//4,self.size().height()//13)
          
        self.button_next = QPushButton("Next")
        self.button_next.clicked.connect(self.button_click_next)
        self.button_next.setFixedSize(self.size().width()//4,self.size().height()//13)

        self.button_save = AnimatedButton1("Save")
        self.button_save.clicked.connect(self.save_coordinates_to_json)
        self.button_save.setFixedSize(self.size().width()//4,self.size().height()//13)

        self.button_zoomIn = QPushButton("Zoom +")
        self.button_zoomOut = QPushButton("Zoom -")

        self.button_zoomIn.clicked.connect(self.zoomIn)
        self.button_zoomOut.clicked.connect(self.zoomOut)
    
        self.increase_rot = QPushButton('R+')
        self.decrease_rot = QPushButton('R-')
        self.increase_rot.clicked.connect(lambda: self.rotate_selected_item_r(5))
        self.decrease_rot.clicked.connect(lambda: self.rotate_selected_item_r(-5))
        self.increase_rot.setFixedSize(45,35)
        self.decrease_rot.setFixedSize(45,35)

        self.rotation_value = QLineEdit()
        self.rotation_value.setText("0")
        self.rotation_value.setValidator(QIntValidator(-360, 360, self))
        self.rotation_value.setFixedSize(45,35)
        self.rotation_value.setAlignment(Qt.AlignCenter)
        self.rotation_value.returnPressed.connect(lambda: self.rotate_selected_item_r(0))

        self.button_delete = AnimatedButton2("Delete")
        self.button_delete.clicked.connect(self.handleDelete)
        self.button_delete.setFixedSize(self.size().width()//4,self.size().height()//13)

        self.activate_button = QPushButton("Draw Polygon")
        self.activate_button.setCheckable(True)
        self.activate_button.setChecked(False)
        self.activate_button.toggled.connect(self.toggle_painting)
        self.activate_button.setFixedSize(self.size().width()//4,self.size().height()//13)


        self.ask_folder = QPushButton("Choose Folder")
        self.ask_folder.clicked.connect(self.min_run)
        self.ask_folder.setFixedSize(self.size().width()//4,self.size().height()//13)

        self.button_reset = QPushButton("Reset")
        self.button_reset.setFixedSize(self.size().width()//4,self.size().height()//13)
        self.button_ai_modale_load = QPushButton("Model_load")
        self.button_ai_modale_load.setFixedSize(self.size().width()//4,self.size().height()//13)
        self.button_ai_modale_load.setStyleSheet("background-color : red")
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(-360)
        self.slider.setMaximum(360)
        self.slider.setValue(0)
        self.slider.setTickInterval(5)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(lambda: self.rotate_selected_item_r(1))

        self.label_coordinates = QListWidget()
        
        self.scrollable = QScrollArea()
        self.scrollable.setWidgetResizable(True)
        self.scroll_widget = QWidget(self.scrollable)
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        
        hbox  = QHBoxLayout()
        hbox.addWidget(self.button_prev)
        hbox.addWidget(self.button_next)
        hbox.addWidget(self.button_save)
        hbox.addWidget(self.button_delete)  
        hbox.addWidget(self.button_reset)
        hbox.addWidget(self.button_ai_modale_load)
        hbox.addWidget(self.button_zoomIn)
        hbox.addWidget(self.button_zoomOut)
        hbox.setAlignment(Qt.AlignCenter)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.decrease_rot)
        hbox2.addWidget(self.rotation_value)
        hbox2.addWidget(self.increase_rot)
        hbox2.addWidget(self.activate_button)
        hbox2.addWidget(self.ask_folder)
        hbox2.setAlignment(Qt.AlignCenter)
        

        self.scene = GraphicsScene('',self.label_coordinates,self.coordinates_data,self.scroll_layout,self.rotation_value,self)
        self.pixmap = QPixmap()
        self.view = QGraphicsView(self.scene)
        self.scene.setSceneRect(0, 0,self.pixmap.width() , self.pixmap.height())
        self.view.setScene(self.scene)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

        self.view_box = QVBoxLayout()
        self.view_box.addWidget(self.view)
        self.view_box.setAlignment(Qt.AlignCenter)
        
        self.scrollable.setWidget(self.scroll_widget)
        self.scrollable.setFixedWidth(250)
        
        self.box = QHBoxLayout()
        self.box.addWidget(self.scrollable)
        self.box.addLayout(self.view_box)
        self.box.setAlignment(Qt.AlignRight)
        
        vbox2 = QVBoxLayout()
        vbox2.addLayout(self.box)
        vbox2.addLayout(hbox) 
        vbox2.addLayout(hbox2)
        vbox2.addWidget(self.slider)  
        
        self.setLayout(vbox2)
        
        self.label_coordinates.clicked.connect(self.select_rectangle)
        self.button_reset.clicked.connect(self.reset_image)
        self.button_delete.clicked.connect(self.delete_rectangle)
        self.button_ai_modale_load.clicked.connect(self.call_modale)
        
        self.deleteShortcut = QShortcut(QKeySequence.Delete, self)
        self.deleteShortcut.activated.connect(self.delete_rectangle)
        self.saveShortcut = QShortcut(QKeySequence.Save,self)
        self.saveShortcut.activated.connect(self.save_coordinates_to_json)


    def toggle_painting(self, checked):
        self.scene.is_painting_activated = checked
        if checked:
            self.activate_button.setText("End Polygon")
        else:
            self.activate_button.setText("Draw Polygon")
            self.scene.currentItem = None

    def showMessageBox(self, title, text):
        message_box = QMessageBox(self)
        message_box.setWindowTitle(title)
        message_box.setText(text)
        message_box.show()

        # Automatically close the message box after 3 seconds (adjust the duration as needed)
        close_timer = QTimer(self)
        close_timer.setSingleShot(True)
        close_timer.timeout.connect(message_box.close)
        close_timer.start(3000)

    def hasExistingRectangles(self):
        image_path = self.image_paths[self.current_image_index]
        if image_path in self.coordinates_data:
            return len(self.coordinates_data[image_path]) > 0
        return True

    def hasNewRectangles(self):
        image_path = self.image_paths[self.current_image_index]
        if image_path in self.coordinates_data:
            saved_rectangles = len(self.coordinates_data[image_path])
            new_rectangles = len([item for item in self.scene.items() if isinstance(item, QGraphicsItem)])
            if saved_rectangles == 0 and new_rectangles > 0:
                return True
            return new_rectangles > saved_rectangles
        return True
            
    def handleDelete(self):
        if len(self.scene.items()) == 0:
            # No bounding boxes present
            print("....")
            #QMessageBox.warning(self, "No Bounding Box", "There are no bounding boxes to delete.")
        else:
            # Bounding boxes are present, perform the delete functionality here
            print("Deleting data...")
        
    def load_images_from_folder(self, folder):
        self.image_paths = []
        for filename in os.listdir(folder):
            if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
                self.image_paths.append(os.path.join(folder, filename))
        if self.image_paths:
            self.load_last_image_path()  # Load the last image path if available
            if self.current_image_index >= len(self.image_paths):
                self.current_image_index = 0
        self.load_image()

    def zoomIn(self):
        try:
            current_scale = self.view.transform().m11() # Get the current horizontal scale factor
            new_scale = min(current_scale * 1.2, 1.5)  # Calculate the new scale factor with a limit
            self.view.setTransform(QTransform().scale(new_scale, new_scale))  # Apply the new scale
        except Exception as e:
            print("Error while zooming in:", e)

    def zoomOut(self):
        try:
            current_scale = self.view.transform().m11()  # Get the current horizontal scale factor
            new_scale = max(current_scale * 0.8, 0.5)  # Calculate the new scale factor with a limit
            self.view.setTransform(QTransform().scale(new_scale, new_scale))  # Apply the new scale
        except Exception as e:
            print("Error while zooming out:", e)

    def load_image(self):
        self.load_coordinates_from_json()
        self.scene.clear()
        if self.image_paths:
            self.scene.clear()
            image_path = self.image_paths[self.current_image_index]
            self.pixmap = QPixmap(image_path)
            self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height()) 
            self.background_image_item = QGraphicsPixmapItem(self.pixmap)
            self.scene.addItem(self.background_image_item)
                
            for item in self.scene.items():
                if isinstance(item, GraphicsRectItem):
                    self.scene.removeItem(item)
                elif isinstance(item,CustomPolygonItem):
                    self.scene.removeItem(item)
            
            while self.scroll_layout.count():
                item = self.scroll_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            if self.coordinates_data != {}:
                if image_path in self.coordinates_data:
                    self.text_data[image_path] = {}
                    for key in self.coordinates_data[image_path]:
                        data = self.coordinates_data[image_path][key]
                        if key[0] == "[" and key[-1] == "]":
                            item = CustomPolygonItem()
                            for point in data['coordinates']:
                                item.addPoint(QPointF(point[0],point[1]))
                            self.scene.addItem(item)
                            t = CustomLineEdit(key,self.scene,self.scroll_layout)
                            self.text_data[image_path][t.index] = t
                            if 'text' in data:
                                t.setText(data['text'])
                            t.setCursorPosition(0)
                            self.scroll_layout.addWidget(t)
                        else:   
                            if 'width' not in data or 'height' not in data:
                                x1 = data['x1']
                                x2 = data['x2']
                                x3 = data['x3']
                                x4 = data['x4']
                                y1 = data['y1']
                                y2 = data['y2']
                                y3 = data['y3']
                                y4 = data['y4']
                                width = math.sqrt((x4 - x1)**2 + (y4 - y1)**2)**0.5
                                height = math.sqrt((x2 - x3)**2 + (y2 - y3)**2)**0.5
                                item = GraphicsRectItem(QRectF(QPointF(0,0),QSizeF(width,height)))
                            else:
                                item = GraphicsRectItem(QRectF(QPointF(0,0),QSizeF(data['width'],data['height'])))
                            item.moveBy(data['x1'], data['y1'])
                            if 'rotation' in data:
                                item.setRotation(data['rotation'])
                            self.scene.addItem(item)
                            t = CustomLineEdit(key,self.scene,self.scroll_layout)
                            self.text_data[image_path][t.index] = t
                            if 'text' in data:
                                t.setText(data['text'])
                            t.setCursorPosition(0)
                            self.scroll_layout.addWidget(t)
                    self.scrollable.setWidget(self.scroll_widget)
                self.box.addWidget(self.scrollable)
            self.save_last_image_path()

    def save_coordinates_to_json(self):
        if self.image_paths and len(self.scene.items()) != 0:

            image_path = self.image_paths[self.current_image_index]
            self.coordinates_data[image_path] = {}
            original_coordinates = {}
            original_coordinates[image_path] = {}
            self.toggle_painting(False)
            scene_height = 0
            scene_width = 0
            image_height = 0
            image_width = 0
            with Image.open(image_path) as img:
                original_image_size = img.size
                if original_image_size is not None:
                    scene_width = self.scene.width()
                    scene_height = self.scene.height()
                    image_width, image_height = original_image_size
            for item in self.scene.items():
                if isinstance(item, GraphicsRectItem):
                    rect1 = item.mapToScene(item.rect().topLeft())
                    rect3 = item.mapToScene(item.rect().bottomRight())
                    key = f"{int(rect1.x())}_{int(rect1.y())}_{int(rect3.x())}_{int(rect3.y())}"
                    data = {
                        'x1': rect1.x(),
                        'y1': rect1.y(),
                        'x2': rect3.x(),
                        'y2': rect3.y(),
                        'height' : item.rect().height(),
                        'width' : item.rect().width(),
                        'rotation': item.rotation(),
                        'text': f"{int(rect1.x()), int(rect1.y())}"
                    }
                    self.coordinates_data[image_path][key] = data

                    rect2 = item.mapToScene(item.rect().topRight())
                    rect4 = item.mapFromScene(item.rect().bottomLeft())

                    x1_image = int((rect1.x() / scene_width) * image_width)
                    y1_image = int((rect1.y() / scene_height) * image_height)
                    x2_image = int((rect2.x() / scene_width) * image_width)
                    y2_image = int((rect2.y() / scene_height) * image_height)
                    x3_image = int((rect3.x() / scene_width) * image_width)
                    y3_image = int((rect3.y() / scene_height) * image_height)
                    x4_image = int((rect4.x() / scene_width) * image_width)
                    y4_image = int((rect4.y() / scene_height) * image_height)
                    temp_key = f"{x1_image}{y1_image}{x3_image}{y3_image}"
                    original_coordinates[image_path][temp_key] = {
                        'x1' : x1_image,
                        'y1' : y1_image,
                        'x2' : x2_image,
                        'y2' : y2_image,
                        'x3' : x3_image,
                        'y3' : y3_image,
                        'x4' : x4_image,
                        'y4' : y4_image,
                    }
                

                elif isinstance(item,CustomPolygonItem):
                    coord = item.getCoordinates()
                    key = str(coord)
                    data = {
                        'coordinates': coord,
                        'text': f"{coord[1]}_{coord[2]}"
                    }
                    self.coordinates_data[image_path][key] = data

                    coord_image = []
                    for c in coord:
                        x1 = c[0]
                        y1 = c[1]
                        x1 = int((x1/scene_width)*image_width)
                        y1 = int((y1/scene_height)*image_height)
                        coord_image.append([x1,y1])
                    temp_key = str(coord_image)
                    original_coordinates[image_path][temp_key] = {
                        'coordinates': coord_image
                    }

            for i in range(self.scroll_layout.count()):
                item = self.scroll_layout.itemAt(i)
                wid = item.widget()
                if isinstance(wid,CustomLineEdit):
                    text = wid.text()
                    self.text_data[image_path][wid.index].setText(text)
            if image_path in self.text_data:
                for key, value in self.coordinates_data[image_path].items():
                    if key in self.text_data[image_path]:
                        value["text"] = self.text_data[image_path][key].text()
            if not self.coordinates_data:
                print("No coordinates to save.")
                return

            image_name = os.path.splitext(os.path.basename(image_path))[0]
            coordinates_folder = os.path.join(self.folder_path, "coordinates")
            os.makedirs(coordinates_folder, exist_ok=True)

            
            original_coordinates_folder = os.path.join(self.folder_path,"original_coordinates")
            os.makedirs(original_coordinates_folder, exist_ok=True)

            json_file = os.path.join(coordinates_folder, f"{image_name}_coordinates.json")
            with open(json_file, "w") as f:
                json.dump(self.coordinates_data[image_path], f, indent=4)

            json_file2 = os.path.join(original_coordinates_folder, f"{image_name}_original_coordinates.json")
            with open(json_file2, "w") as f:
                json.dump(original_coordinates[image_path], f, indent=4)

            print("Saved Coordinates")

            self.load_image()
            self.scene.update()
        
        else:
            self.showMessageBox("No Coordinates to Save", "There are no rectangles or polygons to save.") 

    def delete_rectangle(self):
        if len(self.scene.selectedItems()) == 0:
            return 
        try:
            if len(self.scene.items()) == 0:
                # No bounding boxes present
                message_box = QMessageBox(self)
                message_box.setWindowTitle("No Bounding Box")
                message_box.setText("There are no bounding boxes to delete.")
                message_box.show()

            # Automatically close the message box after 3 seconds (adjust the duration as needed)
                close_timer = QTimer(self)
                close_timer.setSingleShot(True)
                close_timer.timeout.connect(message_box.close)
                close_timer.start(3000)

            else:
                scene_height = 0
                scene_width = 0
                image_height = 0
                image_width = 0
                image_path = self.image_paths[self.current_image_index]
                with Image.open(image_path) as img:
                    original_image_size = img.size
                    if original_image_size is not None:
                        scene_width = self.scene.width()
                        scene_height = self.scene.height()
                        image_width, image_height = original_image_size
                selected_item_r = None
                selected_item_p = None
                for item in self.scene.items():
                    if isinstance(item, GraphicsRectItem) and item.isSelected():
                        selected_item_r = item
                        break
                    elif isinstance(item,CustomPolygonItem) and item.isSelected():
                        selected_item_p = item
                        break

                if selected_item_r:
                    rect = selected_item_r.mapToScene(selected_item_r.rect().topLeft())
                    rect2 = selected_item_r.mapToScene(selected_item_r.rect().bottomRight())
                    data = f"{int(rect.x())}_{int(rect.y())}_{int(rect2.x())}_{int(rect2.y())}"
                    self.scene.removeItem(selected_item_r)

                    image_path = self.image_paths[self.current_image_index]
                    if image_path in self.coordinates_data:
                        d = self.coordinates_data[image_path]
                        for key, value in list(d.items()):
                            if key[0] != "[":
                                if key == data:
                                    key_to_delete = data
                                    if key_to_delete in self.text_data[image_path]:
                                        del self.text_data[image_path][key_to_delete]
                                    del self.coordinates_data[image_path][key]
                                    print("deleted rectangle")
                                    break
                    

                    # Delete the corresponding JSON file and image file
                    image_name = os.path.splitext(os.path.basename(image_path))[0]
                    coordinates_folder = os.path.join(self.folder_path,"coordinates")
                    json_file1 = os.path.join(coordinates_folder, f"{image_name}_coordinates.json")

                    if os.path.exists(json_file1):
                        with open(json_file1, 'r') as f:
                            data = json.load(f)
                        
                        for key, value in list(data.items()):
                            if key[0] != "[":
                                if (
                                    value['x1'] == rect.x()
                                    and value['y1'] == rect.y()
                                    and value['x2'] == rect2.x()
                                    and value['y2'] == rect2.y()
                                ):
                                    del data[key]
                                    break
                        
                        with open(json_file1, 'w') as f:
                            json.dump(data, f, indent=4)
                            print(f"JSON file updated: {json_file1}")
                    

                    x1_image = int((rect.x() / scene_width) * image_width)
                    y1_image = int((rect.y() / scene_height) * image_height)
                    x3_image = int((rect2.x() / scene_width) * image_width)
                    y3_image = int((rect2.y() / scene_height) * image_height)

                    original_coordinates_folder = os.path.join(self.folder_path, "original_coordinates")
                    json_file2 = os.path.join(original_coordinates_folder, f"{image_name}_original_coordinates.json")
                    if os.path.exists(json_file2):
                        with open(json_file2, 'r') as f:
                            data2 = json.load(f)
                        for key, value in list(data2.items()):
                            if key == f"{x1_image}{y1_image}{x3_image}{y3_image}":
                                del data2[key]
                                break
                        
                        with open(json_file2, 'w') as f:
                            json.dump(data2, f, indent=4)
                            print(f"JSON file updated: {json_file2}")

                    print("Item removed successfully.")

                elif selected_item_p:
                    image_path = self.image_paths[self.current_image_index]
                    key = str(selected_item_p.getCoordinates())
                    self.scene.removeItem(selected_item_p)
                    if key in self.coordinates_data[image_path]:
                        temp_data = self.coordinates_data[image_path][key]
                        del self.coordinates_data[image_path][key]
                        image_name = os.path.splitext(os.path.basename(image_path))[0]
                        coordinates_folder = os.path.join(self.folder_path, "coordinates")
                        json_file1 = os.path.join(coordinates_folder, f"{image_name}_coordinates.json")
                        if os.path.exists(json_file1):
                            with open(json_file1, 'r') as f:
                                data = json.load(f)
                            
                            for temp_key, value in list(data.items()):
                                if (temp_key == key):
                                    if value['coordinates'] == temp_data['coordinates']:
                                        del data[key]
                                        break
                            
                            with open(json_file1, 'w') as f:
                                json.dump(data, f, indent=4)
                                print(f"JSON file updated: {json_file1}")
                        
                        coord = selected_item_p.getCoordinates()
                        coord_image = []
                        for c in coord:
                            x1 = c[0]
                            y1 = c[1]
                            x1 = int((x1/scene_width)*image_width)
                            y1 = int((y1/scene_height)*image_height)
                            coord_image.append([x1,y1])
                        temp_key = str(coord_image)
                        original_coordinates_folder = os.path.join(os.path.dirname(image_path), "original_coordinates", image_name)
                        json_file2 = os.path.join(original_coordinates_folder, f"{image_name}_original_coordinates.json")
                        if os.path.exists(json_file2):
                            with open(json_file2, 'r') as f:
                                data2 = json.load(f)
                            for key, value in list(data2.items()):
                                if key == temp_key:
                                    del data2[key]
                                    break
                            
                            with open(json_file2, 'w') as f:
                                json.dump(data2, f, indent=4)
                                print(f"JSON file updated: {json_file2}")

                        print("Item removed successfully.")


                else:
                    message_box = QMessageBox(self)
                    message_box.setWindowTitle("No Selection")
                    message_box.setText("Please select a bounding box to delete.")
                    message_box.show()

            # Automatically close the message box after 3 seconds (adjust the duration as needed)
                    close_timer = QTimer(self)
                    close_timer.setSingleShot(True)
                    close_timer.timeout.connect(message_box.close)
                    close_timer.start(3000)
                    
                        

        except Exception as e:
        # Handle the exception here (e.g., log the error or show an error message to the user).
            print(f"An error occurred: {e}")
            traceback.print_exc() 

        while self.scroll_layout.count():
                item = self.scroll_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        if self.coordinates_data != {}:
            if image_path in self.coordinates_data:
                self.text_data[image_path] = {}
                for key in self.coordinates_data[image_path]:
                    data = self.coordinates_data[image_path][key]
                    if key[0] == "[" and key[-1] == "]":
                        t = CustomLineEdit(key,self.scene,self.scroll_layout)
                        self.text_data[image_path][t.index] = t
                        t.setText(data['text'])
                        t.setCursorPosition(0)
                        self.scroll_layout.addWidget(t)
                    else:   
                        t = CustomLineEdit(key,self.scene,self.scroll_layout)
                        self.text_data[image_path][t.index] = t
                        t.setText(data['text'])
                        t.setCursorPosition(0)
                        self.scroll_layout.addWidget(t)
                self.scrollable.setWidget(self.scroll_widget)
            self.box.addWidget(self.scrollable)
        self.selected_index = -1

    def load_coordinates_from_json(self):
        if(self.model_activate == False):
            self.coordinates_data = {}
            image_path = self.image_paths[self.current_image_index]
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            coordinates_folder = os.path.join(self.folder_path,"coordinates")
            if os.path.exists(coordinates_folder) and os.path.isdir(coordinates_folder):
                if os.path.exists(coordinates_folder) and os.path.isdir(coordinates_folder):
                    json_file = os.path.join(coordinates_folder, f"{image_name}_coordinates.json")
                    if os.path.exists(json_file):
                        with open(json_file, "r") as f:
                            self.coordinates_data[image_path] = json.load(f)
                else:
                    print(f"1. Coordinates folder not found for image: {image_name}")
            else:
                print(f"2. Coordinates folder not found for image: {image_name}")
        if(self.model_activate and self.coordinates_lodaded == False):
            self.load_model_coordinates()
            self.coordinates_lodaded = True
            image_path = self.image_paths[self.current_image_index]
            if(image_path in self.model_coord_copy):
                # print(self.coordinates_data[image_path])
                if(image_path not in self.coordinates_data):
                    self.coordinates_data[image_path] = {}
                self.coordinates_data[image_path].update(self.model_coord_[image_path])
            print(self.coordinates_data)
        elif(self.model_activate and self.coordinates_lodaded == True):
            self.coordinates_data = {}
            image_path = self.image_paths[self.current_image_index]
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            coordinates_folder = os.path.join(self.folder_path,"coordinates")
            if os.path.exists(coordinates_folder) and os.path.isdir(coordinates_folder):
                if os.path.exists(coordinates_folder) and os.path.isdir(coordinates_folder):
                    json_file = os.path.join(coordinates_folder, f"{image_name}_coordinates.json")
                    if os.path.exists(json_file):
                        with open(json_file, "r") as f:
                            self.coordinates_data[image_path] = json.load(f)
                else:
                    print(f"1. Coordinates folder not found for image: {image_name}")
            else:
                print(f"2. Coordinates folder not found for image: {image_name}")

    def button_click_prev(self):
        if self.scene.items():
            image_path = self.image_paths[self.current_image_index]
            if image_path in self.coordinates_data:
                saved_rectangles = len(self.coordinates_data[image_path])
                unsaved_rectangles = len(self.scene.items())
                if unsaved_rectangles - 1 > saved_rectangles:
                    reply = QMessageBox.question(self, "Unsaved Changes",
                                                 f"There are {unsaved_rectangles - saved_rectangles - 1} unsaved rectangles on the current image.\n"
                                                 f"Do you want to save the changes before moving to the previous image?",
                                                 QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                    if reply == QMessageBox.Yes:
                        self.handleSave()  # Save the changes
                    elif reply == QMessageBox.Cancel:
                        return  # Cancel the action, do not move to the previous image

        self.current_image_index -= 1
        if self.current_image_index < 0:
            self.current_image_index = len(self.image_paths) - 1
        self.load_image()
        self.update()
        #self.handleSave()
    
    def button_click_next(self):
        if self.scene.items():
            image_path = self.image_paths[self.current_image_index]
            if image_path in self.coordinates_data:
                saved_rectangles = len(self.coordinates_data[image_path])
                unsaved_rectangles = len(self.scene.items())
                if unsaved_rectangles - 1 > saved_rectangles:
                    reply = QMessageBox.question(self, "Unsaved Changes",
                                                f"There are {unsaved_rectangles - saved_rectangles - 1} unsaved rectangles or polygons on the current image.\n"
                                                "Do you want to save the changes before moving to the next image?",
                                                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                    if reply == QMessageBox.Yes:
                        self.save_coordinates_to_json()  # Save the changes
                    elif reply == QMessageBox.Cancel:
                        return  # Cancel the action, do not move to the next image

        self.current_image_index += 1
        if self.current_image_index >= len(self.image_paths):
            self.current_image_index = 0
        self.load_image()
        self.update()
    
    def select_rectangle(self):
        self.selected_index = self.label_coordinates.currentItem()
        rec = self.label_coordinates.currentItem().text()

        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i).widget()

            if isinstance(item, CustomLineEdit):
                if f"{item.index}" == rec:
                    line_edit = item
                    line_edit.focusInEvent(QFocusEvent(QKeyEvent.FocusIn))
                else:
                    line_edit = item
                    line_edit.focusOutEvent(QFocusEvent(QKeyEvent.FocusOut))
            else:
                line_edit = item
                line_edit.focusOutEvent(QFocusEvent(QKeyEvent.FocusOut))

        for item in self.scene.items():
            if isinstance(item, GraphicsRectItem):
                rect = item.mapToScene(item.rect().topLeft())
                key = f"{rect.x()}_{rect.y()}_{item.rect().width()}_{item.rect().height()}"
                if key == rec:
                    item.setSelected(True)
                else:
                    item.setSelected(False)
    
    def reset_image(self):
        if self.image_paths and self.model_activate == False:
            image_path = self.image_paths[self.current_image_index]
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            coordinates_folder = os.path.join(self.folder_path, "coordinates")
            original_coordinates_folder = os.path.join(self.folder_path, "original_coordinates")

            # Delete JSON file for the current image
            json_file = os.path.join(coordinates_folder, f"{image_name}_coordinates.json")
            if os.path.exists(json_file):
                os.remove(json_file)
                print(f"JSON file removed successfully: {json_file}")
            else:
                print(f"JSON file does not exist: {json_file}")
            
            original_json = os.path.join(original_coordinates_folder,f"{image_name}_original_coordinates.json")

            if os.path.exists(original_json):
                os.remove(original_json)
                print("removed")
            else:
                print(f"{original_json}")
            # Remove the current image from coordinates_data
            if image_path in self.coordinates_data:
                del self.coordinates_data[image_path]

            self.load_image()
        elif self.model_activate:
            self.coordinates_data[self.image_paths[self.current_image_index]] = {}
            self.load_image()
        self.repaint()

    def call_modale(self):
        if self.model_activate == False:
            self.model_folder_path = askdirectory(title="Select Folder with coordinates")
            if self.model_folder_path:
                self.model_activate = True
                self.button_ai_modale_load.setStyleSheet("background-color : green")
                self.load_model_coordinates()
            self.load_image()
        else:
            self.model_activate = False
            self.button_ai_modale_load.setStyleSheet("background-color : red")

    def load_model_coordinates(self):
        self.model_coord = {}
        image_path = self.image_paths[self.current_image_index]
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        if os.path.exists(self.model_folder_path) and os.path.isdir(self.model_folder_path):
            if os.path.exists(self.model_folder_path) and os.path.isdir(self.model_folder_path):
                json_file = os.path.join(self.model_folder_path, f"{image_name}_coordinates.json")
                if json_file.endswith(".json"):
                    file = os.path.join(self.model_folder_path,json_file)
                    if(os.path.exists(file)):
                        with open(file, "r") as f:
                            self.model_coord[image_path] = json.load(f)
            else:
                print(f"1. Coordinates folder not found for image: {image_name}")
        else:
            print(f"2. Coordinates folder not found for image: {image_name}")
        self.model_coord_copy = self.model_coord.copy()
    
    def save_last_image_path(self):
        if self.current_image_index < len(self.image_paths):
            data = {'last_image_path': self.image_paths[self.current_image_index]}
            with open('last_image.json', 'w') as f:
                json.dump(data, f)

    def load_last_image_path(self):
        if os.path.exists('last_image.json'):
            with open('last_image.json', 'r') as f:
                data = json.load(f)
                last_image_path = data.get('last_image_path')
                if last_image_path and last_image_path in self.image_paths:
                    self.current_image_index = self.image_paths.index(last_image_path)

    def rotate_selected_item_r(self,value):
        for item in self.scene.items():
            if isinstance(item, GraphicsRectItem) and item.isSelected():
                point = item.rect().topLeft()
                value += int(self.rotation_value.text())
                # item.setTransformOriginPoint(point)

                value = (value)%360
                item.setRotation(value/2)
                self.rotation_value.setText(str(int(value)))
                # if(value >= 360 or value <= -360):
                #    self.rotation_value.setText(str((int(value)%360 + 360)%360)) 
                break
        self.update()
    
    def run(self):
        try:
            splash_pix = QPixmap("Scene-text-annotation-tool - Copy\sample.png") 
            max_splash_size = QtCore.QSize(300, 300)
            splash_pix = splash_pix.scaled(max_splash_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
            desktop = QtWidgets.QApplication.desktop()
            screen_rect = desktop.availableGeometry(desktop.primaryScreen())
            splash.move(screen_rect.center() - splash.rect().center())
            #splash.setFixedSize(splash_pix.size())
            splash.setMask(splash_pix.mask())
        except Exception as e:
            print("Error loading image:", e) 
        splash.showMessage("Loading...", Qt.AlignBottom | Qt.AlignCenter, QtGui.QColor(Qt.black))
        splash.show()
        app.processEvents()

        # Check if folder_path.txt exists and read the folder path from it
        if os.path.exists("folder_path.txt"):
            with open("folder_path.txt", "r") as file:
                self.folder_path = file.read().strip()
        else:
            self.folder_path = None

        # If folder_path is empty or does not exist, prompt the user to select a folder
        if not self.folder_path:
            self.folder_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Folder ai folder")

        # Save the selected folder path to folder_path.txt
        with open("folder_path.txt", "w") as file:
            file.write(self.folder_path)

        # If the user canceled the folder selection, exit the application
        if not self.folder_path:
            sys.exit()

        timer = QElapsedTimer()
        timer.start()

        while timer.elapsed() < 3000:  # 3000 milliseconds = 3 seconds
            app.processEvents()

        splash.close()
        self.load_images_from_folder(self.folder_path)
        self.load_image()
        self.showMaximized()
    
    def min_run(self):
        self.folder_path = askdirectory(title="Select Folder ai folder")
        if self.folder_path:
            try:
                splash_pix = QPixmap("https://www.google.com/url?sa=i&url=https%3A%2F%2Fgithub.com%2Ftopics%2Fscreen-annotation&psig=AOvVaw0K5r_ors996VBjGeYkQjFX&ust=1689769272621000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCPD6u5-fmIADFQAAAAAdAAAAABAD") 
                max_splash_size = QtCore.QSize(300, 300)
                splash_pix = splash_pix.scaled(max_splash_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
                desktop = QtWidgets.QApplication.desktop()
                screen_rect = desktop.availableGeometry(desktop.primaryScreen())
                splash.move(screen_rect.center() - splash.rect().center())
                #splash.setFixedSize(splash_pix.size())
                splash.setMask(splash_pix.mask())
            except Exception as e:
                print("Error loading image:", e) 
            splash.showMessage("Loading...", Qt.AlignBottom | Qt.AlignCenter, QtGui.QColor(Qt.black))
            splash.show()
            app.processEvents()
            timer = QElapsedTimer()
            timer.start()

            while timer.elapsed() < 3000:  # 3000 milliseconds = 3 seconds
                app.processEvents()
            with open("folder_path.txt", "w") as file:
                file.write(self.folder_path)
        if not self.folder_path:
            with open("folder_path.txt", "r") as file:
                self.folder_path = file.read().strip()
        self.load_images_from_folder(self.folder_path)
        self.load_image()
        self.showMaximized()

def message_handler(mode, context, message):
    pass  
qInstallMessageHandler(message_handler)

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(Qt.AA_Use96Dpi, True)
    w = MainWindow()
    w.setStyleSheet("""
    /* General styles */
    QPushButton {
        background-color: #3498db;
        color: white;
        font-size: 16px;
        padding: 8px;
        border-radius: 5px;
    }
    
    QSlider {
        background-color: #dcdde1;
        height: 20px;
        border-radius: 6px;
    }
    
    QGraphicsView {
        background-color: #f5f6fa;
        border: 1px solid #dcdde1;
    }

    QListWidget {
        background-color: #f5f6fa;
        border: 1px solid #dcdde1;
        font-size: 14px;
        padding: 5px;
        border-radius: 5px;
    }
    
    QScrollArea {
        background-color: #f5f6fa;
        border: 1px solid #dcdde1;
    }
    
    CustomLineEdit {
        background-color: #dcdde1;
        border-radius: 5px;
        padding: 5px;
        font-size: 14px;
    }
    
    /* Button-specific styles */
    QPushButton:hover {
        background-color: #2980b9;
    }
    
    QPushButton:pressed {
        background-color: #21618c;
    }
""")
    w.run()
    sys.exit(app.exec_())
