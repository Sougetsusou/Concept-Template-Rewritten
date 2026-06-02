from math import atan, cos, pi, sin

from code.geometry_rewritten import (
    Box_Cylinder_Ring,
    ConceptTemplate,
    Cuboid,
    Cylinder,
    Rectangular_Ring,
    Ring,
)


WASHINGMACHINE_ROTATION_ORDER = "XYZ"


class FrontFacingRollerWashingMachineBody(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        drum_opening_size,
        drum_opening_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=WASHINGMACHINE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                drum_opening_size=drum_opening_size,
                drum_opening_offset=drum_opening_offset,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(outer_size, drum_opening_size, drum_opening_offset):
        outer_length, outer_height, outer_depth = outer_size
        opening_radius, opening_frame_depth = drum_opening_size
        opening_offset_x, opening_offset_y = drum_opening_offset
        rear_body_depth = outer_depth - opening_frame_depth

        front_frame = Box_Cylinder_Ring(
            outer_height=outer_height,
            outer_length=outer_length,
            outer_width=opening_frame_depth,
            inner_radius=opening_radius,
            inner_cylinder_offset=(opening_offset_x, opening_offset_y),
        ).with_name("front_drum_opening_frame")
        front_frame.move_anchor_to(
            "outer_front_center",
            (0.0, 0.0, outer_depth / 2.0),
        )

        rear_body = Cuboid(
            height=outer_height,
            top_length=outer_length,
            top_width=rear_body_depth,
        ).with_name("rear_solid_body")
        rear_body.move_anchor_to(
            "front_center",
            front_frame.world_anchor("outer_back_center"),
        )

        return [rear_body, front_frame]


class UprightRollerWashingMachineBody(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        top_opening_size,
        top_opening_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=WASHINGMACHINE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                top_opening_size=top_opening_size,
                top_opening_offset=top_opening_offset,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(outer_size, top_opening_size, top_opening_offset):
        outer_length, outer_height, outer_depth = outer_size
        opening_radius, opening_frame_height = top_opening_size
        opening_offset_x, opening_offset_z = top_opening_offset
        lower_body_height = outer_height - opening_frame_height

        lower_body = Cuboid(
            height=lower_body_height,
            top_length=outer_length,
            top_width=outer_depth,
        ).with_name("lower_solid_body")
        lower_body.move_anchor_to(
            "bottom_center",
            (0.0, -outer_height / 2.0, 0.0),
        )

        upper_frame = Box_Cylinder_Ring(
            outer_height=outer_depth,
            outer_length=outer_length,
            outer_width=opening_frame_height,
            inner_radius=opening_radius,
            inner_cylinder_offset=(opening_offset_x, -opening_offset_z),
            rotation=(-pi / 2.0, 0.0, 0.0),
        ).with_name("top_drum_opening_frame")
        upper_frame.move_anchor_to(
            "outer_back_center",
            lower_body.world_anchor("top_center"),
        )

        return [lower_body, upper_frame]


class CuboidalWashingMachineBody(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        wall_thickness,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=WASHINGMACHINE_ROTATION_ORDER,
        )
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
        depth_wall_thickness, length_wall_thickness, bottom_thickness = wall_thickness
        shell_height = outer_height - bottom_thickness
        inner_length = outer_length - length_wall_thickness * 2.0
        inner_depth = outer_depth - depth_wall_thickness * 2.0

        bottom_plate = Cuboid(
            height=bottom_thickness,
            top_length=outer_length,
            top_width=outer_depth,
        ).with_name("bottom_plate")
        bottom_plate.move_anchor_to(
            "bottom_center",
            (0.0, -outer_height / 2.0, 0.0),
        )

        upper_shell = Rectangular_Ring(
            front_height=shell_height,
            outer_top_length=outer_length,
            outer_top_width=outer_depth,
            inner_top_length=inner_length,
            inner_top_width=inner_depth,
        ).with_name("upper_open_shell")
        upper_shell.move_anchor_to(
            "outer_bottom_center",
            bottom_plate.world_anchor("top_center"),
        )

        return [bottom_plate, upper_shell]


class RollerWashingMachineDoor(ConceptTemplate):
    def __init__(
        self,
        outer_ring_size,
        center_disc_size,
        center_disc_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=WASHINGMACHINE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                outer_ring_size=outer_ring_size,
                center_disc_size=center_disc_size,
                center_disc_offset=center_disc_offset,
            )
        )
        self.semantic = "Door"

    @staticmethod
    def _build_components(outer_ring_size, center_disc_size, center_disc_offset):
        outer_radius, middle_outer_radius, outer_depth = outer_ring_size
        center_radius, center_depth = center_disc_size
        center_offset_y, center_offset_z = center_disc_offset
        door_frame_center = (outer_radius, 0.0, outer_depth / 2.0)
        door_rotation = (pi / 2.0, 0.0, 0.0)

        outer_ring = Ring(
            height=outer_depth,
            outer_top_radius=outer_radius,
            inner_top_radius=middle_outer_radius,
            position=door_frame_center,
            rotation=door_rotation,
        ).with_name("outer_door_ring")

        middle_ring = Ring(
            height=center_depth,
            outer_top_radius=middle_outer_radius,
            inner_top_radius=center_radius,
            inner_offset=(center_offset_y, center_offset_z),
            position=door_frame_center,
            rotation=door_rotation,
        ).with_name("offset_middle_ring")

        center_disc = Cylinder(
            height=center_depth,
            top_radius=center_radius,
            position=(
                outer_radius,
                center_offset_y,
                outer_depth / 2.0 + center_offset_z,
            ),
            rotation=door_rotation,
        ).with_name("offset_center_disc")

        return [outer_ring, middle_ring, center_disc]


class CuboidalWashingMachineDoor(ConceptTemplate):
    def __init__(
        self,
        panel_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=WASHINGMACHINE_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(panel_size=panel_size))
        self.semantic = "Door"

    @staticmethod
    def _build_components(panel_size):
        panel_length, panel_height, panel_depth = panel_size
        panel = Cuboid(
            height=panel_height,
            top_length=panel_length,
            top_width=panel_depth,
        ).with_name("door_panel")
        panel.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        return [panel]


class SlopedControlButtonPanel(ConceptTemplate):
    def __init__(
        self,
        panel_size,
        button_specs,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=WASHINGMACHINE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                panel_size=panel_size,
                button_specs=button_specs,
            )
        )
        self.semantic = "Button"

    @classmethod
    def _build_components(cls, panel_size, button_specs):
        panel_length, panel_height, top_depth, bottom_depth = panel_size
        panel = Cuboid(
            height=panel_height,
            top_length=panel_length,
            top_width=top_depth,
            bottom_width=bottom_depth,
            top_offset=(0.0, -(bottom_depth - top_depth) / 2.0),
        ).with_name("sloped_control_panel")
        panel.move_anchor_to("bottom_back_center", (0.0, -panel_height / 2.0, 0.0))

        slope_angle = cls._slope_angle(panel_size)
        components = [panel]

        for button_index, button_spec in enumerate(button_specs, start=1):
            button_length, button_height, button_depth = button_spec["size"]
            offset_x, offset_along_slope = button_spec["surface_offset"]
            button = Cuboid(
                height=button_height,
                top_length=button_length,
                top_width=button_depth,
                rotation=(-slope_angle, 0.0, 0.0),
            ).with_name(f"button_{button_index}")
            button.move_anchor_to(
                "back_center",
                cls._panel_surface_point(
                    panel_size=panel_size,
                    offset_x=offset_x,
                    offset_along_slope=offset_along_slope,
                    slope_angle=slope_angle,
                ),
            )
            components.append(button)

        return components

    @staticmethod
    def _slope_angle(panel_size):
        _, panel_height, top_depth, bottom_depth = panel_size
        return atan((bottom_depth - top_depth) / panel_height)

    @staticmethod
    def _panel_surface_point(panel_size, offset_x, offset_along_slope, slope_angle):
        _, _, top_depth, bottom_depth = panel_size
        return (
            offset_x,
            offset_along_slope * cos(slope_angle),
            (top_depth + bottom_depth) / 2.0
            - offset_along_slope * sin(slope_angle),
        )
