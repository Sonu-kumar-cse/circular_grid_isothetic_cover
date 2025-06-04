import numpy as np

def get_type_of_point(binary_image,y,x,height,width):

    temp_array=np.zeros(4)
    if x>=0 and x<width and y>=0 and y<height and binary_image[y,x]==0:
        temp_array[0]=temp_array[1]=temp_array[2]=temp_array[3]=1
    if x+1<width and y>=0 and y<height and binary_image[y,x+1]==0:
        temp_array[0]=temp_array[1]=1
    if x-1>=0 and y>=0 and y<height and binary_image[y,x-1]==0:
        temp_array[2]=temp_array[3]=1
    if y+1<height and x>=0 and x<width and binary_image[y+1,x]==0:
        temp_array[0]=temp_array[3]=1
    if y-1>=0 and x>=0 and x<width and binary_image[y-1,x]==0:
        temp_array[1]=temp_array[2]=1
    if x+1<width and y+1<height and binary_image[y+1,x+1]==0:
        temp_array[0]=1
    if x+1<width and y-1>=0 and binary_image[y-1,x+1]==0:
        temp_array[1]=1
    if x-1>=0 and y-1>=0 and binary_image[y-1,x-1]==0:
        temp_array[2]=1
    if x-1>=0 and y+1<height and binary_image[y+1,x-1]==0:
        temp_array[3]=1

    ugb_count=0
    for i in range(4):
        if temp_array[i]==1: ugb_count+=1
    
    if ugb_count==1:
        if temp_array[0]==1:return 5
        return 1
    if ugb_count==2:
        if (temp_array[1]==1 and temp_array[3]==1) or (temp_array[0]==1 and temp_array[2]==1): return -1
        return 0
    if ugb_count==3: return -1
    return 0
        
def trace_rect_outer_cover(binary_image,y,x,visited,height,width,sum_x,sum_y,total_count):
    print("inside trace")
    direction=3
    start_x=x
    start_y=y
    next_x=x
    next_y=y+1
    
    sum_x+=next_x
    sum_y+=next_y
    total_count+=1
 
    myfile.write(f'{start_x} {start_y}\n')
    myfile.write(f'{next_x} {next_y}\n')

    while not(start_x==next_x and start_y==next_y):
        visited[next_y+1,next_x+1]=True
        occ_type=get_type_of_point(binary_image,next_y,next_x,height,width)
        if occ_type==5: occ_type=1
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

        
    myfile.write(f'{-2} {-2}\n')
    return sum_x,sum_y,total_count
    pass

def make_rect_svg(height,width,sum_x,sum_y,total_count):
    svgfile=open('outputs/rect_cover.svg','w')
    datafile=open('outputs/rect_data.txt','r')
    svgfile.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width+2}" height="{height+2}">\n')
    

    while True:
            line=datafile.readline()
            if not line:
                break
            x_str, y_str = line.strip().split()
            first_x, first_y = int(x_str), int(y_str)

            line=datafile.readline()
            if not line:
                break
            x_str, y_str = line.strip().split()
            second_x, second_y = int(x_str), int(y_str)
            

            while True:
                
                svgfile.write(f'<line x1="{first_x+1}" y1="{first_y+1}" x2="{second_x+1}" y2="{second_y+1}" stroke="red" stroke-width="2"/>')
                
                first_x=second_x
                first_y=second_y
                line=datafile.readline()
                if not line:
                    break
                x_str, y_str = line.strip().split()
                second_x, second_y = int(x_str), int(y_str)
                if second_x==-2 and second_y==-2 : break
    
    if total_count!=0:
        svgfile.write(f'  <circle cx="{(sum_x//total_count)+1}" cy="{(sum_y//total_count)+1}" r="{5}" stroke="green" fill="green" stroke-width="0.5" />\n')

    svgfile.write('</svg>\n')
    datafile.close()
    svgfile.close()    

def get_center_of_object(binary_image):
    print('inisde get_center')
    global myfile
    sum_x=0
    sum_y=0
    total_count=0
    myfile= open('outputs/rect_data.txt','w')
    height, width = binary_image.shape
    visited = np.full((height+2, width+2), False, dtype=bool)
    for i in range(-1,height+1,1):
        for j in range(-1,width+1,1):
            if visited[i+1,j+1]==False:
                visited[i+1,j+1]=True
                v_type=get_type_of_point(binary_image,i,j,height,width)
                # image_value=1
                # if(i>=0 and i<height and j>=0 and j<width):image_value=binary_image[i,j]
                # print(f'{i,j} type={v_type} image-value={image_value}')
                if v_type==5:
                    temp_sum_x,temp_sum_y,temp_total_conut=trace_rect_outer_cover(binary_image,i,j,visited,height,width,0,0,0)
                    sum_x+=temp_sum_x
                    sum_y+=temp_sum_y
                    total_count+=temp_total_conut
    myfile.close()
    make_rect_svg(height,width,sum_x,sum_y,total_count)
    if total_count==0: return -5,-5

    return sum_x//total_count,sum_y//total_count