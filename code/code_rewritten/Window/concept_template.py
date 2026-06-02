from math import asin, cos, pi, sin

from code.geometry_rewritten import ConceptTemplate, Cuboid, Rectangular_Ring, Ring


def _panel_frame(
    name,
    frame_width,
    frame_depth,
    frame_thickness,
    glass_width,
    glass_height,
    glass_vertical_offset,
    center,
):
    center_x, center_y, center_z = center
    frame = Rectangular_Ring(
        front_height=frame_thickness,
        outer_top_length=frame_width,
        outer_top_width=frame_depth,
        inner_top_length=glass_width,
        inner_top_width=glass_height,
        inner_offset=(0.0, -glass_vertical_offset),
        position=(center_x, center_y, center_z),
        rotation=(pi / 2.0, 0.0, 0.0),
    ).with_name(name)
    return frame


def _glass_pane(name, glass_width, glass_height, glass_depth, center):
    return Cuboid(
        height=glass_height,
        top_length=glass_width,
        top_width=glass_depth,
        position=center,
    ).with_name(name)


class StandardWindowFrame(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        inner_size,
        inner_outer_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                inner_size=inner_size,
                inner_outer_offset=inner_outer_offset,
            )
        )
        self.semantic = "Frame"

    @staticmethod
    def _build_components(outer_size, inner_size, inner_outer_offset):
        outer_width, outer_height, frame_depth = outer_size
        inner_width, inner_height = inner_size
        inner_offset_x, inner_offset_y = inner_outer_offset

        frame = Rectangular_Ring(
            front_height=frame_depth,
            outer_top_length=outer_width,
            outer_top_width=outer_height,
            inner_top_length=inner_width,
            inner_top_width=inner_height,
            inner_offset=(inner_offset_x, -inner_offset_y),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("outer_window_frame")
        return [frame]


class SymmetricalPanelWindow(ConceptTemplate):
    def __init__(
        self,
        outside_inner_size,
        outside_inner_offset,
        panel_count,
        panel_profiles,
        horizontal_offsets,
        base_z_offset,
        mirror_glass_offsets,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outside_inner_size=outside_inner_size,
                outside_inner_offset=outside_inner_offset,
                panel_count=panel_count,
                panel_profiles=panel_profiles,
                horizontal_offsets=horizontal_offsets,
                base_z_offset=base_z_offset,
                mirror_glass_offsets=mirror_glass_offsets,
            )
        )
        self.semantic = "Window"

    @staticmethod
    def _layer_positions(panel_profiles, base_z_offset):
        lower_reference_profile, upper_reference_profile, _ = panel_profiles
        return (
            base_z_offset - lower_reference_profile["frame_height"],
            base_z_offset,
            base_z_offset
            + lower_reference_profile["frame_height"] / 2.0
            + upper_reference_profile["frame_height"] / 2.0,
        )

    @classmethod
    def _panel_layout(cls, panel_count, panel_profiles, horizontal_offsets, base_z_offset):
        lower_z, middle_z, upper_z = cls._layer_positions(panel_profiles, base_z_offset)
        profile_0, profile_1, profile_2 = panel_profiles
        (
            offset_0,
            offset_1,
            offset_2,
            offset_3,
            offset_4,
            offset_5,
        ) = horizontal_offsets
        layouts_by_count = {
            1: ((profile_0, offset_0, middle_z, 1.0),),
            2: (
                (profile_0, offset_0, middle_z, 1.0),
                (profile_0, offset_1, middle_z, -1.0),
            ),
            3: (
                (profile_0, offset_0, middle_z, 1.0),
                (profile_1, offset_1, upper_z, 1.0),
                (profile_0, offset_2, middle_z, -1.0),
            ),
            4: (
                (profile_0, offset_0, middle_z, 1.0),
                (profile_1, offset_1, upper_z, 1.0),
                (profile_1, offset_2, upper_z, -1.0),
                (profile_0, offset_3, middle_z, -1.0),
            ),
            5: (
                (profile_2, offset_0, lower_z, 1.0),
                (profile_0, offset_1, middle_z, 1.0),
                (profile_1, offset_2, upper_z, 1.0),
                (profile_0, offset_3, middle_z, -1.0),
                (profile_2, offset_4, lower_z, -1.0),
            ),
            6: (
                (profile_2, offset_0, lower_z, 1.0),
                (profile_0, offset_1, middle_z, 1.0),
                (profile_1, offset_2, upper_z, 1.0),
                (profile_1, offset_3, upper_z, -1.0),
                (profile_0, offset_4, middle_z, -1.0),
                (profile_2, offset_5, lower_z, -1.0),
            ),
        }
        return layouts_by_count.get(int(panel_count), ())

    @classmethod
    def _build_components(
        cls,
        outside_inner_size,
        outside_inner_offset,
        panel_count,
        panel_profiles,
        horizontal_offsets,
        base_z_offset,
        mirror_glass_offsets,
    ):
        _, frame_depth = outside_inner_size
        _, outside_offset_y = outside_inner_offset
        components = []
        for panel_index, (profile, center_x, center_z, mirror_sign) in enumerate(
            cls._panel_layout(
                panel_count,
                panel_profiles,
                horizontal_offsets,
                base_z_offset,
            ),
            start=1,
        ):
            sign = mirror_sign if mirror_glass_offsets else 1.0
            glass_offset_x, glass_offset_y, glass_offset_z = profile["glass_offset"]
            glass_width, glass_height, glass_depth = profile["glass_size"]
            frame_center = (center_x, outside_offset_y, center_z)
            signed_glass_offset_x = glass_offset_x * sign
            components.append(
                _panel_frame(
                    name=f"panel_{panel_index}_frame",
                    frame_width=profile["frame_width"],
                    frame_depth=frame_depth,
                    frame_thickness=profile["frame_height"],
                    glass_width=glass_width,
                    glass_height=glass_height,
                    glass_vertical_offset=glass_offset_y,
                    center=frame_center,
                )
            )
            components.append(
                _glass_pane(
                    name=f"panel_{panel_index}_glass",
                    glass_width=glass_width,
                    glass_height=glass_height,
                    glass_depth=glass_depth,
                    center=(
                        center_x + signed_glass_offset_x,
                        outside_offset_y + glass_offset_y,
                        center_z + glass_offset_z,
                    ),
                )
            )
        return components


