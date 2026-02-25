import math
import numpy as np
import random

def mark_ugb_array(center_x,center_y,radius_step,angle_step,labeled_image,label,UGB_array,height,width,total_circles,total_arc_per_circle):
    
    if 0<=center_x<width and 0<=center_y<height and labeled_image[center_y,center_x]==label:
        for i in range(total_arc_per_circle):
            UGB_array[0,i]=True
    else:
        for i in range(total_arc_per_circle):
            first_angle_degrees = i*angle_step
            first_angle_radians = math.radians(first_angle_degrees)
            second_angle_degrees = ((i+1)%total_arc_per_circle) * angle_step
            if second_angle_degrees==0:
                second_angle_degrees=360
            second_angle_radians = math.radians(second_angle_degrees)
            middle_angle_degrees =  (first_angle_degrees+second_angle_degrees)/2
            middle_angle_radians = math.radians(middle_angle_degrees)
            
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
            
            flag_inside=False
            for y in range(y_min,y_max+1):
                for x in range(x_min,x_max+1):
                    if x>=0 and y>=0 and x<width and y<height:
                        distance=np.sqrt((x - (center_x))**2 + (y - (center_y))**2)
                        curr_angle = np.arctan2(y - (center_y), x - (center_x))
                        curr_angle =curr_angle+ 2 * np.pi if curr_angle<0 else curr_angle # Normalize angles to [0, 2π)
                        curr_angle=np.degrees(curr_angle)
                        if 0<=math.ceil(distance) and math.floor(distance)<=radius_step:
                            if math.ceil(curr_angle)>=first_angle_degrees and math.floor(curr_angle)<=second_angle_degrees:
                                flag_inside=True
                                if labeled_image[y,x]==label:
                                    UGB_array[0,i]=True
            if flag_inside==False: 
                count_one=0
                count_zero=0
                for y in range(y_min,y_max+1):
                    for x in range(x_min,x_max+1):
                        if x>=0 and y>=0 and x<width and y<height:
                            if labeled_image[y,x]==label:count_one+=1
                            else : count_zero+=1
                if count_one>count_zero: UGB_array[0,i]=True

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
            flag_inside=False

            for y in range(y_min,y_max+1):
                for x in range(x_min,x_max+1):
                    if x>=0 and y>=0 and x<width and y<height:
                        distance=np.sqrt((x - (center_x))**2 + (y - (center_y))**2)
                        curr_angle = np.arctan2(y - (center_y), x - (center_x))
                        curr_angle =curr_angle+ 2 * np.pi if curr_angle<0 else curr_angle # Normalize angles to [0, 2π)
                        curr_angle=np.degrees(curr_angle)
                        if prev_radius<=math.ceil(distance) and math.floor(distance)<=curr_radius:
                            if math.ceil(curr_angle)>=first_angle_degrees and math.floor(curr_angle)<=second_angle_degrees:
                                flag_inside=True
                                if labeled_image[y,x]==label:
                                    UGB_array[i,j]=True
            if flag_inside==False: 
                count_one=0
                count_zero=0
                for y in range(y_min,y_max+1):
                    for x in range(x_min,x_max+1):
                        if x>=0 and y>=0 and x<width and y<height:
                            if labeled_image[y,x]==label:count_one+=1
                            else : count_zero+=1
                if count_one>count_zero: UGB_array[i,j]=True

            
    pass

def get_type(i,j,UGB_array,total_circles,total_arc_per_circle): 
    row,col=UGB_array.shape
    if i>=row: return 0
    temp_array=np.zeros(4)
    if(UGB_array[i][j]==True) : temp_array[0]=1
    if(j==0):
        if(UGB_array[i][total_arc_per_circle-1]==True) :temp_array[1]=1
        if i+1<total_circles : 
            if(UGB_array[i+1][total_arc_per_circle-1]==True) : temp_array[2]=1 
    else:
        if(UGB_array[i][j-1]==True): temp_array[1]=1
        if(i+1<total_circles):
            if(UGB_array[i+1][j-1]==True): temp_array[2]=1
    if i+1<total_circles and UGB_array[i+1][j]==True:
        temp_array[3]=1
    
    occ_count=0
    for i in range(4):
        if temp_array[i]==1:
            occ_count+=1
    
    if occ_count==1 : 
        if temp_array[0]==1: return 5
        return 1
    if occ_count==4 or occ_count==0 : return 0
    if occ_count==3 : 
        if temp_array[3]==0  : return 3
        else : return -1
        
    if (temp_array[0]==1 and temp_array[2]==1) or (temp_array[1]==1 and temp_array[3]==1): return -1
    # if temp_array[0]==1 and temp_array[1]==1: return 2

    return 0

