from PyQt5 import QtWidgets,QtGui,QtCore
import os
import json
import glob
from tkinter.filedialog import askdirectory
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from GraphicsScene import GraphicsScene
from GraphicsRectItem import GraphicsRectItem
from CustomLineEdit import CustomLineEdit
import shutil
from datetime import datetime



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

        self.button_prev = QPushButton("Previous")
        self.button_prev.clicked.connect(self.button_click_prev)
       
       
        self.button_next = QPushButton("Next")
        self.button_next.clicked.connect(self.button_click_next)

        #self.button_save = QPushButton("Save")
        self.button_save = AnimatedButton1("Save")
        # Connect the save button to a slot if needed
        self.button_save.clicked.connect(self.handleSave)
    
 

        self.button_delete = AnimatedButton2("Delete")
        # Connect the delete button to a slot if needed
        self.button_delete.clicked.connect(self.handleDelete)
 

        #self.button_delete = QPushButton("Delete")  
        #self.button_save_crop = QPushButton("Save Crop")
        self.button_reset = QPushButton("Reset")
        self.button_ai_modale_load = QPushButton("Modal_load")
        
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

        vbox2 = QVBoxLayout()
        

        self.scene = GraphicsScene('',self.label_coordinates,self.coordinates_data,self.scroll_layout,self)
        # self.scene.rectangleUpdated.connect(self.updateLabelCoordinates)
        # self.label_coordinates.clicked.connect(self.scene.highlight_item)

        self.pixmap = QPixmap()
        self.view = QGraphicsView(self.scene)
        
        self.scene.setSceneRect(0, 0,self.pixmap.width() , self.pixmap.height())

        self.view.setScene(self.scene)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        # self.view.setBackgroundBrush(QImage('D:\Intern Project\SamplePhoto_1.jpg'))
        self.box.addWidget(self.view)
    
        self.scrollable.setWidget(self.scroll_widget)
        self.scrollable.setFixedWidth(250)
        self.box.addWidget(self.scrollable)
        
        
        
        vbox2.addLayout(self.box)
        vbox2.addLayout(hbox) 
        vbox2.addWidget(self.slider)  
        # vbox2.addLayout(scrol_layout)
        self.setLayout(vbox2)
        self.label_coordinates.clicked.connect(self.select_rectangle)
        #self.button_save_crop.clicked.connect(self.save_image_inside_rectangle)
        self.button_reset.clicked.connect(self.reset_image)
        self.button_delete.clicked.connect(self.delete_rectangle)
        self.button_ai_modale_load.clicked.connect(self.call_modale)



    def handleSave(self):
        if len(self.scene.items()) == 0:
            # No bounding boxes present
            QMessageBox.warning(self, "No Bounding Box", "There are no bounding boxes to save.")
        else:
            # Bounding boxes are present, perform the save functionality here
            print("Saving data...")

    def handleDelete(self):
        if len(self.scene.items()) == 0:
            # No bounding boxes present
            QMessageBox.warning(self, "No Bounding Box", "There are no bounding boxes to delete.")
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
            # print(self.coordinates_data)
            if self.coordinates_data != {}:
                if image_path in self.coordinates_data:
                    self.text_data[image_path] = {}
                    for i in self.coordinates_data[image_path]:
                        data = self.coordinates_data[image_path][i]
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
            self.button_save.clicked.connect(self.save_image_inside_rectangle)
            
            self.scene.add_list()
            self.save_last_image_path()
            # self.scene.update()
        # self.save_coordinates_to_json()
    def save_coordinates_to_json(self):
        if self.image_paths and  len(self.scene.items()) != 0:
            image_path = self.image_paths[self.current_image_index]
            for i,item in enumerate(self.scene.items()):
                data = {
                    'x': 0,
                    'y': 0,
                    'width': 0,
                    'height': 0,
                    'rotation': 0,
                    'text' : ""
                }
                if isinstance(item, GraphicsRectItem):
                    # print("Graphics Rect Item found!")
                    rect = item.mapToScene(item.rect().topLeft())
                    # print(rect.x(),rect.y())
                    if image_path not in self.coordinates_data:
                        self.coordinates_data[image_path] = {}

                    if i not in self.coordinates_data[image_path]:
                         self.coordinates_data[image_path][i] = {}
                    data["x"] = rect.x()
                    data["y"] = rect.y()
                    data["height"] = item.rect().height()
                    data["width"] = item.rect().width()
                    data["rotation"] = item.rotation()
                    data["text"] = f"{rect.x(),rect.y()}"
                    self.coordinates_data[image_path][i] = data

            d = self.coordinates_data[image_path]
            for box in d:
                id = f"{d[box]['x'],d[box]['y']}"
                if image_path in self.text_data:
                    if id in self.text_data[image_path]:
                        d[box]["text"] = self.text_data[image_path][id].text() 



            # print(self.coordinates_data)
            if not self.coordinates_data:
                print("No coordinates to save.")
                return

            for image_path in self.coordinates_data:
                image_name = os.path.splitext(os.path.basename(image_path))[0]
                coordinates_folder = os.path.join(os.path.dirname(image_path), "coordinates", image_name)
                os.makedirs(coordinates_folder, exist_ok=True)

                existing_files = os.listdir(coordinates_folder)
                for file_name in existing_files:
                    if file_name.endswith("_coordinate.json"):
                        file_path = os.path.join(coordinates_folder, file_name)
                        os.remove(file_path)

                d = self.coordinates_data[image_path]
                # print(d)
                for key in d:
                    data = f"{d[key]['x']}_{d[key]['y']}_{d[key]['width']}_{d[key]['height']}"
                    save = d[key]
                    json_file = os.path.join(coordinates_folder, f"{image_name}_rectangle_{data}_coordinate.json")
                    with open(json_file, "w") as f:
                        json.dump(save, f, indent=4)

                    # print(f"saved at {json_file}")
            self.load_image()
            self.scene.update()

    def button_click_prev(self):
        if self.image_paths:
            self.save_last_image_path()  # Save the last image path
            self.current_image_index -= 1
            if self.current_image_index < 0:
                self.current_image_index = len(self.image_paths) - 1
            self.load_image()
            self.update()

    def button_click_next(self):
        if self.image_paths:
            self.save_last_image_path()  # Save the last image path
            self.current_image_index += 1
            if self.current_image_index >= len(self.image_paths):
                self.current_image_index = 0
            self.load_image()
            self.update()
    
    def load_coordinates_from_json(self):
        self.coordinates_data = {}
        for image_path in self.image_paths:
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            coordinates_folder = os.path.join(os.path.dirname(image_path), "coordinates")
            if os.path.exists(coordinates_folder) and os.path.isdir(coordinates_folder):
                image_coordinates_folder = os.path.join(coordinates_folder, image_name)
                if os.path.exists(image_coordinates_folder) and os.path.isdir(image_coordinates_folder):
                    # n = len(os.listdir(image_coordinates_folder))
                    for i,filename in enumerate(os.listdir(image_coordinates_folder)):
                        if filename.endswith("_coordinate.json"):
                            json_file = os.path.join(image_coordinates_folder, filename)
                            with open(json_file, "r") as f:
                                rectangle_data = json.load(f)

                            if image_path not in self.coordinates_data:
                                self.coordinates_data[image_path] = {}
                            # print(self.coordinates_data)
                            self.coordinates_data[image_path][i] = rectangle_data
            else:
                print(f"Coordinates folder not found for image: {image_name}")

    def select_rectangle(self):

        self.selected_index = self.label_coordinates.currentItem()
        rec = self.label_coordinates.currentItem().text()
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i).widget()

            if isinstance(item, CustomLineEdit):
                if f"Rec:- {item.index}" == rec:
                    line_edit = item
                    line_edit.focusInEvent(QtGui.QFocusEvent(QtGui.QKeyEvent.FocusIn))
                else:
                    line_edit = item
                    line_edit.focusOutEvent(QtGui.QFocusEvent(QtGui.QKeyEvent.FocusOut))
            else:
                line_edit = item
                line_edit.focusOutEvent(QtGui.QFocusEvent(QtGui.QKeyEvent.FocusOut))

        for item in self.scene.items():
            if isinstance(item, GraphicsRectItem):
                rect = item.mapToScene(item.rect().topLeft())
                data = f"Rec:- {rect.x(), rect.y()}"
                if data == rec:
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

    def save_image_inside_rectangle(self):
        if not self.coordinates_data:
            print("No coordinates to save.")
            return

        for image_path in self.coordinates_data:
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            image_folder = os.path.join(os.path.dirname(image_path), "image", image_name)
            os.makedirs(image_folder, exist_ok=True)
            
            d = self.coordinates_data[image_path]
            original_image = QImage(image_path)
            for i in d:

                # Calculate the rectangle's dimensions
                left = d[i]['x']
                top = d[i]['y']
                width = d[i]['width']
                height = d[i]['height']

                # # Create a cropped image of the rectangle area
                cropped_image = original_image.copy(int(left), int(top), int(width), int(height))

    
                # # Save the cropped image with a unique name
                data = f"{left}_{top}_{width}_{height}"
                image_file = os.path.join(image_folder, f"{image_name}_rectangle_{data}.png")
                cropped_image.save(image_file)
    
                print(f"Cropped image saved: {image_file}")

    def delete_rectangle(self):
        # if self.selected_index == -1:
        #     self.message_box.setIcon(QMessageBox.Information)
        #     self.message_box.setText("Please select a rectangle")
        #     self.message_box.setWindowTitle("Information")
        #     self.message_box.exec_()
        #     return
        
        pattern = ""
        data = ""
        image_path = self.image_paths[self.current_image_index]
        # print(self.coordinates_data)
        if image_path in self.coordinates_data:
            # if self.label_coordinates.currentItem().text() is not None:
                # id = self.label_coordinates.currentItem().text()
            for item in self.scene.items():
                if isinstance(item,GraphicsRectItem) and item.isSelected():
                    rect = item.mapToScene(item.rect().topLeft())
                    data = f"Rec:- {rect.x(),rect.y()}"
                    pattern = f"{rect.x()}_{rect.y()}_{item.rect().width()}_{item.rect().height()}"
                    self.scene.removeItem(item)
                    break
            d = self.coordinates_data[image_path]
            print(self.text_data)
            for key in d:
                if data == f"Rec:- {d[key]['x'],d[key]['y']}":
                    del self.text_data[image_path][f"{d[key]['x'],d[key]['y']}"]
                    del self.coordinates_data[image_path][key]
                    break
            
            # Delete the corresponding JSON file and image file
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            coordinates_folder = os.path.join(os.path.dirname(image_path), "coordinates", image_name)
            image_folder = os.path.join(os.path.dirname(image_path), "image", image_name)
            json_file_pattern = os.path.join(coordinates_folder, f"{image_name}_rectangle_{pattern}_coordinate.json")
            image_file_pattern = os.path.join(image_folder, f"{image_name}_rectangle_{pattern}.png")
            # Delete JSON files
            json_files = glob.glob(json_file_pattern)
            for json_file in json_files:
                if os.path.exists(json_file):
                    os.remove(json_file)
                    print(f"JSON file removed successfully: {json_file}")
                    text_file = os.path.splitext(json_file)[0] + ".txt"
                    with open(text_file, "w") as file:
                        file.write("This file is deleted")
                        print(f"Text file created: {text_file}")
                else:
                    print(f"JSON file does not exist: {json_file}")

            # Delete image files
            image_files = glob.glob(image_file_pattern)
            for image_file in image_files:
                if os.path.exists(image_file):
                    os.remove(image_file)
                    print(f"Image file removed successfully: {image_file}")
                    text_file = os.path.splitext(image_file)[0] + ".txt"
                    with open(text_file, "w") as file:
                        file.write("This file is deleted")
                        print(f"Text file created: {text_file}")
                else:
                    print(f"Image file does not exist: {image_file}")

            print("Item removed successfully.")
            self.load_image()
    
        self.selected_index = -1

    
    
    
    def reset_image(self):
        if self.image_paths:
            image_path = self.image_paths[self.current_image_index]
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            coordinates_folder = os.path.join(os.path.dirname(image_path), "coordinates", image_name)
            image_folder = os.path.join(os.path.dirname(image_path),"image",image_name)
            text_folder = os.path.join(os.path.dirname(image_path), "text", image_name)
            # Delete all JSON files for the current image
            json_files = glob.glob(os.path.join(coordinates_folder, f"{image_name}_rectangle_*_coordinate.json"))
            for json_file in json_files:
                if os.path.exists(json_file):
                    os.remove(json_file)
                    print(f"JSON file removed successfully: {json_file}")
                else:
                    print(f"JSON file does not exist: {json_file}")

            # Delete all image files for the current image
            image_files = glob.glob(os.path.join(image_folder, f"{image_name}_rectangle_*.png"))
            for image_file in image_files:
                if os.path.exists(image_file):
                    os.remove(image_file)
                    print(f"Image file removed successfully: {image_file}")
                else:
                    print(f"Image file does not exist: {image_file}")

            text_files = glob.glob(os.path.join(text_folder, f"{image_name}_text_data_*.json"))

            # Remove the current image from coordinates_data
            if image_path in self.coordinates_data:
                del self.coordinates_data[image_path]
                del self.text_data[image_path]
            self.load_image()

        self.repaint()
        self.call_modale()


    def run(self):
        folder_path = askdirectory(title="Select Folder ai folder")
        with open("folder_path.txt", "w") as file:
            file.write(folder_path)
        if not folder_path:
            sys.exit()
        self.load_images_from_folder(folder_path)
        self.load_coordinates_from_json()
        self.load_image()
        self.show()


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
    w.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint)
    w.setWindowFlags(w.windowFlags() & ~Qt.WindowMaximizeButtonHint)
    w.run()
    sys.exit(app.exec_())
