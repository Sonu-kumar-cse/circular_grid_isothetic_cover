import numpy as np
from collections import deque
def do_bfs(my_image,i,j,height,width,primitive_number):
    queue = deque()
    queue.append((i,j))
    while len(queue)!=0:
        y,x= queue.popleft()
        my_image[y,x]=primitive_number
        if y-1>=0 and my_image[y-1,x]==0: queue.append((y-1,x))
        if y+1<height and my_image[y+1,x]==0: queue.append((y+1,x))
        if x-1>=0 and my_image[y,x-1]==0: queue.append((y,x-1))
        if x+1<width and my_image[y,x+1]==0: queue.append((y,x+1))
        pass
    pass

def seperate_primitives(my_image):
    height, width = my_image.shape
    primitive_number=2
    for i in range(height):
        for j in range(width):
            if my_image[i,j]==0:
                do_bfs(my_image,i,j,height,width,primitive_number)
                primitive_number+=1
    pass