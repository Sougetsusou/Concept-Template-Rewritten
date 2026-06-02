from math import cos, pi

from code.geometry import ConceptTemplate, Cuboid, Cylinder, Ring, Sphere


DEGREES_TO_RADIANS = pi / 180.0


class CylindricalKitchenPotBody(ConceptTemplate):
    def __init__(
        self,
        outer_profile,
        inner_opening,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_profile=outer_profile,
                inner_opening=inner_opening,
            )
        )
        self.semantic = "Body"

    @classmethod
    def _build_components(cls, outer_profile, inner_opening):
        outer_top_radius, outer_bottom_radius, total_height = outer_profile
        inner_top_radius, inner_bottom_radius, open_height = inner_opening
        lower_height = total_height - open_height
        split_outer_radius = cls._outer_radius_at_open_bottom(
            outer_top_radius=outer_top_radius,
            outer_bottom_radius=outer_bottom_radius,
            total_height=total_height,
            open_height=open_height,
        )

        lower_shell = Cylinder(
            height=lower_height,
            top_radius=split_outer_radius,
            bottom_radius=outer_bottom_radius,
        ).with_name("lower_closed_body")
        lower_shell.move_anchor_to(
            "bottom_center",
            (0.0, -total_height / 2.0, 0.0),
        )

        upper_shell = Ring(
            height=open_height,
            outer_top_radius=outer_top_radius,
            inner_top_radius=inner_top_radius,
            outer_bottom_radius=split_outer_radius,
            inner_bottom_radius=inner_bottom_radius,
        ).with_name("upper_open_body")
        upper_shell.move_anchor_to(
            "axis_bottom_center",
            lower_shell.world_anchor("top_center"),
        )

        return [lower_shell, upper_shell]

    @staticmethod
    def _outer_radius_at_open_bottom(
        outer_top_radius,
        outer_bottom_radius,
        total_height,
        open_height,
    ):
        open_fraction = open_height / total_height
        return outer_top_radius * (1.0 - open_fraction) + (
            outer_bottom_radius * open_fraction
        )


class CylindricalKitchenPotCover(ConceptTemplate):
    def __init__(self, cover_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        radius, height = cover_size
        self._finalize_mesh(
            [
                Cylinder(height=height, top_radius=radius).with_name(
                    "flat_cylindrical_cover"
                )
            ]
        )
        self.semantic = "Cover"


class CarvedCylindricalKitchenPotCover(ConceptTemplate):
    def __init__(
        self,
        outer_profile,
        inner_opening,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_profile=outer_profile,
                inner_opening=inner_opening,
            )
        )
        self.semantic = "Cover"

    @classmethod
    def _build_components(cls, outer_profile, inner_opening):
        outer_top_radius, outer_bottom_radius, total_height = outer_profile
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
        ).with_name("lower_carved_opening")
        lower_ring.move_anchor_to(
            "axis_bottom_center",
            (0.0, -total_height / 2.0, 0.0),
        )

        upper_cap = Cylinder(
            height=cap_height,
            top_radius=outer_top_radius,
            bottom_radius=split_outer_radius,
        ).with_name("upper_cover_cap")
        upper_cap.move_anchor_to(
            "bottom_center",
            lower_ring.world_anchor("axis_top_center"),
        )

        return [upper_cap, lower_ring]

    @staticmethod
    def _outer_radius_at_open_top(
        outer_top_radius,
        outer_bottom_radius,
        total_height,
        open_height,
    ):
        open_fraction = open_height / total_height
        return outer_bottom_radius * (1.0 - open_fraction) + (
            outer_top_radius * open_fraction
        )