class AsymmetricalPanelWindow(ConceptTemplate):
    def __init__(
        self,
        outside_inner_size,
        outside_inner_offset,
        panel_count,
        panel_profiles,
        horizontal_offsets,
        base_z_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outside_inner_size=outside_inner_size,
                outside_inner_offset=outside_inner_offset,
                panel_count=panel_count,
                panel_profiles=panel_profiles,
                horizontal_offsets=horizontal_offsets,
                base_z_offset=base_z_offset,
            )
        )
        self.semantic = "Window"

    @staticmethod
    def _layer_positions(panel_profiles, base_z_offset):
        profile_0, profile_1, profile_2, profile_3 = panel_profiles
        return (
            base_z_offset,
            base_z_offset
            + profile_0["frame_height"] / 2.0
            + profile_1["frame_height"] / 2.0,
            base_z_offset
            + profile_0["frame_height"] / 2.0
            + profile_1["frame_height"]
            + profile_2["frame_height"] / 2.0,
            base_z_offset
            + profile_0["frame_height"] / 2.0
            + profile_1["frame_height"]
            + profile_2["frame_height"]
            + profile_3["frame_height"] / 2.0,
        )

    @classmethod
    def _build_components(
        cls,
        outside_inner_size,
        outside_inner_offset,
        panel_count,
        panel_profiles,
        horizontal_offsets,
        base_z_offset,
    ):
        _, frame_depth = outside_inner_size
        _, outside_offset_y = outside_inner_offset
        layer_positions = cls._layer_positions(panel_profiles, base_z_offset)
        active_panels = zip(
            panel_profiles[: int(panel_count)],
            horizontal_offsets[: int(panel_count)],
            layer_positions[: int(panel_count)],
        )
        components = []
        for panel_index, (profile, center_x, center_z) in enumerate(active_panels, start=1):
            glass_offset_x, glass_offset_y, glass_offset_z = profile["glass_offset"]
            glass_width, glass_height, glass_depth = profile["glass_size"]
            components.append(
                _panel_frame(
                    name=f"panel_{panel_index}_frame",
                    frame_width=profile["frame_width"],
                    frame_depth=frame_depth,
                    frame_thickness=profile["frame_height"],
                    glass_width=glass_width,
                    glass_height=glass_height,
                    glass_vertical_offset=glass_offset_y,
                    center=(center_x, outside_offset_y, center_z),
                )
            )
            components.append(
                _glass_pane(
                    name=f"panel_{panel_index}_glass",
                    glass_width=glass_width,
                    glass_height=glass_height,
                    glass_depth=glass_depth,
                    center=(
                        center_x + glass_offset_x,
                        outside_offset_y + glass_offset_y,
                        center_z + glass_offset_z,
                    ),
                )
            )
        return components


