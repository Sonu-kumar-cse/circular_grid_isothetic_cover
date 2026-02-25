import cv2
import numpy as np
import math
import os
import queue
from concurrent.futures import ProcessPoolExecutor, as_completed
import Levenshtein
import time

import helper_functions.get_center as get_center
import helper_functions.bfs_traversal as bfs_traversal
import helper_functions.make_circular_cover as make_ciruclar_cover_opt
import helper_functions.make_svg_file as make_svg
import helper_functions.levenshtien_distance as lev_dist
import helper_functions.find_similarity as find_similarity
import helper_functions.convex_hull as convex_hull


# ---------------- WORKERS ----------------
def cover_worker(args):
    i, primitive_data, radius_step, angle_step, labeled_image, image_height, image_width = args
    result = make_ciruclar_cover_opt.make_circular_cover(
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
    return i, result


def levenshtein_worker(args):
    i, j, string_encodings = args
    dist = Levenshtein.distance(string_encodings[i], string_encodings[j])
    return i, j, dist


# ================= MAIN PIPELINE FUNCTION =================
def run_pipeline(file_path, radius_step, angle_step):
    start_time = time.time()

    os.makedirs("outputs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    # ---------------- IMAGE PREPROCESSING ----------------
    image = cv2.imread(file_path)
    image_height, image_width = image.shape[:2]

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('temp/grayscale.jpg', gray_image)

    gray_image = cv2.imread('temp/grayscale.jpg', cv2.IMREAD_GRAYSCALE)
    my_image = (gray_image < 200).astype(np.uint8)

    num_labels, labeled_image = cv2.connectedComponents(my_image, connectivity=8)

    # ---------------- PRIMITIVE DATA ----------------
    primitive_data = get_center.get_center_of_object(labeled_image, file_path)

    # ---------------- FILTER SMALL OBJECTS ----------------
    filtered_data = []
    for i in range(len(primitive_data)):
        if 'area' in primitive_data[i] and primitive_data[i]['area'] > 50:
            filtered_data.append({
                'index': i,
                'center_x': primitive_data[i]['center_x'],
                'center_y': primitive_data[i]['center_y']
            })

    # ---------------- CONVEX HULL GROUPING ----------------
    convex_hull_groups, remaining_indices = convex_hull.group_indices_by_convex_hulls(filtered_data)

    string_encodings = [None] * len(primitive_data)

    cover_tasks = [
        (i, primitive_data, radius_step, angle_step, labeled_image, image_height, image_width)
        for i in range(1, len(primitive_data))
    ]

    workers = min(os.cpu_count(), 8)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(cover_worker, t) for t in cover_tasks]

        for f in as_completed(futures):
            idx, value = f.result()
            string_encodings[idx] = value
            primitive_data[idx]["encoding_length"] = len(value)

    total_arc_per_circle = math.ceil(360 / angle_step)

    # ✅ FINAL SVG PATH
    output_svg_path = "outputs/seperate_primitive.svg"

    make_svg.make_ciruclar_svg(
        output_svg_path,
        file_path,
        primitive_data,
        radius_step,
        total_arc_per_circle,
        angle_step,
        image_width,
        image_height
    )

    # ---------------- LEVENSHTEIN ----------------
    lev_tasks = []
    for i in range(1, len(primitive_data)):
        for j in range(i + 1, len(primitive_data)):
            lev_tasks.append((i, j, string_encodings))

    lev_results = []

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(levenshtein_worker, t) for t in lev_tasks]
        for f in as_completed(futures):
            lev_results.append(f.result())

    result_queue_for_lev_distance = queue.Queue()
    for i, j, dist in lev_results:
        result_queue_for_lev_distance.put((i, j, dist))

    find_similarity.new_group_primitives(
        convex_hull_groups,
        remaining_indices,
        primitive_data,
        result_queue_for_lev_distance,
        image_height,
        image_width
    )

    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.4f} seconds")


    