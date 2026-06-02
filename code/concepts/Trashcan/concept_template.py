from math import pi

from code.geometry import (
    ConceptTemplate,
    Cuboid,
    Cylinder,
    Rectangular_Ring,
    Ring,
    radial_array_frames,
)


DEGREES_TO_RADIANS = pi / 180.0


class CylindricalTrashcanBody(ConceptTemplate):
    def __init__(
        self,
        outer_profile,
        inner_profile,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_profile=outer_profile,
                inner_profile=inner_profile,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _transition_radius(outer_top_radius, outer_bottom_radius, total_height, hollow_height):
        hollow_fraction = hollow_height / total_height
        return outer_top_radius * (1.0 - hollow_fraction) + outer_bottom_radius * hollow_fraction

    @classmethod
    def _build_components(cls, outer_profile, inner_profile):
        outer_top_radius, outer_bottom_radius, total_height = outer_profile
        inner_top_radius, inner_bottom_radius, hollow_height = inner_profile
        bottom_height = total_height - hollow_height
        transition_radius = cls._transition_radius(
            outer_top_radius=outer_top_radius,
            outer_bottom_radius=outer_bottom_radius,
            total_height=total_height,
            hollow_height=hollow_height,
        )

        bottom = Cylinder(
            height=bottom_height,
            top_radius=transition_radius,
            bottom_radius=outer_bottom_radius,
        ).with_name("bottom_solid_transition")
        bottom.move_anchor_to("bottom_center", (0.0, -total_height / 2.0, 0.0))

        wall = Ring(
            height=hollow_height,
            outer_top_radius=outer_top_radius,
            inner_top_radius=inner_top_radius,
            outer_bottom_radius=transition_radius,
            inner_bottom_radius=inner_bottom_radius,
        ).with_name("upper_hollow_wall")
        wall.move_anchor_to("axis_bottom_center", bottom.world_anchor("top_center"))

        return [bottom, wall]


class PrismaticTrashcanBody(ConceptTemplate):
    def __init__(
        self,
        top_size,
        bottom_size,
        shell_heights,
        top_offset,
        wall_thickness,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                top_size=top_size,
                bottom_size=bottom_size,
                shell_heights=shell_heights,
                top_offset=top_offset,
                wall_thickness=wall_thickness,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(top_size, bottom_size, shell_heights, top_offset, wall_thickness):
        top_length, top_width = top_size
        bottom_length, bottom_width = bottom_size
        front_height, back_height = shell_heights
        top_offset_x, top_offset_z = top_offset
        wall_thickness_x, wall_thickness_z, bottom_plate_height = wall_thickness

        inner_top_length = top_length - wall_thickness_x * 2.0
        inner_top_width = top_width - wall_thickness_z * 2.0
        inner_bottom_length = bottom_length - wall_thickness_x * 2.0
        inner_bottom_width = bottom_width - wall_thickness_z * 2.0

        wall = Rectangular_Ring(
            front_height=front_height,
            outer_top_length=top_length,
            outer_top_width=top_width,
            inner_top_length=inner_top_length,
            inner_top_width=inner_top_width,
            outer_bottom_length=bottom_length,
            outer_bottom_width=bottom_width,
            inner_bottom_length=inner_bottom_length,
            inner_bottom_width=inner_bottom_width,
            back_height=back_height,
            top_bottom_offset=(top_offset_x, top_offset_z),
        ).with_name("tapered_box_wall")
        wall.move_anchor_to("outer_bottom_center", (0.0, -back_height / 2.0, 0.0))

        interpolation_fraction = bottom_plate_height / front_height
        plate_top_length = (
            inner_top_length * interpolation_fraction
            + inner_bottom_length * (1.0 - interpolation_fraction)
        )
        plate_top_width = (
            inner_top_width * interpolation_fraction
            + inner_bottom_width * (1.0 - interpolation_fraction)
        )
        plate_top_offset_x = top_offset_x * interpolation_fraction
        plate_top_offset_z = top_offset_z * interpolation_fraction

        bottom_plate = Cuboid(
            height=bottom_plate_height,
            top_length=plate_top_length,
            top_width=plate_top_width,
            bottom_length=inner_bottom_length,
            bottom_width=inner_bottom_width,
            top_offset=(plate_top_offset_x, plate_top_offset_z),
        ).with_name("bottom_plate")
        bottom_plate.move_anchor_to("bottom_center", wall.world_anchor("outer_bottom_center"))

        return [wall, bottom_plate]


class SeparatedCylindricalTrashcanBody(ConceptTemplate):
    def __init__(
        self,
        outer_profile,
        inner_profile,
        partition_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_profile=outer_profile,
                inner_profile=inner_profile,
                partition_size=partition_size,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _transition_radius(outer_top_radius, outer_bottom_radius, total_height, hollow_height):
        hollow_fraction = hollow_height / total_height
        return outer_top_radius * (1.0 - hollow_fraction) + outer_bottom_radius * hollow_fraction

    @classmethod
    def _build_components(cls, outer_profile, inner_profile, partition_size):
        outer_top_radius, outer_bottom_radius, total_height = outer_profile
        inner_top_radius, inner_bottom_radius, hollow_height = inner_profile
        partition_length, partition_height, partition_width = partition_size
        bottom_height = total_height - hollow_height
        transition_radius = cls._transition_radius(
            outer_top_radius=outer_top_radius,
            outer_bottom_radius=outer_bottom_radius,
            total_height=total_height,
            hollow_height=hollow_height,
        )

        bottom = Cylinder(
            height=bottom_height,
            top_radius=transition_radius,
            bottom_radius=outer_bottom_radius,
        ).with_name("bottom_solid_transition")
        bottom.move_anchor_to("bottom_center", (0.0, -total_height / 2.0, 0.0))

        wall = Ring(
            height=hollow_height,
            outer_top_radius=outer_top_radius,
            inner_top_radius=inner_top_radius,
            outer_bottom_radius=transition_radius,
            inner_bottom_radius=inner_bottom_radius,
        ).with_name("upper_hollow_wall")
        wall.move_anchor_to("axis_bottom_center", bottom.world_anchor("top_center"))

        partition = Cuboid(
            height=partition_height,
            top_length=partition_length,
            top_width=partition_width,
        ).with_name("internal_partition")
        partition.move_anchor_to("bottom_center", bottom.world_anchor("top_center"))

        return [bottom, wall, partition]


class CylindricalTrashcanCover(ConceptTemplate):
    def __init__(self, cover_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        radius, height = cover_size
        self._finalize_mesh(
            [Cylinder(height=height, top_radius=radius).with_name("cylindrical_cover")]
        )
        self.semantic = "Cover"


class CuboidalTrashcanCover(ConceptTemplate):
    def __init__(
        self,
        top_size,
        bottom_size,
        cover_heights,
        top_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                top_size=top_size,
                bottom_size=bottom_size,
                cover_heights=cover_heights,
                top_offset=top_offset,
            )
        )
        self.semantic = "Cover"

    @staticmethod
    def _build_components(top_size, bottom_size, cover_heights, top_offset):
        top_length, top_width = top_size
        bottom_length, bottom_width = bottom_size
        front_height, back_height = cover_heights
        top_offset_x, top_offset_z = top_offset

        cover = Cuboid(
            height=front_height,
            top_length=top_length,
            top_width=top_width,
            bottom_length=bottom_length,
            bottom_width=bottom_width,
            top_offset=(top_offset_x, top_offset_z),
            back_height=back_height,
        ).with_name("tapered_cover")
        cover.move_anchor_to("bottom_center", (0.0, 0.0, bottom_width / 2.0))
        return [cover]


class DoubleLayerCuboidalTrashcanCover(ConceptTemplate):
    def __init__(
        self,
        top_size,
        bottom_size,
        top_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                top_size=top_size,
                bottom_size=bottom_size,
                top_offset=top_offset,
            )
        )
        self.semantic = "Cover"

    @staticmethod
    def _build_components(top_size, bottom_size, top_offset):
        top_length, top_height, top_width = top_size
        bottom_length, bottom_height, bottom_width = bottom_size
        top_offset_x, top_offset_z = top_offset

        bottom_layer = Cuboid(
            height=bottom_height,
            top_length=bottom_length,
            top_width=bottom_width,
        ).with_name("bottom_cover_layer")
        bottom_layer.move_anchor_to("bottom_center", (0.0, 0.0, bottom_width / 2.0))

        top_layer = Cuboid(
            height=top_height,
            top_length=top_length,
            top_width=top_width,
        ).with_name("top_cover_layer")
        top_layer.move_anchor_to(
            "bottom_center",
            (top_offset_x, bottom_height, bottom_width / 2.0 + top_offset_z),
        )

        return [bottom_layer, top_layer]


class CylindricalHollowTrashcanCover(ConceptTemplate):
    def __init__(self, cover_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        outer_radius, inner_radius, height = cover_size
        cover = Ring(
            height=height,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
        ).with_name("hollow_cylindrical_cover")
        cover.move_anchor_to("axis_bottom_center", (0.0, 0.0, 0.0))
        self._finalize_mesh([cover])
        self.semantic = "Cover"


class CuboidalHollowTrashcanCover(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        inner_size,
        inner_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        outer_length, outer_height, outer_width = outer_size
        inner_length, inner_width = inner_size
        inner_offset_x, inner_offset_z = inner_offset
        cover = Rectangular_Ring(
            front_height=outer_height,
            outer_top_length=outer_length,
            outer_top_width=outer_width,
            inner_top_length=inner_length,
            inner_top_width=inner_width,
            inner_offset=(inner_offset_x, inner_offset_z),
        ).with_name("hollow_cuboidal_cover")
        cover.move_anchor_to("outer_bottom_center", (0.0, 0.0, 0.0))
        self._finalize_mesh([cover])
        self.semantic = "Cover"


class HoledCylindricalTrashcanCover(ConceptTemplate):
    def __init__(
        self,
        radii,
        heights,
        arc_angle_degrees,
        side_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                radii=radii,
                heights=heights,
                arc_angle_degrees=arc_angle_degrees,
                side_count=side_count,
            )
        )
        self.semantic = "Cover"

    @staticmethod
    def _build_components(radii, heights, arc_angle_degrees, side_count):
        outer_radius, inner_radius = radii
        total_height, middle_ring_height, lower_arc_height = heights
        arc_angle = arc_angle_degrees * DEGREES_TO_RADIANS
        components = []

        for frame in radial_array_frames(
            count=int(side_count),
            center_point=(0.0, lower_arc_height / 2.0, 0.0),
            radial_axis="y",
        ):
            arc = Ring(
                height=lower_arc_height,
                outer_top_radius=outer_radius,
                inner_top_radius=inner_radius,
                exist_angle=arc_angle,
                position=frame.position,
                rotation=(0.0, frame.angle, 0.0),
            ).with_name(f"lower_arc_{frame.index + 1}")
            components.append(arc)

        middle_ring = Ring(
            height=middle_ring_height,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
        ).with_name("middle_ring")
        middle_ring.move_anchor_to("axis_bottom_center", (0.0, lower_arc_height, 0.0))
        components.append(middle_ring)

        top_disc_height = total_height - middle_ring_height
        top_disc = Cylinder(height=top_disc_height, top_radius=outer_radius).with_name("top_disc")
        top_disc.move_anchor_to(
            "bottom_center",
            (0.0, lower_arc_height + middle_ring_height, 0.0),
        )
        components.append(top_disc)

        return components


class HoledCuboidalTrashcanCover(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        inner_size,
        front_back_hole_size,
        left_right_hole_size,
        side_holes,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                inner_size=inner_size,
                front_back_hole_size=front_back_hole_size,
                left_right_hole_size=left_right_hole_size,
                side_holes=side_holes,
            )
        )
        self.semantic = "Cover"

    @staticmethod
    def _build_components(
        outer_size,
        inner_size,
        front_back_hole_size,
        left_right_hole_size,
        side_holes,
    ):
        outer_length, outer_height, outer_width = outer_size
        inner_length, inner_height, inner_width = inner_size
        front_back_hole_length, front_back_hole_height = front_back_hole_size
        left_right_hole_width, left_right_hole_height = left_right_hole_size
        front_has_hole = side_holes["front"]
        back_has_hole = side_holes["back"]
        left_has_hole = side_holes["left"]
        right_has_hole = side_holes["right"]
        front_back_wall_width = (outer_width - inner_width) / 2.0
        side_wall_length = (outer_length - inner_length) / 2.0
        components = []

        top_panel = Cuboid(
            height=outer_height - inner_height,
            top_length=outer_length,
            top_width=outer_width,
        ).with_name("top_panel")
        top_panel.move_anchor_to("bottom_center", (0.0, inner_height, 0.0))
        components.append(top_panel)

        front_z = (outer_width + inner_width) / 4.0
        back_z = -front_z
        HoledCuboidalTrashcanCover._append_front_back_side(
            components=components,
            name_prefix="front",
            has_hole=front_has_hole,
            wall_center_z=front_z,
            outer_length=outer_length,
            inner_height=inner_height,
            wall_width=front_back_wall_width,
            hole_length=front_back_hole_length,
            hole_height=front_back_hole_height,
        )
        HoledCuboidalTrashcanCover._append_front_back_side(
            components=components,
            name_prefix="back",
            has_hole=back_has_hole,
            wall_center_z=back_z,
            outer_length=outer_length,
            inner_height=inner_height,
            wall_width=front_back_wall_width,
            hole_length=front_back_hole_length,
            hole_height=front_back_hole_height,
        )

        left_x = -(outer_length + inner_length) / 4.0
        right_x = -left_x
        HoledCuboidalTrashcanCover._append_left_right_side(
            components=components,
            name_prefix="left",
            has_hole=left_has_hole,
            wall_center_x=left_x,
            side_wall_length=side_wall_length,
            inner_height=inner_height,
            inner_width=inner_width,
            hole_width=left_right_hole_width,
            hole_height=left_right_hole_height,
        )
        HoledCuboidalTrashcanCover._append_left_right_side(
            components=components,
            name_prefix="right",
            has_hole=right_has_hole,
            wall_center_x=right_x,
            side_wall_length=side_wall_length,
            inner_height=inner_height,
            inner_width=inner_width,
            hole_width=left_right_hole_width,
            hole_height=left_right_hole_height,
        )

        return components

    @staticmethod
    def _append_front_back_side(
        components,
        name_prefix,
        has_hole,
        wall_center_z,
        outer_length,
        inner_height,
        wall_width,
        hole_length,
        hole_height,
    ):
        if not has_hole:
            panel = Cuboid(
                height=inner_height,
                top_length=outer_length,
                top_width=wall_width,
            ).with_name(f"{name_prefix}_solid_panel")
            panel.move_anchor_to("bottom_center", (0.0, 0.0, wall_center_z))
            components.append(panel)
            return

        side_post_length = (outer_length - hole_length) / 2.0
        left_post_x = -(outer_length + hole_length) / 4.0
        right_post_x = -left_post_x
        for post_name, post_x in (
            ("left_post", left_post_x),
            ("right_post", right_post_x),
        ):
            post = Cuboid(
                height=inner_height,
                top_length=side_post_length,
                top_width=wall_width,
            ).with_name(f"{name_prefix}_{post_name}")
            post.move_anchor_to("bottom_center", (post_x, 0.0, wall_center_z))
            components.append(post)

        top_rail = Cuboid(
            height=inner_height - hole_height,
            top_length=hole_length,
            top_width=wall_width,
        ).with_name(f"{name_prefix}_top_rail")
        top_rail.move_anchor_to("bottom_center", (0.0, hole_height, wall_center_z))
        components.append(top_rail)

    @staticmethod
    def _append_left_right_side(
        components,
        name_prefix,
        has_hole,
        wall_center_x,
        side_wall_length,
        inner_height,
        inner_width,
        hole_width,
        hole_height,
    ):
        if not has_hole:
            panel = Cuboid(
                height=inner_height,
                top_length=side_wall_length,
                top_width=inner_width,
            ).with_name(f"{name_prefix}_solid_panel")
            panel.move_anchor_to("bottom_center", (wall_center_x, 0.0, 0.0))
            components.append(panel)
            return

        side_post_width = (inner_width - hole_width) / 2.0
        back_post_z = -(inner_width + hole_width) / 4.0
        front_post_z = -back_post_z
        for post_name, post_z in (
            ("back_post", back_post_z),
            ("front_post", front_post_z),
        ):
            post = Cuboid(
                height=inner_height,
                top_length=side_wall_length,
                top_width=side_post_width,
            ).with_name(f"{name_prefix}_{post_name}")
            post.move_anchor_to("bottom_center", (wall_center_x, 0.0, post_z))
            components.append(post)

        top_rail = Cuboid(
            height=inner_height - hole_height,
            top_length=side_wall_length,
            top_width=hole_width,
        ).with_name(f"{name_prefix}_top_rail")
        top_rail.move_anchor_to("bottom_center", (wall_center_x, hole_height, 0.0))
        components.append(top_rail)


class StandardTrashcanWheelSet(ConceptTemplate):
    def __init__(self, wheel_size, wheel_separation, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                wheel_size=wheel_size,
                wheel_separation=wheel_separation,
            )
        )
        self.semantic = "Wheel"

    @staticmethod
    def _build_components(wheel_size, wheel_separation):
        radius, thickness = wheel_size
        separation = wheel_separation
        components = []
        for name, center_x in (
            ("left_wheel", -separation),
            ("right_wheel", separation),
        ):
            components.append(
                Cylinder(
                    height=thickness,
                    top_radius=radius,
                    position=(center_x, 0.0, 0.0),
                    rotation=(0.0, 0.0, pi / 2.0),
                ).with_name(name)
            )
        return components


class CylindricalTrashcanShell(ConceptTemplate):
    def __init__(self, outer_profile, inner_profile, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        outer_top_radius, outer_bottom_radius, height = outer_profile
        inner_top_radius, inner_bottom_radius = inner_profile
        self._finalize_mesh(
            [
                Ring(
                    height=height,
                    outer_top_radius=outer_top_radius,
                    inner_top_radius=inner_top_radius,
                    outer_bottom_radius=outer_bottom_radius,
                    inner_bottom_radius=inner_bottom_radius,
                ).with_name("cylindrical_shell")
            ]
        )
        self.semantic = "Shell"


class CuboidalTrashcanShell(ConceptTemplate):
    def __init__(self, outer_size, inner_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        outer_length, outer_height, outer_width = outer_size
        inner_length, inner_width = inner_size
        self._finalize_mesh(
            [
                Rectangular_Ring(
                    front_height=outer_height,
                    outer_top_length=outer_length,
                    outer_top_width=outer_width,
                    inner_top_length=inner_length,
                    inner_top_width=inner_width,
                ).with_name("cuboidal_shell")
            ]
        )
        self.semantic = "Shell"
