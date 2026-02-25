from scipy.spatial import ConvexHull
import numpy as np

def group_indices_by_convex_hulls(filtered_data):
    """
    Groups point indices by iteratively finding convex hulls.
    
    Args:
        filtered_data: List of dictionaries with 'index', 'center_x', and 'center_y'
        
    Returns:
        tuple: (convex_hull_groups, remaining_indices)
        - convex_hull_groups: List of lists, each containing indices of hull points
        - remaining_indices: Indices that couldn't form a convex hull (<3 points)
    """
    convex_hull_groups = []
    remaining_data = filtered_data.copy()
    
    while len(remaining_data) >= 3:
        points = []
        index_mapping = []
        
        for item in remaining_data:
            points.append([item['center_x'], item['center_y']])
            index_mapping.append(item['index'])
        
        points_array = np.array(points)
        
        try:
            hull = ConvexHull(points_array)
            hull_indices = [index_mapping[i] for i in hull.vertices]
            
            convex_hull_groups.append(hull_indices)
            remaining_data = [item for item in remaining_data if item['index'] not in hull_indices]
            
            print(f"Group {len(convex_hull_groups)-1}: {len(hull_indices)} points")
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    remaining_indices = [item['index'] for item in remaining_data]
    return convex_hull_groups, remaining_indices