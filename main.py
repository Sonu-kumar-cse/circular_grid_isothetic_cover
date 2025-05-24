import cv2
import numpy as np
import math


def ugb_occupancy_marker():
    if center_x-10>=0 and center_x-10<image_width and center_y-10>=0 and center_y-10<image_height and binary_image[center_x-10,center_y-10]==0:
        for i in range(total_arc_per_circle):
            print("hello")
            UGB_array[0,i]=True
    else :
        for i in range(total_arc_per_circle):
            first_angle_degrees = i*angle_step
            first_angle_radians = math.radians(first_angle_degrees)
            second_angle_degrees = ((i+1)%total_arc_per_circle) * angle_step
            if second_angle_degrees==0:
                second_angle_degrees=360
            second_angle_radians = math.radians(second_angle_degrees)
            middle_angle_degrees =  (first_angle_degrees+second_angle_degrees)/2
            middle_angle_radians = math.radians(middle_angle_degrees)
            print(f'first={first_angle_degrees}_{first_angle_radians} second={second_angle_degrees}_{second_angle_radians} middle={middle_angle_degrees}_{middle_angle_radians}')
            x1=center_x+radius_step*math.cos(first_angle_radians)
            x2=center_x+radius_step*math.cos(second_angle_radians)
            x3=center_x+radius_step*math.cos(middle_angle_radians)
            y1=center_y+radius_step*math.sin(first_angle_radians)
            y2=center_y+radius_step*math.sin(second_angle_radians)
            y3=center_y+radius_step*math.sin(middle_angle_radians)
            x_min=math.floor(min(x1,x2,x3,center_x))
            y_min=math.floor(min(y1,y2,y3,center_y))
            x_max=math.ceil(max(x1,x2,x3,center_x))
            y_max=math.ceil(max(y1,y2,y3,center_y))
            print(f'{x_min},{y_min} {x_max},{y_max} ')
            for y in range(y_min-10,y_max-10+1):
                for x in range(x_min-10,x_max-10+1):
                    if x>=0 and y>=0 and x<image_width and y<image_height:
                        distance=np.sqrt((x - (center_x-10))**2 + (y - (center_y-10))**2)
                        curr_angle = np.arctan2(y - center_y, x - center_x)
                        curr_angle =curr_angle+ 2 * np.pi if curr_angle<0 else curr_angle # Normalize angles to [0, 2π)
                        curr_angle=np.degrees(curr_angle)
                        if 0<=math.ceil(distance) and math.floor(distance)<=radius_step:
                            if math.ceil(curr_angle)>=first_angle_degrees and math.floor(curr_angle)<=second_angle_degrees:
                                if binary_image[y,x]==0:
                                    UGB_array[0,i]=True
    
    for i in range(1,total_circles):
        for j in range(total_arc_per_circle):
            first_angle_degrees = j*angle_step
            first_angle_radians = math.radians(first_angle_degrees)
            second_angle_degrees = ((j+1)%total_arc_per_circle) * angle_step
            if second_angle_degrees==0:
                second_angle_degrees=360
            second_angle_radians = math.radians(second_angle_degrees)
            middle_angle_degrees =  (first_angle_degrees+second_angle_degrees)/2
            middle_angle_radians = math.radians(middle_angle_degrees)
            prev_radius=i*radius_step
            curr_radius=prev_radius+radius_step
            
            x1=center_x+prev_radius*math.cos(first_angle_radians)
            x2=center_x+curr_radius*math.cos(first_angle_radians)
            x3=center_x+prev_radius*math.cos(second_angle_radians)
            x4=center_x+curr_radius*math.cos(second_angle_radians)
            x5=center_x+curr_radius*math.cos(middle_angle_radians)
            
            y1=center_y+prev_radius*math.sin(first_angle_radians)
            y2=center_y+curr_radius*math.sin(first_angle_radians)
            y3=center_y+prev_radius*math.sin(second_angle_radians)
            y4=center_y+curr_radius*math.sin(second_angle_radians)
            y5=center_y+curr_radius*math.sin(middle_angle_radians)

            x_min=math.floor(min(x1,x2,x3,x4,x5))
            x_max=math.ceil(max(x1,x2,x3,x4,x5))
            y_min=math.floor(min(y1,y2,y3,y4,y5))
            y_max=math.ceil(max(y1,y2,y3,y4,y5))
            for y in range(y_min-10,y_max-10+1):
                for x in range(x_min-10,x_max-10+1):
                    if x>=0 and y>=0 and x<image_width and y<image_height:
                        distance=np.sqrt((x - (center_x-10))**2 + (y - (center_y-10))**2)
                        curr_angle = np.arctan2(y - center_y, x - center_x)
                        curr_angle =curr_angle+ 2 * np.pi if curr_angle<0 else curr_angle # Normalize angles to [0, 2π)
                        curr_angle=np.degrees(curr_angle)
                        if prev_radius<=math.ceil(distance) and math.floor(distance)<=curr_radius:
                            if math.ceil(curr_angle)>=first_angle_degrees and math.floor(curr_angle)<=second_angle_degrees:
                                if binary_image[y,x]==0:
                                    UGB_array[i,j]=True


            
 
            
                                
                            
   


