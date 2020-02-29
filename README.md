# Obstacle-detection-using-OpenCV 
# Beta Version 

The goal is to detect a rectangle obstacle by using OpenCV, controlling a drone's movement through ROS in order to make an approach without colliding with the obstacle

The logic is based on https://stackoverflow.com/questions/60357533/separate-objects-countours-with-opencv:

 - Read the input
 - Convert to HSV and extract only the saturation channel (black/white/gray have zero saturation)
 - Threshold
 - Apply morphology open and close to remove the extranous white regions
 - Get the contour and approximate to simple polygon
 - Draw the polygon on the input
 - Analyze the obstacle's area
 
Achieved:

 - Obstacle detection
 - Area analysis
 - ROS implementation
 - Tested and working
 
Future tasks:

 - Improve filters fiability
 - Improve approach function
 - Dynamic filters
 - Fix bugs