class VerticalSlidingWindow(ConceptTemplate):
    def __init__(
        self,
        outside_inner_size,
        outside_inner_offset,
        panel_count,
        panel_profiles,
        depth_offsets,
        base_z_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outside_inner_size=outside_inner_size,
                outside_inner_offset=outside_inner_offset,
                panel_count=panel_count,
                panel_profiles=panel_profiles,
                depth_offsets=depth_offsets,
                base_z_offset=base_z_offset,
            )
        )
        self.semantic = "Window"

    @staticmethod
    def _layer_positions(panel_profiles, base_z_offset):
        lower_profile, upper_profile = panel_profiles
        return (
            base_z_offset,
            base_z_offset
            + lower_profile["frame_height"] / 2.0
            + upper_profile["frame_height"] / 2.0,
        )

    @classmethod
    def _build_components(
        cls,
        outside_inner_size,
        outside_inner_offset,
        panel_count,
        panel_profiles,
        depth_offsets,
        base_z_offset,
    ):
        frame_width, _ = outside_inner_size
        outside_offset_x, _ = outside_inner_offset
        layer_positions = cls._layer_positions(panel_profiles, base_z_offset)
        active_panels = zip(
            panel_profiles[: int(panel_count)],
            depth_offsets[: int(panel_count)],
            layer_positions[: int(panel_count)],
        )
        components = []
        for panel_index, (profile, center_y, center_z) in enumerate(active_panels, start=1):
            glass_offset_x, glass_offset_y, glass_offset_z = profile["glass_offset"]
            glass_width, glass_height, glass_depth = profile["glass_size"]
            components.append(
                _panel_frame(
                    name=f"sliding_panel_{panel_index}_frame",
                    frame_width=frame_width,
                    frame_depth=profile["frame_depth"],
                    frame_thickness=profile["frame_height"],
                    glass_width=glass_width,
                    glass_height=glass_height,
                    glass_vertical_offset=glass_offset_y,
                    center=(outside_offset_x, center_y, center_z),
                )
            )
            components.append(
                _glass_pane(
                    name=f"sliding_panel_{panel_index}_glass",
                    glass_width=glass_width,
                    glass_height=glass_height,
                    glass_depth=glass_depth,
                    center=(
                        outside_offset_x + glass_offset_x,
                        center_y + glass_offset_y,
                        center_z + glass_offset_z,
                    ),
                )
            )
        return components


class _LayerAnchoredWindowHandle(ConceptTemplate):
    @staticmethod
    def _front_mount_z(layer_position, window_type, window_layer_heights):
        if window_type == 0:
            if layer_position == -1:
                return -window_layer_heights["layer_0"] / 2.0
            z = window_layer_heights["layer_0"] / 2.0 if layer_position >= 0 else 0.0
            if layer_position >= 1:
                z += window_layer_heights["layer_1"]
            return z

        z = window_layer_heights["layer_0"] / 2.0 if layer_position >= 0 else 0.0
        if layer_position >= 1:
            z += window_layer_heights["layer_1"]
        if layer_position >= 2:
            z += window_layer_heights["layer_2"]
        if layer_position == 3:
            z += window_layer_heights["layer_3"]
        return z

    @staticmethod
    def _rear_mount_z(layer_position, window_type, window_layer_heights):
        if window_type == 0:
            if layer_position == -1:
                return -(
                    window_layer_heights["layer_0"] / 2.0
                    + window_layer_heights["layer_2"]
                )
            z = window_layer_heights["layer_0"] / 2.0 if layer_position >= 0 else 0.0
            if layer_position >= 1:
                z += window_layer_heights["layer_0"]
            return z

        z = -window_layer_heights["layer_0"] / 2.0 if layer_position >= 0 else 0.0
        if layer_position >= 1:
            z += window_layer_heights["layer_0"]
        if layer_position >= 2:
            z += window_layer_heights["layer_1"]
        if layer_position == 3:
            z += window_layer_heights["layer_2"]
        return z

    @classmethod
    def _handle_mounts(
        cls,
        handle_mounts,
        window_type,
        window_layer_heights,
    ):
        for mount_index, mount in enumerate(handle_mounts, start=1):
            side = mount["side"]
            layer_position = mount["layer_position"]
            center_x = mount["x_offset"]
            if side == "front":
                mount_z = cls._front_mount_z(
                    layer_position,
                    window_type,
                    window_layer_heights,
                )
            else:
                mount_z = cls._rear_mount_z(
                    layer_position,
                    window_type,
                    window_layer_heights,
                )
            yield mount_index, side, center_x, mount_z


