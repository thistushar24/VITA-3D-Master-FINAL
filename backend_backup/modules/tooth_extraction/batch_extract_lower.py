import json
import os
import numpy as np
import open3d as o3d


# ============================================================
# PATHS
# ============================================================

DATASET_DIR = r"C:\Users\PREDATOR\Downloads\EDI\5cmg3-osfstorage-archive\data_part_1\lower"

OUTPUT_DIR = r"C:\Users\PREDATOR\Downloads\EDI\TESTING\processed_part1_lower"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# FUNCTION: PROCESS ONE CASE
# ============================================================

def process_case(case_dir):

    case_name = os.path.basename(case_dir)

    obj_path = os.path.join(
        case_dir,
        f"{case_name}_lower.obj"
    )

    json_path = os.path.join(
        case_dir,
        f"{case_name}_lower.json"
    )

    # --------------------------------------------------------
    # Check files
    # --------------------------------------------------------

    if not os.path.exists(obj_path):

        print("SKIP - OBJ missing:", case_name)
        return False

    if not os.path.exists(json_path):

        print("SKIP - JSON missing:", case_name)
        return False

    print("\n========================================")
    print("Processing:", case_name)
    print("========================================")


    # ========================================================
    # READ ORIGINAL OBJ DIRECTLY
    # IMPORTANT:
    # Do NOT use Open3D to read vertices here.
    # Teeth3DS JSON follows the original OBJ vertex order.
    # ========================================================

    vertices = []
    faces = []

    with open(obj_path, "r") as f:

        for line in f:

            # ------------------------------------------------
            # Vertex
            # ------------------------------------------------

            if line.startswith("v "):

                parts = line.strip().split()

                vertices.append([
                    float(parts[1]),
                    float(parts[2]),
                    float(parts[3])
                ])

            # ------------------------------------------------
            # Face
            # ------------------------------------------------

            elif line.startswith("f "):

                parts = line.strip().split()[1:]

                face = []

                for part in parts:

                    vertex_index = int(
                        part.split("/")[0]
                    )

                    # OBJ is 1-based
                    if vertex_index > 0:

                        vertex_index -= 1

                    else:

                        vertex_index = (
                            len(vertices) + vertex_index
                        )

                    face.append(vertex_index)


                # Normal triangle
                if len(face) == 3:

                    faces.append(face)

                # Polygon → triangles
                elif len(face) > 3:

                    for i in range(1, len(face) - 1):

                        faces.append([
                            face[0],
                            face[i],
                            face[i + 1]
                        ])


    vertices = np.array(
        vertices,
        dtype=np.float64
    )

    faces = np.array(
        faces,
        dtype=np.int32
    )

    print("Vertices :", len(vertices))
    print("Triangles:", len(faces))


    # ========================================================
    # READ JSON
    # ========================================================

    with open(json_path, "r") as f:

        data = json.load(f)

    labels = np.array(
        data["labels"]
    )

    instances = np.array(
        data["instances"]
    )


    # ========================================================
    # VERIFY VERTEX MAPPING
    # ========================================================

    if len(vertices) != len(labels):

        print(
            "ERROR: vertex/label mismatch"
        )

        print(
            "OBJ:",
            len(vertices)
        )

        print(
            "JSON:",
            len(labels)
        )

        return False


    if len(vertices) != len(instances):

        print(
            "ERROR: vertex/instance mismatch"
        )

        print(
            "OBJ:",
            len(vertices)
        )

        print(
            "JSON:",
            len(instances)
        )

        return False


    print("Vertex/JSON mapping: OK")


    # ========================================================
    # CREATE OUTPUT FOLDER
    # ========================================================

    case_output = os.path.join(
        OUTPUT_DIR,
        case_name
    )

    os.makedirs(
        case_output,
        exist_ok=True
    )


    # ========================================================
    # METADATA
    # ========================================================

    metadata = {

        "patient_id": data.get(
            "id_patient",
            case_name
        ),

        "jaw": "lower",

        "vertex_count": int(
            len(vertices)
        ),

        "triangle_count": int(
            len(faces)
        ),

        "teeth": {}
    }


    # ========================================================
    # FIND ALL INSTANCES
    # ========================================================

    unique_instances = sorted(
        np.unique(instances)
    )

    print(
        "Instances:",
        unique_instances
    )


    # ========================================================
    # EXTRACT EACH TOOTH
    # ========================================================

    for instance_id in unique_instances:

        # ----------------------------------------------------
        # Instance 0 = gingiva
        # ----------------------------------------------------

        if instance_id == 0:
            continue


        # ----------------------------------------------------
        # Find vertices belonging to tooth
        # ----------------------------------------------------

        tooth_mask = (
            instances == instance_id
        )

        tooth_vertex_indices = np.where(
            tooth_mask
        )[0]


        # ----------------------------------------------------
        # Find FDI number
        # ----------------------------------------------------

        tooth_labels = labels[
            tooth_vertex_indices
        ]

        tooth_number = int(
            np.bincount(
                tooth_labels
            ).argmax()
        )


        print(
            f"  Instance {instance_id}"
            f" -> FDI {tooth_number}"
            f" -> {len(tooth_vertex_indices)} vertices"
        )


        # ----------------------------------------------------
        # Select original mesh faces
        #
        # A face belongs to the tooth when at least
        # 2 of its vertices belong to that tooth.
        # ----------------------------------------------------

        selected_faces = []

        for face in faces:

            count = np.sum(
                tooth_mask[face]
            )

            if count >= 2:

                selected_faces.append(
                    face
                )


        if len(selected_faces) == 0:

            print(
                f"    WARNING: no faces for tooth {tooth_number}"
            )

            continue


        selected_faces = np.array(
            selected_faces,
            dtype=np.int32
        )


        # ----------------------------------------------------
        # Find vertices used by selected faces
        # ----------------------------------------------------

        used_vertices = np.unique(
            selected_faces.flatten()
        )


        # ----------------------------------------------------
        # Remap original indices
        # to local tooth indices
        # ----------------------------------------------------

        vertex_map = {
            old_index: new_index

            for new_index, old_index
            in enumerate(used_vertices)
        }


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


        # ----------------------------------------------------
        # Create tooth mesh
        # ----------------------------------------------------

        tooth_mesh = o3d.geometry.TriangleMesh()

        tooth_mesh.vertices = (
            o3d.utility.Vector3dVector(
                vertices[used_vertices]
            )
        )

        tooth_mesh.triangles = (
            o3d.utility.Vector3iVector(
                local_faces
            )
        )


        # ----------------------------------------------------
        # Clean mesh
        # ----------------------------------------------------

        tooth_mesh.remove_duplicated_vertices()

        tooth_mesh.remove_duplicated_triangles()

        tooth_mesh.remove_degenerate_triangles()

        tooth_mesh.compute_vertex_normals()


        # ----------------------------------------------------
        # Output filename
        # ----------------------------------------------------

        output_path = os.path.join(
            case_output,
            f"tooth_{tooth_number}.obj"
        )


        # ----------------------------------------------------
        # Save OBJ
        # ----------------------------------------------------

        success = o3d.io.write_triangle_mesh(
            output_path,
            tooth_mesh
        )


        if not success:

            print(
                f"    ERROR saving tooth {tooth_number}"
            )

            continue


        # ----------------------------------------------------
        # Save metadata
        # ----------------------------------------------------

        metadata["teeth"][
            str(tooth_number)
        ] = {

            "instance_id": int(
                instance_id
            ),

            "vertex_count": int(
                len(used_vertices)
            ),

            "triangle_count": int(
                len(local_faces)
            ),

            "file":
                f"tooth_{tooth_number}.obj"
        }


        print(
            f"    Saved tooth_{tooth_number}.obj"
        )


    # ========================================================
    # SAVE CASE METADATA
    # ========================================================

    metadata_path = os.path.join(
        case_output,
        "metadata.json"
    )

    with open(
        metadata_path,
        "w"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=4
        )


    print(
        "Completed:",
        case_name
    )

    return True


# ============================================================
# FIND ALL CASES
# ============================================================

cases = []

for name in os.listdir(
    DATASET_DIR
):

    path = os.path.join(
        DATASET_DIR,
        name
    )

    if os.path.isdir(path):

        cases.append(path)


cases.sort()


# ============================================================
# START
# ============================================================

print()
print("========================================")
print("TEETH3DS LOWER JAW BATCH PROCESSING")
print("========================================")
print()
print("Dataset:")
print(DATASET_DIR)

print()
print("Output:")
print(OUTPUT_DIR)

print()
print("Cases found:", len(cases))
print()


# ============================================================
# PROCESS
# ============================================================

successful = 0
failed = 0


for case_dir in cases:

    try:

        result = process_case(
            case_dir
        )

        if result:

            successful += 1

        else:

            failed += 1


    except Exception as e:

        print()
        print("ERROR processing:")
        print(
            os.path.basename(
                case_dir
            )
        )

        print(
            "Error:",
            e
        )

        failed += 1


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("========================================")
print("BATCH PROCESSING COMPLETE")
print("========================================")

print(
    "Successful:",
    successful
)

print(
    "Failed:",
    failed
)

print(
    "Total:",
    len(cases)
)

print()
print("Output:")
print(OUTPUT_DIR)