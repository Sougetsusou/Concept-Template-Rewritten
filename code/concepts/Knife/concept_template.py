from math import pi

from code.geometry import ConceptTemplate, Cuboid, Cylinder, Ring


DEGREES_TO_RADIANS = pi / 180.0


class CuboidalKnifeHandle(ConceptTemplate):
    def __init__(self, handle_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        length, height, depth = handle_size
        self._finalize_mesh(
            [
                Cuboid(
                    height=height,
                    top_length=length,
                    top_width=depth,
                ).with_name("cuboidal_handle_body")
            ]
        )
        self.semantic = "Handle"


class TShapedKnifeHandle(ConceptTemplate):
    def __init__(
        self,
        main_size,
        bottom_size,
        bottom_planar_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                main_size=main_size,
                bottom_size=bottom_size,
                bottom_planar_offset=bottom_planar_offset,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(main_size, bottom_size, bottom_planar_offset):
        main_length, main_height, main_depth = main_size
        bottom_length, bottom_height, bottom_depth = bottom_size
        bottom_offset_x, bottom_offset_z = bottom_planar_offset

        main = Cuboid(
            height=main_height,
            top_length=main_length,
            top_width=main_depth,
        ).with_name("main_t_handle_block")

        bottom = Cuboid(
            height=bottom_height,
            top_length=bottom_length,
            top_width=bottom_depth,
        ).with_name("lower_t_handle_block")
        main_bottom_x, main_bottom_y, main_bottom_z = main.world_anchor("bottom_center")
        bottom.move_anchor_to(
            "top_center",
            (
                main_bottom_x + bottom_offset_x,
                main_bottom_y,
                main_bottom_z + bottom_offset_z,
            ),
        )

        return [main, bottom]


class CylindricalKnifeHandle(ConceptTemplate):
    def __init__(self, handle_profile, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        top_radius, bottom_radius, height = handle_profile
        self._finalize_mesh(
            [
                Cylinder(
                    height=height,
                    top_radius=top_radius,
                    bottom_radius=bottom_radius,
                ).with_name("cylindrical_handle_body")
            ]
        )
        self.semantic = "Handle"


class CurvedKnifeHandle(ConceptTemplate):
    def __init__(
        self,
        radius_profile,
        tube_height,
        arc_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        outer_radius, inner_radius = radius_profile
        arc_angle = arc_angle_degrees * DEGREES_TO_RADIANS
        centerline_radius = (outer_radius + inner_radius) / 2.0
        arc_frame_position = (0.0, 0.0, centerline_radius)
        arc_frame_rotation = (pi / 2.0, pi / 2.0, 0.0)
        ring = Ring(
            height=tube_height,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=arc_angle,
            position=arc_frame_position,
            rotation=arc_frame_rotation,
        ).with_name("curved_ring_handle")
        self._finalize_mesh([ring])
        self.semantic = "Handle"


class MultideckKnifeHandle(ConceptTemplate):
    def __init__(
        self,
        bottom_size,
        side_size,
        side_separation,
        side_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                bottom_size=bottom_size,
                side_size=side_size,
                side_separation=side_separation,
                side_offset=side_offset,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(bottom_size, side_size, side_separation, side_offset):
        bottom_length, bottom_height, bottom_depth = bottom_size
        side_length, side_height, side_depth = side_size
        side_offset_x, side_offset_z = side_offset

        base = Cuboid(
            height=bottom_height,
            top_length=bottom_length,
            top_width=bottom_depth,
        ).with_name("lower_deck")
        base.move_anchor_to(
            "top_center",
            (0.0, bottom_height / 2.0 - side_height / 2.0, 0.0),
        )
        _, base_top_y, _ = base.world_anchor("top_center")

        components = [base]
        for side_name, side_sign in (("left_upper_deck", 1.0), ("right_upper_deck", -1.0)):
            side = Cuboid(
                height=side_height,
                top_length=side_length,
                top_width=side_depth,
            ).with_name(side_name)
            side.move_anchor_to(
                "bottom_center",
                (
                    side_sign * side_separation / 2.0 + side_offset_x,
                    base_top_y,
                    side_offset_z,
                ),
            )
            components.append(side)

        return components


class EnvelopingKnifeHandle(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        frame_thickness,
        front_gap_width,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                frame_thickness=frame_thickness,
                front_gap_width=front_gap_width,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(outer_size, frame_thickness, front_gap_width):
        outer_length, outer_height, outer_depth = outer_size
        bottom_thickness, rear_thickness, side_thickness = frame_thickness
        vertical_height = outer_height - bottom_thickness
        side_bar_length = outer_length - rear_thickness
        split_bar_depth = (outer_depth - front_gap_width) / 2.0 - side_thickness

        bottom = Cuboid(
            height=bottom_thickness,
            top_length=outer_length,
            top_width=outer_depth,
        ).with_name("bottom_full_bar")
        bottom.move_anchor_to("bottom_center", (0.0, -outer_height / 2.0, 0.0))
        _, bottom_top_y, _ = bottom.world_anchor("top_center")

        rear_bar = Cuboid(
            height=vertical_height,
            top_length=rear_thickness,
            top_width=outer_depth,
        ).with_name("x_negative_rear_bar")
        rear_bar.move_anchor_to(
            "bottom_left_center",
            (-outer_length / 2.0, bottom_top_y, 0.0),
        )

        front_side_bar = Cuboid(
            height=vertical_height,
            top_length=side_bar_length,
            top_width=side_thickness,
        ).with_name("z_positive_side_bar")
        front_side_bar.move_anchor_to(
            "bottom_front_left",
            (-outer_length / 2.0 + rear_thickness, bottom_top_y, outer_depth / 2.0),
        )

        back_side_bar = Cuboid(
            height=vertical_height,
            top_length=side_bar_length,
            top_width=side_thickness,
        ).with_name("z_negative_side_bar")
        back_side_bar.move_anchor_to(
            "bottom_back_left",
            (-outer_length / 2.0 + rear_thickness, bottom_top_y, -outer_depth / 2.0),
        )

        positive_gap_bar = Cuboid(
            height=vertical_height,
            top_length=side_thickness,
            top_width=split_bar_depth,
        ).with_name("z_positive_gap_bar")
        positive_gap_bar.move_anchor_to(
            "bottom_back_right",
            (outer_length / 2.0, bottom_top_y, front_gap_width / 2.0),
        )

        negative_gap_bar = Cuboid(
            height=vertical_height,
            top_length=side_thickness,
            top_width=split_bar_depth,
        ).with_name("z_negative_gap_bar")
        negative_gap_bar.move_anchor_to(
            "bottom_front_right",
            (outer_length / 2.0, bottom_top_y, -front_gap_width / 2.0),
        )

        return [
            bottom,
            rear_bar,
            front_side_bar,
            back_side_bar,
            positive_gap_bar,
            negative_gap_bar,
        ]


class CuboidalKnifeBlade(ConceptTemplate):
    def __init__(self, blade_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        length, height, depth = blade_size
        blade = Cuboid(
            height=height,
            top_length=length,
            top_width=depth,
        ).with_name("base_aligned_cuboidal_blade")
        blade.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        self._finalize_mesh([blade])
        self.semantic = "Blade"


class CuspKnifeBlade(ConceptTemplate):
    def __init__(
        self,
        root_profile,
        root_top_z_offset,
        tip_length,
        tip_top_z_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                root_profile=root_profile,
                root_top_z_offset=root_top_z_offset,
                tip_length=tip_length,
                tip_top_z_offset=tip_top_z_offset,
            )
        )
        self.semantic = "Blade"

    @staticmethod
    def _build_components(root_profile, root_top_z_offset, tip_length, tip_top_z_offset):
        root_length, root_height, root_bottom_depth, root_top_depth = root_profile

        root = Cuboid(
            height=root_height,
            top_length=root_length,
            top_width=root_top_depth,
            bottom_length=root_length,
            bottom_width=root_bottom_depth,
            top_offset=(0.0, root_top_z_offset),
        ).with_name("tapered_blade_root")
        root.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        tip = Cuboid(
            height=tip_length,
            top_length=root_length,
            top_width=0.0,
            bottom_length=root_length,
            bottom_width=root_top_depth,
            top_offset=(0.0, tip_top_z_offset),
        ).with_name("cusp_blade_tip")
        tip.move_anchor_to("bottom_center", root.world_anchor("top_center"))

        return [root, tip]


class CurvedKnifeBlade(ConceptTemplate):
    def __init__(
        self,
        root_profile,
        root_top_z_offset,
        tip_radius,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                root_profile=root_profile,
                root_top_z_offset=root_top_z_offset,
                tip_radius=tip_radius,
            )
        )
        self.semantic = "Blade"

    @staticmethod
    def _build_components(root_profile, root_top_z_offset, tip_radius):
        root_length, root_height, root_bottom_depth, root_top_depth = root_profile

        root = Cuboid(
            height=root_height,
            top_length=root_length,
            top_width=root_top_depth,
            bottom_length=root_length,
            bottom_width=root_bottom_depth,
            top_offset=(0.0, root_top_z_offset),
        ).with_name("tapered_blade_root")
        root.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        tip = Cylinder(
            height=root_length,
            top_radius=tip_radius,
            bottom_radius=tip_radius,
            top_radius_z=root_top_depth,
            bottom_radius_z=root_top_depth,
            is_quarter=True,
            rotation=(0.0, 0.0, pi / 2.0),
        ).with_name("quarter_cylinder_blade_tip")
        root_top_x, root_top_y, root_top_z = root.world_anchor("top_center")
        tip_axis_origin = (0.0, 0.0, 0.0)
        tip.move_local_point_to(
            tip_axis_origin,
            (root_top_x, root_top_y, root_top_z - root_top_depth / 2.0),
        )

        return [root, tip]


class StandardKnifeGuard(ConceptTemplate):
    def __init__(self, guard_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        length, height, depth = guard_size
        self._finalize_mesh(
            [
                Cuboid(
                    height=height,
                    top_length=length,
                    top_width=depth,
                ).with_name("standard_guard")
            ]
        )
        self.semantic = "Guard"


class RegularKnifeButton(ConceptTemplate):
    def __init__(self, button_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        length, height, depth = button_size
        self._finalize_mesh(
            [
                Cuboid(
                    height=height,
                    top_length=length,
                    top_width=depth,
                ).with_name("regular_button")
            ]
        )
        self.semantic = "Button"
