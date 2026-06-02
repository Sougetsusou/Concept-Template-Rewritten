from math import pi

from code.geometry_rewritten import ConceptTemplate, Cuboid, Cylinder, Rectangular_Ring


class CuboidalLighterBody(ConceptTemplate):
    def __init__(self, body_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(body_size))
        self.semantic = "Body"

    @staticmethod
    def _build_components(body_size):
        body_length, body_height, body_depth = body_size
        return [
            Cuboid(
                height=body_height,
                top_length=body_length,
                top_width=body_depth,
            ).with_name("cuboidal_body")
        ]


class CamberedLighterBody(ConceptTemplate):
    def __init__(
        self,
        body_size,
        side_radius_z,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(body_size, side_radius_z))
        self.semantic = "Body"

    @staticmethod
    def _build_components(body_size, side_radius_z):
        body_length, body_height, body_depth = body_size

        body = Cuboid(
            height=body_height,
            top_length=body_length,
            top_width=body_depth,
        ).with_name("body_core")

        back_round = Cylinder(
            height=body_height,
            top_radius=body_length / 2.0,
            top_radius_z=side_radius_z,
            bottom_radius_z=side_radius_z,
            is_half=True,
            rotation=(0.0, pi, 0.0),
        ).with_name("back_camber")
        back_round.move_anchor_to("half_flat_center", body.world_anchor("back_center"))

        front_round = Cylinder(
            height=body_height,
            top_radius=body_length / 2.0,
            top_radius_z=side_radius_z,
            bottom_radius_z=side_radius_z,
            is_half=True,
        ).with_name("front_camber")
        front_round.move_anchor_to("half_flat_center", body.world_anchor("front_center"))

        return [body, back_round, front_round]


class DoubleLayerLighterBody(ConceptTemplate):
    def __init__(
        self,
        main_size,
        top_size,
        top_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(main_size, top_size, top_offset))
        self.semantic = "Body"

    @staticmethod
    def _build_components(main_size, top_size, top_offset):
        main_length, main_height, main_depth = main_size
        top_length, top_height, top_depth = top_size
        top_offset_x, top_offset_z = top_offset

        main = Cuboid(
            height=main_height,
            top_length=main_length,
            top_width=main_depth,
        ).with_name("main_body")

        top = Cuboid(
            height=top_height,
            top_length=top_length,
            top_width=top_depth,
        ).with_name("raised_top_body")
        main_top_x, main_top_y, main_top_z = main.world_anchor("top_center")
        top.move_anchor_to(
            "bottom_center",
            (main_top_x + top_offset_x, main_top_y, main_top_z + top_offset_z),
        )

        return [main, top]


class SimplifiedLighterWheel(ConceptTemplate):
    def __init__(
        self,
        wheel_radius,
        wheel_width,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(wheel_radius, wheel_width))
        self.semantic = "Wheel"

    @staticmethod
    def _build_components(wheel_radius, wheel_width):
        return [
            Cylinder(
                height=wheel_width,
                top_radius=wheel_radius,
                rotation=(0.0, 0.0, pi / 2.0),
            ).with_name("wheel")
        ]


class StandardLighterWheel(ConceptTemplate):
    def __init__(
        self,
        middle_radius,
        middle_width,
        side_radius,
        side_width,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                middle_radius=middle_radius,
                middle_width=middle_width,
                side_radius=side_radius,
                side_width=side_width,
            )
        )
        self.semantic = "Wheel"

    @staticmethod
    def _build_components(middle_radius, middle_width, side_radius, side_width):
        middle = Cylinder(
            height=middle_width,
            top_radius=middle_radius,
            rotation=(0.0, 0.0, pi / 2.0),
        ).with_name("middle_wheel")

        right_side = Cylinder(
            height=side_width,
            top_radius=side_radius,
            rotation=(0.0, 0.0, pi / 2.0),
        ).with_name("right_side_wheel")
        right_side.move_anchor_to("top_center", middle.world_anchor("bottom_center"))

        left_side = Cylinder(
            height=side_width,
            top_radius=side_radius,
            rotation=(0.0, 0.0, pi / 2.0),
        ).with_name("left_side_wheel")
        left_side.move_anchor_to("bottom_center", middle.world_anchor("top_center"))

        return [middle, right_side, left_side]


