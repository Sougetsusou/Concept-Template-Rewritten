from math import atan, pi, sqrt

from code.geometry_rewritten import (
    ConceptTemplate,
    Cuboid,
    Cylinder,
    Rectangular_Ring,
    Ring,
    Torus,
)


SQUARE_PROFILE_SCALE = sqrt(2.0)
DEGREES_TO_RADIANS = pi / 180.0


def _outer_radius_at_shell_bottom(
    top_outer_radius,
    bottom_outer_radius,
    total_height,
    open_shell_height,
):
    shell_fraction = open_shell_height / total_height
    return (
        top_outer_radius * (1.0 - shell_fraction)
        + bottom_outer_radius * shell_fraction
    )


class CylindricalBucketBody(ConceptTemplate):
    def __init__(
        self,
        top_outer_radius,
        bottom_outer_radius,
        total_height,
        top_inner_radius,
        bottom_inner_radius,
        open_shell_height,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                top_outer_radius=top_outer_radius,
                bottom_outer_radius=bottom_outer_radius,
                total_height=total_height,
                top_inner_radius=top_inner_radius,
                bottom_inner_radius=bottom_inner_radius,
                open_shell_height=open_shell_height,
            )
        )

    @staticmethod
    def _build_components(
        top_outer_radius,
        bottom_outer_radius,
        total_height,
        top_inner_radius,
        bottom_inner_radius,
        open_shell_height,
    ):
        bottom_height = total_height - open_shell_height
        middle_outer_radius = _outer_radius_at_shell_bottom(
            top_outer_radius=top_outer_radius,
            bottom_outer_radius=bottom_outer_radius,
            total_height=total_height,
            open_shell_height=open_shell_height,
        )

        bottom_section = Cylinder(
            height=bottom_height,
            top_radius=middle_outer_radius,
            bottom_radius=bottom_outer_radius,
        ).with_name("bottom_solid_section")
        bottom_section.move_anchor_to("bottom_center", (0, -total_height / 2.0, 0))

        upper_shell = Ring(
            height=open_shell_height,
            outer_top_radius=top_outer_radius,
            inner_top_radius=top_inner_radius,
            outer_bottom_radius=middle_outer_radius,
            inner_bottom_radius=bottom_inner_radius,
        ).with_name("upper_open_shell")
        upper_shell.move_anchor_to(
            "axis_bottom_center", bottom_section.world_anchor("top_center")
        )

        return [bottom_section, upper_shell]


class PrismaticBucketBody(ConceptTemplate):
    def __init__(
        self,
        top_outer_radius,
        bottom_outer_radius,
        total_height,
        top_inner_radius,
        bottom_inner_radius,
        open_shell_height,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                top_outer_radius=top_outer_radius,
                bottom_outer_radius=bottom_outer_radius,
                total_height=total_height,
                top_inner_radius=top_inner_radius,
                bottom_inner_radius=bottom_inner_radius,
                open_shell_height=open_shell_height,
            )
        )

    @staticmethod
    def _square_profile_width(radius):
        return radius * SQUARE_PROFILE_SCALE

    @classmethod
    def _build_components(
        cls,
        top_outer_radius,
        bottom_outer_radius,
        total_height,
        top_inner_radius,
        bottom_inner_radius,
        open_shell_height,
    ):
        bottom_height = total_height - open_shell_height
        middle_outer_radius = _outer_radius_at_shell_bottom(
            top_outer_radius=top_outer_radius,
            bottom_outer_radius=bottom_outer_radius,
            total_height=total_height,
            open_shell_height=open_shell_height,
        )

        top_outer_width = cls._square_profile_width(top_outer_radius)
        bottom_outer_width = cls._square_profile_width(bottom_outer_radius)
        middle_outer_width = cls._square_profile_width(middle_outer_radius)
        top_inner_width = cls._square_profile_width(top_inner_radius)
        bottom_inner_width = cls._square_profile_width(bottom_inner_radius)

        bottom_section = Cuboid(
            height=bottom_height,
            top_length=middle_outer_width,
            top_width=middle_outer_width,
            bottom_length=bottom_outer_width,
            bottom_width=bottom_outer_width,
        ).with_name("bottom_solid_section")
        bottom_section.move_anchor_to("bottom_center", (0, -total_height / 2.0, 0))

        upper_shell = Rectangular_Ring(
            front_height=open_shell_height,
            outer_top_length=top_outer_width,
            outer_top_width=top_outer_width,
            inner_top_length=top_inner_width,
            inner_top_width=top_inner_width,
            outer_bottom_length=middle_outer_width,
            outer_bottom_width=middle_outer_width,
            inner_bottom_length=bottom_inner_width,
            inner_bottom_width=bottom_inner_width,
        ).with_name("upper_open_shell")
        upper_shell.move_anchor_to(
            "outer_bottom_center", bottom_section.world_anchor("top_center")
        )

        return [bottom_section, upper_shell]


