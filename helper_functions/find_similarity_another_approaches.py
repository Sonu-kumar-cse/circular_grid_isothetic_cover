
def calculate_similarity(primitive_data, result_queue_for_lev_distance,height,width):
    n = len(primitive_data) - 1
    lev_matrix = np.zeros((n, n))

    center_diff = np.zeros((n,n))
    radius_diff = np.zeros((n,n))
    encoding_length_diff = np.zeros((n,n))

    while not result_queue_for_lev_distance.empty():
        i, j, lev_dist = result_queue_for_lev_distance.get()
        lev_matrix[i - 1][j - 1] = lev_dist
        lev_matrix[j - 1][i - 1] = lev_dist

        center_diff[i-1][j-1] = abs(primitive_data[i]['center_distance']-primitive_data[j]['center_distance'])
        center_diff[j-1][i-1] = abs(primitive_data[i]['center_distance']-primitive_data[j]['center_distance'])

        radius_diff[i-1][j-1]= abs(primitive_data[i]['radius']-primitive_data[j]['radius'])
        radius_diff[j-1][i-1]= abs(primitive_data[i]['radius']-primitive_data[j]['radius'])

        encoding_length_diff[i-1][j-1]= abs(primitive_data[i]['encoding_length']-primitive_data[j]['encoding_length'])
        encoding_length_diff[j-1][i-1]= abs(primitive_data[i]['encoding_length']-primitive_data[j]['encoding_length'])


    plot_point(lev_matrix)

    min_val = lev_matrix.min()
    max_val = lev_matrix.max()

    # Avoid division by zero
    if max_val > min_val:
        lev_matrix_normalized = (lev_matrix - min_val) / (max_val - min_val)
    else:
        lev_matrix_normalized = lev_matrix.copy()
    
    min_val=center_diff.min()
    max_val=center_diff.max()

    if max_val > min_val:
        center_diff = (center_diff - min_val) / (max_val - min_val)
    else:
        center_diff = center_diff.copy()
    
    min_val=radius_diff.min()
    max_val=radius_diff.max()

    if max_val > min_val:
        radius_diff = (radius_diff - min_val) / (max_val - min_val)
    else:
        radius_diff = radius_diff.copy()
    
    min_val=encoding_length_diff.min()
    max_val=encoding_length_diff.max()

    if max_val > min_val:
        encoding_length_diff = (encoding_length_diff - min_val) / (max_val - min_val)
    else:
        encoding_length_diff = encoding_length_diff.copy()
    
    

    center_distance = [primitive_data[i + 1]["center_distance"] for i in range(n)]
    alpha = 0.1
    beta = 0.6
    gamma= 0.2
    sigma=0.1

    combined_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                combined_matrix[i][j] = alpha * lev_matrix_normalized[i][j] + beta * center_diff[i][j] + gamma* radius_diff[i][j] + sigma*encoding_length_diff[i][j]

    best_labels = None
    best_clusters = {}
    max_cluster_count = 0

    for eps in [1,0.5,0.2,0.025,0.015,0.1,0.05,0.01,0.005,0.001]:
        for min_samples in [3,4,5,6,7]:
            db = DBSCAN(eps=eps, min_samples=min_samples, metric='precomputed')
            labels = db.fit_predict(combined_matrix)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            print(f"eps={eps}, min_samples={min_samples} -> Clusters formed: {n_clusters}")

            if n_clusters > max_cluster_count:
                max_cluster_count = n_clusters
                best_labels = labels


    final_clusters = {}
    for i, label in enumerate(best_labels):
        final_clusters.setdefault(label, []).append(i + 1)

    print("\nBest Clustering Result:")
    for label, members in final_clusters.items():
        print(f"Cluster {label}: {members}")
    make_rect_svg(height,width,primitive_data,final_clusters)


