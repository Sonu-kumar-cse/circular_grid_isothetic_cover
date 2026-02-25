import math
import numpy as np
import random


def mark_ugb_array(center_x, center_y, radius_step, angle_step,
                   labeled_image, label, UGB_array,
                   height, width, total_circles, total_arc_per_circle):

    img = labeled_image
    lbl = label
    cx = center_x
    cy = center_y

    angles_deg = [i * angle_step for i in range(total_arc_per_circle)]
    angles_rad = [math.radians(a) for a in angles_deg]
    sin_vals = [math.sin(a) for a in angles_rad]
    cos_vals = [math.cos(a) for a in angles_rad]

    # ---- Circle 0 ----
    if 0 <= cx < width and 0 <= cy < height and img[cy, cx] == lbl:
        UGB_array[0, :] = True
    else:
        for j in range(total_arc_per_circle):
            a1 = angles_deg[j]
            a2 = angles_deg[(j + 1) % total_arc_per_circle] or 360
            am = (a1 + a2) * 0.5

            r = radius_step

            x1 = cx + r * cos_vals[j]
            y1 = cy + r * sin_vals[j]
            x2 = cx + r * math.cos(math.radians(a2))
            y2 = cy + r * math.sin(math.radians(a2))
            x3 = cx + r * math.cos(math.radians(am))
            y3 = cy + r * math.sin(math.radians(am))

            x_min = max(0, int(min(x1, x2, x3, cx)))
            y_min = max(0, int(min(y1, y2, y3, cy)))
            x_max = min(width - 1, int(max(x1, x2, x3, cx)))
            y_max = min(height - 1, int(max(y1, y2, y3, cy)))

            flag_inside = False
            r_sq = r * r

            for y in range(y_min, y_max + 1):
                dy = y - cy
                for x in range(x_min, x_max + 1):
                    dx = x - cx
                    dist_sq = dx * dx + dy * dy
                    if dist_sq <= r_sq:
                        ang = math.degrees(math.atan2(dy, dx))
                        if ang < 0:
                            ang += 360
                        if a1 <= ang <= a2:
                            flag_inside = True
                            if img[y, x] == lbl:
                                UGB_array[0, j] = True
                                break
                if UGB_array[0, j]:
                    break

            if not flag_inside:
                count_one = count_zero = 0
                for y in range(y_min, y_max + 1):
                    for x in range(x_min, x_max + 1):
                        if img[y, x] == lbl:
                            count_one += 1
                        else:
                            count_zero += 1
                if count_one > count_zero:
                    UGB_array[0, j] = True

    # ---- Remaining circles ----
    for i in range(1, total_circles):
        prev_r = i * radius_step
        curr_r = prev_r + radius_step
        prev_r_sq = prev_r * prev_r
        curr_r_sq = curr_r * curr_r

        for j in range(total_arc_per_circle):
            a1 = angles_deg[j]
            a2 = angles_deg[(j + 1) % total_arc_per_circle] or 360
            am = (a1 + a2) * 0.5

            x1 = cx + prev_r * cos_vals[j]
            y1 = cy + prev_r * sin_vals[j]
            x2 = cx + curr_r * cos_vals[j]
            y2 = cy + curr_r * sin_vals[j]
            x3 = cx + prev_r * math.cos(math.radians(a2))
            y3 = cy + prev_r * math.sin(math.radians(a2))
            x4 = cx + curr_r * math.cos(math.radians(a2))
            y4 = cy + curr_r * math.sin(math.radians(a2))
            x5 = cx + curr_r * math.cos(math.radians(am))
            y5 = cy + curr_r * math.sin(math.radians(am))

            x_min = max(0, int(min(x1, x2, x3, x4, x5)))
            y_min = max(0, int(min(y1, y2, y3, y4, y5)))
            x_max = min(width - 1, int(max(x1, x2, x3, x4, x5)))
            y_max = min(height - 1, int(max(y1, y2, y3, y4, y5)))

            flag_inside = False

            for y in range(y_min, y_max + 1):
                dy = y - cy
                for x in range(x_min, x_max + 1):
                    dx = x - cx
                    dist_sq = dx * dx + dy * dy
                    if prev_r_sq <= dist_sq <= curr_r_sq:
                        ang = math.degrees(math.atan2(dy, dx))
                        if ang < 0:
                            ang += 360
                        if a1 <= ang <= a2:
                            flag_inside = True
                            if img[y, x] == lbl:
                                UGB_array[i, j] = True
                                break
                if UGB_array[i, j]:
                    break

            if not flag_inside:
                count_one = count_zero = 0
                for y in range(y_min, y_max + 1):
                    for x in range(x_min, x_max + 1):
                        if img[y, x] == lbl:
                            count_one += 1
                        else:
                            count_zero += 1
                if count_one > count_zero:
                    UGB_array[i, j] = True


