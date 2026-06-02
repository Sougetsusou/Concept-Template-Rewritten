from math import pi

from code.geometry_rewritten import ConceptTemplate, Cuboid, Cylinder, Rectangular_Ring


STAPLER_ROTATION_ORDER = "XYZ"


class SideBlockStaplerBody(ConceptTemplate):
    def __init__(
        self,
        base_size,
        side_block_size,
        side_block_spacing,
        side_block_depth_offset,
        has_shaft,
        shaft_center_section_size,
        shaft_side_section_size,
        shaft_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=STAPLER_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                base_size=base_size,
                side_block_size=side_block_size,
                side_block_spacing=side_block_spacing,
                side_block_depth_offset=side_block_depth_offset,
                has_shaft=has_shaft,
                shaft_center_section_size=shaft_center_section_size,
                shaft_side_section_size=shaft_side_section_size,
                shaft_offset=shaft_offset,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(
        base_size,
        side_block_size,
        side_block_spacing,
        side_block_depth_offset,
        has_shaft,
        shaft_center_section_size,
        shaft_side_section_size,
        shaft_offset,
    ):
        base_length, base_height, base_depth = base_size
        side_length, side_height, side_depth = side_block_size
        side_spacing = side_block_spacing
        side_depth_offset = side_block_depth_offset
        shaft_center_radius, shaft_center_length = shaft_center_section_size
        shaft_side_radius, shaft_side_length = shaft_side_section_size
        shaft_offset_y, shaft_offset_z = shaft_offset

        base = Cuboid(
            height=base_height,
            top_length=base_length,
            top_width=base_depth,
        ).with_name("base")

        base_top_x, base_top_y, base_top_z = base.world_anchor("top_center")
        _, _, base_back_z = base.world_anchor("back_center")
        side_center_z = base_back_z + side_depth / 2.0 + side_depth_offset

        components = [base]
        reference_side_block = None
        for name, side_sign in (
            ("left_side_block", 1.0),
            ("right_side_block", -1.0),
        ):
            side = Cuboid(
                height=side_height,
                top_length=side_length,
                top_width=side_depth,
            ).with_name(name)
            side.move_anchor_to(
                "bottom_center",
                (
                    side_sign * side_spacing / 2.0,
                    base_top_y,
                    side_center_z,
                ),
            )
            if reference_side_block is None:
                reference_side_block = side
            components.append(side)

        if int(has_shaft) == 1:
            _, side_center_y, side_center_z = reference_side_block.world_anchor("center")
            shaft_center_y = side_center_y + shaft_offset_y
            shaft_center_z = side_center_z + shaft_offset_z

            center_shaft = Cylinder(
                height=shaft_center_length,
                top_radius=shaft_center_radius,
                position=(base_top_x, shaft_center_y, shaft_center_z),
                rotation=(0.0, 0.0, pi / 2.0),
            ).with_name("center_shaft")
            components.append(center_shaft)

            left_shaft = Cylinder(
                height=shaft_side_length,
                top_radius=shaft_side_radius,
                rotation=(0.0, 0.0, pi / 2.0),
            ).with_name("left_shaft")
            left_shaft.move_anchor_to(
                "top_center",
                center_shaft.world_anchor("bottom_center"),
            )
            components.append(left_shaft)

            right_shaft = Cylinder(
                height=shaft_side_length,
                top_radius=shaft_side_radius,
                rotation=(0.0, 0.0, pi / 2.0),
            ).with_name("right_shaft")
            right_shaft.move_anchor_to(
                "bottom_center",
                center_shaft.world_anchor("top_center"),
            )
            components.append(right_shaft)

        return components


class SolidStaplerCover(ConceptTemplate):
    def __init__(
        self,
        size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=STAPLER_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(size=size))
        self.semantic = "Cover"

    @staticmethod
    def _build_components(size):
        cover_length, cover_height, cover_depth = size
        cover = Cuboid(
            height=cover_height,
            top_length=cover_length,
            top_width=cover_depth,
        ).with_name("solid_cover")
        cover.move_anchor_to("bottom_back_center", (0.0, 0.0, 0.0))
        return [cover]


class CarvedStaplerCover(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        inner_opening_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=STAPLER_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                inner_opening_size=inner_opening_size,
            )
        )
        self.semantic = "Cover"

    @staticmethod
    def _build_components(outer_size, inner_opening_size):
        outer_length, outer_height, outer_depth = outer_size
        inner_length, opening_height, inner_depth = inner_opening_size
        solid_height = outer_height - opening_height

        lower_frame = Rectangular_Ring(
            front_height=opening_height,
            outer_top_length=outer_length,
            outer_top_width=outer_depth,
            inner_top_length=inner_length,
            inner_top_width=inner_depth,
        ).with_name("lower_open_frame")
        lower_frame.move_anchor_to("outer_bottom_back_center", (0.0, 0.0, 0.0))

        upper_solid = Cuboid(
            height=solid_height,
            top_length=outer_length,
            top_width=outer_depth,
        ).with_name("upper_solid_cover")
        upper_solid.move_anchor_to(
            "bottom_back_center",
            lower_frame.world_anchor("outer_top_back_center"),
        )

        return [upper_solid, lower_frame]


