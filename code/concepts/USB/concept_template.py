from math import cos, pi, sin, tan

from code.geometry import (
    ConceptTemplate,
    Cuboid,
    Cylinder,
    Rectangular_Ring,
    Ring,
    Sphere,
    rotation_matrix,
)


DEGREES_TO_RADIANS = pi / 180.0
USB_ROTATION_ORDER = "YXZ"


class RegularUsbBody(ConceptTemplate):
    def __init__(
        self,
        body_size,
        rounded_back=False,
        rounded_sides=False,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=USB_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                body_size=body_size,
                rounded_back=rounded_back,
                rounded_sides=rounded_sides,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(body_size, rounded_back, rounded_sides):
        body_length, body_thickness, body_depth = body_size
        round_radius = body_thickness / 2.0

        main = Cuboid(
            height=body_thickness,
            top_length=body_length,
            top_width=body_depth,
        ).with_name("rectangular_body")
        main.move_anchor_to("front_center", (0.0, 0.0, 0.0))

        components = [main]

        if rounded_back:
            back = Cylinder(
                height=body_length,
                top_radius=round_radius,
                is_half=True,
                rotation=(0.0, pi, pi / 2.0),
            ).with_name("rounded_back_edge")
            back.move_anchor_to("flat_back_center", main.world_anchor("back_center"))
            components.append(back)

        if rounded_sides:
            left = Cylinder(
                height=body_depth,
                top_radius=round_radius,
                is_half=True,
                rotation=(pi / 2.0, 0.0, -pi / 2.0),
            ).with_name("left_rounded_side")
            left.move_anchor_to("flat_back_center", main.world_anchor("left_center"))
            components.append(left)

            right = Cylinder(
                height=body_depth,
                top_radius=round_radius,
                is_half=True,
                rotation=(pi / 2.0, 0.0, pi / 2.0),
            ).with_name("right_rounded_side")
            right.move_anchor_to("flat_back_center", main.world_anchor("right_center"))
            components.append(right)

        if rounded_back and rounded_sides:
            left_corner = Sphere(
                radius=round_radius,
                longitude_angle=pi / 2.0,
                rotation=(0.0, pi, 0.0),
            ).with_name("left_back_corner_patch")
            left_corner.move_local_point_to(
                (0.0, 0.0, 0.0),
                main.world_anchor("back_left_center"),
            )
            components.append(left_corner)

            right_corner = Sphere(
                radius=round_radius,
                longitude_angle=pi / 2.0,
                rotation=(0.0, pi / 2.0, 0.0),
            ).with_name("right_back_corner_patch")
            right_corner.move_local_point_to(
                (0.0, 0.0, 0.0),
                main.world_anchor("back_right_center"),
            )
            components.append(right_corner)

        return components


class RoundEndedUsbBody(ConceptTemplate):
    def __init__(self, body_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=USB_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(self._build_components(body_size))
        self.semantic = "Body"

    @staticmethod
    def _build_components(body_size):
        body_length, body_thickness, body_depth = body_size

        main = Cuboid(
            height=body_thickness,
            top_length=body_length,
            top_width=body_depth,
        ).with_name("rectangular_body")
        main.move_anchor_to("front_center", (0.0, 0.0, 0.0))

        back = Cylinder(
            height=body_thickness,
            top_radius=body_length / 2.0,
            is_half=True,
            rotation=(0.0, pi, 0.0),
        ).with_name("round_back_end")
        back.move_anchor_to("flat_back_center", main.world_anchor("back_center"))

        return [main, back]


class SolidUsbConnector(ConceptTemplate):
    def __init__(self, connector_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=USB_ROTATION_ORDER,
            offset_first=True,
        )
        connector_length, connector_thickness, connector_depth = connector_size
        block = Cuboid(
            height=connector_thickness,
            top_length=connector_length,
            top_width=connector_depth,
        ).with_name("solid_connector_block")
        block.move_anchor_to("back_center", (0.0, 0.0, 0.0))
        self._finalize_mesh([block])
        self.semantic = "Connector"


class HollowUsbConnector(ConceptTemplate):
    def __init__(
        self,
        connector_size,
        border_thickness,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=USB_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                connector_size=connector_size,
                border_thickness=border_thickness,
            )
        )
        self.semantic = "Connector"

    @staticmethod
    def _build_components(connector_size, border_thickness):
        outer_length, outer_height, connector_depth = connector_size
        inner_length = outer_length - border_thickness * 2.0
        inner_height = outer_height / 2.0 - border_thickness
        inner_offset_y = border_thickness / 2.0 - outer_height / 4.0

        socket = Rectangular_Ring(
            front_height=connector_depth,
            outer_top_length=outer_length,
            outer_top_width=outer_height,
            inner_top_length=inner_length,
            inner_top_width=inner_height,
            inner_offset=(0.0, inner_offset_y),
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("offset_hollow_socket")
        socket.move_anchor_to("outer_bottom_center", (0.0, 0.0, 0.0))
        return [socket]


class StandardUsbCap(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        inner_size,
        inner_outer_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=USB_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                inner_size=inner_size,
                inner_outer_offset=inner_outer_offset,
            )
        )
        self.semantic = "Cap"

    @staticmethod
    def _build_components(outer_size, inner_size, inner_outer_offset):
        outer_length, outer_height, cap_depth = outer_size
        inner_length, inner_height, sleeve_depth = inner_size
        closure_depth = cap_depth - sleeve_depth

        sleeve = Rectangular_Ring(
            front_height=sleeve_depth,
            outer_top_length=outer_length,
            outer_top_width=outer_height,
            inner_top_length=inner_length,
            inner_top_width=inner_height,
            inner_offset=inner_outer_offset,
            rotation=(pi / 2.0, 0.0, 0.0),
        ).with_name("front_hollow_sleeve")
        sleeve.move_anchor_to("outer_bottom_center", (0.0, 0.0, 0.0))

        closure = Cuboid(
            height=outer_height,
            top_length=outer_length,
            top_width=closure_depth,
        ).with_name("rear_solid_closure")
        closure.move_anchor_to("back_center", sleeve.world_anchor("outer_top_center"))

        return [sleeve, closure]


class SquareEndedRotaryUsbCap(ConceptTemplate):
    def __init__(
        self,
        cap_size,
        proximal_interval,
        inclination_degrees,
        cap_yaw_degrees,
        shaft_enabled,
        shaft_size,
        shaft_offset,
        shaft_interval,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=USB_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                cap_size=cap_size,
                proximal_interval=proximal_interval,
                inclination_degrees=inclination_degrees,
                cap_yaw_degrees=cap_yaw_degrees,
                shaft_enabled=shaft_enabled,
                shaft_size=shaft_size,
                shaft_offset=shaft_offset,
                shaft_interval=shaft_interval,
            )
        )
        self.semantic = "Cap"

    @staticmethod
    def _centerline_plane_point(local_y, local_z, cap_yaw, shaft_offset):
        return (
            local_z * sin(cap_yaw),
            local_y,
            local_z * cos(cap_yaw) + shaft_offset,
        )

    @staticmethod
    def _bridge_rotation_matrix(cap_yaw):
        return rotation_matrix((0.0, cap_yaw, 0.0)) @ rotation_matrix(
            (0.0, pi, pi / 2.0)
        )

    @staticmethod
    def _shaft_components(shaft_enabled, shaft_size, shaft_offset, shaft_interval):
        if not shaft_enabled:
            return []

        shaft_radius, shaft_height = shaft_size
        top = Cylinder(
            height=shaft_height,
            top_radius=shaft_radius,
        ).with_name("upper_pivot_shaft")
        top.move_anchor_to("bottom_center", (0.0, shaft_interval / 2.0, shaft_offset))

        bottom = Cylinder(
            height=shaft_height,
            top_radius=shaft_radius,
        ).with_name("lower_pivot_shaft")
        bottom.move_anchor_to("top_center", (0.0, -shaft_interval / 2.0, shaft_offset))

        return [top, bottom]

    @classmethod
    def _build_components(
        cls,
        cap_size,
        proximal_interval,
        inclination_degrees,
        cap_yaw_degrees,
        shaft_enabled,
        shaft_size,
        shaft_offset,
        shaft_interval,
    ):
        cap_width, arm_thickness, arm_length = cap_size
        inclination = inclination_degrees * DEGREES_TO_RADIANS
        cap_yaw = cap_yaw_degrees * DEGREES_TO_RADIANS
        bridge_radius = proximal_interval / 2.0 / cos(inclination) + arm_length * tan(
            inclination
        )
        bridge_z = -bridge_radius * sin(inclination) - arm_length * cos(
            inclination
        ) - shaft_offset
        arm_center_y = (bridge_radius + arm_thickness / 2.0) * cos(
            inclination
        ) - arm_length * sin(inclination) / 2.0
        arm_center_z = (
            (bridge_radius + arm_thickness / 2.0) * sin(inclination)
            + arm_length * cos(inclination) / 2.0
            + bridge_z
        )

        upper_arm = Cuboid(
            height=arm_thickness,
            top_length=cap_width,
            top_width=arm_length,
            position=cls._centerline_plane_point(
                arm_center_y,
                arm_center_z,
                cap_yaw,
                shaft_offset,
            ),
            rotation=(inclination, cap_yaw, 0.0),
        ).with_name("upper_straight_arm")

        lower_arm = Cuboid(
            height=arm_thickness,
            top_length=cap_width,
            top_width=arm_length,
            position=cls._centerline_plane_point(
                -arm_center_y,
                arm_center_z,
                cap_yaw,
                shaft_offset,
            ),
            rotation=(-inclination, cap_yaw, 0.0),
        ).with_name("lower_straight_arm")

        bridge = Ring(
            height=cap_width,
            outer_top_radius=bridge_radius + arm_thickness,
            inner_top_radius=bridge_radius,
            exist_angle=pi + inclination * 2.0,
        ).with_name("rear_curved_bridge")
        bridge.set_rotation_matrix(cls._bridge_rotation_matrix(cap_yaw))
        bridge.set_transform(
            position=cls._centerline_plane_point(0.0, bridge_z, cap_yaw, shaft_offset)
        )

        components = [upper_arm, lower_arm, bridge]
        components.extend(
            cls._shaft_components(
                shaft_enabled=shaft_enabled,
                shaft_size=shaft_size,
                shaft_offset=shaft_offset,
                shaft_interval=shaft_interval,
            )
        )
        return components