def get_type(i, j, UGB_array, total_circles, total_arc_per_circle):
    if i >= total_circles:
        return 0

    t0 = UGB_array[i, j]
    t1 = UGB_array[i, j - 1] if j > 0 else UGB_array[i, total_arc_per_circle - 1]
    t2 = UGB_array[i + 1, j - 1] if (i + 1 < total_circles and j > 0) else \
         (UGB_array[i + 1, total_arc_per_circle - 1] if i + 1 < total_circles else False)
    t3 = UGB_array[i + 1, j] if i + 1 < total_circles else False

    occ = t0 + t1 + t2 + t3

    if occ == 1:
        return 5 if t0 else 1
    if occ == 0 or occ == 4:
        return 0
    if occ == 3:
        return 3 if not t3 else -1
    if (t0 and t2) or (t1 and t3):
        return -1
    return 0


def trace_cover(i, j, visited, occ_type,
                total_arc_per_circle, UGB_array, total_circles, myfile):

    myfile.write(f"{i} {j}\n")
    start_i, start_j = i, j
    next_i = i
    next_j = (j + 1) % total_arc_per_circle
    myfile.write(f"{next_i} {next_j}\n")

    direction = 0
    string_encoding = ['1']

    while not (start_i == next_i and start_j == next_j):
        if next_i < 0:
            string_encoding.append('4')
            temp_j = (next_j - 1) % total_arc_per_circle
            while UGB_array[0, temp_j]:
                visited[0, temp_j] = True
                temp_j = (temp_j - 1) % total_arc_per_circle
            next_i = 0
            next_j = (temp_j + 1) % total_arc_per_circle
            visited[0, next_j] = True
            direction = 3
        else:
            visited[next_i, next_j] = True
            v = get_type(next_i, next_j, UGB_array, total_circles, total_arc_per_circle)
            if v == 3:
                v = -1
            elif v == 2:
                v = 0
            elif v == 5:
                v = 1

            string_encoding.append('1' if v == 1 else '2' if v == 0 else '3')
            direction = (direction + v) % 4

            if direction == 0:
                next_j = (next_j + 1) % total_arc_per_circle
            elif direction == 1:
                next_i -= 1
            elif direction == 2:
                next_j = (next_j - 1) % total_arc_per_circle
            else:
                next_i += 1

        myfile.write(f"{next_i} {next_j}\n")

    myfile.write("-2 -2\n")
    return string_encoding


def make_circular_cover(center_x, center_y, radius,
                        radius_step, angle_step,
                        labeled_image, label, height, width):

    radius += 10
    total_circles = math.ceil(radius / radius_step)
    total_arc_per_circle = math.ceil(360 / angle_step)

    UGB_array = np.zeros((total_circles, total_arc_per_circle), dtype=bool)

    mark_ugb_array(center_x, center_y, radius_step, angle_step,
                   labeled_image, label, UGB_array,
                   height, width, total_circles, total_arc_per_circle)

    visited = np.zeros_like(UGB_array, dtype=bool)
    string_encoding = []

    with open(f"temp/primitive_ciruclar_cover/primitive_{label}.txt", "w") as myfile:
        for i in range(total_circles - 1, -1, -1):
            for j in range(total_arc_per_circle):
                if not visited[i, j]:
                    visited[i, j] = True
                    if get_type(i, j, UGB_array, total_circles, total_arc_per_circle) == 5:
                        string_encoding = trace_cover(
                            i, j, visited, 5,
                            total_arc_per_circle, UGB_array, total_circles, myfile
                        )
                        break
            if string_encoding:
                break

    print(f"primitive_{label}-done")

    if string_encoding:
        k = random.randint(1, 200) % len(string_encoding)
        string_encoding = string_encoding[-k:] + string_encoding[:-k]

    return ''.join(string_encoding) * 2