class CarvedStaplerMagazine(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        inner_opening_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=STAPLER_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                inner_opening_size=inner_opening_size,
            )
        )
        self.semantic = "Magazine"

    @staticmethod
    def _build_components(outer_size, inner_opening_size):
        outer_length, outer_height, outer_depth = outer_size
        inner_length, opening_height, inner_depth = inner_opening_size
        solid_height = outer_height - opening_height

        lower_frame = Rectangular_Ring(
            front_height=opening_height,
            outer_top_length=outer_length,
            outer_top_width=outer_depth,
            inner_top_length=inner_length,
            inner_top_width=inner_depth,
        ).with_name("lower_open_magazine_frame")
        lower_frame.move_anchor_to("outer_bottom_back_center", (0.0, 0.0, 0.0))

        upper_solid = Cuboid(
            height=solid_height,
            top_length=outer_length,
            top_width=outer_depth,
        ).with_name("upper_solid_magazine")
        upper_solid.move_anchor_to(
            "bottom_back_center",
            lower_frame.world_anchor("outer_top_back_center"),
        )

        return [upper_solid, lower_frame]


class BoxTrayStaplerMagazine(ConceptTemplate):
    def __init__(
        self,
        tray_size,
        wall_thickness,
        front_wall_height,
        side_wall_depth,
        side_wall_depth_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=STAPLER_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                tray_size=tray_size,
                wall_thickness=wall_thickness,
                front_wall_height=front_wall_height,
                side_wall_depth=side_wall_depth,
                side_wall_depth_offset=side_wall_depth_offset,
            )
        )
        self.semantic = "Magazine"

    @staticmethod
    def _build_components(
        tray_size,
        wall_thickness,
        front_wall_height,
        side_wall_depth,
        side_wall_depth_offset,
    ):
        tray_width, tray_height, tray_depth = tray_size
        thickness = wall_thickness
        side_depth = side_wall_depth
        side_depth_offset = side_wall_depth_offset

        bottom_panel = Cuboid(
            height=thickness,
            top_length=tray_width,
            top_width=tray_depth,
        ).with_name("bottom_panel")
        bottom_panel.move_anchor_to("bottom_back_center", (0.0, 0.0, 0.0))

        back_panel = Cuboid(
            height=tray_height,
            top_length=tray_width,
            top_width=thickness,
        ).with_name("back_panel")
        back_panel.move_anchor_to("bottom_back_center", (0.0, 0.0, 0.0))

        front_panel = Cuboid(
            height=front_wall_height,
            top_length=tray_width,
            top_width=thickness,
        ).with_name("front_panel")
        front_panel.move_anchor_to(
            "bottom_front_center",
            (0.0, 0.0, tray_depth),
        )

        side_center_z = tray_depth / 2.0 + side_depth_offset
        side_center_y = tray_height / 2.0
        left_panel = Cuboid(
            height=tray_height,
            top_length=thickness,
            top_width=side_depth,
        ).with_name("left_panel")
        left_panel.move_anchor_to(
            "right_center",
            (
                tray_width / 2.0,
                side_center_y,
                side_center_z,
            ),
        )

        right_panel = Cuboid(
            height=tray_height,
            top_length=thickness,
            top_width=side_depth,
        ).with_name("right_panel")
        right_panel.move_anchor_to(
            "left_center",
            (
                -tray_width / 2.0,
                side_center_y,
                side_center_z,
            ),
        )

        return [bottom_panel, back_panel, front_panel, left_panel, right_panel]