class RoundEndedRotaryUsbCap(ConceptTemplate):
    def __init__(
        self,
        cap_size,
        proximal_interval,
        inclination_degrees,
        cap_yaw_degrees,
        shaft_enabled,
        shaft_size,
        shaft_offset,
        shaft_interval,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=USB_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                cap_size=cap_size,
                proximal_interval=proximal_interval,
                inclination_degrees=inclination_degrees,
                cap_yaw_degrees=cap_yaw_degrees,
                shaft_enabled=shaft_enabled,
                shaft_size=shaft_size,
                shaft_offset=shaft_offset,
                shaft_interval=shaft_interval,
            )
        )
        self.semantic = "Cap"

    @staticmethod
    def _centerline_plane_point(local_y, local_z, cap_yaw, shaft_offset):
        return (
            local_z * sin(cap_yaw),
            local_y,
            local_z * cos(cap_yaw) + shaft_offset,
        )

    @staticmethod
    def _bridge_rotation_matrix(cap_yaw):
        return rotation_matrix((0.0, cap_yaw, 0.0)) @ rotation_matrix(
            (0.0, pi, pi / 2.0)
        )

    @staticmethod
    def _shaft_components(shaft_enabled, shaft_size, shaft_offset, shaft_interval):
        if not shaft_enabled:
            return []

        shaft_radius, shaft_height = shaft_size
        top = Cylinder(
            height=shaft_height,
            top_radius=shaft_radius,
        ).with_name("upper_pivot_shaft")
        top.move_anchor_to("bottom_center", (0.0, shaft_interval / 2.0, shaft_offset))

        bottom = Cylinder(
            height=shaft_height,
            top_radius=shaft_radius,
        ).with_name("lower_pivot_shaft")
        bottom.move_anchor_to("top_center", (0.0, -shaft_interval / 2.0, shaft_offset))

        return [top, bottom]

    @classmethod
    def _build_components(
        cls,
        cap_size,
        proximal_interval,
        inclination_degrees,
        cap_yaw_degrees,
        shaft_enabled,
        shaft_size,
        shaft_offset,
        shaft_interval,
    ):
        cap_width, arm_thickness, cap_length = cap_size
        inclination = inclination_degrees * DEGREES_TO_RADIANS
        cap_yaw = cap_yaw_degrees * DEGREES_TO_RADIANS
        straight_arm_length = cap_length - cap_width / 2.0
        bridge_radius = proximal_interval / 2.0 / cos(inclination) + cap_length * tan(
            inclination
        )
        bridge_z = -bridge_radius * sin(inclination) - cap_length * cos(
            inclination
        ) - shaft_offset
        arm_center_y = (bridge_radius + arm_thickness / 2.0) * cos(
            inclination
        ) - straight_arm_length * sin(inclination) / 2.0
        arm_center_z = (
            (bridge_radius + arm_thickness / 2.0) * sin(inclination)
            + straight_arm_length * cos(inclination) / 2.0
            + bridge_z
        )
        upper_arm = Cuboid(
            height=arm_thickness,
            top_length=cap_width,
            top_width=straight_arm_length,
            position=cls._centerline_plane_point(
                arm_center_y,
                arm_center_z,
                cap_yaw,
                shaft_offset,
            ),
            rotation=(inclination, cap_yaw, 0.0),
        ).with_name("upper_straight_arm")

        lower_arm = Cuboid(
            height=arm_thickness,
            top_length=cap_width,
            top_width=straight_arm_length,
            position=cls._centerline_plane_point(
                -arm_center_y,
                arm_center_z,
                cap_yaw,
                shaft_offset,
            ),
            rotation=(-inclination, cap_yaw, 0.0),
        ).with_name("lower_straight_arm")

        bridge = Ring(
            height=cap_width,
            outer_top_radius=bridge_radius + arm_thickness,
            inner_top_radius=bridge_radius,
            exist_angle=pi + inclination * 2.0,
        ).with_name("rear_curved_bridge")
        bridge.set_rotation_matrix(cls._bridge_rotation_matrix(cap_yaw))
        bridge.set_transform(
            position=cls._centerline_plane_point(0.0, bridge_z, cap_yaw, shaft_offset)
        )

        upper_terminal = Cylinder(
            height=arm_thickness,
            top_radius=cap_width / 2.0,
            is_half=True,
            rotation=(inclination, cap_yaw, 0.0),
        ).with_name("upper_round_terminal")
        upper_terminal.move_anchor_to(
            "flat_back_center",
            upper_arm.world_anchor("front_center"),
        )

        lower_terminal = Cylinder(
            height=arm_thickness,
            top_radius=cap_width / 2.0,
            is_half=True,
            rotation=(-inclination, cap_yaw, 0.0),
        ).with_name("lower_round_terminal")
        lower_terminal.move_anchor_to(
            "flat_back_center",
            lower_arm.world_anchor("front_center"),
        )

        components = [upper_arm, lower_arm, bridge, upper_terminal, lower_terminal]
        components.extend(
            cls._shaft_components(
                shaft_enabled=shaft_enabled,
                shaft_size=shaft_size,
                shaft_offset=shaft_offset,
                shaft_interval=shaft_interval,
            )
        )
        return components
