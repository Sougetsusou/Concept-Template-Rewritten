from math import cos, pi, sin

import numpy as np

from code.geometry import ConceptTemplate, Cuboid, Cylinder, Ring, Sphere, Torus


DEGREES_TO_RADIANS = pi / 180.0


class SemiSphericalKettleBody(ConceptTemplate):
    def __init__(
        self,
        horizontal_radius,
        vertical_radii,
        section_angles_degrees,
        bottom_profile,
        x_radius_scale,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                horizontal_radius=horizontal_radius,
                vertical_radii=vertical_radii,
                section_angles_degrees=section_angles_degrees,
                bottom_profile=bottom_profile,
                x_radius_scale=x_radius_scale,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(
        horizontal_radius,
        vertical_radii,
        section_angles_degrees,
        bottom_profile,
        x_radius_scale,
    ):
        upper_vertical_radius, lower_vertical_radius = vertical_radii
        upper_angle_degrees, lower_angle_degrees = section_angles_degrees
        bottom_radius, bottom_height = bottom_profile
        upper_angle = upper_angle_degrees * DEGREES_TO_RADIANS
        lower_angle = lower_angle_degrees * DEGREES_TO_RADIANS

        upper_shell = Sphere(
            radius=horizontal_radius * x_radius_scale,
            radius_y=upper_vertical_radius,
            radius_z=horizontal_radius,
            top_angle=pi / 2.0 - upper_angle,
            bottom_angle=pi / 2.0,
        ).with_name("upper_spherical_shell")

        lower_shell = Sphere(
            radius=horizontal_radius * x_radius_scale,
            radius_y=lower_vertical_radius,
            radius_z=horizontal_radius,
            top_angle=pi / 2.0 - lower_angle,
            bottom_angle=pi / 2.0,
            rotation=(pi, 0.0, 0.0),
        ).with_name("lower_spherical_shell")

        shell_bottom_radius = horizontal_radius * cos(lower_angle)
        shell_bottom_y = -lower_vertical_radius * sin(lower_angle)
        bottom = Cylinder(
            height=bottom_height,
            top_radius=shell_bottom_radius * x_radius_scale,
            bottom_radius=bottom_radius * x_radius_scale,
            top_radius_z=shell_bottom_radius,
            bottom_radius_z=bottom_radius,
        ).with_name("projected_bottom_foot")
        bottom.move_anchor_to("top_center", (0.0, shell_bottom_y, 0.0))

        return [upper_shell, lower_shell, bottom]


class SphericalCylindricalKettleBody(ConceptTemplate):
    def __init__(
        self,
        horizontal_radius,
        vertical_radius,
        shell_angle_degrees,
        bottom_profile,
        x_radius_scale,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                horizontal_radius=horizontal_radius,
                vertical_radius=vertical_radius,
                shell_angle_degrees=shell_angle_degrees,
                bottom_profile=bottom_profile,
                x_radius_scale=x_radius_scale,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(
        horizontal_radius,
        vertical_radius,
        shell_angle_degrees,
        bottom_profile,
        x_radius_scale,
    ):
        bottom_radius, bottom_height = bottom_profile
        shell_angle = shell_angle_degrees * DEGREES_TO_RADIANS

        shell = Sphere(
            radius=horizontal_radius * x_radius_scale,
            radius_y=vertical_radius,
            radius_z=horizontal_radius,
            top_angle=pi / 2.0 - shell_angle,
            bottom_angle=pi / 2.0,
        ).with_name("spherical_upper_shell")

        bottom = Cylinder(
            height=bottom_height,
            top_radius=horizontal_radius * x_radius_scale,
            bottom_radius=bottom_radius * x_radius_scale,
            top_radius_z=horizontal_radius,
            bottom_radius_z=bottom_radius,
        ).with_name("cylindrical_lower_shell")
        bottom.move_anchor_to("top_center", (0.0, 0.0, 0.0))

        return [shell, bottom]


class MultilevelKettleBody(ConceptTemplate):
    def __init__(
        self,
        first_level_bottom_radii,
        first_level_top_radii,
        first_level_heights,
        upper_levels,
        x_radius_scale,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                first_level_bottom_radii=first_level_bottom_radii,
                first_level_top_radii=first_level_top_radii,
                first_level_heights=first_level_heights,
                upper_levels=upper_levels,
                x_radius_scale=x_radius_scale,
            )
        )
        self.semantic = "Body"

    @classmethod
    def _build_components(
        cls,
        first_level_bottom_radii,
        first_level_top_radii,
        first_level_heights,
        upper_levels,
        x_radius_scale,
    ):
        bottom_outer_radius, bottom_inner_radius = first_level_bottom_radii
        top_outer_radius, top_inner_radius = first_level_top_radii
        total_height, open_height = first_level_heights
        lower_height = total_height - open_height
        split_outer_radius = cls._outer_radius_at_open_ring_bottom(
            bottom_outer_radius=bottom_outer_radius,
            top_outer_radius=top_outer_radius,
            total_height=total_height,
            open_height=open_height,
        )

        lower_shell = Cylinder(
            height=lower_height,
            top_radius=split_outer_radius * x_radius_scale,
            bottom_radius=bottom_outer_radius * x_radius_scale,
            top_radius_z=split_outer_radius,
            bottom_radius_z=bottom_outer_radius,
        ).with_name("level_1_lower_shell")
        lower_shell.move_anchor_to("bottom_center", (0.0, -total_height / 2.0, 0.0))

        first_open_ring = Ring(
            height=open_height,
            outer_top_radius=top_outer_radius,
            inner_top_radius=top_inner_radius,
            outer_bottom_radius=split_outer_radius,
            inner_bottom_radius=bottom_inner_radius,
            x_z_ratio=x_radius_scale,
        ).with_name("level_1_open_ring")
        first_open_ring.move_anchor_to(
            "axis_bottom_center",
            lower_shell.world_anchor("top_center"),
        )

        components = [lower_shell, first_open_ring]
        previous_outer_radius = top_outer_radius
        previous_inner_radius = top_inner_radius
        previous_top_anchor = first_open_ring.world_anchor("axis_top_center")

        for level_number, level in enumerate(upper_levels, start=2):
            level_outer_radius, level_inner_radius = level["top_radii"]
            level_height = level["height"]
            upper_ring = Ring(
                height=level_height,
                outer_top_radius=level_outer_radius,
                inner_top_radius=level_inner_radius,
                outer_bottom_radius=previous_outer_radius,
                inner_bottom_radius=previous_inner_radius,
                x_z_ratio=x_radius_scale,
            ).with_name(f"level_{level_number}_open_ring")
            upper_ring.move_anchor_to("axis_bottom_center", previous_top_anchor)
            components.append(upper_ring)
            previous_outer_radius = level_outer_radius
            previous_inner_radius = level_inner_radius
            previous_top_anchor = upper_ring.world_anchor("axis_top_center")

        return components

    @staticmethod
    def _outer_radius_at_open_ring_bottom(
        bottom_outer_radius,
        top_outer_radius,
        total_height,
        open_height,
    ):
        return top_outer_radius * (1.0 - open_height / total_height) + (
            bottom_outer_radius * open_height / total_height
        )


class StandardKettleCover(ConceptTemplate):
    def __init__(
        self,
        cover_profile,
        inner_opening,
        knob_sections,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                cover_profile=cover_profile,
                inner_opening=inner_opening,
                knob_sections=knob_sections,
            )
        )
        self.semantic = "Cover"

    @classmethod
    def _build_components(cls, cover_profile, inner_opening, knob_sections):
        outer_top_radius, outer_bottom_radius, total_height = cover_profile
        inner_top_radius, inner_bottom_radius, open_height = inner_opening
        cap_height = total_height - open_height
        split_outer_radius = cls._outer_radius_at_open_top(
            outer_top_radius=outer_top_radius,
            outer_bottom_radius=outer_bottom_radius,
            total_height=total_height,
            open_height=open_height,
        )

        lower_ring = Ring(
            height=open_height,
            outer_top_radius=split_outer_radius,
            inner_top_radius=inner_top_radius,
            outer_bottom_radius=outer_bottom_radius,
            inner_bottom_radius=inner_bottom_radius,
        ).with_name("lower_open_ring")
        lower_ring.move_anchor_to("axis_bottom_center", (0.0, 0.0, 0.0))

        upper_cap = Cylinder(
            height=cap_height,
            top_radius=outer_top_radius,
            bottom_radius=split_outer_radius,
        ).with_name("upper_closed_cap")
        upper_cap.move_anchor_to("bottom_center", lower_ring.world_anchor("axis_top_center"))

        components = [upper_cap, lower_ring]
        previous_top_anchor = upper_cap.world_anchor("top_center")
        for knob_number, knob in enumerate(knob_sections, start=1):
            knob_top_radius, knob_bottom_radius, knob_height = knob
            knob_part = Cylinder(
                height=knob_height,
                top_radius=knob_top_radius,
                bottom_radius=knob_bottom_radius,
            ).with_name(f"knob_section_{knob_number}")
            knob_part.move_anchor_to("bottom_center", previous_top_anchor)
            components.append(knob_part)
            previous_top_anchor = knob_part.world_anchor("top_center")

        return components

    @staticmethod
    def _outer_radius_at_open_top(
        outer_top_radius,
        outer_bottom_radius,
        total_height,
        open_height,
    ):
        return outer_bottom_radius * (1.0 - open_height / total_height) + (
            outer_top_radius * open_height / total_height
        )


