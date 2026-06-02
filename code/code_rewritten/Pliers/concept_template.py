from math import pi

from code.geometry_rewritten import ConceptTemplate, Cuboid, Cylinder, Ring


DEGREES_TO_RADIANS = pi / 180.0


class RoundPliersShaft(ConceptTemplate):
    def __init__(
        self,
        shaft_radius,
        shaft_height,
        secondary_shaft_enabled=False,
        secondary_shaft_radius=0.0,
        secondary_shaft_height=0.0,
        secondary_shaft_offset=(0, 0, 0),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                shaft_radius=shaft_radius,
                shaft_height=shaft_height,
                secondary_shaft_enabled=secondary_shaft_enabled,
                secondary_shaft_radius=secondary_shaft_radius,
                secondary_shaft_height=secondary_shaft_height,
                secondary_shaft_offset=secondary_shaft_offset,
            )
        )
        self.semantic = "Shaft"

    @staticmethod
    def _build_components(
        shaft_radius,
        shaft_height,
        secondary_shaft_enabled,
        secondary_shaft_radius,
        secondary_shaft_height,
        secondary_shaft_offset,
    ):
        components = [
            Cylinder(
                height=shaft_height,
                top_radius=shaft_radius,
            ).with_name("main_round_shaft")
        ]

        if secondary_shaft_enabled:
            components.append(
                Cylinder(
                    height=secondary_shaft_height,
                    top_radius=secondary_shaft_radius,
                    position=secondary_shaft_offset,
                ).with_name("secondary_offset_round_shaft")
            )

        return components


class LayeredPliersShaft(ConceptTemplate):
    def __init__(
        self,
        lower_layer_size,
        lower_layer_yaw_degrees,
        upper_layers=(),
        secondary_shaft_enabled=False,
        secondary_shaft_radius=0.0,
        secondary_shaft_height=0.0,
        secondary_shaft_offset=(0, 0, 0),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                lower_layer_size=lower_layer_size,
                lower_layer_yaw_degrees=lower_layer_yaw_degrees,
                upper_layers=upper_layers,
                secondary_shaft_enabled=secondary_shaft_enabled,
                secondary_shaft_radius=secondary_shaft_radius,
                secondary_shaft_height=secondary_shaft_height,
                secondary_shaft_offset=secondary_shaft_offset,
            )
        )
        self.semantic = "Shaft"

    @staticmethod
    def _block(name, size, yaw_degrees):
        length, height, width = size
        return Cuboid(
            height=height,
            top_length=length,
            top_width=width,
            rotation=(0.0, yaw_degrees * DEGREES_TO_RADIANS, 0.0),
        ).with_name(name)

    @classmethod
    def _build_components(
        cls,
        lower_layer_size,
        lower_layer_yaw_degrees,
        upper_layers,
        secondary_shaft_enabled,
        secondary_shaft_radius,
        secondary_shaft_height,
        secondary_shaft_offset,
    ):
        components = []
        lower = cls._block(
            name="lower_reference_layer",
            size=lower_layer_size,
            yaw_degrees=lower_layer_yaw_degrees,
        )
        lower.move_anchor_to("top_center", (0.0, 0.0, 0.0))
        components.append(lower)

        current_reference_y = 0.0
        for layer_index, layer in enumerate(upper_layers, start=2):
            offset_x, offset_z = layer["offset"]
            length, height, width = layer["size"]
            block = cls._block(
                name=f"upper_layer_{layer_index}",
                size=(length, height, width),
                yaw_degrees=layer["yaw_degrees"],
            )
            block.move_anchor_to("bottom_center", (offset_x, current_reference_y, offset_z))
            components.append(block)
            current_reference_y += height

        if secondary_shaft_enabled:
            components.append(
                Cylinder(
                    height=secondary_shaft_height,
                    top_radius=secondary_shaft_radius,
                    position=secondary_shaft_offset,
                ).with_name("secondary_offset_round_shaft")
            )

        return components