class LShapedLighterButton(ConceptTemplate):
    def __init__(
        self,
        bottom_size,
        top_size,
        top_z_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                bottom_size=bottom_size,
                top_size=top_size,
                top_z_offset=top_z_offset,
            )
        )
        self.semantic = "Button"

    @staticmethod
    def _build_components(bottom_size, top_size, top_z_offset):
        bottom_length, bottom_height, bottom_depth = bottom_size
        top_length, top_height, top_depth = top_size

        bottom = Cuboid(
            height=bottom_height,
            top_length=bottom_length,
            top_width=bottom_depth,
        ).with_name("lower_button")
        bottom.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        top = Cuboid(
            height=top_height,
            top_length=top_length,
            top_width=top_depth,
        ).with_name("upper_button")
        bottom_top_x, bottom_top_y, bottom_top_z = bottom.world_anchor("top_center")
        top.move_anchor_to(
            "bottom_center",
            (bottom_top_x, bottom_top_y, bottom_top_z + top_z_offset),
        )

        return [bottom, top]


class DoubleCamberedLighterButton(ConceptTemplate):
    def __init__(
        self,
        bottom_size,
        top_size,
        bottom_side_radius_z,
        top_side_radius_z,
        top_z_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                bottom_size=bottom_size,
                top_size=top_size,
                bottom_side_radius_z=bottom_side_radius_z,
                top_side_radius_z=top_side_radius_z,
                top_z_offset=top_z_offset,
            )
        )
        self.semantic = "Button"

    @staticmethod
    def _build_components(
        bottom_size,
        top_size,
        bottom_side_radius_z,
        top_side_radius_z,
        top_z_offset,
    ):
        bottom_length, bottom_height, bottom_depth = bottom_size
        top_length, top_height, top_depth = top_size

        bottom = Cuboid(
            height=bottom_height,
            top_length=bottom_length,
            top_width=bottom_depth,
        ).with_name("lower_button")
        bottom.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        top = Cuboid(
            height=top_height,
            top_length=top_length,
            top_width=top_depth,
        ).with_name("upper_button")
        bottom_top_x, bottom_top_y, bottom_top_z = bottom.world_anchor("top_center")
        top.move_anchor_to(
            "bottom_center",
            (bottom_top_x, bottom_top_y, bottom_top_z + top_z_offset),
        )

        bottom_round = Cylinder(
            height=bottom_height,
            top_radius=bottom_length / 2.0,
            top_radius_z=bottom_side_radius_z,
            bottom_radius_z=bottom_side_radius_z,
            is_half=True,
            rotation=(0.0, pi, 0.0),
        ).with_name("lower_button_back_camber")
        bottom_round.move_anchor_to("half_flat_center", bottom.world_anchor("back_center"))

        top_round = Cylinder(
            height=top_height,
            top_radius=top_length / 2.0,
            top_radius_z=top_side_radius_z,
            bottom_radius_z=top_side_radius_z,
            is_half=True,
            rotation=(0.0, pi, 0.0),
        ).with_name("upper_button_back_camber")
        top_round.move_anchor_to("half_flat_center", top.world_anchor("back_center"))

        return [bottom, top, bottom_round, top_round]


class CuboidalLighterNozzle(ConceptTemplate):
    def __init__(
        self,
        nozzle_size,
        wall_thickness,
        top_open_length,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                nozzle_size=nozzle_size,
                wall_thickness=wall_thickness,
                top_open_length=top_open_length,
            )
        )
        self.semantic = "Nozzle"

    @staticmethod
    def _build_components(nozzle_size, wall_thickness, top_open_length):
        outer_length, outer_height, outer_depth = nozzle_size

        right_wall = Cuboid(
            height=outer_height,
            top_length=wall_thickness,
            top_width=outer_depth,
        ).with_name("right_wall")
        right_wall.move_anchor_to(
            "right_center",
            (outer_length / 2.0, outer_height / 2.0, 0.0),
        )

        left_wall = Cuboid(
            height=outer_height,
            top_length=wall_thickness,
            top_width=outer_depth,
        ).with_name("left_wall")
        left_wall.move_anchor_to(
            "left_center",
            (-outer_length / 2.0, outer_height / 2.0, 0.0),
        )

        front_wall = Cuboid(
            height=outer_height,
            top_length=outer_length,
            top_width=wall_thickness,
        ).with_name("front_wall")
        front_wall.move_anchor_to(
            "front_center",
            (0.0, outer_height / 2.0, outer_depth / 2.0),
        )

        top_cap = Cuboid(
            height=wall_thickness,
            top_length=outer_length,
            top_width=top_open_length,
        ).with_name("top_cap")
        top_cap.move_anchor_to(
            "top_center",
            (0.0, outer_height, (outer_depth - top_open_length) / 2.0),
        )

        return [right_wall, left_wall, front_wall, top_cap]


