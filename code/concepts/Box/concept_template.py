from math import pi

from code.geometry import ConceptTemplate, Cuboid, Rectangular_Ring


def _degrees_to_radians(rotation_degrees):
    return [angle / 180.0 * pi for angle in rotation_degrees]


class OpenBoxBody(ConceptTemplate):
    def __init__(
        self,
        top_outer_size,
        bottom_outer_size,
        total_height,
        wall_thickness,
        top_to_bottom_offset=(0, 0),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                top_outer_size=top_outer_size,
                bottom_outer_size=bottom_outer_size,
                total_height=total_height,
                wall_thickness=wall_thickness,
                top_to_bottom_offset=top_to_bottom_offset,
            )
        )

    @staticmethod
    def _interpolate_middle_profile(
        top_outer_length,
        top_outer_width,
        bottom_outer_length,
        bottom_outer_width,
        total_height,
        bottom_height,
        top_offset_x,
        top_offset_z,
    ):
        split_fraction = bottom_height / total_height
        middle_outer_length = (
            bottom_outer_length * (1.0 - split_fraction)
            + top_outer_length * split_fraction
        )
        middle_outer_width = (
            bottom_outer_width * (1.0 - split_fraction)
            + top_outer_width * split_fraction
        )
        middle_offset_x = top_offset_x * split_fraction
        middle_offset_z = top_offset_z * split_fraction
        return (
            middle_outer_length,
            middle_outer_width,
            middle_offset_x,
            middle_offset_z,
        )

    @classmethod
    def _build_components(
        cls,
        top_outer_size,
        bottom_outer_size,
        total_height,
        wall_thickness,
        top_to_bottom_offset,
    ):
        top_outer_length, top_outer_width = top_outer_size
        bottom_outer_length, bottom_outer_width = bottom_outer_size
        wall_thickness_x, bottom_height, wall_thickness_z = wall_thickness
        top_offset_x, top_offset_z = top_to_bottom_offset

        shell_height = total_height - bottom_height
        (
            middle_outer_length,
            middle_outer_width,
            middle_offset_x,
            middle_offset_z,
        ) = cls._interpolate_middle_profile(
            top_outer_length=top_outer_length,
            top_outer_width=top_outer_width,
            bottom_outer_length=bottom_outer_length,
            bottom_outer_width=bottom_outer_width,
            total_height=total_height,
            bottom_height=bottom_height,
            top_offset_x=top_offset_x,
            top_offset_z=top_offset_z,
        )
        shell_offset = [top_offset_x - middle_offset_x, top_offset_z - middle_offset_z]

        bottom_plate = Cuboid(
            height=bottom_height,
            top_length=middle_outer_length,
            top_width=middle_outer_width,
            bottom_length=bottom_outer_length,
            bottom_width=bottom_outer_width,
            top_offset=[middle_offset_x, middle_offset_z],
        ).with_name("bottom_plate")
        bottom_plate.move_anchor_to("bottom_center", (0, -total_height / 2.0, 0))

        upper_shell = Rectangular_Ring(
            front_height=shell_height,
            outer_top_length=top_outer_length,
            outer_top_width=top_outer_width,
            inner_top_length=top_outer_length - wall_thickness_x * 2.0,
            inner_top_width=top_outer_width - wall_thickness_z * 2.0,
            outer_bottom_length=middle_outer_length,
            outer_bottom_width=middle_outer_width,
            inner_bottom_length=middle_outer_length - wall_thickness_x * 2.0,
            inner_bottom_width=middle_outer_width - wall_thickness_z * 2.0,
            top_bottom_offset=shell_offset,
        ).with_name("upper_open_shell")
        upper_shell.move_anchor_to(
            "outer_bottom_center", bottom_plate.world_anchor("top_center")
        )

        return [upper_shell, bottom_plate]


class HingedPanelBoxCover(ConceptTemplate):
    def __init__(self, panels, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(panels))

    @staticmethod
    def _build_components(panels):
        components = []
        for panel in panels:
            if not panel.get("enabled", True):
                continue

            panel_length, panel_height, panel_width = panel["size"]
            cover_panel = Cuboid(
                height=panel_height,
                top_length=panel_length,
                top_width=panel_width,
                rotation=_degrees_to_radians(panel.get("rotation_degrees", (0, 0, 0))),
            ).with_name(panel["name"])
            cover_panel.move_anchor_to("bottom_center", panel["hinge_anchor"])
            components.append(cover_panel)

        return components


class RectangularBoxCover(ConceptTemplate):
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

    @staticmethod
    def _build_components(outer_size, inner_opening_size):
        outer_length, outer_height, outer_width = outer_size
        inner_length, rim_height, inner_width = inner_opening_size
        top_plate_height = outer_height - rim_height

        lower_rim = Rectangular_Ring(
            front_height=rim_height,
            outer_top_length=outer_length,
            outer_top_width=outer_width,
            inner_top_length=inner_length,
            inner_top_width=inner_width,
        ).with_name("lower_open_rim")
        lower_rim.move_anchor_to("outer_bottom_center", (0, 0, outer_width / 2.0))

        top_plate = Cuboid(
            height=top_plate_height,
            top_length=outer_length,
            top_width=outer_width,
        ).with_name("top_plate")
        top_plate.move_anchor_to(
            "bottom_center", lower_rim.world_anchor("outer_top_center")
        )

        return [top_plate, lower_rim]


class BoxLegSet(ConceptTemplate):
    def __init__(self, legs, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(legs))

    @staticmethod
    def _build_components(legs):
        components = []
        for leg in legs:
            if not leg.get("enabled", True):
                continue

            leg_length, leg_height, leg_width = leg["size"]
            leg_primitive = Cuboid(
                height=leg_height,
                top_length=leg_length,
                top_width=leg_width,
            ).with_name(leg["name"])
            leg_primitive.move_anchor_to("top_center", leg["top_anchor"])
            components.append(leg_primitive)

        return components
