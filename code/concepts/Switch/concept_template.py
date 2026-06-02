from math import pi

from code.geometry import ConceptTemplate, Cuboid, Cylinder, Rectangular_Ring


DEGREES_TO_RADIANS = pi / 180.0
SWITCH_ROTATION_ORDER = "XYZ"


class StandardSwitchBase(ConceptTemplate):
    def __init__(
        self,
        body_size,
        back_part=None,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SWITCH_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(body_size=body_size, back_part=back_part)
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(body_size, back_part):
        body_length, body_height, body_depth = body_size
        body = Cuboid(
            height=body_height,
            top_length=body_length,
            top_width=body_depth,
        ).with_name("front_base_block")
        body.move_anchor_to("front_center", (0.0, 0.0, 0.0))

        components = [body]
        if back_part is not None:
            back_length, back_height, back_depth = back_part["size"]
            offset_x, offset_y = back_part["offset"]
            back = Cuboid(
                height=back_height,
                top_length=back_length,
                top_width=back_depth,
            ).with_name("rear_base_block")
            body_back_x, body_back_y, body_back_z = body.world_anchor("back_center")
            back.move_anchor_to(
                "front_center",
                (body_back_x + offset_x, body_back_y + offset_y, body_back_z),
            )
            components.append(back)
        return components


class FrameSwitchBase(ConceptTemplate):
    def __init__(
        self,
        frame_size,
        opening_size,
        opening_offset=(0, 0),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SWITCH_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                frame_size=frame_size,
                opening_size=opening_size,
                opening_offset=opening_offset,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(frame_size, opening_size, opening_offset):
        outer_length, outer_width, frame_depth = frame_size
        opening_length, opening_width = opening_size
        opening_offset_x, opening_offset_z = opening_offset
        frame = Rectangular_Ring(
            frame_depth,
            outer_length,
            outer_width,
            opening_length,
            opening_width,
            inner_offset=(opening_offset_x, -opening_offset_z),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("rectangular_frame")
        return [frame]


class ParallelSwitchBase(ConceptTemplate):
    def __init__(
        self,
        left_block_size,
        right_block_size,
        right_block_y_offset=0.0,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SWITCH_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                left_block_size=left_block_size,
                right_block_size=right_block_size,
                right_block_y_offset=right_block_y_offset,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(left_block_size, right_block_size, right_block_y_offset):
        left_length, left_height, shared_depth = left_block_size
        right_length, right_height, right_depth = right_block_size

        left = Cuboid(
            height=left_height,
            top_length=left_length,
            top_width=shared_depth,
        ).with_name("left_parallel_block")
        left.move_anchor_to("front_right_center", (0.0, 0.0, 0.0))

        right = Cuboid(
            height=right_height,
            top_length=right_length,
            top_width=right_depth,
        ).with_name("right_parallel_block")
        right.move_anchor_to("front_left_center", (0.0, right_block_y_offset, 0.0))

        return [left, right]


class CylindricalSwitchKnob(ConceptTemplate):
    def __init__(
        self,
        knob_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SWITCH_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(self._build_components(knob_size=knob_size))
        self.semantic = "Knob"

    @staticmethod
    def _build_components(knob_size):
        radius, depth = knob_size
        knob = Cylinder(
            height=depth,
            top_radius=radius,
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("cylindrical_knob")
        knob.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        return [knob]


class RoundButtonSwitch(ConceptTemplate):
    def __init__(
        self,
        button_size,
        button_xy_centers,
        center_depth_offset,
        tilt_degrees=0.0,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SWITCH_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                button_size=button_size,
                button_xy_centers=button_xy_centers,
                center_depth_offset=center_depth_offset,
                tilt_degrees=tilt_degrees,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(
        button_size,
        button_xy_centers,
        center_depth_offset,
        tilt_degrees,
    ):
        radius, depth = button_size
        tilt = tilt_degrees * DEGREES_TO_RADIANS
        components = []
        for button_index, center in enumerate(button_xy_centers, start=1):
            center_x, center_y = center
            components.append(
                Cylinder(
                    height=depth,
                    top_radius=radius,
                    position=(center_x, center_y, center_depth_offset),
                    rotation=(pi / 2.0 + tilt, 0.0, 0.0),
                ).with_name(f"round_button_{button_index}")
            )
        return components


class FlipXSwitch(ConceptTemplate):
    def __init__(
        self,
        switch_size,
        switch_count,
        center_spacing,
        tilt_degrees=0.0,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SWITCH_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                switch_size=switch_size,
                switch_count=switch_count,
                center_spacing=center_spacing,
                tilt_degrees=tilt_degrees,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(switch_size, switch_count, center_spacing, tilt_degrees):
        switch_length, switch_height, switch_depth = switch_size
        tilt = tilt_degrees * DEGREES_TO_RADIANS
        components = []
        for switch_index in range(int(switch_count)):
            components.append(
                Cuboid(
                    height=switch_height,
                    top_length=switch_length,
                    top_width=switch_depth,
                    position=(center_spacing * switch_index, 0.0, 0.0),
                    rotation=(tilt, 0.0, 0.0),
                ).with_name(f"flip_x_switch_{switch_index + 1}")
            )
        return components


class FlipYSwitch(ConceptTemplate):
    def __init__(
        self,
        switch_size,
        switch_count,
        center_spacing,
        tilt_degrees=0.0,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SWITCH_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                switch_size=switch_size,
                switch_count=switch_count,
                center_spacing=center_spacing,
                tilt_degrees=tilt_degrees,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(switch_size, switch_count, center_spacing, tilt_degrees):
        switch_length, switch_height, switch_depth = switch_size
        tilt = tilt_degrees * DEGREES_TO_RADIANS
        components = []
        for switch_index in range(int(switch_count)):
            components.append(
                Cuboid(
                    height=switch_height,
                    top_length=switch_length,
                    top_width=switch_depth,
                    position=(center_spacing * switch_index, 0.0, 0.0),
                    rotation=(0.0, tilt, 0.0),
                ).with_name(f"flip_y_switch_{switch_index + 1}")
            )
        return components


class LeverSwitch(ConceptTemplate):
    def __init__(
        self,
        base_size,
        lever_size,
        lever_mount_offset=(0, 0, 0),
        switch_count=1,
        center_spacing=0.0,
        lever_tilt_degrees=0.0,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SWITCH_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                base_size=base_size,
                lever_size=lever_size,
                lever_mount_offset=lever_mount_offset,
                switch_count=switch_count,
                center_spacing=center_spacing,
                lever_tilt_degrees=lever_tilt_degrees,
            )
        )
        self.semantic = "Switch"

    @staticmethod
    def _build_components(
        base_size,
        lever_size,
        lever_mount_offset,
        switch_count,
        center_spacing,
        lever_tilt_degrees,
    ):
        base_radius, base_depth = base_size
        lever_bottom_radius, lever_top_radius, lever_length = lever_size
        mount_offset_x, mount_offset_y, mount_offset_z = lever_mount_offset
        lever_tilt = lever_tilt_degrees * DEGREES_TO_RADIANS
        components = []

        for switch_index in range(int(switch_count)):
            switch_center_x = center_spacing * switch_index
            base = Cylinder(
                height=base_depth,
                top_radius=base_radius,
                rotation=(pi / 2.0, 0.0, 0.0),
            ).with_name(f"lever_base_{switch_index + 1}")
            base.move_anchor_to("bottom_center", (switch_center_x, 0.0, 0.0))
            components.append(base)

            lever = Cylinder(
                height=lever_length,
                top_radius=lever_top_radius,
                bottom_radius=lever_bottom_radius,
                rotation=(pi / 2.0 + lever_tilt, 0.0, 0.0),
            ).with_name(f"lever_stem_{switch_index + 1}")
            base_top_x, base_top_y, base_top_z = base.world_anchor("top_center")
            lever.move_anchor_to(
                "bottom_center",
                (
                    base_top_x + mount_offset_x,
                    base_top_y + mount_offset_y,
                    base_top_z + mount_offset_z,
                ),
            )
            components.append(lever)

        return components


class CuboidalPlugGrid(ConceptTemplate):
    def __init__(
        self,
        contact_size,
        column_count,
        row_count,
        contact_interval=(0, 0),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SWITCH_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                contact_size=contact_size,
                column_count=column_count,
                row_count=row_count,
                contact_interval=contact_interval,
            )
        )
        self.semantic = "Plug"

    @staticmethod
    def _build_components(contact_size, column_count, row_count, contact_interval):
        contact_length, contact_height, contact_depth = contact_size
        interval_x, interval_y = contact_interval
        step_x = interval_x + contact_length
        step_y = interval_y + contact_height
        components = []

        for row_index in range(int(row_count)):
            for column_index in range(int(column_count)):
                contact = Cuboid(
                    height=contact_height,
                    top_length=contact_length,
                    top_width=contact_depth,
                ).with_name(f"cuboidal_contact_{row_index + 1}_{column_index + 1}")
                contact.move_anchor_to(
                    "front_center",
                    (step_x * column_index, step_y * row_index, 0.0),
                )
                components.append(contact)
        return components


class ThreeProngPlug(ConceptTemplate):
    def __init__(
        self,
        prong_size,
        side_prong_offset,
        center_rotation_degrees=0.0,
        side_spread_degrees=0.0,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SWITCH_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                prong_size=prong_size,
                side_prong_offset=side_prong_offset,
                center_rotation_degrees=center_rotation_degrees,
                side_spread_degrees=side_spread_degrees,
            )
        )
        self.semantic = "Plug"

    @staticmethod
    def _build_components(
        prong_size,
        side_prong_offset,
        center_rotation_degrees,
        side_spread_degrees,
    ):
        prong_length, prong_height, prong_depth = prong_size
        side_offset_x, side_offset_y = side_prong_offset
        center_rotation = center_rotation_degrees * DEGREES_TO_RADIANS
        side_spread = side_spread_degrees * DEGREES_TO_RADIANS

        center = Cuboid(
            height=prong_height,
            top_length=prong_length,
            top_width=prong_depth,
            rotation=(0.0, 0.0, center_rotation),
        ).with_name("center_prong")
        center.move_anchor_to("front_center", (0.0, 0.0, 0.0))

        left = Cuboid(
            height=prong_height,
            top_length=prong_length,
            top_width=prong_depth,
            rotation=(0.0, 0.0, side_spread),
        ).with_name("left_side_prong")
        left.move_anchor_to("front_center", (-side_offset_x, side_offset_y, 0.0))
        left.rotate_about_point((0.0, 0.0, 0.0), (0.0, 0.0, center_rotation))

        right = Cuboid(
            height=prong_height,
            top_length=prong_length,
            top_width=prong_depth,
            rotation=(0.0, 0.0, -side_spread),
        ).with_name("right_side_prong")
        right.move_anchor_to("front_center", (side_offset_x, side_offset_y, 0.0))
        right.rotate_about_point((0.0, 0.0, 0.0), (0.0, 0.0, center_rotation))

        return [center, left, right]


class CylindricalPlugGrid(ConceptTemplate):
    def __init__(
        self,
        contact_size,
        column_count,
        row_count,
        contact_interval=(0, 0),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SWITCH_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                contact_size=contact_size,
                column_count=column_count,
                row_count=row_count,
                contact_interval=contact_interval,
            )
        )
        self.semantic = "Plug"

    @staticmethod
    def _build_components(contact_size, column_count, row_count, contact_interval):
        contact_radius, contact_depth = contact_size
        interval_x, interval_y = contact_interval
        step_x = interval_x + contact_radius * 2.0
        step_y = interval_y + contact_radius * 2.0
        components = []

        for row_index in range(int(row_count)):
            for column_index in range(int(column_count)):
                contact = Cylinder(
                    height=contact_depth,
                    top_radius=contact_radius,
                    rotation=(pi / 2.0, 0.0, 0.0),
                ).with_name(f"cylindrical_contact_{row_index + 1}_{column_index + 1}")
                contact.move_anchor_to(
                    "top_center",
                    (step_x * column_index, step_y * row_index, 0.0),
                )
                components.append(contact)
        return components