class SemiSphericalKitchenPotCover(ConceptTemplate):
    def __init__(
        self,
        sphere_radius,
        bottom_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        bottom_angle = bottom_angle_degrees * DEGREES_TO_RADIANS
        cover = Sphere(
            radius=sphere_radius,
            top_angle=0.0,
            bottom_angle=bottom_angle,
        ).with_name("semi_spherical_cover")
        cover.move_anchor_to("bottom_pole", (0.0, 0.0, 0.0))
        self._finalize_mesh([cover])
        self.semantic = "Cover"


class CuboidalKitchenPotTopHandle(ConceptTemplate):
    def __init__(self, handle_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        length, height, depth = handle_size
        handle = Cuboid(
            height=height,
            top_length=length,
            top_width=depth,
        ).with_name("single_cuboidal_top_handle")
        handle.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        self._finalize_mesh([handle])
        self.semantic = "Handle"


class TrifoldKitchenPotTopHandle(ConceptTemplate):
    def __init__(
        self,
        mounting_size,
        mounting_separation,
        grip_size,
        mounting_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                mounting_size=mounting_size,
                mounting_separation=mounting_separation,
                grip_size=grip_size,
                mounting_rotation_degrees=mounting_rotation_degrees,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        mounting_size,
        mounting_separation,
        grip_size,
        mounting_rotation_degrees,
    ):
        mount_length, mount_height, mount_depth = mounting_size
        grip_length, grip_height, grip_depth = grip_size
        mount_rotation = mounting_rotation_degrees * DEGREES_TO_RADIANS

        left_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
            rotation=(0.0, 0.0, -mount_rotation),
        ).with_name("left_slanted_mount")
        left_mount.move_anchor_to(
            "bottom_center",
            (mounting_separation / 2.0, 0.0, 0.0),
        )

        right_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
            rotation=(0.0, 0.0, mount_rotation),
        ).with_name("right_slanted_mount")
        right_mount.move_anchor_to(
            "bottom_center",
            (-mounting_separation / 2.0, 0.0, 0.0),
        )

        grip = Cuboid(
            height=grip_height,
            top_length=grip_length,
            top_width=grip_depth,
        ).with_name("top_grip_bridge")
        left_top_anchor = left_mount.world_anchor("top_center")
        right_top_anchor = right_mount.world_anchor("top_center")
        grip_mount = (left_top_anchor + right_top_anchor) / 2.0
        grip.move_anchor_to(
            "bottom_center",
            grip_mount,
        )

        return [left_mount, right_mount, grip]


class SemiRingKitchenPotTopHandle(ConceptTemplate):
    def __init__(
        self,
        ring_size,
        arc_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        outer_radius, inner_radius, tube_height = ring_size
        arc_angle = arc_angle_degrees * DEGREES_TO_RADIANS
        top_handle = Ring(
            height=tube_height,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=arc_angle,
            position=(0.0, -outer_radius * cos(arc_angle / 2.0), 0.0),
            rotation=(-pi / 2.0, -pi / 2.0 + arc_angle / 2.0, 0.0),
            rotation_order="YXZ",
        ).with_name("semi_ring_top_handle")
        self._finalize_mesh([top_handle])
        self.semantic = "Handle"


class MultilevelKitchenPotTopHandle(ConceptTemplate):
    def __init__(
        self,
        level_sections,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(level_sections=level_sections))
        self.semantic = "Handle"

    @staticmethod
    def _build_components(level_sections):
        components = []
        previous_top_anchor = (0.0, 0.0, 0.0)
        for level_number, section in enumerate(level_sections, start=1):
            level = Cylinder(
                height=section["height"],
                top_radius=section["top_radius"],
                bottom_radius=section["bottom_radius"],
            ).with_name(f"level_{level_number}_cylindrical_knob")
            level.move_anchor_to("bottom_center", previous_top_anchor)
            components.append(level)
            previous_top_anchor = level.world_anchor("top_center")
        return components


class TrifoldKitchenPotSideHandle(ConceptTemplate):
    def __init__(
        self,
        mounting_size,
        mounting_separation,
        grip_size,
        mounting_rotation_degrees,
        handle_separation,
        whole_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                mounting_size=mounting_size,
                mounting_separation=mounting_separation,
                grip_size=grip_size,
                mounting_rotation_degrees=mounting_rotation_degrees,
                handle_separation=handle_separation,
                whole_rotation_degrees=whole_rotation_degrees,
            )
        )
        self.semantic = "Handle"

    @classmethod
    def _build_components(
        cls,
        mounting_size,
        mounting_separation,
        grip_size,
        mounting_rotation_degrees,
        handle_separation,
        whole_rotation_degrees,
    ):
        mount_rotation = mounting_rotation_degrees * DEGREES_TO_RADIANS
        whole_rotation = whole_rotation_degrees * DEGREES_TO_RADIANS

        positive_x_group = cls._build_side_triplet(
            name_prefix="positive_x",
            extension_sign=1.0,
            group_origin=(handle_separation / 2.0, 0.0, 0.0),
            group_rotation=(0.0, 0.0, whole_rotation),
            mounting_size=mounting_size,
            mounting_separation=mounting_separation,
            grip_size=grip_size,
            mount_rotation=mount_rotation,
        )
        negative_x_group = cls._build_side_triplet(
            name_prefix="negative_x",
            extension_sign=-1.0,
            group_origin=(-handle_separation / 2.0, 0.0, 0.0),
            group_rotation=(0.0, 0.0, -whole_rotation),
            mounting_size=mounting_size,
            mounting_separation=mounting_separation,
            grip_size=grip_size,
            mount_rotation=mount_rotation,
        )
        return positive_x_group + negative_x_group

    @classmethod
    def _build_side_triplet(
        cls,
        name_prefix,
        extension_sign,
        group_origin,
        group_rotation,
        mounting_size,
        mounting_separation,
        grip_size,
        mount_rotation,
    ):
        mount_length, mount_height, mount_depth = mounting_size
        grip_length, grip_height, grip_depth = grip_size
        mount_anchor = "left_center" if extension_sign > 0.0 else "right_center"
        grip_anchor = "left_center" if extension_sign > 0.0 else "right_center"

        front_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
            rotation=(0.0, -extension_sign * mount_rotation, 0.0),
        ).with_name(f"{name_prefix}_front_mount")
        front_mount.move_anchor_to(
            mount_anchor,
            (0.0, 0.0, mounting_separation / 2.0),
        )

        back_mount = Cuboid(
            height=mount_height,
            top_length=mount_length,
            top_width=mount_depth,
            rotation=(0.0, extension_sign * mount_rotation, 0.0),
        ).with_name(f"{name_prefix}_back_mount")
        back_mount.move_anchor_to(
            mount_anchor,
            (0.0, 0.0, -mounting_separation / 2.0),
        )

        bridge = Cuboid(
            height=grip_height,
            top_length=grip_length,
            top_width=grip_depth,
        ).with_name(f"{name_prefix}_grip_bridge")
        external_mount_anchor = "right_center" if extension_sign > 0.0 else "left_center"
        front_bridge_mount = front_mount.world_anchor(external_mount_anchor)
        back_bridge_mount = back_mount.world_anchor(external_mount_anchor)
        bridge_mount = (front_bridge_mount + back_bridge_mount) / 2.0
        bridge.move_anchor_to(
            grip_anchor,
            bridge_mount,
        )

        components = [front_mount, back_mount, bridge]
        for component in components:
            cls._apply_group_transform(component, group_origin, group_rotation)
        return components

    @staticmethod
    def _apply_group_transform(component, group_origin, group_rotation):
        component.rotate_about_point((0.0, 0.0, 0.0), group_rotation)
        current_x, current_y, current_z = component.position
        origin_x, origin_y, origin_z = group_origin
        component.set_transform(
            position=(
                current_x + origin_x,
                current_y + origin_y,
                current_z + origin_z,
            )
        )
        return component


