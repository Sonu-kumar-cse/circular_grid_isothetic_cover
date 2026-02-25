import numpy as np
import os
import shutil
import math
def get_type_of_point(my_image,y,x,height,width,label):

    temp_array=np.zeros(4)
    if x>=0 and x<width and y>=0 and y<height and my_image[y,x]==label:
        temp_array[0]=temp_array[1]=temp_array[2]=temp_array[3]=1
    if x+1<width and y>=0 and y<height and my_image[y,x+1]==label:
        temp_array[0]=temp_array[1]=1
    if x-1>=0 and y>=0 and y<height and my_image[y,x-1]==label:
        temp_array[2]=temp_array[3]=1
    if y+1<height and x>=0 and x<width and my_image[y+1,x]==label:
        temp_array[0]=temp_array[3]=1
    if y-1>=0 and x>=0 and x<width and my_image[y-1,x]==label:
        temp_array[1]=temp_array[2]=1
    if x+1<width and y+1<height and my_image[y+1,x+1]==label:
        temp_array[0]=1
    if x+1<width and y-1>=0 and my_image[y-1,x+1]==label:
        temp_array[1]=1
    if x-1>=0 and y-1>=0 and my_image[y-1,x-1]==label:
        temp_array[2]=1
    if x-1>=0 and y+1<height and my_image[y+1,x-1]==label:
        temp_array[3]=1

    ugb_count=0
    for i in range(4):
        if temp_array[i]==1: ugb_count+=1
    
    if ugb_count==1:
        return 1
    if ugb_count==2:
        if (temp_array[1]==1 and temp_array[3]==1) or (temp_array[0]==1 and temp_array[2]==1): return -1
        return 0
    if ugb_count==3: return -1
    return 0
        
def trace_rect_outer_cover(my_image,y,x,height,width,label):
    sum_x=0
    sum_y=0
    total_count=0
    direction=3
    start_x=x
    start_y=y
    next_x=x
    next_y=y+1
    
    sum_x+=next_x
    sum_y+=next_y
    total_count+=1
    rect_cover_path=f"temp/primitive_rect_cover/primitive_{label}.txt"
    myfile=open(rect_cover_path,'w')
    minimum_x=start_x
    minimum_y=start_y
    maximum_x=start_x
    maximum_y=start_y
    myfile.write(f'{start_x} {start_y}\n')
    myfile.write(f'{next_x} {next_y}\n')
    minimum_x = min(minimum_x, next_x)
    minimum_y = min(minimum_y, next_y)
    maximum_x=max(maximum_x,next_x)
    maximum_y=max(maximum_y,next_y)
    while not(start_x==next_x and start_y==next_y):
        occ_type=get_type_of_point(my_image,next_y,next_x,height,width,label)
  
        direction=(direction+occ_type)%4
        if direction==-1:direction=3
        
        if direction==0: next_x+=1
        elif direction==1: next_y-=1
        elif direction==2: next_x-=1
        else : next_y+=1
        myfile.write(f'{next_x} {next_y}\n')
        sum_x+=next_x
        sum_y+=next_y
        total_count+=1
        minimum_x = min(minimum_x, next_x)
        minimum_y = min(minimum_y, next_y)
        maximum_x=max(maximum_x,next_x)
        maximum_y=max(maximum_y,next_y)
    myfile.write(f'{-2} {-2}\n')
    myfile.close()
    return sum_x,sum_y,total_count,rect_cover_path,minimum_x,minimum_y,maximum_x,maximum_y
    pass
import cv2
import numpy as np
import math

