from math import pi

from code.geometry_rewritten import ConceptTemplate, Cuboid, Cylinder, Sphere


DEGREES_TO_RADIANS = pi / 180.0
DOOR_OFFSET_FIRST_ROTATION_ORDER = "YXZ"


class PivotDoorPanelSet(ConceptTemplate):
    def __init__(
        self,
        has_left_panel,
        has_right_panel,
        panel_size,
        open_angles_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DOOR_OFFSET_FIRST_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                has_left_panel=has_left_panel,
                has_right_panel=has_right_panel,
                panel_size=panel_size,
                open_angles_degrees=open_angles_degrees,
            )
        )
        self.semantic = "Door"

    @staticmethod
    def _build_components(
        has_left_panel,
        has_right_panel,
        panel_size,
        open_angles_degrees,
    ):
        panel_width, panel_height, panel_depth = panel_size
        left_open_degrees, right_open_degrees = open_angles_degrees
        left_open_angle = -left_open_degrees * DEGREES_TO_RADIANS
        right_open_angle = right_open_degrees * DEGREES_TO_RADIANS

        components = []
        if has_left_panel and has_right_panel:
            components.append(
                PivotDoorPanelSet._panel(
                    name="left_panel",
                    panel_width=panel_width,
                    panel_height=panel_height,
                    panel_depth=panel_depth,
                    closed_center_x=-panel_width / 2.0,
                    pivot_x=-panel_width,
                    open_angle=left_open_angle,
                )
            )
            components.append(
                PivotDoorPanelSet._panel(
                    name="right_panel",
                    panel_width=panel_width,
                    panel_height=panel_height,
                    panel_depth=panel_depth,
                    closed_center_x=panel_width / 2.0,
                    pivot_x=panel_width,
                    open_angle=right_open_angle,
                )
            )
        elif has_left_panel:
            components.append(
                PivotDoorPanelSet._panel(
                    name="left_panel",
                    panel_width=panel_width,
                    panel_height=panel_height,
                    panel_depth=panel_depth,
                    closed_center_x=0.0,
                    pivot_x=-panel_width / 2.0,
                    open_angle=left_open_angle,
                )
            )
        elif has_right_panel:
            components.append(
                PivotDoorPanelSet._panel(
                    name="right_panel",
                    panel_width=panel_width,
                    panel_height=panel_height,
                    panel_depth=panel_depth,
                    closed_center_x=0.0,
                    pivot_x=panel_width / 2.0,
                    open_angle=right_open_angle,
                )
            )

        return components

    @staticmethod
    def _panel(
        name,
        panel_width,
        panel_height,
        panel_depth,
        closed_center_x,
        pivot_x,
        open_angle,
    ):
        panel = Cuboid(
            height=panel_height,
            top_length=panel_width,
            top_width=panel_depth,
            position=(closed_center_x, 0.0, 0.0),
        ).with_name(name)
        panel.rotate_about_point((pivot_x, 0.0, 0.0), (0.0, open_angle, 0.0))
        return panel


