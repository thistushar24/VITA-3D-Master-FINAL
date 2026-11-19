import os
import glob
import random
import open3d as o3d

OUTPUT_DIR = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\processed_part1_upper"


# ============================================================
# FIND PROCESSED CASES
# ============================================================

cases = [
    x for x in os.listdir(OUTPUT_DIR)
    if os.path.isdir(os.path.join(OUTPUT_DIR, x))
]

# Don't use the case we already tested manually
cases = [
    x for x in cases
    if x != "BUGB9DY1"
]

if not cases:
    raise RuntimeError("No other processed cases found.")


# Select one random case
case_name = random.choice(cases)

case_dir = os.path.join(
    OUTPUT_DIR,
    case_name
)

print("Selected case:", case_name)


# ============================================================
# FIND TOOTH FILES
# ============================================================

files = sorted(
    glob.glob(
        os.path.join(
            case_dir,
            "tooth_*.obj"
        )
    )
)

print("Number of teeth:", len(files))

if len(files) == 0:
    raise RuntimeError("No tooth OBJ files found.")


# ============================================================
# LOAD TEETH
# ============================================================

geometries = []

for file in files:

    mesh = o3d.io.read_triangle_mesh(file)

    if mesh.is_empty():
        print("WARNING: Empty mesh:", file)
        continue

    mesh.compute_vertex_normals()

    mesh.paint_uniform_color(
        [0.85, 0.85, 0.85]
    )

    geometries.append(mesh)

    print(
        os.path.basename(file),
        "| vertices:",
        len(mesh.vertices),
        "| triangles:",
        len(mesh.triangles)
    )


# ============================================================
# VISUALIZE
# ============================================================

print("\nOpening:", case_name)

o3d.visualization.draw_geometries(
    geometries,
    window_name=f"{case_name} - Extracted Teeth",
    mesh_show_back_face=True
)