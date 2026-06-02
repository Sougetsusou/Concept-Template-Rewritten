from math import cos, pi, sin

import numpy as np

from code.geometry import (
    ConceptTemplate,
    Cuboid,
    Cylinder,
    radial_array_frames,
    rotate_y,
)


DEGREES_TO_RADIANS = pi / 180.0
TABLE_ROTATION_ORDER = "XYZ"


class TableTop(ConceptTemplate):
    def __init__(self, size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(size))
        self.semantic = "Body"

    @staticmethod
    def _build_components(size):
        length, thickness, depth = size
        return [
            Cuboid(
                height=thickness,
                top_length=length,
                top_width=depth,
            ).with_name("tabletop")
        ]


class CylindricalTableTop(ConceptTemplate):
    def __init__(self, size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(size))
        self.semantic = "Body"

    @staticmethod
    def _build_components(size):
        radius, thickness = size
        return [
            Cylinder(
                height=thickness,
                top_radius=radius,
            ).with_name("cylindrical_tabletop")
        ]


class LShapedTableTop(ConceptTemplate):
    def __init__(
        self,
        horizontal_size,
        branch_offset_distance,
        branch_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                horizontal_size=horizontal_size,
                branch_offset_distance=branch_offset_distance,
                branch_angle_degrees=branch_angle_degrees,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(horizontal_size, branch_offset_distance, branch_angle_degrees):
        length, thickness, depth = horizontal_size
        angle = branch_angle_degrees * DEGREES_TO_RADIANS
        distance = abs(branch_offset_distance)

        base = Cuboid(
            height=thickness,
            top_length=length,
            top_width=depth,
        ).with_name("base_leaf")

        branch = Cuboid(
            height=thickness,
            top_length=length,
            top_width=depth,
            position=(
                -length / 2.0 - distance * sin(angle),
                0.0,
                -thickness / 2.0 - distance * cos(angle),
            ),
            rotation=(0.0, angle, 0.0),
        ).with_name("angled_leaf")

        return [base, branch]


class RegularTableLegSet(ConceptTemplate):
    def __init__(
        self,
        front_leg_size,
        rear_leg_size,
        leg_count,
        leg_center_spacing,
        central_yaw_degrees,
        front_tilt_degrees,
        rear_tilt_degrees,
        mirror_rolls,
        extra_legs=(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                front_leg_size=front_leg_size,
                rear_leg_size=rear_leg_size,
                leg_count=leg_count,
                leg_center_spacing=leg_center_spacing,
                central_yaw_degrees=central_yaw_degrees,
                front_tilt_degrees=front_tilt_degrees,
                rear_tilt_degrees=rear_tilt_degrees,
                mirror_rolls=mirror_rolls,
                extra_legs=extra_legs,
            )
        )
        self.semantic = "Leg"

    @classmethod
    def _build_components(
        cls,
        front_leg_size,
        rear_leg_size,
        leg_count,
        leg_center_spacing,
        central_yaw_degrees,
        front_tilt_degrees,
        rear_tilt_degrees,
        mirror_rolls,
        extra_legs,
    ):
        front_spacing, rear_spacing, front_rear_spacing = leg_center_spacing
        front_pitch, front_roll = [
            value * DEGREES_TO_RADIANS for value in front_tilt_degrees
        ]
        rear_pitch, rear_roll = [
            value * DEGREES_TO_RADIANS for value in rear_tilt_degrees
        ]
        central_yaw = central_yaw_degrees * DEGREES_TO_RADIANS
        count = int(leg_count)
        components = []
        legs = {}

        if count == 1:
            components.append(
                cls._leg_from_center_layout(
                    "front_center_leg",
                    front_leg_size,
                    (0.0, 0.0),
                    (front_pitch, central_yaw, 0.0),
                )
            )
        elif count == 2:
            for leg_index in range(2):
                position_sign = 1.0 if leg_index == 1 else -1.0
                rotation_sign = 1.0 if leg_index == 0 else -1.0
                layout_x = position_sign * front_spacing / 2.0 * cos(central_yaw)
                layout_z = position_sign * front_spacing / 2.0 * sin(central_yaw)
                components.append(
                    cls._leg_from_center_layout(
                        f"front_leg_{leg_index + 1}",
                        front_leg_size,
                        (layout_x, layout_z),
                        (front_pitch, central_yaw, rotation_sign * front_roll),
                    )
                )
        elif count == 3:
            for leg_index in range(3):
                if leg_index < 2:
                    position_sign = 1.0 if leg_index == 1 else -1.0
                    rotation_sign = 1.0 if leg_index == 0 else -1.0
                    layout_x = (
                        position_sign * front_spacing / 2.0 * cos(central_yaw)
                        + front_rear_spacing / 2.0 * sin(central_yaw)
                    )
                    layout_z = (
                        -position_sign * front_spacing / 2.0 * sin(central_yaw)
                        + front_rear_spacing / 2.0 * cos(central_yaw)
                    )
                    components.append(
                        cls._leg_from_center_layout(
                            f"front_leg_{leg_index + 1}",
                            front_leg_size,
                            (layout_x, layout_z),
                            (front_pitch, central_yaw, rotation_sign * front_roll),
                        )
                    )
                else:
                    layout_x = -front_rear_spacing / 2.0 * sin(central_yaw)
                    layout_z = -front_rear_spacing / 2.0 * cos(central_yaw)
                    components.append(
                        cls._leg_from_center_layout(
                            "rear_center_leg",
                            rear_leg_size,
                            (layout_x, layout_z),
                            (rear_pitch, central_yaw, rear_roll),
                        )
                    )
        elif count == 4:
            for leg_index in range(4):
                position_sign = 1.0 if leg_index % 2 == 1 else -1.0
                if leg_index < 2:
                    rotation_sign = (
                        -1.0
                        if leg_index % 2 == 1 and int(mirror_rolls) == 1
                        else 1.0
                    )
                    layout_x = (
                        position_sign * front_spacing / 2.0 * cos(central_yaw)
                        + front_rear_spacing / 2.0 * sin(central_yaw)
                    )
                    layout_z = (
                        -position_sign * front_spacing / 2.0 * sin(central_yaw)
                        + front_rear_spacing / 2.0 * cos(central_yaw)
                    )
                    components.append(
                        cls._leg_from_center_layout(
                            f"front_leg_{leg_index + 1}",
                            front_leg_size,
                            (layout_x, layout_z),
                            (front_pitch, central_yaw, rotation_sign * front_roll),
                        )
                    )
                else:
                    rotation_sign = (
                        -1.0
                        if leg_index % 2 == 1 and int(mirror_rolls) == 1
                        else 1.0
                    )
                    layout_x = (
                        position_sign * rear_spacing / 2.0 * cos(central_yaw)
                        - front_rear_spacing / 2.0 * sin(central_yaw)
                    )
                    layout_z = (
                        -position_sign * rear_spacing / 2.0 * sin(central_yaw)
                        - front_rear_spacing / 2.0 * cos(central_yaw)
                    )
                    components.append(
                        cls._leg_from_center_layout(
                            f"rear_leg_{leg_index - 1}",
                            rear_leg_size,
                            (layout_x, layout_z),
                            (rear_pitch, central_yaw, rotation_sign * rear_roll),
                        )
                    )

        components.extend(cls._extra_leg_components(extra_legs))
        return components

    @staticmethod
    def _leg_from_center_layout(name, size, center_layout, rotation):
        length, height, depth = size
        center_x, center_z = center_layout
        leg = Cuboid(
            height=height,
            top_length=length,
            top_width=depth,
            position=(center_x, 0.0, center_z),
            rotation=rotation,
        ).with_name(name)
        leg.move_anchor_axis_to("top_center", 0.0, "y")
        return leg

    @staticmethod
    def _extra_leg_components(extra_legs):
        components = []
        for leg_index, spec in enumerate(extra_legs):
            length, height, depth = spec["size"]
            center_x, top_y, center_z = spec["center_layout_top"]
            pitch, yaw, roll = spec["rotation"]
            leg = Cuboid(
                height=height,
                top_length=length,
                top_width=depth,
                position=(center_x, 0.0, center_z),
                rotation=(pitch, yaw, roll),
            ).with_name(f"extra_leg_{leg_index + 1}")
            leg.move_anchor_axis_to("top_center", top_y, "y")
            components.append(leg)
        return components


class SplatTableLegSet(ConceptTemplate):
    def __init__(
        self,
        front_leg_size,
        rear_leg_size,
        leg_center_spacing,
        central_yaw_degrees,
        front_tilt_degrees,
        rear_tilt_degrees,
        front_rear_bar_size,
        side_bar_size,
        front_rear_bar_offsets,
        side_bar_offsets,
        enabled_bars,
        extra_legs=(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                front_leg_size=front_leg_size,
                rear_leg_size=rear_leg_size,
                leg_center_spacing=leg_center_spacing,
                central_yaw_degrees=central_yaw_degrees,
                front_tilt_degrees=front_tilt_degrees,
                rear_tilt_degrees=rear_tilt_degrees,
                front_rear_bar_size=front_rear_bar_size,
                side_bar_size=side_bar_size,
                front_rear_bar_offsets=front_rear_bar_offsets,
                side_bar_offsets=side_bar_offsets,
                enabled_bars=enabled_bars,
                extra_legs=extra_legs,
            )
        )
        self.semantic = "Leg"

    @classmethod
    def _build_components(
        cls,
        front_leg_size,
        rear_leg_size,
        leg_center_spacing,
        central_yaw_degrees,
        front_tilt_degrees,
        rear_tilt_degrees,
        front_rear_bar_size,
        side_bar_size,
        front_rear_bar_offsets,
        side_bar_offsets,
        enabled_bars,
        extra_legs,
    ):
        front_spacing, rear_spacing, front_rear_spacing = leg_center_spacing
        front_pitch, front_roll = [
            value * DEGREES_TO_RADIANS for value in front_tilt_degrees
        ]
        rear_pitch, rear_roll = [
            value * DEGREES_TO_RADIANS for value in rear_tilt_degrees
        ]
        central_yaw = central_yaw_degrees * DEGREES_TO_RADIANS
        front_leg_length, front_leg_height, _ = front_leg_size
        rear_leg_length, rear_leg_height, _ = rear_leg_size
        components = []
        legs = {}

        for leg_index in range(4):
            position_sign = -1.0 if leg_index % 2 == 0 else 1.0
            rotation_sign = -1.0 if leg_index % 2 == 1 else 1.0
            if leg_index < 2:
                layout_x = (
                    position_sign * front_spacing / 2.0 * cos(central_yaw)
                    + front_rear_spacing / 2.0 * sin(central_yaw)
                )
                layout_z = (
                    -position_sign * front_spacing / 2.0 * sin(central_yaw)
                    + front_rear_spacing / 2.0 * cos(central_yaw)
                )
                leg = RegularTableLegSet._leg_from_center_layout(
                    f"front_leg_{leg_index + 1}",
                    front_leg_size,
                    (layout_x, layout_z),
                    (front_pitch, central_yaw, rotation_sign * front_roll),
                )
                legs[f"front_{leg_index}"] = leg
                components.append(leg)
            else:
                layout_x = (
                    position_sign * rear_spacing / 2.0 * cos(central_yaw)
                    - front_rear_spacing / 2.0 * sin(central_yaw)
                )
                layout_z = (
                    -position_sign * rear_spacing / 2.0 * sin(central_yaw)
                    - front_rear_spacing / 2.0 * cos(central_yaw)
                )
                leg = RegularTableLegSet._leg_from_center_layout(
                    f"rear_leg_{leg_index - 1}",
                    rear_leg_size,
                    (layout_x, layout_z),
                    (rear_pitch, central_yaw, rotation_sign * rear_roll),
                )
                legs[f"rear_{leg_index - 2}"] = leg
                components.append(leg)

        front_offset, rear_offset = front_rear_bar_offsets
        if int(enabled_bars["front_width_bar"]):
            components.append(
                cls._width_bar(
                    name="front_width_bar",
                    bar_size=front_rear_bar_size,
                    spacing=front_spacing,
                    leg_length=front_leg_length,
                    first_mount=legs["front_0"].world_point(
                        (front_leg_length / 2.0, front_offset, 0.0)
                    ),
                    second_mount=legs["front_1"].world_point(
                        (-front_leg_length / 2.0, front_offset, 0.0)
                    ),
                    offset=front_offset,
                    pitch=front_pitch,
                    roll=front_roll,
                    central_yaw=central_yaw,
                )
            )
        if int(enabled_bars["rear_width_bar"]):
            components.append(
                cls._width_bar(
                    name="rear_width_bar",
                    bar_size=front_rear_bar_size,
                    spacing=rear_spacing,
                    leg_length=rear_leg_length,
                    first_mount=legs["rear_0"].world_point(
                        (rear_leg_length / 2.0, rear_offset, 0.0)
                    ),
                    second_mount=legs["rear_1"].world_point(
                        (-rear_leg_length / 2.0, rear_offset, 0.0)
                    ),
                    offset=rear_offset,
                    pitch=rear_pitch,
                    roll=rear_roll,
                    central_yaw=central_yaw,
                )
            )

        if int(enabled_bars["left_depth_bar"]):
            components.append(
                cls._depth_bar(
                    name="left_depth_bar",
                    front_leg_size=front_leg_size,
                    rear_leg_size=rear_leg_size,
                    front_leg=legs["front_0"],
                    rear_leg=legs["rear_0"],
                    side_bar_size=side_bar_size,
                    side_bar_offsets=side_bar_offsets,
                )
            )
        if int(enabled_bars["right_depth_bar"]):
            components.append(
                cls._depth_bar(
                    name="right_depth_bar",
                    front_leg_size=front_leg_size,
                    rear_leg_size=rear_leg_size,
                    front_leg=legs["front_1"],
                    rear_leg=legs["rear_1"],
                    side_bar_size=side_bar_size,
                    side_bar_offsets=side_bar_offsets,
                )
            )

        components.extend(RegularTableLegSet._extra_leg_components(extra_legs))
        return components

    @staticmethod
    def _width_bar(
        name,
        bar_size,
        spacing,
        leg_length,
        first_mount,
        second_mount,
        offset,
        pitch,
        roll,
        central_yaw,
    ):
        bar_height, bar_depth = bar_size
        span = spacing - leg_length + offset * sin(roll) * 2.0
        _ = pitch, central_yaw
        bar = Cuboid(
            height=bar_height,
            top_length=span,
            top_width=bar_depth,
        ).with_name(name)
        bar.align_axis_between_points("x", first_mount, second_mount)
        return bar

    @staticmethod
    def _depth_bar(
        name,
        front_leg_size,
        rear_leg_size,
        front_leg,
        rear_leg,
        side_bar_size,
        side_bar_offsets,
    ):
        _, _, front_depth = front_leg_size
        _, _, rear_depth = rear_leg_size
        side_bar_length, side_bar_height = side_bar_size
        front_offset, rear_offset = side_bar_offsets

        front_anchor = front_leg.world_point(
            (
                0.0,
                front_offset,
                0.0,
            )
        )
        rear_anchor = rear_leg.world_point(
            (
                0.0,
                rear_offset,
                0.0,
            )
        )
        span = np.linalg.norm(front_anchor - rear_anchor)
        if span <= 0.0:
            return Cuboid(0.0, 0.0, 0.0).with_name(name)

        bar = Cuboid(
            height=side_bar_height,
            top_length=side_bar_length,
            top_width=span - (front_depth + rear_depth) / 2.0,
        ).with_name(name)
        bar.align_axis_between_points("z", rear_anchor, front_anchor)
        return bar


class CableStayedTableLegSet(ConceptTemplate):
    def __init__(
        self,
        front_leg_size,
        rear_leg_size,
        leg_count,
        connection_size,
        leg_center_spacing,
        central_yaw_degrees,
        leg_tilt_degrees,
        extra_legs=(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                front_leg_size=front_leg_size,
                rear_leg_size=rear_leg_size,
                leg_count=leg_count,
                connection_size=connection_size,
                leg_center_spacing=leg_center_spacing,
                central_yaw_degrees=central_yaw_degrees,
                leg_tilt_degrees=leg_tilt_degrees,
                extra_legs=extra_legs,
            )
        )
        self.semantic = "Leg"

    @classmethod
    def _build_components(
        cls,
        front_leg_size,
        rear_leg_size,
        leg_count,
        connection_size,
        leg_center_spacing,
        central_yaw_degrees,
        leg_tilt_degrees,
        extra_legs,
    ):
        front_spacing, rear_spacing, front_rear_spacing = leg_center_spacing
        pitch, roll = [value * DEGREES_TO_RADIANS for value in leg_tilt_degrees]
        central_yaw = central_yaw_degrees * DEGREES_TO_RADIANS
        count = int(leg_count)
        components = []
        legs = {}

        if count == 1:
            components.append(
                RegularTableLegSet._leg_from_center_layout(
                    "center_cable_stayed_leg",
                    front_leg_size,
                    (0.0, 0.0),
                    (pitch, central_yaw, roll),
                )
            )
        elif count == 4:
            for leg_index in range(4):
                position_sign = 1.0 if leg_index % 2 == 1 else -1.0
                rotation_sign = 1.0 if leg_index == 0 else -1.0
                if leg_index < 2:
                    layout_x = (
                        position_sign * front_spacing / 2.0 * cos(central_yaw)
                        + front_rear_spacing / 2.0 * sin(central_yaw)
                    )
                    layout_z = (
                        -position_sign * front_spacing / 2.0 * sin(central_yaw)
                        + front_rear_spacing / 2.0 * cos(central_yaw)
                    )
                    leg = RegularTableLegSet._leg_from_center_layout(
                        f"front_leg_{leg_index + 1}",
                        front_leg_size,
                        (layout_x, layout_z),
                        (pitch, central_yaw, rotation_sign * roll),
                    )
                    legs[f"front_{leg_index}"] = leg
                    components.append(leg)
                else:
                    layout_x = (
                        position_sign * rear_spacing / 2.0 * cos(central_yaw)
                        - front_rear_spacing / 2.0 * sin(central_yaw)
                    )
                    layout_z = (
                        -position_sign * rear_spacing / 2.0 * sin(central_yaw)
                        - front_rear_spacing / 2.0 * cos(central_yaw)
                    )
                    leg = RegularTableLegSet._leg_from_center_layout(
                        f"rear_leg_{leg_index - 1}",
                        rear_leg_size,
                        (layout_x, layout_z),
                        (-pitch, central_yaw, rotation_sign * roll),
                    )
                    legs[f"rear_{leg_index - 2}"] = leg
                    components.append(leg)
            components.extend(
                cls._connection_bars(
                    first_pair=(legs["front_0"], legs["rear_1"]),
                    second_pair=(legs["front_1"], legs["rear_0"]),
                    connection_size=connection_size,
                )
            )

        components.extend(RegularTableLegSet._extra_leg_components(extra_legs))
        return components

    @staticmethod
    def _connection_bars(first_pair, second_pair, connection_size):
        bars = []
        for bar_index, leg_pair in enumerate((first_pair, second_pair)):
            start_leg, end_leg = leg_pair
            bars.append(
                CableStayedTableLegSet._connection_bar(
                    name=f"cable_bar_{bar_index + 1}",
                    start_leg=start_leg,
                    end_leg=end_leg,
                    connection_size=connection_size,
                )
            )
        return bars

    @staticmethod
    def _connection_bar(name, start_leg, end_leg, connection_size):
        thickness, depth = connection_size
        start_x, start_y, start_z = start_leg.world_anchor("top_center")
        end_x, end_y, end_z = end_leg.world_anchor("top_center")
        start_point = np.array((start_x, start_y - thickness / 2.0, start_z))
        end_point = np.array((end_x, end_y - thickness / 2.0, end_z))
        span = np.linalg.norm(end_point - start_point)
        bar = Cuboid(
            height=thickness,
            top_length=span,
            top_width=depth,
        ).with_name(name)
        bar.align_axis_between_points("x", start_point, end_point)
        return bar


class StarTableLegSet(ConceptTemplate):
    def __init__(
        self,
        vertical_size,
        sub_leg_size,
        sub_center_offset,
        tilt_degrees,
        central_yaw_degrees,
        horizontal_pitch_degrees,
        sub_leg_count,
        extra_legs=(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                vertical_size=vertical_size,
                sub_leg_size=sub_leg_size,
                sub_center_offset=sub_center_offset,
                tilt_degrees=tilt_degrees,
                central_yaw_degrees=central_yaw_degrees,
                horizontal_pitch_degrees=horizontal_pitch_degrees,
                sub_leg_count=sub_leg_count,
                extra_legs=extra_legs,
            )
        )
        self.semantic = "Leg"

    @staticmethod
    def _build_components(
        vertical_size,
        sub_leg_size,
        sub_center_offset,
        tilt_degrees,
        central_yaw_degrees,
        horizontal_pitch_degrees,
        sub_leg_count,
        extra_legs,
    ):
        vertical_radius, vertical_height = vertical_size
        sub_length, sub_height, sub_depth = sub_leg_size
        tilt = tilt_degrees * DEGREES_TO_RADIANS
        central_yaw = central_yaw_degrees * DEGREES_TO_RADIANS
        horizontal_pitch = horizontal_pitch_degrees * DEGREES_TO_RADIANS
        radial_count = int(sub_leg_count)
        components = [
            Cylinder(
                height=vertical_height,
                top_radius=vertical_radius,
                position=(0.0, -vertical_height / 2.0 * cos(horizontal_pitch), 0.0),
                rotation=(horizontal_pitch, central_yaw, 0.0),
            ).with_name("central_post")
        ]

        base_y = -vertical_height + sub_height / 2.0 + sub_center_offset
        radial_distance = sub_depth / 2.0 * cos(tilt)
        frames = radial_array_frames(
            count=radial_count,
            center_point=(0.0, 0.0, radial_distance),
            radial_axis="y",
            angle_sign=-1.0,
            post_rotation_steps=(((0.0, central_yaw, 0.0), "XYZ"),),
        )
        for frame in frames:
            layout_x, _, projected_depth = frame.position
            layout_y = base_y * cos(horizontal_pitch) - projected_depth * sin(
                horizontal_pitch
            )
            layout_z = (
                projected_depth * cos(horizontal_pitch)
                + base_y * sin(horizontal_pitch)
                + vertical_height / 2.0 * sin(horizontal_pitch)
            )
            components.append(
                Cuboid(
                    height=sub_height,
                    top_length=sub_length,
                    top_width=sub_depth,
                    position=(layout_x, layout_y, layout_z),
                    rotation=(tilt + horizontal_pitch, frame.angle * -1.0 + central_yaw, 0.0),
                ).with_name(f"radial_foot_{frame.index + 1}")
            )

        components.extend(RegularTableLegSet._extra_leg_components(extra_legs))
        return components


class BarCylindricalTableLeg(ConceptTemplate):
    def __init__(
        self,
        support_size,
        foot_size,
        horizontal_pitch_degrees,
        extra_legs=(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                support_size=support_size,
                foot_size=foot_size,
                horizontal_pitch_degrees=horizontal_pitch_degrees,
                extra_legs=extra_legs,
            )
        )
        self.semantic = "Leg"

    @staticmethod
    def _build_components(support_size, foot_size, horizontal_pitch_degrees, extra_legs):
        support_radius, support_height = support_size
        foot_radius, foot_height = foot_size
        pitch = horizontal_pitch_degrees * DEGREES_TO_RADIANS
        support = Cylinder(
            height=support_height,
            top_radius=support_radius,
            position=(0.0, -support_height / 2.0 * cos(pitch), 0.0),
            rotation=(pitch, 0.0, 0.0),
        ).with_name("tilted_support")
        foot = Cylinder(
            height=foot_height,
            top_radius=foot_radius,
            rotation=(pitch, 0.0, 0.0),
        ).with_name("terminal_foot")
        foot.move_anchor_to("top_center", support.world_anchor("bottom_center"))
        components = [support, foot]
        components.extend(RegularTableLegSet._extra_leg_components(extra_legs))
        return components


class BarCuboidTableLeg(ConceptTemplate):
    def __init__(
        self,
        support_size,
        foot_size,
        foot_yaw_degrees,
        horizontal_pitch_degrees,
        extra_legs=(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                support_size=support_size,
                foot_size=foot_size,
                foot_yaw_degrees=foot_yaw_degrees,
                horizontal_pitch_degrees=horizontal_pitch_degrees,
                extra_legs=extra_legs,
            )
        )
        self.semantic = "Leg"

    @staticmethod
    def _build_components(
        support_size,
        foot_size,
        foot_yaw_degrees,
        horizontal_pitch_degrees,
        extra_legs,
    ):
        support_length, support_height, support_depth = support_size
        foot_length, foot_height, foot_depth = foot_size
        foot_yaw = foot_yaw_degrees * DEGREES_TO_RADIANS
        pitch = horizontal_pitch_degrees * DEGREES_TO_RADIANS
        support = Cuboid(
            height=support_height,
            top_length=support_length,
            top_width=support_depth,
            position=(0.0, -support_height / 2.0 * cos(pitch), 0.0),
            rotation=(pitch, 0.0, 0.0),
        ).with_name("tilted_support")
        foot = Cuboid(
            height=foot_height,
            top_length=foot_length,
            top_width=foot_depth,
            rotation=(pitch, foot_yaw, 0.0),
        ).with_name("terminal_foot")
        foot.move_anchor_to("top_center", support.world_anchor("bottom_center"))
        components = [support, foot]
        components.extend(RegularTableLegSet._extra_leg_components(extra_legs))
        return components


class DeskFrameTableLegSet(ConceptTemplate):
    def __init__(
        self,
        vertical_size,
        horizontal_size,
        vertical_spacing,
        vertical_tilt_degrees,
        horizontal_pitch_degrees,
        connection_size,
        connection_count,
        first_connection_offset,
        connection_interval,
        extra_legs=(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                vertical_size=vertical_size,
                horizontal_size=horizontal_size,
                vertical_spacing=vertical_spacing,
                vertical_tilt_degrees=vertical_tilt_degrees,
                horizontal_pitch_degrees=horizontal_pitch_degrees,
                connection_size=connection_size,
                connection_count=connection_count,
                first_connection_offset=first_connection_offset,
                connection_interval=connection_interval,
                extra_legs=extra_legs,
            )
        )
        self.semantic = "Leg"

    @staticmethod
    def _build_components(
        vertical_size,
        horizontal_size,
        vertical_spacing,
        vertical_tilt_degrees,
        horizontal_pitch_degrees,
        connection_size,
        connection_count,
        first_connection_offset,
        connection_interval,
        extra_legs,
    ):
        vertical_length, vertical_height, vertical_depth = vertical_size
        horizontal_length, horizontal_height, horizontal_depth = horizontal_size
        connection_height, connection_depth = connection_size
        pitch, roll = [value * DEGREES_TO_RADIANS for value in vertical_tilt_degrees]
        horizontal_pitch = horizontal_pitch_degrees * DEGREES_TO_RADIANS
        spacing = vertical_spacing
        offset = first_connection_offset
        interval = connection_interval
        probe = Cuboid(
            height=vertical_height,
            top_length=vertical_length,
            top_width=vertical_depth,
            rotation=(pitch, 0.0, roll),
        )
        bottom_x, bottom_y, bottom_z = probe.world_anchor("bottom_center")

        components = []
        for side_index, side_sign in enumerate((-1.0, 1.0)):
            rotation_sign = 1.0 if side_index == 0 else -1.0
            components.append(
                Cuboid(
                    height=vertical_height,
                    top_length=vertical_length,
                    top_width=vertical_depth,
                    position=(side_sign * spacing / 2.0, bottom_y, 0.0),
                    rotation=(pitch, 0.0, rotation_sign * roll),
                ).with_name(f"vertical_side_{side_index + 1}")
            )
            components.append(
                Cuboid(
                    height=horizontal_height,
                    top_length=horizontal_length,
                    top_width=horizontal_depth,
                    position=(
                        side_sign * (spacing / 2.0 - bottom_x),
                        2.0 * bottom_y,
                        bottom_z,
                    ),
                    rotation=(horizontal_pitch, 0.0, 0.0),
                ).with_name(f"lower_foot_{side_index + 1}")
            )

        for connection_index in range(int(connection_count)):
            distance_down = offset + connection_index * interval
            bar_y = -(
                vertical_height / 2.0
                - distance_down * cos(pitch) * cos(roll)
            )
            bar_z = distance_down * sin(pitch)
            bar_span = spacing - vertical_length + 2.0 * distance_down * sin(roll)
            components.append(
                Cuboid(
                    height=connection_height,
                    top_length=bar_span,
                    top_width=connection_depth,
                    position=(0.0, bar_y, bar_z),
                    rotation=(pitch, 0.0, 0.0),
                ).with_name(f"connection_bar_{connection_index + 1}")
            )

        components.extend(RegularTableLegSet._extra_leg_components(extra_legs))
        return components


class TableSublayers(ConceptTemplate):
    def __init__(
        self,
        layer_size,
        layer_count,
        first_layer_y,
        layer_interval,
        extra_layers=(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                layer_size=layer_size,
                layer_count=layer_count,
                first_layer_y=first_layer_y,
                layer_interval=layer_interval,
                extra_layers=extra_layers,
            )
        )
        self.semantic = "Layer"

    @staticmethod
    def _build_components(
        layer_size,
        layer_count,
        first_layer_y,
        layer_interval,
        extra_layers,
    ):
        length, thickness, depth = layer_size
        components = []
        for layer_index in range(int(layer_count)):
            components.append(
                Cuboid(
                    height=thickness,
                    top_length=length,
                    top_width=depth,
                    position=(0.0, first_layer_y + layer_index * layer_interval, 0.0),
                ).with_name(f"layer_{layer_index + 1}")
            )
        components.extend(TableSublayers._extra_layer_components(extra_layers))
        return components

    @staticmethod
    def _extra_layer_components(extra_layers):
        components = []
        for layer_index, spec in enumerate(extra_layers):
            length, thickness, depth = spec["size"]
            components.append(
                Cuboid(
                    height=thickness,
                    top_length=length,
                    top_width=depth,
                    position=spec["position"],
                    rotation=spec["rotation"],
                ).with_name(f"extra_layer_{layer_index + 1}")
            )
        return components


class CylindricalTableSublayers(ConceptTemplate):
    def __init__(
        self,
        layer_size,
        layer_count,
        first_layer_y,
        layer_interval,
        extra_layers=(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                layer_size=layer_size,
                layer_count=layer_count,
                first_layer_y=first_layer_y,
                layer_interval=layer_interval,
                extra_layers=extra_layers,
            )
        )
        self.semantic = "Layer"

    @staticmethod
    def _build_components(
        layer_size,
        layer_count,
        first_layer_y,
        layer_interval,
        extra_layers,
    ):
        radius, thickness = layer_size
        components = []
        for layer_index in range(int(layer_count)):
            components.append(
                Cylinder(
                    height=thickness,
                    top_radius=radius,
                    position=(0.0, first_layer_y + layer_index * layer_interval, 0.0),
                ).with_name(f"cylindrical_layer_{layer_index + 1}")
            )
        components.extend(TableSublayers._extra_layer_components(extra_layers))
        return components


class TableBackboard(ConceptTemplate):
    def __init__(self, size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(size))
        self.semantic = "Board"

    @staticmethod
    def _build_components(size):
        length, height, depth = size
        board = Cuboid(
            height=height,
            top_length=length,
            top_width=depth,
        ).with_name("backboard")
        board.move_anchor_to("top_center", (0.0, 0.0, 0.0))
        return [board]


class TableDrawerAssembly(ConceptTemplate):
    def __init__(self, drawers, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(drawers))
        self.semantic = "Drawer"

    @staticmethod
    def _build_components(drawers):
        components = []
        for drawer_index, drawer in enumerate(drawers):
            components.extend(
                TableDrawerAssembly._drawer_components(
                    drawer_index=drawer_index,
                    drawer=drawer,
                )
            )
        return components

    @staticmethod
    def _drawer_components(drawer_index, drawer):
        length, height, depth = drawer["drawer_size"]
        bottom_thickness = drawer["bottom_thickness"]
        front_length, front_height, front_depth = drawer["front_size"]
        front_offset_y = drawer["front_offset_y"]
        side_thickness = drawer["side_thickness"]
        front_back_thickness = drawer["front_back_thickness"]
        drawer_x, drawer_y, drawer_z = drawer["offset"]
        components = []

        for side_index, side_sign in enumerate((-1.0, 1.0)):
            components.append(
                Cuboid(
                    height=height,
                    top_length=side_thickness,
                    top_width=depth,
                    position=(
                        side_sign * (length - side_thickness) / 2.0 + drawer_x,
                        -height / 2.0 + drawer_y,
                        drawer_z,
                    ),
                ).with_name(f"drawer_{drawer_index + 1}_side_{side_index + 1}")
            )
        for panel_index, depth_sign in enumerate((1.0, -1.0)):
            components.append(
                Cuboid(
                    height=height,
                    top_length=length - 2.0 * side_thickness,
                    top_width=front_back_thickness,
                    position=(
                        drawer_x,
                        -height / 2.0 + drawer_y,
                        depth_sign * (depth - front_back_thickness) / 2.0 + drawer_z,
                    ),
                ).with_name(f"drawer_{drawer_index + 1}_depth_panel_{panel_index + 1}")
            )
        components.append(
            Cuboid(
                height=bottom_thickness,
                top_length=length,
                top_width=depth,
                position=(
                    drawer_x,
                    -height + drawer_y - bottom_thickness / 2.0,
                    drawer_z,
                ),
            ).with_name(f"drawer_{drawer_index + 1}_bottom")
        )
        components.append(
            Cuboid(
                height=front_height,
                top_length=front_length,
                top_width=front_depth,
                position=(
                    drawer_x,
                    -height / 2.0 + drawer_y + front_offset_y,
                    drawer_z + depth / 2.0 + front_depth / 2.0,
                ),
            ).with_name(f"drawer_{drawer_index + 1}_front")
        )

        handle_length, handle_height, handle_depth = drawer["handle_size"]
        handle_offset_x, handle_offset_y = drawer["handle_offset"]
        for handle_index in range(int(drawer["handle_count"])):
            if int(drawer["handle_count"]) == 2:
                handle_sign = 1.0 if handle_index == 0 else -1.0
            else:
                handle_sign = 0.0
            components.append(
                Cuboid(
                    height=handle_height,
                    top_length=handle_length,
                    top_width=handle_depth,
                    position=(
                        drawer_x
                        + handle_offset_x
                        + handle_sign * drawer["handle_separation"] / 2.0,
                        -height / 2.0 + drawer_y + handle_offset_y,
                        drawer_z + depth / 2.0 + front_depth + front_depth / 2.0,
                    ),
                    rotation=(0.0, 0.0, drawer["handle_rotation"]),
                ).with_name(f"drawer_{drawer_index + 1}_handle_{handle_index + 1}")
            )
        return components


class TableDoorAssembly(ConceptTemplate):
    def __init__(self, doors, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(doors))
        self.semantic = "Door"

    @staticmethod
    def _build_components(doors):
        components = []
        for door_index, door in enumerate(doors):
            length, height, depth = door["door_size"]
            handle_length, handle_height, handle_depth = door["handle_size"]
            door_x, door_y, door_z = door["offset"]
            handle_offset_x, handle_offset_y = door["handle_offset"]
            door_rotation = door["door_rotation"]
            components.append(
                Cuboid(
                    height=height,
                    top_length=length,
                    top_width=depth,
                    position=(door_x, door_y - height / 2.0, door_z),
                    rotation=(0.0, door_rotation, 0.0),
                ).with_name(f"door_{door_index + 1}_panel")
            )
            components.append(
                Cuboid(
                    height=handle_height,
                    top_length=handle_length,
                    top_width=handle_depth,
                    position=(
                        door_x
                        + handle_offset_x * cos(door_rotation)
                        + handle_depth / 2.0 * sin(door_rotation),
                        door_y - height / 2.0 + handle_offset_y,
                        door_z
                        - handle_offset_x * sin(door_rotation)
                        + handle_depth / 2.0 * cos(door_rotation),
                    ),
                    rotation=(0.0, door_rotation, door["handle_rotation"]),
                ).with_name(f"door_{door_index + 1}_handle")
            )
        return components


class TableCabinetAssembly(ConceptTemplate):
    def __init__(
        self,
        top_cabinets,
        beneath_cabinets,
        drawer_inner_size,
        drawer_bottom_thickness,
        door_thickness,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                top_cabinets=top_cabinets,
                beneath_cabinets=beneath_cabinets,
                drawer_inner_size=drawer_inner_size,
                drawer_bottom_thickness=drawer_bottom_thickness,
                door_thickness=door_thickness,
            )
        )
        self.semantic = "Cabinet"

    @classmethod
    def _build_components(
        cls,
        top_cabinets,
        beneath_cabinets,
        drawer_inner_size,
        drawer_bottom_thickness,
        door_thickness,
    ):
        components = []
        for cabinet_index, cabinet in enumerate(top_cabinets):
            components.extend(
                cls._cabinet_components(
                    cabinet_index=cabinet_index,
                    cabinet=cabinet,
                    drawer_inner_size=drawer_inner_size,
                    drawer_bottom_thickness=drawer_bottom_thickness,
                    door_thickness=door_thickness,
                    is_top=True,
                )
            )
        for cabinet_index, cabinet in enumerate(beneath_cabinets):
            components.extend(
                cls._cabinet_components(
                    cabinet_index=cabinet_index,
                    cabinet=cabinet,
                    drawer_inner_size=drawer_inner_size,
                    drawer_bottom_thickness=drawer_bottom_thickness,
                    door_thickness=door_thickness,
                    is_top=False,
                )
            )
        return components

    @classmethod
    def _cabinet_components(
        cls,
        cabinet_index,
        cabinet,
        drawer_inner_size,
        drawer_bottom_thickness,
        door_thickness,
        is_top,
    ):
        components = []
        components.extend(cls._cabinet_body_components(cabinet_index, cabinet, is_top))
        components.extend(
            cls._cabinet_space_components(
                cabinet_index=cabinet_index,
                cabinet=cabinet,
                drawer_inner_size=drawer_inner_size,
                drawer_bottom_thickness=drawer_bottom_thickness,
                door_thickness=door_thickness,
                is_top=is_top,
            )
        )
        return components

    @staticmethod
    def _cabinet_body_components(cabinet_index, cabinet, is_top):
        length, height, depth = cabinet["size"]
        side_thickness = cabinet["side_thickness"]
        cap_thickness = cabinet["cap_thickness"]
        back_thickness = cabinet["back_thickness"]
        layer_count = int(cabinet["layer_count"])
        layer_thickness = cabinet["layer_thickness"]
        layer_offset = cabinet["layer_offset"]
        layer_interval = cabinet["layer_interval"]
        offset_x, offset_y, offset_z = cabinet["offset"]
        components = []

        for side_index, side_sign in enumerate((-1.0, 1.0)):
            y_center = offset_y - height / 2.0 if is_top else offset_y
            panel = Cuboid(
                height=height,
                top_length=side_thickness,
                top_width=depth,
                position=(
                    side_sign * (length - side_thickness) / 2.0 + offset_x,
                    y_center,
                    offset_z,
                ),
            ).with_name(f"cabinet_{cabinet_index + 1}_side_{side_index + 1}")
            TableCabinetAssembly._apply_top_cabinet_frame(panel, cabinet, cabinet_index, is_top)
            components.append(panel)

        for cap_index, cap_sign in enumerate((-1.0, 1.0)):
            if is_top:
                y_center = cap_sign * (height - cap_thickness) / 2.0 + offset_y - height / 2.0
            else:
                y_center = cap_sign * (height - cap_thickness) / 2.0 + offset_y
            panel = Cuboid(
                height=cap_thickness,
                top_length=length - 2.0 * side_thickness,
                top_width=depth,
                position=(offset_x, y_center, offset_z),
            ).with_name(f"cabinet_{cabinet_index + 1}_cap_{cap_index + 1}")
            TableCabinetAssembly._apply_top_cabinet_frame(panel, cabinet, cabinet_index, is_top)
            components.append(panel)

        if is_top or back_thickness != 0:
            back_center_y = offset_y - height / 2.0 if is_top else offset_y
            back = Cuboid(
                height=height,
                top_length=length,
                top_width=back_thickness,
                position=(
                    offset_x,
                    back_center_y,
                    offset_z - (depth + back_thickness) / 2.0,
                ),
            ).with_name(f"cabinet_{cabinet_index + 1}_back")
            TableCabinetAssembly._apply_top_cabinet_frame(back, cabinet, cabinet_index, is_top)
            components.append(back)
        elif components:
            duplicate = components[-1]
            components.append(duplicate)

        for layer_index in range(layer_count):
            if is_top:
                y_center = -(layer_offset + layer_index * layer_interval) - height / 2.0
            else:
                y_center = offset_y + height / 2.0 - (
                    layer_offset + layer_index * layer_interval
                )
            layer = Cuboid(
                height=layer_thickness,
                top_length=length - 2.0 * side_thickness,
                top_width=depth,
                position=(offset_x, y_center, offset_z),
            ).with_name(f"cabinet_{cabinet_index + 1}_layer_{layer_index + 1}")
            TableCabinetAssembly._apply_top_cabinet_frame(layer, cabinet, cabinet_index, is_top)
            components.append(layer)
        return components

    @staticmethod
    def _cabinet_space_components(
        cabinet_index,
        cabinet,
        drawer_inner_size,
        drawer_bottom_thickness,
        door_thickness,
        is_top,
    ):
        length, height, depth = cabinet["size"]
        offset_x, offset_y, offset_z = cabinet["offset"]
        side_thickness = cabinet["side_thickness"]
        cap_thickness = cabinet["cap_thickness"]
        layer_count = int(cabinet["layer_count"])
        layer_thickness = cabinet["layer_thickness"]
        layer_offset = cabinet["layer_offset"]
        layer_interval = cabinet["layer_interval"]
        drawer_side_thickness, drawer_depth_thickness = drawer_inner_size
        components = []

        for space_index in range(layer_count + 1):
            space_height, space_center_y = TableCabinetAssembly._space_height_and_center(
                cabinet=cabinet,
                space_index=space_index,
                is_top=is_top,
            )
            space_type = int(cabinet["space_types"][space_index])
            if space_type == 1:
                drawer_interval = cabinet["drawer_intervals"][space_index]
                drawer_offset = cabinet["drawer_offsets"][space_index]
                for side_index, side_sign in enumerate((-1.0, 1.0)):
                    panel = Cuboid(
                        height=space_height,
                        top_length=drawer_side_thickness,
                        top_width=depth - drawer_interval,
                        position=(
                            side_sign
                            * (length / 2.0 - side_thickness - drawer_side_thickness / 2.0)
                            + offset_x,
                            space_center_y + offset_y + (-height / 2.0 if is_top else 0.0),
                            offset_z + drawer_offset + drawer_interval / 2.0,
                        ),
                    ).with_name(
                        f"cabinet_{cabinet_index + 1}_space_{space_index + 1}_drawer_side_{side_index + 1}"
                    )
                    TableCabinetAssembly._apply_embedded_vertical_shift(
                        panel, cabinet, cabinet_index, is_top
                    )
                    components.append(panel)
                for panel_index, depth_sign in enumerate((1.0, -1.0)):
                    panel = Cuboid(
                        height=space_height,
                        top_length=length - 2.0 * side_thickness - 2.0 * drawer_side_thickness,
                        top_width=drawer_depth_thickness,
                        position=(
                            offset_x,
                            space_center_y + offset_y + (-height / 2.0 if is_top else 0.0),
                            offset_z
                            + depth_sign * (depth - drawer_depth_thickness) / 2.0
                            + (0.0 if is_top else drawer_offset),
                        ),
                    ).with_name(
                        f"cabinet_{cabinet_index + 1}_space_{space_index + 1}_drawer_depth_{panel_index + 1}"
                    )
                    TableCabinetAssembly._apply_embedded_vertical_shift(
                        panel, cabinet, cabinet_index, is_top
                    )
                    components.append(panel)
                bottom_y = (
                    space_center_y
                    + offset_y
                    - (space_height + drawer_bottom_thickness) / 2.0
                    + (-height / 2.0 if is_top else 0.0)
                )
                bottom = Cuboid(
                    height=drawer_bottom_thickness,
                    top_length=length - 2.0 * side_thickness,
                    top_width=depth - drawer_interval,
                    position=(
                        offset_x,
                        bottom_y,
                        offset_z + drawer_interval / 2.0 + drawer_offset,
                    ),
                ).with_name(
                    f"cabinet_{cabinet_index + 1}_space_{space_index + 1}_drawer_bottom"
                )
                TableCabinetAssembly._apply_embedded_vertical_shift(
                    bottom, cabinet, cabinet_index, is_top
                )
                components.append(bottom)

                handle_length, handle_height, handle_depth = cabinet["drawer_handle_size"]
                handle_rotation = cabinet["drawer_handle_rotations"][space_index]
                handle_separation = cabinet["drawer_handle_separations"][space_index]
                handle_offset_x, handle_offset_y = cabinet["drawer_handle_offsets"][space_index]
                handle_count = int(cabinet["drawer_handle_counts"][space_index])
                for handle_index in range(handle_count):
                    handle_sign = (
                        1.0
                        if handle_count == 2 and handle_index == 0
                        else (-1.0 if handle_count == 2 else 0.0)
                    )
                    handle = Cuboid(
                        height=handle_height,
                        top_length=handle_length,
                        top_width=handle_depth,
                        position=(
                            offset_x + handle_offset_x + handle_sign * handle_separation,
                            space_center_y
                            + offset_y
                            + handle_offset_y
                            + (-height / 2.0 if is_top else 0.0),
                            offset_z + (depth + handle_depth) / 2.0 + drawer_offset,
                        ),
                        rotation=(0.0, 0.0, handle_rotation),
                    ).with_name(
                        f"cabinet_{cabinet_index + 1}_space_{space_index + 1}_drawer_handle_{handle_index + 1}"
                    )
                    TableCabinetAssembly._apply_embedded_vertical_shift(
                        handle, cabinet, cabinet_index, is_top
                    )
                    components.append(handle)
            elif space_type == 2:
                panel = Cuboid(
                    height=space_height,
                    top_length=length - 2.0 * side_thickness,
                    top_width=door_thickness,
                    position=(
                        offset_x,
                        space_center_y + offset_y,
                        offset_z + (depth + door_thickness) / 2.0,
                    ),
                ).with_name(
                    f"cabinet_{cabinet_index + 1}_space_{space_index + 1}_door_panel"
                )
                TableCabinetAssembly._apply_embedded_vertical_shift(
                    panel, cabinet, cabinet_index, is_top
                )
                components.append(panel)

                handle_length, handle_height, handle_depth = cabinet["door_handle_size"]
                handle_offset_x, handle_offset_y = cabinet["door_handle_offsets"][space_index]
                handle = Cuboid(
                    height=handle_height,
                    top_length=handle_length,
                    top_width=handle_depth,
                    position=(
                        offset_x + handle_offset_x,
                        space_center_y + offset_y + handle_offset_y,
                        offset_z
                        + (depth + door_thickness) / 2.0
                        + (handle_depth + door_thickness) / 2.0,
                    ),
                    rotation=(0.0, 0.0, cabinet["door_handle_rotations"][space_index]),
                ).with_name(
                    f"cabinet_{cabinet_index + 1}_space_{space_index + 1}_door_handle"
                )
                TableCabinetAssembly._apply_embedded_vertical_shift(
                    handle, cabinet, cabinet_index, is_top
                )
                components.append(handle)
                _ = cap_thickness, layer_thickness
        return components

    @staticmethod
    def _space_height_and_center(cabinet, space_index, is_top):
        _, height, _ = cabinet["size"]
        cap_thickness = cabinet["cap_thickness"]
        layer_count = int(cabinet["layer_count"])
        layer_thickness = cabinet["layer_thickness"]
        layer_offset = cabinet["layer_offset"]
        layer_interval = cabinet["layer_interval"]
        if layer_count == 0:
            return height - 2.0 * cap_thickness, 0.0 if is_top else height / 2.0
        if space_index == 0:
            space_height = layer_offset - cap_thickness - layer_thickness / 2.0
            center_y = height - layer_offset / 2.0 - cap_thickness / 2.0 + layer_thickness / 4.0
            return space_height, center_y
        if space_index == layer_count:
            space_height = (
                height
                - (layer_offset + (space_index - 1) * layer_interval)
                - cap_thickness
                - layer_thickness / 2.0
            )
            center_y = cap_thickness + space_height / 2.0
            if is_top:
                center_y -= 5.0
            return space_height, center_y
        space_height = layer_interval - layer_thickness
        center_y = height - layer_offset - (2.0 * space_index - 1.0) / 2.0 * layer_interval
        return space_height, center_y

    @staticmethod
    def _apply_top_cabinet_frame(component, cabinet, cabinet_index, is_top):
        if not is_top:
            return component
        length, height, _ = cabinet["size"]
        current_x, current_y, current_z = component.position
        new_x = current_x
        new_y = current_y + height / 2.0
        if cabinet["top_cabinet_count"] == 2:
            if cabinet_index % 2 == 0:
                new_x += length / 2.0
            else:
                new_x -= length / 2.0
        component.set_transform(position=(new_x, new_y, current_z))
        return component

    @staticmethod
    def _apply_embedded_vertical_shift(component, cabinet, cabinet_index, is_top):
        length, height, _ = cabinet["size"]
        current_x, current_y, current_z = component.position
        new_x = current_x
        new_y = current_y
        if is_top:
            new_y += height / 2.0
            if cabinet["top_cabinet_count"] == 2:
                if cabinet_index % 2 == 0:
                    new_x += length / 2.0
                else:
                    new_x -= length / 2.0
        else:
            new_y -= height / 2.0
        component.set_transform(position=(new_x, new_y, current_z))
        return component


