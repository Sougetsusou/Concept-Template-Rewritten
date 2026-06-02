from math import atan, cos, pi, sin, sqrt, tan

import numpy as np

from code.geometry import ConceptTemplate, Cuboid, Cylinder, Ring, rotate_y


DEGREES_TO_RADIANS = pi / 180.0


class LayeredCuboidalScissorsShaft(ConceptTemplate):
    def __init__(
        self,
        layer_size,
        layer_offset_z,
        layer_yaw_degrees,
        left_layer_above=True,
        central_shaft_enabled=False,
        central_shaft_size=(0, 0),
        central_shaft_offset=(0, 0, 0),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                layer_size=layer_size,
                layer_offset_z=layer_offset_z,
                layer_yaw_degrees=layer_yaw_degrees,
                left_layer_above=left_layer_above,
                central_shaft_enabled=central_shaft_enabled,
                central_shaft_size=central_shaft_size,
                central_shaft_offset=central_shaft_offset,
            )
        )
        self.semantic = "Shaft"

    @staticmethod
    def _layer(name, size, center_y, center_z, yaw):
        layer_length, layer_height, layer_width = size
        return Cuboid(
            height=layer_height,
            top_length=layer_length,
            top_width=layer_width,
            position=(0.0, center_y, center_z),
            rotation=(0.0, yaw, 0.0),
        ).with_name(name)

    @classmethod
    def _build_components(
        cls,
        layer_size,
        layer_offset_z,
        layer_yaw_degrees,
        left_layer_above,
        central_shaft_enabled,
        central_shaft_size,
        central_shaft_offset,
    ):
        _, layer_height, _ = layer_size
        layer_yaw = layer_yaw_degrees * DEGREES_TO_RADIANS
        left_y_sign = 1.0 if left_layer_above else -1.0
        components = [
            cls._layer(
                "left_layer",
                layer_size,
                left_y_sign * layer_height / 2.0,
                layer_offset_z,
                layer_yaw,
            ),
            cls._layer(
                "right_layer",
                layer_size,
                -left_y_sign * layer_height / 2.0,
                -layer_offset_z,
                -layer_yaw,
            ),
        ]

        if central_shaft_enabled:
            central_radius, central_height = central_shaft_size
            components.append(
                Cylinder(
                    height=central_height,
                    top_radius=central_radius,
                    position=central_shaft_offset,
                ).with_name("central_pivot_shaft")
            )
        return components


