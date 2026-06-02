import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.concept_agent.lib.native_params import (
    ROOT,
    combine_instances,
    default_package_path,
    instantiate_object_concepts,
    load_rewritten_category_module,
    load_rewritten_parameter_package,
    package_object_label,
)
from tools.concept_agent.lib.render_preview import render_class_preview, write_preview_sheet
from tools.concept_agent.lib.report_schema import to_jsonable, write_json


def main(argv=None):
    args = parse_args(argv)
    report = visualize(args)
    if args.verbose:
        print(json.dumps(to_jsonable(report), ensure_ascii=False))
    elif report["status"] != "passed":
        print(
            f"visualize failed: {report['failed_object_count']} failed objects, "
            f"{len(report['events'])} events",
            file=sys.stderr,
        )
    return 0 if report["status"] == "passed" else 1


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Render rewritten-native parameter package meshes with Open3D, optionally saving OBJ/PNG files."
    )
    parser.add_argument("--category", help="Category name. Inferred from package when omitted.")
    parser.add_argument(
        "--params",
        help=(
            "rewritten_parameters directory, index/object JSON, or rewritten_parameters.pkl. "
            "Defaults to code_rewritten/<Category>/rewritten_parameters/."
        ),
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Persist OBJ, PNG previews, preview sheet, and render_report.json.",
    )
    parser.add_argument(
        "--no-viewer",
        action="store_true",
        help="Do not open the Open3D viewer. Intended for CI/headless checks.",
    )
    parser.add_argument(
        "--export-concepts",
        action="store_true",
        help="Also export individual concept OBJ files for each rendered object.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print the full JSON render report to stdout.",
    )
    args = parser.parse_args(argv)
    if args.export_concepts and not args.save:
        parser.error("--export-concepts requires --save")
    return args


def visualize(args):
    if args.export_concepts and not args.save:
        raise ValueError("--export-concepts requires --save")

    no_viewer = bool(getattr(args, "no_viewer", False))
    verbose = bool(getattr(args, "verbose", False))
    category_name = args.category
    params_path = Path(args.params) if args.params else None
    if params_path is None:
        if not category_name:
            raise ValueError("--category is required when --params is omitted")
        params_path = default_package_path(category_name)

    package = load_rewritten_parameter_package(params_path)
    category_name = category_name or package["category"]
    output_dir = None
    if args.save:
        output_dir = default_output_dir(category_name)
        output_dir.mkdir(parents=True, exist_ok=True)

    category_module = load_rewritten_category_module(category_name)
    objects = package.get("objects", [])

    object_results = []
    preview_paths = []
    viewer_meshes = []
    events = []
    for object_record in objects:
        label = package_object_label(object_record)
        safe_label = safe_filename(label)
        instances, instantiate_events = instantiate_object_concepts(
            category_module, object_record
        )
        events.extend(instantiate_events)
        if not instances:
            object_results.append(
                {
                    "object": label,
                    "status": "failed",
                    "concept_count": 0,
                    "obj": None,
                    "preview": None,
                    "events": instantiate_events,
                }
            )
            continue

        combined = combine_instances(instances)
        bbox = mesh_bbox(combined)
        viewer_meshes.append({"label": label, "mesh": combined})
        obj_path = None
        preview_path = None
        concept_obj_paths = []
        if args.save:
            obj_path = output_dir / "objs" / f"{safe_label}.obj"
            obj_path.parent.mkdir(parents=True, exist_ok=True)
            export_mesh(combined.vertices, combined.faces, obj_path)
            preview_path = render_class_preview(combined, output_dir / "previews", safe_label)
            preview_paths.append(preview_path)

            if args.export_concepts:
                concept_obj_paths = export_concept_objs(
                    instances,
                    object_record,
                    output_dir / "concept_objs" / safe_label,
                )

        object_results.append(
            {
                "object": label,
                "status": "passed",
                "concept_count": len(instances),
                "vertex_count": int(len(combined.vertices)),
                "face_count": int(len(combined.faces)),
                "bbox": bbox,
                "obj": str(obj_path.relative_to(output_dir)) if obj_path else None,
                "preview": str(preview_path.relative_to(output_dir)) if preview_path else None,
                "concept_objs": [
                    str(path.relative_to(output_dir)) for path in concept_obj_paths
                ],
            }
        )

    sheet_path = None
    if args.save:
        sheet_path = write_preview_sheet(preview_paths, output_dir / "preview_sheet.png")
    if not no_viewer and viewer_meshes:
        show_meshes_in_open3d(viewer_meshes, category_name, verbose=verbose)
    failed_objects = [item for item in object_results if item["status"] != "passed"]
    report = {
        "category": category_name,
        "status": "failed" if failed_objects or events else "passed",
        "params": str(params_path),
        "viewer": not no_viewer,
        "save": bool(args.save),
        "output_dir": str(output_dir) if output_dir else None,
        "package_summary": package.get("summary", {}),
        "rendered_object_count": len(object_results),
        "failed_object_count": len(failed_objects),
        "preview_sheet": (
            str(sheet_path.relative_to(output_dir)) if sheet_path and output_dir else None
        ),
        "objects": object_results,
        "events": events,
    }
    if args.save:
        write_json(output_dir / "render_report.json", report)
    return report


def export_concept_objs(instances, object_record, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    concepts = object_record.get("concepts", [])
    for concept_index, instance in enumerate(instances):
        class_name = concepts[concept_index].get("template", instance.__class__.__name__)
        path = output_dir / f"concept{concept_index:03d}_{safe_filename(class_name)}.obj"
        export_mesh(instance.vertices, instance.faces, path)
        paths.append(path)
    return paths


def default_output_dir(category_name):
    return ROOT / "reports" / f"{category_name}_rewritten_native_visualization"


def export_mesh(vertices, faces, path):
    import numpy as np
    import trimesh

    mesh = trimesh.Trimesh(
        vertices=np.asarray(vertices, dtype=float),
        faces=np.asarray(faces, dtype=int),
        process=False,
    )
    mesh.export(str(path))


def mesh_bbox(mesh):
    vertices = mesh.vertices
    if len(vertices) == 0:
        return None
    return {
        "min": vertices.min(axis=0).tolist(),
        "max": vertices.max(axis=0).tolist(),
    }


def show_meshes_in_open3d(named_meshes, category_name, verbose=False):
    import open3d as o3d

    valid_items = [
        item
        for item in named_meshes
        if len(item["mesh"].vertices) > 0 and len(item["mesh"].faces) > 0
    ]
    if not valid_items:
        return

    for item_index, item in enumerate(valid_items):
        mesh = item["mesh"]
        geometry = o3d.geometry.TriangleMesh(
            o3d.utility.Vector3dVector(mesh.vertices),
            o3d.utility.Vector3iVector(mesh.faces),
        )
        geometry.compute_vertex_normals()
        if verbose:
            print(
                f"Showing {category_name} object {item_index + 1}/{len(valid_items)}: "
                f"{item['label']}. Close the Open3D window to continue.",
                flush=True,
            )
        o3d.visualization.draw_geometries(
            [geometry],
            window_name=(
                f"{category_name} object {item_index + 1}/{len(valid_items)}: "
                f"{item['label']}"
            ),
        )


def safe_filename(value):
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(value))


if __name__ == "__main__":
    raise SystemExit(main())
