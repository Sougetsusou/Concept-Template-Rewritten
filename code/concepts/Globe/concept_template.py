from math import cos, pi, sin

from code.geometry import (
    ConceptTemplate,
    Cuboid,
    Cylinder,
    Ring,
    Sphere,
    Torus,
    radial_array_frames,
)


DEGREES_TO_RADIANS = pi / 180.0


class GlobeSphere(ConceptTemplate):
    def __init__(self, radius, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh([Sphere(radius).with_name("globe_sphere")])
        self.semantic = "Sphere"


class SemiRingGlobeBracket(ConceptTemplate):
    def __init__(
        self,
        pivot_size,
        pivot_continuous,
        pivot_separation,
        has_top_endpoint,
        has_bottom_endpoint,
        endpoint_radius,
        bracket_size,
        bracket_arc_degrees,
        bracket_offset,
        bracket_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                pivot_size=pivot_size,
                pivot_continuous=pivot_continuous,
                pivot_separation=pivot_separation,
                has_top_endpoint=has_top_endpoint,
                has_bottom_endpoint=has_bottom_endpoint,
                endpoint_radius=endpoint_radius,
                bracket_size=bracket_size,
                bracket_arc_degrees=bracket_arc_degrees,
                bracket_offset=bracket_offset,
                bracket_rotation_degrees=bracket_rotation_degrees,
            )
        )
        self.semantic = "Bracket"

    @classmethod
    def _build_components(
        cls,
        pivot_size,
        pivot_continuous,
        pivot_separation,
        has_top_endpoint,
        has_bottom_endpoint,
        endpoint_radius,
        bracket_size,
        bracket_arc_degrees,
        bracket_offset,
        bracket_rotation_degrees,
    ):
        pivot_radius, pivot_height = pivot_size
        bracket_outer_radius, bracket_inner_radius, bracket_depth = bracket_size
        bracket_arc = bracket_arc_degrees * DEGREES_TO_RADIANS
        bracket_rotation = bracket_rotation_degrees * DEGREES_TO_RADIANS

        components, top_mount, bottom_mount = cls._pivot_components(
            pivot_radius=pivot_radius,
            pivot_height=pivot_height,
            pivot_continuous=pivot_continuous,
            pivot_separation=pivot_separation,
        )

        if has_top_endpoint:
            top_endpoint = Sphere(endpoint_radius).with_name("top_endpoint")
            top_endpoint.move_anchor_to("bottom_pole", top_mount)
            components.append(top_endpoint)

        if has_bottom_endpoint:
            bottom_endpoint = Sphere(endpoint_radius).with_name("bottom_endpoint")
            bottom_endpoint.move_anchor_to("top_pole", bottom_mount)
            components.append(bottom_endpoint)

        bracket = Ring(
            height=bracket_depth,
            outer_top_radius=bracket_outer_radius,
            inner_top_radius=bracket_inner_radius,
            exist_angle=bracket_arc,
            rotation=(0.0, -pi / 2.0 + bracket_arc / 2.0 - bracket_rotation, pi / 2.0),
        ).with_name("semi_ring_bracket")
        bracket.move_anchor_to("arc_origin", (0.0, bracket_offset, 0.0))
        components.append(bracket)

        return components

    @staticmethod
    def _pivot_components(
        pivot_radius,
        pivot_height,
        pivot_continuous,
        pivot_separation,
    ):
        if pivot_continuous:
            pivot = Cylinder(height=pivot_height, top_radius=pivot_radius).with_name(
                "continuous_pivot"
            )
            return [pivot], pivot.world_anchor("top_center"), pivot.world_anchor("bottom_center")

        top_pivot = Cylinder(height=pivot_height, top_radius=pivot_radius).with_name(
            "top_pivot"
        )
        top_pivot.move_anchor_to("bottom_center", (0.0, pivot_separation / 2.0, 0.0))

        bottom_pivot = Cylinder(height=pivot_height, top_radius=pivot_radius).with_name(
            "bottom_pivot"
        )
        bottom_pivot.move_anchor_to("top_center", (0.0, -pivot_separation / 2.0, 0.0))

        return (
            [top_pivot, bottom_pivot],
            top_pivot.world_anchor("top_center"),
            bottom_pivot.world_anchor("bottom_center"),
        )


