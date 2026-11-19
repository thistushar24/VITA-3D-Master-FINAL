import json
import os
import numpy as np
import open3d as o3d


# ============================================================
# PATHS
# ============================================================

OBJ_PATH = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.obj"

JSON_PATH = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\BUGB9DY1_upper.json"

OUTPUT_DIR = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\BUGB9DY1\correct_teeth"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# READ ORIGINAL OBJ DIRECTLY
# ============================================================

print("Reading OBJ directly...")

vertices = []
faces = []

with open(OBJ_PATH, "r") as f:

    for line in f:

        # Vertex
        if line.startswith("v "):

            parts = line.strip().split()

            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])

            vertices.append([x, y, z])

        # Face
        elif line.startswith("f "):

            parts = line.strip().split()[1:]

            face = []

            for part in parts:

                # Handles:
                # v
                # v/vt
                # v/vt/vn
                # v//vn

                vertex_index = int(part.split("/")[0])

                # OBJ uses 1-based indexing
                if vertex_index > 0:
                    vertex_index -= 1
                else:
                    vertex_index = len(vertices) + vertex_index

                face.append(vertex_index)

            # Dataset should contain triangular faces
            if len(face) == 3:
                faces.append(face)

            # Handle polygon just in case
            elif len(face) > 3:

                for i in range(1, len(face) - 1):
                    faces.append([
                        face[0],
                        face[i],
                        face[i + 1]
                    ])


vertices = np.array(vertices, dtype=np.float64)
faces = np.array(faces, dtype=np.int32)

print("Original OBJ vertices :", len(vertices))
print("Original OBJ triangles:", len(faces))


# ============================================================
# LOAD JSON
# ============================================================

with open(JSON_PATH, "r") as f:
    data = json.load(f)

labels = np.array(data["labels"])
instances = np.array(data["instances"])


# ============================================================
# VERIFY
# ============================================================

print("\nChecking annotation mapping...")

if len(vertices) != len(labels):
    raise ValueError(
        f"Vertex count mismatch: "
        f"{len(vertices)} vs {len(labels)}"
    )

if len(vertices) != len(instances):
    raise ValueError(
        f"Vertex count mismatch: "
        f"{len(vertices)} vs {len(instances)}"
    )

print("Vertex order is preserved.")
print("JSON mapping matches original OBJ.")


# ============================================================
# EXTRACT EACH TOOTH
# ============================================================

unique_instances = sorted(np.unique(instances))

for instance_id in unique_instances:

    # Instance 0 = gingiva
    if instance_id == 0:
        continue

    # Vertices belonging to this tooth
    tooth_vertex_mask = instances == instance_id

    tooth_vertex_indices = np.where(
        tooth_vertex_mask
    )[0]

    # Determine FDI number
    tooth_labels = labels[tooth_vertex_indices]

    tooth_number = int(
        np.bincount(tooth_labels).argmax()
    )

    print("\n--------------------------------")
    print("Instance:", instance_id)
    print("FDI tooth:", tooth_number)
    print("Vertices:", len(tooth_vertex_indices))


    # ========================================================
    # SELECT FACES
    #
    # Keep a face when at least TWO of its vertices
    # belong to this tooth.
    #
    # This preserves boundary faces instead of requiring
    # all 3 vertices to have the same instance.
    # ========================================================

    selected_faces = []

    for face in faces:

        count = np.sum(
            tooth_vertex_mask[face]
        )

        if count >= 2:
            selected_faces.append(face)


    selected_faces = np.array(
        selected_faces,
        dtype=np.int32
    )

    print(
        "Selected faces:",
        len(selected_faces)
    )

    if len(selected_faces) == 0:
        print("WARNING: No faces found.")
        continue


    # ========================================================
    # FIND VERTICES USED BY SELECTED FACES
    # ========================================================

    used_vertices = np.unique(
        selected_faces.flatten()
    )


    # Map original vertex indices → local indices

    vertex_map = {
        old: new
        for new, old in enumerate(used_vertices)
    }


    # ========================================================
    # CONVERT FACES TO LOCAL INDICES
    # ========================================================

    local_faces = np.array(
        [
            [
                vertex_map[face[0]],
                vertex_map[face[1]],
                vertex_map[face[2]]
            ]
            for face in selected_faces
        ],
        dtype=np.int32
    )


    # ========================================================
    # CREATE OPEN3D MESH
    # ========================================================

    tooth_mesh = o3d.geometry.TriangleMesh()

    tooth_mesh.vertices = o3d.utility.Vector3dVector(
        vertices[used_vertices]
    )

    tooth_mesh.triangles = o3d.utility.Vector3iVector(
        local_faces
    )

    tooth_mesh.remove_duplicated_vertices()
    tooth_mesh.remove_duplicated_triangles()
    tooth_mesh.remove_degenerate_triangles()

    tooth_mesh.compute_vertex_normals()


    # ========================================================
    # SAVE
    # ========================================================

    output_path = os.path.join(
        OUTPUT_DIR,
        f"tooth_{tooth_number}.obj"
    )

    o3d.io.write_triangle_mesh(
        output_path,
        tooth_mesh
    )

    print("Saved:", output_path)


print("\n========================================")
print("CORRECT EXTRACTION FINISHED")
print("========================================")