import json
import numpy as np
import open3d as o3d

OBJ_PATH = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.obj"
JSON_PATH = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.json"


# ============================================================
# 1. Read OBJ directly
# ============================================================

raw_vertices = []

with open(OBJ_PATH, "r") as f:

    for line in f:

        if line.startswith("v "):

            parts = line.strip().split()

            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])

            raw_vertices.append([x, y, z])


raw_vertices = np.array(raw_vertices)

print("========== RAW OBJ ==========")
print("Vertex count:", len(raw_vertices))


# ============================================================
# 2. Read OBJ using Open3D
# ============================================================

mesh = o3d.io.read_triangle_mesh(OBJ_PATH)

open3d_vertices = np.asarray(mesh.vertices)

print("\n========== OPEN3D ==========")
print("Vertex count:", len(open3d_vertices))


# ============================================================
# 3. Compare counts
# ============================================================

print("\n========== COUNT CHECK ==========")

if len(raw_vertices) == len(open3d_vertices):

    print("COUNT MATCH: YES")

else:

    print("COUNT MATCH: NO")


# ============================================================
# 4. Compare first 10 vertices
# ============================================================

print("\n========== FIRST 10 VERTICES ==========")

for i in range(min(10, len(raw_vertices))):

    print(
        f"\nVertex {i}"
    )

    print(
        "OBJ raw :",
        raw_vertices[i]
    )

    print(
        "Open3D  :",
        open3d_vertices[i]
    )

    difference = np.linalg.norm(
        raw_vertices[i] - open3d_vertices[i]
    )

    print(
        "Difference:",
        difference
    )


# ============================================================
# 5. Load JSON
# ============================================================

with open(JSON_PATH, "r") as f:
    data = json.load(f)

instances = np.array(data["instances"])
labels = np.array(data["labels"])


# ============================================================
# 6. Select FDI 11
# ============================================================

TARGET_INSTANCE = 10

indices = np.where(
    instances == TARGET_INSTANCE
)[0]

selected_raw = raw_vertices[indices]

selected_open3d = open3d_vertices[indices]


# ============================================================
# 7. Bounding boxes
# ============================================================

print("\n========== INSTANCE 10 / FDI 11 ==========")

print("Number of points:", len(indices))

print("\nRAW OBJ bounding box:")

print(
    "X:",
    selected_raw[:, 0].min(),
    "to",
    selected_raw[:, 0].max()
)

print(
    "Y:",
    selected_raw[:, 1].min(),
    "to",
    selected_raw[:, 1].max()
)

print(
    "Z:",
    selected_raw[:, 2].min(),
    "to",
    selected_raw[:, 2].max()
)


print("\nOPEN3D bounding box:")

print(
    "X:",
    selected_open3d[:, 0].min(),
    "to",
    selected_open3d[:, 0].max()
)

print(
    "Y:",
    selected_open3d[:, 1].min(),
    "to",
    selected_open3d[:, 1].max()
)

print(
    "Z:",
    selected_open3d[:, 2].min(),
    "to",
    selected_open3d[:, 2].max()
)


# ============================================================
# 8. Overall bounding box
# ============================================================

print("\n========== WHOLE JAW ==========")

print(
    "X:",
    raw_vertices[:, 0].min(),
    "to",
    raw_vertices[:, 0].max()
)

print(
    "Y:",
    raw_vertices[:, 1].min(),
    "to",
    raw_vertices[:, 1].max()
)

print(
    "Z:",
    raw_vertices[:, 2].min(),
    "to",
    raw_vertices[:, 2].max()
)