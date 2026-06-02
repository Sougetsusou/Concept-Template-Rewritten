from math import atan, cos, pi, sin, sqrt

from code.geometry import (
    ConceptTemplate,
    Cuboid,
    Cylinder,
    Rectangular_Ring,
    Ring,
)


DEGREES_TO_RADIANS = pi / 180.0
HANDLE_ROTATION_ORDER = "ZXY"


class CuboidalOvenBody(ConceptTemplate):
    def __init__(self, body_size, wall_thickness, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(body_size, wall_thickness))
        self.semantic = "Body"

    @staticmethod
    def _build_components(body_size, wall_thickness):
        body_length, body_height, body_depth = body_size
        top_thickness, bottom_thickness, left_thickness, right_thickness, rear_depth = (
            wall_thickness
        )
        shell_depth = body_depth - rear_depth
        opening_length = body_length - left_thickness - right_thickness
        opening_height = body_height - top_thickness - bottom_thickness
        opening_offset_x = (right_thickness - left_thickness) / 2.0
        opening_offset_y = (top_thickness - bottom_thickness) / 2.0

        rear_panel = Cuboid(
            height=body_height,
            top_length=body_length,
            top_width=rear_depth,
        ).with_name("rear_solid_panel")
        rear_panel.move_anchor_to("back_center", (0.0, 0.0, -body_depth / 2.0))

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
            rear_panel.world_anchor("front_center"),
        )

        return [rear_panel, front_shell]


class DoubleLayerOvenBody(ConceptTemplate):
    def __init__(
        self,
        body_size,
        wall_thickness,
        partition_size,
        partition_offset_y,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                body_size=body_size,
                wall_thickness=wall_thickness,
                partition_size=partition_size,
                partition_offset_y=partition_offset_y,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(
        body_size,
        wall_thickness,
        partition_size,
        partition_offset_y,
    ):
        body_length, body_height, body_depth = body_size
        top_thickness, bottom_thickness, left_thickness, right_thickness, rear_depth = (
            wall_thickness
        )
        partition_height, partition_depth = partition_size
        opening_length = body_length - left_thickness - right_thickness
        opening_offset_x = (right_thickness - left_thickness) / 2.0
        opening_offset_y = (top_thickness - bottom_thickness) / 2.0
        partition_center_y = -opening_offset_y + partition_offset_y

        components = CuboidalOvenBody._build_components(body_size, wall_thickness)
        rear_panel = components[0]
        rear_front_x, rear_front_y, rear_front_z = rear_panel.world_anchor("front_center")

        partition = Cuboid(
            height=partition_height,
            top_length=opening_length,
            top_width=partition_depth,
        ).with_name("middle_partition")
        partition.move_anchor_to(
            "back_center",
            (
                rear_front_x + opening_offset_x,
                rear_front_y + partition_center_y,
                rear_front_z,
            ),
        )

        return [*components, partition]


class CuboidalOvenDoor(ConceptTemplate):
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


class SunkenOvenDoor(ConceptTemplate):
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


class CuboidalOvenHandle(ConceptTemplate):
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


class TrifoldOvenHandle(ConceptTemplate):
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


class TrifoldCurveOvenHandle(ConceptTemplate):
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
        chord_half_length = mount_spacing / 2.0
        curve_origin_depth = mount_front_z - sqrt(
            curve_inner_radius * curve_inner_radius - chord_half_length * chord_half_length
        )

        curve = Ring(
            height=curve_thickness,
            outer_top_radius=curve_radius,
            inner_top_radius=curve_inner_radius,
            exist_angle=curve_angle,
            rotation=(0.0, -pi / 2.0 + half_angle, pi / 2.0),
        ).with_name("arc_grip")
        curve.move_anchor_to("arc_origin", (0.0, 0.0, curve_origin_depth))

        return [upper_mount, lower_mount, curve]


class CurveOvenHandle(ConceptTemplate):
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


class FlatOvenTray(ConceptTemplate):
    def __init__(self, tray_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(tray_size))
        self.semantic = "Tray"

    @staticmethod
    def _build_components(tray_size):
        tray_length, tray_height, tray_depth = tray_size
        tray = Cuboid(
            height=tray_height,
            top_length=tray_length,
            top_width=tray_depth,
        ).with_name("flat_tray")
        return [tray]


class DrawerLikeOvenTray(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        inner_opening_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                inner_opening_size=inner_opening_size,
            )
        )
        self.semantic = "Tray"

    @staticmethod
    def _build_components(outer_size, inner_opening_size):
        outer_length, outer_height, outer_depth = outer_size
        inner_length, inner_height, inner_depth = inner_opening_size
        base_height = outer_height - inner_height

        base_panel = Cuboid(
            height=base_height,
            top_length=outer_length,
            top_width=outer_depth,
        ).with_name("tray_base_panel")
        base_panel.move_anchor_to("bottom_center", (0.0, -outer_height / 2.0, 0.0))

        tray_wall = Rectangular_Ring(
            front_height=inner_height,
            outer_top_length=outer_length,
            outer_top_width=outer_depth,
            inner_top_length=inner_length,
            inner_top_width=inner_depth,
        ).with_name("tray_upper_wall")
        tray_wall.move_anchor_to(
            "outer_bottom_center",
            base_panel.world_anchor("top_center"),
        )

        return [base_panel, tray_wall]


