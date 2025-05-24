import cv2
import numpy as np
import math
def ugb_occupancy_marker():
    
    pass


if __name__=="__main__":
    #take inputs
    file_path=input("Enter image path: ")
    global radius_step,angle_step
    radius_step=int(input("Enter the radius difference: "))
    angle_step=int(input("Enter angle steps: "))
    ##currently i am using center as center of impge only, later i will generalize it

    #make the image gray
    image = cv2.imread(file_path)
    global image_height,image_width
    image_height, image_width = image.shape[:2]
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('temp/grayscale.jpg', gray_image)

    #make binary image
    gray_image = cv2.imread('temp/grayscale.jpg', cv2.IMREAD_GRAYSCALE)
    global binary_image
    binary_image = (gray_image > 127).astype(np.uint8)  # 1 for >127, 0 otherwise

   
    global center_x,center_y
    center_x=(image_width//2)+10
    center_y=(image_height//2)+10
    a=math.ceil(np.sqrt((center_x)*(center_x)+(center_y)*(center_y)))
    b=math.ceil(np.sqrt((center_x-image_width-20)*(center_x-image_width-20)+(center_y)*(center_y)))
    c=math.ceil(np.sqrt((center_x)*(center_x)+(center_y-image_height-20)*(center_y-image_height-20)))
    d=math.ceil(np.sqrt((center_x-image_width-20)*(center_x-image_width-20)+(center_y-image_height-20)*(center_y-image_height-20)))
    max_radius=max([a,b,c,d])

    print(a,b,c,d)
    print(max_radius)

    global total_circles,total_arcs_per_circle
    total_circles=math.ceil(max_radius/radius_step)
    total_arc_per_circle=math.floor(360/angle_step)

    global UGB_array
    UGB_array = np.full((total_circles, total_arc_per_circle), False, dtype=bool)


    print(total_circles)
    print(total_arc_per_circle)