class TablePartitionSet(ConceptTemplate):
    def __init__(
        self,
        enabled_panels,
        side_panel_size,
        rear_panel_size,
        side_panel_spacing,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=TABLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                enabled_panels=enabled_panels,
                side_panel_size=side_panel_size,
                rear_panel_size=rear_panel_size,
                side_panel_spacing=side_panel_spacing,
            )
        )
        self.semantic = "Board"

    @staticmethod
    def _build_components(
        enabled_panels,
        side_panel_size,
        rear_panel_size,
        side_panel_spacing,
    ):
        side_length, side_height, side_depth = side_panel_size
        rear_height, rear_depth = rear_panel_size
        components = []
        if enabled_panels["right"]:
            components.append(
                Cuboid(
                    height=side_height,
                    top_length=side_length,
                    top_width=side_depth,
                    position=(
                        side_panel_spacing / 2.0 + side_length / 2.0,
                        side_height / 2.0,
                        0.0,
                    ),
                ).with_name("right_partition")
            )
        if enabled_panels["rear"]:
            components.append(
                Cuboid(
                    height=rear_height,
                    top_length=side_panel_spacing + 2.0 * side_length,
                    top_width=rear_depth,
                    position=(
                        0.0,
                        rear_height / 2.0,
                        -side_depth / 2.0 - rear_depth / 2.0,
                    ),
                ).with_name("rear_partition")
            )
        if enabled_panels["left"]:
            components.append(
                Cuboid(
                    height=side_height,
                    top_length=side_length,
                    top_width=side_depth,
                    position=(
                        -side_panel_spacing / 2.0 - side_length / 2.0,
                        side_height / 2.0,
                        0.0,
                    ),
                ).with_name("left_partition")
            )
        return components
