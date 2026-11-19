import open3d as o3d
import os
import glob

TEETH_DIR = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\correct_teeth"

files = sorted(
    glob.glob(
        os.path.join(TEETH_DIR, "tooth_*.obj")
    )
)

print("Found", len(files), "teeth")

geometries = []

for file in files:

    mesh = o3d.io.read_triangle_mesh(file)

    if mesh.is_empty():
        print("EMPTY:", file)
        continue

    mesh.compute_vertex_normals()

    # Same neutral color for easy inspection
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


print("\nOpening all extracted teeth...")

o3d.visualization.draw_geometries(
    geometries,
    window_name="BUGB9DY1 - All Extracted Teeth",
    mesh_show_back_face=True
)