"""Transform utilities for runtime geometry primitives.

The legacy templates apply Euler rotations to vertex arrays immediately.
This module keeps the same rotation convention while making transforms
explicit and reusable for vertices, anchors, and directions.
"""

from dataclasses import dataclass

import numpy as np


def _as_vector(values, name):
    vector = np.asarray(values, dtype=float)
    if vector.shape != (3,):
        raise ValueError(f"{name} must contain exactly three values")
    return vector


def get_rodrigues_matrix(axis, angle):
    axis = _as_vector(axis, "axis")
    identity = np.eye(3)
    s1 = np.array(
        [
            [np.zeros([]), -axis[2], axis[1]],
            [axis[2], np.zeros([]), -axis[0]],
            [-axis[1], axis[0], np.zeros([])],
        ]
    )
    s2 = np.matmul(axis[:, None], axis[None])
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)

    return cos_angle * identity + sin_angle * s1 + (1 - cos_angle) * s2


def rotation_matrix(rotation, rotation_order="XYZ"):
    """Return the combined matrix used by legacy ``apply_transformation``."""

    rotation = _as_vector(rotation, "rotation")
    matrices = {
        "X": get_rodrigues_matrix([1, 0, 0], rotation[0]),
        "Y": get_rodrigues_matrix([0, 1, 0], rotation[1]),
        "Z": get_rodrigues_matrix([0, 0, 1], rotation[2]),
    }

    combined = np.eye(3)
    for axis_name in rotation_order:
        if axis_name not in matrices:
            raise ValueError(f"unsupported rotation axis {axis_name!r}")
        combined = matrices[axis_name] @ combined
    return combined


def apply_transform(points, position, rotation, rotation_order="XYZ", offset_first=False):
    points = np.asarray(points, dtype=float)
    matrix = rotation_matrix(rotation, rotation_order)
    position = _as_vector(position, "position")
    if offset_first:
        return np.matmul(points + position, matrix.T)
    return np.matmul(points, matrix.T) + position


def rotate_y(points, angle):
    """Rotate one or more 3D points around the Y axis without translation."""

    points = np.asarray(points, dtype=float)
    if points.shape[-1:] != (3,):
        raise ValueError("points must have three coordinates in the last dimension")
    matrix = rotation_matrix((0.0, angle, 0.0))
    return np.matmul(points, matrix.T)


def inverse_apply_transform(
    points,
    position,
    rotation,
    rotation_order="XYZ",
    offset_first=False,
):
    points = np.asarray(points, dtype=float)
    matrix = rotation_matrix(rotation, rotation_order)
    position = _as_vector(position, "position")
    if offset_first:
        return np.matmul(points, matrix) - position
    return np.matmul(points - position, matrix)


def transform_direction(direction, rotation, rotation_order="XYZ"):
    direction = _as_vector(direction, "direction")
    matrix = rotation_matrix(rotation, rotation_order)
    return np.matmul(direction, matrix.T)


@dataclass(frozen=True)
class RadialArrayFrame:
    """Position and orientation for one item in a radial array."""

    index: int
    angle: float
    position: np.ndarray
    rotation_matrix: np.ndarray


@dataclass(frozen=True)
class Transform:
    position: tuple
    rotation: tuple
    rotation_order: str = "XYZ"
    offset_first: bool = False

    def apply_points(self, points):
        return apply_transform(
            points,
            self.position,
            self.rotation,
            self.rotation_order,
            offset_first=self.offset_first,
        )

    def inverse_apply_points(self, points):
        return inverse_apply_transform(
            points,
            self.position,
            self.rotation,
            self.rotation_order,
            offset_first=self.offset_first,
        )

    def apply_direction(self, direction):
        return transform_direction(direction, self.rotation, self.rotation_order)


def _axis_rotation(axis, angle):
    try:
        axis = axis.lower()
    except AttributeError:
        raise ValueError("radial_axis must be one of 'x', 'y', or 'z'") from None
    if axis == "x":
        return (angle, 0.0, 0.0)
    if axis == "y":
        return (0.0, angle, 0.0)
    if axis == "z":
        return (0.0, 0.0, angle)
    raise ValueError("radial_axis must be one of 'x', 'y', or 'z'")


def _rotation_step_matrix(step):
    try:
        rotation, rotation_order = step
    except (TypeError, ValueError):
        raise ValueError(
            "post_rotation_steps entries must be (rotation, rotation_order) pairs"
        ) from None
    return rotation_matrix(rotation, rotation_order)


def radial_array_frames(
    count,
    center_point,
    item_rotation=(0.0, 0.0, 0.0),
    item_rotation_order="XYZ",
    radial_axis="y",
    start_angle=0.0,
    angle_step=None,
    angle_sign=1.0,
    post_rotation_steps=(),
):
    """Return per-item frames for an equal-angle radial array.

    ``center_point`` is the item center before array rotation. ``item_rotation``
    is applied in that local item frame, then each item is rotated around
    ``radial_axis``. Optional post-rotation steps rotate the whole array frame.
    """

    array_count = int(count)
    if array_count <= 0:
        raise ValueError("count must be positive")

    center_point = _as_vector(center_point, "center_point")
    base_matrix = rotation_matrix(item_rotation, item_rotation_order)
    if angle_step is None:
        angle_step = np.pi * 2.0 / array_count

    frames = []
    for index in range(array_count):
        angle = float(start_angle) + float(angle_step) * index
        radial_matrix = rotation_matrix(
            _axis_rotation(radial_axis, float(angle_sign) * angle)
        )
        position = radial_matrix @ center_point
        matrix = radial_matrix @ base_matrix

        for step in post_rotation_steps:
            post_matrix = _rotation_step_matrix(step)
            position = post_matrix @ position
            matrix = post_matrix @ matrix

        frames.append(
            RadialArrayFrame(
                index=index,
                angle=angle,
                position=position,
                rotation_matrix=matrix,
            )
        )

    return tuple(frames)
