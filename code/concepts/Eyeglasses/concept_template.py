from math import cos, pi, sin, sqrt

import numpy as np

from code.geometry import ConceptTemplate, Cuboid, Cylinder, Ring
from code.geometry.transforms import rotation_matrix


DEGREES_TO_RADIANS = pi / 180.0
EYEGLASSES_ROTATION_ORDER = "YXZ"
LENS_THICKNESS_TO_DEPTH = (pi / 2.0, 0.0, 0.0)


class TrapezoidalLensPair(ConceptTemplate):
    def __init__(
        self,
        lens_size,
        bridge_interval,
        lens_rotation_degrees,
        top_offset_x,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=EYEGLASSES_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                lens_size=lens_size,
                bridge_interval=bridge_interval,
                lens_rotation_degrees=lens_rotation_degrees,
                top_offset_x=top_offset_x,
            )
        )
        self.semantic = "Glasses"

    @staticmethod
    def _build_components(lens_size, bridge_interval, lens_rotation_degrees, top_offset_x):
        top_length, bottom_length, lens_height, lens_depth = lens_size
        yaw_degrees, roll_degrees = lens_rotation_degrees
        yaw = yaw_degrees * DEGREES_TO_RADIANS
        roll = roll_degrees * DEGREES_TO_RADIANS

        components = []
        for name, side_sign, signed_top_offset in (
            ("right_lens", 1.0, top_offset_x),
            ("left_lens", -1.0, -top_offset_x),
        ):
            lens_rotation = (0.0, side_sign * yaw, side_sign * roll)
            lens = Cuboid(
                height=lens_height,
                top_length=top_length,
                top_width=lens_depth,
                bottom_length=bottom_length,
                bottom_width=lens_depth,
                top_offset=(signed_top_offset, 0.0),
                rotation=lens_rotation,
            ).with_name(name)

            bridge_local_point = (signed_top_offset, 0.0, -lens_depth / 2.0)
            bridge_target = (
                side_sign
                * (top_length * cos(yaw) * cos(roll) / 2.0 + bridge_interval / 2.0),
                0.0,
                top_length * sin(yaw) / 2.0,
            )
            lens.move_local_point_to(bridge_local_point, bridge_target)
            components.append(lens)

        return components


