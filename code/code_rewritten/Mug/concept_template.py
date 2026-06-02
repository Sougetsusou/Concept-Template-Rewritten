from math import pi, sqrt

from code.geometry_rewritten import (
    ConceptTemplate,
    Cuboid,
    Cylinder,
    Rectangular_Ring,
    Ring,
    Torus,
)


DEGREES_TO_RADIANS = pi / 180.0
SQUARE_PROFILE_SCALE = sqrt(2.0)


class CylindricalMugBody(ConceptTemplate):
    def __init__(
        self,
        outer_profile,
        inner_opening,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(outer_profile, inner_opening))
        self.semantic = "Body"

    @staticmethod
    def _split_outer_radius(top_outer_radius, bottom_outer_radius, total_height, open_height):
        open_fraction = open_height / total_height
        return top_outer_radius * (1.0 - open_fraction) + bottom_outer_radius * open_fraction

    @classmethod
    def _build_components(cls, outer_profile, inner_opening):
        top_outer_radius, bottom_outer_radius, total_height = outer_profile
        top_inner_radius, bottom_inner_radius, open_height = inner_opening
        bottom_height = total_height - open_height
        split_outer_radius = cls._split_outer_radius(
            top_outer_radius=top_outer_radius,
            bottom_outer_radius=bottom_outer_radius,
            total_height=total_height,
            open_height=open_height,
        )

        bottom = Cylinder(
            height=bottom_height,
            top_radius=split_outer_radius,
            bottom_radius=bottom_outer_radius,
        ).with_name("solid_lower_body")
        bottom.move_anchor_to("bottom_center", (0.0, -total_height / 2.0, 0.0))

        upper = Ring(
            height=open_height,
            outer_top_radius=top_outer_radius,
            inner_top_radius=top_inner_radius,
            outer_bottom_radius=split_outer_radius,
            inner_bottom_radius=bottom_inner_radius,
        ).with_name("open_upper_wall")
        upper.move_anchor_to("axis_bottom_center", bottom.world_anchor("top_center"))

        return [bottom, upper]


class PrismaticMugBody(ConceptTemplate):
    def __init__(
        self,
        outer_profile,
        inner_opening,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(outer_profile, inner_opening))
        self.semantic = "Body"

    @staticmethod
    def _profile_width(radius):
        return radius * SQUARE_PROFILE_SCALE

    @classmethod
    def _build_components(cls, outer_profile, inner_opening):
        top_outer_radius, bottom_outer_radius, total_height = outer_profile
        top_inner_radius, bottom_inner_radius, open_height = inner_opening
        bottom_height = total_height - open_height
        split_outer_radius = CylindricalMugBody._split_outer_radius(
            top_outer_radius=top_outer_radius,
            bottom_outer_radius=bottom_outer_radius,
            total_height=total_height,
            open_height=open_height,
        )

        bottom = Cuboid(
            height=bottom_height,
            top_length=cls._profile_width(split_outer_radius),
            top_width=cls._profile_width(split_outer_radius),
            bottom_length=cls._profile_width(bottom_outer_radius),
            bottom_width=cls._profile_width(bottom_outer_radius),
        ).with_name("solid_lower_body")
        bottom.move_anchor_to("bottom_center", (0.0, -total_height / 2.0, 0.0))

        upper = Rectangular_Ring(
            front_height=open_height,
            outer_top_length=cls._profile_width(top_outer_radius),
            outer_top_width=cls._profile_width(top_outer_radius),
            inner_top_length=cls._profile_width(top_inner_radius),
            inner_top_width=cls._profile_width(top_inner_radius),
            outer_bottom_length=cls._profile_width(split_outer_radius),
            outer_bottom_width=cls._profile_width(split_outer_radius),
            inner_bottom_length=cls._profile_width(bottom_inner_radius),
            inner_bottom_width=cls._profile_width(bottom_inner_radius),
        ).with_name("open_upper_wall")
        upper.move_anchor_to("outer_bottom_center", bottom.world_anchor("top_center"))

        return [bottom, upper]