class CuboidalOvenBaffle(ConceptTemplate):
    def __init__(self, baffle_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(baffle_size))
        self.semantic = "Baffle"

    @staticmethod
    def _build_components(baffle_size):
        baffle_length, baffle_height, baffle_depth = baffle_size
        baffle = Cuboid(
            height=baffle_height,
            top_length=baffle_length,
            top_width=baffle_depth,
        ).with_name("cuboidal_baffle")
        baffle.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        return [baffle]


class OvenControllerWithButtons(ConceptTemplate):
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
    def _front_surface_point(panel_top_depth, panel_bottom_depth, panel_slope, offset):
        offset_x, offset_along_slope = offset
        front_mid_depth = (panel_top_depth + panel_bottom_depth) / 2.0
        return (
            offset_x,
            offset_along_slope * cos(panel_slope),
            front_mid_depth - offset_along_slope * sin(panel_slope),
        )

    @staticmethod
    def _build_components(panel_size, button_specs):
        panel_length, panel_height, panel_top_depth, panel_bottom_depth = panel_size
        panel_slope = atan((panel_bottom_depth - panel_top_depth) / panel_height)

        panel = Cuboid(
            height=panel_height,
            top_length=panel_length,
            top_width=panel_top_depth,
            bottom_width=panel_bottom_depth,
            top_offset=(0.0, -(panel_bottom_depth - panel_top_depth) / 2.0),
        ).with_name("sloped_controller_panel")
        panel.move_anchor_to("bbox_back_center", (0.0, 0.0, 0.0))

        components = [panel]
        for button_index, button_spec in enumerate(button_specs):
            button_length, button_height, button_depth = button_spec["size"]
            button_mount = OvenControllerWithButtons._front_surface_point(
                panel_top_depth=panel_top_depth,
                panel_bottom_depth=panel_bottom_depth,
                panel_slope=panel_slope,
                offset=button_spec["offset"],
            )
            button = Cuboid(
                height=button_height,
                top_length=button_length,
                top_width=button_depth,
                rotation=(-panel_slope, 0.0, 0.0),
            ).with_name(f"button_{button_index + 1}")
            button.move_anchor_to("back_center", button_mount)
            components.append(button)

        return components


class FlatOvenTop(ConceptTemplate):
    def __init__(self, top_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(top_size))
        self.semantic = "Body"

    @staticmethod
    def _build_components(top_size):
        top_length, top_height, top_depth = top_size
        top = Cuboid(
            height=top_height,
            top_length=top_length,
            top_width=top_depth,
        ).with_name("flat_top")
        top.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        return [top]


