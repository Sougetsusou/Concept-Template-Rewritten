"""Base objects for runtime geometry templates."""

from dataclasses import dataclass

import numpy as np

from .transforms import (
    Transform,
    apply_transform,
    inverse_apply_transform,
    rotation_matrix,
    transform_direction,
)


def _normalize(vector):
    vector = np.asarray(vector, dtype=float)
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


@dataclass(frozen=True)
class AnchorFrame:
    """A point plus optional orientation vectors in the same coordinate frame."""

    point: np.ndarray
    normal: np.ndarray | None = None
    tangent: np.ndarray | None = None
    bitangent: np.ndarray | None = None


class GeometryTemplate:
    """Primitive mesh with persistent local geometry and dynamic transforms.

    ``vertices`` remains compatible with legacy code by returning transformed
    vertices, but ``local_vertices`` is never overwritten by normal transform
    changes.
    """

    _BBOX_ANCHOR_NAMES = {
        "bbox_center",
        "bbox_top_center",
        "bbox_bottom_center",
        "bbox_left_center",
        "bbox_right_center",
        "bbox_front_center",
        "bbox_back_center",
        "bbox_top_front_left",
        "bbox_top_front_right",
        "bbox_top_back_left",
        "bbox_top_back_right",
        "bbox_bottom_front_left",
        "bbox_bottom_front_right",
        "bbox_bottom_back_left",
        "bbox_bottom_back_right",
    }

    def __init__(
        self,
        local_vertices,
        faces,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        rotation_order="XYZ",
        name=None,
    ):
        self.name = name or self.__class__.__name__
        self.local_vertices = np.asarray(local_vertices, dtype=float).copy()
        self.faces = np.asarray(faces).copy()
        self.position = list(position)
        self.rotation = list(rotation)
        self.rotation_order = rotation_order
        self._rotation_matrix_override = None
        self._anchor_points = {}
        self._anchor_normals = {}
        self._anchor_tangents = {}

    @property
    def transform(self):
        return Transform(
            position=tuple(self.position),
            rotation=tuple(self.rotation),
            rotation_order=self.rotation_order,
        )

    @property
    def vertices(self):
        return self.world_vertices()

    @vertices.setter
    def vertices(self, world_vertices):
        if self._rotation_matrix_override is not None:
            self.local_vertices = self._inverse_matrix_transform(world_vertices)
            return
        self.local_vertices = inverse_apply_transform(
            world_vertices,
            self.position,
            self.rotation,
            self.rotation_order,
        )

    def world_vertices(self):
        if self._rotation_matrix_override is not None:
            return self._apply_matrix_transform(self.local_vertices)
        return apply_transform(
            self.local_vertices,
            self.position,
            self.rotation,
            self.rotation_order,
        )

    def set_transform(self, position=None, rotation=None, rotation_order=None):
        if position is not None:
            self.position = list(position)
        if rotation is not None:
            self.rotation = list(rotation)
            self._rotation_matrix_override = None
        if rotation_order is not None:
            self.rotation_order = rotation_order
            self._rotation_matrix_override = None
        return self

    def set_rotation_matrix(self, matrix):
        matrix = np.asarray(matrix, dtype=float)
        if matrix.shape != (3, 3):
            raise ValueError("rotation matrix must be a 3x3 matrix")
        self._rotation_matrix_override = matrix.copy()
        return self

    def align_axis_between_points(self, axis, start_point, end_point):
        try:
            axis_index = {"x": 0, "y": 1, "z": 2}[axis.lower()]
        except (AttributeError, KeyError):
            raise ValueError("axis must be one of 'x', 'y', or 'z'") from None
        start_point = np.asarray(start_point, dtype=float)
        end_point = np.asarray(end_point, dtype=float)
        if start_point.shape != (3,) or end_point.shape != (3,):
            raise ValueError("start_point and end_point must be 3D points")

        direction = end_point - start_point
        span = np.linalg.norm(direction)
        if span <= 0:
            raise ValueError("start_point and end_point must be distinct")
        target_axis = direction / span

        matrix = self._axis_alignment_matrix(axis_index, target_axis)
        self.set_rotation_matrix(matrix)
        self.set_transform(position=(start_point + end_point) / 2.0)
        return self

    @staticmethod
    def _axis_alignment_matrix(axis_index, target_axis):
        target_axis = np.asarray(target_axis, dtype=float)
        candidates = (
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
            np.array([1.0, 0.0, 0.0]),
        )

        def projected_reference(exclude_axis):
            for candidate in candidates:
                projected = candidate - np.dot(candidate, exclude_axis) * exclude_axis
                norm = np.linalg.norm(projected)
                if norm > 1e-12:
                    return projected / norm
            raise ValueError("unable to build alignment frame")

        axes = [None, None, None]
        axes[axis_index] = target_axis
        if axis_index == 0:
            axes[1] = projected_reference(axes[0])
            axes[2] = np.cross(axes[0], axes[1])
        elif axis_index == 1:
            axes[2] = projected_reference(axes[1])
            axes[0] = np.cross(axes[1], axes[2])
        else:
            axes[1] = projected_reference(axes[2])
            axes[0] = np.cross(axes[1], axes[2])

        axes = [axis / np.linalg.norm(axis) for axis in axes]
        return np.column_stack(axes)

    def _current_rotation_matrix(self):
        if self._rotation_matrix_override is not None:
            return self._rotation_matrix_override
        return rotation_matrix(self.rotation, self.rotation_order)

    def _apply_matrix_transform(self, points):
        return np.matmul(
            np.asarray(points, dtype=float),
            self._current_rotation_matrix().T,
        ) + np.asarray(self.position, dtype=float)

    def _inverse_matrix_transform(self, points):
        return np.matmul(
            np.asarray(points, dtype=float) - np.asarray(self.position, dtype=float),
            self._current_rotation_matrix(),
        )

    def with_name(self, name):
        self.name = name
        return self

    def move_anchor_to(self, source_anchor, target_point):
        target_point = np.asarray(target_point, dtype=float)
        current_anchor = self.world_anchor(source_anchor)
        self.set_transform(
            position=np.asarray(self.position, dtype=float) + target_point - current_anchor
        )
        return self

    def move_local_point_to(self, local_point, target_point):
        target_point = np.asarray(target_point, dtype=float)
        current_point = self.world_point(local_point)
        self.set_transform(
            position=np.asarray(self.position, dtype=float) + target_point - current_point
        )
        return self

    def move_local_point_axes_to(self, local_point, target_point, axes):
        axis_indices = {"x": 0, "y": 1, "z": 2}
        selected_indices = [axis_indices[axis] for axis in axes]
        target_point = np.asarray(target_point, dtype=float)
        current_point = self.world_point(local_point)
        position = np.asarray(self.position, dtype=float)
        for axis_index in selected_indices:
            position[axis_index] += target_point[axis_index] - current_point[axis_index]
        self.set_transform(position=position)
        return self

    def move_anchor_axis_to(self, source_anchor, target_value, axis):
        axis_index = {"x": 0, "y": 1, "z": 2}[axis]
        current_anchor = self.world_anchor(source_anchor)
        position = np.asarray(self.position, dtype=float)
        position[axis_index] += float(target_value) - current_anchor[axis_index]
        self.set_transform(position=position)
        return self

    def rotate_about_point(self, pivot_point, rotation, rotation_order="XYZ"):
        pivot_point = np.asarray(pivot_point, dtype=float)
        if pivot_point.shape != (3,):
            raise ValueError("pivot_point must contain exactly three values")

        matrix = rotation_matrix(rotation, rotation_order)
        current_matrix = self._current_rotation_matrix()
        position = np.asarray(self.position, dtype=float)
        self.position = list(matrix @ (position - pivot_point) + pivot_point)
        self._rotation_matrix_override = matrix @ current_matrix
        return self

    def reflect_across_coordinate_plane(self, axis):
        try:
            axis_index = {"x": 0, "y": 1, "z": 2}[axis.lower()]
        except (AttributeError, KeyError):
            raise ValueError("axis must be one of 'x', 'y', or 'z'") from None

        reflection = np.eye(3)
        reflection[axis_index, axis_index] = -1.0
        position = np.asarray(self.position, dtype=float)
        self.position = list(reflection @ position)
        self._rotation_matrix_override = reflection @ self._current_rotation_matrix()
        self.faces = np.asarray(self.faces, dtype=int)[:, [0, 2, 1]]
        return self

    def world_point(self, local_point):
        if self._rotation_matrix_override is not None:
            return self._apply_matrix_transform(np.asarray([local_point], dtype=float))[0]
        return apply_transform(
            np.asarray([local_point], dtype=float),
            self.position,
            self.rotation,
            self.rotation_order,
        )[0]

    def local_bounds(self):
        return np.stack([self.local_vertices.min(axis=0), self.local_vertices.max(axis=0)])

    def world_bounds(self):
        vertices = self.vertices
        return np.stack([vertices.min(axis=0), vertices.max(axis=0)])

    def _set_anchor(self, name, point, normal=None, tangent=None):
        self._anchor_points[name] = np.asarray(point, dtype=float)
        if normal is not None:
            self._anchor_normals[name] = _normalize(normal)
        if tangent is not None:
            self._anchor_tangents[name] = _normalize(tangent)

    def _set_anchor_alias(self, alias, source):
        self._anchor_points[alias] = self._anchor_points[source]
        if source in self._anchor_normals:
            self._anchor_normals[alias] = self._anchor_normals[source]
        if source in self._anchor_tangents:
            self._anchor_tangents[alias] = self._anchor_tangents[source]

    def anchor_names(self):
        return sorted(set(self._anchor_points) | self._BBOX_ANCHOR_NAMES | {"center"})

    def _bbox_anchor(self, name):
        bounds = self.local_bounds()
        low, high = bounds[0], bounds[1]
        center = (low + high) / 2.0

        if name in ("center", "bbox_center"):
            return center

        if name == "bbox_top_center":
            return np.array([center[0], high[1], center[2]])
        if name == "bbox_bottom_center":
            return np.array([center[0], low[1], center[2]])
        if name == "bbox_left_center":
            return np.array([low[0], center[1], center[2]])
        if name == "bbox_right_center":
            return np.array([high[0], center[1], center[2]])
        if name == "bbox_front_center":
            return np.array([center[0], center[1], high[2]])
        if name == "bbox_back_center":
            return np.array([center[0], center[1], low[2]])

        corner_parts = {
            "top": high[1],
            "bottom": low[1],
            "front": high[2],
            "back": low[2],
            "left": low[0],
            "right": high[0],
        }
        if name.startswith("bbox_"):
            labels = name.removeprefix("bbox_").split("_")
            if len(labels) == 3:
                y_label, z_label, x_label = labels
                if y_label in ("top", "bottom") and z_label in ("front", "back") and x_label in ("left", "right"):
                    return np.array(
                        [
                            corner_parts[x_label],
                            corner_parts[y_label],
                            corner_parts[z_label],
                        ]
                    )

        raise KeyError(f"unknown anchor {name!r}")

    def local_anchor(self, name):
        if name in self._anchor_points:
            return self._anchor_points[name].copy()
        return self._bbox_anchor(name).copy()

    def world_anchor(self, name):
        if self._rotation_matrix_override is not None:
            return self._apply_matrix_transform(np.asarray([self.local_anchor(name)]))[0]
        return apply_transform(
            np.asarray([self.local_anchor(name)]),
            self.position,
            self.rotation,
            self.rotation_order,
        )[0]

    def _infer_normal(self, name):
        directions = []
        if "top" in name:
            directions.append(np.array([0.0, 1.0, 0.0]))
        if "bottom" in name:
            directions.append(np.array([0.0, -1.0, 0.0]))
        if "left" in name:
            directions.append(np.array([-1.0, 0.0, 0.0]))
        if "right" in name:
            directions.append(np.array([1.0, 0.0, 0.0]))
        if "front" in name:
            directions.append(np.array([0.0, 0.0, 1.0]))
        if "back" in name:
            directions.append(np.array([0.0, 0.0, -1.0]))
        if not directions:
            return None
        return _normalize(np.sum(directions, axis=0))

    def _default_tangent(self, normal):
        if normal is None:
            return None
        if abs(normal[0]) < 0.9:
            candidate = np.array([1.0, 0.0, 0.0])
        else:
            candidate = np.array([0.0, 1.0, 0.0])
        tangent = candidate - normal * np.dot(candidate, normal)
        return _normalize(tangent)

    def local_anchor_frame(self, name):
        point = self.local_anchor(name)
        normal = self._anchor_normals.get(name)
        if normal is None:
            normal = self._infer_normal(name)
        tangent = self._anchor_tangents.get(name)
        if tangent is None:
            tangent = self._default_tangent(normal)
        bitangent = None
        if normal is not None and tangent is not None:
            bitangent = _normalize(np.cross(normal, tangent))
        return AnchorFrame(point=point, normal=normal, tangent=tangent, bitangent=bitangent)

    def world_anchor_frame(self, name):
        frame = self.local_anchor_frame(name)
        normal = None
        tangent = None
        bitangent = None
        if frame.normal is not None:
            if self._rotation_matrix_override is not None:
                normal = _normalize(np.matmul(frame.normal, self._current_rotation_matrix().T))
            else:
                normal = _normalize(
                    transform_direction(frame.normal, self.rotation, self.rotation_order)
                )
        if frame.tangent is not None:
            if self._rotation_matrix_override is not None:
                tangent = _normalize(np.matmul(frame.tangent, self._current_rotation_matrix().T))
            else:
                tangent = _normalize(
                    transform_direction(frame.tangent, self.rotation, self.rotation_order)
                )
        if frame.bitangent is not None:
            if self._rotation_matrix_override is not None:
                bitangent = _normalize(
                    np.matmul(frame.bitangent, self._current_rotation_matrix().T)
                )
            else:
                bitangent = _normalize(
                    transform_direction(frame.bitangent, self.rotation, self.rotation_order)
                )
        return AnchorFrame(
            point=self.world_anchor(name),
            normal=normal,
            tangent=tangent,
            bitangent=bitangent,
        )
