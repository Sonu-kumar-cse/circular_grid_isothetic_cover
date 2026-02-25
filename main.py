import cv2
import numpy as np
import math
import helper_functions.get_center as get_center
import helper_functions.bfs_traversal as bfs_traversal
import helper_functions.make_circular_cover as make_ciruclar_cover
import helper_functions.make_svg_file as make_svg
import helper_functions.levenshtien_distance as lev_dist
import helper_functions.find_similarity as find_similarity
import helper_functions.convex_hull as convex_hull
import threading
import queue
import Levenshtein
import time



result_queue_for_cover = queue.Queue()
def threaded_call_for_cover(i,primitive_data):
    try:
        result = make_ciruclar_cover.make_circular_cover(
            primitive_data[i]["center_x"],
            primitive_data[i]["center_y"],
            primitive_data[i]["radius"],
            radius_step,
            angle_step,
            labeled_image,
            i,
            image_height,
            image_width
        )
        result_queue_for_cover.put((i, result))
    except Exception as e:
        print('something woring')
        result_queue_for_cover.put((i, f"Error: {e}"))

result_queue_for_lev_distance=queue.Queue()
def threaded_levenshtein(i, j):
    try:
        temp_lev_distance = Levenshtein.distance(string_encodings[i], string_encodings[j])
        result_queue_for_lev_distance.put((i, j, temp_lev_distance))

    except Exception as e:
        print("somethinf adfasdfasdf")
        result_queue_for_lev_distance.put((i, j, f"Error: {e}"))



if __name__=="__main__":
    #take inputs
    start_time=time.time()

    global file_path
    file_path=input("Enter image path: ")
    
    global radius_step,angle_step
    radius_step=int(input("Enter the radius difference: "))
    angle_step=int(input("Enter angle steps: "))
    
    #make the image gray
    image = cv2.imread(file_path)
    global image_height,image_width
    image_height, image_width = image.shape[:2]
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('temp/grayscale.jpg', gray_image)

    #make binary image
    gray_image = cv2.imread('temp/grayscale.jpg', cv2.IMREAD_GRAYSCALE)
    global my_image
    my_image = (gray_image < 200).astype(np.uint8)  # 1 for <200, 0 otherwise
    
    ## labeling each connected components
    num_labels, labeled_image = cv2.connectedComponents(my_image, connectivity=8)
    
    ## caclcualte each primitive center radius etc.
    primitive_data=get_center.get_center_of_object(labeled_image,file_path)
    for i in range(len(primitive_data)):
        print(f"{i}: {primitive_data[i]}")

    

    filtered_data = []

    for i in range(len(primitive_data)):
        # Check if 'area' key exists and if its value is greater than 20
        if 'area' in primitive_data[i] and primitive_data[i]['area'] > 50:
            filtered_data.append({
                'index': i,
                'center_x': primitive_data[i]['center_x'],
                'center_y': primitive_data[i]['center_y']
            })

    # Print the filtered results
    for item in filtered_data:
        print(f"{item['index']}: center_x={item['center_x']}, center_y={item['center_y']}")

    convex_hull_groups, remaining_indices = convex_hull.group_indices_by_convex_hulls(filtered_data)
    print(f"\nFound {len(convex_hull_groups)} convex hull groups:")
    for i, group in enumerate(convex_hull_groups):
        print(f"Group {i}: {group}")

    if remaining_indices:
        print(f"\nRemaining indices: {remaining_indices}")
##################################################################################################################    
    # # calculate each primitive circular cover and their encodings
    threads = []
    for i in range(1, len(primitive_data)):
        t = threading.Thread(target=threaded_call_for_cover, args=(i,primitive_data))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    global string_encodings
    string_encodings = [None] * len(primitive_data)
    while not result_queue_for_cover.empty():
        idx, value = result_queue_for_cover.get()
        string_encodings[idx] = value
        primitive_data[idx]["encoding_length"]=len(value)


    for i, str_encode in enumerate(string_encodings):
        if str_encode:  # skips None and empty strings
            print(f"Index {i}: Length = {len(str_encode)}")
        else:
            print(f"Index {i}: Empty or None")

    total_arc_per_circle=math.ceil(360/angle_step)
    make_svg.make_ciruclar_svg("outputs/seperate_primitive.svg",file_path,primitive_data,radius_step,total_arc_per_circle,angle_step,image_width,image_height)

    print("calculating lev distance")
    thread_lev=[]
    for i in range(1, len(primitive_data)):
        for j in range(i + 1, len(primitive_data)):
            t = threading.Thread(target=threaded_levenshtein, args=(i, j))
            thread_lev.append(t)
            t.start()
    

    for t in thread_lev:
        t.join()


    print("calculating similarity")
    find_similarity.new_group_primitives(convex_hull_groups,remaining_indices,primitive_data,result_queue_for_lev_distance,image_height,image_width)
    end_time = time.time()

    print(f"Total time taken: {end_time - start_time:.4f} seconds")
    









   
    # find_similarity.group_similar_primitive(primitive_data,result_queue_for_lev_distance,image_height,image_width,string_encodings)
#     # # find_similarity.calculate_similarity(primitive_data,result_queue_for_lev_distance,image_height,image_width)






# ##################################################################################################################



#     # print(image_width//2,image_height//2)
#     # print(num_labels)
#     # center_x=primitive_data[0]["center_x"]
#     # center_y=primitive_data[0]["center_y"]
#     # center_x+=10
#     # center_y+=10
#     # a=math.ceil(np.sqrt((center_x)*(center_x)+(center_y)*(center_y)))
#     # b=math.ceil(np.sqrt((center_x-image_width-20)*(center_x-image_width-20)+(center_y)*(center_y)))
#     # c=math.ceil(np.sqrt((center_x)*(center_x)+(center_y-image_height-20)*(center_y-image_height-20)))
#     # d=math.ceil(np.sqrt((center_x-image_width-20)*(center_x-image_width-20)+(center_y-image_height-20)*(center_y-image_height-20)))
#     # max_radius=max([a,b,c,d])

#     # print(a,b,c,d)
#     # print(max_radius)
#     # print(f'cener_x={center_x} center_y={center_y}')
#     # print(f'image width={image_width} height={image_height}')
#     # global total_circles,total_arcs_per_circle
#     # total_circles=math.ceil(max_radius/radius_step)
#     # total_arc_per_circle=math.ceil(360/angle_step)



#     # global UGB_array
#     # UGB_array = np.full((total_circles, total_arc_per_circle), False, dtype=bool)



#     # print(total_circles)
#     # print(total_arc_per_circle)
    
#     # ugb_occupancy_marker()
#     # make_outer_cover()
#     # create_svg_file('outputs/output.svg',total_circles,radius_step)
#     # print(UGB_array)


