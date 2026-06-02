from math import pi

import numpy as np

from code.geometry import ConceptTemplate, Cuboid, Cylinder


DEGREES_TO_RADIANS = pi / 180.0
DISPLAY_ROTATION_ORDER = "YXZ"


class FrustumDisplayScreen(ConceptTemplate):
    def __init__(
        self,
        has_front_layer,
        front_layer_size,
        back_shell_size,
        back_shell_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPLAY_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                has_front_layer=has_front_layer,
                front_layer_size=front_layer_size,
                back_shell_size=back_shell_size,
                back_shell_offset=back_shell_offset,
            )
        )
        self.semantic = "Screen"

    @staticmethod
    def _build_components(
        has_front_layer,
        front_layer_size,
        back_shell_size,
        back_shell_offset,
    ):
        back_shell_length, back_shell_height, back_shell_depth = back_shell_size
        front_layer_length, front_layer_height, front_layer_depth = front_layer_size
        shell_offset_x, shell_offset_y = back_shell_offset

        back_shell = Cuboid(
            height=back_shell_depth,
            top_length=back_shell_length,
            top_width=back_shell_height,
            bottom_length=front_layer_length,
            bottom_width=front_layer_height,
            top_offset=(shell_offset_x, shell_offset_y),
            rotation=(-pi / 2.0, 0.0, 0.0),
        ).with_name("tapered_back_shell")
        back_shell.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        components = [back_shell]
        if has_front_layer:
            front_layer = Cuboid(
                height=front_layer_height,
                top_length=front_layer_length,
                top_width=front_layer_depth,
            ).with_name("front_flat_layer")
            front_layer.move_anchor_to("back_center", (0.0, 0.0, 0.0))
            components.append(front_layer)

        return components


class FlatDisplayScreen(ConceptTemplate):
    def __init__(
        self,
        screen_size,
        has_back_layer,
        back_layer_size,
        back_layer_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPLAY_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                screen_size=screen_size,
                has_back_layer=has_back_layer,
                back_layer_size=back_layer_size,
                back_layer_offset=back_layer_offset,
            )
        )
        self.semantic = "Screen"

    @staticmethod
    def _build_components(screen_size, has_back_layer, back_layer_size, back_layer_offset):
        screen_length, screen_height, screen_depth = screen_size
        back_layer_length, back_layer_height, back_layer_depth = back_layer_size
        back_offset_x, back_offset_y = back_layer_offset

        screen = Cuboid(
            height=screen_height,
            top_length=screen_length,
            top_width=screen_depth,
        ).with_name("front_screen_panel")

        components = [screen]
        if has_back_layer:
            _, _, screen_back_z = screen.world_anchor("back_center")
            back_layer = Cuboid(
                height=back_layer_height,
                top_length=back_layer_length,
                top_width=back_layer_depth,
            ).with_name("back_layer")
            back_layer.move_anchor_to(
                "front_center",
                (back_offset_x, back_offset_y, screen_back_z),
            )
            components.append(back_layer)

        return components