class CuboidalWindowHandle(_LayerAnchoredWindowHandle):
    def __init__(
        self,
        handle_mounts,
        window_type,
        window_layer_heights,
        handle_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                handle_mounts=handle_mounts,
                window_type=window_type,
                window_layer_heights=window_layer_heights,
                handle_size=handle_size,
            )
        )
        self.semantic = "Handle"

    @classmethod
    def _build_components(
        cls,
        handle_mounts,
        window_type,
        window_layer_heights,
        handle_size,
    ):
        handle_width, handle_height, handle_depth = handle_size
        components = []
        for mount_index, side, center_x, mount_z in cls._handle_mounts(
            handle_mounts,
            window_type,
            window_layer_heights,
        ):
            handle = Cuboid(
                height=handle_height,
                top_length=handle_width,
                top_width=handle_depth,
                position=(center_x, 0.0, mount_z),
            ).with_name(f"{side}_cuboidal_handle_{mount_index}")
            if side == "front":
                handle.move_anchor_to("back_center", (center_x, 0.0, mount_z))
            else:
                handle.move_anchor_to("front_center", (center_x, 0.0, mount_z))
            components.append(handle)
        return components


class ArchedWindowHandle(_LayerAnchoredWindowHandle):
    def __init__(
        self,
        handle_mounts,
        window_type,
        window_layer_heights,
        arch_radius,
        foot_size,
        foot_separation,
        inner_radius_extra,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                handle_mounts=handle_mounts,
                window_type=window_type,
                window_layer_heights=window_layer_heights,
                arch_radius=arch_radius,
                foot_size=foot_size,
                foot_separation=foot_separation,
                inner_radius_extra=inner_radius_extra,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _rear_mount_z(layer_position, window_type, window_layer_heights):
        if window_type == 0:
            if layer_position == -1:
                return -(
                    window_layer_heights["layer_0"] / 2.0
                    + window_layer_heights["layer_2"]
                )
            z = -window_layer_heights["layer_0"] / 2.0 if layer_position >= 0 else 0.0
            if layer_position >= 1:
                z += window_layer_heights["layer_0"]
            return z
        return _LayerAnchoredWindowHandle._rear_mount_z(
            layer_position,
            window_type,
            window_layer_heights,
        )

    @staticmethod
    def _arch_profile(arch_radius, foot_size, foot_separation, inner_radius_extra):
        foot_width, foot_height, foot_depth = foot_size
        central_angle = asin((foot_separation / 2.0 + foot_height) / arch_radius) * 2.0
        arch_offset_z = foot_depth - cos(central_angle / 2.0) * arch_radius
        inner_radius = (
            foot_separation / 2.0 / sin(central_angle / 2.0) + inner_radius_extra
        )
        return foot_width, foot_height, foot_depth, central_angle, arch_offset_z, inner_radius

    @classmethod
    def _build_components(
        cls,
        handle_mounts,
        window_type,
        window_layer_heights,
        arch_radius,
        foot_size,
        foot_separation,
        inner_radius_extra,
    ):
        (
            foot_width,
            foot_height,
            foot_depth,
            central_angle,
            arch_offset_z,
            inner_radius,
        ) = cls._arch_profile(
            arch_radius=arch_radius,
            foot_size=foot_size,
            foot_separation=foot_separation,
            inner_radius_extra=inner_radius_extra,
        )
        components = []
        for mount_index, side, center_x, mount_z in cls._handle_mounts(
            handle_mounts,
            window_type,
            window_layer_heights,
        ):
            z_sign = 1.0 if side == "front" else -1.0
            upper_foot_y = foot_separation / 2.0 + foot_height / 2.0
            lower_foot_y = -foot_separation / 2.0 - foot_height / 2.0
            upper_mount_point = (center_x, upper_foot_y, mount_z)
            lower_mount_point = (center_x, lower_foot_y, mount_z)

            upper_foot = Cuboid(
                height=foot_height,
                top_length=foot_width,
                top_width=foot_depth,
                position=(center_x, upper_foot_y, mount_z),
            ).with_name(f"{side}_upper_foot_{mount_index}")
            lower_foot = Cuboid(
                height=foot_height,
                top_length=foot_width,
                top_width=foot_depth,
                position=(center_x, lower_foot_y, mount_z),
            ).with_name(f"{side}_lower_foot_{mount_index}")
            if side == "front":
                upper_foot.move_anchor_to("back_center", upper_mount_point)
                lower_foot.move_anchor_to("back_center", lower_mount_point)
            else:
                upper_foot.move_anchor_to("front_center", upper_mount_point)
                lower_foot.move_anchor_to("front_center", lower_mount_point)

            arch_rotation_y = (
                -pi / 2.0 + central_angle / 2.0
                if side == "front"
                else pi / 2.0 + central_angle / 2.0
            )
            arch = Ring(
                height=foot_width,
                outer_top_radius=arch_radius,
                inner_top_radius=inner_radius,
                exist_angle=central_angle,
                position=(center_x, 0.0, mount_z + z_sign * arch_offset_z),
                rotation=(0.0, arch_rotation_y, pi / 2.0),
            ).with_name(f"{side}_arch_{mount_index}")
            components.extend([upper_foot, lower_foot, arch])
        return components


class LShapedWindowHandle(_LayerAnchoredWindowHandle):
    def __init__(
        self,
        handle_mounts,
        window_type,
        window_layer_heights,
        bottom_size,
        middle_size,
        top_size,
        middle_y_offset,
        top_y_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                handle_mounts=handle_mounts,
                window_type=window_type,
                window_layer_heights=window_layer_heights,
                bottom_size=bottom_size,
                middle_size=middle_size,
                top_size=top_size,
                middle_y_offset=middle_y_offset,
                top_y_offset=top_y_offset,
            )
        )
        self.semantic = "Handle"

    @classmethod
    def _build_components(
        cls,
        handle_mounts,
        window_type,
        window_layer_heights,
        bottom_size,
        middle_size,
        top_size,
        middle_y_offset,
        top_y_offset,
    ):
        bottom_width, bottom_height, bottom_depth = bottom_size
        middle_width, middle_height, middle_depth = middle_size
        top_width, top_height, top_depth = top_size
        components = []
        for mount_index, side, center_x, mount_z in cls._handle_mounts(
            handle_mounts,
            window_type,
            window_layer_heights,
        ):
            y_after_middle = middle_y_offset
            y_after_top = middle_y_offset + top_y_offset
            if side == "front":
                bottom = Cuboid(
                    height=bottom_height,
                    top_length=bottom_width,
                    top_width=bottom_depth,
                    position=(center_x, 0.0, mount_z),
                ).with_name(f"front_bottom_segment_{mount_index}")
                bottom.move_anchor_to("back_center", (center_x, 0.0, mount_z))

                middle = Cuboid(
                    height=middle_height,
                    top_length=middle_width,
                    top_width=middle_depth,
                    position=(center_x, y_after_middle, mount_z + bottom_depth),
                ).with_name(f"front_middle_segment_{mount_index}")
                middle.move_anchor_to(
                    "back_center",
                    (center_x, y_after_middle, mount_z + bottom_depth),
                )

                top = Cuboid(
                    height=top_height,
                    top_length=top_width,
                    top_width=top_depth,
                    position=(
                        center_x,
                        y_after_top,
                        mount_z + bottom_depth + middle_depth,
                    ),
                ).with_name(f"front_top_segment_{mount_index}")
                top.move_anchor_to(
                    "back_center",
                    (center_x, y_after_top, mount_z + bottom_depth + middle_depth),
                )
            else:
                bottom = Cuboid(
                    height=bottom_height,
                    top_length=bottom_width,
                    top_width=bottom_depth,
                    position=(center_x, 0.0, mount_z),
                ).with_name(f"rear_bottom_segment_{mount_index}")
                bottom.move_anchor_to("front_center", (center_x, 0.0, mount_z))

                middle = Cuboid(
                    height=middle_height,
                    top_length=middle_width,
                    top_width=middle_depth,
                    position=(center_x, y_after_middle, mount_z - bottom_depth),
                ).with_name(f"rear_middle_segment_{mount_index}")
                middle.move_anchor_to(
                    "front_center",
                    (center_x, y_after_middle, mount_z - bottom_depth),
                )

                top = Cuboid(
                    height=top_height,
                    top_length=top_width,
                    top_width=top_depth,
                    position=(
                        center_x,
                        y_after_top,
                        mount_z - bottom_depth - middle_depth,
                    ),
                ).with_name(f"rear_top_segment_{mount_index}")
                top.move_anchor_to(
                    "front_center",
                    (center_x, y_after_top, mount_z - bottom_depth - middle_depth),
                )
            components.extend([bottom, middle, top])
        return components