## encodings
## 1 - 90 degree
## 2 - 180 degree
## 3 - 270 degree
## 4 - center

def trace_cover(i,j,visited,occ_type,total_arc_per_circle,UGB_array,total_circles,myfile):
    
    myfile.write(f'{i} {j}\n')
    direction=0
    start_i=i
    start_j=j
    next_i=i
    next_j=(j+1)%total_arc_per_circle
    myfile.write(f"{next_i} {next_j}\n")
    string_encoding=[]

    string_encoding.append('1')
    
    while not(start_i==next_i and start_j==next_j):
        
        if(next_i<0):
            string_encoding.append('4')
            temp_j=next_j
            temp_j-=1
            if temp_j==-1: temp_j=total_arc_per_circle-1
            while True:
                if UGB_array[0,temp_j]==False:
                    break
                visited[0,temp_j]=True
                temp_j-=1
                if temp_j==-1: temp_j=total_arc_per_circle-1
            next_i=0
            next_j=temp_j+1
            if next_j==total_arc_per_circle: next_j=0
            visited[0,next_j]=True
            direction=3
            # for i in range(next_j+1,total_arc_per_circle):
            #     if UGB_array[0,i]==True:
            #         next_i=0
            #         next_j=i
            #         direction=3
            #         break
            pass
        else:
            
            v_type=get_type(next_i,next_j,UGB_array,total_circles,total_arc_per_circle)
            if next_i>=total_circles or next_j>=total_arc_per_circle:break
            visited[next_i,next_j]=True
            if v_type==3: v_type=-1
            if v_type==2:v_type=0
            if v_type==5: v_type=1
            
            if v_type==1:string_encoding.append('1')
            elif v_type==0 : string_encoding.append('2')
            else : string_encoding.append('3')
            direction= (direction+v_type)%4
            if direction==-1: direction=3
            if direction==0:next_j=(next_j+1)%total_arc_per_circle
            elif direction==1: next_i=next_i-1
            elif direction==2: 
                if next_j==0: next_j=total_arc_per_circle-1
                else :next_j-=1
            else :
                next_i+=1
        
        myfile.write(f"{next_i} {next_j}\n")
    
    myfile.write(f"{-2} {-2}\n")
    return string_encoding
    


def make_circular_cover(center_x,center_y,radius,radius_step,angle_step,labeled_image,label,height,width):
    radius+=10
    total_circles=math.ceil(radius/radius_step)
    total_arc_per_circle=math.ceil(360/angle_step)
    
    UGB_array = np.full((total_circles, total_arc_per_circle), False, dtype=bool)
    
    
    mark_ugb_array(center_x,center_y,radius_step,angle_step,labeled_image,label,UGB_array,height,width,total_circles,total_arc_per_circle)
    


    visited = np.full((total_circles, total_arc_per_circle), False, dtype=bool)
    string_encoding=[] 
    myfile=open(f"temp/primitive_ciruclar_cover/primitive_{label}.txt","w")
    for i in range(total_circles-1,-1,-1):
        single_cover=False
        for j in range(total_arc_per_circle):
            if not visited[i,j]: 
                visited[i][j]=True
                occ_type=get_type(i,j,UGB_array,total_circles,total_arc_per_circle)
                if occ_type==5 :
                    string_encoding=trace_cover(i,j,visited,occ_type,total_arc_per_circle,UGB_array,total_circles,myfile)
                    single_cover=True
                    break
        if single_cover : break

    myfile.close()

    print(f'primitive_{label}-done')
    if len(string_encoding)!=0:
        random_k=random.randint(1,200)
        random_k=random_k%len(string_encoding)
        string_encoding=string_encoding[-random_k:] + string_encoding[:-random_k]
    return ''.join(string_encoding)*2