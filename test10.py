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

class AnimatedButton1(QPushButton):
    def __init__(self, parent=None):
        super(AnimatedButton1, self).__init__(parent)
        self.defaultText = "Save"
        self.savedText = "Saved"
        self.animationDuration = 2000  # Duration in milliseconds
        self.clicked.connect(self.animateSave)

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
        self.animationDuration = 2000  # Duration in milliseconds
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

        self.button_prev = QPushButton("Previous")
        self.button_prev.clicked.connect(self.button_click_prev)
       
       
        self.button_next = QPushButton("Next")
        self.button_next.clicked.connect(self.button_click_next)

        #self.button_save = QPushButton("Save")
        self.button_save = AnimatedButton1("Save")
        # Connect the save button to a slot if needed
        self.button_save.clicked.connect(self.handleSave)
        #self.button_save.clicked.connect(self.save_image_inside_rectangle)
    
 

        self.button_delete = AnimatedButton2("Delete")
        # Connect the delete button to a slot if needed
        self.button_delete.clicked.connect(self.handleDelete)

        self.activate_button = QPushButton("Draw Polygon")
        self.activate_button.setCheckable(True)
        self.activate_button.setChecked(False)
        self.activate_button.toggled.connect(self.toggle_painting)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_current_polygon)

        self.finish_button = QPushButton("Finish")
        self.finish_button.clicked.connect(self.finish_current_polygon)

        self.ask_folder = QPushButton("Choose Folder")
        self.ask_folder.clicked.connect(self.min_run)

        self.button_reset = QPushButton("Reset")
        self.button_ai_modale_load = QPushButton("Model_load")
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(-360)
        self.slider.setMaximum(360)
        self.slider.setValue(0)
        self.slider.setTickInterval(5)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.rotate_selected_item)


        self.label_coordinates = QListWidget()
        self.box = QHBoxLayout()
        # self.box.addWidget(self.label_coordinates)

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
        #hbox.addWidget(self.button_save_crop)
        hbox.addWidget(self.button_ai_modale_load)

        hbox2 = QHBoxLayout()

        hbox2.addWidget(self.activate_button)
        hbox2.addWidget(self.clear_button)
        hbox2.addWidget(self.finish_button)
        hbox2.addWidget(self.ask_folder)
        vbox2 = QVBoxLayout()
        

        self.scene = GraphicsScene('',self.label_coordinates,self.coordinates_data,self.scroll_layout,self)

        self.pixmap = QPixmap()
        self.view = QGraphicsView(self.scene)
        
        self.scene.setSceneRect(0, 0,self.pixmap.width() , self.pixmap.height())

        self.view.setScene(self.scene)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.box.addWidget(self.view)
    
        self.scrollable.setWidget(self.scroll_widget)
        self.scrollable.setFixedWidth(250)
        self.box.addWidget(self.scrollable)
        
        
        
        vbox2.addLayout(self.box)
        vbox2.addLayout(hbox) 
        vbox2.addLayout(hbox2)
        vbox2.addWidget(self.slider)  
        self.setLayout(vbox2)
        self.label_coordinates.clicked.connect(self.select_rectangle)
        #self.button_save_crop.clicked.connect(self.save_image_inside_rectangle)
        self.button_reset.clicked.connect(self.reset_image)
        self.button_delete.clicked.connect(self.delete_rectangle)
        self.button_ai_modale_load.clicked.connect(self.call_modale)



    def toggle_painting(self, checked):
        self.scene.is_painting_activated = checked
        if checked:
            self.activate_button.setText("End Polygon")
        else:
            self.activate_button.setText("Draw Polygon")
        self.scene.clearCurrentPolygon()

    def clear_current_polygon(self):
        self.scene.clearCurrentPolygon()

    def finish_current_polygon(self):
        self.scene.finishCurrentPolygon()


    def handleSave(self):
        if len(self.scene.items()) == 0:
            # No new bounding boxes
            if self.hasExistingRectangles():
                self.showMessageBox("No New Rectangles", "There are no new rectangles to save.")
            else:
                self.showMessageBox("No Rectangles", "There are no rectangles to save.")
        else:
            # New bounding boxes are present, perform the save functionality here
            image_path = self.image_paths[self.current_image_index]
            if self.hasNewRectangles():
                print("Saving data...")
                self.save_coordinates_to_json()
                self.save_image_inside_rectangle(image_path)
            else:
                self.showMessageBox("No New Rectangles", "There are no new rectangles to save.")

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
        return False

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

    def load_image(self):
        self.load_coordinates_from_json()
        if self.image_paths:
            
            image_path = self.image_paths[self.current_image_index]
            self.scene.image= image_path
            self.pixmap = QPixmap(image_path)
            
            # self.label_coordinates = self.scene.label_c
            self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            
            for item in self.scene.items():
                if isinstance(item, GraphicsRectItem):
                    self.scene.removeItem(item)
            
            while self.scroll_layout.count():
                item = self.scroll_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            a = 0
            if self.coordinates_data != {}:
                if image_path in self.coordinates_data:
                    self.text_data[image_path] = {}
                    for key in self.coordinates_data[image_path]:
                        data = self.coordinates_data[image_path][key]
                        if key[0] == "[":
                            item = CustomPolygonItem()
                            for point in data['coordinates']:
                                item.addPoint(QPointF(point[0],point[1]))
                            self.scene.addItem(item)
                            t = CustomLineEdit(f"{tuple(data['coordinates'][0])}_{tuple(data['coordinates'][1])}",self.scene,self.scroll_layout)
                            self.text_data[image_path][t.index] = t
                            t.setText(data['text'])
                            t.setCursorPosition(0)
                            self.scroll_layout.addWidget(t)
                        else:   
                            item = GraphicsRectItem(QRectF(QPointF(0,0),QSizeF(data['width'],data['height'])))
                            item.moveBy(data['x'], data['y'])
                            item.setRotation(data['rotation'])
                            self.scene.addItem(item)
                            t = CustomLineEdit(f"{data['x'],data['y']}",self.scene,self.scroll_layout)
                            self.text_data[image_path][t.index] = t
                            t.setText(data['text'])
                            t.setCursorPosition(0)
                            self.scroll_layout.addWidget(t)
                    self.scrollable.setWidget(self.scroll_widget)
                self.box.addWidget(self.scrollable)
            self.button_save.clicked.connect(self.save_coordinates_to_json)
            #self.button_save.clicked.connect(self.save_image_inside_rectangle)
            
            #self.image_path = image_path
            self.scene.add_list()
            self.save_last_image_path()
            # self.scene.update()
        # self.save_coordinates_to_json()


    def save_coordinates_to_json(self):
        if self.image_paths and len(self.scene.items()) != 0:
            image_path = self.image_paths[self.current_image_index]
            if image_path not in self.coordinates_data:
                self.coordinates_data[image_path] = {}

            for item in self.scene.items():
                if isinstance(item, GraphicsRectItem):
                    rect = item.mapToScene(item.rect().topLeft())
                    key = f"{rect.x()}_{rect.y()}_{item.rect().width()}_{item.rect().height()}"
                    data = {
                        'x': rect.x(),
                        'y': rect.y(),
                        'width': item.rect().width(),
                        'height': item.rect().height(),
                        'rotation': item.rotation(),
                        'text': f"{rect.x(), rect.y()}"
                    }
                    self.coordinates_data[image_path][key] = data
                if isinstance(item,CustomPolygonItem):
                    coord = item.getCoordinates()
                    key = str(coord)
                    data = {
                        'coordinates': coord,
                        'text': f"{coord[1]}_{coord[2]}"
                    }
                    self.coordinates_data[image_path][key] = data
            # Update text data for existing coordinates
            if image_path in self.text_data:
                for key, value in self.coordinates_data[image_path].items():
                    if key in self.text_data[image_path]:
                        value["text"] = self.text_data[image_path][key].text()

            if not self.coordinates_data:
                print("No coordinates to save.")
                return

            image_name = os.path.splitext(os.path.basename(image_path))[0]
            coordinates_folder = os.path.join(os.path.dirname(image_path), "coordinates", image_name)
            os.makedirs(coordinates_folder, exist_ok=True)

            json_file = os.path.join(coordinates_folder, f"{image_name}_coordinates.json")
            with open(json_file, "w") as f:
                json.dump(self.coordinates_data[image_path], f, indent=4)

            self.load_image()
            self.scene.update()

    def delete_rectangle(self):
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
            # Bounding boxes are present
            selected_item = None
            for item in self.scene.items():
                if isinstance(item, GraphicsRectItem) and item.isSelected():
                    selected_item = item
                    break

            if selected_item:
                rect = selected_item.mapToScene(selected_item.rect().topLeft())
                data = f"Rec:- {rect.x(), rect.y()}"
                pattern = f"{rect.x()}_{rect.y()}_{selected_item.rect().width()}_{selected_item.rect().height()}"
                self.scene.removeItem(selected_item)

                image_path = self.image_paths[self.current_image_index]
                if image_path in self.coordinates_data:
                    d = self.coordinates_data[image_path]
                    for key, value in list(d.items()):
                        if f"Rec:- {value['x'], value['y']}" == data:
                            del self.text_data[image_path][f"{value['x'], value['y']}"]
                            del self.coordinates_data[image_path][key]

                # Delete the corresponding JSON file and image file
                image_name = os.path.splitext(os.path.basename(image_path))[0]
                coordinates_folder = os.path.join(os.path.dirname(image_path), "coordinates", image_name)
                image_folder = os.path.join(os.path.dirname(image_path), "image", image_name)
                json_file_pattern = os.path.join(coordinates_folder, f"{image_name}_coordinates.json")
                image_file_pattern = os.path.join(image_folder, f"{image_name}.png")

                # Delete JSON files
                json_files = glob.glob(json_file_pattern)
                for json_file in json_files:
                    if os.path.exists(json_file):
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                        
                        for key, value in list(data.items()):
                            if (
                                value['x'] == rect.x()
                                and value['y'] == rect.y()
                                and value['width'] == selected_item.rect().width()
                                and value['height'] == selected_item.rect().height()
                            ):
                                del data[key]
                                break
                        
                        with open(json_file, 'w') as f:
                            json.dump(data, f, indent=4)
                            print(f"JSON file updated: {json_file}")

                # Delete image files
                image_files = glob.glob(image_file_pattern)
                for image_file in image_files:
                    if os.path.exists(image_file):
                        os.remove(image_file)
                        print(f"Image file removed successfully: {image_file}")

                print("Item removed successfully.")
                self.load_image()
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

        self.selected_index = -1

    def load_coordinates_from_json(self):
        self.coordinates_data = {}
        for image_path in self.image_paths:
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            coordinates_folder = os.path.join(os.path.dirname(image_path), "coordinates")
            if os.path.exists(coordinates_folder) and os.path.isdir(coordinates_folder):
                image_coordinates_folder = os.path.join(coordinates_folder, image_name)
                if os.path.exists(image_coordinates_folder) and os.path.isdir(image_coordinates_folder):
                    json_file = os.path.join(image_coordinates_folder, f"{image_name}_coordinates.json")
                    if os.path.exists(json_file):
                        with open(json_file, "r") as f:
                            self.coordinates_data[image_path] = json.load(f)
                else:
                    print(f"Coordinates folder not found for image: {image_name}")
            else:
                print(f"Coordinates folder not found for image: {image_name}")


    def button_click_prev(self):
        if self.scene.items():
            image_path = self.image_paths[self.current_image_index]
            if image_path in self.coordinates_data:
                saved_rectangles = len(self.coordinates_data[image_path])
                unsaved_rectangles = len(self.scene.items())
                if unsaved_rectangles > saved_rectangles:
                    reply = QMessageBox.question(self, "Unsaved Changes",
                                                 f"There are {unsaved_rectangles - saved_rectangles} unsaved rectangles on the current image.\n"
                                                 f"Do you want to save the changes before moving to the previous image?",
                                                 QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                    if reply == QMessageBox.Yes:
                        self.handleSave()  # Save the changes
                    elif reply == QMessageBox.Cancel:
                        return  # Cancel the action, do not move to the previous image

        self.current_image_index -= 1  # Move to the previous image
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
                if unsaved_rectangles > saved_rectangles:
                    reply = QMessageBox.question(self, "Unsaved Changes",
                                                 f"There are {unsaved_rectangles - saved_rectangles} unsaved rectangles on the current image.\n"
                                                 f"Do you want to save the changes before moving to the previous image?",
                                                 QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                    if reply == QMessageBox.Yes:
                        self.handleSave()  # Save the changes
                    elif reply == QMessageBox.Cancel:
                        return  # Cancel the action, do not move to the previous image
                    
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
                if f"Rec:- {item.index}" == rec:
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
    
    def rotate_rec(self):
        for item in self.scene.items():
            if isinstance(item,GraphicsRectItem):
                if item.isSelected():
                    item.rotate(5)
                    # self.scene.update()
                    break

    def save_image_inside_rectangle(self, image_path):
            if not self.coordinates_data:
                print("No coordinates to save.")
                return

        #for image_path in self.coordinates_data:
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            image_folder = os.path.join(os.path.dirname(image_path), "image", image_name)
            os.makedirs(image_folder, exist_ok=True)
            

            existing_files = os.listdir(image_folder)
            for file_name in existing_files:
                if file_name.endswith(".png"):
                    file_path = os.path.join(image_folder, file_name)
                    os.remove(file_path)


            d = self.coordinates_data[image_path]
            original_image = QImage(image_path)
            for i in d:

                # Calculate the rectangle's dimensions
                if i[0] == "[":
                    image = Image.open(image_path)
                    mask = Image.new("L", image.size, 0)
                    draw = ImageDraw.Draw(mask)
                    polygon_points = [QPointF(point[0], point[1]) for point in d[i]['coordinates']]
                    polygon = Polygon([(point.x(), point.y()) for point in polygon_points])
                    xy = [(int(point.x()), int(point.y())) for point in polygon_points]
                    draw.polygon(xy, fill=255)
                    cropped_image = Image.new("RGBA", image.size)
                    cropped_image.paste(image, mask=mask)
                    data = f"{d[i]['coordinates']}"
                else:
                    left = d[i]['x']
                    top = d[i]['y']
                    width = d[i]['width']
                    height = d[i]['height']

                    # # Create a cropped image of the rectangle area
                    cropped_image = original_image.copy(int(left), int(top), int(width), int(height))
                    data = f"{left}_{top}_{width}_{height}"

    
                # # Save the cropped image with a unique name
                image_file = os.path.join(image_folder, f"{image_name}_rectangle_{data}.png")
                cropped_image.save(image_file)
    
                print(f"Cropped image saved: {image_file}")




    def reset_image(self):
        if self.image_paths:
            image_path = self.image_paths[self.current_image_index]
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            coordinates_folder = os.path.join(os.path.dirname(image_path), "coordinates", image_name)
            image_folder = os.path.join(os.path.dirname(image_path), "image", image_name)

            # Delete JSON file for the current image
            json_file = os.path.join(coordinates_folder, f"{image_name}_coordinates.json")
            if os.path.exists(json_file):
                os.remove(json_file)
                print(f"JSON file removed successfully: {json_file}")
            else:
                print(f"JSON file does not exist: {json_file}")

            # Delete cropped image file for the current image
            image_file = os.path.join(image_folder, f"{image_name}.png")
            if os.path.exists(image_file):
                os.remove(image_file)
                print(f"Image file removed successfully: {image_file}")
            else:
                print(f"Image file does not exist: {image_file}")

            # Remove the current image from coordinates_data
            if image_path in self.coordinates_data:
                del self.coordinates_data[image_path]

            self.load_image()

        self.repaint()
        self.call_modale()



    def call_modale(self):
        with open("folder_path.txt", "r") as file:
            folder_path = file.read().strip()


        source_directory = r"E:\x\IITJ_project\pro\ai"  # Replace with the desired destination folder path
        
        for root, dirs, files in os.walk(source_directory):
    # Create the corresponding subdirectory in the destination directory
            for dir_name in dirs:
                source_path = os.path.join(root, dir_name)
                destination_path = os.path.join(folder_path, os.path.relpath(source_path, source_directory))
                os.makedirs(destination_path, exist_ok=True)

        # Copy files from the source to the destination directory
        for root, dirs, files in os.walk(source_directory):
            for file_name in files:
                source_path = os.path.join(root, file_name)
                destination_path = os.path.join(folder_path, os.path.relpath(source_path, source_directory))
                shutil.copy2(source_path, destination_path)
        
        self.load_image()
        self.load_coordinates_from_json()

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

    def rotate_selected_item(self):
        rotation_angle = self.slider.value()
        for item in self.scene.items():
            if isinstance(item, QGraphicsRectItem) and item.isSelected():
                item.setRotation(rotation_angle)
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
            splash.setFixedSize(splash_pix.size())
            splash.setMask(splash_pix.mask())
        except Exception as e:
            print("Error loading image:", e) 
        splash.showMessage("Loading...", Qt.AlignBottom | Qt.AlignCenter, QtGui.QColor(Qt.black))
        splash.show()
        app.processEvents()

        # Check if folder_path.txt exists and read the folder path from it
        if os.path.exists("folder_path.txt"):
            with open("folder_path.txt", "r") as file:
                folder_path = file.read().strip()
        else:
            folder_path = None

        # If folder_path is empty or does not exist, prompt the user to select a folder
        if not folder_path:
            folder_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Folder ai folder")

        # Save the selected folder path to folder_path.txt
        with open("folder_path.txt", "w") as file:
            file.write(folder_path)

        # If the user canceled the folder selection, exit the application
        if not folder_path:
            sys.exit()

        timer = QElapsedTimer()
        timer.start()

        while timer.elapsed() < 3000:  # 3000 milliseconds = 3 seconds
            app.processEvents()

        splash.close()
        self.load_images_from_folder(folder_path)
        self.load_coordinates_from_json()
        self.load_image()
        self.show()
    def min_run(self):
        folder_path = askdirectory(title="Select Folder ai folder")
        try:
            splash_pix = QPixmap("https://www.google.com/url?sa=i&url=https%3A%2F%2Fgithub.com%2Ftopics%2Fscreen-annotation&psig=AOvVaw0K5r_ors996VBjGeYkQjFX&ust=1689769272621000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCPD6u5-fmIADFQAAAAAdAAAAABAD") 
            max_splash_size = QtCore.QSize(300, 300)
            splash_pix = splash_pix.scaled(max_splash_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
            desktop = QtWidgets.QApplication.desktop()
            screen_rect = desktop.availableGeometry(desktop.primaryScreen())
            splash.move(screen_rect.center() - splash.rect().center())
            splash.setFixedSize(splash_pix.size())
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
            file.write(folder_path)
        if not folder_path:
            sys.exit()
        self.load_images_from_folder(folder_path)
        self.load_coordinates_from_json()
        self.load_image()
        self.show()
def message_handler(mode, context, message):
    pass  
qInstallMessageHandler(message_handler)

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(Qt.AA_Use96Dpi, True)
    w = MainWindow()
    w.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint)
    w.setWindowFlags(w.windowFlags() & ~Qt.WindowMaximizeButtonHint)
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