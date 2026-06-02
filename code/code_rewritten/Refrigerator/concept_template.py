from math import cos, pi, sqrt

from code.geometry_rewritten import ConceptTemplate, Cuboid, Rectangular_Ring, Ring


DEGREES_TO_RADIANS = pi / 180.0
HANDLE_ROTATION_ORDER = "ZXY"


class CuboidalRefrigeratorBody(ConceptTemplate):
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


class DoubleLayerRefrigeratorBody(ConceptTemplate):
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

        rear_panel, front_shell = CuboidalRefrigeratorBody._build_components(
            body_size, wall_thickness
        )
        rear_front_x, rear_front_y, rear_front_z = rear_panel.world_anchor("front_center")

        partition = Cuboid(
            height=partition_height,
            top_length=opening_length,
            top_width=partition_depth,
        ).with_name("horizontal_inner_partition")
        partition.move_anchor_to(
            "back_center",
            (
                rear_front_x + opening_offset_x,
                rear_front_y + partition_center_y,
                rear_front_z,
            ),
        )

        return [rear_panel, front_shell, partition]


class LeftRightDoubleLayerRefrigeratorBody(ConceptTemplate):
    def __init__(
        self,
        body_size,
        wall_thickness,
        partition_size,
        partition_offset_x,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                body_size=body_size,
                wall_thickness=wall_thickness,
                partition_size=partition_size,
                partition_offset_x=partition_offset_x,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(
        body_size,
        wall_thickness,
        partition_size,
        partition_offset_x,
    ):
        body_length, body_height, body_depth = body_size
        top_thickness, bottom_thickness, left_thickness, right_thickness, rear_depth = (
            wall_thickness
        )
        partition_length, partition_depth = partition_size
        opening_height = body_height - top_thickness - bottom_thickness
        opening_offset_x = (right_thickness - left_thickness) / 2.0
        opening_offset_y = (top_thickness - bottom_thickness) / 2.0
        partition_center_x = opening_offset_x + partition_offset_x

        rear_panel, front_shell = CuboidalRefrigeratorBody._build_components(
            body_size, wall_thickness
        )
        rear_front_x, rear_front_y, rear_front_z = rear_panel.world_anchor("front_center")

        partition = Cuboid(
            height=opening_height,
            top_length=partition_length,
            top_width=partition_depth,
        ).with_name("vertical_inner_partition")
        partition.move_anchor_to(
            "back_center",
            (
                rear_front_x + partition_center_x,
                rear_front_y - opening_offset_y,
                rear_front_z,
            ),
        )

        return [rear_panel, front_shell, partition]


class CuboidalRefrigeratorDoor(ConceptTemplate):
    def __init__(self, door_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(door_size))
        self.semantic = "Door"

    @staticmethod
    def _build_components(door_size):
        door_length, door_height, door_depth = door_size
        door_panel = Cuboid(
            height=door_height,
            top_length=door_length,
            top_width=door_depth,
        ).with_name("door_panel")
        door_panel.move_anchor_to("back_center", (0.0, 0.0, 0.0))
        return [door_panel]


class SunkenRefrigeratorDoor(ConceptTemplate):
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
        ).with_name("rear_door_layer")
        rear_panel.move_anchor_to("back_center", (0.0, 0.0, 0.0))

        front_frame = Rectangular_Ring(
            front_height=sunken_depth,
            outer_top_length=door_length,
            outer_top_width=door_height,
            inner_top_length=opening_length,
            inner_top_width=opening_height,
            inner_offset=(opening_offset_x, -opening_offset_y),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("front_sunken_frame")
        front_frame.move_anchor_to(
            "outer_bottom_center",
            rear_panel.world_anchor("front_center"),
        )

        return [rear_panel, front_frame]


class CuboidalRefrigeratorHandle(ConceptTemplate):
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


class TrifoldRefrigeratorHandle(ConceptTemplate):
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

        grip = Cuboid(
            height=grip_height,
            top_length=grip_length,
            top_width=grip_depth,
        ).with_name("front_grip")
        grip.move_anchor_to("back_center", (0.0, 0.0, mount_depth))

        return [upper_mount, lower_mount, grip]


class TrifoldCurveRefrigeratorHandle(ConceptTemplate):
    def __init__(
        self,
        mount_size,
        mount_spacing,
        curve_outer_radius,
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
                curve_outer_radius=curve_outer_radius,
                curve_inner_radius=curve_inner_radius,
                curve_thickness=curve_thickness,
                curve_angle_degrees=curve_angle_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        mount_size,
        mount_spacing,
        curve_outer_radius,
        curve_inner_radius,
        curve_thickness,
        curve_angle_degrees,
    ):
        mount_length, mount_height, mount_depth = mount_size
        curve_angle = curve_angle_degrees * DEGREES_TO_RADIANS

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

        chord_sagitta_z = sqrt(
            curve_inner_radius * curve_inner_radius
            - (mount_spacing / 2.0) * (mount_spacing / 2.0)
        )
        arc_origin_z = mount_depth - chord_sagitta_z
        arc_grip = Ring(
            height=curve_thickness,
            outer_top_radius=curve_outer_radius,
            inner_top_radius=curve_inner_radius,
            exist_angle=curve_angle,
            rotation=(0.0, -pi / 2.0 + curve_angle / 2.0, pi / 2.0),
        ).with_name("arc_grip")
        arc_grip.move_anchor_to("arc_origin", (0.0, 0.0, arc_origin_z))

        return [upper_mount, lower_mount, arc_grip]


class CurveRefrigeratorHandle(ConceptTemplate):
    def __init__(
        self,
        curve_outer_radius,
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
                curve_outer_radius=curve_outer_radius,
                curve_inner_radius=curve_inner_radius,
                curve_thickness=curve_thickness,
                curve_angle_degrees=curve_angle_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        curve_outer_radius,
        curve_inner_radius,
        curve_thickness,
        curve_angle_degrees,
    ):
        curve_angle = curve_angle_degrees * DEGREES_TO_RADIANS
        arc_origin_z = -curve_outer_radius * cos(curve_angle / 2.0)
        arc_grip = Ring(
            height=curve_thickness,
            outer_top_radius=curve_outer_radius,
            inner_top_radius=curve_inner_radius,
            exist_angle=curve_angle,
            rotation=(0.0, -pi / 2.0 + curve_angle / 2.0, pi / 2.0),
        ).with_name("arc_handle")
        arc_grip.move_anchor_to("arc_origin", (0.0, 0.0, arc_origin_z))
        return [arc_grip]


class CuboidalRefrigeratorVessel(ConceptTemplate):
    def __init__(self, outer_size, inner_opening_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                inner_opening_size=inner_opening_size,
            )
        )
        self.semantic = "Vessel"

    @staticmethod
    def _build_components(outer_size, inner_opening_size):
        outer_length, outer_height, outer_depth = outer_size
        inner_length, inner_height, inner_depth = inner_opening_size
        base_height = outer_height - inner_height

        base = Cuboid(
            height=base_height,
            top_length=outer_length,
            top_width=outer_depth,
        ).with_name("lower_solid_base")
        base.move_anchor_to("front_center", (0.0, -inner_height / 2.0, 0.0))

        upper_ring = Rectangular_Ring(
            front_height=inner_height,
            outer_top_length=outer_length,
            outer_top_width=outer_depth,
            inner_top_length=inner_length,
            inner_top_width=inner_depth,
            inner_offset=(0.0, (outer_depth - inner_depth) / 2.0),
        ).with_name("upper_open_ring")
        upper_ring.move_anchor_to("outer_bottom_center", base.world_anchor("top_center"))

        return [base, upper_ring]