class TrifoldBucketHandle(ConceptTemplate):
    def __init__(
        self,
        vertical_cross_section,
        arm_lengths,
        bridge_cross_section,
        arm_rotations_degrees,
        arm_separation,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                vertical_cross_section=vertical_cross_section,
                arm_lengths=arm_lengths,
                bridge_cross_section=bridge_cross_section,
                arm_rotations_degrees=arm_rotations_degrees,
                arm_separation=arm_separation,
            )
        )

    @staticmethod
    def _build_components(
        vertical_cross_section,
        arm_lengths,
        bridge_cross_section,
        arm_rotations_degrees,
        arm_separation,
    ):
        vertical_thickness_x, vertical_thickness_z = vertical_cross_section
        positive_arm_length, negative_arm_length = arm_lengths
        bridge_height, bridge_width = bridge_cross_section
        positive_arm_rotation_degrees, negative_arm_rotation_degrees = (
            arm_rotations_degrees
        )
        positive_arm_rotation = positive_arm_rotation_degrees * DEGREES_TO_RADIANS
        negative_arm_rotation = negative_arm_rotation_degrees * DEGREES_TO_RADIANS

        positive_arm = Cuboid(
            height=positive_arm_length,
            top_length=vertical_thickness_x,
            top_width=vertical_thickness_z,
            rotation=(0, 0, positive_arm_rotation),
        ).with_name("positive_x_vertical_arm")
        positive_arm.move_anchor_to("bottom_center", (arm_separation / 2.0, 0, 0))

        negative_arm = Cuboid(
            height=negative_arm_length,
            top_length=vertical_thickness_x,
            top_width=vertical_thickness_z,
            rotation=(0, 0, negative_arm_rotation),
        ).with_name("negative_x_vertical_arm")
        negative_arm.move_anchor_to("bottom_center", (-arm_separation / 2.0, 0, 0))

        positive_top = positive_arm.world_anchor("top_center")
        negative_top = negative_arm.world_anchor("top_center")
        delta_x, delta_y, _ = positive_top - negative_top
        midpoint_x, midpoint_y, _ = (positive_top + negative_top) / 2.0

        bridge_length = sqrt(delta_x * delta_x + delta_y * delta_y) + vertical_thickness_x
        bridge_rotation = atan(delta_y / delta_x)
        bridge = Cuboid(
            height=bridge_height,
            top_length=bridge_length,
            top_width=bridge_width,
            rotation=(0, 0, bridge_rotation),
        ).with_name("top_bridge")
        bridge.set_transform(position=(midpoint_x, midpoint_y + bridge_height / 2.0, 0))

        return [positive_arm, negative_arm, bridge]


class CurvedBucketHandle(ConceptTemplate):
    def __init__(
        self,
        center_radius,
        tube_radius,
        arc_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            [
                Torus(
                    central_radius=center_radius,
                    start_torus_radius=tube_radius,
                    exist_angle=arc_angle_degrees * DEGREES_TO_RADIANS,
                    rotation=(-pi / 2.0, 0, 0),
                ).with_name("arc_tube")
            ]
        )


class RoundUBucketHandle(ConceptTemplate):
    def __init__(
        self,
        tube_radius,
        leg_separation,
        leg_length,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                tube_radius=tube_radius,
                leg_separation=leg_separation,
                leg_length=leg_length,
            )
        )

    @staticmethod
    def _build_components(tube_radius, leg_separation, leg_length):
        positive_leg = Cylinder(
            height=leg_length,
            top_radius=tube_radius,
        ).with_name("positive_x_vertical_leg")
        positive_leg.move_anchor_to("bottom_center", (leg_separation / 2.0, 0, 0))

        negative_leg = Cylinder(
            height=leg_length,
            top_radius=tube_radius,
        ).with_name("negative_x_vertical_leg")
        negative_leg.move_anchor_to("bottom_center", (-leg_separation / 2.0, 0, 0))

        top_arc = Torus(
            central_radius=leg_separation / 2.0,
            start_torus_radius=tube_radius,
            exist_angle=pi,
            rotation=(-pi / 2.0, 0, 0),
        ).with_name("top_arc")
        top_arc.move_anchor_to("start_center", positive_leg.world_anchor("top_center"))

        return [positive_leg, negative_leg, top_arc]


class FlatUBucketHandle(ConceptTemplate):
    def __init__(
        self,
        vertical_size,
        leg_separation,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                vertical_size=vertical_size,
                leg_separation=leg_separation,
            )
        )

    @staticmethod
    def _build_components(vertical_size, leg_separation):
        leg_thickness_x, leg_height, leg_thickness_z = vertical_size

        positive_leg = Cuboid(
            height=leg_height,
            top_length=leg_thickness_x,
            top_width=leg_thickness_z,
        ).with_name("positive_x_vertical_leg")
        positive_leg.move_anchor_to("bottom_center", (leg_separation / 2.0, 0, 0))

        negative_leg = Cuboid(
            height=leg_height,
            top_length=leg_thickness_x,
            top_width=leg_thickness_z,
        ).with_name("negative_x_vertical_leg")
        negative_leg.move_anchor_to("bottom_center", (-leg_separation / 2.0, 0, 0))

        outer_radius = (leg_separation + leg_thickness_x) / 2.0
        inner_radius = (leg_separation - leg_thickness_x) / 2.0
        top_arc = Ring(
            height=leg_thickness_z,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=pi,
            rotation=(-pi / 2.0, 0, 0),
        ).with_name("top_flat_arc")
        top_arc.move_anchor_to("arc_origin", (0, leg_height, 0))

        return [positive_leg, negative_leg, top_arc]


class SingleBucketCylinder(ConceptTemplate):
    def __init__(
        self,
        radius,
        height,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            [
                Cylinder(
                    height=height,
                    top_radius=radius,
                ).with_name("cylinder")
            ]
        )