class DoubleLayeredCuboidalScissorsShaft(ConceptTemplate):
    def __init__(
        self,
        rear_layer_size,
        front_extension_size,
        front_extension_offset_z,
        layer_offset_z,
        layer_yaw_degrees,
        left_layer_above=True,
        central_shaft_enabled=False,
        central_shaft_size=(0, 0),
        central_shaft_offset=(0, 0, 0),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                rear_layer_size=rear_layer_size,
                front_extension_size=front_extension_size,
                front_extension_offset_z=front_extension_offset_z,
                layer_offset_z=layer_offset_z,
                layer_yaw_degrees=layer_yaw_degrees,
                left_layer_above=left_layer_above,
                central_shaft_enabled=central_shaft_enabled,
                central_shaft_size=central_shaft_size,
                central_shaft_offset=central_shaft_offset,
            )
        )
        self.semantic = "Shaft"

    @staticmethod
    def _layer(name, size, center_y, center_z, yaw):
        layer_length, layer_height, layer_width = size
        return Cuboid(
            height=layer_height,
            top_length=layer_length,
            top_width=layer_width,
            position=(0.0, center_y, center_z),
            rotation=(0.0, yaw, 0.0),
        ).with_name(name)

    @staticmethod
    def _front_extension(
        name,
        rear_layer,
        front_extension_size,
        front_extension_offset_z,
        yaw,
    ):
        rear_length = rear_layer.top_length
        rear_height = rear_layer.height
        front_length, front_width = front_extension_size
        extension = Cuboid(
            height=rear_height,
            top_length=front_length,
            top_width=front_width,
            rotation=(0.0, yaw, 0.0),
        ).with_name(name)
        extension.move_anchor_to(
            "left_center",
            rear_layer.world_point((rear_length / 2.0, 0.0, front_extension_offset_z)),
        )
        return extension

    @classmethod
    def _build_components(
        cls,
        rear_layer_size,
        front_extension_size,
        front_extension_offset_z,
        layer_offset_z,
        layer_yaw_degrees,
        left_layer_above,
        central_shaft_enabled,
        central_shaft_size,
        central_shaft_offset,
    ):
        _, layer_height, _ = rear_layer_size
        layer_yaw = layer_yaw_degrees * DEGREES_TO_RADIANS
        left_y_sign = 1.0 if left_layer_above else -1.0
        left_base_y = left_y_sign * layer_height / 2.0
        right_base_y = -left_y_sign * layer_height / 2.0

        left_rear = cls._layer(
            "left_rear_layer",
            rear_layer_size,
            left_base_y,
            layer_offset_z,
            layer_yaw,
        )
        right_rear = cls._layer(
            "right_rear_layer",
            rear_layer_size,
            right_base_y,
            -layer_offset_z,
            -layer_yaw,
        )
        components = [
            left_rear,
            cls._front_extension(
                "left_front_extension",
                left_rear,
                front_extension_size,
                front_extension_offset_z,
                layer_yaw,
            ),
            right_rear,
            cls._front_extension(
                "right_front_extension",
                right_rear,
                front_extension_size,
                -front_extension_offset_z,
                -layer_yaw,
            ),
        ]

        if central_shaft_enabled:
            central_radius, central_height = central_shaft_size
            components.append(
                Cylinder(
                    height=central_height,
                    top_radius=central_radius,
                    position=central_shaft_offset,
                ).with_name("central_pivot_shaft")
            )
        return components


class SplitCylindricalScissorsShaft(ConceptTemplate):
    def __init__(self, shaft_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(shaft_size=shaft_size))
        self.semantic = "Shaft"

    @staticmethod
    def _build_components(shaft_size):
        shaft_radius, total_height = shaft_size
        layer_height = total_height / 2.0
        return [
            Cylinder(
                height=layer_height,
                top_radius=shaft_radius,
                position=(0.0, total_height / 4.0, 0.0),
            ).with_name("upper_cylindrical_half"),
            Cylinder(
                height=layer_height,
                top_radius=shaft_radius,
                position=(0.0, -total_height / 4.0, 0.0),
            ).with_name("lower_cylindrical_half"),
        ]


class CuspScissorsBlade(ConceptTemplate):
    def __init__(
        self,
        root_size,
        root_tip_offset_z,
        tip_length,
        tip_offset_z,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                root_size=root_size,
                root_tip_offset_z=root_tip_offset_z,
                tip_length=tip_length,
                tip_offset_z=tip_offset_z,
            )
        )
        self.semantic = "Blade"

    @staticmethod
    def _build_components(root_size, root_tip_offset_z, tip_length, tip_offset_z):
        root_length, blade_thickness, root_bottom_width, root_top_width = root_size
        blade_rotation = (pi / 2.0, -pi / 2.0, 0.0)
        return [
            Cuboid(
                height=root_length,
                top_length=root_top_width,
                top_width=blade_thickness,
                bottom_length=root_bottom_width,
                bottom_width=blade_thickness,
                top_offset=(root_tip_offset_z, 0.0),
                position=(-root_length / 2.0, 0.0, 0.0),
                rotation=blade_rotation,
            ).with_name("blade_root"),
            Cuboid(
                height=tip_length,
                top_length=0.0,
                top_width=blade_thickness,
                bottom_length=root_top_width,
                bottom_width=blade_thickness,
                top_offset=(tip_offset_z, 0.0),
                position=(-root_length - tip_length / 2.0, 0.0, root_tip_offset_z),
                rotation=blade_rotation,
            ).with_name("cusp_tip"),
        ]


