from math import cos, pi, sqrt

from code.geometry import ConceptTemplate, Cuboid, Rectangular_Ring, Ring


DEGREES_TO_RADIANS = pi / 180.0
HANDLE_ROTATION_ORDER = "ZXY"


class RectangularDishwasherBody(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        wall_thickness,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                wall_thickness=wall_thickness,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(outer_size, wall_thickness):
        outer_length, outer_height, outer_depth = outer_size
        (
            negative_y_wall_thickness,
            positive_y_wall_thickness,
            negative_x_wall_thickness,
            positive_x_wall_thickness,
            back_panel_depth,
        ) = wall_thickness

        bottom_panel = Cuboid(
            height=outer_height,
            top_length=outer_length,
            top_width=back_panel_depth,
        ).with_name("back_panel")
        bottom_panel.move_anchor_to(
            "back_center",
            (0.0, 0.0, -outer_depth / 2.0),
        )

        inner_length = outer_length - negative_x_wall_thickness - positive_x_wall_thickness
        inner_height = outer_height - negative_y_wall_thickness - positive_y_wall_thickness
        inner_center_x = (positive_x_wall_thickness - negative_x_wall_thickness) / 2.0
        inner_center_y = (positive_y_wall_thickness - negative_y_wall_thickness) / 2.0

        side_shell = Rectangular_Ring(
            front_height=outer_depth - back_panel_depth,
            outer_top_length=outer_length,
            outer_top_width=outer_height,
            inner_top_length=inner_length,
            inner_top_width=inner_height,
            inner_offset=(inner_center_x, -inner_center_y),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("side_shell")
        side_shell.move_anchor_to(
            "outer_bottom_center",
            bottom_panel.world_anchor("front_center"),
        )

        return [bottom_panel, side_shell]


class DoubleLayerDishwasherBody(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        wall_thickness,
        shelf_size,
        shelf_y_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                wall_thickness=wall_thickness,
                shelf_size=shelf_size,
                shelf_y_offset=shelf_y_offset,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(outer_size, wall_thickness, shelf_size, shelf_y_offset):
        outer_length, _, _ = outer_size
        shelf_height, shelf_depth = shelf_size
        (
            negative_y_wall_thickness,
            positive_y_wall_thickness,
            negative_x_wall_thickness,
            positive_x_wall_thickness,
            _,
        ) = wall_thickness

        bottom_panel, side_shell = RectangularDishwasherBody._build_components(
            outer_size=outer_size,
            wall_thickness=wall_thickness,
        )

        inner_length = outer_length - negative_x_wall_thickness - positive_x_wall_thickness
        inner_center_x = (positive_x_wall_thickness - negative_x_wall_thickness) / 2.0
        inner_center_y = (
            (positive_y_wall_thickness - negative_y_wall_thickness) / 2.0
            + shelf_y_offset
        )

        shelf = Cuboid(
            height=shelf_height,
            top_length=inner_length,
            top_width=shelf_depth,
            position=(inner_center_x, inner_center_y, 0.0),
        ).with_name("internal_shelf")
        (
            _back_panel_front_x,
            _back_panel_front_y,
            back_panel_front_z,
        ) = bottom_panel.world_anchor("front_center")
        shelf.move_anchor_to(
            "back_center",
            (inner_center_x, inner_center_y, back_panel_front_z),
        )

        return [bottom_panel, side_shell, shelf]


class FlatDishwasherDoor(ConceptTemplate):
    def __init__(self, panel_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(panel_size=panel_size))
        self.semantic = "Door"

    @staticmethod
    def _build_components(panel_size):
        panel_length, panel_height, panel_depth = panel_size
        panel = Cuboid(
            height=panel_height,
            top_length=panel_length,
            top_width=panel_depth,
        ).with_name("flat_panel")
        panel.move_anchor_to("back_center", (0.0, 0.0, 0.0))
        return [panel]


class SunkenDishwasherDoor(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        recess_size,
        recess_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                recess_size=recess_size,
                recess_offset=recess_offset,
            )
        )
        self.semantic = "Door"

    @staticmethod
    def _build_components(outer_size, recess_size, recess_offset):
        outer_length, outer_height, outer_depth = outer_size
        recess_length, recess_height, recess_depth = recess_size
        recess_offset_x, recess_offset_y = recess_offset

        back_panel = Cuboid(
            height=outer_height,
            top_length=outer_length,
            top_width=outer_depth - recess_depth,
        ).with_name("back_panel")
        back_panel.move_anchor_to("back_center", (0.0, 0.0, 0.0))

        front_frame = Rectangular_Ring(
            front_height=recess_depth,
            outer_top_length=outer_length,
            outer_top_width=outer_height,
            inner_top_length=recess_length,
            inner_top_width=recess_height,
            inner_offset=(recess_offset_x, -recess_offset_y),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("recess_frame")
        front_frame.move_anchor_to(
            "outer_bottom_center",
            back_panel.world_anchor("front_center"),
        )

        return [back_panel, front_frame]


class FlatDishwasherHandle(ConceptTemplate):
    def __init__(self, handle_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=HANDLE_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(handle_size=handle_size))
        self.semantic = "Handle"

    @staticmethod
    def _build_components(handle_size):
        handle_length, handle_height, handle_depth = handle_size
        handle = Cuboid(
            height=handle_height,
            top_length=handle_length,
            top_width=handle_depth,
        ).with_name("flat_handle")
        handle.move_anchor_to("back_center", (0.0, 0.0, 0.0))
        return [handle]


class TrifoldDishwasherHandle(ConceptTemplate):
    def __init__(
        self,
        mount_size,
        mount_separation,
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
                mount_separation=mount_separation,
                grip_size=grip_size,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(mount_size, mount_separation, grip_size):
        mount_length, mount_height, mount_depth = mount_size
        grip_length, grip_height, grip_depth = grip_size
        mount_half_separation = mount_separation / 2.0

        upper_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
            position=(0.0, mount_half_separation, 0.0),
        ).with_name("upper_mount")
        upper_mount.move_anchor_to(
            "back_center",
            (0.0, mount_half_separation, 0.0),
        )

        lower_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
            position=(0.0, -mount_half_separation, 0.0),
        ).with_name("lower_mount")
        lower_mount.move_anchor_to(
            "back_center",
            (0.0, -mount_half_separation, 0.0),
        )

        grip = Cuboid(
            height=grip_height,
            top_length=grip_length,
            top_width=grip_depth,
        ).with_name("grip")
        grip.move_anchor_to("back_center", (0.0, 0.0, mount_depth))

        return [upper_mount, lower_mount, grip]


class TrifoldArcDishwasherHandle(ConceptTemplate):
    def __init__(
        self,
        mount_size,
        mount_separation,
        outer_radius,
        inner_radius,
        arc_height,
        arc_angle_degrees,
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
                mount_separation=mount_separation,
                outer_radius=outer_radius,
                inner_radius=inner_radius,
                arc_height=arc_height,
                arc_angle_degrees=arc_angle_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        mount_size,
        mount_separation,
        outer_radius,
        inner_radius,
        arc_height,
        arc_angle_degrees,
    ):
        mount_length, mount_height, mount_depth = mount_size
        mount_half_separation = mount_separation / 2.0
        arc_angle = arc_angle_degrees * DEGREES_TO_RADIANS

        upper_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
            position=(0.0, mount_half_separation, 0.0),
        ).with_name("upper_mount")
        upper_mount.move_anchor_to(
            "back_center",
            (0.0, mount_half_separation, 0.0),
        )

        lower_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
            position=(0.0, -mount_half_separation, 0.0),
        ).with_name("lower_mount")
        lower_mount.move_anchor_to(
            "back_center",
            (0.0, -mount_half_separation, 0.0),
        )

        arc_z_offset = mount_depth - sqrt(
            inner_radius * inner_radius - mount_half_separation * mount_half_separation
        )
        arc = Ring(
            height=arc_height,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=arc_angle,
            position=(0.0, 0.0, arc_z_offset),
            rotation=(0.0, -pi / 2.0 + arc_angle / 2.0, pi / 2.0),
        ).with_name("arc_grip")

        return [upper_mount, lower_mount, arc]