class TrapezoidalFramePair(ConceptTemplate):
    def __init__(
        self,
        frame_size,
        bridge_interval,
        frame_rotation_degrees,
        top_offset_x,
        rim_width,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=EYEGLASSES_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                frame_size=frame_size,
                bridge_interval=bridge_interval,
                frame_rotation_degrees=frame_rotation_degrees,
                top_offset_x=top_offset_x,
                rim_width=rim_width,
            )
        )
        self.semantic = "Glasses"

    @classmethod
    def _build_components(
        cls,
        frame_size,
        bridge_interval,
        frame_rotation_degrees,
        top_offset_x,
        rim_width,
    ):
        top_length, bottom_length, frame_height, frame_depth = frame_size
        yaw_degrees, roll_degrees = frame_rotation_degrees
        yaw = yaw_degrees * DEGREES_TO_RADIANS
        roll = roll_degrees * DEGREES_TO_RADIANS
        bar_specs = cls._bar_specs(
            top_length=top_length,
            bottom_length=bottom_length,
            frame_height=frame_height,
            frame_depth=frame_depth,
            top_offset_x=top_offset_x,
            rim_width=rim_width,
        )

        components = []
        bridge_local_point = np.array([top_offset_x, 0.0, -frame_depth / 2.0])
        bridge_z_target = top_length * sin(yaw) / 2.0
        bridge_x_projection = top_length * cos(yaw) * cos(roll) / 2.0

        for side_label, side_sign in (("right", 1.0), ("left", -1.0)):
            side_rotation = (0.0, side_sign * yaw, side_sign * roll)
            matrix = rotation_matrix(side_rotation)
            bridge_target = np.array(
                [
                    side_sign * (bridge_x_projection + bridge_interval / 2.0),
                    0.0,
                    bridge_z_target,
                ]
            )
            translation = bridge_target - matrix @ bridge_local_point

            for spec in bar_specs:
                pre_position = np.asarray(spec["pre_position"], dtype=float)
                component_position = matrix @ pre_position + translation
                bar = Cuboid(
                    height=spec["height"],
                    top_length=spec["top_length"],
                    top_width=frame_depth,
                    bottom_length=spec["bottom_length"],
                    bottom_width=frame_depth,
                    top_offset=spec["top_offset"],
                    position=component_position,
                    rotation=side_rotation,
                ).with_name(f"{side_label}_{spec['name']}")
                components.append(bar)

        return components

    @staticmethod
    def _bar_specs(
        top_length,
        bottom_length,
        frame_height,
        frame_depth,
        top_offset_x,
        rim_width,
    ):
        upper_inner_length = (
            bottom_length * rim_width / frame_height
            + top_length * (frame_height - rim_width) / frame_height
        )
        lower_inner_length = (
            bottom_length * (frame_height - rim_width) / frame_height
            + top_length * rim_width / frame_height
        )
        side_height = frame_height - 2.0 * rim_width
        left_side_length = (
            rim_width
            * sqrt((top_length - top_offset_x - bottom_length) ** 2 + frame_height ** 2)
            / frame_height
        )
        right_side_length = (
            rim_width
            * sqrt((top_length + top_offset_x - bottom_length) ** 2 + frame_height ** 2)
            / frame_height
        )
        inner_length_delta = upper_inner_length - lower_inner_length

        left_side_top_offset = (
            -inner_length_delta / 2.0 - top_offset_x * side_height / frame_height
        )
        right_side_top_offset = (
            inner_length_delta / 2.0 - top_offset_x * side_height / frame_height
        )

        left_side_x = (
            -lower_inner_length / 2.0
            + top_offset_x * (frame_height - rim_width) / frame_height
            + left_side_length / 2.0
        )
        right_side_x = (
            lower_inner_length / 2.0
            + top_offset_x * (frame_height - rim_width) / frame_height
            - right_side_length / 2.0
        )

        return (
            {
                "name": "top_bar",
                "height": rim_width,
                "top_length": top_length,
                "bottom_length": upper_inner_length,
                "top_offset": (-top_offset_x * rim_width / frame_height, 0.0),
                "pre_position": (
                    top_offset_x * rim_width / frame_height,
                    (frame_height - rim_width) / 2.0,
                    0.0,
                ),
            },
            {
                "name": "bottom_bar",
                "height": rim_width,
                "top_length": lower_inner_length,
                "bottom_length": bottom_length,
                "top_offset": (-top_offset_x * rim_width / frame_height, 0.0),
                "pre_position": (
                    top_offset_x,
                    -(frame_height - rim_width) / 2.0,
                    0.0,
                ),
            },
            {
                "name": "inner_side_bar",
                "height": side_height,
                "top_length": left_side_length,
                "bottom_length": left_side_length,
                "top_offset": (left_side_top_offset, 0.0),
                "pre_position": (left_side_x, 0.0, 0.0),
            },
            {
                "name": "outer_side_bar",
                "height": side_height,
                "top_length": right_side_length,
                "bottom_length": right_side_length,
                "top_offset": (right_side_top_offset, 0.0),
                "pre_position": (right_side_x, 0.0, 0.0),
            },
        )


