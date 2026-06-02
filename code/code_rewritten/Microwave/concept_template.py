from math import cos, pi, sqrt

from code.geometry_rewritten import (
    ConceptTemplate,
    Cuboid,
    Cylinder,
    Rectangular_Ring,
    Ring,
)


DEGREES_TO_RADIANS = pi / 180.0
HANDLE_ROTATION_ORDER = "ZXY"


class CuboidalMicrowaveBody(ConceptTemplate):
    def __init__(self, body_size, wall_thickness, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(body_size, wall_thickness))
        self.semantic = "Body"

    @staticmethod
    def _build_components(body_size, wall_thickness):
        body_length, body_height, body_depth = body_size
        top_thickness, bottom_thickness, left_thickness, right_thickness, back_depth = (
            wall_thickness
        )
        shell_depth = body_depth - back_depth
        opening_length = body_length - left_thickness - right_thickness
        opening_height = body_height - top_thickness - bottom_thickness
        opening_offset_x = (right_thickness - left_thickness) / 2.0
        opening_offset_y = -(bottom_thickness - top_thickness) / 2.0

        back_slab = Cuboid(
            height=body_height,
            top_length=body_length,
            top_width=back_depth,
        ).with_name("rear_solid_slab")
        back_slab.move_anchor_to("back_center", (0.0, 0.0, -body_depth / 2.0))

        front_shell = Rectangular_Ring(
            front_height=shell_depth,
            outer_top_length=body_length,
            outer_top_width=body_height,
            inner_top_length=opening_length,
            inner_top_width=opening_height,
            inner_offset=(opening_offset_x, opening_offset_y),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("front_open_shell")
        front_shell.move_anchor_to(
            "outer_bottom_center",
            back_slab.world_anchor("front_center"),
        )

        return [back_slab, front_shell]


class CuboidalMicrowaveDoor(ConceptTemplate):
    def __init__(self, door_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(door_size))
        self.semantic = "Door"

    @staticmethod
    def _build_components(door_size):
        door_length, door_height, door_depth = door_size
        panel = Cuboid(
            height=door_height,
            top_length=door_length,
            top_width=door_depth,
        ).with_name("door_panel")
        panel.move_anchor_to("back_center", (0.0, 0.0, 0.0))
        return [panel]


class SunkenMicrowaveDoor(ConceptTemplate):
    def __init__(
        self,
        door_size,
        sunken_opening_size,
        sunken_opening_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                door_size=door_size,
                sunken_opening_size=sunken_opening_size,
                sunken_opening_offset=sunken_opening_offset,
            )
        )
        self.semantic = "Door"

    @staticmethod
    def _build_components(door_size, sunken_opening_size, sunken_opening_offset):
        door_length, door_height, door_depth = door_size
        opening_length, opening_height, sunken_depth = sunken_opening_size
        opening_offset_x, opening_offset_y = sunken_opening_offset
        rear_depth = door_depth - sunken_depth

        rear_panel = Cuboid(
            height=door_height,
            top_length=door_length,
            top_width=rear_depth,
        ).with_name("rear_door_panel")
        rear_panel.move_anchor_to("back_center", (0.0, 0.0, 0.0))

        front_frame = Rectangular_Ring(
            front_height=sunken_depth,
            outer_top_length=door_length,
            outer_top_width=door_height,
            inner_top_length=opening_length,
            inner_top_width=opening_height,
            inner_offset=(opening_offset_x, -opening_offset_y),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("sunken_front_frame")
        front_frame.move_anchor_to(
            "outer_bottom_center",
            rear_panel.world_anchor("front_center"),
        )

        return [rear_panel, front_frame]


class CuboidalMicrowaveHandle(ConceptTemplate):
    def __init__(self, handle_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=HANDLE_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(handle_size))
        self.semantic = "Handle"

    @staticmethod
    def _build_components(handle_size):
        handle_length, handle_height, handle_depth = handle_size
        handle = Cuboid(
            height=handle_height,
            top_length=handle_length,
            top_width=handle_depth,
        ).with_name("cuboidal_handle")
        handle.move_anchor_to("back_center", (0.0, 0.0, 0.0))
        return [handle]


class TrifoldMicrowaveHandle(ConceptTemplate):
    def __init__(
        self,
        mount_size,
        mount_spacing,
        grip_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=HANDLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                mount_size=mount_size,
                mount_spacing=mount_spacing,
                grip_size=grip_size,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(mount_size, mount_spacing, grip_size):
        mount_length, mount_height, mount_depth = mount_size
        grip_length, grip_height, grip_depth = grip_size

        upper_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
        ).with_name("upper_mount")
        upper_mount.move_anchor_to("back_center", (0.0, mount_spacing / 2.0, 0.0))

        lower_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
        ).with_name("lower_mount")
        lower_mount.move_anchor_to("back_center", (0.0, -mount_spacing / 2.0, 0.0))

        upper_front_x, upper_front_y, upper_front_z = upper_mount.world_anchor("front_center")
        lower_front_x, lower_front_y, lower_front_z = lower_mount.world_anchor("front_center")
        grip_mount_point = (
            (upper_front_x + lower_front_x) / 2.0,
            (upper_front_y + lower_front_y) / 2.0,
            (upper_front_z + lower_front_z) / 2.0,
        )

        grip = Cuboid(
            height=grip_height,
            top_length=grip_length,
            top_width=grip_depth,
        ).with_name("front_grip_bar")
        grip.move_anchor_to("back_center", grip_mount_point)

        return [upper_mount, lower_mount, grip]