class RectangularDisplayBase(ConceptTemplate):
    def __init__(
        self,
        base_size,
        base_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPLAY_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                base_size=base_size,
                base_rotation_degrees=base_rotation_degrees,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(base_size, base_rotation_degrees):
        base_length, base_height, base_depth = base_size
        pitch = base_rotation_degrees * DEGREES_TO_RADIANS
        base = Cuboid(
            height=base_height,
            top_length=base_length,
            top_width=base_depth,
            position=(0.0, -base_height / 2.0, 0.0),
            rotation=(pitch, 0.0, 0.0),
        ).with_name("rectangular_base_plate")
        return [base]


class CircularDisplayBase(ConceptTemplate):
    def __init__(
        self,
        base_size,
        base_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPLAY_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                base_size=base_size,
                base_rotation_degrees=base_rotation_degrees,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(base_size, base_rotation_degrees):
        base_radius, base_height = base_size
        pitch = base_rotation_degrees * DEGREES_TO_RADIANS
        base = Cylinder(
            height=base_height,
            top_radius=base_radius,
            position=(0.0, -base_height / 2.0, 0.0),
            rotation=(pitch, 0.0, 0.0),
        ).with_name("circular_base_plate")
        return [base]


class TShapedDisplayBase(ConceptTemplate):
    def __init__(
        self,
        main_bar_size,
        cross_bar_size,
        base_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPLAY_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                main_bar_size=main_bar_size,
                cross_bar_size=cross_bar_size,
                base_rotation_degrees=base_rotation_degrees,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(main_bar_size, cross_bar_size, base_rotation_degrees):
        main_length, main_height, main_depth = main_bar_size
        cross_length, cross_depth = cross_bar_size
        pitch = base_rotation_degrees * DEGREES_TO_RADIANS

        cross_bar = Cuboid(
            height=main_height,
            top_length=cross_length,
            top_width=cross_depth,
            position=(0.0, -main_height / 2.0, 0.0),
            rotation=(pitch, 0.0, 0.0),
        ).with_name("cross_bar")

        main_bar = Cuboid(
            height=main_height,
            top_length=main_length,
            top_width=main_depth,
            rotation=(pitch, 0.0, 0.0),
        ).with_name("main_bar")
        main_bar.move_anchor_to("back_center", cross_bar.world_anchor("front_center"))

        return [cross_bar, main_bar]


class VShapedDisplayBase(ConceptTemplate):
    def __init__(
        self,
        wing_size,
        open_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPLAY_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                wing_size=wing_size,
                open_angle_degrees=open_angle_degrees,
            )
        )
        self.semantic = "Base"

    @staticmethod
    def _build_components(wing_size, open_angle_degrees):
        wing_length, wing_height, wing_depth = wing_size
        half_open_angle = open_angle_degrees * DEGREES_TO_RADIANS / 2.0
        components = []

        for name, yaw in (
            ("left_wing", -half_open_angle),
            ("right_wing", half_open_angle),
        ):
            wing = Cuboid(
                height=wing_height,
                top_length=wing_length,
                top_width=wing_depth,
                position=(0.0, -wing_height / 2.0, wing_depth / 2.0),
            ).with_name(name)
            wing.rotate_about_point((0.0, 0.0, 0.0), (0.0, yaw, 0.0))
            components.append(wing)

        return components


class RearDisplaySupportSet(ConceptTemplate):
    def __init__(
        self,
        support_count,
        support_size,
        support_spacing,
        support_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPLAY_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                support_count=support_count,
                support_size=support_size,
                support_spacing=support_spacing,
                support_rotation_degrees=support_rotation_degrees,
            )
        )
        self.semantic = "Support"

    @staticmethod
    def _build_components(
        support_count,
        support_size,
        support_spacing,
        support_rotation_degrees,
    ):
        support_length, support_height, support_depth = support_size
        pitch = support_rotation_degrees * DEGREES_TO_RADIANS
        components = []

        for support_index in range(int(support_count)):
            mount_x = (support_spacing + support_length) * support_index
            support = Cuboid(
                height=support_height,
                top_length=support_length,
                top_width=support_depth,
                rotation=(pitch, 0.0, 0.0),
            ).with_name(f"rear_support_{support_index + 1}")
            support.move_anchor_to("top_front_center", (mount_x, 0.0, 0.0))
            components.append(support)

        return components


class RectangularDisplaySupportSet(ConceptTemplate):
    def __init__(
        self,
        support_count,
        support_size,
        support_spacing,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPLAY_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                support_count=support_count,
                support_size=support_size,
                support_spacing=support_spacing,
            )
        )
        self.semantic = "Support"

    @staticmethod
    def _build_components(support_count, support_size, support_spacing):
        support_length, support_height, support_depth = support_size
        components = []

        for support_index in range(int(support_count)):
            mount_x = (support_spacing + support_length) * support_index
            support = Cuboid(
                height=support_height,
                top_length=support_length,
                top_width=support_depth,
            ).with_name(f"vertical_support_{support_index + 1}")
            support.move_anchor_to("top_center", (mount_x, 0.0, 0.0))
            components.append(support)

        return components


