import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import squareform
from collections import defaultdict

# Sample input (replace these with actual data)
n = 6
string_encodings = ['abc', 'abd', 'xyz', 'xzz', 'acd', 'xbc']
radii = np.array([1.0, 1.1, 3.5, 3.7, 0.9, 3.6])
distances = np.array([10.0, 11.0, 50.0, 52.0, 9.5, 49.0])

# Levenshtein distance matrix (n x n) - this is just an example
from Levenshtein import distance as lev
lev_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        if i != j:
            lev_matrix[i][j] = lev(string_encodings[i], string_encodings[j])

# Step 1: Normalize radius and distance features
scaler = MinMaxScaler()
radius_scaled = scaler.fit_transform(radii.reshape(-1, 1)).flatten()
dist_scaled = scaler.fit_transform(distances.reshape(-1, 1)).flatten()

# Step 2: Compute full combined distance matrix
combined_distance = np.zeros((n, n))
α, β, γ = 1.0, 1.0, 1.0  # weights: you can tune them

# Normalize Levenshtein distances
lev_matrix = lev_matrix / np.max(lev_matrix)

for i in range(n):
    for j in range(n):
        if i != j:
            r_diff = abs(radius_scaled[i] - radius_scaled[j])
            d_diff = abs(dist_scaled[i] - dist_scaled[j])
            combined_distance[i][j] = α * lev_matrix[i][j] + β * r_diff + γ * d_diff

# Step 3: Apply Agglomerative Clustering
model = AgglomerativeClustering(
    affinity='precomputed',
    linkage='average',
    distance_threshold=0.8,  # you can tune this
    n_clusters=None
)

labels = model.fit_predict(combined_distance)
print("Initial labels:", labels)

# Step 4: Group objects by initial cluster labels
def group_by_labels(labels):
    clusters = defaultdict(list)
    for idx, label in enumerate(labels):
        clusters[label].append(idx)
    return list(clusters.values())

clusters = group_by_labels(labels)

# Step 5: Enforce GCD constraint
def is_gcd_compatible(len_a, len_b):
    g = math.gcd(len_a, len_b)
    return len_a == g or len_b == g

def enforce_gcd_constraint(clusters):
    changed = True
    while changed:
        changed = False
        new_clusters = []
        merged = [False] * len(clusters)

        for i in range(len(clusters)):
            if merged[i]:
                continue
            for j in range(i + 1, len(clusters)):
                if merged[j]:
                    continue
                if not is_gcd_compatible(len(clusters[i]), len(clusters[j])):
                    # merge clusters
                    merged[i] = merged[j] = True
                    new_clusters.append(clusters[i] + clusters[j])
                    changed = True
                    break
            if not merged[i]:
                new_clusters.append(clusters[i])

        clusters = new_clusters

    return clusters

final_clusters = enforce_gcd_constraint(clusters)

# Step 6: Display final clusters
for i, cluster in enumerate(final_clusters):
    print(f"Cluster {i+1}: {[string_encodings[idx] for idx in cluster]} (size: {len(cluster)})")
