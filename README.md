# Scene-text-annotation-tool

## Running and Editing files
  1. Clone or download the zip folder of the repository.
  2. Unzip the zipped files and open the main.py file and run it.
  3. You will ask to select the folder of images. Select the folder and now start annotating.
## .exe file
  1. Go into the dist folder and run the main application to directly run the tool
## Link for the tool documentation
  https://docs.google.com/document/d/1Uaa3zA8UAS_9SWPOeY4MIJ8pCr-T93YCt7ttH3UqCXQ/edit?usp=sharing

## Steps to use the Program
  1. Run the main.py file or the main executable file in your desktop.
  2. Select the folder of images you want to annotate.
     
  ### Drawing Rectangle
    1. Press the left mouse key button and drag the mouse holding the left mouse button
    2. You can use the 8 size handlers to resize the the rectangle in respective 8 directions.
    3. Hover over the mouse handler and you will see that cursor changes into size handling cursor type.
    4. Click and drag the size handler, you will be able to resize the rectangle.

  ### Drawing Polygon
    1. Click on "draw polygon" button and click anywhere on the image. A point appears.
    2. Now again click and a line will be drawn between 1 and 2 point. 
    3. Repeat the step 1 and 2 to draw the polygon point by point.
    4. The last and the first point will be joined on every new click.
    5. To finish the current polygon click "Finish" button.
    6. After finishing the current polygon you can start drawing the new polygon.
    7. To clear the current drawn polygon click on the "Clear" button.
    8. By clicking on "End Polygon" button you can stop the polygon drawing function.

  ### Editing and adding text
    1. To add text to the polygon first save the all the new shapes drawn on the image. 
    2. As soon as you click on the "Save" button, you will see that on right side text boxes are being displayed.
    3. Now when you click on the text box you will see that the shape associated with the box is being highlighted as green.
    4. Similary when a shape is selected by clicking on it, the associated text box is highlighted.
    5. Edit the text box and again click on the save button to save the changes.

  ### Deleting a shape
    1. Select the shape you want to delete by clicking on the shape.
    2. Click on the "Delete" button to delete that selected shape.

  ### Reset (Use with caution)
    1. The reset button allows you to reset the image to its default presence by deleting all the shapes drawn on it.