def create_svg_file(filename, n, r_step):

    with open(filename, 'w') as f:
        # SVG Header
        extra_padding_x=total_circles*radius_step-(image_width//2+10)
        extra_padding_y=total_circles*radius_step-(image_height//2+10)
        print(f"extar_padding = {extra_padding_x,extra_padding_y}")
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{image_height+20+2*extra_padding_x}" height="{image_width+20+2*extra_padding_y}">\n')
        f.write(f'<image href="image1.png" x="{10+extra_padding_x}" y="{10+extra_padding_y}" width="{image_width}" height="{image_height}" />')
        # Add concentric circles
        for i in range(1, n + 1):
            r = i * r_step
            f.write(f'  <circle cx="{center_x+extra_padding_x}" cy="{center_y+extra_padding_y}" r="{r}" stroke="red" fill="none" />\n')
        
        for i in range(total_arc_per_circle):
            curr_angle=i*angle_step
            curr_angle_radian=math.radians(curr_angle)
            x=center_x+extra_padding_x+total_circles*radius_step*math.cos(curr_angle_radian)
            y=center_y+extra_padding_y+total_circles*radius_step*math.sin(curr_angle_radian)
            f.write(f'<line x1="{center_x+extra_padding_x}" y1="{center_y+extra_padding_y}" x2="{x}" y2="{y}" stroke="black" stroke-width="2"/>')
            
        # f.write(f'  <circle cx="{100}" cy="{10}" r="{2}" stroke="red" fill="pink" />\n')
        # f.write(f'<line x1="{269}" y1="{280}" x2="{269}" y2="{367}" stroke="green" stroke-width="2"/>')
        # f.write(f'<line x1="{269}" y1="{280}" x2="{369}" y2="{280}" stroke="green" stroke-width="2"/>')
        # f.write(f'<line x1="{369}" y1="{367}" x2="{269}" y2="{367}" stroke="green" stroke-width="2"/>')
        # f.write(f'<line x1="{369}" y1="{367}" x2="{369}" y2="{280}" stroke="green" stroke-width="2"/>')

        # f.write(f'<line x1="{219}" y1="{280}" x2="{219}" y2="{380}" stroke="pink" stroke-width="2"/>')
        # f.write(f'<line x1="{219}" y1="{280}" x2="{319}" y2="{280}" stroke="pink" stroke-width="2"/>')
        # f.write(f'<line x1="{319}" y1="{380}" x2="{219}" y2="{380}" stroke="pink" stroke-width="2"/>')
        # f.write(f'<line x1="{319}" y1="{380}" x2="{319}" y2="{280}" stroke="pink" stroke-width="2"/>')

        # f.write(f'<line x1="{169}" y1="{280}" x2="{169}" y2="{367}" stroke="blue" stroke-width="2"/>')
        # f.write(f'<line x1="{169}" y1="{280}" x2="{269}" y2="{280}" stroke="blue" stroke-width="2"/>')
        # f.write(f'<line x1="{269}" y1="{367}" x2="{169}" y2="{367}" stroke="blue" stroke-width="2"/>')
        # f.write(f'<line x1="{269}" y1="{367}" x2="{269}" y2="{280}" stroke="blue" stroke-width="2"/>')

        # SVG Footer
        for i in range(total_circles):
            curr_radius=i*radius_step+radius_step
            for j in range(total_arc_per_circle):
                curr_angle=j*angle_step
                curr_angle_radian=math.radians(curr_angle)
                x=center_x+extra_padding_x+curr_radius*math.cos(curr_angle_radian)
                y=center_y+extra_padding_y+curr_radius*math.sin(curr_angle_radian)
                my_color='green'
                if(UGB_array[i,j]): my_color='blue'
                f.write(f'  <circle cx="{x}" cy="{y}" r="{2}" stroke="{my_color}" fill="{my_color}" />\n')
        f.write('</svg>\n')

    print(f"SVG file '{filename}' created with {n} concentric circles.")

if __name__=="__main__":
    #take inputs
    # file_path=input("Enter image path: ")
    file_path='inputs/image1.png'
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

   
    global center_x,center_y,max_radius
    center_x=(image_width//2)+10
    center_y=(image_height//2)+10
    a=math.ceil(np.sqrt((center_x)*(center_x)+(center_y)*(center_y)))
    b=math.ceil(np.sqrt((center_x-image_width-20)*(center_x-image_width-20)+(center_y)*(center_y)))
    c=math.ceil(np.sqrt((center_x)*(center_x)+(center_y-image_height-20)*(center_y-image_height-20)))
    d=math.ceil(np.sqrt((center_x-image_width-20)*(center_x-image_width-20)+(center_y-image_height-20)*(center_y-image_height-20)))
    max_radius=max([a,b,c,d])

    print(a,b,c,d)
    print(max_radius)
    print(f'cener_x={center_x} center_y={center_y}')
    print(f'image width={image_width} height={image_height}')
    global total_circles,total_arcs_per_circle
    total_circles=math.ceil(max_radius/radius_step)
    total_arc_per_circle=math.ceil(360/angle_step)

    global UGB_array
    UGB_array = np.full((total_circles, total_arc_per_circle), False, dtype=bool)


    print(total_circles)
    print(total_arc_per_circle)
    
    ugb_occupancy_marker()
    create_svg_file('outputs/output.svg',total_circles,radius_step)
    print(UGB_array)