class FlatRefrigeratorTray(ConceptTemplate):
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


class DrawerLikeRefrigeratorTray(ConceptTemplate):
    def __init__(self, outer_size, inner_opening_size, position=(0, 0, 0), rotation=(0, 0, 0)):
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

        base = Cuboid(
            height=base_height,
            top_length=outer_length,
            top_width=outer_depth,
        ).with_name("lower_solid_base")
        base.move_anchor_to("center", (0.0, -inner_height / 2.0, 0.0))

        upper_ring = Rectangular_Ring(
            front_height=inner_height,
            outer_top_length=outer_length,
            outer_top_width=outer_depth,
            inner_top_length=inner_length,
            inner_top_width=inner_depth,
        ).with_name("upper_open_ring")
        upper_ring.move_anchor_to("outer_bottom_center", base.world_anchor("top_center"))

        return [base, upper_ring]


class MultilevelRefrigeratorLegSet(ConceptTemplate):
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
    def _leg(name, leg_size, top_mount):
        leg_length, leg_height, leg_depth = leg_size
        leg = Cuboid(
            height=leg_height,
            top_length=leg_length,
            top_width=leg_depth,
        ).with_name(name)
        leg.move_anchor_to("top_center", top_mount)
        return leg

    @classmethod
    def _build_components(
        cls,
        front_leg_size,
        rear_leg_size,
        front_leg_spacing,
        rear_leg_spacing,
        front_rear_spacing,
        leg_count,
    ):
        count = int(leg_count)
        if count == 1:
            return [cls._leg("center_leg", front_leg_size, (0.0, 0.0, 0.0))]

        if count == 2:
            return [
                cls._leg(
                    "right_front_leg",
                    front_leg_size,
                    (front_leg_spacing / 2.0, 0.0, 0.0),
                ),
                cls._leg(
                    "left_front_leg",
                    front_leg_size,
                    (-front_leg_spacing / 2.0, 0.0, 0.0),
                ),
            ]

        front_z = front_rear_spacing / 2.0
        rear_z = -front_rear_spacing / 2.0
        components = [
            cls._leg(
                "right_front_leg",
                front_leg_size,
                (front_leg_spacing / 2.0, 0.0, front_z),
            ),
            cls._leg(
                "left_front_leg",
                front_leg_size,
                (-front_leg_spacing / 2.0, 0.0, front_z),
            ),
        ]

        if count == 3:
            components.append(cls._leg("rear_center_leg", rear_leg_size, (0.0, 0.0, rear_z)))
        elif count == 4:
            components.extend(
                [
                    cls._leg(
                        "right_rear_leg",
                        rear_leg_size,
                        (rear_leg_spacing / 2.0, 0.0, rear_z),
                    ),
                    cls._leg(
                        "left_rear_leg",
                        rear_leg_size,
                        (-rear_leg_spacing / 2.0, 0.0, rear_z),
                    ),
                ]
            )

        return components