def make_rect_svg(height, width, image_file_path, primitive_data):
    
    svgfile=open('outputs/rect_cover.svg','w')
    canvas_w = width +  2
    canvas_h = height +  2

    svgfile.write(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="100%" height="100%" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" '
        f'preserveAspectRatio="xMidYMid meet">\n'
    )
    # svgfile.write(f'<image href="../{image_file_path}" x="{1}" y="{1}" width="{width}" height="{height}" />\n')

    for i in range(1, len(primitive_data)):
        points = []   # store primitive vertices here

        with open(primitive_data[i]["rect_cover_path"], "r") as cover_file:
            line = cover_file.readline()
            if not line:
                break
            x_str, y_str = line.strip().split()
            first_x, first_y = int(x_str), int(y_str)

            line = cover_file.readline()
            if not line:
                break
            x_str, y_str = line.strip().split()
            second_x, second_y = int(x_str), int(y_str)

            # collect points
            points.append([first_x, first_y])
            points.append([second_x, second_y])

            max_radius = math.sqrt((second_x - primitive_data[i]["center_x"])**2 +
                                   (second_y - primitive_data[i]["center_y"])**2)
            area_of_shape = 0.0

            for line in cover_file:
                svgfile.write(f'<line x1="{first_x+1}" y1="{first_y+1}" x2="{second_x+1}" y2="{second_y+1}" stroke="red" stroke-width="2"/>')

                # area calculation (shoelace method)
                area_of_shape += first_x * second_y - second_x * first_y

                first_x, first_y = second_x, second_y
                x_str, y_str = line.strip().split()
                second_x, second_y = int(x_str), int(y_str)

                if second_x == -2 and second_y == -2:
                    break

                # collect points
                points.append([second_x, second_y])

                # max radius calculation
                current_radius = math.sqrt((second_x - primitive_data[i]["center_x"])**2 +
                                           (second_y - primitive_data[i]["center_y"])**2)
                if max_radius < current_radius:
                    max_radius = current_radius

            # finalize features
            primitive_data[i]["radius"] = max_radius
            primitive_data[i]["area"] = abs(area_of_shape) / 2

            # ===== Convert to numpy contour =====
            contour = np.array(points, dtype=np.int32).reshape(-1,1,2)

            # Minimum enclosing circle
            (cx, cy), min_radius = cv2.minEnclosingCircle(contour)
            primitive_data[i]["min_circle"] = {"center": (cx, cy), "radius": min_radius}

            # Aspect ratio (from bounding rect)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h if h != 0 else 0
            primitive_data[i]["aspect_ratio"] = aspect_ratio

            # OR more rotation-invariant aspect ratio:
            rect = cv2.minAreaRect(contour)  # (center, (w,h), angle)
            w, h = rect[1]
            if h != 0:
                primitive_data[i]["rot_invariant_aspect_ratio"] = max(w, h) / min(w, h)
            else:
                primitive_data[i]["rot_invariant_aspect_ratio"] = 0

    # ===== Draw centers =====
    for i in range(1, len(primitive_data)):
        center_x = primitive_data[i]["center_x"]
        center_y = primitive_data[i]["center_y"]
        svgfile.write(f'<circle cx="{center_x+1}" cy="{center_y+1}" r="{3}" stroke="green" fill="green" />\n')
        svgfile.write(f'<text x="{center_x+2}" y="{center_y+2}" fill="black" font-size="20">{i}</text>')

    svgfile.write(f'<circle cx="{primitive_data[0]["center_x"]+1}" cy="{primitive_data[0]["center_y"]+1}" r="{3}" stroke="pink" fill="pink" />\n')
    svgfile.write('</svg>\n')
    svgfile.close()


def get_center_of_object(my_image,image_file_path):

    folder_path = 'temp/primitive_rect_cover'

    # Iterate through all files and folders in the directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # If it's a file or symbolic link, delete it
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        
        # If it's a folder, delete it and all its contents
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    folder_path = 'temp/primitive_ciruclar_cover'

    # Iterate through all files and folders in the directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # If it's a file or symbolic link, delete it
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        
        # If it's a folder, delete it and all its contents
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    my_map={}

    sum_x=0
    sum_y=0
    total_count=0
  
    height, width = my_image.shape
    primitive_data={}
    ## get the starting pixel location of each and every connected components
    start_loc={}
    for i in range(height):
        for j in range(width):
            if my_image[i,j]!=0:
                if my_image[i,j] not in start_loc:
                    start_loc[my_image[i,j]]=(i,j)
    
    for label, (y, x) in start_loc.items():


        temp_sum_x,temp_sum_y,temp_total_count,rect_cover_path,minimum_x,minimum_y,maximum_x,maximum_y=trace_rect_outer_cover(my_image,y-1,x-1,height,width,label)
        primitive_data[label]={"center_x":temp_sum_x//temp_total_count,"center_y":temp_sum_y//temp_total_count,"radius":0.0,"rect_cover_path":rect_cover_path,"center_distance":0.0,"encoding_length":0,"area":0.0,"minimum_x":minimum_x,"minimum_y":minimum_y,"maximum_x":maximum_x,"maximum_y":maximum_y}
        sum_x+=temp_sum_x
        sum_y+=temp_sum_y
        total_count+=temp_total_count
        pass


    if total_count==0:return -10, -10
    primitive_data[np.int32(0)]={"center_x":sum_x//total_count,"center_y":sum_y//total_count,"radius":0.0,"rect_cover_path":"","center_distance":0.0,"encoding_length":0}
    make_rect_svg(height,width,image_file_path,primitive_data)

    for i in range(1,len(primitive_data)):
        primitive_data[i]["center_distance"]=math.sqrt( ((primitive_data[0]["center_x"]-primitive_data[i]["center_x"])**2) + ((primitive_data[0]["center_y"]-primitive_data[i]["center_y"])**2))
    
    return primitive_data


    