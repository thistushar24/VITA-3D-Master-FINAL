import json
import os
import numpy as np
import open3d as o3d

# ============================================================
# PATHS
# ============================================================

OBJ_PATH = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.obj"

JSON_PATH = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.json"

OUTPUT_DIR = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\extracted_teeth"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOAD MESH
# ============================================================

print("Loading mesh...")

mesh = o3d.io.read_triangle_mesh(OBJ_PATH)

vertices = np.asarray(mesh.vertices)
triangles = np.asarray(mesh.triangles)

print("Vertices:", len(vertices))
print("Triangles:", len(triangles))


# ============================================================
# LOAD LABELS
# ============================================================

print("\nLoading JSON...")

with open(JSON_PATH, "r") as f:
    data = json.load(f)

labels = np.array(data["labels"])
instances = np.array(data["instances"])


# ============================================================
# CHECK
# ============================================================

if len(vertices) != len(labels):
    raise ValueError(
        f"Vertex count {len(vertices)} != label count {len(labels)}"
    )

if len(vertices) != len(instances):
    raise ValueError(
        f"Vertex count {len(vertices)} != instance count {len(instances)}"
    )

print("Vertex / label / instance counts match.")


# ============================================================
# EXTRACT EACH TOOTH
# ============================================================

unique_instances = sorted(set(instances))

print("\nInstances:", unique_instances)

for instance_id in unique_instances:

    # 0 = gingiva
    if instance_id == 0:
        continue

    print("\n--------------------------------")
    print("Processing instance:", instance_id)

    # --------------------------------------------------------
    # Find tooth number
    # --------------------------------------------------------

    vertex_indices = np.where(instances == instance_id)[0]

    tooth_labels = labels[vertex_indices]

    nonzero_labels = tooth_labels[tooth_labels != 0]

    if len(nonzero_labels) == 0:
        print("No tooth label found.")
        continue

    tooth_number = int(np.bincount(nonzero_labels).argmax())

    print("Tooth number:", tooth_number)
    print("Labeled vertices:", len(vertex_indices))


    # --------------------------------------------------------
    # Determine which TRIANGLES belong to this tooth
    #
    # A triangle is assigned to a tooth if the majority
    # of its vertices belong to that instance.
    # --------------------------------------------------------

    selected_triangles = []

    for triangle in triangles:

        v1, v2, v3 = triangle

        instance_values = [
            instances[v1],
            instances[v2],
            instances[v3]
        ]

        # Majority vote
        counts = np.bincount(
            instance_values,
            minlength=max(unique_instances) + 1
        )

        majority_instance = np.argmax(counts)

        if majority_instance == instance_id:
            selected_triangles.append(triangle)


    selected_triangles = np.array(
        selected_triangles,
        dtype=np.int32
    )

    print("Selected triangles:", len(selected_triangles))

    if len(selected_triangles) == 0:
        print("WARNING: no triangles found.")
        continue


    # --------------------------------------------------------
    # Find vertices actually used by selected triangles
    # --------------------------------------------------------

    used_vertex_indices = np.unique(
        selected_triangles.flatten()
    )

    # Original → local index
    vertex_map = {
        old_index: new_index
        for new_index, old_index
        in enumerate(used_vertex_indices)
    }


    # --------------------------------------------------------
    # Convert triangle indices
    # --------------------------------------------------------

    local_triangles = np.array(
        [
            [
                vertex_map[v1],
                vertex_map[v2],
                vertex_map[v3]
            ]
            for v1, v2, v3 in selected_triangles
        ],
        dtype=np.int32
    )


    # --------------------------------------------------------
    # Create tooth mesh
    # --------------------------------------------------------

    tooth_vertices = vertices[used_vertex_indices]

    tooth_mesh = o3d.geometry.TriangleMesh()

    tooth_mesh.vertices = o3d.utility.Vector3dVector(
        tooth_vertices
    )

    tooth_mesh.triangles = o3d.utility.Vector3iVector(
        local_triangles
    )

    tooth_mesh.remove_duplicated_vertices()
    tooth_mesh.remove_duplicated_triangles()
    tooth_mesh.remove_degenerate_triangles()

    tooth_mesh.compute_vertex_normals()


    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_path = os.path.join(
        OUTPUT_DIR,
        f"tooth_{tooth_number}.obj"
    )

    o3d.io.write_triangle_mesh(
        output_path,
        tooth_mesh
    )

    print("Saved:", output_path)


print("\n================================")
print("EXTRACTION FINISHED")
print("================================")