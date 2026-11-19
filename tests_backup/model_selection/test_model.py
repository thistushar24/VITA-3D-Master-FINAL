import open3d as o3d
import os

path = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.obj"

print("File exists:", os.path.exists(path))
print("File size:", os.path.getsize(path), "bytes")

mesh = o3d.io.read_triangle_mesh(path)

print(mesh)
print("Vertices:", len(mesh.vertices))
print("Triangles:", len(mesh.triangles))

if len(mesh.vertices) == 0:
    print("ERROR: No vertices loaded.")
else:
    mesh.compute_vertex_normals()

    print("Opening 3D viewer...")

    o3d.visualization.draw_geometries(
        [mesh],
        window_name="BUGB9DY1 Upper Jaw",
        width=1200,
        height=800
    )

    print("Viewer closed.")