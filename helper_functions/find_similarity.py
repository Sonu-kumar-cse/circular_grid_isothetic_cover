import numpy as np
from collections import deque
import random
import math
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import queue
import hdbscan
import numpy as np
import numpy as np
import numpy as np
import os
import glob

def new_group_primitives(convex_hull_groups, remaining_indices, primitive_data, result_queue_for_lev_distance, height, width):
    """
    Subdivide convex_hull_groups based on Levenshtein distances between primitives.
    Subdivision only happens when a unique best offset (step) is found according to frequency voting.
    Votes count = min_group_length (one vote per base in 0..min_group_length-1).
    Offsets considered = num_offsets = max(1, len(current_group) // min_group_length).
    For each base i in [0..min_group_length-1], compare base -> base + offset*min_group_length for offset=1..num_offsets.
    """
    convex_hull_groups_copy = [group.copy() for group in convex_hull_groups]
    remaining_indices_copy = remaining_indices.copy()

    if not convex_hull_groups_copy:
        return convex_hull_groups_copy, remaining_indices_copy

    # Find minimum group length
    min_group_length = min(len(group) for group in convex_hull_groups_copy)
    print(f"\nMinimum group length = {min_group_length}")

    # Build Levenshtein distance matrix (assumes 1-based indices in queue items)
    n = len(primitive_data)
    lev_matrix = np.zeros((n, n))
    while not result_queue_for_lev_distance.empty():
        i, j, lev_dist = result_queue_for_lev_distance.get()
        lev_matrix[i - 1][j - 1] = lev_dist
        lev_matrix[j - 1][i - 1] = lev_dist  # symmetric

    # optional plotting
    try:
        plot_point(lev_matrix)
    except Exception:
        pass

    new_convex_hull_groups = []

    # Process each convex hull group
    for group in convex_hull_groups_copy:
        current_group = group.copy()

        if len(current_group) <= min_group_length:
            new_convex_hull_groups.append(current_group)
            continue

        print(f"\nProcessing group with {len(current_group)} elements: {current_group}")

        while len(current_group) > min_group_length:

            max_rotations = max(1, len(current_group) // min_group_length)
            found_valid_pattern = False
            rotation_count = 0

            # number of offset candidates for each base
            num_offsets = max(1, len(current_group) // min_group_length)

            while not found_valid_pattern and rotation_count < max_rotations:
                # votes for offsets 1..num_offsets, but we will have min_group_length voters
                current_frequency_of_min_distance = {offset: 0 for offset in range(1, num_offsets + 1)}

                # --- IMPORTANT FIX ---
                # One vote per base in 0..min_group_length-1 (so total votes = min_group_length)
                for base_pos in range(0, min_group_length):
                    # base element index (wrap around)
                    base_idx = current_group[base_pos % len(current_group)]

                    best_local_offset = None
                    best_local_lev = None

                    # Compare base to positions spaced by min_group_length: base_pos + offset*min_group_length
                    for offset in range(1, num_offsets + 1):
                        compare_pos = (base_pos + offset * min_group_length) % len(current_group)
                        compare_idx = current_group[compare_pos]
                        lev = lev_matrix[base_idx - 1][compare_idx - 1]

                        if best_local_lev is None or lev < best_local_lev:
                            best_local_lev = lev
                            best_local_offset = offset

                    if best_local_offset is not None:
                        current_frequency_of_min_distance[best_local_offset] += 1

                # Now check which offsets have the max votes
                freq_values = list(current_frequency_of_min_distance.values())
                max_freq = max(freq_values)
                best_offsets = [offset for offset, freq in current_frequency_of_min_distance.items() if freq == max_freq]

                print(f"Rotation {rotation_count}: freq={current_frequency_of_min_distance}")

                if len(best_offsets) == 1:
                    found_valid_pattern = True
                    best_match_position = best_offsets[0]
                    print(f" Unique best step size found: {best_match_position} (freq={max_freq})")
                else:
                    # ambiguous -> rotate left and retry
                    current_group = current_group[1:] + current_group[:1]
                    rotation_count += 1
                    print(f" Ambiguous pattern (multiple max freq={max_freq}) → rotating left → new group: {current_group}")

            # If still no valid subdivision pattern found after all rotations → keep whole group
            if not found_valid_pattern:
                print(f"⚠️ No unique best pattern found after {rotation_count} rotations → keeping group as is")
                new_convex_hull_groups.append(current_group)
                break

            # If found a pattern → create subgroup using the step (offset)
            step = best_match_position
            new_subgroup = current_group[::step]
            print(f"🧩 Step={step} → New subgroup: {new_subgroup}")

            # remove used elements
            remaining_after_subdivision = [x for x in current_group if x not in new_subgroup]

            # Store subgroup or move to remaining if too small
            if len(new_subgroup) >= min_group_length:
                new_convex_hull_groups.append(new_subgroup)
            else:
                remaining_indices_copy.extend(new_subgroup)
                print(f"Subgroup too small ({len(new_subgroup)} elements) → moved to remaining")

            # Update current_group to leftover and handle small leftovers immediately
            current_group = remaining_after_subdivision
            if 0 < len(current_group) < min_group_length:
                remaining_indices_copy.extend(current_group)
                print(f"Leftover too small ({len(current_group)} elements) → moved to remaining")
                break

        # After finishing subdivisions for this group, if leftover is still >= min_group_length, append it
        if len(current_group) >= min_group_length:
            new_convex_hull_groups.append(current_group)

    # Final summary
    print("\n--- After Subdivision ---")
    print(f"Total new groups: {len(new_convex_hull_groups)}")
    for i, g in enumerate(new_convex_hull_groups):
        print(f"  Group {i+1}: {g}")
    print(f"Remaining indices: {remaining_indices_copy}")

    final_clusters = {i: group for i, group in enumerate(new_convex_hull_groups)}
    if remaining_indices_copy:
        final_clusters["remaining"] = remaining_indices_copy

    # Try to create SVG if function exists
    try:
        make_rect_svg(height, width, primitive_data, final_clusters)
        print("\nSVG visualization saved to outputs/similar_primitive.svg ")
    except Exception as e:
        print(f" Error while creating SVG visualization: {e}")

    return new_convex_hull_groups, remaining_indices_copy

def recommended_colors(n):
    """
    Return up to n (n <= 15) visually distinct bright colors as hex strings.
    """
    base_colors = [
        (230, 25, 75),    # Bright Red
        (0, 130, 200),    # Strong Blue
        (245, 130, 48),   # Orange
        (60, 180, 75),    # Green
        (128, 0, 128),    # Purple (darker, distinct from Blue Violet)
        (64, 224, 208),   # Turquoise
        (0, 0, 128),      # Navy
        (255, 225, 25),   # Yellow
        (253,245,230),    # Cyan (instead of Blue Violet)
        (170, 110, 40),   # Brown
        (255, 0, 255),    # Magenta (more saturated than before)
        (220, 20, 60),    # Crimson
        (128, 128, 0),    # Olive
        (128, 128, 128),  # Gray
        (0, 0, 0),        # Black
    ]



    if n > 15:
        raise ValueError("n must be ≤ 15")
    return [f'#{r:02x}{g:02x}{b:02x}' for (r, g, b) in base_colors[:n]]

import os

def write_single_primitive_svg(primitive_info, color,label, pad=2):
    os.makedirs("outputs/primitive_found", exist_ok=True)

    min_x = primitive_info["minimum_x"]
    min_y = primitive_info["minimum_y"]
    max_x = primitive_info["maximum_x"]
    max_y = primitive_info["maximum_y"]
    path = primitive_info["rect_cover_path"]


    width = (max_x - min_x + 1) + 2 * pad
    height = (max_y - min_y + 1) + 2 * pad

    out_path = f"outputs/primitive_found/primitive_{label}.svg"

    svg = open(out_path, "w")
    svg.write(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="100%" height="100%">\n'
    )

    char_data = []

    with open(path, "r") as cover_file:
        line = cover_file.readline()
        if not line:
            return

        first_x, first_y = map(int, line.strip().split())

        line = cover_file.readline()
        if not line:
            return

        second_x, second_y = map(int, line.strip().split())

        for line in cover_file:
            # ✅ shift by min and add padding
            sx = (second_x - min_x) + pad
            sy = (second_y - min_y) + pad

            char_data.append(f"{sx},{sy} ")

            second_x, second_y = map(int, line.strip().split())
            if second_x == -2 and second_y == -2:
                break

        # close polygon
        fx = (first_x - min_x) + pad
        fy = (first_y - min_y) + pad
        char_data.append(f"{fx},{fy}")

    svg.write(
        f'<polygon points="{"".join(char_data)}" '
        f'fill="{color}" stroke="none"/>\n'
    )
    svg.write("</svg>")
    svg.close()



def make_rect_svg(height,width,primitive_data,final_clusters):
    svgfile=open('outputs/similar_primitive.svg','w')
    canvas_w = width  + 2
    canvas_h = height  + 2

    svgfile.write(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="100%" height="100%" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" '
        f'preserveAspectRatio="xMidYMid meet">\n'
    )

    os.makedirs("outputs/primitive_found", exist_ok=True)

    # ✅ remove all existing SVG files
    for file_path in glob.glob("outputs/primitive_found/*.svg"):
        try:
            os.remove(file_path)
        except OSError:
            pass
    colors=recommended_colors(len(final_clusters))
    color_index=-1
    for label, members in final_clusters.items():
        color_index+=1
        if members:
            rep_primitive = members[0]
            write_single_primitive_svg(
                primitive_data[rep_primitive],
                colors[color_index],
                color_index,
                pad=2
            )
        for ith_primitive in members:
            char_data=[]
            with open(primitive_data[ith_primitive]["rect_cover_path"],"r") as cover_file:
                line=cover_file.readline()
                if not line:
                    break
                first_x_str, first_y_str = line.strip().split()
                

                line=cover_file.readline()
                if not line:
                    break
                second_x_str, second_y_str = line.strip().split()
                second_x, second_y = int(second_x_str), int(second_y_str)


                for line in cover_file:
                    char_data.append(str(second_x+1))
                    char_data.append(",")
                    char_data.append(str(second_y+1))
                    char_data.append(" ")

                    second_x_str, second_y_str = line.strip().split()
                    second_x, second_y = int(second_x_str), int(second_y_str)
                    if second_x==-2 and second_y==-2 : break
                
                char_data.append(str(int(first_x_str)+1))
                char_data.append(",")
                char_data.append(str(int(first_y_str)+1))
                svgfile.write(f'<polygon points="{"".join(char_data)}" fill="{colors[color_index]}" stroke="none" stroke-width="0"/>')

                    
    svgfile.write('</svg>\n')
    svgfile.close()    

def plot_point(lev_matrix):
    n = lev_matrix.shape[0]

    with open("outputs/lev_distance.txt", "w") as f:
        # Optional: Write a header row with column indices
        f.write("\t" + "\t".join(str(j + 1) for j in range(n)) + "\n")
        
        for i in range(n):
            # Write the row index first
            row_values = "\t".join(f"{lev_matrix[i][j]:.2f}" for j in range(n))
            f.write(f"{i + 1}\t{row_values}\n")
