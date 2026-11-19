import json
import os
import open3d as o3d

# Paths
obj_path = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.obj"
json_path = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.json"

# -----------------------------
# Load 3D model
# -----------------------------
mesh = o3d.io.read_triangle_mesh(obj_path)

print("========== OBJ INFORMATION ==========")
print("Vertices:", len(mesh.vertices))
print("Triangles:", len(mesh.triangles))

# -----------------------------
# Load JSON
# -----------------------------
with open(json_path, "r") as f:
    data = json.load(f)

print("\n========== JSON INFORMATION ==========")
print("JSON type:", type(data))

if isinstance(data, dict):
    print("JSON keys:")
    for key in data.keys():
        print("  -", key)

print("\n========== JSON CONTENT SUMMARY ==========")

for key, value in data.items():

    if isinstance(value, list):
        print(f"{key}: list with {len(value)} elements")

        if len(value) > 0:
            print("  First 10 values:", value[:10])

    else:
        print(f"{key}: {value}")

# -----------------------------
# Check labels
# -----------------------------
if "labels" in data:

    labels = data["labels"]

    print("\n========== LABEL INFORMATION ==========")
    print("Number of labels:", len(labels))
    print("Number of mesh vertices:", len(mesh.vertices))

    unique_labels = sorted(set(labels))

    print("Unique labels:")
    print(unique_labels)

# -----------------------------
# Check instances
# -----------------------------
if "instances" in data:

    instances = data["instances"]

    print("\n========== INSTANCE INFORMATION ==========")
    print("Number of instances:", len(instances))

    unique_instances = sorted(set(instances))

    print("Number of unique instances:", len(unique_instances))
    print("Unique instances:")
    print(unique_instances)

print("\n========== DONE ==========")