class ThreeSideDoorFrame(ConceptTemplate):
    def __init__(
        self,
        opening_size,
        has_front_frame,
        has_back_frame,
        main_outer_size,
        main_inner_offset,
        main_center_offset,
        front_outer_size,
        front_inner_size,
        front_inner_offset,
        front_center_offset,
        back_outer_size,
        back_inner_size,
        back_inner_offset,
        back_center_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DOOR_OFFSET_FIRST_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                opening_size=opening_size,
                has_front_frame=has_front_frame,
                has_back_frame=has_back_frame,
                main_outer_size=main_outer_size,
                main_inner_offset=main_inner_offset,
                main_center_offset=main_center_offset,
                front_outer_size=front_outer_size,
                front_inner_size=front_inner_size,
                front_inner_offset=front_inner_offset,
                front_center_offset=front_center_offset,
                back_outer_size=back_outer_size,
                back_inner_size=back_inner_size,
                back_inner_offset=back_inner_offset,
                back_center_offset=back_center_offset,
            )
        )
        self.semantic = "Doorframe"

    @staticmethod
    def _build_components(
        opening_size,
        has_front_frame,
        has_back_frame,
        main_outer_size,
        main_inner_offset,
        main_center_offset,
        front_outer_size,
        front_inner_size,
        front_inner_offset,
        front_center_offset,
        back_outer_size,
        back_inner_size,
        back_inner_offset,
        back_center_offset,
    ):
        opening_width, opening_height, _ = opening_size
        main_offset_x, main_offset_z = main_center_offset
        _, _, main_outer_depth = main_outer_size
        _, main_inner_offset_y = main_inner_offset

        components = []
        components.extend(
            ThreeSideDoorFrame._three_side_frame(
                name_prefix="main",
                inner_width=opening_width,
                inner_height=opening_height,
                outer_size=main_outer_size,
                inner_offset=main_inner_offset,
                frame_center_x=main_offset_x,
                inner_bottom_y=-opening_height / 2.0 + main_inner_offset_y,
                inner_top_y=opening_height / 2.0,
                frame_center_z=main_offset_z,
            )
        )

        if has_front_frame:
            front_offset_x, front_offset_y = front_center_offset
            _, _, front_outer_depth = front_outer_size
            front_inner_width, front_inner_height = front_inner_size
            _, front_inner_offset_y = front_inner_offset
            front_center_z = main_offset_z + main_outer_depth / 2.0 - front_outer_depth / 2.0
            components.extend(
                ThreeSideDoorFrame._three_side_frame(
                    name_prefix="front",
                    inner_width=front_inner_width,
                    inner_height=front_inner_height,
                    outer_size=front_outer_size,
                    inner_offset=front_inner_offset,
                    frame_center_x=front_offset_x,
                    inner_bottom_y=front_offset_y
                    - opening_height / 2.0
                    + front_inner_offset_y,
                    inner_top_y=front_offset_y - opening_height / 2.0 + front_inner_height,
                    frame_center_z=front_center_z,
                )
            )

        if has_back_frame:
            back_offset_x, back_offset_y = back_center_offset
            back_inner_width, back_inner_height = back_inner_size
            _, back_inner_offset_y = back_inner_offset
            _, _, back_outer_depth = back_outer_size
            back_center_z = main_offset_z - main_outer_depth / 2.0 - back_outer_depth / 2.0
            components.extend(
                ThreeSideDoorFrame._three_side_frame(
                    name_prefix="back",
                    inner_width=back_inner_width,
                    inner_height=back_inner_height,
                    outer_size=back_outer_size,
                    inner_offset=back_inner_offset,
                    frame_center_x=back_offset_x,
                    inner_bottom_y=back_offset_y
                    - opening_height / 2.0
                    + back_inner_offset_y,
                    inner_top_y=back_offset_y - opening_height / 2.0 + back_inner_height,
                    frame_center_z=back_center_z,
                )
            )

        return components

    @staticmethod
    def _three_side_frame(
        name_prefix,
        inner_width,
        inner_height,
        outer_size,
        inner_offset,
        frame_center_x,
        inner_bottom_y,
        inner_top_y,
        frame_center_z,
    ):
        outer_width, outer_height, outer_depth = outer_size
        inner_offset_x, inner_offset_y = inner_offset
        top_height = outer_height + inner_offset_y - inner_height
        left_width = (outer_width - inner_width) / 2.0 - inner_offset_x
        right_width = (outer_width - inner_width) / 2.0 + inner_offset_x
        inner_left_x = frame_center_x - inner_width / 2.0
        inner_right_x = frame_center_x + inner_width / 2.0

        top = Cuboid(
            height=top_height,
            top_length=inner_width,
            top_width=outer_depth,
        ).with_name(f"{name_prefix}_top_beam")
        top.move_anchor_to(
            "bottom_center",
            (frame_center_x, inner_top_y, frame_center_z),
        )

        left = Cuboid(
            height=outer_height,
            top_length=left_width,
            top_width=outer_depth,
        ).with_name(f"{name_prefix}_left_beam")
        left.move_anchor_to(
            "bottom_right_center",
            (inner_left_x, inner_bottom_y, frame_center_z),
        )

        right = Cuboid(
            height=outer_height,
            top_length=right_width,
            top_width=outer_depth,
        ).with_name(f"{name_prefix}_right_beam")
        right.move_anchor_to(
            "bottom_left_center",
            (inner_right_x, inner_bottom_y, frame_center_z),
        )

        return [top, left, right]