class MultilevelMugBody(ConceptTemplate):
    def __init__(
        self,
        base_section,
        upper_sections,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                base_section=base_section,
                upper_sections=upper_sections,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _base_split_outer_radius(base_section):
        total_height = base_section["total_height"]
        open_height = base_section["open_height"]
        open_fraction = open_height / total_height
        return (
            base_section["top_outer_radius"] * (1.0 - open_fraction)
            + base_section["bottom_outer_radius"] * open_fraction
        )

    @classmethod
    def _build_components(cls, base_section, upper_sections):
        total_height = base_section["total_height"]
        open_height = base_section["open_height"]
        solid_height = total_height - open_height
        split_outer_radius = cls._base_split_outer_radius(base_section)

        components = []
        bottom = Cylinder(
            height=solid_height,
            top_radius=split_outer_radius,
            bottom_radius=base_section["bottom_outer_radius"],
        ).with_name("base_solid_lower_body")
        bottom.move_anchor_to("bottom_center", (0.0, -total_height / 2.0, 0.0))
        components.append(bottom)

        first_open_wall = Ring(
            height=open_height,
            outer_top_radius=base_section["top_outer_radius"],
            inner_top_radius=base_section["top_inner_radius"],
            outer_bottom_radius=split_outer_radius,
            inner_bottom_radius=base_section["bottom_inner_radius"],
        ).with_name("base_open_upper_wall")
        first_open_wall.move_anchor_to("axis_bottom_center", bottom.world_anchor("top_center"))
        components.append(first_open_wall)

        previous_top_anchor = first_open_wall.world_anchor("axis_top_center")
        previous_outer_radius = base_section["top_outer_radius"]
        previous_inner_radius = base_section["top_inner_radius"]
        for section_index, section in enumerate(upper_sections, start=2):
            section_height = section["height"]
            section_outer_radius = section["top_outer_radius"]
            section_inner_radius = section["top_inner_radius"]
            wall = Ring(
                height=section_height,
                outer_top_radius=section_outer_radius,
                inner_top_radius=section_inner_radius,
                outer_bottom_radius=previous_outer_radius,
                inner_bottom_radius=previous_inner_radius,
            ).with_name(f"upper_wall_{section_index}")
            wall.move_anchor_to("axis_bottom_center", previous_top_anchor)
            components.append(wall)
            previous_top_anchor = wall.world_anchor("axis_top_center")
            previous_outer_radius = section_outer_radius
            previous_inner_radius = section_inner_radius

        return components


class TrifoldMugHandle(ConceptTemplate):
    def __init__(
        self,
        bar_cross_section,
        upper_bar_length,
        lower_bar_length,
        connector_cross_section,
        upper_bar_angle_degrees,
        lower_bar_angle_degrees,
        bar_anchor_spacing,
        upper_mount_depth,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                bar_cross_section=bar_cross_section,
                upper_bar_length=upper_bar_length,
                lower_bar_length=lower_bar_length,
                connector_cross_section=connector_cross_section,
                upper_bar_angle_degrees=upper_bar_angle_degrees,
                lower_bar_angle_degrees=lower_bar_angle_degrees,
                bar_anchor_spacing=bar_anchor_spacing,
                upper_mount_depth=upper_mount_depth,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _distance_between(start_point, end_point):
        start_x, start_y, start_z = start_point
        end_x, end_y, end_z = end_point
        delta_x = end_x - start_x
        delta_y = end_y - start_y
        delta_z = end_z - start_z
        return sqrt(delta_x * delta_x + delta_y * delta_y + delta_z * delta_z)

    @classmethod
    def _build_components(
        cls,
        bar_cross_section,
        upper_bar_length,
        lower_bar_length,
        connector_cross_section,
        upper_bar_angle_degrees,
        lower_bar_angle_degrees,
        bar_anchor_spacing,
        upper_mount_depth,
    ):
        bar_width, bar_thickness = bar_cross_section
        connector_width, connector_depth = connector_cross_section
        upper_angle = upper_bar_angle_degrees * DEGREES_TO_RADIANS
        lower_angle = lower_bar_angle_degrees * DEGREES_TO_RADIANS

        upper_bar = Cuboid(
            height=bar_thickness,
            top_length=bar_width,
            top_width=upper_bar_length,
            rotation=(upper_angle, 0.0, 0.0),
        ).with_name("upper_mount_bar")
        upper_bar.move_anchor_to(
            "back_center",
            (0.0, bar_anchor_spacing / 2.0, upper_mount_depth),
        )

        lower_bar = Cuboid(
            height=bar_thickness,
            top_length=bar_width,
            top_width=lower_bar_length,
            rotation=(lower_angle, 0.0, 0.0),
        ).with_name("lower_mount_bar")
        lower_bar.move_anchor_to(
            "back_center",
            (0.0, -bar_anchor_spacing / 2.0, 0.0),
        )

        upper_front_x, upper_front_y, upper_front_z = upper_bar.world_anchor("front_center")
        lower_front_x, lower_front_y, lower_front_z = lower_bar.world_anchor("front_center")
        upper_mount_line = (upper_front_x, upper_front_y, upper_front_z)
        lower_mount_line = (lower_front_x, lower_front_y, lower_front_z)
        mount_line_midpoint = (
            (upper_front_x + lower_front_x) / 2.0,
            (upper_front_y + lower_front_y) / 2.0,
            (upper_front_z + lower_front_z) / 2.0,
        )
        connector_span = cls._distance_between(lower_mount_line, upper_mount_line)

        connector = Cuboid(
            height=connector_span + bar_thickness,
            top_length=connector_width,
            top_width=connector_depth,
        ).with_name("front_bridge_bar")
        connector.align_axis_between_points(
            "y",
            lower_mount_line,
            upper_mount_line,
        )
        connector.move_local_point_to(
            (0.0, 0.0, -connector_depth / 2.0),
            mount_line_midpoint,
        )

        return [upper_bar, lower_bar, connector]


class CurvedMugHandle(ConceptTemplate):
    def __init__(
        self,
        curve_radius,
        tube_radius,
        arc_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                curve_radius=curve_radius,
                tube_radius=tube_radius,
                arc_angle_degrees=arc_angle_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(curve_radius, tube_radius, arc_angle_degrees):
        handle = Torus(
            central_radius=curve_radius,
            start_torus_radius=tube_radius,
            exist_angle=arc_angle_degrees * DEGREES_TO_RADIANS,
            rotation=(0.0, 0.0, pi / 2.0),
        ).with_name("curved_handle_arc")
        return [handle]


class CylindricalMugComponent(ConceptTemplate):
    def __init__(
        self,
        radius,
        height,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(radius=radius, height=height))
        self.semantic = "Cylinder"

    @staticmethod
    def _build_components(radius, height):
        return [Cylinder(height=height, top_radius=radius).with_name("cylinder")]
