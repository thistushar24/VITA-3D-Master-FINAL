import open3d as o3d
import os
import glob

TEETH_DIR = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\extracted_teeth"

files = sorted(glob.glob(os.path.join(TEETH_DIR, "tooth_*.obj")))

print("Teeth found:", len(files))

geometries = []

for file in files:
    mesh = o3d.io.read_triangle_mesh(file)

    if mesh.is_empty():
        print("WARNING - empty:", file)
        continue

    mesh.compute_vertex_normals()

    # Give each tooth a different random-looking color
    mesh.paint_uniform_color([
        0.3 + (len(geometries) * 0.05) % 0.6,
        0.5,
        0.8
    ])

    geometries.append(mesh)

    print("Loaded:", os.path.basename(file))


print("\nOpening visualization...")

o3d.visualization.draw_geometries(
    geometries,
    window_name="BUGB9DY1 - Individual Teeth"
)