class TrifoldKettleHandle(ConceptTemplate):
    def __init__(
        self,
        horizontal_thickness,
        horizontal_lengths,
        vertical_thickness,
        horizontal_rotation_degrees,
        horizontal_separation,
        mounting_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                horizontal_thickness=horizontal_thickness,
                horizontal_lengths=horizontal_lengths,
                vertical_thickness=vertical_thickness,
                horizontal_rotation_degrees=horizontal_rotation_degrees,
                horizontal_separation=horizontal_separation,
                mounting_offset=mounting_offset,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        horizontal_thickness,
        horizontal_lengths,
        vertical_thickness,
        horizontal_rotation_degrees,
        horizontal_separation,
        mounting_offset,
    ):
        horizontal_width, horizontal_depth = horizontal_thickness
        vertical_width, vertical_depth = vertical_thickness
        upper_length, lower_length = horizontal_lengths
        upper_rotation_degrees, lower_rotation_degrees = horizontal_rotation_degrees
        upper_rotation = upper_rotation_degrees * DEGREES_TO_RADIANS
        lower_rotation = lower_rotation_degrees * DEGREES_TO_RADIANS

        upper_mount = (0.0, horizontal_separation / 2.0, -mounting_offset)
        upper_bar = Cuboid(
            height=horizontal_depth,
            top_length=horizontal_width,
            top_width=upper_length,
            rotation=(-upper_rotation, 0.0, 0.0),
        ).with_name("upper_mounting_bar")
        upper_bar.move_anchor_to("front_center", upper_mount)

        lower_mount = (0.0, -horizontal_separation / 2.0, 0.0)
        lower_bar = Cuboid(
            height=horizontal_depth,
            top_length=horizontal_width,
            top_width=lower_length,
            rotation=(-lower_rotation, 0.0, 0.0),
        ).with_name("lower_mounting_bar")
        lower_bar.move_anchor_to("front_center", lower_mount)

        upper_back = upper_bar.world_anchor("back_center")
        lower_back = lower_bar.world_anchor("back_center")
        connector_span = np.linalg.norm(upper_back - lower_back)
        connector = Cuboid(
            height=connector_span + horizontal_depth,
            top_length=vertical_width,
            top_width=vertical_depth,
        ).with_name("rear_bridge_bar")
        connector.align_axis_between_points("y", lower_back, upper_back)
        connector.set_transform(
            position=np.asarray(connector.position, dtype=float)
            + np.array([0.0, 0.0, -vertical_depth / 2.0])
        )

        return [upper_bar, lower_bar, connector]