class CurvedScissorsBlade(ConceptTemplate):
    def __init__(
        self,
        root_size,
        root_tip_offset_z,
        curved_tip_radius,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                root_size=root_size,
                root_tip_offset_z=root_tip_offset_z,
                curved_tip_radius=curved_tip_radius,
            )
        )
        self.semantic = "Blade"

    @staticmethod
    def _build_components(root_size, root_tip_offset_z, curved_tip_radius):
        root_length, blade_thickness, root_bottom_width, root_top_width = root_size
        return [
            Cuboid(
                height=root_length,
                top_length=root_top_width,
                top_width=blade_thickness,
                bottom_length=root_bottom_width,
                bottom_width=blade_thickness,
                top_offset=(root_tip_offset_z, 0.0),
                position=(-root_length / 2.0, 0.0, 0.0),
                rotation=(pi / 2.0, -pi / 2.0, 0.0),
            ).with_name("blade_root"),
            Cylinder(
                height=blade_thickness,
                top_radius=curved_tip_radius,
                bottom_radius=curved_tip_radius,
                top_radius_z=root_top_width,
                bottom_radius_z=root_top_width,
                is_quarter=True,
                position=(-root_length, 0.0, -root_top_width / 2.0 + root_tip_offset_z),
                rotation=(0.0, 0.0, pi),
            ).with_name("quarter_curve_tip"),
        ]


class _RootedScissorsHandleFrame:
    """Scissors-only local frame for root connector to grip contour assembly."""
    @staticmethod
    def root_component(root_size, root_yaw):
        root_length, root_thickness, root_bottom_width, root_top_width = root_size
        root_x, root_y, root_z = rotate_y((root_length / 2.0, 0.0, 0.0), -root_yaw)
        return Cuboid(
            height=root_length,
            top_length=root_top_width,
            top_width=root_thickness,
            bottom_length=root_bottom_width,
            bottom_width=root_thickness,
            position=(root_x, root_y, root_z),
            rotation=(pi / 2.0, pi / 2.0 - root_yaw, 0.0),
        ).with_name("root_connector")

    @staticmethod
    def handle_origin(root_size, root_yaw, handle_offset_z):
        root_length, _, _, _ = root_size
        return np.array(
            (
                root_length * cos(root_yaw) - handle_offset_z * tan(root_yaw),
                0.0,
                root_length * sin(root_yaw) + handle_offset_z,
            )
        )

    @staticmethod
    def position_from_handle_origin(origin, local_x, local_z, arm_yaw):
        offset_x, offset_y, offset_z = rotate_y((local_x, 0.0, local_z), -arm_yaw)
        return origin + np.array((offset_x, offset_y, offset_z))


class RingScissorsHandle(ConceptTemplate):
    def __init__(
        self,
        root_size,
        root_yaw_degrees,
        outer_radius_x,
        outer_radius_z,
        inner_radius_x,
        inner_radius_z,
        ring_thickness,
        handle_offset_z,
        handle_yaw_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                root_size=root_size,
                root_yaw_degrees=root_yaw_degrees,
                outer_radius_x=outer_radius_x,
                outer_radius_z=outer_radius_z,
                inner_radius_x=inner_radius_x,
                inner_radius_z=inner_radius_z,
                ring_thickness=ring_thickness,
                handle_offset_z=handle_offset_z,
                handle_yaw_degrees=handle_yaw_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        root_size,
        root_yaw_degrees,
        outer_radius_x,
        outer_radius_z,
        inner_radius_x,
        inner_radius_z,
        ring_thickness,
        handle_offset_z,
        handle_yaw_degrees,
    ):
        root_yaw = root_yaw_degrees * DEGREES_TO_RADIANS
        handle_yaw = handle_yaw_degrees * DEGREES_TO_RADIANS
        origin = _RootedScissorsHandleFrame.handle_origin(root_size, root_yaw, handle_offset_z)
        ring_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            outer_radius_x,
            0.0,
            handle_yaw,
        )
        return [
            _RootedScissorsHandleFrame.root_component(root_size, root_yaw),
            Ring(
                height=ring_thickness,
                outer_top_radius=outer_radius_z,
                inner_top_radius=inner_radius_z,
                x_z_ratio=outer_radius_x / outer_radius_z,
                inner_x_z_ratio=inner_radius_x / inner_radius_z,
                position=ring_position,
                rotation=(0.0, -handle_yaw, 0.0),
            ).with_name("closed_finger_ring"),
        ]