class TiltedGlobeBracket(ConceptTemplate):
    def __init__(
        self,
        pivot_size,
        bracket_size,
        circle_thickness,
        circle_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                pivot_size=pivot_size,
                bracket_size=bracket_size,
                circle_thickness=circle_thickness,
                circle_rotation_degrees=circle_rotation_degrees,
            )
        )
        self.semantic = "Bracket"

    @staticmethod
    def _build_components(
        pivot_size,
        bracket_size,
        circle_thickness,
        circle_rotation_degrees,
    ):
        pivot_radius, pivot_length = pivot_size
        bracket_outer_radius, bracket_inner_radius, bracket_depth = bracket_size
        circle_radial_thickness, circle_depth = circle_thickness
        circle_rotation = circle_rotation_degrees * DEGREES_TO_RADIANS

        pivot = Cylinder(
            height=pivot_length,
            top_radius=pivot_radius,
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("horizontal_pivot")

        bracket = Ring(
            height=bracket_depth,
            outer_top_radius=bracket_outer_radius,
            inner_top_radius=bracket_inner_radius,
            exist_angle=pi,
            rotation=(pi / 2.0, pi / 2.0, 0.0),
        ).with_name("tilted_half_ring")

        inner_circle = Ring(
            height=circle_depth,
            outer_top_radius=bracket_inner_radius,
            inner_top_radius=bracket_inner_radius - circle_radial_thickness,
            rotation=(0.0, 0.0, circle_rotation),
        ).with_name("inner_full_ring")

        return [pivot, bracket, inner_circle]


class EnclosedGlobeBracket(ConceptTemplate):
    def __init__(
        self,
        bracket_size,
        circle_radius,
        circle_thickness,
        half_circle_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                bracket_size=bracket_size,
                circle_radius=circle_radius,
                circle_thickness=circle_thickness,
                half_circle_count=half_circle_count,
            )
        )
        self.semantic = "Bracket"

    @staticmethod
    def _build_components(
        bracket_size,
        circle_radius,
        circle_thickness,
        half_circle_count,
    ):
        bracket_outer_radius, bracket_inner_radius, bracket_depth = bracket_size
        circle_radial_thickness, circle_depth = circle_thickness

        components = [
            Ring(
                height=bracket_depth,
                outer_top_radius=bracket_outer_radius,
                inner_top_radius=bracket_inner_radius,
                exist_angle=pi,
                rotation=(pi / 2.0, pi / 2.0, 0.0),
            ).with_name("front_half_ring")
        ]

        if half_circle_count == 2:
            components.append(
                Ring(
                    height=bracket_depth,
                    outer_top_radius=bracket_outer_radius,
                    inner_top_radius=bracket_inner_radius,
                    exist_angle=pi,
                    rotation=(pi / 2.0, 0.0, 0.0),
                ).with_name("side_half_ring")
            )

        components.append(
            Ring(
                height=circle_depth,
                outer_top_radius=circle_radius + circle_radial_thickness / 2.0,
                inner_top_radius=circle_radius - circle_radial_thickness / 2.0,
            ).with_name("equator_ring")
        )
        return components


