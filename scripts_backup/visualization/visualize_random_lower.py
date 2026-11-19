import os
import glob
import random
import open3d as o3d

OUTPUT_DIR = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\processed_part1_lower"

# Find processed cases
cases = [
    x for x in os.listdir(OUTPUT_DIR)
    if os.path.isdir(os.path.join(OUTPUT_DIR, x))
]

if not cases:
    raise RuntimeError("No processed lower-jaw cases found.")

# Pick a random case
case_name = random.choice(cases)

case_dir = os.path.join(
    OUTPUT_DIR,
    case_name
)

print("Selected case:", case_name)

# Find tooth meshes
files = sorted(
    glob.glob(
        os.path.join(
            case_dir,
            "tooth_*.obj"
        )
    )
)

print("Teeth found:", len(files))

geometries = []

for file in files:

    mesh = o3d.io.read_triangle_mesh(file)

    if mesh.is_empty():
        print("WARNING: empty:", file)
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

print("\nOpening visualization...")

o3d.visualization.draw_geometries(
    geometries,
    window_name=f"{case_name} - Lower Jaw Teeth",
    mesh_show_back_face=True
)