class HalfRingScissorsHandle(ConceptTemplate):
    def __init__(
        self,
        root_size,
        root_yaw_degrees,
        outer_radius_x,
        outer_radius_z,
        inner_radius_x,
        inner_radius_z,
        ring_thickness,
        bridge_thickness_z,
        handle_offset_z,
        handle_yaw_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                root_size=root_size,
                root_yaw_degrees=root_yaw_degrees,
                outer_radius_x=outer_radius_x,
                outer_radius_z=outer_radius_z,
                inner_radius_x=inner_radius_x,
                inner_radius_z=inner_radius_z,
                ring_thickness=ring_thickness,
                bridge_thickness_z=bridge_thickness_z,
                handle_offset_z=handle_offset_z,
                handle_yaw_degrees=handle_yaw_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        root_size,
        root_yaw_degrees,
        outer_radius_x,
        outer_radius_z,
        inner_radius_x,
        inner_radius_z,
        ring_thickness,
        bridge_thickness_z,
        handle_offset_z,
        handle_yaw_degrees,
    ):
        root_yaw = root_yaw_degrees * DEGREES_TO_RADIANS
        handle_yaw = handle_yaw_degrees * DEGREES_TO_RADIANS
        origin = _RootedScissorsHandleFrame.handle_origin(root_size, root_yaw, handle_offset_z)
        ring_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            outer_radius_x,
            0.0,
            handle_yaw,
        )
        bridge_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            outer_radius_x,
            -bridge_thickness_z / 2.0,
            handle_yaw,
        )
        return [
            _RootedScissorsHandleFrame.root_component(root_size, root_yaw),
            Ring(
                height=ring_thickness,
                outer_top_radius=outer_radius_z,
                inner_top_radius=inner_radius_z,
                exist_angle=pi,
                x_z_ratio=outer_radius_x / outer_radius_z,
                inner_x_z_ratio=inner_radius_x / inner_radius_z,
                position=ring_position,
                rotation=(0.0, -handle_yaw, 0.0),
            ).with_name("half_finger_ring"),
            Cuboid(
                height=ring_thickness,
                top_length=outer_radius_x * 2.0,
                top_width=bridge_thickness_z,
                position=bridge_position,
                rotation=(0.0, -handle_yaw, 0.0),
            ).with_name("flat_ring_bridge"),
        ]