class ArcDishwasherHandle(ConceptTemplate):
    def __init__(
        self,
        outer_radius,
        inner_radius,
        arc_height,
        arc_angle_degrees,
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
                outer_radius=outer_radius,
                inner_radius=inner_radius,
                arc_height=arc_height,
                arc_angle_degrees=arc_angle_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        outer_radius,
        inner_radius,
        arc_height,
        arc_angle_degrees,
    ):
        arc_angle = arc_angle_degrees * DEGREES_TO_RADIANS
        arc = Ring(
            height=arc_height,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=arc_angle,
            position=(0.0, 0.0, -outer_radius * cos(arc_angle / 2.0)),
            rotation=(0.0, -pi / 2.0 + arc_angle / 2.0, pi / 2.0),
        ).with_name("arc_handle")
        return [arc]


class FlatDishwasherTray(ConceptTemplate):
    def __init__(self, tray_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(tray_size=tray_size))
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


class DrawerDishwasherTray(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        inner_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                inner_size=inner_size,
            )
        )
        self.semantic = "Tray"

    @staticmethod
    def _build_components(outer_size, inner_size):
        outer_length, outer_height, outer_depth = outer_size
        inner_length, inner_height, inner_depth = inner_size

        bottom_height = outer_height - inner_height
        bottom_panel = Cuboid(
            height=bottom_height,
            top_length=outer_length,
            top_width=outer_depth,
        ).with_name("bottom_panel")
        bottom_panel.move_anchor_to(
            "bottom_center",
            (0.0, -outer_height / 2.0, 0.0),
        )

        tray_walls = Rectangular_Ring(
            front_height=inner_height,
            outer_top_length=outer_length,
            outer_top_width=outer_depth,
            inner_top_length=inner_length,
            inner_top_width=inner_depth,
        ).with_name("tray_walls")
        tray_walls.move_anchor_to(
            "outer_bottom_center",
            bottom_panel.world_anchor("top_center"),
        )

        return [bottom_panel, tray_walls]