class VerticalDoorHingeSet(ConceptTemplate):
    def __init__(
        self,
        hinge_group_count,
        hinge_count_per_group,
        hinge_size,
        hinge_separations,
        group_offsets,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                hinge_group_count=hinge_group_count,
                hinge_count_per_group=hinge_count_per_group,
                hinge_size=hinge_size,
                hinge_separations=hinge_separations,
                group_offsets=group_offsets,
            )
        )
        self.semantic = "Hinge"

    @staticmethod
    def _build_components(
        hinge_group_count,
        hinge_count_per_group,
        hinge_size,
        hinge_separations,
        group_offsets,
    ):
        hinge_radius, hinge_height = hinge_size
        group_count = int(hinge_group_count)
        hinge_count = int(hinge_count_per_group)
        components = []

        for group_index in range(group_count):
            offset_x, offset_y, offset_z = group_offsets[group_index]
            next_hinge_bottom_y = offset_y
            for hinge_index in range(hinge_count):
                hinge = Cylinder(
                    height=hinge_height,
                    top_radius=hinge_radius,
                ).with_name(f"hinge_{group_index + 1}_{hinge_index + 1}")
                hinge.move_anchor_to(
                    "bottom_center",
                    (offset_x, next_hinge_bottom_y, offset_z),
                )
                components.append(hinge)

                separation = 0.0
                if hinge_index < len(hinge_separations):
                    separation = hinge_separations[hinge_index]
                next_hinge_bottom_y += hinge_height + separation

        return components