class RoundLensPair(ConceptTemplate):
    def __init__(
        self,
        lens_size,
        bridge_interval,
        lens_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=EYEGLASSES_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                lens_size=lens_size,
                bridge_interval=bridge_interval,
                lens_rotation_degrees=lens_rotation_degrees,
            )
        )
        self.semantic = "Glasses"

    @staticmethod
    def _build_components(lens_size, bridge_interval, lens_rotation_degrees):
        radius_x, radius_z, lens_depth = lens_size
        yaw_degrees, roll_degrees = lens_rotation_degrees
        yaw = yaw_degrees * DEGREES_TO_RADIANS
        roll = roll_degrees * DEGREES_TO_RADIANS

        components = []
        for name, side_sign in (("right_lens", 1.0), ("left_lens", -1.0)):
            lens = Cylinder(
                height=lens_depth,
                top_radius=radius_x,
                bottom_radius=radius_x,
                top_radius_z=radius_z,
                bottom_radius_z=radius_z,
            ).with_name(name)
            matrix = rotation_matrix((0.0, side_sign * yaw, side_sign * roll), "YZX")
            matrix = matrix @ rotation_matrix(LENS_THICKNESS_TO_DEPTH)
            lens.set_rotation_matrix(matrix)
            lens.set_transform(
                position=RoundLensPair._lens_pair_position(
                    matrix=matrix,
                    radius_x=radius_x,
                    depth=lens_depth,
                    bridge_interval=bridge_interval,
                    side_sign=side_sign,
                )
            )
            components.append(lens)

        return components

    @staticmethod
    def _lens_pair_position(matrix, radius_x, depth, bridge_interval, side_sign):
        right_edge = matrix @ np.array([radius_x, -depth / 2.0, 0.0])
        left_edge = matrix @ np.array([-radius_x, -depth / 2.0, 0.0])
        right_edge_x, _, right_edge_z = right_edge
        left_edge_x, _, left_edge_z = left_edge

        if side_sign > 0:
            return (-left_edge_x + bridge_interval / 2.0, 0.0, -right_edge_z)
        return (-right_edge_x - bridge_interval / 2.0, 0.0, -left_edge_z)


class RoundFramePair(ConceptTemplate):
    def __init__(
        self,
        frame_size,
        bridge_interval,
        rim_width,
        frame_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=EYEGLASSES_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                frame_size=frame_size,
                bridge_interval=bridge_interval,
                rim_width=rim_width,
                frame_rotation_degrees=frame_rotation_degrees,
            )
        )
        self.semantic = "Glasses"

    @staticmethod
    def _build_components(frame_size, bridge_interval, rim_width, frame_rotation_degrees):
        outer_radius, radius_z_reference, frame_depth = frame_size
        yaw_degrees, roll_degrees = frame_rotation_degrees
        yaw = yaw_degrees * DEGREES_TO_RADIANS
        roll = roll_degrees * DEGREES_TO_RADIANS
        x_z_ratio = outer_radius / radius_z_reference
        edge_radius_x = outer_radius * x_z_ratio

        components = []
        for name, side_sign in (("right_frame", 1.0), ("left_frame", -1.0)):
            frame = Ring(
                height=frame_depth,
                inner_top_radius=outer_radius - rim_width,
                outer_top_radius=outer_radius,
                x_z_ratio=x_z_ratio,
            ).with_name(name)
            matrix = rotation_matrix((0.0, side_sign * yaw, side_sign * roll), "YZX")
            matrix = matrix @ rotation_matrix(LENS_THICKNESS_TO_DEPTH)
            frame.set_rotation_matrix(matrix)
            frame.set_transform(
                position=RoundLensPair._lens_pair_position(
                    matrix=matrix,
                    radius_x=edge_radius_x,
                    depth=frame_depth,
                    bridge_interval=bridge_interval,
                    side_sign=side_sign,
                )
            )
            components.append(frame)

        return components