def calculate_gcd_value(primitive_data, result_queue_for_lev_distance, height, width, string_encodings):
    center_distance_array_temp = np.zeros(len(primitive_data) - 1)
    string_encodings_length_array_temp=np.zeros(len(string_encodings))
    for i in range(1, len(primitive_data)):
        center_distance_array_temp[i - 1] = primitive_data[i].get("center_distance", 0.0)
        string_encodings_length_array_temp[i-1]=len(string_encodings[i])

    # Plot on number line
    x_values = string_encodings_length_array_temp
    y_values = np.zeros_like(x_values)
    plt.figure(figsize=(12, 2))
    plt.scatter(x_values, y_values, color='blue')
    for idx, x in enumerate(x_values):
        plt.text(x, 0.01, str(idx + 1), ha='center', va='bottom', fontsize=7, rotation=90)
    plt.yticks([])
    plt.title("Center Distances (Index Labels)")
    plt.grid(True, axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

    center_distance_array_temp = center_distance_array_temp.reshape(-1, 1)
    string_encodings_length_array_temp = string_encodings_length_array_temp.reshape(-1,1)
    count_of_cluster_length={}

    for eps in [5,10]:
        for min_samples in [3,4,5]:
            db = DBSCAN(eps=eps, min_samples=min_samples)
            labels = db.fit_predict(center_distance_array_temp)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            print(f"eps={eps}, min_samples={min_samples} -> Clusters formed: {n_clusters}")

            final_clusters = {}
            for i, label in enumerate(labels):
                final_clusters.setdefault(label, []).append(i + 1)
            for label, members in final_clusters.items():
                count_of_cluster_length[len(members)] = count_of_cluster_length.get(len(members), 0) + 1

    for eps in [10,15,20]:
        for min_samples in [3,4,5]:
            db = DBSCAN(eps=eps, min_samples=min_samples)
            labels = db.fit_predict(string_encodings_length_array_temp)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            print(f"eps={eps}, min_samples={min_samples} -> Clusters formed: {n_clusters}")

            final_clusters = {}
            for i, label in enumerate(labels):
                final_clusters.setdefault(label, []).append(i + 1)
            for label, members in final_clusters.items():
                count_of_cluster_length[len(members)] = count_of_cluster_length.get(len(members), 0) + 1


    max_key=0
    max_number=0
    for key, values in count_of_cluster_length.items():
        if key==1: continue
        if max_number<values:
            max_number=values
            max_key=key


    print(count_of_cluster_length)
    print(max_key)
    return max_key
    pass

def test_similarity(primitive_data, result_queue_for_lev_distance, height, width, string_encodings):

    n = len(primitive_data) - 1
    lev_matrix = np.zeros((n, n))
    while not result_queue_for_lev_distance.empty():
        i, j, lev_dist = result_queue_for_lev_distance.get()
        lev_matrix[i - 1][j - 1] = lev_dist
        lev_matrix[j - 1][i - 1] = lev_dist

    plot_point(lev_matrix)


    gcd_value=calculate_gcd_value(primitive_data, result_queue_for_lev_distance, height, width, string_encodings)
    center_distance_array = np.zeros(len(primitive_data) - 1)
    for i in range(1, len(primitive_data)):
        center_distance_array[i - 1] = primitive_data[i].get("center_distance", 0.0)

    center_distance_array = center_distance_array.reshape(-1, 1)
    clusterer = DBSCAN(eps=10, min_samples=gcd_value) 
    labels = clusterer.fit_predict(center_distance_array)

    clusters_of_similar_center_distance = {}
    for index, label in enumerate(labels):
        clusters_of_similar_center_distance.setdefault(label, []).append(index + 1)

    final_cluster={}
    final_cluster_index=0
    for center_diff_label, center_diff_indices in clusters_of_similar_center_distance.items():
        print()
        print(f'for {center_diff_label} with values {center_diff_indices}')
        if(len(center_diff_indices)<=gcd_value):
            final_cluster[final_cluster_index]=center_diff_indices
            final_cluster_index+=1
            continue
       
        temp_encoding_len_array=np.zeros(len(center_diff_indices))
        temp_encoding_count=0
       
        for indices_value in center_diff_indices:
            temp_encoding_len_array[temp_encoding_count]=len(string_encodings[indices_value])
            temp_encoding_count+=1
        temp_encoding_len_array=temp_encoding_len_array.reshape(-1,1)
        
        clusterer = DBSCAN(eps=40, min_samples=gcd_value) 
        labels = clusterer.fit_predict(temp_encoding_len_array)
        
        clusters_of_similar_encoding_len = {}
        for encoding_len_index, encoding_len_label in enumerate(labels):
            clusters_of_similar_encoding_len.setdefault(encoding_len_label, []).append(clusters_of_similar_center_distance[center_diff_label][encoding_len_index])

        for encoding_len_label,encoding_len_indices in clusters_of_similar_encoding_len.items():
            final_cluster[final_cluster_index]=encoding_len_indices
            final_cluster_index+=1
                
    print()
    print()
    print(final_cluster)

        

    make_rect_svg(height,width,primitive_data,final_cluster)
    
    


    return
    # Plot on number line
    # x_values = center_distance_array
    # y_values = np.zeros_like(x_values)
    # plt.figure(figsize=(12, 2))
    # plt.scatter(x_values, y_values, color='blue')
    # for idx, x in enumerate(x_values):
    #     plt.text(x, 0.01, str(idx + 1), ha='center', va='bottom', fontsize=7, rotation=90)
    # plt.yticks([])
    # plt.title("Center Distances (Index Labels)")
    # plt.grid(True, axis='x', linestyle='--', alpha=0.5)
    # plt.tight_layout()
    # plt.show()

    # # Clustering with DBSCAN
    # center_distance_array = center_distance_array.reshape(-1, 1)
    # clusterer = DBSCAN(eps=10, min_samples=2)  # Try 25, 30, 35, etc.
    # labels = clusterer.fit_predict(center_distance_array)

    # clusters = {}
    # for index, label in enumerate(labels):
    #     clusters.setdefault(label, []).append(index + 1)

    # print("Clusters:")
    # for label, indices in clusters.items():
    #     print(f"Cluster {label}: Indices {indices}")
    # make_rect_svg(height,width,primitive_data,clusters)   

from collections import deque
import numpy as np
def test_similarity2(primitive_data, result_queue_for_lev_distance, height, width, string_encodings, alpha=0.2,
                     w1=0.3, w2=0.3, w3=0.4):

    n = len(primitive_data) - 1
    lev_matrix = np.zeros((n, n))

    # Fill Levenshtein distance matrix
    while not result_queue_for_lev_distance.empty():
        i, j, lev_dist = result_queue_for_lev_distance.get()
        lev_matrix[i - 1][j - 1] = lev_dist
        lev_matrix[j - 1][i - 1] = lev_dist

    # Extract radius & area features
    radii = np.array([primitive_data[i+1]["radius"] for i in range(n)])
    areas = np.array([primitive_data[i+1]["area"] for i in range(n)])

    # Normalize radius and area
    max_radius = np.max(radii) if np.max(radii) > 0 else 1
    max_area = np.max(areas) if np.max(areas) > 0 else 1
    radii = radii / max_radius
    areas = areas / max_area

    bool_array = np.zeros(n, dtype=bool)
    total_done_count = 0
    final_cluster = {}
    final_clustur_index = 0

    while total_done_count != n:

        # Step 1: find closest pair
        min_dist = float('inf')
        min_i, min_j = -1, -1
        for i in range(n):
            if bool_array[i]:
                continue
            for j in range(i + 1, n):
                if not bool_array[j]:
                    # composite distance
                    shape_dist = (
                        w1 * lev_matrix[i][j] +
                        w2 * abs(radii[i] - radii[j]) +
                        w3 * abs(areas[i] - areas[j])
                    )
                    if shape_dist < min_dist:
                        min_dist = shape_dist
                        min_i, min_j = i, j

        if min_i == -1:
            break

        # Step 2: initialize cluster
        final_cluster[final_clustur_index] = [min_i + 1, min_j + 1]
        bool_array[min_i] = True
        bool_array[min_j] = True
        total_done_count += 2

        avg_dist = min_dist
        q = deque([min_i, min_j])

        # Step 3: expand cluster
        while q:
            current_item = q.popleft()

            closest_dist = float('inf')
            closest_idx = -1

            for k in range(n):
                if not bool_array[k]:
                    shape_dist = (
                        w1 * lev_matrix[current_item][k] +
                        w2 * abs(radii[current_item] - radii[k]) +
                        w3 * abs(areas[current_item] - areas[k])
                    )
                    if shape_dist < closest_dist:
                        closest_dist = shape_dist
                        closest_idx = k

            if closest_idx != -1 and closest_dist <= 1.5 * avg_dist:
                final_cluster[final_clustur_index].append(closest_idx + 1)
                bool_array[closest_idx] = True
                total_done_count += 1

                num_items = len(final_cluster[final_clustur_index])
                avg_dist = ((avg_dist * (num_items - 2)) + closest_dist) / (num_items - 1)

                q.append(closest_idx)

        final_clustur_index += 1

    # Handle unclustered shapes
    final_cluster[final_clustur_index] = []
    for i in range(n):
        if not bool_array[i]:
            final_cluster[final_clustur_index].append(i+1)

    print(final_cluster)
    make_rect_svg(height, width, primitive_data, final_cluster)
    return


from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import numpy as np

def group_similar_primitive(primitive_data, result_queue_for_lev_distance, height, width, string_encodings):
    n = len(primitive_data) - 1  

    lev_matrix = np.zeros((n, n))
    while not result_queue_for_lev_distance.empty():
        i, j, lev_dist = result_queue_for_lev_distance.get()
        # max_len = max(len(string_encodings[i]), len(string_encodings[j]))
        # norm_lev = lev_dist / max_len if max_len > 0 else 0
        lev_matrix[i - 1][j - 1] = lev_dist
        lev_matrix[j - 1][i - 1] = lev_dist
    plot_point(lev_matrix)

    return 
    features = []
    for i in range(1, len(primitive_data)):
        p = primitive_data[i]
        encoding_len = len(string_encodings[i])
        features.append([
            p["area"],
            p["radius"],
            p["rot_invariant_aspect_ratio"],
            encoding_len,
            p["center_distance"]
        ])
    features = np.array(features)

    scaler = StandardScaler()
    norm_features = scaler.fit_transform(features)

    avg_lev = lev_matrix.mean(axis=1).reshape(-1, 1)  
    avg_lev = StandardScaler().fit_transform(avg_lev)

    weights = np.array([0.5, 2, 0.0, 0.5, 0.0])  # area, radius, aspect_ratio, encoding_len, distance_from_center
    weighted_features = norm_features * weights


    combined_features = np.hstack([weighted_features, avg_lev * 2.0])

    clustering = DBSCAN(eps=0.4, min_samples=3).fit(combined_features)
    labels = clustering.labels_

    final_clusters = {}
    for idx, label in enumerate(labels, start=1):
        if label not in final_clusters:
            final_clusters[label] = []
        final_clusters[label].append(idx)

    for i in range(1, len(primitive_data)):
        primitive_data[i]["cluster_id"] = int(labels[i-1])


    make_rect_svg(height, width, primitive_data, final_clusters)
    print(final_clusters)
    return primitive_data, final_clusters