class OvenTopWithBurners(ConceptTemplate):
    def __init__(
        self,
        top_size,
        burner_specs,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(top_size=top_size, burner_specs=burner_specs)
        )
        self.semantic = "Burner"

    @staticmethod
    def _build_components(top_size, burner_specs):
        top_length, top_height, top_depth = top_size
        top = Cuboid(
            height=top_height,
            top_length=top_length,
            top_width=top_depth,
        ).with_name("stove_top_panel")
        top.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        top_x, top_y, top_z = top.world_anchor("top_center")

        components = [top]
        for burner_index, burner_spec in enumerate(burner_specs):
            burner_length, burner_height, burner_depth = burner_spec["size"]
            burner_offset_x, burner_offset_z = burner_spec["offset"]
            burner_thickness = burner_spec["thickness"]
            central_radius, central_height = burner_spec["central_size"]
            central_offset_x, central_offset_z = burner_spec["central_offset"]

            burner = Rectangular_Ring(
                front_height=burner_height,
                outer_top_length=burner_length,
                outer_top_width=burner_depth,
                inner_top_length=burner_length - burner_thickness * 2.0,
                inner_top_width=burner_depth - burner_thickness * 2.0,
            ).with_name(f"burner_{burner_index + 1}_outer_ring")
            burner.move_anchor_to(
                "outer_bottom_center",
                (
                    top_x + burner_offset_x,
                    top_y,
                    top_z + burner_offset_z,
                ),
            )
            components.append(burner)

            central_cap = Cylinder(
                height=central_height,
                top_radius=central_radius,
            ).with_name(f"burner_{burner_index + 1}_central_cap")
            central_cap.move_anchor_to(
                "bottom_center",
                (
                    top_x + burner_offset_x + central_offset_x,
                    top_y,
                    top_z + burner_offset_z + central_offset_z,
                ),
            )
            components.append(central_cap)

        return components


class MultilevelOvenLegSet(ConceptTemplate):
    def __init__(
        self,
        front_leg_size,
        rear_leg_size,
        front_leg_spacing,
        rear_leg_spacing,
        front_rear_spacing,
        leg_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                front_leg_size=front_leg_size,
                rear_leg_size=rear_leg_size,
                front_leg_spacing=front_leg_spacing,
                rear_leg_spacing=rear_leg_spacing,
                front_rear_spacing=front_rear_spacing,
                leg_count=leg_count,
            )
        )
        self.semantic = "Leg"

    @staticmethod
    def _leg(name, size, top_mount):
        leg_length, leg_height, leg_depth = size
        leg = Cuboid(
            height=leg_height,
            top_length=leg_length,
            top_width=leg_depth,
        ).with_name(name)
        leg.move_anchor_to("top_center", top_mount)
        return leg

    @staticmethod
    def _build_components(
        front_leg_size,
        rear_leg_size,
        front_leg_spacing,
        rear_leg_spacing,
        front_rear_spacing,
        leg_count,
    ):
        count = int(leg_count)
        if count == 1:
            return [
                MultilevelOvenLegSet._leg(
                    "front_center_leg",
                    front_leg_size,
                    (0.0, 0.0, 0.0),
                )
            ]

        if count == 2:
            return [
                MultilevelOvenLegSet._leg(
                    "front_right_leg",
                    front_leg_size,
                    (front_leg_spacing / 2.0, 0.0, 0.0),
                ),
                MultilevelOvenLegSet._leg(
                    "front_left_leg",
                    front_leg_size,
                    (-front_leg_spacing / 2.0, 0.0, 0.0),
                ),
            ]

        components = [
            MultilevelOvenLegSet._leg(
                "front_right_leg",
                front_leg_size,
                (front_leg_spacing / 2.0, 0.0, front_rear_spacing / 2.0),
            ),
            MultilevelOvenLegSet._leg(
                "front_left_leg",
                front_leg_size,
                (-front_leg_spacing / 2.0, 0.0, front_rear_spacing / 2.0),
            ),
        ]

        if count == 3:
            components.append(
                MultilevelOvenLegSet._leg(
                    "rear_center_leg",
                    rear_leg_size,
                    (0.0, 0.0, -front_rear_spacing / 2.0),
                )
            )
            return components

        if count == 4:
            components.extend(
                [
                    MultilevelOvenLegSet._leg(
                        "rear_right_leg",
                        rear_leg_size,
                        (rear_leg_spacing / 2.0, 0.0, -front_rear_spacing / 2.0),
                    ),
                    MultilevelOvenLegSet._leg(
                        "rear_left_leg",
                        rear_leg_size,
                        (-rear_leg_spacing / 2.0, 0.0, -front_rear_spacing / 2.0),
                    ),
                ]
            )
            return components

        raise ValueError("leg_count must be 1, 2, 3, or 4")