class CamberedLighterNozzle(ConceptTemplate):
    def __init__(
        self,
        nozzle_size,
        front_radius_z,
        wall_thickness,
        top_open_length,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                nozzle_size=nozzle_size,
                front_radius_z=front_radius_z,
                wall_thickness=wall_thickness,
                top_open_length=top_open_length,
            )
        )
        self.semantic = "Nozzle"

    @staticmethod
    def _build_components(nozzle_size, front_radius_z, wall_thickness, top_open_length):
        outer_length, outer_height, outer_depth = nozzle_size

        right_wall = Cuboid(
            height=outer_height,
            top_length=wall_thickness,
            top_width=outer_depth,
        ).with_name("right_wall")
        right_wall.move_anchor_to(
            "right_center",
            (outer_length / 2.0, outer_height / 2.0, 0.0),
        )

        left_wall = Cuboid(
            height=outer_height,
            top_length=wall_thickness,
            top_width=outer_depth,
        ).with_name("left_wall")
        left_wall.move_anchor_to(
            "left_center",
            (-outer_length / 2.0, outer_height / 2.0, 0.0),
        )

        front_round = Cylinder(
            height=outer_height,
            top_radius=outer_length / 2.0,
            top_radius_z=front_radius_z,
            bottom_radius_z=front_radius_z,
            is_half=True,
        ).with_name("front_camber")
        front_round.move_anchor_to(
            "half_flat_center",
            (0.0, outer_height / 2.0, outer_depth / 2.0),
        )

        top_cap = Cuboid(
            height=wall_thickness,
            top_length=outer_length,
            top_width=top_open_length,
        ).with_name("top_cap")
        top_cap.move_anchor_to(
            "top_center",
            (0.0, outer_height, (outer_depth - top_open_length) / 2.0),
        )

        return [right_wall, left_wall, front_round, top_cap]


class EnvelopingLighterNozzle(ConceptTemplate):
    def __init__(
        self,
        nozzle_size,
        wall_thickness,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(nozzle_size, wall_thickness))
        self.semantic = "Nozzle"

    @staticmethod
    def _build_components(nozzle_size, wall_thickness):
        outer_length, outer_height, outer_depth = nozzle_size
        nozzle = Rectangular_Ring(
            front_height=outer_height,
            outer_top_length=outer_length,
            outer_top_width=outer_depth,
            inner_top_length=outer_length - wall_thickness * 2.0,
            inner_top_width=outer_depth - wall_thickness * 2.0,
        ).with_name("enveloping_nozzle")
        nozzle.move_anchor_to("outer_bottom_center", (0.0, 0.0, 0.0))
        return [nozzle]


class RegularLighterCover(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        inner_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(outer_size, inner_size))
        self.semantic = "Cover"

    @staticmethod
    def _build_components(outer_size, inner_size):
        outer_length, outer_height, outer_depth = outer_size
        inner_length, inner_height, inner_depth = inner_size
        cap_height = outer_height - inner_height

        lower_ring = Rectangular_Ring(
            front_height=inner_height,
            outer_top_length=outer_length,
            outer_top_width=outer_depth,
            inner_top_length=inner_length,
            inner_top_width=inner_depth,
        ).with_name("lower_cover_ring")
        lower_ring.move_anchor_to("outer_bottom_center", (0.0, 0.0, -outer_depth / 2.0))

        top_cap = Cuboid(
            height=cap_height,
            top_length=outer_length,
            top_width=outer_depth,
        ).with_name("top_cover_cap")
        top_cap.move_anchor_to(
            "bottom_center",
            lower_ring.world_anchor("outer_top_center"),
        )

        return [top_cap, lower_ring]


class StandardLighterWick(ConceptTemplate):
    def __init__(
        self,
        wick_radius,
        wick_height,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(wick_radius, wick_height))
        self.semantic = "Wick"

    @staticmethod
    def _build_components(wick_radius, wick_height):
        wick = Cylinder(
            height=wick_height,
            top_radius=wick_radius,
        ).with_name("wick")
        wick.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        return [wick]
