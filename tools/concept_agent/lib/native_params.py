"""Runtime utilities for rewritten-native parameter packages.

This release package consumes already-converted rewritten parameters. It does
not read legacy ``conceptualization.pkl`` files and does not run mappers.
"""

from __future__ import annotations

import importlib
import json
import pickle
import sys
from pathlib import Path

import numpy as np

from tools.concept_agent.lib.report_schema import event_from_exception


ROOT = Path(__file__).resolve().parents[3]
FORMAT_VERSION = "rewritten_category_parameters.v1"
JSON_INDEX_FORMAT_VERSION = "rewritten_category_parameter_index.v1"
JSON_OBJECT_FORMAT_VERSION = "rewritten_category_object_parameters.v1"
DEFAULT_JSON_DIR_NAME = "rewritten_parameters"
DEFAULT_PKL_NAME = "rewritten_parameters.pkl"


class MeshBundle:
    def __init__(self, vertices, faces):
        self.vertices = np.asarray(vertices, dtype=float)
        self.faces = np.asarray(faces, dtype=int)


def default_package_path(category_name, rewritten_root=None, prefer_json=True):
    rewritten_root = Path(rewritten_root or ROOT / "code" / "code_rewritten")
    filename = DEFAULT_JSON_DIR_NAME if prefer_json else DEFAULT_PKL_NAME
    return rewritten_root / category_name / filename


def load_rewritten_parameter_package(path):
    path = Path(path)
    if path.is_dir():
        return load_rewritten_parameter_json_directory(path)

    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        data_format = data.get("format")
        if data_format == FORMAT_VERSION:
            package = data
        elif data_format == JSON_INDEX_FORMAT_VERSION:
            package = load_rewritten_parameter_json_directory(path.parent)
        elif data_format == JSON_OBJECT_FORMAT_VERSION:
            package = package_from_object_json(data, path)
        else:
            raise ValueError(
                f"Unsupported rewritten JSON parameter format {data_format!r}: {path}"
            )
    elif suffix == ".pkl":
        with path.open("rb") as stream:
            package = pickle.load(stream)
    else:
        raise ValueError(f"Unsupported rewritten parameter package extension: {path}")

    if package.get("format") != FORMAT_VERSION:
        raise ValueError(
            f"Unsupported parameter package format {package.get('format')!r}; "
            f"expected {FORMAT_VERSION!r}."
        )
    return package


def load_rewritten_parameter_json_directory(json_dir):
    json_dir = Path(json_dir)
    index_path = json_dir / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if index.get("format") != JSON_INDEX_FORMAT_VERSION:
        raise ValueError(
            f"Unsupported parameter index format {index.get('format')!r}; "
            f"expected {JSON_INDEX_FORMAT_VERSION!r}."
        )

    objects = []
    for object_ref in index.get("objects", []):
        object_path = json_dir / object_ref["file"]
        object_data = json.loads(object_path.read_text(encoding="utf-8"))
        if object_data.get("format") != JSON_OBJECT_FORMAT_VERSION:
            raise ValueError(
                f"Unsupported object parameter format {object_data.get('format')!r}: "
                f"{object_path}"
            )
        if object_data.get("category") != index.get("category"):
            raise ValueError(
                f"Object parameter category mismatch in {object_path}: "
                f"{object_data.get('category')!r} != {index.get('category')!r}"
            )
        objects.append(object_data["object"])

    package = {
        "format": index["package_format"],
        "category": index["category"],
        "status": index["status"],
        "source": index["source"],
        "conversion": index["conversion"],
        "summary": index["summary"],
        "objects": objects,
        "events": index.get("events", []),
    }
    if package.get("format") != FORMAT_VERSION:
        raise ValueError(
            f"Unsupported parameter package format {package.get('format')!r}; "
            f"expected {FORMAT_VERSION!r}."
        )
    return package


def package_from_object_json(object_data, object_path):
    category = object_data.get("category")
    object_record = object_data.get("object")
    if not isinstance(object_record, dict):
        raise ValueError(f"Object parameter JSON must contain an object record: {object_path}")
    return {
        "format": FORMAT_VERSION,
        "category": category,
        "status": "passed",
        "source": {
            "type": "rewritten_object_parameter_json",
            "path": str(object_path),
        },
        "conversion": {
            "mapper_module": None,
            "max_objects": 1,
        },
        "summary": {
            "object_count": 1,
            "concept_count": len(object_record.get("concepts", [])),
            "class_counts": class_counts_for_objects([object_record]),
            "legacy_class_counts": legacy_class_counts_for_objects([object_record]),
            "event_count": 0,
            "failed_event_count": 0,
        },
        "objects": [object_record],
        "events": [],
    }


def class_counts_for_objects(objects):
    counts = {}
    for object_record in objects:
        for concept in object_record.get("concepts", []):
            template = concept.get("template")
            counts[template] = counts.get(template, 0) + 1
    return dict(sorted(counts.items()))


def legacy_class_counts_for_objects(objects):
    counts = {}
    for object_record in objects:
        for concept in object_record.get("concepts", []):
            legacy_template = concept.get("source", {}).get("legacy_template")
            if legacy_template is not None:
                counts[legacy_template] = counts.get(legacy_template, 0) + 1
    return dict(sorted(counts.items()))


def load_rewritten_category_module(category_name):
    _ensure_root_on_path()
    return importlib.import_module(f"code.code_rewritten.{category_name}")


def instantiate_rewritten_concept(category_module, concept_record):
    class_name = concept_record["template"]
    cls = getattr(category_module, class_name)
    return cls(**concept_record["parameters"])


def instantiate_object_concepts(category_module, object_record):
    instances = []
    events = []
    for concept_index, concept_record in enumerate(object_record.get("concepts", [])):
        try:
            instances.append(instantiate_rewritten_concept(category_module, concept_record))
        except Exception as exc:
            events.append(
                event_from_exception(
                    "instantiate_rewritten",
                    exc,
                    class_name=concept_record.get("template"),
                    case_index=concept_index,
                    suggestion="Check rewritten_parameters package against rewritten constructor.",
                )
            )
    return instances, events


def combine_instances(instances):
    vertices = []
    faces = []
    vertex_offset = 0
    for instance in instances:
        instance_vertices = np.asarray(instance.vertices, dtype=float)
        instance_faces = np.asarray(instance.faces, dtype=int)
        vertices.append(instance_vertices)
        faces.append(instance_faces + vertex_offset)
        vertex_offset += len(instance_vertices)
    if not vertices:
        return MeshBundle(np.empty((0, 3), dtype=float), np.empty((0, 3), dtype=int))
    return MeshBundle(np.concatenate(vertices), np.concatenate(faces))


def package_object_label(object_record):
    object_id = object_record.get("id")
    object_index = object_record.get("source_object_index")
    if object_id not in (None, ""):
        return f"object_{object_index}_{object_id}"
    return f"object_{object_index}"


def _ensure_root_on_path():
    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
