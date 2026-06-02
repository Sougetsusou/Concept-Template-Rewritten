from math import cos, pi, sin, sqrt

import numpy as np

from code.geometry import (
    ConceptTemplate,
    Cuboid,
    Cylinder,
    Torus,
    get_rodrigues_matrix,
    radial_array_frames,
    rotation_matrix,
)


DEGREES_TO_RADIANS = pi / 180.0
FAUCET_ROTATION_ORDER = "YXZ"


class Cuboidal_Base(ConceptTemplate):
    def __init__(
        self,
        box_count,
        primary_size,
        secondary_size,
        secondary_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                box_count=box_count,
                primary_size=primary_size,
                secondary_size=secondary_size,
                secondary_offset=secondary_offset,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(box_count, primary_size, secondary_size, secondary_offset):
        primary_length, primary_height, primary_depth = primary_size
        secondary_length, secondary_height, secondary_depth = secondary_size
        secondary_x, secondary_y, secondary_z = secondary_offset

        primary = Cuboid(
            height=primary_height,
            top_length=primary_length,
            top_width=primary_depth,
            position=(0.0, -primary_height / 2.0, -primary_depth / 2.0),
        ).with_name("primary_box")
        components = [primary]

        if int(box_count) == 2:
            secondary = Cuboid(
                height=secondary_height,
                top_length=secondary_length,
                top_width=secondary_depth,
                position=(
                    secondary_x,
                    -primary_height - secondary_height / 2.0 + secondary_y,
                    secondary_z - primary_depth / 2.0,
                ),
            ).with_name("secondary_box")
            components.append(secondary)

        return components


class Cylindrical_Base(ConceptTemplate):
    def __init__(
        self,
        cylinder_count,
        primary_size,
        secondary_size,
        secondary_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                cylinder_count=cylinder_count,
                primary_size=primary_size,
                secondary_size=secondary_size,
                secondary_offset=secondary_offset,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(cylinder_count, primary_size, secondary_size, secondary_offset):
        primary_radius, primary_height = primary_size
        secondary_radius, secondary_height = secondary_size
        secondary_x, secondary_y, secondary_z = secondary_offset

        primary = Cylinder(
            height=primary_height,
            top_radius=primary_radius,
            position=(0.0, -primary_height / 2.0, -primary_radius),
        ).with_name("primary_cylinder")
        components = [primary]

        if int(cylinder_count) == 2:
            secondary = Cylinder(
                height=secondary_height,
                top_radius=secondary_radius,
                position=(
                    secondary_x,
                    -primary_height - secondary_height / 2.0 + secondary_y,
                    secondary_z - primary_radius,
                ),
            ).with_name("secondary_cylinder")
            components.append(secondary)

        return components


class Curved_Base(ConceptTemplate):
    def __init__(
        self,
        tube_radius,
        arc_size,
        base_rotation,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                tube_radius=tube_radius,
                arc_size=arc_size,
                base_rotation=base_rotation,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(tube_radius, arc_size, base_rotation):
        radius = tube_radius
        chord_length, sagitta = arc_size
        base_angle = base_rotation

        center_y = -chord_length / 2.0
        center_z = chord_length ** 2 / 4.0 / sagitta
        center_position = np.array([0.0, center_y, center_z], dtype=float)
        center_angle = np.arctan(chord_length / 2.0 / center_z) * 2.0
        center_radius = center_z / np.cos(center_angle / 2.0)
        main_rotation = (center_angle / 2.0 + pi / 2.0, 0.0, -pi / 2.0)
        base_matrix = rotation_matrix((base_angle, 0.0, 0.0))
        matrix = base_matrix @ rotation_matrix(
            main_rotation,
            "ZXY",
        )

        arc = Torus(
            central_radius=center_radius,
            start_torus_radius=radius,
            exist_angle=center_angle,
        ).with_name("curved_base_arc")
        arc.set_rotation_matrix(matrix)
        arc.set_transform(position=base_matrix @ center_position)
        return [arc]


class UShapedXZ_Base(ConceptTemplate):
    def __init__(
        self,
        tube_radius,
        tube_size,
        base_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                tube_radius=tube_radius,
                tube_size=tube_size,
                base_size=base_size,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(tube_radius, tube_size, base_size):
        radius = tube_radius
        tube_span_x, tube_depth = tube_size
        base_radius, base_depth = base_size
        left_x = -tube_span_x / 2.0
        right_x = tube_span_x / 2.0
        side_center_z = base_depth + tube_depth / 2.0
        bridge_z = base_depth + tube_depth

        return [
            Cylinder(
                height=tube_depth,
                top_radius=radius,
                position=(left_x, 0.0, side_center_z),
                rotation=(pi / 2.0, 0.0, 0.0),
            ).with_name("left_upper_tube"),
            Cylinder(
                height=tube_depth,
                top_radius=radius,
                position=(right_x, 0.0, side_center_z),
                rotation=(pi / 2.0, 0.0, 0.0),
            ).with_name("right_upper_tube"),
            Cylinder(
                height=tube_span_x,
                top_radius=radius,
                position=(0.0, 0.0, bridge_z),
                rotation=(0.0, 0.0, pi / 2.0),
            ).with_name("top_bridge"),
            Cylinder(
                height=base_depth,
                top_radius=base_radius,
                position=(right_x, 0.0, base_depth / 2.0),
                rotation=(pi / 2.0, 0.0, 0.0),
            ).with_name("right_base_tube"),
            Cylinder(
                height=base_depth,
                top_radius=base_radius,
                position=(left_x, 0.0, base_depth / 2.0),
                rotation=(pi / 2.0, 0.0, 0.0),
            ).with_name("left_base_tube"),
        ]


class UShapedYZ_Base(ConceptTemplate):
    def __init__(
        self,
        tube_radius,
        tube_size,
        base_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                tube_radius=tube_radius,
                tube_size=tube_size,
                base_size=base_size,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(tube_radius, tube_size, base_size):
        radius = tube_radius
        tube_span_x, tube_drop_y = tube_size
        base_radius, base_drop_y = base_size
        left_x = -tube_span_x / 2.0
        right_x = tube_span_x / 2.0

        return [
            Cylinder(
                height=tube_drop_y,
                top_radius=radius,
                position=(left_x, -tube_drop_y / 2.0, 0.0),
            ).with_name("left_upper_tube"),
            Cylinder(
                height=tube_drop_y,
                top_radius=radius,
                position=(right_x, -tube_drop_y / 2.0, 0.0),
            ).with_name("right_upper_tube"),
            Cylinder(
                height=tube_span_x,
                top_radius=radius,
                rotation=(0.0, 0.0, pi / 2.0),
            ).with_name("top_bridge"),
            Cylinder(
                height=base_drop_y,
                top_radius=base_radius,
                position=(right_x, -(base_drop_y / 2.0 + tube_drop_y), 0.0),
            ).with_name("right_base_tube"),
            Cylinder(
                height=base_drop_y,
                top_radius=base_radius,
                position=(left_x, -(base_drop_y / 2.0 + tube_drop_y), 0.0),
            ).with_name("left_base_tube"),
        ]


class Round_Base(ConceptTemplate):
    def __init__(self, base_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(self._build_components(base_size=base_size))
        self.semantic = "Base"

    @staticmethod
    def _build_components(base_size):
        radius, depth = base_size
        base = Cylinder(
            height=depth,
            top_radius=radius,
            position=(0.0, 0.0, -depth / 2.0),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("round_base")
        return [base]


class Trifold_Spout(ConceptTemplate):
    def __init__(
        self,
        tube_radius,
        start_point,
        segment_offsets,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                tube_radius=tube_radius,
                start_point=start_point,
                segment_offsets=segment_offsets,
            )
        )
        self.semantic = "Spout"

    @classmethod
    def _build_components(cls, tube_radius, start_point, segment_offsets):
        points = cls._points_from_offsets(start_point, segment_offsets)
        return cls._pipe_segments("spout_segment", tube_radius, points)

    @staticmethod
    def _points_from_offsets(start_point, segment_offsets):
        points = [np.asarray(start_point, dtype=float)]
        for offset in segment_offsets:
            points.append(points[-1] + np.asarray(offset, dtype=float))
        return points

    @staticmethod
    def _pipe_segments(name_prefix, tube_radius, points):
        components = []
        for segment_index in range(len(points) - 1):
            start_point = points[segment_index]
            end_point = points[segment_index + 1]
            length = float(np.linalg.norm(end_point - start_point))
            segment = Cylinder(height=length, top_radius=tube_radius).with_name(
                f"{name_prefix}_{segment_index + 1}"
            )
            segment.align_axis_between_points("y", start_point, end_point)
            components.append(segment)
        return components


class ShowerRose_Spout(ConceptTemplate):
    def __init__(
        self,
        tube_radius,
        start_point,
        segment_offsets,
        has_shower_head,
        shower_head_size,
        shower_head_offset,
        shower_head_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                tube_radius=tube_radius,
                start_point=start_point,
                segment_offsets=segment_offsets,
                has_shower_head=has_shower_head,
                shower_head_size=shower_head_size,
                shower_head_offset=shower_head_offset,
                shower_head_rotation_degrees=shower_head_rotation_degrees,
            )
        )
        self.semantic = "Spout"

    @classmethod
    def _build_components(
        cls,
        tube_radius,
        start_point,
        segment_offsets,
        has_shower_head,
        shower_head_size,
        shower_head_offset,
        shower_head_rotation_degrees,
    ):
        points = Trifold_Spout._points_from_offsets(start_point, segment_offsets)
        components = Trifold_Spout._pipe_segments("shower_spout_segment", tube_radius, points)

        if int(has_shower_head):
            head_radius_x, head_radius_z, head_depth = shower_head_size
            offset_x, offset_y, offset_z = shower_head_offset
            _path_end_x, path_end_y, path_end_z = points[-1]
            mount_point = (offset_x, path_end_y + offset_y, path_end_z + offset_z)
            head_angle = -shower_head_rotation_degrees * DEGREES_TO_RADIANS
            head_matrix = rotation_matrix((head_angle, 0.0, 0.0))
            head = Cylinder(
                height=head_depth,
                top_radius=head_radius_z,
                bottom_radius=head_radius_x,
            ).with_name("shower_head")
            head.set_rotation_matrix(head_matrix)
            head.move_anchor_to("top_center", mount_point)
            components.append(head)

        return components


class Quadfold_Spout(ConceptTemplate):
    def __init__(
        self,
        tube_radius,
        start_point,
        segment_offsets,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                tube_radius=tube_radius,
                start_point=start_point,
                segment_offsets=segment_offsets,
            )
        )
        self.semantic = "Spout"

    @classmethod
    def _build_components(cls, tube_radius, start_point, segment_offsets):
        points = Trifold_Spout._points_from_offsets(start_point, segment_offsets)
        return Trifold_Spout._pipe_segments("spout_segment", tube_radius, points)


class Curved_Spout(ConceptTemplate):
    def __init__(
        self,
        tube_radius,
        end_extension_scale,
        bottom_start,
        bottom_offset,
        arc_center_offset,
        spout_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                tube_radius=tube_radius,
                end_extension_scale=end_extension_scale,
                bottom_start=bottom_start,
                bottom_offset=bottom_offset,
                arc_center_offset=arc_center_offset,
                spout_rotation_degrees=spout_rotation_degrees,
            )
        )
        self.semantic = "Spout"

    @staticmethod
    def _build_components(
        tube_radius,
        end_extension_scale,
        bottom_start,
        bottom_offset,
        arc_center_offset,
        spout_rotation_degrees,
    ):
        radius = tube_radius
        bottom_start = np.asarray(bottom_start, dtype=float)
        bottom_offset = np.asarray(bottom_offset, dtype=float)
        center = np.asarray(arc_center_offset, dtype=float)
        center_x, center_y, center_z = center
        spout_angle = spout_rotation_degrees * DEGREES_TO_RADIANS

        bottom_end = bottom_start + bottom_offset
        straight_length = float(np.linalg.norm(bottom_offset))
        bottom_segment = Cylinder(
            height=straight_length,
            top_radius=radius,
        ).with_name("bottom_straight_segment")
        bottom_segment.align_axis_between_points("y", bottom_start, bottom_end)

        center_radius = float(np.linalg.norm(center))
        center_radius_xz = sqrt(center_x ** 2 + center_z ** 2)
        center_angle = np.arctan(-center_y / center_radius_xz)
        end_length = center_radius * end_extension_scale * (spout_angle + center_angle)
        yaw = np.arctan(center_x / center_z)
        axis = np.array([center_z / center_radius_xz, 0.0, -center_x / center_radius_xz])
        tilt = -np.arctan(center_y / (center_z / np.cos(yaw)))
        tilt_matrix = get_rodrigues_matrix(axis, tilt)

        arc = Torus(
            central_radius=center_radius,
            start_torus_radius=radius,
            exist_angle=center_angle + spout_angle,
        ).with_name("curved_arc")
        arc_matrix = tilt_matrix @ rotation_matrix((-pi / 2.0, yaw, pi / 2.0), "ZXY")
        arc.set_rotation_matrix(arc_matrix)
        arc.set_transform(position=bottom_start + bottom_offset + center)

        end_segment = Cylinder(
            height=end_length,
            top_radius=radius,
        ).with_name("end_straight_segment")
        end_start_position = np.array([0.0, end_length / 2.0, 0.0])
        yaw_matrix = rotation_matrix((0.0, yaw, 0.0))
        sweep_matrix = get_rodrigues_matrix(axis, center_angle + spout_angle)
        end_matrix = sweep_matrix @ tilt_matrix @ yaw_matrix
        end_position = (
            sweep_matrix @ (tilt_matrix @ (yaw_matrix @ end_start_position) - center)
            + bottom_start
            + bottom_offset
            + center
        )
        end_segment.set_rotation_matrix(end_matrix)
        end_segment.set_transform(position=end_position)

        return [bottom_segment, arc, end_segment]


class Cuboidal_Spout(ConceptTemplate):
    def __init__(
        self,
        main_part_size,
        head_size,
        head_offset,
        main_rotation_degrees,
        head_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                main_part_size=main_part_size,
                head_size=head_size,
                head_offset=head_offset,
                main_rotation_degrees=main_rotation_degrees,
                head_rotation_degrees=head_rotation_degrees,
            )
        )
        self.semantic = "Spout"

    @staticmethod
    def _build_components(
        main_part_size,
        head_size,
        head_offset,
        main_rotation_degrees,
        head_rotation_degrees,
    ):
        main_width, main_height, main_depth = main_part_size
        head_radius, head_height = head_size
        head_offset_x, head_offset_y, head_offset_z = head_offset
        main_angle = -main_rotation_degrees * DEGREES_TO_RADIANS
        head_angle = head_rotation_degrees * DEGREES_TO_RADIANS
        main_matrix = rotation_matrix((main_angle, 0.0, 0.0))
        head_matrix = rotation_matrix((head_angle, 0.0, 0.0))

        main = Cuboid(
            height=main_height,
            top_length=main_width,
            top_width=main_depth,
        ).with_name("main_body")
        main.set_rotation_matrix(main_matrix)
        main.move_anchor_to("bottom_back_center", (0.0, 0.0, 0.0))

        head_mount_offset = np.array(
            [head_offset_x, head_offset_y, head_offset_z + main_depth - head_radius],
            dtype=float,
        )
        head_mount_point = main.world_point(
            main.local_anchor("bottom_back_center") + head_mount_offset
        )
        head = Cylinder(height=head_height, top_radius=head_radius).with_name("head")
        head.set_rotation_matrix(main_matrix @ head_matrix)
        head.move_anchor_to("top_center", head_mount_point)
        return [head, main]


class Cylindrical_Spout(ConceptTemplate):
    def __init__(
        self,
        main_part_size,
        head_size,
        head_offset,
        main_rotation_degrees,
        head_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                main_part_size=main_part_size,
                head_size=head_size,
                head_offset=head_offset,
                main_rotation_degrees=main_rotation_degrees,
                head_rotation_degrees=head_rotation_degrees,
            )
        )
        self.semantic = "Spout"

    @staticmethod
    def _build_components(
        main_part_size,
        head_size,
        head_offset,
        main_rotation_degrees,
        head_rotation_degrees,
    ):
        main_radius, main_depth = main_part_size
        head_radius, head_height = head_size
        head_offset_x, head_offset_y, head_offset_z = head_offset
        main_angle = -main_rotation_degrees * DEGREES_TO_RADIANS
        head_angle = head_rotation_degrees * DEGREES_TO_RADIANS
        main_matrix = rotation_matrix((main_angle, 0.0, 0.0))
        head_matrix = rotation_matrix((head_angle, 0.0, 0.0))

        main = Cylinder(
            height=main_depth,
            top_radius=main_radius,
        ).with_name("main_cylinder")
        main_initial_matrix = rotation_matrix((pi / 2.0, 0.0, 0.0))
        main_axis_start = main_matrix @ np.array([0.0, main_radius, 0.0])
        main.set_rotation_matrix(main_matrix @ main_initial_matrix)
        main.move_anchor_to("bottom_center", main_axis_start)

        head_mount_point = main_matrix @ np.array(
            [head_offset_x, -head_offset_y, head_offset_z + main_depth - head_radius],
            dtype=float,
        )
        head = Cylinder(height=head_height, top_radius=head_radius).with_name("head")
        head.set_rotation_matrix(main_matrix @ head_matrix)
        head.move_anchor_to("top_center", head_mount_point)
        return [head, main]


class SimplifiedZ_Switch(ConceptTemplate):
    def __init__(
        self,
        switch_count,
        switch_size,
        first_offset_x,
        second_offset_x,
        offset_yz,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                switch_count=switch_count,
                switch_size=switch_size,
                first_offset_x=first_offset_x,
                second_offset_x=second_offset_x,
                offset_yz=offset_yz,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(switch_count, switch_size, first_offset_x, second_offset_x, offset_yz):
        radius, depth = switch_size
        offset_y, offset_z = offset_yz
        x_offsets = [first_offset_x, second_offset_x]

        components = []
        for switch_index in range(int(switch_count)):
            switch = Cylinder(
                height=depth,
                top_radius=radius,
                position=(x_offsets[switch_index], offset_y, offset_z),
                rotation=(pi / 2.0, 0.0, 0.0),
            ).with_name(f"switch_{switch_index + 1}")
            components.append(switch)
        return components


class Knob_Switch(ConceptTemplate):
    def __init__(
        self,
        switch_count,
        cylinder_count,
        cylinder_sizes,
        offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                switch_count=switch_count,
                cylinder_count=cylinder_count,
                cylinder_sizes=cylinder_sizes,
                offset=offset,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(switch_count, cylinder_count, cylinder_sizes, offset):
        first_x, second_x, base_y, base_z = offset
        x_offsets = [first_x, second_x]
        components = []

        for switch_index in range(int(switch_count)):
            current_bottom_y = base_y
            for cylinder_index in range(int(cylinder_count)):
                radius, height = cylinder_sizes[cylinder_index]
                cylinder = Cylinder(
                    height=height,
                    top_radius=radius,
                    position=(
                        x_offsets[switch_index],
                        current_bottom_y + height / 2.0,
                        base_z,
                    ),
                ).with_name(f"switch_{switch_index + 1}_cylinder_{cylinder_index + 1}")
                components.append(cylinder)
                current_bottom_y += height
        return components


class HandleY_Switch(ConceptTemplate):
    def __init__(
        self,
        switch_count,
        cube_count,
        cube_sizes,
        middle_offset,
        top_offset,
        first_offset_x,
        second_offset_x,
        offset_yz,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                switch_count=switch_count,
                cube_count=cube_count,
                cube_sizes=cube_sizes,
                middle_offset=middle_offset,
                top_offset=top_offset,
                first_offset_x=first_offset_x,
                second_offset_x=second_offset_x,
                offset_yz=offset_yz,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(
        switch_count,
        cube_count,
        cube_sizes,
        middle_offset,
        top_offset,
        first_offset_x,
        second_offset_x,
        offset_yz,
    ):
        base_y, base_z = offset_yz
        middle_offset_x, middle_offset_z = middle_offset
        top_offset_x, top_offset_z = top_offset
        x_offsets = [first_offset_x, second_offset_x]
        bottom_size, middle_size, top_size = cube_sizes
        _bottom_length, bottom_height, _bottom_depth = bottom_size
        _middle_length, middle_height, _middle_depth = middle_size
        _top_length, top_height, _top_depth = top_size
        components = []

        for switch_index in range(int(switch_count)):
            side_sign = 1.0 if switch_index == 0 else -1.0
            candidate_positions = [
                (x_offsets[switch_index], base_y + bottom_height / 2.0, base_z),
                (
                    x_offsets[switch_index] + side_sign * middle_offset_x,
                    base_y + bottom_height + middle_height / 2.0,
                    base_z + middle_offset_z,
                ),
                (
                    x_offsets[switch_index] + side_sign * top_offset_x,
                    base_y + bottom_height + middle_height + top_height / 2.0,
                    base_z + top_offset_z,
                ),
            ]

            for cube_index in range(int(cube_count)):
                length, height, depth = cube_sizes[cube_index]
                cube = Cuboid(
                    height=height,
                    top_length=length,
                    top_width=depth,
                    position=candidate_positions[cube_index],
                ).with_name(f"switch_{switch_index + 1}_cube_{cube_index + 1}")
                components.append(cube)
        return components


class HandleZ_Switch(ConceptTemplate):
    def __init__(
        self,
        switch_count,
        cube_count,
        cube_sizes,
        middle_offset,
        top_offset,
        first_offset_x,
        second_offset_x,
        offset_yz,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                switch_count=switch_count,
                cube_count=cube_count,
                cube_sizes=cube_sizes,
                middle_offset=middle_offset,
                top_offset=top_offset,
                first_offset_x=first_offset_x,
                second_offset_x=second_offset_x,
                offset_yz=offset_yz,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(
        switch_count,
        cube_count,
        cube_sizes,
        middle_offset,
        top_offset,
        first_offset_x,
        second_offset_x,
        offset_yz,
    ):
        base_y, base_z = offset_yz
        middle_offset_x, middle_offset_y = middle_offset
        top_offset_x, top_offset_y = top_offset
        x_offsets = [first_offset_x, second_offset_x]
        bottom_size, middle_size, top_size = cube_sizes
        _bottom_length, _bottom_height, bottom_depth = bottom_size
        _middle_length, _middle_height, middle_depth = middle_size
        _top_length, _top_height, top_depth = top_size
        components = []

        for switch_index in range(int(switch_count)):
            side_sign = 1.0 if switch_index == 0 else -1.0
            candidate_positions = [
                (x_offsets[switch_index], base_y, base_z + bottom_depth / 2.0),
                (
                    x_offsets[switch_index] + side_sign * middle_offset_x,
                    base_y + middle_offset_y,
                    base_z + bottom_depth + middle_depth / 2.0,
                ),
                (
                    x_offsets[switch_index] + side_sign * top_offset_x,
                    base_y + top_offset_y,
                    base_z + bottom_depth + middle_depth + top_depth / 2.0,
                ),
            ]

            for cube_index in range(int(cube_count)):
                length, height, depth = cube_sizes[cube_index]
                cube = Cuboid(
                    height=height,
                    top_length=length,
                    top_width=depth,
                    position=candidate_positions[cube_index],
                ).with_name(f"switch_{switch_index + 1}_cube_{cube_index + 1}")
                components.append(cube)
        return components


class RegularY_Switch(ConceptTemplate):
    def __init__(
        self,
        main_size,
        sub_size,
        sub_offset,
        main_y_rotation_degrees,
        main_x_rotation_degrees,
        sub_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                main_size=main_size,
                sub_size=sub_size,
                sub_offset=sub_offset,
                main_y_rotation_degrees=main_y_rotation_degrees,
                main_x_rotation_degrees=main_x_rotation_degrees,
                sub_rotation_degrees=sub_rotation_degrees,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(
        main_size,
        sub_size,
        sub_offset,
        main_y_rotation_degrees,
        main_x_rotation_degrees,
        sub_rotation_degrees,
    ):
        main_radius, main_height = main_size
        sub_radius, sub_depth = sub_size
        sub_offset_y, sub_offset_z = sub_offset
        main_x_angle = -main_x_rotation_degrees * DEGREES_TO_RADIANS
        main_y_angle = -main_y_rotation_degrees * DEGREES_TO_RADIANS
        sub_angle = -sub_rotation_degrees * DEGREES_TO_RADIANS
        mount_matrix = rotation_matrix((main_x_angle, main_y_angle, 0.0))
        sub_matrix = rotation_matrix((sub_angle, 0.0, 0.0))
        tangent_distance = sqrt(main_radius ** 2 - sub_radius ** 2)
        main_center = np.array([0.0, main_height / 2.0, 0.0])
        tangent_mount_offset = np.array([0.0, sub_offset_y, tangent_distance])
        sub_bottom_offset = np.array([0.0, 0.0, sub_offset_z])

        sub = Cylinder(
            height=sub_depth,
            top_radius=sub_radius,
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("side_sub_cylinder")
        sub_initial_matrix = rotation_matrix((pi / 2.0, 0.0, 0.0))
        sub.set_rotation_matrix(mount_matrix @ sub_matrix @ sub_initial_matrix)
        sub.move_anchor_to(
            "bottom_center",
            mount_matrix @ (sub_matrix @ sub_bottom_offset + tangent_mount_offset)
            + main_center,
        )

        main = Cylinder(height=main_height, top_radius=main_radius).with_name("main_cylinder")
        main.set_rotation_matrix(mount_matrix)
        main.move_anchor_to("center", main_center)
        return [sub, main]


class RegularX_Switch(ConceptTemplate):
    def __init__(
        self,
        main_size,
        sub_size,
        sub_offset,
        main_z_rotation_degrees,
        main_x_rotation_degrees,
        sub_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                main_size=main_size,
                sub_size=sub_size,
                sub_offset=sub_offset,
                main_z_rotation_degrees=main_z_rotation_degrees,
                main_x_rotation_degrees=main_x_rotation_degrees,
                sub_rotation_degrees=sub_rotation_degrees,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(
        main_size,
        sub_size,
        sub_offset,
        main_z_rotation_degrees,
        main_x_rotation_degrees,
        sub_rotation_degrees,
    ):
        main_radius, main_length = main_size
        sub_radius, sub_height = sub_size
        sub_offset_x, sub_offset_y = sub_offset
        main_x_angle = -main_x_rotation_degrees * DEGREES_TO_RADIANS
        main_z_angle = -main_z_rotation_degrees * DEGREES_TO_RADIANS
        sub_angle = -sub_rotation_degrees * DEGREES_TO_RADIANS
        mount_matrix = rotation_matrix((main_x_angle, 0.0, main_z_angle))
        sub_matrix = rotation_matrix((0.0, 0.0, sub_angle))
        tangent_distance = sqrt(main_radius ** 2 - sub_radius ** 2)
        main_center = np.array([main_length / 2.0, 0.0, 0.0])
        tangent_mount_offset = np.array([sub_offset_x, tangent_distance, 0.0])
        sub_bottom_offset = np.array([0.0, sub_offset_y, 0.0])

        sub = Cylinder(height=sub_height, top_radius=sub_radius).with_name("side_sub_cylinder")
        sub.set_rotation_matrix(mount_matrix @ sub_matrix)
        sub.move_anchor_to(
            "bottom_center",
            mount_matrix @ (sub_matrix @ sub_bottom_offset + tangent_mount_offset)
            + main_center,
        )

        main = Cylinder(
            height=main_length,
            top_radius=main_radius,
            rotation=(0.0, 0.0, pi / 2.0),
        ).with_name("main_cylinder")
        main_initial_matrix = rotation_matrix((0.0, 0.0, pi / 2.0))
        main.set_rotation_matrix(mount_matrix @ main_initial_matrix)
        main.move_anchor_to("center", main_center)
        return [sub, main]


class RegularZ_Switch(ConceptTemplate):
    def __init__(
        self,
        main_size,
        sub_size,
        sub_offset,
        main_z_rotation_degrees,
        main_x_rotation_degrees,
        sub_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                main_size=main_size,
                sub_size=sub_size,
                sub_offset=sub_offset,
                main_z_rotation_degrees=main_z_rotation_degrees,
                main_x_rotation_degrees=main_x_rotation_degrees,
                sub_rotation_degrees=sub_rotation_degrees,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(
        main_size,
        sub_size,
        sub_offset,
        main_z_rotation_degrees,
        main_x_rotation_degrees,
        sub_rotation_degrees,
    ):
        main_radius, main_depth = main_size
        sub_radius, sub_height = sub_size
        sub_offset_z, sub_offset_y = sub_offset
        main_x_angle = main_x_rotation_degrees * DEGREES_TO_RADIANS
        main_z_angle = main_z_rotation_degrees * DEGREES_TO_RADIANS
        sub_angle = sub_rotation_degrees * DEGREES_TO_RADIANS
        mount_matrix = rotation_matrix((main_x_angle, 0.0, main_z_angle))
        sub_matrix = rotation_matrix((sub_angle, 0.0, 0.0))
        tangent_distance = sqrt(main_radius ** 2 - sub_radius ** 2)
        main_center = np.array([0.0, 0.0, main_depth / 2.0])
        tangent_mount_offset = np.array([0.0, tangent_distance, sub_offset_z])
        sub_bottom_offset = np.array([0.0, sub_offset_y, 0.0])

        sub = Cylinder(height=sub_height, top_radius=sub_radius).with_name("side_sub_cylinder")
        sub.set_rotation_matrix(mount_matrix @ sub_matrix)
        sub.move_anchor_to(
            "bottom_center",
            mount_matrix @ (sub_matrix @ sub_bottom_offset + tangent_mount_offset)
            + main_center,
        )

        main = Cylinder(
            height=main_depth,
            top_radius=main_radius,
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("main_cylinder")
        main_initial_matrix = rotation_matrix((pi / 2.0, 0.0, 0.0))
        main.set_rotation_matrix(mount_matrix @ main_initial_matrix)
        main.move_anchor_to("center", main_center)
        return [sub, main]


class TShaped_Switch(ConceptTemplate):
    def __init__(
        self,
        lower_size,
        middle_size,
        top_bar_size,
        top_bar_offset,
        top_bar_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                lower_size=lower_size,
                middle_size=middle_size,
                top_bar_size=top_bar_size,
                top_bar_offset=top_bar_offset,
                top_bar_rotation_degrees=top_bar_rotation_degrees,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(lower_size, middle_size, top_bar_size, top_bar_offset, top_bar_rotation_degrees):
        lower_radius, lower_height = lower_size
        middle_radius, middle_height = middle_size
        top_length, top_height, top_depth = top_bar_size
        top_offset_z = top_bar_offset
        top_angle = top_bar_rotation_degrees * DEGREES_TO_RADIANS

        lower = Cylinder(
            height=lower_height,
            top_radius=lower_radius,
            position=(0.0, lower_height / 2.0, 0.0),
        ).with_name("lower_cylinder")
        middle = Cylinder(
            height=middle_height,
            top_radius=middle_radius,
            position=(0.0, lower_height + middle_height / 2.0, 0.0),
        ).with_name("middle_cylinder")
        top = Cuboid(
            height=top_height,
            top_length=top_length,
            top_width=top_depth,
        ).with_name("top_bar")
        top_pivot = middle.world_anchor("top_center")
        top.move_anchor_to(
            "center",
            top_pivot + np.array([0.0, top_height / 2.0, top_offset_z]),
        )
        top.rotate_about_point(top_pivot, (0.0, top_angle, 0.0))
        return [lower, middle, top]


class Lever_Switch(ConceptTemplate):
    def __init__(
        self,
        base_size,
        tube_radius,
        start_point,
        segment_offsets,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                base_size=base_size,
                tube_radius=tube_radius,
                start_point=start_point,
                segment_offsets=segment_offsets,
            )
        )
        self.semantic = "Switch"

    @classmethod
    def _build_components(cls, base_size, tube_radius, start_point, segment_offsets):
        base_radius, base_height = base_size
        points = Trifold_Spout._points_from_offsets(start_point, segment_offsets)
        lever_origin_offset = np.array([0.0, base_height, base_radius])
        shifted_points = [point + lever_origin_offset for point in points]
        components = Trifold_Spout._pipe_segments("lever_segment", tube_radius, shifted_points)
        base = Cylinder(
            height=base_height,
            top_radius=base_radius,
            position=(0.0, base_height / 2.0, 0.0),
        ).with_name("base_cylinder")
        components.append(base)
        return components


class Cuboidal_Switch(ConceptTemplate):
    def __init__(
        self,
        main_size,
        sub_size,
        sub_offset,
        switch_rotation_degrees,
        sub_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                main_size=main_size,
                sub_size=sub_size,
                sub_offset=sub_offset,
                switch_rotation_degrees=switch_rotation_degrees,
                sub_rotation_degrees=sub_rotation_degrees,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(
        main_size,
        sub_size,
        sub_offset,
        switch_rotation_degrees,
        sub_rotation_degrees,
    ):
        main_length, main_height, main_depth = main_size
        sub_length, sub_height, sub_depth = sub_size
        sub_offset_y, sub_offset_z = sub_offset
        switch_angle = switch_rotation_degrees * DEGREES_TO_RADIANS
        sub_angle = sub_rotation_degrees * DEGREES_TO_RADIANS
        offset_z = sub_depth / 2.0 + sub_offset_z
        sub_position = np.array(
            [
                0.0,
                offset_z * sin(sub_angle)
                + sub_offset_y
                + main_height / 2.0
                - sub_height / 2.0 * cos(sub_angle),
                offset_z * cos(sub_angle),
            ]
        )
        switch_matrix = rotation_matrix((0.0, -switch_angle, 0.0))

        sub = Cuboid(
            height=sub_height,
            top_length=sub_length,
            top_width=sub_depth,
            rotation=(-sub_angle, 0.0, 0.0),
        ).with_name("sub_handle")
        sub_initial_matrix = rotation_matrix((-sub_angle, 0.0, 0.0))
        sub.set_rotation_matrix(switch_matrix @ sub_initial_matrix)
        sub.set_transform(
            position=switch_matrix @ sub_position
            + np.array([0.0, main_height / 2.0, 0.0])
        )

        main = Cuboid(
            height=main_height,
            top_length=main_length,
            top_width=main_depth,
            position=(0.0, main_height / 2.0, 0.0),
            rotation=(0.0, -switch_angle, 0.0),
        ).with_name("main_body")
        return [sub, main]


class RotaryX_Switch(ConceptTemplate):
    def __init__(
        self,
        main_size_1,
        main_size_2,
        switch_offsets_x,
        sub_size,
        sub_offset,
        tilt_degrees,
        first_rotation_degrees,
        second_rotation_degrees,
        switch_existence,
        sub_count,
        switch_interval,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                main_size_1=main_size_1,
                main_size_2=main_size_2,
                switch_offsets_x=switch_offsets_x,
                sub_size=sub_size,
                sub_offset=sub_offset,
                tilt_degrees=tilt_degrees,
                first_rotation_degrees=first_rotation_degrees,
                second_rotation_degrees=second_rotation_degrees,
                switch_existence=switch_existence,
                sub_count=sub_count,
                switch_interval=switch_interval,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(
        main_size_1,
        main_size_2,
        switch_offsets_x,
        sub_size,
        sub_offset,
        tilt_degrees,
        first_rotation_degrees,
        second_rotation_degrees,
        switch_existence,
        sub_count,
        switch_interval,
    ):
        first_main_radius, first_main_length = main_size_1
        second_main_radius, second_main_length = main_size_2
        sub_length, sub_height, sub_depth = sub_size
        sub_offset_x = sub_offset
        tilt_angle = tilt_degrees * DEGREES_TO_RADIANS
        rotations = [
            first_rotation_degrees * DEGREES_TO_RADIANS,
            second_rotation_degrees * DEGREES_TO_RADIANS,
        ]
        existences = [int(switch_existence[0]) * -1, int(switch_existence[1])]
        components = []
        blade_count = int(sub_count)

        for switch_index, existence in enumerate(existences):
            if existence == 0:
                continue
            offset_x = switch_offsets_x[switch_index]
            first_center_x = offset_x + existence * (switch_interval / 2.0 + first_main_length / 2.0)
            second_center_x = (
                offset_x
                + existence * (switch_interval / 2.0 + first_main_length + second_main_length / 2.0)
            )
            components.append(
                Cylinder(
                    height=first_main_length,
                    top_radius=first_main_radius,
                    position=(first_center_x, 0.0, 0.0),
                    rotation=(0.0, 0.0, pi / 2.0),
                ).with_name(f"switch_{switch_index + 1}_inner_cylinder")
            )
            components.append(
                Cylinder(
                    height=second_main_length,
                    top_radius=second_main_radius,
                    position=(second_center_x, 0.0, 0.0),
                    rotation=(0.0, 0.0, pi / 2.0),
                ).with_name(f"switch_{switch_index + 1}_outer_cylinder")
            )

            blade_mount_point = np.array(
                [
                offset_x
                + existence
                * (
                    first_main_length
                    + second_main_length
                    - sub_length / 2.0
                    + sub_offset_x
                    + switch_interval / 2.0
                ),
                0.0,
                0.0,
                ]
            )
            if blade_count <= 0:
                continue
            for frame in radial_array_frames(
                count=blade_count,
                center_point=(0.0, 0.0, 0.0),
                item_rotation=(0.0, 0.0, -tilt_angle),
                radial_axis="x",
                start_angle=rotations[switch_index],
            ):
                blade_center_offset = np.array(
                    [0.0, cos(tilt_angle) * sub_height / 2.0, 0.0]
                )
                sub = Cuboid(
                    height=sub_height,
                    top_length=sub_length,
                    top_width=sub_depth,
                    position=blade_center_offset,
                    rotation=(0.0, 0.0, -tilt_angle),
                ).with_name(f"switch_{switch_index + 1}_sub_{frame.index + 1}")
                sub.set_rotation_matrix(frame.rotation_matrix)
                sub.set_transform(
                    position=frame.rotation_matrix @ blade_center_offset
                    + blade_mount_point
                )
                components.append(sub)
        return components


class RotaryY_Switch(ConceptTemplate):
    def __init__(
        self,
        main_size_1,
        main_size_2,
        switch_offsets_x,
        sub_size,
        sub_offset,
        tilt_degrees,
        first_rotation_degrees,
        second_rotation_degrees,
        switch_count,
        sub_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                main_size_1=main_size_1,
                main_size_2=main_size_2,
                switch_offsets_x=switch_offsets_x,
                sub_size=sub_size,
                sub_offset=sub_offset,
                tilt_degrees=tilt_degrees,
                first_rotation_degrees=first_rotation_degrees,
                second_rotation_degrees=second_rotation_degrees,
                switch_count=switch_count,
                sub_count=sub_count,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(
        main_size_1,
        main_size_2,
        switch_offsets_x,
        sub_size,
        sub_offset,
        tilt_degrees,
        first_rotation_degrees,
        second_rotation_degrees,
        switch_count,
        sub_count,
    ):
        first_main_radius, first_main_height = main_size_1
        second_main_radius, second_main_height = main_size_2
        sub_length, sub_height, sub_depth = sub_size
        sub_offset_y = sub_offset
        tilt_angle = tilt_degrees * DEGREES_TO_RADIANS
        rotations = [
            first_rotation_degrees * DEGREES_TO_RADIANS,
            second_rotation_degrees * DEGREES_TO_RADIANS,
        ]
        components = []
        blade_count = int(sub_count)

        for switch_index in range(int(switch_count)):
            offset_x = switch_offsets_x[switch_index]
            components.append(
                Cylinder(
                    height=first_main_height,
                    top_radius=first_main_radius,
                    position=(offset_x, first_main_height / 2.0, 0.0),
                ).with_name(f"switch_{switch_index + 1}_lower_cylinder")
            )
            components.append(
                Cylinder(
                    height=second_main_height,
                    top_radius=second_main_radius,
                    position=(offset_x, first_main_height + second_main_height / 2.0, 0.0),
                ).with_name(f"switch_{switch_index + 1}_upper_cylinder")
            )

            blade_mount_point = np.array(
                [
                offset_x,
                first_main_height + second_main_height - sub_height / 2.0 + sub_offset_y,
                0.0,
                ]
            )
            if blade_count <= 0:
                continue
            for frame in radial_array_frames(
                count=blade_count,
                center_point=(0.0, 0.0, 0.0),
                item_rotation=(-tilt_angle, 0.0, 0.0),
                radial_axis="y",
                start_angle=rotations[switch_index],
            ):
                blade_center_offset = np.array(
                    [0.0, 0.0, cos(tilt_angle) * sub_depth / 2.0]
                )
                sub = Cuboid(
                    height=sub_height,
                    top_length=sub_length,
                    top_width=sub_depth,
                    position=blade_center_offset,
                    rotation=(-tilt_angle, 0.0, 0.0),
                ).with_name(f"switch_{switch_index + 1}_sub_{frame.index + 1}")
                sub.set_rotation_matrix(frame.rotation_matrix)
                sub.set_transform(
                    position=frame.rotation_matrix @ blade_center_offset
                    + blade_mount_point
                )
                components.append(sub)
        return components


class RotaryZ_Switch(ConceptTemplate):
    def __init__(
        self,
        main_size_1,
        main_size_2,
        switch_offsets_x,
        sub_size,
        sub_offset,
        tilt_degrees,
        first_rotation_degrees,
        second_rotation_degrees,
        switch_count,
        sub_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=FAUCET_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                main_size_1=main_size_1,
                main_size_2=main_size_2,
                switch_offsets_x=switch_offsets_x,
                sub_size=sub_size,
                sub_offset=sub_offset,
                tilt_degrees=tilt_degrees,
                first_rotation_degrees=first_rotation_degrees,
                second_rotation_degrees=second_rotation_degrees,
                switch_count=switch_count,
                sub_count=sub_count,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(
        main_size_1,
        main_size_2,
        switch_offsets_x,
        sub_size,
        sub_offset,
        tilt_degrees,
        first_rotation_degrees,
        second_rotation_degrees,
        switch_count,
        sub_count,
    ):
        first_main_radius, first_main_depth = main_size_1
        second_main_radius, second_main_depth = main_size_2
        sub_length, sub_height, sub_depth = sub_size
        sub_offset_z = sub_offset
        tilt_angle = tilt_degrees * DEGREES_TO_RADIANS
        rotations = [
            first_rotation_degrees * DEGREES_TO_RADIANS,
            second_rotation_degrees * DEGREES_TO_RADIANS,
        ]
        components = []
        blade_count = int(sub_count)

        for switch_index in range(int(switch_count)):
            offset_x = switch_offsets_x[switch_index]
            components.append(
                Cylinder(
                    height=first_main_depth,
                    top_radius=first_main_radius,
                    position=(offset_x, 0.0, first_main_depth / 2.0),
                    rotation=(pi / 2.0, 0.0, 0.0),
                ).with_name(f"switch_{switch_index + 1}_front_cylinder")
            )
            components.append(
                Cylinder(
                    height=second_main_depth,
                    top_radius=second_main_radius,
                    position=(offset_x, 0.0, first_main_depth + second_main_depth / 2.0),
                    rotation=(pi / 2.0, 0.0, 0.0),
                ).with_name(f"switch_{switch_index + 1}_rear_cylinder")
            )

            blade_mount_point = np.array(
                [
                offset_x,
                0.0,
                first_main_depth + second_main_depth - sub_depth / 2.0 + sub_offset_z,
                ]
            )
            if blade_count <= 0:
                continue
            for frame in radial_array_frames(
                count=blade_count,
                center_point=(0.0, 0.0, 0.0),
                item_rotation=(0.0, -tilt_angle, 0.0),
                radial_axis="z",
                start_angle=rotations[switch_index],
            ):
                blade_center_offset = np.array(
                    [cos(tilt_angle) * sub_length / 2.0, 0.0, 0.0]
                )
                sub = Cuboid(
                    height=sub_height,
                    top_length=sub_length,
                    top_width=sub_depth,
                    position=blade_center_offset,
                    rotation=(0.0, -tilt_angle, 0.0),
                ).with_name(f"switch_{switch_index + 1}_sub_{frame.index + 1}")
                sub.set_rotation_matrix(frame.rotation_matrix)
                sub.set_transform(
                    position=frame.rotation_matrix @ blade_center_offset
                    + blade_mount_point
                )
                components.append(sub)
        return components
