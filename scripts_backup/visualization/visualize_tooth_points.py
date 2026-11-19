import json
import numpy as np
import open3d as o3d

OBJ_PATH = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.obj"
JSON_PATH = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.json"

# Load mesh
mesh = o3d.io.read_triangle_mesh(OBJ_PATH)

vertices = np.asarray(mesh.vertices)

# Load JSON
with open(JSON_PATH, "r") as f:
    data = json.load(f)

instances = np.array(data["instances"])
labels = np.array(data["labels"])

# ---------------------------------------------------------
# Create point clouds for each tooth
# ---------------------------------------------------------

geometries = []

for instance_id in sorted(np.unique(instances)):

    # Skip gingiva
    if instance_id == 0:
        continue

    # Vertices belonging to this tooth
    indices = np.where(instances == instance_id)[0]

    tooth_points = vertices[indices]

    # Find FDI label
    tooth_labels = labels[indices]
    tooth_labels = tooth_labels[tooth_labels != 0]

    if len(tooth_labels) == 0:
        continue

    tooth_number = np.bincount(tooth_labels).argmax()

    print(
        f"Instance {instance_id} "
        f"-> Tooth {tooth_number} "
        f"-> {len(tooth_points)} points"
    )

    # Create point cloud
    pcd = o3d.geometry.PointCloud()

    pcd.points = o3d.utility.Vector3dVector(
        tooth_points
    )

    # Give each tooth a simple color
    color = np.random.rand(3)

    pcd.paint_uniform_color(color)

    geometries.append(pcd)


# ---------------------------------------------------------
# Visualize
# ---------------------------------------------------------

print("\nOpening tooth point clouds...")

o3d.visualization.draw_geometries(
    geometries,
    window_name="BUGB9DY1 - Individual Tooth Point Clouds",
    point_show_normal=False
)