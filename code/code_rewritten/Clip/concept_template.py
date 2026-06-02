from copy import deepcopy
from math import cos, pi, sin

import numpy as np

from code.geometry_rewritten import ConceptTemplate, Cuboid, Ring


DEGREES_TO_RADIANS = pi / 180.0
CLIP_ROTATION_ORDER = "YXZ"


class RegularClipLever(ConceptTemplate):
    def __init__(
        self,
        support_size,
        support_inner_half_gap,
        handle_size,
        handle_offset,
        handle_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=CLIP_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                support_size=support_size,
                support_inner_half_gap=support_inner_half_gap,
                handle_size=handle_size,
                handle_offset=handle_offset,
                handle_rotation_degrees=handle_rotation_degrees,
            )
        )
        self.semantic = "Lever"

    @staticmethod
    def _build_components(
        support_size,
        support_inner_half_gap,
        handle_size,
        handle_offset,
        handle_rotation_degrees,
    ):
        support_length, support_height, support_width = support_size
        handle_length, handle_height, handle_width = handle_size
        handle_rotation = handle_rotation_degrees * DEGREES_TO_RADIANS

        left_support = Cuboid(
            height=support_height,
            top_length=support_length,
            top_width=support_width,
        ).with_name("left_support_block")
        left_support.move_anchor_to(
            "right_center",
            (-support_inner_half_gap, 0.0, 0.0),
        )

        right_support = Cuboid(
            height=support_height,
            top_length=support_length,
            top_width=support_width,
        ).with_name("right_support_block")
        right_support.move_anchor_to(
            "left_center",
            (support_inner_half_gap, 0.0, 0.0),
        )

        handle_y = handle_offset * cos(handle_rotation)
        positive_handle_z = (
            (support_width + handle_width) / 2.0
            - handle_offset * sin(handle_rotation)
        )
        negative_handle_z = -positive_handle_z

        positive_handle = Cuboid(
            height=handle_height,
            top_length=handle_length,
            top_width=handle_width,
            position=(0.0, handle_y, positive_handle_z),
            rotation=(-handle_rotation, 0.0, 0.0),
        ).with_name("positive_z_handle")

        negative_handle = Cuboid(
            height=handle_height,
            top_length=handle_length,
            top_width=handle_width,
            position=(0.0, handle_y, negative_handle_z),
            rotation=(handle_rotation, 0.0, 0.0),
        ).with_name("negative_z_handle")

        return [left_support, right_support, positive_handle, negative_handle]


class StraightClipJaw(ConceptTemplate):
    def __init__(
        self,
        jaw_size,
        jaw_half_separation,
        jaw_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=CLIP_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                jaw_size=jaw_size,
                jaw_half_separation=jaw_half_separation,
                jaw_rotation_degrees=jaw_rotation_degrees,
            )
        )
        self.semantic = "Jaw"

    @staticmethod
    def _build_components(jaw_size, jaw_half_separation, jaw_rotation_degrees):
        jaw_length, jaw_height, jaw_width = jaw_size
        jaw_rotation = jaw_rotation_degrees * DEGREES_TO_RADIANS

        positive_jaw = Cuboid(
            height=jaw_height,
            top_length=jaw_length,
            top_width=jaw_width,
            position=(0.0, 0.0, jaw_half_separation),
        ).with_name("positive_z_jaw")
        positive_jaw.rotate_about_point((0.0, 0.0, 0.0), (-jaw_rotation, 0.0, 0.0))

        negative_jaw = Cuboid(
            height=jaw_height,
            top_length=jaw_length,
            top_width=jaw_width,
            position=(0.0, 0.0, -jaw_half_separation),
        ).with_name("negative_z_jaw")
        negative_jaw.rotate_about_point((0.0, 0.0, 0.0), (jaw_rotation, 0.0, 0.0))

        return [positive_jaw, negative_jaw]


class CurvedClipJaw(ConceptTemplate):
    def __init__(
        self,
        outer_radius,
        inner_radius,
        jaw_height,
        central_angle_degrees,
        jaw_half_separation,
        jaw_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=CLIP_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                outer_radius=outer_radius,
                inner_radius=inner_radius,
                jaw_height=jaw_height,
                central_angle_degrees=central_angle_degrees,
                jaw_half_separation=jaw_half_separation,
                jaw_rotation_degrees=jaw_rotation_degrees,
            )
        )
        self.semantic = "Jaw"

    @staticmethod
    def _build_components(
        outer_radius,
        inner_radius,
        jaw_height,
        central_angle_degrees,
        jaw_half_separation,
        jaw_rotation_degrees,
    ):
        centerline_radius = (outer_radius + inner_radius) / 2.0
        central_angle = central_angle_degrees * DEGREES_TO_RADIANS
        jaw_rotation = jaw_rotation_degrees * DEGREES_TO_RADIANS

        positive_jaw = Ring(
            height=jaw_height,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=central_angle,
            rotation=(pi, pi / 2.0, -pi / 2.0),
        ).with_name("positive_z_curved_jaw")
        positive_jaw.rotate_about_point(
            (0.0, 0.0, -centerline_radius),
            (jaw_rotation, 0.0, 0.0),
        )
        positive_jaw.set_transform(
            position=np.asarray(positive_jaw.position, dtype=float)
            + np.array((0.0, 0.0, centerline_radius - jaw_half_separation))
        )

        negative_jaw = deepcopy(positive_jaw).with_name("negative_z_curved_jaw")
        negative_jaw.reflect_across_coordinate_plane("z")

        return [positive_jaw, negative_jaw]