class TwoSegmentTemplePair(ConceptTemplate):
    def __init__(
        self,
        frame_interval,
        main_segment_size,
        end_segment_size,
        main_rotation_degrees,
        fold_rotation_degrees,
        hinge_offset_x,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=EYEGLASSES_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                frame_interval=frame_interval,
                main_segment_size=main_segment_size,
                end_segment_size=end_segment_size,
                main_rotation_degrees=main_rotation_degrees,
                fold_rotation_degrees=fold_rotation_degrees,
                hinge_offset_x=hinge_offset_x,
            )
        )
        self.semantic = "Leg"

    @staticmethod
    def _build_components(
        frame_interval,
        main_segment_size,
        end_segment_size,
        main_rotation_degrees,
        fold_rotation_degrees,
        hinge_offset_x,
    ):
        main_length, main_height, main_depth = main_segment_size
        end_length, end_height, end_depth = end_segment_size
        main_pitch_degrees, main_yaw_degrees = main_rotation_degrees
        fold_pitch_degrees, fold_yaw_degrees = fold_rotation_degrees
        main_pitch = main_pitch_degrees * DEGREES_TO_RADIANS
        main_yaw = main_yaw_degrees * DEGREES_TO_RADIANS
        fold_pitch = fold_pitch_degrees * DEGREES_TO_RADIANS
        fold_yaw = fold_yaw_degrees * DEGREES_TO_RADIANS
        temple_interval = frame_interval + hinge_offset_x * 2.0

        components = []
        for side_label, side_sign in (("left", -1.0), ("right", 1.0)):
            side_translation = np.array([side_sign * temple_interval / 2.0, 0.0, 0.0])
            main_rotation = (-main_pitch, -side_sign * main_yaw, 0.0)
            fold_rotation = (-fold_pitch, -side_sign * fold_yaw, 0.0)
            main_matrix = rotation_matrix(main_rotation, "YXZ")
            fold_matrix = rotation_matrix(fold_rotation, "YXZ")

            end_seed = np.array(
                [-side_sign * end_length / 2.0, -end_height / 2.0, -end_depth / 2.0]
            )
            end_pre_translation = np.array([0.0, 0.0, -main_depth])
            end_position = (
                main_matrix @ (fold_matrix @ end_seed + end_pre_translation)
                + side_translation
            )
            end_segment = Cuboid(
                height=end_height,
                top_length=end_length,
                top_width=end_depth,
            ).with_name(f"{side_label}_folded_end_segment")
            end_segment.set_rotation_matrix(main_matrix @ fold_matrix)
            end_segment.set_transform(position=end_position)
            components.append(end_segment)

            main_seed = np.array(
                [-side_sign * main_length / 2.0, -main_height / 2.0, -main_depth / 2.0]
            )
            main_segment = Cuboid(
                height=main_height,
                top_length=main_length,
                top_width=main_depth,
            ).with_name(f"{side_label}_main_segment")
            main_segment.set_rotation_matrix(main_matrix)
            main_segment.set_transform(position=main_matrix @ main_seed + side_translation)
            components.append(main_segment)

        return components


class TrifoldTemplePair(ConceptTemplate):
    def __init__(
        self,
        frame_interval,
        main_segment_size,
        end_segment_size,
        main_rotation_degrees,
        fold_rotation_degrees,
        connector_size,
        hinge_offset_x,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=EYEGLASSES_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                frame_interval=frame_interval,
                main_segment_size=main_segment_size,
                end_segment_size=end_segment_size,
                main_rotation_degrees=main_rotation_degrees,
                fold_rotation_degrees=fold_rotation_degrees,
                connector_size=connector_size,
                hinge_offset_x=hinge_offset_x,
            )
        )
        self.semantic = "Leg"

    @staticmethod
    def _build_components(
        frame_interval,
        main_segment_size,
        end_segment_size,
        main_rotation_degrees,
        fold_rotation_degrees,
        connector_size,
        hinge_offset_x,
    ):
        main_length, main_height, main_depth = main_segment_size
        end_length, end_height, end_depth = end_segment_size
        connector_length, connector_height, connector_depth = connector_size
        main_pitch_degrees, main_yaw_degrees = main_rotation_degrees
        fold_pitch_degrees, fold_yaw_degrees = fold_rotation_degrees
        main_pitch = main_pitch_degrees * DEGREES_TO_RADIANS
        main_yaw = main_yaw_degrees * DEGREES_TO_RADIANS
        fold_pitch = fold_pitch_degrees * DEGREES_TO_RADIANS
        fold_yaw = fold_yaw_degrees * DEGREES_TO_RADIANS
        temple_interval = frame_interval + hinge_offset_x * 2.0

        components = []
        for side_label, side_sign in (("left", -1.0), ("right", 1.0)):
            side_translation = np.array(
                [
                    side_sign * temple_interval / 2.0
                    + hinge_offset_x
                    + side_sign * connector_length,
                    connector_height / 2.0,
                    0.0,
                ]
            )
            main_rotation = (-main_pitch, -side_sign * main_yaw, 0.0)
            fold_rotation = (-fold_pitch, -side_sign * fold_yaw, 0.0)
            main_matrix = rotation_matrix(main_rotation, "XYZ")
            fold_matrix = rotation_matrix(fold_rotation, "XYZ")

            end_seed = np.array(
                [-side_sign * end_length / 2.0, -end_height / 2.0, -end_depth / 2.0]
            )
            end_pre_translation = np.array([0.0, 0.0, -main_depth])
            end_segment = Cuboid(
                height=end_height,
                top_length=end_length,
                top_width=end_depth,
            ).with_name(f"{side_label}_folded_end_segment")
            end_segment.set_rotation_matrix(main_matrix @ fold_matrix)
            end_segment.set_transform(
                position=main_matrix @ (fold_matrix @ end_seed + end_pre_translation)
                + side_translation
            )
            components.append(end_segment)

            main_seed = np.array(
                [-side_sign * main_length / 2.0, -main_height / 2.0, -main_depth / 2.0]
            )
            main_segment = Cuboid(
                height=main_height,
                top_length=main_length,
                top_width=main_depth,
            ).with_name(f"{side_label}_main_segment")
            main_segment.set_rotation_matrix(main_matrix)
            main_segment.set_transform(position=main_matrix @ main_seed + side_translation)
            components.append(main_segment)

            connector_seed = np.array(
                [
                    -side_sign * connector_length / 2.0,
                    -connector_height / 2.0,
                    connector_depth / 2.0,
                ]
            )
            connector = Cuboid(
                height=connector_height,
                top_length=connector_length,
                top_width=connector_depth,
                position=connector_seed + side_translation,
            ).with_name(f"{side_label}_connector")
            components.append(connector)

        return components