class DoubleCurvedScissorsHandle(ConceptTemplate):
    def __init__(
        self,
        root_size,
        root_yaw_degrees,
        upper_arc_radius,
        lower_arc_radius,
        ring_thickness,
        band_thickness,
        upper_arc_angle_degrees,
        lower_arc_angle_degrees,
        arc_center_separation_x,
        handle_offset_z,
        handle_yaw_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                root_size=root_size,
                root_yaw_degrees=root_yaw_degrees,
                upper_arc_radius=upper_arc_radius,
                lower_arc_radius=lower_arc_radius,
                ring_thickness=ring_thickness,
                band_thickness=band_thickness,
                upper_arc_angle_degrees=upper_arc_angle_degrees,
                lower_arc_angle_degrees=lower_arc_angle_degrees,
                arc_center_separation_x=arc_center_separation_x,
                handle_offset_z=handle_offset_z,
                handle_yaw_degrees=handle_yaw_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        root_size,
        root_yaw_degrees,
        upper_arc_radius,
        lower_arc_radius,
        ring_thickness,
        band_thickness,
        upper_arc_angle_degrees,
        lower_arc_angle_degrees,
        arc_center_separation_x,
        handle_offset_z,
        handle_yaw_degrees,
    ):
        root_yaw = root_yaw_degrees * DEGREES_TO_RADIANS
        handle_yaw = handle_yaw_degrees * DEGREES_TO_RADIANS
        upper_angle = upper_arc_angle_degrees * DEGREES_TO_RADIANS
        lower_angle = lower_arc_angle_degrees * DEGREES_TO_RADIANS
        origin = _RootedScissorsHandleFrame.handle_origin(root_size, root_yaw, handle_offset_z)
        side_delta_z = upper_arc_radius * sin(upper_angle / 2.0) - lower_arc_radius * sin(
            lower_angle / 2.0
        )
        side_length = sqrt(side_delta_z * side_delta_z + arc_center_separation_x ** 2)
        side_yaw = atan(side_delta_z / arc_center_separation_x)
        side_center_x = (
            lower_arc_radius * (1.0 - cos(lower_angle / 2.0))
            + arc_center_separation_x / 2.0
            + band_thickness / 2.0 * sin(side_yaw)
        )
        side_center_z = (
            upper_arc_radius * sin(upper_angle / 2.0)
            + lower_arc_radius * sin(lower_angle / 2.0)
        ) / 2.0
        side_z_clearance = band_thickness / 2.0 * cos(side_yaw)

        bottom_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            lower_arc_radius,
            0.0,
            handle_yaw,
        )
        top_center_x = (
            -upper_arc_radius * cos(upper_angle / 2.0)
            + lower_arc_radius * (1.0 - cos(lower_angle / 2.0))
            + arc_center_separation_x
        )
        top_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            top_center_x,
            0.0,
            handle_yaw,
        )
        left_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            side_center_x,
            -side_center_z + side_z_clearance,
            handle_yaw,
        )
        right_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            side_center_x,
            side_center_z - side_z_clearance,
            handle_yaw,
        )

        return [
            _RootedScissorsHandleFrame.root_component(root_size, root_yaw),
            Ring(
                height=ring_thickness,
                outer_top_radius=lower_arc_radius,
                inner_top_radius=lower_arc_radius - band_thickness,
                exist_angle=lower_angle,
                position=bottom_position,
                rotation=(0.0, -handle_yaw - pi + lower_angle / 2.0, 0.0),
            ).with_name("lower_arc"),
            Ring(
                height=ring_thickness,
                outer_top_radius=upper_arc_radius,
                inner_top_radius=upper_arc_radius - band_thickness,
                exist_angle=upper_angle,
                position=top_position,
                rotation=(0.0, -handle_yaw + upper_angle / 2.0, 0.0),
            ).with_name("upper_arc"),
            Cuboid(
                height=ring_thickness,
                top_length=side_length,
                top_width=band_thickness,
                position=left_position,
                rotation=(0.0, -handle_yaw + side_yaw, 0.0),
            ).with_name("left_side_bridge"),
            Cuboid(
                height=ring_thickness,
                top_length=side_length,
                top_width=band_thickness,
                position=right_position,
                rotation=(0.0, -handle_yaw - side_yaw, 0.0),
            ).with_name("right_side_bridge"),
        ]