class CurvedKettleHandle(ConceptTemplate):
    def __init__(
        self,
        torus_profile,
        arc_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        central_radius, tube_radius = torus_profile
        arc_angle = arc_angle_degrees * DEGREES_TO_RADIANS
        self._finalize_mesh(
            [
                Torus(
                    central_radius=central_radius,
                    start_torus_radius=tube_radius,
                    exist_angle=arc_angle,
                    rotation=(pi, 0.0, -pi / 2.0),
                ).with_name("curved_torus_handle")
            ]
        )
        self.semantic = "Handle"


class RingKettleHandle(ConceptTemplate):
    def __init__(
        self,
        ring_size,
        arc_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        outer_radius, inner_radius, height = ring_size
        arc_angle = arc_angle_degrees * DEGREES_TO_RADIANS
        self._finalize_mesh(
            [
                Ring(
                    height=height,
                    outer_top_radius=outer_radius,
                    inner_top_radius=inner_radius,
                    exist_angle=arc_angle,
                    rotation=(pi, 0.0, -pi / 2.0),
                ).with_name("curved_ring_handle")
            ]
        )
        self.semantic = "Handle"


class CylindricalKettleHandle(ConceptTemplate):
    def __init__(self, handle_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        top_radius, bottom_radius, length = handle_size
        handle = Cylinder(
            height=length,
            top_radius=top_radius,
            bottom_radius=bottom_radius,
            rotation=(-pi / 2.0, 0.0, 0.0),
        ).with_name("straight_cylindrical_handle")
        handle.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        self._finalize_mesh([handle])
        self.semantic = "Handle"


class RoundUKettleHandle(ConceptTemplate):
    def __init__(
        self,
        tube_radius,
        vertical_separation,
        vertical_length,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                tube_radius=tube_radius,
                vertical_separation=vertical_separation,
                vertical_length=vertical_length,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(tube_radius, vertical_separation, vertical_length):
        left_post = Cylinder(height=vertical_length, top_radius=tube_radius).with_name(
            "left_vertical_post"
        )
        left_post.move_anchor_to(
            "bottom_center",
            (0.0, 0.0, vertical_separation / 2.0),
        )

        right_post = Cylinder(height=vertical_length, top_radius=tube_radius).with_name(
            "right_vertical_post"
        )
        right_post.move_anchor_to(
            "bottom_center",
            (0.0, 0.0, -vertical_separation / 2.0),
        )

        top_arc = Torus(
            central_radius=vertical_separation / 2.0,
            start_torus_radius=tube_radius,
            exist_angle=pi,
            position=(0.0, vertical_length, 0.0),
            rotation=(-pi / 2.0, pi / 2.0, 0.0),
        ).with_name("top_round_arc")

        return [left_post, right_post, top_arc]


class FlatUKettleHandle(ConceptTemplate):
    def __init__(
        self,
        vertical_size,
        vertical_separation,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                vertical_size=vertical_size,
                vertical_separation=vertical_separation,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(vertical_size, vertical_separation):
        post_width, post_height, post_depth = vertical_size
        left_post = Cuboid(
            height=post_height,
            top_length=post_width,
            top_width=post_depth,
        ).with_name("left_flat_post")
        left_post.move_anchor_to(
            "bottom_center",
            (0.0, 0.0, vertical_separation / 2.0),
        )

        right_post = Cuboid(
            height=post_height,
            top_length=post_width,
            top_width=post_depth,
        ).with_name("right_flat_post")
        right_post.move_anchor_to(
            "bottom_center",
            (0.0, 0.0, -vertical_separation / 2.0),
        )

        outer_radius = (vertical_separation + post_depth) / 2.0
        inner_radius = (vertical_separation - post_depth) / 2.0
        top_arc = Ring(
            height=post_width,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=pi,
            position=(0.0, post_height, 0.0),
            rotation=(-pi / 2.0, pi / 2.0, 0.0),
        ).with_name("top_flat_arc")

        return [left_post, right_post, top_arc]


class StraightKettleSpout(ConceptTemplate):
    def __init__(
        self,
        spout_sections,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(spout_sections=spout_sections))
        self.semantic = "Spout"

    @staticmethod
    def _build_components(spout_sections):
        components = []
        cursor_y = 0.0
        cursor_z = 0.0

        if spout_sections:
            first_section = spout_sections[0]
            first_front_length, first_back_length = first_section["lengths"]
            first_rotation = first_section["rotation_degrees"] * DEGREES_TO_RADIANS
            first_average_length = (first_front_length + first_back_length) / 2.0
            cursor_y -= first_average_length * sin(first_rotation) / 2.0
            cursor_z -= first_average_length * cos(first_rotation) / 2.0

        for section_number, section in enumerate(spout_sections, start=1):
            front_length, back_length = section["lengths"]
            outer_top_radius, outer_bottom_radius = section["outer_radii"]
            wall_thickness = section["wall_thickness"]
            rotation_angle = section["rotation_degrees"] * DEGREES_TO_RADIANS
            average_length = (front_length + back_length) / 2.0

            cursor_y += average_length * sin(rotation_angle) / 2.0
            cursor_z += average_length * cos(rotation_angle) / 2.0
            segment = Ring(
                height=front_length,
                outer_top_radius=outer_top_radius,
                inner_top_radius=outer_top_radius - wall_thickness * 2.0,
                outer_bottom_radius=outer_bottom_radius,
                inner_bottom_radius=outer_bottom_radius - wall_thickness * 2.0,
                back_height=back_length,
                generatrix_offset=section["generatrix_offset"],
                position=(0.0, cursor_y, cursor_z),
                rotation=(pi / 2.0 - rotation_angle, pi / 2.0, 0.0),
                rotation_order="YXZ",
            ).with_name(f"spout_segment_{section_number}")
            components.append(segment)
            cursor_y += average_length * sin(rotation_angle) / 2.0
            cursor_z += average_length * cos(rotation_angle) / 2.0

        return components


class CurvedKettleSpout(ConceptTemplate):
    def __init__(
        self,
        central_radii,
        arc_angles_degrees,
        tube_radii,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                central_radii=central_radii,
                arc_angles_degrees=arc_angles_degrees,
                tube_radii=tube_radii,
            )
        )
        self.semantic = "Spout"

    @staticmethod
    def _build_components(central_radii, arc_angles_degrees, tube_radii):
        upper_central_radius, lower_central_radius = central_radii
        upper_angle_degrees, lower_angle_degrees = arc_angles_degrees
        start_tube_radius, joint_tube_radius, end_tube_radius = tube_radii
        upper_angle = upper_angle_degrees * DEGREES_TO_RADIANS
        lower_angle = lower_angle_degrees * DEGREES_TO_RADIANS

        upper_arc = Torus(
            central_radius=upper_central_radius,
            start_torus_radius=start_tube_radius,
            exist_angle=upper_angle,
            end_torus_radius=joint_tube_radius,
            position=(0.0, upper_central_radius, 0.0),
            rotation=(0.0, 0.0, -pi / 2.0),
        ).with_name("upper_spout_arc")

        lower_arc = Torus(
            central_radius=lower_central_radius,
            start_torus_radius=joint_tube_radius,
            exist_angle=lower_angle,
            end_torus_radius=end_tube_radius,
            rotation=(-upper_angle, 0.0, pi / 2.0),
            rotation_order="ZXY",
        ).with_name("lower_spout_arc")
        lower_arc.move_anchor_to("start_center", upper_arc.world_anchor("end_center"))

        return [upper_arc, lower_arc]