class StraightPliersHandle(ConceptTemplate):
    def __init__(
        self,
        front_segment_size,
        rear_segment_size,
        side_separation,
        front_yaw_degrees,
        rear_yaw_degrees,
        rear_offset,
        right_side_y_offset=0.0,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                front_segment_size=front_segment_size,
                rear_segment_size=rear_segment_size,
                side_separation=side_separation,
                front_yaw_degrees=front_yaw_degrees,
                rear_yaw_degrees=rear_yaw_degrees,
                rear_offset=rear_offset,
                right_side_y_offset=right_side_y_offset,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _straight_segment(name, size, yaw_degrees):
        length, height, width = size
        return Cuboid(
            height=height,
            top_length=length,
            top_width=width,
            rotation=(0.0, yaw_degrees * DEGREES_TO_RADIANS, 0.0),
        ).with_name(name)

    @classmethod
    def _build_components(
        cls,
        front_segment_size,
        rear_segment_size,
        side_separation,
        front_yaw_degrees,
        rear_yaw_degrees,
        rear_offset,
        right_side_y_offset,
    ):
        rear_offset_x, rear_offset_y = rear_offset
        left_front = cls._straight_segment(
            "left_front_handle_segment",
            front_segment_size,
            -front_yaw_degrees,
        )
        left_front.move_anchor_to("front_center", (side_separation / 2.0, 0.0, 0.0))

        right_front = cls._straight_segment(
            "right_front_handle_segment",
            front_segment_size,
            front_yaw_degrees,
        )
        right_front.move_anchor_to(
            "front_center",
            (-side_separation / 2.0, right_side_y_offset, 0.0),
        )

        left_rear_target_x, left_rear_target_y, left_rear_target_z = left_front.world_anchor(
            "back_right_center"
        )
        left_rear = cls._straight_segment(
            "left_rear_handle_segment",
            rear_segment_size,
            -rear_yaw_degrees,
        )
        left_rear.move_anchor_to(
            "front_right_center",
            (
                left_rear_target_x + rear_offset_x,
                left_rear_target_y + rear_offset_y,
                left_rear_target_z,
            ),
        )

        right_rear_target_x, right_rear_target_y, right_rear_target_z = (
            right_front.world_anchor("back_left_center")
        )
        right_rear = cls._straight_segment(
            "right_rear_handle_segment",
            rear_segment_size,
            rear_yaw_degrees,
        )
        right_rear.move_anchor_to(
            "front_left_center",
            (
                right_rear_target_x - rear_offset_x,
                right_rear_target_y + rear_offset_y,
                right_rear_target_z,
            ),
        )

        return [left_front, left_rear, right_front, right_rear]


class RearCurvedPliersHandle(ConceptTemplate):
    def __init__(
        self,
        front_segment_size,
        rear_arc_outer_radius,
        rear_arc_inner_radius,
        rear_arc_height,
        rear_arc_angle_degrees,
        side_separation,
        front_yaw_degrees,
        rear_arc_yaw_degrees,
        rear_offset,
        right_side_y_offset=0.0,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                front_segment_size=front_segment_size,
                rear_arc_outer_radius=rear_arc_outer_radius,
                rear_arc_inner_radius=rear_arc_inner_radius,
                rear_arc_height=rear_arc_height,
                rear_arc_angle_degrees=rear_arc_angle_degrees,
                side_separation=side_separation,
                front_yaw_degrees=front_yaw_degrees,
                rear_arc_yaw_degrees=rear_arc_yaw_degrees,
                rear_offset=rear_offset,
                right_side_y_offset=right_side_y_offset,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _front_segment(name, size, yaw_degrees):
        length, height, width = size
        return Cuboid(
            height=height,
            top_length=length,
            top_width=width,
            rotation=(0.0, yaw_degrees * DEGREES_TO_RADIANS, 0.0),
        ).with_name(name)

    @staticmethod
    def _rear_arc(name, outer_radius, inner_radius, height, angle_degrees, rotation):
        return Ring(
            height=height,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=angle_degrees * DEGREES_TO_RADIANS,
            rotation=rotation,
        ).with_name(name)

    @classmethod
    def _build_components(
        cls,
        front_segment_size,
        rear_arc_outer_radius,
        rear_arc_inner_radius,
        rear_arc_height,
        rear_arc_angle_degrees,
        side_separation,
        front_yaw_degrees,
        rear_arc_yaw_degrees,
        rear_offset,
        right_side_y_offset,
    ):
        rear_offset_x, rear_offset_y = rear_offset
        rear_arc_yaw = rear_arc_yaw_degrees * DEGREES_TO_RADIANS

        left_front = cls._front_segment(
            "left_front_handle_segment",
            front_segment_size,
            -front_yaw_degrees,
        )
        left_front.move_anchor_to("front_center", (side_separation / 2.0, 0.0, 0.0))

        right_front = cls._front_segment(
            "right_front_handle_segment",
            front_segment_size,
            front_yaw_degrees,
        )
        right_front.move_anchor_to(
            "front_center",
            (-side_separation / 2.0, right_side_y_offset, 0.0),
        )

        left_arc_x, left_arc_y, left_arc_z = left_front.world_anchor("back_left_center")
        left_arc = cls._rear_arc(
            "left_rear_handle_arc",
            rear_arc_outer_radius,
            rear_arc_inner_radius,
            rear_arc_height,
            rear_arc_angle_degrees,
            (0.0, pi + rear_arc_yaw, pi),
        )
        left_arc.move_anchor_to(
            "inner_mid_start",
            (
                left_arc_x + rear_offset_x,
                left_arc_y + rear_offset_y,
                left_arc_z,
            ),
        )

        right_arc_x, right_arc_y, right_arc_z = right_front.world_anchor(
            "back_right_center"
        )
        right_arc = cls._rear_arc(
            "right_rear_handle_arc",
            rear_arc_outer_radius,
            rear_arc_inner_radius,
            rear_arc_height,
            rear_arc_angle_degrees,
            (0.0, pi + rear_arc_yaw, 0.0),
        )
        right_arc.move_anchor_to(
            "inner_mid_start",
            (
                right_arc_x - rear_offset_x,
                right_arc_y + rear_offset_y,
                right_arc_z,
            ),
        )

        return [left_front, left_arc, right_front, right_arc]


class MiddleCurvedPliersHandle(ConceptTemplate):
    def __init__(
        self,
        front_segment_size,
        middle_arc_outer_radius,
        middle_arc_inner_radius,
        middle_arc_height,
        middle_arc_angle_degrees,
        rear_segment_size,
        side_separation,
        front_yaw_degrees,
        middle_arc_yaw_degrees,
        rear_yaw_degrees,
        front_to_middle_offset,
        middle_to_rear_offset,
        right_side_y_offset=0.0,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                front_segment_size=front_segment_size,
                middle_arc_outer_radius=middle_arc_outer_radius,
                middle_arc_inner_radius=middle_arc_inner_radius,
                middle_arc_height=middle_arc_height,
                middle_arc_angle_degrees=middle_arc_angle_degrees,
                rear_segment_size=rear_segment_size,
                side_separation=side_separation,
                front_yaw_degrees=front_yaw_degrees,
                middle_arc_yaw_degrees=middle_arc_yaw_degrees,
                rear_yaw_degrees=rear_yaw_degrees,
                front_to_middle_offset=front_to_middle_offset,
                middle_to_rear_offset=middle_to_rear_offset,
                right_side_y_offset=right_side_y_offset,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _straight_segment(name, size, yaw_degrees):
        length, height, width = size
        return Cuboid(
            height=height,
            top_length=length,
            top_width=width,
            rotation=(0.0, yaw_degrees * DEGREES_TO_RADIANS, 0.0),
        ).with_name(name)

    @staticmethod
    def _arc_segment(name, outer_radius, inner_radius, height, angle_degrees, rotation):
        return Ring(
            height=height,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=angle_degrees * DEGREES_TO_RADIANS,
            rotation=rotation,
        ).with_name(name)

    @classmethod
    def _build_components(
        cls,
        front_segment_size,
        middle_arc_outer_radius,
        middle_arc_inner_radius,
        middle_arc_height,
        middle_arc_angle_degrees,
        rear_segment_size,
        side_separation,
        front_yaw_degrees,
        middle_arc_yaw_degrees,
        rear_yaw_degrees,
        front_to_middle_offset,
        middle_to_rear_offset,
        right_side_y_offset,
    ):
        front_to_middle_x, front_to_middle_y = front_to_middle_offset
        middle_to_rear_x, middle_to_rear_y = middle_to_rear_offset
        middle_arc_yaw = middle_arc_yaw_degrees * DEGREES_TO_RADIANS

        left_front = cls._straight_segment(
            "left_front_handle_segment",
            front_segment_size,
            -front_yaw_degrees,
        )
        left_front.move_anchor_to("front_center", (side_separation / 2.0, 0.0, 0.0))

        right_front = cls._straight_segment(
            "right_front_handle_segment",
            front_segment_size,
            front_yaw_degrees,
        )
        right_front.move_anchor_to(
            "front_center",
            (-side_separation / 2.0, right_side_y_offset, 0.0),
        )

        (
            left_middle_base_x,
            left_middle_base_y,
            left_middle_base_z,
        ) = left_front.world_anchor("back_left_center")
        left_middle_target = (
            left_middle_base_x + front_to_middle_x,
            left_middle_base_y + front_to_middle_y,
            left_middle_base_z,
        )
        left_middle = cls._arc_segment(
            "left_middle_handle_arc",
            middle_arc_outer_radius,
            middle_arc_inner_radius,
            middle_arc_height,
            middle_arc_angle_degrees,
            (0.0, pi + middle_arc_yaw, pi),
        )
        left_middle.move_anchor_to(
            "inner_mid_start",
            left_middle_target,
        )

        left_rear = cls._straight_segment(
            "left_rear_handle_segment",
            rear_segment_size,
            -rear_yaw_degrees,
        )
        left_rear_target_x, left_rear_target_y, left_rear_target_z = (
            left_middle.world_anchor("inner_mid_end")
        )
        left_rear.move_anchor_to(
            "front_left_center",
            (
                left_rear_target_x + middle_to_rear_x,
                left_rear_target_y + middle_to_rear_y,
                left_rear_target_z,
            ),
        )

        (
            right_middle_base_x,
            right_middle_base_y,
            right_middle_base_z,
        ) = right_front.world_anchor("back_right_center")
        right_middle_target = (
            right_middle_base_x - front_to_middle_x,
            right_middle_base_y + front_to_middle_y,
            right_middle_base_z,
        )
        right_middle = cls._arc_segment(
            "right_middle_handle_arc",
            middle_arc_outer_radius,
            middle_arc_inner_radius,
            middle_arc_height,
            middle_arc_angle_degrees,
            (0.0, pi + middle_arc_yaw, 0.0),
        )
        right_middle.move_anchor_to(
            "inner_mid_start",
            right_middle_target,
        )

        right_rear = cls._straight_segment(
            "right_rear_handle_segment",
            rear_segment_size,
            rear_yaw_degrees,
        )
        right_rear_target_x, right_rear_target_y, right_rear_target_z = (
            right_middle.world_anchor("inner_mid_end")
        )
        right_rear.move_anchor_to(
            "front_right_center",
            (
                right_rear_target_x - middle_to_rear_x,
                right_rear_target_y + middle_to_rear_y,
                right_rear_target_z,
            ),
        )

        return [left_front, left_middle, left_rear, right_front, right_middle, right_rear]


class AsymmetricStraightPliersHandle(ConceptTemplate):
    def __init__(
        self,
        left_front_segment_size,
        left_rear_segment_size,
        left_front_yaw_degrees,
        left_rear_yaw_degrees,
        left_rear_offset,
        right_front_segment_size,
        right_rear_segment_size,
        right_front_yaw_degrees,
        right_rear_yaw_degrees,
        right_rear_offset,
        side_separation,
        right_side_y_offset=0.0,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                left_front_segment_size=left_front_segment_size,
                left_rear_segment_size=left_rear_segment_size,
                left_front_yaw_degrees=left_front_yaw_degrees,
                left_rear_yaw_degrees=left_rear_yaw_degrees,
                left_rear_offset=left_rear_offset,
                right_front_segment_size=right_front_segment_size,
                right_rear_segment_size=right_rear_segment_size,
                right_front_yaw_degrees=right_front_yaw_degrees,
                right_rear_yaw_degrees=right_rear_yaw_degrees,
                right_rear_offset=right_rear_offset,
                side_separation=side_separation,
                right_side_y_offset=right_side_y_offset,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _segment(name, size, yaw_degrees):
        length, height, width = size
        return Cuboid(
            height=height,
            top_length=length,
            top_width=width,
            rotation=(0.0, yaw_degrees * DEGREES_TO_RADIANS, 0.0),
        ).with_name(name)

    @classmethod
    def _build_components(
        cls,
        left_front_segment_size,
        left_rear_segment_size,
        left_front_yaw_degrees,
        left_rear_yaw_degrees,
        left_rear_offset,
        right_front_segment_size,
        right_rear_segment_size,
        right_front_yaw_degrees,
        right_rear_yaw_degrees,
        right_rear_offset,
        side_separation,
        right_side_y_offset,
    ):
        left_rear_offset_x, left_rear_offset_y = left_rear_offset
        right_rear_offset_x, right_rear_offset_y = right_rear_offset

        left_front = cls._segment(
            "left_front_handle_segment",
            left_front_segment_size,
            left_front_yaw_degrees,
        )
        left_front.move_anchor_to("front_center", (-side_separation / 2.0, 0.0, 0.0))

        left_target_x, left_target_y, left_target_z = left_front.world_anchor(
            "back_left_center"
        )
        left_rear = cls._segment(
            "left_rear_handle_segment",
            left_rear_segment_size,
            left_rear_yaw_degrees,
        )
        left_rear.move_anchor_to(
            "front_left_center",
            (
                left_target_x - left_rear_offset_x,
                left_target_y + left_rear_offset_y,
                left_target_z,
            ),
        )

        right_front = cls._segment(
            "right_front_handle_segment",
            right_front_segment_size,
            -right_front_yaw_degrees,
        )
        right_front.move_anchor_to(
            "front_center",
            (side_separation / 2.0, right_side_y_offset, 0.0),
        )

        right_target_x, right_target_y, right_target_z = right_front.world_anchor(
            "back_right_center"
        )
        right_rear = cls._segment(
            "right_rear_handle_segment",
            right_rear_segment_size,
            -right_rear_yaw_degrees,
        )
        right_rear.move_anchor_to(
            "front_right_center",
            (
                right_target_x + right_rear_offset_x,
                right_target_y + right_rear_offset_y,
                right_target_z,
            ),
        )

        return [left_front, left_rear, right_front, right_rear]


class CuspPliersGripper(ConceptTemplate):
    def __init__(
        self,
        rear_segment_size,
        front_segment_size,
        side_separation,
        jaw_yaw_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                rear_segment_size=rear_segment_size,
                front_segment_size=front_segment_size,
                side_separation=side_separation,
                jaw_yaw_degrees=jaw_yaw_degrees,
            )
        )
        self.semantic = "Gripper"

    @staticmethod
    def _tapered_segment(name, size, side_sign, yaw_degrees):
        bottom_length, top_length, width, depth = size
        top_offset_x = side_sign * (top_length - bottom_length) / 2.0
        return Cuboid(
            height=depth,
            top_length=top_length,
            top_width=width,
            bottom_length=bottom_length,
            bottom_width=width,
            top_offset=(top_offset_x, 0.0),
            rotation=(pi / 2.0, yaw_degrees * DEGREES_TO_RADIANS, 0.0),
        ).with_name(name)

    @classmethod
    def _build_components(
        cls,
        rear_segment_size,
        front_segment_size,
        side_separation,
        jaw_yaw_degrees,
    ):
        rear_bottom_length, _, _, rear_depth = rear_segment_size
        front_bottom_length, _, _, front_depth = front_segment_size

        left_base = (side_separation / 2.0, 0.0, 0.0)
        right_base = (-side_separation / 2.0, 0.0, 0.0)

        left_rear = cls._tapered_segment(
            "left_rear_gripper_segment",
            rear_segment_size,
            side_sign=-1.0,
            yaw_degrees=jaw_yaw_degrees,
        )
        left_rear.move_anchor_to("bottom_left_center", left_base)

        left_front = cls._tapered_segment(
            "left_front_gripper_segment",
            front_segment_size,
            side_sign=1.0,
            yaw_degrees=jaw_yaw_degrees,
        )
        left_front.move_local_point_to(
            (
                -front_bottom_length / 2.0,
                -(rear_depth + front_depth / 2.0),
                0.0,
            ),
            left_base,
        )

        right_front = cls._tapered_segment(
            "right_front_gripper_segment",
            front_segment_size,
            side_sign=-1.0,
            yaw_degrees=-jaw_yaw_degrees,
        )
        right_front.move_local_point_to(
            (
                front_bottom_length / 2.0,
                -(rear_depth + front_depth / 2.0),
                0.0,
            ),
            right_base,
        )

        right_rear = cls._tapered_segment(
            "right_rear_gripper_segment",
            rear_segment_size,
            side_sign=1.0,
            yaw_degrees=-jaw_yaw_degrees,
        )
        right_rear.move_anchor_to("bottom_right_center", right_base)

        return [left_front, left_rear, right_front, right_rear]


class CurvedPliersGripper(ConceptTemplate):
    def __init__(
        self,
        radius_x,
        radius_z,
        thickness,
        side_separation,
        jaw_yaw_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                radius_x=radius_x,
                radius_z=radius_z,
                thickness=thickness,
                side_separation=side_separation,
                jaw_yaw_degrees=jaw_yaw_degrees,
            )
        )
        self.semantic = "Gripper"

    @staticmethod
    def _build_components(radius_x, radius_z, thickness, side_separation, jaw_yaw_degrees):
        jaw_yaw = jaw_yaw_degrees * DEGREES_TO_RADIANS
        left = Cylinder(
            height=thickness,
            top_radius=radius_x,
            bottom_radius=radius_x,
            top_radius_z=radius_z,
            bottom_radius_z=radius_z,
            is_quarter=True,
            position=(side_separation / 2.0, 0.0, 0.0),
            rotation=(0.0, jaw_yaw, 0.0),
        ).with_name("left_curved_gripper")

        right = Cylinder(
            height=thickness,
            top_radius=radius_x,
            bottom_radius=radius_x,
            top_radius_z=radius_z,
            bottom_radius_z=radius_z,
            is_quarter=True,
            position=(-side_separation / 2.0, 0.0, 0.0),
            rotation=(0.0, -jaw_yaw, pi),
            rotation_order="ZYX",
        ).with_name("right_curved_gripper")

        return [left, right]


class RectangularPliersBaffle(ConceptTemplate):
    def __init__(
        self,
        baffle_size,
        side_separation,
        yaw_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                baffle_size=baffle_size,
                side_separation=side_separation,
                yaw_degrees=yaw_degrees,
            )
        )
        self.semantic = "Baffle"

    @staticmethod
    def _build_components(baffle_size, side_separation, yaw_degrees):
        length, height, width = baffle_size
        yaw = yaw_degrees * DEGREES_TO_RADIANS
        left = Cuboid(
            height=height,
            top_length=length,
            top_width=width,
            position=(side_separation / 2.0, 0.0, 0.0),
            rotation=(0.0, yaw, 0.0),
        ).with_name("left_rectangular_baffle")
        right = Cuboid(
            height=height,
            top_length=length,
            top_width=width,
            position=(-side_separation / 2.0, 0.0, 0.0),
            rotation=(0.0, -yaw, 0.0),
        ).with_name("right_rectangular_baffle")
        return [left, right]


class CurvedPliersBaffle(ConceptTemplate):
    def __init__(
        self,
        outer_radius,
        inner_radius,
        height,
        arc_angle_degrees,
        separation_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_radius=outer_radius,
                inner_radius=inner_radius,
                height=height,
                arc_angle_degrees=arc_angle_degrees,
                separation_angle_degrees=separation_angle_degrees,
            )
        )
        self.semantic = "Baffle"

    @staticmethod
    def _build_components(
        outer_radius,
        inner_radius,
        height,
        arc_angle_degrees,
        separation_angle_degrees,
    ):
        arc_angle = arc_angle_degrees * DEGREES_TO_RADIANS
        base_yaw = pi / 2.0 - separation_angle_degrees * DEGREES_TO_RADIANS / 2.0
        left = Ring(
            height=height,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=arc_angle,
            rotation=(0.0, base_yaw, 0.0),
        ).with_name("left_curved_baffle")
        right = Ring(
            height=height,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=arc_angle,
            rotation=(0.0, base_yaw, pi),
        ).with_name("right_curved_baffle")
        return [left, right]