class LDoorHandle(ConceptTemplate):
    def __init__(
        self,
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_size,
        has_back_handle,
        has_front_handle,
        fixed_part_size,
        vertical_part_size,
        horizontal_part_size,
        moving_part_offset,
        edge_offset_x,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                has_left_panel=has_left_panel,
                has_right_panel=has_right_panel,
                panel_open_angles_degrees=panel_open_angles_degrees,
                door_size=door_size,
                has_back_handle=has_back_handle,
                has_front_handle=has_front_handle,
                fixed_part_size=fixed_part_size,
                vertical_part_size=vertical_part_size,
                horizontal_part_size=horizontal_part_size,
                moving_part_offset=moving_part_offset,
                edge_offset_x=edge_offset_x,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _mount_settings(
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_width,
        has_back_handle,
        has_front_handle,
    ):
        left_open_degrees, right_open_degrees = panel_open_angles_degrees
        panel_settings = (
            (has_left_panel, -1.0, -door_width / 2.0, -left_open_degrees),
            (has_right_panel, 1.0, door_width / 2.0, right_open_degrees),
        )
        handle_settings = (
            (has_back_handle, -1.0),
            (has_front_handle, 1.0),
        )
        is_double_panel = has_left_panel and has_right_panel

        settings = []
        for panel_enabled, x_direction, hinge_seed_x, open_degrees in panel_settings:
            if not panel_enabled:
                continue
            if is_double_panel:
                mount_origin_x = hinge_seed_x
                pivot_x = hinge_seed_x * 2.0
            else:
                mount_origin_x = 0.0
                pivot_x = hinge_seed_x
            for handle_enabled, normal_direction_z in handle_settings:
                if handle_enabled:
                    settings.append(
                        (
                            x_direction,
                            mount_origin_x,
                            normal_direction_z,
                            pivot_x,
                            open_degrees * DEGREES_TO_RADIANS,
                        )
                    )
        return settings

    @staticmethod
    def _build_components(
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_size,
        has_back_handle,
        has_front_handle,
        fixed_part_size,
        vertical_part_size,
        horizontal_part_size,
        moving_part_offset,
        edge_offset_x,
    ):
        door_width, _, door_depth = door_size
        fixed_length, fixed_height, fixed_depth = fixed_part_size
        vertical_length, vertical_height, vertical_depth = vertical_part_size
        horizontal_length, horizontal_height, horizontal_depth = horizontal_part_size
        moving_offset_x, moving_offset_y = moving_part_offset

        components = []
        for setting in LDoorHandle._mount_settings(
            has_left_panel,
            has_right_panel,
            panel_open_angles_degrees,
            door_width,
            has_back_handle,
            has_front_handle,
        ):
            x_direction, mount_origin_x, normal_direction_z, pivot_x, open_angle = setting
            surface_z = normal_direction_z * door_depth / 2.0
            inward_anchor = "back_center" if normal_direction_z > 0 else "front_center"

            base_center_x = mount_origin_x - x_direction * edge_offset_x
            base = Cuboid(
                height=fixed_height,
                top_length=fixed_length,
                top_width=fixed_depth,
                position=(base_center_x, 0.0, 0.0),
            ).with_name("fixed_base")
            base.move_anchor_to(inward_anchor, (base_center_x, 0.0, surface_z))

            vertical_center_x = mount_origin_x + moving_offset_x - x_direction * edge_offset_x
            vertical = Cuboid(
                height=vertical_height,
                top_length=vertical_length,
                top_width=vertical_depth,
                position=(vertical_center_x, moving_offset_y, 0.0),
            ).with_name("vertical_grip")
            vertical.move_anchor_to(
                inward_anchor,
                (
                    vertical_center_x,
                    moving_offset_y,
                    normal_direction_z * (door_depth / 2.0 + fixed_depth),
                ),
            )

            horizontal_center_x = mount_origin_x + moving_offset_x + x_direction * (
                -edge_offset_x + (horizontal_length - vertical_length) / 2.0
            )
            horizontal = Cuboid(
                height=horizontal_height,
                top_length=horizontal_length,
                top_width=horizontal_depth,
                position=(horizontal_center_x, moving_offset_y, 0.0),
            ).with_name("horizontal_grip")
            horizontal.move_anchor_to(
                inward_anchor,
                (
                    horizontal_center_x,
                    moving_offset_y,
                    normal_direction_z
                    * (door_depth / 2.0 + fixed_depth + vertical_depth),
                ),
            )

            for part in (base, vertical, horizontal):
                part.rotate_about_point((pivot_x, 0.0, 0.0), (0.0, open_angle, 0.0))
                components.append(part)

        return components


class PiDoorHandle(ConceptTemplate):
    def __init__(
        self,
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_size,
        has_back_handle,
        has_front_handle,
        main_bar_size,
        foot_size,
        foot_separation,
        main_bar_y_offset,
        edge_offset_x,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                has_left_panel=has_left_panel,
                has_right_panel=has_right_panel,
                panel_open_angles_degrees=panel_open_angles_degrees,
                door_size=door_size,
                has_back_handle=has_back_handle,
                has_front_handle=has_front_handle,
                main_bar_size=main_bar_size,
                foot_size=foot_size,
                foot_separation=foot_separation,
                main_bar_y_offset=main_bar_y_offset,
                edge_offset_x=edge_offset_x,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _mount_settings(
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_width,
        has_back_handle,
        has_front_handle,
    ):
        left_open_degrees, right_open_degrees = panel_open_angles_degrees
        panel_settings = (
            (has_left_panel, -1.0, -door_width / 2.0, -left_open_degrees),
            (has_right_panel, 1.0, door_width / 2.0, right_open_degrees),
        )
        handle_settings = (
            (has_back_handle, 1.0),
            (has_front_handle, -1.0),
        )
        is_double_panel = has_left_panel and has_right_panel

        settings = []
        for panel_enabled, x_direction, hinge_seed_x, open_degrees in panel_settings:
            if not panel_enabled:
                continue
            if is_double_panel:
                mount_origin_x = hinge_seed_x
                pivot_x = hinge_seed_x * 2.0
            else:
                mount_origin_x = 0.0
                pivot_x = hinge_seed_x
            for handle_enabled, normal_direction_z in handle_settings:
                if handle_enabled:
                    settings.append(
                        (
                            x_direction,
                            mount_origin_x,
                            normal_direction_z,
                            pivot_x,
                            open_degrees * DEGREES_TO_RADIANS,
                        )
                    )
        return settings

    @staticmethod
    def _build_components(
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_size,
        has_back_handle,
        has_front_handle,
        main_bar_size,
        foot_size,
        foot_separation,
        main_bar_y_offset,
        edge_offset_x,
    ):
        door_width, _, door_depth = door_size
        main_length, main_height, main_depth = main_bar_size
        foot_length, foot_height, foot_depth = foot_size

        components = []
        for setting in PiDoorHandle._mount_settings(
            has_left_panel,
            has_right_panel,
            panel_open_angles_degrees,
            door_width,
            has_back_handle,
            has_front_handle,
        ):
            x_direction, mount_origin_x, normal_direction_z, pivot_x, open_angle = setting
            surface_z = normal_direction_z * door_depth / 2.0
            inward_anchor = "back_center" if normal_direction_z > 0 else "front_center"

            foot_center_x = mount_origin_x + x_direction * edge_offset_x
            bottom_foot = Cuboid(
                height=foot_height,
                top_length=foot_length,
                top_width=foot_depth,
                position=(foot_center_x, 0.0, 0.0),
            ).with_name("bottom_foot")
            bottom_foot.move_anchor_to(inward_anchor, (foot_center_x, 0.0, surface_z))

            top_foot_y = foot_separation + foot_height
            top_foot = Cuboid(
                height=foot_height,
                top_length=foot_length,
                top_width=foot_depth,
                position=(foot_center_x, top_foot_y, 0.0),
            ).with_name("top_foot")
            top_foot.move_anchor_to(inward_anchor, (foot_center_x, top_foot_y, surface_z))

            main_center_y = main_bar_y_offset + foot_separation / 2.0 + foot_height / 2.0
            main_bar = Cuboid(
                height=main_height,
                top_length=main_length,
                top_width=main_depth,
                position=(foot_center_x, main_center_y, 0.0),
            ).with_name("outer_bar")
            main_bar.move_anchor_to(
                inward_anchor,
                (
                    foot_center_x,
                    main_center_y,
                    normal_direction_z * (door_depth / 2.0 + foot_depth),
                ),
            )

            for part in (top_foot, bottom_foot, main_bar):
                part.rotate_about_point((pivot_x, 0.0, 0.0), (0.0, open_angle, 0.0))
                components.append(part)

        return components


class CylindricalDoorHandle(ConceptTemplate):
    def __init__(
        self,
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_size,
        has_back_handle,
        has_front_handle,
        fixed_part_size,
        middle_part_size,
        main_part_size,
        edge_offset_x,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                has_left_panel=has_left_panel,
                has_right_panel=has_right_panel,
                panel_open_angles_degrees=panel_open_angles_degrees,
                door_size=door_size,
                has_back_handle=has_back_handle,
                has_front_handle=has_front_handle,
                fixed_part_size=fixed_part_size,
                middle_part_size=middle_part_size,
                main_part_size=main_part_size,
                edge_offset_x=edge_offset_x,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _mount_settings(
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_width,
        has_back_handle,
        has_front_handle,
    ):
        left_open_degrees, right_open_degrees = panel_open_angles_degrees
        panel_settings = (
            (has_left_panel, -1.0, -door_width / 2.0, -left_open_degrees),
            (has_right_panel, 1.0, door_width / 2.0, right_open_degrees),
        )
        handle_settings = (
            (has_back_handle, -1.0),
            (has_front_handle, 1.0),
        )
        is_double_panel = has_left_panel and has_right_panel

        settings = []
        for panel_enabled, x_direction, hinge_seed_x, open_degrees in panel_settings:
            if not panel_enabled:
                continue
            if is_double_panel:
                mount_origin_x = hinge_seed_x
                pivot_x = hinge_seed_x * 2.0
            else:
                mount_origin_x = 0.0
                pivot_x = hinge_seed_x
            for handle_enabled, normal_direction_z in handle_settings:
                if handle_enabled:
                    settings.append(
                        (
                            x_direction,
                            mount_origin_x,
                            normal_direction_z,
                            pivot_x,
                            open_degrees * DEGREES_TO_RADIANS,
                        )
                    )
        return settings

    @staticmethod
    def _build_components(
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_size,
        has_back_handle,
        has_front_handle,
        fixed_part_size,
        middle_part_size,
        main_part_size,
        edge_offset_x,
    ):
        door_width, _, door_depth = door_size
        fixed_radius, fixed_length = fixed_part_size
        middle_radius, middle_length = middle_part_size
        main_radius, main_length = main_part_size

        components = []
        for setting in CylindricalDoorHandle._mount_settings(
            has_left_panel,
            has_right_panel,
            panel_open_angles_degrees,
            door_width,
            has_back_handle,
            has_front_handle,
        ):
            x_direction, mount_origin_x, normal_direction_z, pivot_x, open_angle = setting
            handle_center_x = mount_origin_x - x_direction * edge_offset_x
            surface_point = (handle_center_x, 0.0, normal_direction_z * door_depth / 2.0)
            inward_anchor = "bottom_center" if normal_direction_z > 0 else "top_center"
            outward_anchor = "top_center" if normal_direction_z > 0 else "bottom_center"

            base = Cylinder(
                height=fixed_length,
                top_radius=fixed_radius,
                rotation=(pi / 2.0, 0.0, 0.0),
            ).with_name("fixed_cylinder_base")
            base.move_anchor_to(inward_anchor, surface_point)

            middle = Cylinder(
                height=middle_length,
                top_radius=middle_radius,
                rotation=(pi / 2.0, 0.0, 0.0),
            ).with_name("middle_cylinder")
            middle.move_anchor_to(inward_anchor, base.world_anchor(outward_anchor))

            main = Cylinder(
                height=main_length,
                top_radius=main_radius,
                rotation=(pi / 2.0, 0.0, 0.0),
            ).with_name("main_cylinder_grip")
            main.move_anchor_to(inward_anchor, middle.world_anchor(outward_anchor))

            for part in (base, middle, main):
                part.rotate_about_point((pivot_x, 0.0, 0.0), (0.0, open_angle, 0.0))
                components.append(part)

        return components


class SphericalDoorHandle(ConceptTemplate):
    def __init__(
        self,
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_size,
        has_back_handle,
        has_front_handle,
        fixed_part_size,
        middle_part_size,
        knob_size,
        edge_offset_x,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                has_left_panel=has_left_panel,
                has_right_panel=has_right_panel,
                panel_open_angles_degrees=panel_open_angles_degrees,
                door_size=door_size,
                has_back_handle=has_back_handle,
                has_front_handle=has_front_handle,
                fixed_part_size=fixed_part_size,
                middle_part_size=middle_part_size,
                knob_size=knob_size,
                edge_offset_x=edge_offset_x,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _mount_settings(
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_width,
        has_back_handle,
        has_front_handle,
    ):
        left_open_degrees, right_open_degrees = panel_open_angles_degrees
        panel_settings = (
            (has_left_panel, -1.0, -door_width / 2.0, -left_open_degrees),
            (has_right_panel, 1.0, door_width / 2.0, right_open_degrees),
        )
        handle_settings = (
            (has_back_handle, -1.0),
            (has_front_handle, 1.0),
        )
        is_double_panel = has_left_panel and has_right_panel

        settings = []
        for panel_enabled, x_direction, hinge_seed_x, open_degrees in panel_settings:
            if not panel_enabled:
                continue
            if is_double_panel:
                mount_origin_x = hinge_seed_x
                pivot_x = hinge_seed_x * 2.0
            else:
                mount_origin_x = 0.0
                pivot_x = hinge_seed_x
            for handle_enabled, normal_direction_z in handle_settings:
                if handle_enabled:
                    settings.append(
                        (
                            x_direction,
                            mount_origin_x,
                            normal_direction_z,
                            pivot_x,
                            open_degrees * DEGREES_TO_RADIANS,
                        )
                    )
        return settings

    @staticmethod
    def _build_components(
        has_left_panel,
        has_right_panel,
        panel_open_angles_degrees,
        door_size,
        has_back_handle,
        has_front_handle,
        fixed_part_size,
        middle_part_size,
        knob_size,
        edge_offset_x,
    ):
        door_width, _, door_depth = door_size
        fixed_radius, fixed_length = fixed_part_size
        middle_radius, middle_length = middle_part_size
        knob_radius_x, knob_radius_y, knob_radius_z = knob_size

        components = []
        for setting in SphericalDoorHandle._mount_settings(
            has_left_panel,
            has_right_panel,
            panel_open_angles_degrees,
            door_width,
            has_back_handle,
            has_front_handle,
        ):
            x_direction, mount_origin_x, normal_direction_z, pivot_x, open_angle = setting
            handle_center_x = mount_origin_x - x_direction * edge_offset_x
            surface_point = (handle_center_x, 0.0, normal_direction_z * door_depth / 2.0)
            inward_anchor = "bottom_center" if normal_direction_z > 0 else "top_center"
            outward_anchor = "top_center" if normal_direction_z > 0 else "bottom_center"

            base = Cylinder(
                height=fixed_length,
                top_radius=fixed_radius,
                rotation=(pi / 2.0, 0.0, 0.0),
            ).with_name("fixed_cylinder_base")
            base.move_anchor_to(inward_anchor, surface_point)

            middle = Cylinder(
                height=middle_length,
                top_radius=middle_radius,
                rotation=(pi / 2.0, 0.0, 0.0),
            ).with_name("middle_cylinder")
            middle.move_anchor_to(inward_anchor, base.world_anchor(outward_anchor))

            knob = Sphere(
                radius=knob_radius_x,
                radius_y=knob_radius_y,
                radius_z=knob_radius_z,
            ).with_name("spherical_knob")
            contact_offset_z = -normal_direction_z * knob_radius_y / 2.0
            knob.move_local_point_to(
                (0.0, 0.0, contact_offset_z),
                middle.world_anchor(outward_anchor),
            )

            for part in (base, middle, knob):
                part.rotate_about_point((pivot_x, 0.0, 0.0), (0.0, open_angle, 0.0))
                components.append(part)

        return components
