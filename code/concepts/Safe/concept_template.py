from math import cos, pi, sin

from code.geometry import (
    ConceptTemplate,
    Cuboid,
    Cylinder,
    Rectangular_Ring,
    Ring,
    radial_array_frames,
)


DEGREES_TO_RADIANS = pi / 180.0
HANDLE_ROTATION_ORDER = "ZXY"


class CuboidalSafeBody(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        wall_thickness,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                wall_thickness=wall_thickness,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(outer_size, wall_thickness):
        outer_length, outer_height, outer_depth = outer_size
        lower_wall, upper_wall, left_wall, right_wall, back_depth = wall_thickness
        front_depth = outer_depth - back_depth
        inner_length = outer_length - left_wall - right_wall
        inner_height = outer_height - lower_wall - upper_wall
        inner_offset_x = (right_wall - left_wall) / 2.0
        inner_offset_y = (upper_wall - lower_wall) / 2.0

        back_panel = Cuboid(
            height=outer_height,
            top_length=outer_length,
            top_width=back_depth,
        ).with_name("back_panel")
        back_panel.move_anchor_to("back_center", (0.0, 0.0, -outer_depth / 2.0))

        front_frame = Rectangular_Ring(
            front_height=front_depth,
            outer_top_length=outer_length,
            outer_top_width=outer_height,
            inner_top_length=inner_length,
            inner_top_width=inner_height,
            inner_offset=(inner_offset_x, -inner_offset_y),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("front_hollow_frame")
        front_frame.move_anchor_to(
            "outer_bottom_center",
            back_panel.world_anchor("front_center"),
        )

        return [back_panel, front_frame]


class MultiLayerSafeBody(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        wall_thickness,
        main_clapboard_size,
        main_clapboard_offset_y,
        sub_clapboards,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                wall_thickness=wall_thickness,
                main_clapboard_size=main_clapboard_size,
                main_clapboard_offset_y=main_clapboard_offset_y,
                sub_clapboards=sub_clapboards,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(
        outer_size,
        wall_thickness,
        main_clapboard_size,
        main_clapboard_offset_y,
        sub_clapboards,
    ):
        outer_length, outer_height, outer_depth = outer_size
        lower_wall, upper_wall, left_wall, right_wall, back_depth = wall_thickness
        front_depth = outer_depth - back_depth
        inner_length = outer_length - left_wall - right_wall
        inner_height = outer_height - lower_wall - upper_wall
        inner_center_x = (right_wall - left_wall) / 2.0
        inner_center_y = (upper_wall - lower_wall) / 2.0
        inner_back_z = -outer_depth / 2.0 + back_depth

        back_panel = Cuboid(
            height=outer_height,
            top_length=outer_length,
            top_width=back_depth,
        ).with_name("back_panel")
        back_panel.move_anchor_to("back_center", (0.0, 0.0, -outer_depth / 2.0))

        front_frame = Rectangular_Ring(
            front_height=front_depth,
            outer_top_length=outer_length,
            outer_top_width=outer_height,
            inner_top_length=inner_length,
            inner_top_width=inner_height,
            inner_offset=(inner_center_x, -inner_center_y),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("front_hollow_frame")
        front_frame.move_anchor_to(
            "outer_bottom_center",
            back_panel.world_anchor("front_center"),
        )

        main_height, main_depth = main_clapboard_size
        main_clapboard = Cuboid(
            height=main_height,
            top_length=inner_length,
            top_width=main_depth,
        ).with_name("main_clapboard")
        main_clapboard.move_anchor_to(
            "back_center",
            (
                inner_center_x,
                inner_center_y + main_clapboard_offset_y,
                inner_back_z,
            ),
        )

        components = [back_panel, front_frame, main_clapboard]
        for board_index, board_spec in enumerate(sub_clapboards, start=1):
            board_length, board_height, board_depth = board_spec["size"]
            offset_x, offset_y = board_spec["offset"]
            board = Cuboid(
                height=board_height,
                top_length=board_length,
                top_width=board_depth,
            ).with_name(f"sub_clapboard_{board_index}")
            board.move_anchor_to(
                "back_center",
                (
                    inner_center_x + offset_x,
                    inner_center_y + offset_y,
                    inner_back_z,
                ),
            )
            components.append(board)

        return components


class CuboidalSafeDoor(ConceptTemplate):
    def __init__(self, panel_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(panel_size=panel_size))
        self.semantic = "Door"

    @staticmethod
    def _build_components(panel_size):
        panel_length, panel_height, panel_depth = panel_size
        panel = Cuboid(
            height=panel_height,
            top_length=panel_length,
            top_width=panel_depth,
        ).with_name("door_panel")
        panel.move_anchor_to("back_center", (0.0, 0.0, 0.0))
        return [panel]


class RearLayerSafeDoor(ConceptTemplate):
    def __init__(
        self,
        main_panel_size,
        rear_panel_size,
        rear_panel_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                main_panel_size=main_panel_size,
                rear_panel_size=rear_panel_size,
                rear_panel_offset=rear_panel_offset,
            )
        )
        self.semantic = "Door"

    @staticmethod
    def _build_components(main_panel_size, rear_panel_size, rear_panel_offset):
        main_length, main_height, main_depth = main_panel_size
        rear_length, rear_height, rear_depth = rear_panel_size
        rear_offset_x, rear_offset_y = rear_panel_offset

        main_panel = Cuboid(
            height=main_height,
            top_length=main_length,
            top_width=main_depth,
        ).with_name("main_panel")
        main_panel.move_anchor_to("back_center", (0.0, 0.0, 0.0))

        rear_panel = Cuboid(
            height=rear_height,
            top_length=rear_length,
            top_width=rear_depth,
        ).with_name("rear_panel")
        back_x, back_y, back_z = main_panel.world_anchor("back_center")
        rear_panel.move_anchor_to(
            "front_center",
            (back_x + rear_offset_x, back_y + rear_offset_y, back_z),
        )

        return [main_panel, rear_panel]


class FrontLayerSafeDoor(ConceptTemplate):
    def __init__(
        self,
        main_panel_size,
        front_panel_size,
        front_panel_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                main_panel_size=main_panel_size,
                front_panel_size=front_panel_size,
                front_panel_offset=front_panel_offset,
            )
        )
        self.semantic = "Door"

    @staticmethod
    def _build_components(main_panel_size, front_panel_size, front_panel_offset):
        main_length, main_height, main_depth = main_panel_size
        front_length, front_height, front_depth = front_panel_size
        front_offset_x, front_offset_y = front_panel_offset

        main_panel = Cuboid(
            height=main_height,
            top_length=main_length,
            top_width=main_depth,
        ).with_name("main_panel")
        main_panel.move_anchor_to("back_center", (0.0, 0.0, 0.0))

        front_panel = Cuboid(
            height=front_height,
            top_length=front_length,
            top_width=front_depth,
        ).with_name("front_panel")
        front_x, front_y, front_z = main_panel.world_anchor("front_center")
        front_panel.move_anchor_to(
            "back_center",
            (front_x + front_offset_x, front_y + front_offset_y, front_z),
        )

        return [main_panel, front_panel]


class SunkenSafeDoor(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        sunken_opening_size,
        sunken_opening_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                sunken_opening_size=sunken_opening_size,
                sunken_opening_offset=sunken_opening_offset,
            )
        )
        self.semantic = "Door"

    @staticmethod
    def _build_components(outer_size, sunken_opening_size, sunken_opening_offset):
        outer_length, outer_height, outer_depth = outer_size
        opening_length, opening_height, frame_depth = sunken_opening_size
        opening_offset_x, opening_offset_y = sunken_opening_offset
        rear_depth = outer_depth - frame_depth

        rear_slab = Cuboid(
            height=outer_height,
            top_length=outer_length,
            top_width=rear_depth,
        ).with_name("rear_slab")
        rear_slab.move_anchor_to("back_center", (0.0, 0.0, 0.0))

        front_frame = Rectangular_Ring(
            front_height=frame_depth,
            outer_top_length=outer_length,
            outer_top_width=outer_height,
            inner_top_length=opening_length,
            inner_top_width=opening_height,
            inner_offset=(opening_offset_x, -opening_offset_y),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("front_sunken_frame")
        front_frame.move_anchor_to(
            "outer_bottom_center",
            rear_slab.world_anchor("front_center"),
        )

        return [rear_slab, front_frame]


class CylindricalSafeConnector(ConceptTemplate):
    def __init__(self, connector_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(connector_size=connector_size))
        self.semantic = "Connector"

    @staticmethod
    def _build_components(connector_size):
        connector_radius, connector_height = connector_size
        return [
            Cylinder(
                height=connector_height,
                top_radius=connector_radius,
            ).with_name("cylindrical_connector")
        ]


class TShapedSafeConnector(ConceptTemplate):
    def __init__(
        self,
        cylinder_size,
        side_block_size,
        side_block_offset_y,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                cylinder_size=cylinder_size,
                side_block_size=side_block_size,
                side_block_offset_y=side_block_offset_y,
            )
        )
        self.semantic = "Connector"

    @staticmethod
    def _build_components(cylinder_size, side_block_size, side_block_offset_y):
        cylinder_radius, cylinder_height = cylinder_size
        block_length, block_height, block_depth = side_block_size

        cylinder = Cylinder(
            height=cylinder_height,
            top_radius=cylinder_radius,
        ).with_name("cylindrical_stem")

        side_block = Cuboid(
            height=block_height,
            top_length=block_length,
            top_width=block_depth,
        ).with_name("side_block")
        side_block.move_anchor_to(
            "back_left_center",
            (cylinder_radius, side_block_offset_y, -cylinder_radius),
        )

        return [cylinder, side_block]


class TrifoldSafeHandle(ConceptTemplate):
    def __init__(
        self,
        parallel_bar_size,
        parallel_bar_separation_y,
        bridge_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=HANDLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                parallel_bar_size=parallel_bar_size,
                parallel_bar_separation_y=parallel_bar_separation_y,
                bridge_size=bridge_size,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        parallel_bar_size,
        parallel_bar_separation_y,
        bridge_size,
    ):
        bar_length, bar_height, bar_depth = parallel_bar_size
        bridge_length, bridge_height, bridge_depth = bridge_size

        positive_bar = Cuboid(
            height=bar_height,
            top_length=bar_length,
            top_width=bar_depth,
        ).with_name("positive_y_parallel_bar")
        positive_bar.move_anchor_to(
            "back_center",
            (0.0, parallel_bar_separation_y / 2.0, 0.0),
        )

        negative_bar = Cuboid(
            height=bar_height,
            top_length=bar_length,
            top_width=bar_depth,
        ).with_name("negative_y_parallel_bar")
        negative_bar.move_anchor_to(
            "back_center",
            (0.0, -parallel_bar_separation_y / 2.0, 0.0),
        )

        bridge = Cuboid(
            height=bridge_height,
            top_length=bridge_length,
            top_width=bridge_depth,
        ).with_name("front_bridge")
        bridge.move_anchor_to("back_center", (0.0, 0.0, bar_depth))

        return [positive_bar, negative_bar, bridge]


class ClawSafeHandle(ConceptTemplate):
    def __init__(
        self,
        base_size,
        fork_size,
        fork_offset_z,
        fork_tilt_degrees,
        fork_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=HANDLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                base_size=base_size,
                fork_size=fork_size,
                fork_offset_z=fork_offset_z,
                fork_tilt_degrees=fork_tilt_degrees,
                fork_count=fork_count,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        base_size,
        fork_size,
        fork_offset_z,
        fork_tilt_degrees,
        fork_count,
    ):
        base_radius, base_depth = base_size
        fork_radial_length, fork_height, fork_depth = fork_size
        fork_tilt = fork_tilt_degrees * DEGREES_TO_RADIANS
        fork_center_radius = base_radius + fork_radial_length * cos(fork_tilt) / 2.0
        fork_center_z = (
            base_depth
            - fork_depth / 2.0
            + fork_radial_length * sin(fork_tilt) / 2.0
            - fork_offset_z
        )

        base = Cylinder(
            height=base_depth,
            top_radius=base_radius,
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("cylindrical_base")
        base.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        components = [base]
        for frame in radial_array_frames(
            count=fork_count,
            center_point=(fork_center_radius, 0.0, fork_center_z),
            item_rotation=(0.0, -fork_tilt, 0.0),
            radial_axis="z",
        ):
            fork = Cuboid(
                height=fork_height,
                top_length=fork_radial_length,
                top_width=fork_depth,
            ).with_name(f"fork_{frame.index + 1}")
            fork.set_rotation_matrix(frame.rotation_matrix)
            fork.set_transform(position=frame.position)
            components.append(fork)

        return components


class RoundSafeHandle(ConceptTemplate):
    def __init__(
        self,
        base_size,
        fork_size,
        fork_offset_z,
        fork_tilt_degrees,
        outer_ring_size,
        fork_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=HANDLE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                base_size=base_size,
                fork_size=fork_size,
                fork_offset_z=fork_offset_z,
                fork_tilt_degrees=fork_tilt_degrees,
                outer_ring_size=outer_ring_size,
                fork_count=fork_count,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        base_size,
        fork_size,
        fork_offset_z,
        fork_tilt_degrees,
        outer_ring_size,
        fork_count,
    ):
        base_radius, base_depth = base_size
        fork_radial_length, fork_height, fork_depth = fork_size
        outer_ring_radius, ring_depth = outer_ring_size
        fork_tilt = fork_tilt_degrees * DEGREES_TO_RADIANS
        fork_center_radius = base_radius + fork_radial_length * cos(fork_tilt) / 2.0
        fork_center_z = (
            base_depth
            - fork_depth / 2.0
            + fork_radial_length * sin(fork_tilt) / 2.0
            - fork_offset_z
        )
        inner_ring_radius = base_radius + fork_radial_length * cos(fork_tilt)
        ring_center_z = (
            base_depth
            - fork_depth / 2.0
            + fork_radial_length * sin(fork_tilt)
            - fork_offset_z
        )

        base = Cylinder(
            height=base_depth,
            top_radius=base_radius,
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("cylindrical_base")
        base.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        components = [base]
        for frame in radial_array_frames(
            count=fork_count,
            center_point=(fork_center_radius, 0.0, fork_center_z),
            item_rotation=(0.0, -fork_tilt, 0.0),
            radial_axis="z",
        ):
            fork = Cuboid(
                height=fork_height,
                top_length=fork_radial_length,
                top_width=fork_depth,
            ).with_name(f"fork_{frame.index + 1}")
            fork.set_rotation_matrix(frame.rotation_matrix)
            fork.set_transform(position=frame.position)
            components.append(fork)

        outer_ring = Ring(
            height=ring_depth,
            outer_top_radius=outer_ring_radius,
            inner_top_radius=inner_ring_radius,
            position=(0.0, 0.0, ring_center_z),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("outer_ring")
        components.append(outer_ring)

        return components


class CylindricalSafeDial(ConceptTemplate):
    def __init__(
        self,
        base_size,
        top_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                base_size=base_size,
                top_size=top_size,
            )
        )
        self.semantic = "Dial"

    @staticmethod
    def _build_components(base_size, top_size):
        base_top_radius, base_bottom_radius, base_depth = base_size
        top_radius, top_depth = top_size

        base = Cylinder(
            height=base_depth,
            top_radius=base_top_radius,
            bottom_radius=base_bottom_radius,
            rotation=(-pi / 2.0, 0.0, 0.0),
        ).with_name("tapered_base")
        base.move_anchor_to("top_center", (0.0, 0.0, 0.0))

        top = Cylinder(
            height=top_depth,
            top_radius=top_radius,
            rotation=(-pi / 2.0, 0.0, 0.0),
        ).with_name("front_knob")
        top.move_anchor_to("top_center", base.world_anchor("bottom_center"))

        return [base, top]


class RegularSafeController(ConceptTemplate):
    def __init__(self, panel_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_components(panel_size=panel_size))
        self.semantic = "Controller"

    @staticmethod
    def _build_components(panel_size):
        panel_length, panel_height, panel_depth = panel_size
        panel = Cuboid(
            height=panel_height,
            top_length=panel_length,
            top_width=panel_depth,
        ).with_name("controller_panel")
        panel.move_anchor_to("back_center", (0.0, 0.0, 0.0))
        return [panel]


class CuboidalSafeLegSet(ConceptTemplate):
    def __init__(
        self,
        front_leg_size,
        rear_leg_size,
        leg_center_spacing,
        leg_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                front_leg_size=front_leg_size,
                rear_leg_size=rear_leg_size,
                leg_center_spacing=leg_center_spacing,
                leg_count=leg_count,
            )
        )
        self.semantic = "Leg"

    @classmethod
    def _build_components(
        cls,
        front_leg_size,
        rear_leg_size,
        leg_center_spacing,
        leg_count,
    ):
        front_spacing_x, rear_spacing_x, front_rear_spacing_z = leg_center_spacing
        if int(leg_count) == 1:
            return [
                cls._leg(
                    "center_front_leg",
                    front_leg_size,
                    (0.0, 0.0, 0.0),
                )
            ]
        if int(leg_count) == 2:
            return [
                cls._leg(
                    "right_front_leg",
                    front_leg_size,
                    (front_spacing_x / 2.0, 0.0, 0.0),
                ),
                cls._leg(
                    "left_front_leg",
                    front_leg_size,
                    (-front_spacing_x / 2.0, 0.0, 0.0),
                ),
            ]
        if int(leg_count) == 3:
            return [
                cls._leg(
                    "right_front_leg",
                    front_leg_size,
                    (front_spacing_x / 2.0, 0.0, front_rear_spacing_z / 2.0),
                ),
                cls._leg(
                    "left_front_leg",
                    front_leg_size,
                    (-front_spacing_x / 2.0, 0.0, front_rear_spacing_z / 2.0),
                ),
                cls._leg(
                    "center_rear_leg",
                    rear_leg_size,
                    (0.0, 0.0, -front_rear_spacing_z / 2.0),
                ),
            ]
        if int(leg_count) == 4:
            return [
                cls._leg(
                    "right_front_leg",
                    front_leg_size,
                    (front_spacing_x / 2.0, 0.0, front_rear_spacing_z / 2.0),
                ),
                cls._leg(
                    "left_front_leg",
                    front_leg_size,
                    (-front_spacing_x / 2.0, 0.0, front_rear_spacing_z / 2.0),
                ),
                cls._leg(
                    "right_rear_leg",
                    rear_leg_size,
                    (rear_spacing_x / 2.0, 0.0, -front_rear_spacing_z / 2.0),
                ),
                cls._leg(
                    "left_rear_leg",
                    rear_leg_size,
                    (-rear_spacing_x / 2.0, 0.0, -front_rear_spacing_z / 2.0),
                ),
            ]
        return []

    @staticmethod
    def _leg(name, leg_size, top_mount):
        leg_length, leg_height, leg_depth = leg_size
        leg = Cuboid(
            height=leg_height,
            top_length=leg_length,
            top_width=leg_depth,
        ).with_name(name)
        leg.move_anchor_to("top_center", top_mount)
        return leg