class NoseSupportPair(ConceptTemplate):
    def __init__(
        self,
        support_size,
        support_offset_x,
        support_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=EYEGLASSES_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                support_size=support_size,
                support_offset_x=support_offset_x,
                support_rotation_degrees=support_rotation_degrees,
            )
        )
        self.semantic = "Support"

    @staticmethod
    def _build_components(support_size, support_offset_x, support_rotation_degrees):
        support_length, support_height, support_depth = support_size
        pitch_degrees, yaw_degrees, roll_degrees = support_rotation_degrees
        pitch = pitch_degrees * DEGREES_TO_RADIANS
        yaw = yaw_degrees * DEGREES_TO_RADIANS
        roll = roll_degrees * DEGREES_TO_RADIANS

        components = []
        for name, side_sign in (("right_support", 1.0), ("left_support", -1.0)):
            support = Cuboid(
                height=support_height,
                top_length=support_length,
                top_width=support_depth,
                position=(side_sign * support_offset_x, 0.0, 0.0),
                rotation=(pitch, side_sign * yaw, side_sign * roll),
                rotation_order="ZXY",
            ).with_name(name)
            components.append(support)

        return components


class SingleEyeglassesConnector(ConceptTemplate):
    def __init__(self, connector_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=EYEGLASSES_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(self._build_components(connector_size=connector_size))
        self.semantic = "Connector"

    @staticmethod
    def _build_components(connector_size):
        connector_length, connector_height, connector_depth = connector_size
        connector = Cuboid(
            height=connector_height,
            top_length=connector_length,
            top_width=connector_depth,
        ).with_name("connector")
        connector.move_anchor_to("front_center", (0.0, 0.0, 0.0))
        return [connector]


class DualEyeglassesConnector(ConceptTemplate):
    def __init__(
        self,
        first_connector_size,
        first_connector_front_anchor,
        second_connector_size,
        second_connector_front_anchor,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=EYEGLASSES_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                first_connector_size=first_connector_size,
                first_connector_front_anchor=first_connector_front_anchor,
                second_connector_size=second_connector_size,
                second_connector_front_anchor=second_connector_front_anchor,
            )
        )
        self.semantic = "Connector"

    @staticmethod
    def _build_components(
        first_connector_size,
        first_connector_front_anchor,
        second_connector_size,
        second_connector_front_anchor,
    ):
        components = []
        for name, size, front_anchor in (
            ("first_connector", first_connector_size, first_connector_front_anchor),
            ("second_connector", second_connector_size, second_connector_front_anchor),
        ):
            connector_length, connector_height, connector_depth = size
            connector = Cuboid(
                height=connector_height,
                top_length=connector_length,
                top_width=connector_depth,
            ).with_name(name)
            connector.move_anchor_to("front_center", front_anchor)
            components.append(connector)

        return components
