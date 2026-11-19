import open3d as o3d

path = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\extracted_teeth\tooth_15.obj"

mesh = o3d.io.read_triangle_mesh(path)

print("Vertices:", len(mesh.vertices))
print("Triangles:", len(mesh.triangles))

mesh.compute_vertex_normals()

o3d.visualization.draw_geometries(
    [mesh],
    window_name="Extracted Tooth 15"
)