class TripleCurvedScissorsHandle(ConceptTemplate):
    def __init__(
        self,
        root_size,
        root_yaw_degrees,
        arc_radius,
        ring_thickness,
        band_thickness,
        main_arc_angle_degrees,
        arc_center_separation_x,
        handle_offset_z,
        handle_yaw_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                root_size=root_size,
                root_yaw_degrees=root_yaw_degrees,
                arc_radius=arc_radius,
                ring_thickness=ring_thickness,
                band_thickness=band_thickness,
                main_arc_angle_degrees=main_arc_angle_degrees,
                arc_center_separation_x=arc_center_separation_x,
                handle_offset_z=handle_offset_z,
                handle_yaw_degrees=handle_yaw_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        root_size,
        root_yaw_degrees,
        arc_radius,
        ring_thickness,
        band_thickness,
        main_arc_angle_degrees,
        arc_center_separation_x,
        handle_offset_z,
        handle_yaw_degrees,
    ):
        root_yaw = root_yaw_degrees * DEGREES_TO_RADIANS
        handle_yaw = handle_yaw_degrees * DEGREES_TO_RADIANS
        main_angle = main_arc_angle_degrees * DEGREES_TO_RADIANS
        origin = _RootedScissorsHandleFrame.handle_origin(root_size, root_yaw, handle_offset_z)
        opposite_angle = pi - main_angle
        opposite_radius = arc_center_separation_x / 2.0 / sin(opposite_angle / 2.0)
        straight_center_x = arc_radius * (1.0 - cos(main_angle / 2.0)) + (
            arc_center_separation_x / 2.0
        )
        straight_center_z = -arc_radius * sin(main_angle / 2.0) + band_thickness / 2.0

        bottom_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            arc_radius,
            0.0,
            handle_yaw,
        )
        top_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            -arc_radius * cos(main_angle / 2.0)
            + arc_radius * (1.0 - cos(main_angle / 2.0))
            + arc_center_separation_x,
            0.0,
            handle_yaw,
        )
        straight_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            straight_center_x,
            straight_center_z,
            handle_yaw,
        )
        opposite_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            straight_center_x,
            -opposite_radius * cos(opposite_angle / 2.0)
            + arc_radius * sin(main_angle / 2.0),
            handle_yaw,
        )

        return [
            _RootedScissorsHandleFrame.root_component(root_size, root_yaw),
            Ring(
                height=ring_thickness,
                outer_top_radius=arc_radius,
                inner_top_radius=arc_radius - band_thickness,
                exist_angle=main_angle,
                position=bottom_position,
                rotation=(0.0, -handle_yaw - pi + main_angle / 2.0, 0.0),
            ).with_name("lower_main_arc"),
            Ring(
                height=ring_thickness,
                outer_top_radius=arc_radius,
                inner_top_radius=arc_radius - band_thickness,
                exist_angle=main_angle,
                position=top_position,
                rotation=(0.0, -handle_yaw + main_angle / 2.0, 0.0),
            ).with_name("upper_main_arc"),
            Cuboid(
                height=ring_thickness,
                top_length=arc_center_separation_x,
                top_width=band_thickness,
                position=straight_position,
                rotation=(0.0, -handle_yaw, 0.0),
            ).with_name("straight_side_bridge"),
            Ring(
                height=ring_thickness,
                outer_top_radius=opposite_radius,
                inner_top_radius=opposite_radius - band_thickness,
                exist_angle=opposite_angle,
                position=opposite_position,
                rotation=(0.0, -handle_yaw - pi / 2.0 + opposite_angle / 2.0, 0.0),
            ).with_name("opposite_side_arc"),
        ]