class LShapedKitchenPotSideHandle(ConceptTemplate):
    def __init__(
        self,
        bottom_size,
        top_size,
        handle_separation,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                bottom_size=bottom_size,
                top_size=top_size,
                handle_separation=handle_separation,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(bottom_size, top_size, handle_separation):
        bottom_length, bottom_height, bottom_depth = bottom_size
        top_length, top_height, top_depth = top_size

        right_bottom = Cuboid(
            height=bottom_height,
            top_length=bottom_length,
            top_width=bottom_depth,
        ).with_name("right_lower_arm")
        right_bottom.move_anchor_to(
            "left_center",
            (handle_separation / 2.0, 0.0, 0.0),
        )

        right_top = Cuboid(
            height=top_height,
            top_length=top_length,
            top_width=top_depth,
        ).with_name("right_upper_arm")
        right_top.move_anchor_to(
            "bottom_left_center",
            (handle_separation / 2.0, bottom_height / 2.0, 0.0),
        )

        left_bottom = Cuboid(
            height=bottom_height,
            top_length=bottom_length,
            top_width=bottom_depth,
        ).with_name("left_lower_arm")
        left_bottom.move_anchor_to(
            "right_center",
            (-handle_separation / 2.0, 0.0, 0.0),
        )

        left_top = Cuboid(
            height=top_height,
            top_length=top_length,
            top_width=top_depth,
        ).with_name("left_upper_arm")
        left_top.move_anchor_to(
            "bottom_right_center",
            (-handle_separation / 2.0, bottom_height / 2.0, 0.0),
        )

        return [right_bottom, right_top, left_bottom, left_top]


class CuboidalKitchenPotSideHandle(ConceptTemplate):
    def __init__(self, handle_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        length, height, depth = handle_size
        handle = Cuboid(
            height=height,
            top_length=length,
            top_width=depth,
        ).with_name("single_cuboidal_side_handle")
        handle.move_anchor_to("front_center", (0.0, 0.0, 0.0))
        self._finalize_mesh([handle])
        self.semantic = "Handle"