class DishwasherTopCover(ConceptTemplate):
    def __init__(self, cover_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(cover_size=cover_size))
        self.semantic = "Cover"

    @staticmethod
    def _build_components(cover_size):
        cover_length, cover_height, cover_depth = cover_size
        cover = Cuboid(
            height=cover_height,
            top_length=cover_length,
            top_width=cover_depth,
        ).with_name("top_cover")
        cover.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        return [cover]


class SingleDishwasherLeg(ConceptTemplate):
    def __init__(self, leg_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(leg_size=leg_size))
        self.semantic = "Leg"

    @staticmethod
    def _build_components(leg_size):
        leg_length, leg_height, leg_depth = leg_size
        leg = Cuboid(
            height=leg_height,
            top_length=leg_length,
            top_width=leg_depth,
        ).with_name("single_leg")
        leg.move_anchor_to("top_center", (0.0, 0.0, 0.0))
        return [leg]


class MultilevelDishwasherLegSet(ConceptTemplate):
    def __init__(
        self,
        has_top_panel,
        top_panel_size,
        top_to_leg_offset,
        front_leg_size,
        rear_leg_size,
        leg_center_spacing,
        leg_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                has_top_panel=has_top_panel,
                top_panel_size=top_panel_size,
                top_to_leg_offset=top_to_leg_offset,
                front_leg_size=front_leg_size,
                rear_leg_size=rear_leg_size,
                leg_center_spacing=leg_center_spacing,
                leg_count=leg_count,
            )
        )
        self.semantic = "Leg"

    @staticmethod
    def _build_components(
        has_top_panel,
        top_panel_size,
        top_to_leg_offset,
        front_leg_size,
        rear_leg_size,
        leg_center_spacing,
        leg_count,
    ):
        components = []
        top_panel_length, top_panel_height, top_panel_depth = top_panel_size
        offset_x, offset_z = top_to_leg_offset
        front_spacing_x, rear_spacing_x, front_rear_spacing_z = leg_center_spacing

        leg_mount_y = 0.0
        if has_top_panel:
            top_panel = Cuboid(
                height=top_panel_height,
                top_length=top_panel_length,
                top_width=top_panel_depth,
            ).with_name("top_panel")
            top_panel.move_anchor_to("top_center", (0.0, 0.0, 0.0))
            components.append(top_panel)
            leg_mount_y = -top_panel_height

        if leg_count == 1:
            components.append(
                MultilevelDishwasherLegSet._leg(
                    name="center_leg",
                    leg_size=front_leg_size,
                    top_center=(offset_x, leg_mount_y, offset_z),
                )
            )
        elif leg_count == 2:
            components.extend(
                [
                    MultilevelDishwasherLegSet._leg(
                        name="right_leg",
                        leg_size=front_leg_size,
                        top_center=(
                            offset_x + front_spacing_x / 2.0,
                            leg_mount_y,
                            offset_z,
                        ),
                    ),
                    MultilevelDishwasherLegSet._leg(
                        name="left_leg",
                        leg_size=front_leg_size,
                        top_center=(
                            offset_x - front_spacing_x / 2.0,
                            leg_mount_y,
                            offset_z,
                        ),
                    ),
                ]
            )
        elif leg_count == 3:
            components.extend(
                [
                    MultilevelDishwasherLegSet._leg(
                        name="front_right_leg",
                        leg_size=front_leg_size,
                        top_center=(
                            offset_x + front_spacing_x / 2.0,
                            leg_mount_y,
                            offset_z + front_rear_spacing_z / 2.0,
                        ),
                    ),
                    MultilevelDishwasherLegSet._leg(
                        name="front_left_leg",
                        leg_size=front_leg_size,
                        top_center=(
                            offset_x - front_spacing_x / 2.0,
                            leg_mount_y,
                            offset_z + front_rear_spacing_z / 2.0,
                        ),
                    ),
                    MultilevelDishwasherLegSet._leg(
                        name="rear_center_leg",
                        leg_size=rear_leg_size,
                        top_center=(
                            offset_x,
                            leg_mount_y,
                            offset_z - front_rear_spacing_z / 2.0,
                        ),
                    ),
                ]
            )
        elif leg_count == 4:
            components.extend(
                [
                    MultilevelDishwasherLegSet._leg(
                        name="front_right_leg",
                        leg_size=front_leg_size,
                        top_center=(
                            offset_x + front_spacing_x / 2.0,
                            leg_mount_y,
                            offset_z + front_rear_spacing_z / 2.0,
                        ),
                    ),
                    MultilevelDishwasherLegSet._leg(
                        name="front_left_leg",
                        leg_size=front_leg_size,
                        top_center=(
                            offset_x - front_spacing_x / 2.0,
                            leg_mount_y,
                            offset_z + front_rear_spacing_z / 2.0,
                        ),
                    ),
                    MultilevelDishwasherLegSet._leg(
                        name="rear_right_leg",
                        leg_size=rear_leg_size,
                        top_center=(
                            offset_x + rear_spacing_x / 2.0,
                            leg_mount_y,
                            offset_z - front_rear_spacing_z / 2.0,
                        ),
                    ),
                    MultilevelDishwasherLegSet._leg(
                        name="rear_left_leg",
                        leg_size=rear_leg_size,
                        top_center=(
                            offset_x - rear_spacing_x / 2.0,
                            leg_mount_y,
                            offset_z - front_rear_spacing_z / 2.0,
                        ),
                    ),
                ]
            )

        return components

    @staticmethod
    def _leg(name, leg_size, top_center):
        leg_length, leg_height, leg_depth = leg_size
        leg = Cuboid(
            height=leg_height,
            top_length=leg_length,
            top_width=leg_depth,
        ).with_name(name)
        leg.move_anchor_to("top_center", top_center)
        return leg
