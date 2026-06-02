"""Assembly helpers for composing rewritten primitives into concept meshes."""

import numpy as np
import trimesh

from .transforms import apply_transform

DEFAULT_SAMPLE_COUNT = 1024


def _degrees_to_radians(rotation_degrees):
    return [angle / 180.0 * np.pi for angle in rotation_degrees]


def combine_components(components):
    vertices = []
    faces = []
    vertex_offset = 0

    for component in components:
        component_vertices = np.asarray(component.vertices, dtype=float)
        component_faces = np.asarray(component.faces, dtype=int)
        vertices.append(component_vertices)
        faces.append(component_faces + vertex_offset)
        vertex_offset += len(component_vertices)

    if not vertices:
        return np.empty((0, 3), dtype=float), np.empty((0, 3), dtype=int)

    return np.concatenate(vertices), np.concatenate(faces)


class ConceptTemplate:
    def __init__(
        self,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        rotation_order="XYZ",
        offset_first=False,
    ):
        self.position = list(position)
        self.rotation = list(rotation)
        self.rotation_order = rotation_order
        self.offset_first = offset_first
        self.components = []
        self.local_vertices = np.empty((0, 3), dtype=float)
        self.faces = np.empty((0, 3), dtype=int)

    @property
    def vertices(self):
        return apply_transform(
            self.local_vertices,
            self.position,
            _degrees_to_radians(self.rotation),
            self.rotation_order,
            offset_first=self.offset_first,
        )

    def _finalize_mesh(self, components):
        self.components = list(components)
        self.local_vertices, faces = combine_components(self.components)
        self.faces = faces
        self.overall_obj_mesh = trimesh.Trimesh(
            vertices=self.vertices,
            faces=self.faces,
            process=False,
        )
        if len(self.local_vertices) == 0 or len(self.faces) == 0:
            self.overall_obj_pts = np.empty((0, 3), dtype=float)
        else:
            self.overall_obj_pts = np.asarray(self.overall_obj_mesh.sample(DEFAULT_SAMPLE_COUNT))

    def bbox(self):
        if len(self.vertices) == 0:
            return np.zeros((2, 3))
        return np.stack([self.vertices.min(axis=0), self.vertices.max(axis=0)])