class CuboidalRingScissorsHandle(ConceptTemplate):
    def __init__(
        self,
        root_size,
        root_yaw_degrees,
        top_bar_length,
        bottom_bar_length,
        ring_thickness,
        side_bar_thickness,
        top_bar_offset_z,
        top_bar_yaw_degrees,
        bottom_bar_yaw_degrees,
        bar_center_separation_x,
        handle_offset_z,
        handle_yaw_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                root_size=root_size,
                root_yaw_degrees=root_yaw_degrees,
                top_bar_length=top_bar_length,
                bottom_bar_length=bottom_bar_length,
                ring_thickness=ring_thickness,
                side_bar_thickness=side_bar_thickness,
                top_bar_offset_z=top_bar_offset_z,
                top_bar_yaw_degrees=top_bar_yaw_degrees,
                bottom_bar_yaw_degrees=bottom_bar_yaw_degrees,
                bar_center_separation_x=bar_center_separation_x,
                handle_offset_z=handle_offset_z,
                handle_yaw_degrees=handle_yaw_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        root_size,
        root_yaw_degrees,
        top_bar_length,
        bottom_bar_length,
        ring_thickness,
        side_bar_thickness,
        top_bar_offset_z,
        top_bar_yaw_degrees,
        bottom_bar_yaw_degrees,
        bar_center_separation_x,
        handle_offset_z,
        handle_yaw_degrees,
    ):
        root_yaw = root_yaw_degrees * DEGREES_TO_RADIANS
        handle_yaw = handle_yaw_degrees * DEGREES_TO_RADIANS
        top_bar_yaw = top_bar_yaw_degrees * DEGREES_TO_RADIANS
        bottom_bar_yaw = bottom_bar_yaw_degrees * DEGREES_TO_RADIANS
        origin = _RootedScissorsHandleFrame.handle_origin(root_size, root_yaw, handle_offset_z)

        bottom_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            0.0,
            0.0,
            handle_yaw,
        )
        top_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            bar_center_separation_x,
            top_bar_offset_z,
            handle_yaw,
        )
        bottom_bar = Cuboid(
            height=ring_thickness,
            top_length=side_bar_thickness,
            top_width=bottom_bar_length,
            position=bottom_position,
            rotation=(0.0, -handle_yaw + bottom_bar_yaw, 0.0),
        ).with_name("bottom_bar")
        top_bar = Cuboid(
            height=ring_thickness,
            top_length=side_bar_thickness,
            top_width=top_bar_length,
            position=top_position,
            rotation=(0.0, -handle_yaw + top_bar_yaw, 0.0),
        ).with_name("top_bar")

        left_start = bottom_bar.world_anchor("back_center")
        left_end = top_bar.world_anchor("back_center")
        right_start = bottom_bar.world_anchor("front_center")
        right_end = top_bar.world_anchor("front_center")
        left_bar = Cuboid(
            height=ring_thickness,
            top_length=float(np.linalg.norm(left_end - left_start)),
            top_width=side_bar_thickness,
        ).with_name("left_bar")
        left_bar.align_axis_between_points("x", left_start, left_end)

        right_bar = Cuboid(
            height=ring_thickness,
            top_length=float(np.linalg.norm(right_end - right_start)),
            top_width=side_bar_thickness,
        ).with_name("right_bar")
        right_bar.align_axis_between_points("x", right_start, right_end)

        return [
            _RootedScissorsHandleFrame.root_component(root_size, root_yaw),
            bottom_bar,
            top_bar,
            left_bar,
            right_bar,
        ]


class CuboidalScissorsHandle(ConceptTemplate):
    def __init__(
        self,
        root_size,
        root_yaw_degrees,
        arm_size,
        handle_offset_z,
        handle_yaw_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                root_size=root_size,
                root_yaw_degrees=root_yaw_degrees,
                arm_size=arm_size,
                handle_offset_z=handle_offset_z,
                handle_yaw_degrees=handle_yaw_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        root_size,
        root_yaw_degrees,
        arm_size,
        handle_offset_z,
        handle_yaw_degrees,
    ):
        root_yaw = root_yaw_degrees * DEGREES_TO_RADIANS
        handle_yaw = handle_yaw_degrees * DEGREES_TO_RADIANS
        arm_length, arm_height, arm_width = arm_size
        origin = _RootedScissorsHandleFrame.handle_origin(root_size, root_yaw, handle_offset_z)
        arm_position = _RootedScissorsHandleFrame.position_from_handle_origin(
            origin,
            arm_length / 2.0,
            0.0,
            handle_yaw,
        )
        return [
            _RootedScissorsHandleFrame.root_component(root_size, root_yaw),
            Cuboid(
                height=arm_height,
                top_length=arm_length,
                top_width=arm_width,
                position=arm_position,
                rotation=(0.0, -handle_yaw, 0.0),
            ).with_name("straight_cuboidal_grip"),
        ]
