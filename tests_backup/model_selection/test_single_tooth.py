import json
import numpy as np
import open3d as o3d

OBJ_PATH = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.obj"
JSON_PATH = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.json"

# --------------------------------------------------
# Select tooth
# Instance 10 = FDI 11 according to your JSON
# --------------------------------------------------

TARGET_INSTANCE = 10

# --------------------------------------------------
# Load original mesh
# --------------------------------------------------

mesh = o3d.io.read_triangle_mesh(OBJ_PATH)

vertices = np.asarray(mesh.vertices)

# --------------------------------------------------
# Load JSON
# --------------------------------------------------

with open(JSON_PATH, "r") as f:
    data = json.load(f)

instances = np.array(data["instances"])
labels = np.array(data["labels"])

# --------------------------------------------------
# Get vertices for selected tooth
# --------------------------------------------------

indices = np.where(instances == TARGET_INSTANCE)[0]

tooth_vertices = vertices[indices]

tooth_label = np.unique(labels[indices])

print("Instance:", TARGET_INSTANCE)
print("FDI label:", tooth_label)
print("Number of vertices:", len(tooth_vertices))

# --------------------------------------------------
# Create point cloud
# --------------------------------------------------

pcd = o3d.geometry.PointCloud()

pcd.points = o3d.utility.Vector3dVector(
    tooth_vertices
)

# Single color
pcd.paint_uniform_color([0.8, 0.8, 0.8])

# --------------------------------------------------
# Estimate normals
# --------------------------------------------------

pcd.estimate_normals(
    search_param=o3d.geometry.KDTreeSearchParamHybrid(
        radius=0.5,
        max_nn=30
    )
)

# --------------------------------------------------
# Visualize
# --------------------------------------------------

o3d.visualization.draw_geometries(
    [pcd],
    window_name="Single Tooth - FDI 11"
)