class TrifoldCurveMicrowaveHandle(ConceptTemplate):
    def __init__(
        self,
        mount_size,
        mount_spacing,
        curve_radius,
        curve_inner_radius,
        curve_thickness,
        curve_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=HANDLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                mount_size=mount_size,
                mount_spacing=mount_spacing,
                curve_radius=curve_radius,
                curve_inner_radius=curve_inner_radius,
                curve_thickness=curve_thickness,
                curve_angle=curve_angle_degrees * DEGREES_TO_RADIANS,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        mount_size,
        mount_spacing,
        curve_radius,
        curve_inner_radius,
        curve_thickness,
        curve_angle,
    ):
        mount_length, mount_height, mount_depth = mount_size
        half_angle = curve_angle / 2.0

        upper_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
        ).with_name("upper_mount")
        upper_mount.move_anchor_to("back_center", (0.0, mount_spacing / 2.0, 0.0))

        lower_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
        ).with_name("lower_mount")
        lower_mount.move_anchor_to("back_center", (0.0, -mount_spacing / 2.0, 0.0))

        _, _, mount_front_z = upper_mount.world_anchor("front_center")
        curve = Ring(
            height=curve_thickness,
            outer_top_radius=curve_radius,
            inner_top_radius=curve_inner_radius,
            exist_angle=curve_angle,
            rotation=(0.0, -pi / 2.0 + half_angle, pi / 2.0),
        ).with_name("arc_grip")
        chord_half_length = mount_spacing / 2.0
        curve_origin_depth = mount_front_z - sqrt(
            curve_inner_radius * curve_inner_radius
            - chord_half_length * chord_half_length
        )
        curve.move_anchor_to("arc_origin", (0.0, 0.0, curve_origin_depth))

        return [upper_mount, lower_mount, curve]


class CurveMicrowaveHandle(ConceptTemplate):
    def __init__(
        self,
        curve_radius,
        curve_inner_radius,
        curve_thickness,
        curve_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=HANDLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                curve_radius=curve_radius,
                curve_inner_radius=curve_inner_radius,
                curve_thickness=curve_thickness,
                curve_angle=curve_angle_degrees * DEGREES_TO_RADIANS,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(curve_radius, curve_inner_radius, curve_thickness, curve_angle):
        half_angle = curve_angle / 2.0
        curve = Ring(
            height=curve_thickness,
            outer_top_radius=curve_radius,
            inner_top_radius=curve_inner_radius,
            exist_angle=curve_angle,
            rotation=(0.0, -pi / 2.0 + half_angle, pi / 2.0),
        ).with_name("arc_handle")
        curve.move_anchor_to(
            "arc_origin",
            (0.0, 0.0, -curve_radius * cos(half_angle)),
        )
        return [curve]


class MicrowaveControllerWithButtons(ConceptTemplate):
    def __init__(
        self,
        panel_size,
        button_specs,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(panel_size=panel_size, button_specs=button_specs)
        )
        self.semantic = "Button"

    @staticmethod
    def _build_components(panel_size, button_specs):
        panel_length, panel_height, panel_depth = panel_size
        panel = Cuboid(
            height=panel_height,
            top_length=panel_length,
            top_width=panel_depth,
        ).with_name("controller_panel")
        panel.move_anchor_to("back_center", (0.0, 0.0, 0.0))

        panel_front_x, panel_front_y, panel_front_z = panel.world_anchor("front_center")
        components = [panel]
        for button_index, button_spec in enumerate(button_specs):
            button_length, button_height, button_depth = button_spec["size"]
            button_offset_x, button_offset_y = button_spec["offset"]
            button = Cuboid(
                height=button_height,
                top_length=button_length,
                top_width=button_depth,
            ).with_name(f"button_{button_index + 1}")
            button.move_anchor_to(
                "back_center",
                (
                    panel_front_x + button_offset_x,
                    panel_front_y + button_offset_y,
                    panel_front_z,
                ),
            )
            components.append(button)

        return components


class CylindricalMicrowaveTray(ConceptTemplate):
    def __init__(self, tray_radius, tray_height, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(tray_radius, tray_height))
        self.semantic = "Tray"

    @staticmethod
    def _build_components(tray_radius, tray_height):
        tray = Cylinder(
            height=tray_height,
            top_radius=tray_radius,
        ).with_name("cylindrical_tray")
        tray.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        return [tray]