class CylindricalGlobeBase(ConceptTemplate):
    def __init__(
        self,
        bottom_section,
        top_section,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                bottom_section=bottom_section,
                top_section=top_section,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(bottom_section, top_section):
        top_top_radius, top_bottom_radius, top_height = top_section
        bottom_top_radius, bottom_bottom_radius, bottom_height = bottom_section

        top = Cylinder(
            height=top_height,
            top_radius=top_top_radius,
            bottom_radius=top_bottom_radius,
        ).with_name("top_cylindrical_step")
        top.move_anchor_to("top_center", (0.0, 0.0, 0.0))

        bottom = Cylinder(
            height=bottom_height,
            top_radius=bottom_top_radius,
            bottom_radius=bottom_bottom_radius,
        ).with_name("bottom_cylindrical_step")
        bottom.move_anchor_to("top_center", top.world_anchor("bottom_center"))

        return [top, bottom]


class CuboidalGlobeBase(ConceptTemplate):
    def __init__(
        self,
        bottom_size,
        top_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                bottom_size=bottom_size,
                top_size=top_size,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(bottom_size, top_size):
        top_length, top_height, top_depth = top_size
        bottom_length, bottom_height, bottom_depth = bottom_size

        top = Cuboid(
            height=top_height,
            top_length=top_length,
            top_width=top_depth,
        ).with_name("top_cuboidal_step")
        top.move_anchor_to("top_center", (0.0, 0.0, 0.0))

        bottom = Cuboid(
            height=bottom_height,
            top_length=bottom_length,
            top_width=bottom_depth,
        ).with_name("bottom_cuboidal_step")
        bottom.move_anchor_to("top_center", top.world_anchor("bottom_center"))

        return [top, bottom]


class StarShapedGlobeBase(ConceptTemplate):
    def __init__(
        self,
        top_disk_size,
        leg_size,
        leg_count,
        tilt_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                top_disk_size=top_disk_size,
                leg_size=leg_size,
                leg_count=leg_count,
                tilt_degrees=tilt_degrees,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(top_disk_size, leg_size, leg_count, tilt_degrees):
        top_radius, top_height = top_disk_size
        leg_length, leg_height, leg_depth = leg_size
        tilt = tilt_degrees * DEGREES_TO_RADIANS

        top = Cylinder(height=top_height, top_radius=top_radius).with_name("top_disk")
        top.move_anchor_to("top_center", (0.0, 0.0, 0.0))

        leg_center_y = -top_height + leg_height / 2.0 - leg_depth * sin(tilt) / 2.0
        radial_center = leg_depth * cos(tilt) / 2.0
        components = [top]

        for frame in radial_array_frames(
            count=leg_count,
            center_point=(0.0, leg_center_y, radial_center),
            item_rotation=(tilt, 0.0, 0.0),
            radial_axis="y",
            angle_sign=-1.0,
        ):
            leg = Cuboid(
                height=leg_height,
                top_length=leg_length,
                top_width=leg_depth,
            ).with_name(f"radial_leg_{frame.index + 1}")
            leg.set_rotation_matrix(frame.rotation_matrix)
            leg.set_transform(position=frame.position)
            components.append(leg)

        return components


class SpecialGlobeBase(ConceptTemplate):
    def __init__(
        self,
        torus_size,
        top_connector_size,
        top_tilt_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                torus_size=torus_size,
                top_connector_size=top_connector_size,
                top_tilt_degrees=top_tilt_degrees,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(torus_size, top_connector_size, top_tilt_degrees):
        central_radius, tube_radius = torus_size
        connector_radius, connector_height = top_connector_size
        top_tilt = top_tilt_degrees * DEGREES_TO_RADIANS

        connector = Cylinder(
            height=connector_height,
            top_radius=connector_radius,
            rotation=(top_tilt, 0.0, 0.0),
        ).with_name("tilted_connector")
        connector.move_anchor_to("top_center", (0.0, 0.0, 0.0))

        connector_bottom_x, connector_bottom_y, connector_bottom_z = connector.world_anchor(
            "bottom_center"
        )
        torus = Torus(
            central_radius=central_radius,
            start_torus_radius=tube_radius,
            position=(
                connector_bottom_x,
                connector_bottom_y,
                connector_bottom_z + central_radius,
            ),
        ).with_name("round_torus_base")

        return [connector, torus]


class TableLikeGlobeBase(ConceptTemplate):
    def __init__(
        self,
        ring_size,
        leg_count,
        leg_size,
        leg_radial_distance,
        has_feet,
        foot_size,
        foot_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                ring_size=ring_size,
                leg_count=leg_count,
                leg_size=leg_size,
                leg_radial_distance=leg_radial_distance,
                has_feet=has_feet,
                foot_size=foot_size,
                foot_offset=foot_offset,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(
        ring_size,
        leg_count,
        leg_size,
        leg_radial_distance,
        has_feet,
        foot_size,
        foot_offset,
    ):
        ring_outer_radius, ring_inner_radius, ring_height = ring_size
        leg_radius, leg_height = leg_size
        foot_length, foot_height, foot_depth = foot_size

        ring = Ring(
            height=ring_height,
            outer_top_radius=ring_outer_radius,
            inner_top_radius=ring_inner_radius,
        ).with_name("top_ring")
        _, ring_bottom_y, _ = ring.world_anchor("axis_bottom_center")

        components = [ring]
        if int(leg_count) <= 0:
            return components

        leg_center_y = ring_bottom_y - leg_height / 2.0
        foot_center_y = ring_bottom_y - leg_height + foot_height / 2.0 + foot_offset

        for frame in radial_array_frames(
            count=int(leg_count),
            center_point=(leg_radial_distance, leg_center_y, 0.0),
            radial_axis="y",
            angle_sign=-1.0,
        ):
            leg = Cylinder(
                height=leg_height,
                top_radius=leg_radius,
                position=frame.position,
            ).with_name(f"vertical_leg_{frame.index + 1}")
            components.append(leg)

        if has_feet:
            for frame in radial_array_frames(
                count=int(leg_count),
                center_point=(foot_length / 2.0, foot_center_y, 0.0),
                radial_axis="y",
                angle_sign=-1.0,
            ):
                foot = Cuboid(
                    height=foot_height,
                    top_length=foot_length,
                    top_width=foot_depth,
                ).with_name(f"radial_foot_{frame.index + 1}")
                foot.set_rotation_matrix(frame.rotation_matrix)
                foot.set_transform(position=frame.position)
                components.append(foot)

        return components