class TrifoldDisplaySupport(ConceptTemplate):
    def __init__(
        self,
        has_upper_part,
        upper_part_size,
        upper_mount_point,
        has_middle_part,
        middle_part_size,
        middle_y_offset,
        has_bottom_part,
        bottom_part_size,
        bottom_rotation_degrees,
        bottom_z_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPLAY_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                has_upper_part=has_upper_part,
                upper_part_size=upper_part_size,
                upper_mount_point=upper_mount_point,
                has_middle_part=has_middle_part,
                middle_part_size=middle_part_size,
                middle_y_offset=middle_y_offset,
                has_bottom_part=has_bottom_part,
                bottom_part_size=bottom_part_size,
                bottom_rotation_degrees=bottom_rotation_degrees,
                bottom_z_offset=bottom_z_offset,
            )
        )
        self.semantic = "Support"

    @staticmethod
    def _build_components(
        has_upper_part,
        upper_part_size,
        upper_mount_point,
        has_middle_part,
        middle_part_size,
        middle_y_offset,
        has_bottom_part,
        bottom_part_size,
        bottom_rotation_degrees,
        bottom_z_offset,
    ):
        components = []
        base_point = np.array([0.0, 0.0, 0.0])

        if has_upper_part:
            upper_length, upper_height, upper_depth = upper_part_size
            upper = Cuboid(
                height=upper_height,
                top_length=upper_length,
                top_width=upper_depth,
            ).with_name("upper_plate")
            upper.move_anchor_to("front_center", upper_mount_point)
            base_point = upper.world_anchor("back_center")
            components.append(upper)

        if has_middle_part:
            middle_length, middle_height, middle_depth = middle_part_size
            base_x, base_y, base_z = base_point
            middle_mount = (base_x, base_y + middle_y_offset, base_z)
            middle = Cuboid(
                height=middle_height,
                top_length=middle_length,
                top_width=middle_depth,
            ).with_name("middle_stem")
            middle.move_anchor_to("top_front_center", middle_mount)
            base_point = middle.world_anchor("bottom_back_center")
            components.append(middle)

        if has_bottom_part:
            bottom_length, bottom_height, bottom_depth = bottom_part_size
            base_x, base_y, base_z = base_point
            bottom_mount = (base_x, base_y, base_z + bottom_z_offset)
            bottom = Cuboid(
                height=bottom_height,
                top_length=bottom_length,
                top_width=bottom_depth,
                rotation=(bottom_rotation_degrees * DEGREES_TO_RADIANS, 0.0, 0.0),
            ).with_name("bottom_foot")
            bottom.move_anchor_to("top_back_center", bottom_mount)
            components.append(bottom)

        return components


class TShapedDisplaySupport(ConceptTemplate):
    def __init__(
        self,
        upper_bar_size,
        upper_mount_point,
        middle_stem_size,
        middle_front_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPLAY_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                upper_bar_size=upper_bar_size,
                upper_mount_point=upper_mount_point,
                middle_stem_size=middle_stem_size,
                middle_front_offset=middle_front_offset,
            )
        )
        self.semantic = "Support"

    @staticmethod
    def _build_components(
        upper_bar_size,
        upper_mount_point,
        middle_stem_size,
        middle_front_offset,
    ):
        upper_length, upper_height, upper_depth = upper_bar_size
        middle_length, middle_height, middle_depth = middle_stem_size

        upper = Cuboid(
            height=upper_height,
            top_length=upper_length,
            top_width=upper_depth,
        ).with_name("upper_cross_bar")
        upper.move_anchor_to("front_center", upper_mount_point)

        upper_bottom_front_x, upper_bottom_front_y, upper_bottom_front_z = (
            upper.world_anchor("bottom_front_center")
        )
        middle_mount = (
            upper_bottom_front_x,
            upper_bottom_front_y,
            upper_bottom_front_z + middle_front_offset,
        )
        middle = Cuboid(
            height=middle_height,
            top_length=middle_length,
            top_width=middle_depth,
        ).with_name("middle_stem")
        middle.move_anchor_to("top_front_center", middle_mount)

        return [upper, middle]
