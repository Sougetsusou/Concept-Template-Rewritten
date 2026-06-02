from math import cos, pi, sin, sqrt

from code.geometry import ConceptTemplate, Cuboid, Cylinder, radial_array_frames
from code.geometry.transforms import rotate_y


_DEGREES_TO_RADIANS = pi / 180.0


class RectangularChairSeat(ConceptTemplate):
    def __init__(self, seat_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        seat_length, seat_height, seat_width = seat_size
        self._finalize_mesh(
            [
                Cuboid(
                    height=seat_height,
                    top_length=seat_length,
                    top_width=seat_width,
                ).with_name("seat_panel")
            ]
        )


class RoundChairSeat(ConceptTemplate):
    def __init__(self, radius, height, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            [
                Cylinder(
                    height=height,
                    top_radius=radius,
                ).with_name("round_seat")
            ]
        )


class SolidChairBack(ConceptTemplate):
    def __init__(
        self,
        back_size,
        back_tilt_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                back_size=back_size,
                back_tilt=back_tilt_degrees * _DEGREES_TO_RADIANS,
            )
        )

    @staticmethod
    def _build_components(back_size, back_tilt):
        back_length, back_height, back_width = back_size
        back_rotation = (back_tilt, 0, 0)
        panel = Cuboid(
            height=back_height,
            top_length=back_length,
            top_width=back_width,
            position=(0.0, 0.0, 0.0),
            rotation=back_rotation,
        ).with_name("solid_back_panel")
        bottom_x, _, bottom_z = panel.world_anchor("bottom_center")
        panel.move_anchor_to("bottom_center", (bottom_x, 0.0, bottom_z))
        return [panel]


class LadderChairBack(ConceptTemplate):
    def __init__(
        self,
        top_rail_size,
        side_rail_size,
        rung_size,
        side_rail_separation,
        rung_start_offset,
        rung_interval,
        back_tilt_degrees,
        rung_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                top_rail_size=top_rail_size,
                side_rail_size=side_rail_size,
                rung_size=rung_size,
                side_rail_separation=side_rail_separation,
                rung_start_offset=rung_start_offset,
                rung_interval=rung_interval,
                back_tilt=back_tilt_degrees * _DEGREES_TO_RADIANS,
                rung_count=int(rung_count),
            )
        )

    @staticmethod
    def _build_components(
        top_rail_size,
        side_rail_size,
        rung_size,
        side_rail_separation,
        rung_start_offset,
        rung_interval,
        back_tilt,
        rung_count,
    ):
        side_rail_length, side_rail_height, _ = side_rail_size
        _, _, side_rail_width = side_rail_size
        top_rail_length, top_rail_height, top_rail_width = top_rail_size
        rung_height, rung_width = rung_size

        left_rail = Cuboid(
            height=side_rail_height,
            top_length=side_rail_length,
            top_width=side_rail_width,
            position=(-side_rail_separation / 2.0, 0, 0),
            rotation=(back_tilt, 0, 0),
        ).with_name("left_side_rail")
        left_bottom_x, _, left_bottom_z = left_rail.world_anchor("bottom_center")
        left_rail.move_anchor_to("bottom_center", (left_bottom_x, 0.0, left_bottom_z))

        right_rail = Cuboid(
            height=side_rail_height,
            top_length=side_rail_length,
            top_width=side_rail_width,
            position=(side_rail_separation / 2.0, 0, 0),
            rotation=(back_tilt, 0, 0),
        ).with_name("right_side_rail")
        right_bottom_x, _, right_bottom_z = right_rail.world_anchor("bottom_center")
        right_rail.move_anchor_to("bottom_center", (right_bottom_x, 0.0, right_bottom_z))

        top_rail = Cuboid(
            height=top_rail_height,
            top_length=top_rail_length,
            top_width=top_rail_width,
            rotation=(back_tilt, 0, 0),
        ).with_name("top_rail")
        top_rail.move_anchor_to(
            "bottom_center",
            (left_rail.world_anchor("top_center") + right_rail.world_anchor("top_center")) / 2.0,
        )
        components = [left_rail, right_rail, top_rail]

        rung_length = side_rail_separation - side_rail_length
        for rung_index in range(rung_count):
            rung_offset = rung_start_offset - rung_index * rung_interval
            _, target_y, target_z = left_rail.world_point((0, rung_offset, 0))
            target = (0, target_y, target_z)
            rung = Cuboid(
                height=rung_height,
                top_length=rung_length,
                top_width=rung_width,
                rotation=(back_tilt, 0, 0),
            ).with_name(f"ladder_rung_{rung_index + 1}")
            rung.move_anchor_to("center", target)
            components.append(rung)

        return components


class SplatChairBack(ConceptTemplate):
    def __init__(
        self,
        top_rail_size,
        side_rail_size,
        splat_size,
        side_rail_separation,
        splat_start_offset,
        splat_interval,
        back_tilt_degrees,
        splat_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                top_rail_size=top_rail_size,
                side_rail_size=side_rail_size,
                splat_size=splat_size,
                side_rail_separation=side_rail_separation,
                splat_start_offset=splat_start_offset,
                splat_interval=splat_interval,
                back_tilt=back_tilt_degrees * _DEGREES_TO_RADIANS,
                splat_count=int(splat_count),
            )
        )

    @staticmethod
    def _build_components(
        top_rail_size,
        side_rail_size,
        splat_size,
        side_rail_separation,
        splat_start_offset,
        splat_interval,
        back_tilt,
        splat_count,
    ):
        side_rail_length, side_rail_height, side_rail_width = side_rail_size
        top_rail_length, top_rail_height, top_rail_width = top_rail_size
        splat_length, splat_width = splat_size

        left_rail = Cuboid(
            height=side_rail_height,
            top_length=side_rail_length,
            top_width=side_rail_width,
            position=(-side_rail_separation / 2.0, 0, 0),
            rotation=(back_tilt, 0, 0),
        ).with_name("left_side_rail")
        left_bottom_x, _, left_bottom_z = left_rail.world_anchor("bottom_center")
        left_rail.move_anchor_to("bottom_center", (left_bottom_x, 0.0, left_bottom_z))

        right_rail = Cuboid(
            height=side_rail_height,
            top_length=side_rail_length,
            top_width=side_rail_width,
            position=(side_rail_separation / 2.0, 0, 0),
            rotation=(back_tilt, 0, 0),
        ).with_name("right_side_rail")
        right_bottom_x, _, right_bottom_z = right_rail.world_anchor("bottom_center")
        right_rail.move_anchor_to("bottom_center", (right_bottom_x, 0.0, right_bottom_z))

        top_rail = Cuboid(
            height=top_rail_height,
            top_length=top_rail_length,
            top_width=top_rail_width,
            rotation=(back_tilt, 0, 0),
        ).with_name("top_rail")
        top_rail.move_anchor_to(
            "bottom_center",
            (left_rail.world_anchor("top_center") + right_rail.world_anchor("top_center")) / 2.0,
        )
        components = [left_rail, right_rail, top_rail]

        for splat_index in range(splat_count):
            _, target_y, target_z = left_rail.world_anchor("center")
            target = (splat_start_offset + splat_index * splat_interval, target_y, target_z)
            splat = Cuboid(
                height=side_rail_height,
                top_length=splat_length,
                top_width=splat_width,
                rotation=(back_tilt, 0, 0),
            ).with_name(f"vertical_splat_{splat_index + 1}")
            splat.move_anchor_to("center", target)
            components.append(splat)

        return components


class LatticeChairBack(ConceptTemplate):
    def __init__(
        self,
        top_rail_size,
        side_rail_size,
        side_rail_separation,
        vertical_slat_size,
        horizontal_slat_size,
        horizontal_slat_offset,
        vertical_slat_start_offset,
        vertical_slat_interval,
        back_tilt_degrees,
        vertical_slat_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                top_rail_size=top_rail_size,
                side_rail_size=side_rail_size,
                side_rail_separation=side_rail_separation,
                vertical_slat_size=vertical_slat_size,
                horizontal_slat_size=horizontal_slat_size,
                horizontal_slat_offset=horizontal_slat_offset,
                vertical_slat_start_offset=vertical_slat_start_offset,
                vertical_slat_interval=vertical_slat_interval,
                back_tilt=back_tilt_degrees * _DEGREES_TO_RADIANS,
                vertical_slat_count=int(vertical_slat_count),
            )
        )

    @staticmethod
    def _build_components(
        top_rail_size,
        side_rail_size,
        side_rail_separation,
        vertical_slat_size,
        horizontal_slat_size,
        horizontal_slat_offset,
        vertical_slat_start_offset,
        vertical_slat_interval,
        back_tilt,
        vertical_slat_count,
    ):
        side_rail_length, side_rail_height, _ = side_rail_size
        _, _, side_rail_width = side_rail_size
        top_rail_length, top_rail_height, top_rail_width = top_rail_size
        vertical_slat_length, vertical_slat_width = vertical_slat_size
        horizontal_slat_height, horizontal_slat_width = horizontal_slat_size

        left_rail = Cuboid(
            height=side_rail_height,
            top_length=side_rail_length,
            top_width=side_rail_width,
            position=(-side_rail_separation / 2.0, 0, 0),
            rotation=(back_tilt, 0, 0),
        ).with_name("left_side_rail")
        left_bottom_x, _, left_bottom_z = left_rail.world_anchor("bottom_center")
        left_rail.move_anchor_to("bottom_center", (left_bottom_x, 0.0, left_bottom_z))

        right_rail = Cuboid(
            height=side_rail_height,
            top_length=side_rail_length,
            top_width=side_rail_width,
            position=(side_rail_separation / 2.0, 0, 0),
            rotation=(back_tilt, 0, 0),
        ).with_name("right_side_rail")
        right_bottom_x, _, right_bottom_z = right_rail.world_anchor("bottom_center")
        right_rail.move_anchor_to("bottom_center", (right_bottom_x, 0.0, right_bottom_z))

        top_rail = Cuboid(
            height=top_rail_height,
            top_length=top_rail_length,
            top_width=top_rail_width,
            rotation=(back_tilt, 0, 0),
        ).with_name("top_rail")
        top_rail.move_anchor_to(
            "bottom_center",
            (left_rail.world_anchor("top_center") + right_rail.world_anchor("top_center")) / 2.0,
        )

        horizontal_slat = Cuboid(
            height=horizontal_slat_height,
            top_length=side_rail_separation - side_rail_length,
            top_width=horizontal_slat_width,
            rotation=(back_tilt, 0, 0),
        ).with_name("horizontal_lattice_slat")
        _, horizontal_slat_y, horizontal_slat_z = left_rail.world_point(
            (0, horizontal_slat_offset, 0)
        )
        horizontal_slat.move_anchor_to("center", (0, horizontal_slat_y, horizontal_slat_z))

        components = [left_rail, right_rail, top_rail, horizontal_slat]
        vertical_slat_height = (
            side_rail_height / 2.0 - horizontal_slat_height / 2.0 - horizontal_slat_offset
        )
        side_top_center = (
            left_rail.world_anchor("top_center") + right_rail.world_anchor("top_center")
        ) / 2.0
        vertical_center = (horizontal_slat.world_anchor("top_center") + side_top_center) / 2.0
        for slat_index in range(vertical_slat_count):
            slat = Cuboid(
                height=vertical_slat_height,
                top_length=vertical_slat_length,
                top_width=vertical_slat_width,
                rotation=(back_tilt, 0, 0),
            ).with_name(f"vertical_lattice_slat_{slat_index + 1}")
            _, vertical_center_y, vertical_center_z = vertical_center
            slat.move_anchor_to(
                "center",
                (
                    vertical_slat_start_offset + slat_index * vertical_slat_interval,
                    vertical_center_y,
                    vertical_center_z,
                ),
            )
            components.append(slat)

        return components


class SlatChairBack(ConceptTemplate):
    def __init__(
        self,
        side_rail_size,
        horizontal_slat_size,
        side_rail_separation,
        horizontal_slat_start_offset,
        horizontal_slat_interval,
        side_rail_splay_degrees,
        back_tilt_degrees,
        horizontal_slat_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                side_rail_size=side_rail_size,
                horizontal_slat_size=horizontal_slat_size,
                side_rail_separation=side_rail_separation,
                horizontal_slat_start_offset=horizontal_slat_start_offset,
                horizontal_slat_interval=horizontal_slat_interval,
                side_rail_splay=side_rail_splay_degrees * _DEGREES_TO_RADIANS,
                back_tilt=back_tilt_degrees * _DEGREES_TO_RADIANS,
                horizontal_slat_count=int(horizontal_slat_count),
            )
        )

    @staticmethod
    def _build_components(
        side_rail_size,
        horizontal_slat_size,
        side_rail_separation,
        horizontal_slat_start_offset,
        horizontal_slat_interval,
        side_rail_splay,
        back_tilt,
        horizontal_slat_count,
    ):
        side_rail_length, side_rail_height, side_rail_width = side_rail_size
        horizontal_slat_height, horizontal_slat_width = horizontal_slat_size
        components = []
        rails = []

        for name, side_sign in (("left_side_rail", -1), ("right_side_rail", 1)):
            rail_rotation = (back_tilt, side_sign * side_rail_splay, 0)
            rail = Cuboid(
                height=side_rail_height,
                top_length=side_rail_length,
                top_width=side_rail_width,
                position=(side_sign * side_rail_separation / 2.0, 0, 0),
                rotation=rail_rotation,
                rotation_order="ZYX",
            ).with_name(name)
            rail_bottom_x, _, rail_bottom_z = rail.world_anchor("bottom_center")
            rail.move_anchor_to("bottom_center", (rail_bottom_x, 0.0, rail_bottom_z))
            components.append(rail)
            rails.append((rail, side_sign))

        for slat_index in range(horizontal_slat_count):
            slat_offset = horizontal_slat_start_offset - slat_index * horizontal_slat_interval
            inner_points = [
                rail.world_point((-side_sign * side_rail_length / 2.0, slat_offset, 0))
                for rail, side_sign in rails
            ]
            left_inner_point, right_inner_point = inner_points
            left_inner_x, _, _ = left_inner_point
            right_inner_x, _, _ = right_inner_point
            slat = Cuboid(
                height=horizontal_slat_height,
                top_length=abs(left_inner_x - right_inner_x),
                top_width=horizontal_slat_width,
                rotation=(back_tilt, 0, 0),
            ).with_name(f"horizontal_slat_{slat_index + 1}")
            slat.move_anchor_to("center", (left_inner_point + right_inner_point) / 2.0)
            components.append(slat)

        return components


class TiltedChairLegSet(ConceptTemplate):
    def __init__(
        self,
        front_leg_size,
        rear_leg_size,
        leg_count,
        leg_center_spacing,
        central_yaw_degrees=0,
        front_tilt_degrees=(0, 0),
        rear_tilt_degrees=(0, 0),
        roll_policy="mirrored",
        mount_height=0.0,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self.leg_specs = self._leg_specs(
            leg_count=int(leg_count),
            front_leg_size=front_leg_size,
            rear_leg_size=rear_leg_size,
            leg_center_spacing=leg_center_spacing,
            central_yaw=central_yaw_degrees * _DEGREES_TO_RADIANS,
            front_tilt=tuple(
                angle * _DEGREES_TO_RADIANS for angle in front_tilt_degrees
            ),
            rear_tilt=tuple(angle * _DEGREES_TO_RADIANS for angle in rear_tilt_degrees),
            roll_policy=roll_policy,
            mount_height=mount_height,
        )
        self._finalize_mesh(
            self._build_components(
                leg_specs=self.leg_specs,
            )
        )

    @staticmethod
    def _roll_sign(leg_index, roll_policy):
        if roll_policy in (False, 0, "parallel", "same"):
            return 1
        if roll_policy in (True, 1, "mirrored", "mirror"):
            return 1 if leg_index % 2 == 0 else -1
        raise ValueError("roll_policy must be 'mirrored' or 'parallel'")

    @staticmethod
    def _leg_specs(
        leg_count,
        front_leg_size,
        rear_leg_size,
        leg_center_spacing,
        central_yaw,
        front_tilt,
        rear_tilt,
        roll_policy,
        mount_height,
    ):
        front_spacing, rear_spacing, front_rear_spacing = leg_center_spacing
        front_pitch, front_roll = front_tilt
        rear_pitch, rear_roll = rear_tilt

        specs = []
        for leg_index in range(leg_count):
            rotation_sign = TiltedChairLegSet._roll_sign(leg_index, roll_policy)
            position_sign = 1 if leg_index % 2 == 1 else -1

            if leg_count == 1:
                name = "center_front_leg"
                size = front_leg_size
                leg_rotation = (front_pitch, central_yaw, 0)
                rotation_order = "XYZ"
                center_x, center_z = 0.0, 0.0
            elif leg_count == 2:
                name = f"front_leg_{leg_index + 1}"
                size = front_leg_size
                leg_rotation = (front_pitch, central_yaw, rotation_sign * front_roll)
                rotation_order = "XZY"
                center_x = position_sign * front_spacing / 2.0 * cos(central_yaw)
                center_z = position_sign * front_spacing / 2.0 * sin(central_yaw)
            elif leg_count == 3 and leg_index < 2:
                name = f"front_leg_{leg_index + 1}"
                size = front_leg_size
                leg_rotation = (front_pitch, central_yaw, rotation_sign * front_roll)
                rotation_order = "XZY"
                center_x, _, center_z = rotate_y(
                    (
                        position_sign * front_spacing / 2.0,
                        0.0,
                        front_rear_spacing / 2.0,
                    ),
                    central_yaw,
                )
            elif leg_count == 3:
                name = "rear_center_leg"
                size = rear_leg_size
                leg_rotation = (rear_pitch, central_yaw, rear_roll)
                rotation_order = "XZY"
                center_x, _, center_z = rotate_y(
                    (0.0, 0.0, position_sign * front_rear_spacing / 2.0),
                    central_yaw,
                )
            elif leg_count == 4 and leg_index < 2:
                name = f"front_leg_{leg_index + 1}"
                size = front_leg_size
                leg_rotation = (front_pitch, central_yaw, rotation_sign * front_roll)
                rotation_order = "XZY"
                center_x, _, center_z = rotate_y(
                    (
                        position_sign * front_spacing / 2.0,
                        0.0,
                        front_rear_spacing / 2.0,
                    ),
                    central_yaw,
                )
            elif leg_count == 4:
                name = f"rear_leg_{leg_index - 1}"
                size = rear_leg_size
                leg_rotation = (rear_pitch, central_yaw, rotation_sign * rear_roll)
                rotation_order = "XZY"
                center_x, _, center_z = rotate_y(
                    (
                        position_sign * rear_spacing / 2.0,
                        0.0,
                        -front_rear_spacing / 2.0,
                    ),
                    central_yaw,
                )
            else:
                raise ValueError("leg_count must be between 1 and 4")

            specs.append(
                {
                    "name": name,
                    "size": tuple(size),
                    "rotation": leg_rotation,
                    "rotation_order": rotation_order,
                    "center_layout": (center_x, center_z),
                    "mount_height": mount_height,
                }
            )

        return specs

    @staticmethod
    def _leg(name, leg_size, center_layout, mount_height, rotation, rotation_order):
        leg_length, leg_height, leg_width = leg_size
        center_x, center_z = center_layout
        leg = Cuboid(
            height=leg_height,
            top_length=leg_length,
            top_width=leg_width,
            position=(center_x, 0.0, center_z),
            rotation=rotation,
            rotation_order=rotation_order,
        ).with_name(name)
        top_x, _, top_z = leg.world_anchor("top_center")
        leg.move_anchor_to("top_center", (top_x, mount_height, top_z))
        return leg

    @staticmethod
    def _build_components(leg_specs):
        components = []
        for leg_spec in leg_specs:
            components.append(
                TiltedChairLegSet._leg(
                    name=leg_spec["name"],
                    leg_size=leg_spec["size"],
                    center_layout=leg_spec["center_layout"],
                    mount_height=leg_spec["mount_height"],
                    rotation=leg_spec["rotation"],
                    rotation_order=leg_spec["rotation_order"],
                )
            )

        return components


class CShapedOfficeChairLeg(ConceptTemplate):
    def __init__(
        self,
        vertical_leg_size,
        z_foot_size,
        crossbar_size,
        vertical_leg_separation,
        vertical_leg_rotation_degrees,
        horizontal_leg_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                vertical_leg_size=vertical_leg_size,
                z_foot_size=z_foot_size,
                crossbar_size=crossbar_size,
                vertical_leg_separation=vertical_leg_separation,
                vertical_rotation=tuple(
                    angle * _DEGREES_TO_RADIANS for angle in vertical_leg_rotation_degrees
                ),
                horizontal_rotation=tuple(
                    angle * _DEGREES_TO_RADIANS for angle in horizontal_leg_rotation_degrees
                ),
            )
        )

    @staticmethod
    def _vertical_leg(name, leg_size, layout_x, rotation):
        leg_length, leg_height, leg_width = leg_size
        leg = Cuboid(
            height=leg_height,
            top_length=leg_length,
            top_width=leg_width,
            position=(layout_x, 0, 0),
            rotation=rotation,
            rotation_order="ZXY",
        ).with_name(name)
        top_x, _, top_z = leg.world_anchor("top_center")
        leg.move_anchor_to("top_center", (top_x, 0.0, top_z))
        return leg

    @staticmethod
    def _build_components(
        vertical_leg_size,
        z_foot_size,
        crossbar_size,
        vertical_leg_separation,
        vertical_rotation,
        horizontal_rotation,
    ):
        vertical_leg_length, vertical_leg_height, vertical_leg_width = vertical_leg_size
        z_foot_height, z_foot_width = z_foot_size
        crossbar_width, = crossbar_size
        vertical_pitch, vertical_roll = vertical_rotation
        horizontal_pitch, horizontal_roll = horizontal_rotation
        components = []
        vertical_legs = {}
        z_feet = {}

        for side_name, name, rotation_sign, position_sign in (
            ("right", "right_vertical_leg", 1, 1),
            ("left", "left_vertical_leg", -1, -1),
        ):
            leg = CShapedOfficeChairLeg._vertical_leg(
                name,
                vertical_leg_size,
                position_sign * vertical_leg_separation / 2.0,
                (vertical_pitch, 0, rotation_sign * vertical_roll),
            )
            vertical_legs[side_name] = leg
            components.append(leg)

        for side_name, name, rotation_sign in (
            ("right", "right_z_foot", 1),
            ("left", "left_z_foot", -1),
        ):
            foot = Cuboid(
                height=z_foot_height,
                top_length=vertical_leg_length,
                top_width=z_foot_width,
                rotation=(horizontal_pitch, rotation_sign * horizontal_roll, 0),
                rotation_order="YXZ",
            ).with_name(name)
            foot.move_anchor_to(
                "bottom_front_center",
                vertical_legs[side_name].world_anchor("bottom_back_center"),
            )
            z_feet[side_name] = foot
            components.append(foot)

        left_crossbar_end = z_feet["left"].world_anchor("back_left_center")
        right_crossbar_end = z_feet["right"].world_anchor("back_right_center")
        crossbar_front_mount = (
            z_feet["left"].world_anchor("back_center")
            + z_feet["right"].world_anchor("back_center")
        ) / 2.0
        crossbar_span = CShapedOfficeChairLeg._distance(
            left_crossbar_end,
            right_crossbar_end,
        )
        crossbar = Cuboid(
            height=z_foot_height,
            top_length=crossbar_span,
            top_width=crossbar_width,
            rotation=(horizontal_pitch, 0, 0),
        ).with_name("front_crossbar")
        crossbar.move_anchor_to("front_center", crossbar_front_mount)
        components.append(crossbar)

        return components

    @staticmethod
    def _distance(start_point, end_point):
        diff_x, diff_y, diff_z = end_point - start_point
        return sqrt(diff_x ** 2 + diff_y ** 2 + diff_z ** 2)


class StarChairLeg(ConceptTemplate):
    def __init__(
        self,
        center_column_size,
        spoke_size,
        spoke_center_offset,
        spoke_tilt_degrees,
        central_yaw_degrees,
        horizontal_tilt_degrees,
        spoke_count,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                center_column_size=center_column_size,
                spoke_size=spoke_size,
                spoke_center_offset=spoke_center_offset,
                spoke_tilt=spoke_tilt_degrees * _DEGREES_TO_RADIANS,
                central_yaw=central_yaw_degrees * _DEGREES_TO_RADIANS,
                horizontal_tilt=horizontal_tilt_degrees * _DEGREES_TO_RADIANS,
                spoke_count=int(spoke_count),
            )
        )

    @staticmethod
    def _build_components(
        center_column_size,
        spoke_size,
        spoke_center_offset,
        spoke_tilt,
        central_yaw,
        horizontal_tilt,
        spoke_count,
    ):
        column_radius, column_height = center_column_size
        spoke_length, spoke_height, spoke_width = spoke_size
        components = [
            Cylinder(
                height=column_height,
                top_radius=column_radius,
                rotation=(horizontal_tilt, central_yaw, 0),
            ).with_name("center_column")
        ]
        spoke_center_y = -column_height / 2.0 + spoke_height / 2.0 + spoke_center_offset
        spoke_radial_center = spoke_width / 2.0 * cos(spoke_tilt)
        spoke_frames = radial_array_frames(
            count=spoke_count,
            center_point=(0.0, spoke_center_y, spoke_radial_center),
            item_rotation=(spoke_tilt, 0.0, 0.0),
            radial_axis="y",
            angle_sign=-1.0,
            post_rotation_steps=(
                ((0.0, central_yaw, 0.0), "XYZ"),
                ((horizontal_tilt, 0.0, 0.0), "XYZ"),
            ),
        )

        for spoke_frame in spoke_frames:
            spoke = Cuboid(
                height=spoke_height,
                top_length=spoke_length,
                top_width=spoke_width,
                position=spoke_frame.position,
            ).with_name(f"radial_spoke_{spoke_frame.index + 1}")
            spoke.set_rotation_matrix(spoke_frame.rotation_matrix)
            components.append(spoke)

        return components


class StretcherChairLegSet(ConceptTemplate):
    def __init__(
        self,
        front_leg_size,
        rear_leg_size,
        leg_center_spacing,
        central_yaw_degrees,
        front_tilt_degrees,
        rear_tilt_degrees,
        front_rear_stretcher_size,
        side_stretcher_size,
        front_rear_stretcher_offset,
        side_stretcher_offset,
        stretcher_enabled,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self.leg_specs = self._leg_specs(
            front_leg_size=front_leg_size,
            rear_leg_size=rear_leg_size,
            leg_center_spacing=leg_center_spacing,
            central_yaw=central_yaw_degrees * _DEGREES_TO_RADIANS,
            front_tilt=tuple(
                angle * _DEGREES_TO_RADIANS for angle in front_tilt_degrees
            ),
            rear_tilt=tuple(angle * _DEGREES_TO_RADIANS for angle in rear_tilt_degrees),
        )
        self._finalize_mesh(
            self._build_components(
                leg_specs=self.leg_specs,
                front_rear_stretcher_size=front_rear_stretcher_size,
                side_stretcher_size=side_stretcher_size,
                front_rear_stretcher_offset=front_rear_stretcher_offset,
                side_stretcher_offset=side_stretcher_offset,
                stretcher_enabled=tuple(stretcher_enabled),
            )
        )

    @staticmethod
    def _leg_specs(
        front_leg_size,
        rear_leg_size,
        leg_center_spacing,
        central_yaw,
        front_tilt,
        rear_tilt,
    ):
        front_separation, rear_separation, front_rear_separation = leg_center_spacing
        front_pitch, front_roll = front_tilt
        rear_pitch, rear_roll = rear_tilt

        specs = []
        for name, rotation_sign, position_sign in (
            ("front_left_leg", 1, -1),
            ("front_right_leg", -1, 1),
        ):
            layout_x, _, layout_z = rotate_y(
                (
                    position_sign * front_separation / 2.0,
                    0.0,
                    front_rear_separation / 2.0,
                ),
                central_yaw,
            )
            rotation = (front_pitch, central_yaw, rotation_sign * front_roll)
            specs.append(
                {
                    "name": name,
                    "size": tuple(front_leg_size),
                    "rotation": rotation,
                    "center_layout": (layout_x, layout_z),
                    "mount_height": 0.0,
                }
            )

        for name, rotation_sign, position_sign in (
            ("rear_left_leg", 1, -1),
            ("rear_right_leg", -1, 1),
        ):
            layout_x, _, layout_z = rotate_y(
                (
                    position_sign * rear_separation / 2.0,
                    0.0,
                    -front_rear_separation / 2.0,
                ),
                central_yaw,
            )
            rotation = (rear_pitch, central_yaw, rotation_sign * rear_roll)
            specs.append(
                {
                    "name": name,
                    "size": tuple(rear_leg_size),
                    "rotation": rotation,
                    "center_layout": (layout_x, layout_z),
                    "mount_height": 0.0,
                }
            )

        return specs

    @staticmethod
    def _leg(name, leg_size, center_layout, mount_height, rotation):
        leg_length, leg_height, leg_width = leg_size
        center_x, center_z = center_layout
        leg = Cuboid(
            height=leg_height,
            top_length=leg_length,
            top_width=leg_width,
            position=(center_x, 0.0, center_z),
            rotation=rotation,
            rotation_order="XZY",
        ).with_name(name)
        top_x, _, top_z = leg.world_anchor("top_center")
        leg.move_anchor_to("top_center", (top_x, mount_height, top_z))
        return leg

    @staticmethod
    def _build_components(
        leg_specs,
        front_rear_stretcher_size,
        side_stretcher_size,
        front_rear_stretcher_offset,
        side_stretcher_offset,
        stretcher_enabled,
    ):
        front_rear_bar_height, front_rear_bar_width = front_rear_stretcher_size
        side_bar_length, side_bar_height = side_stretcher_size
        front_bar_offset, rear_bar_offset = front_rear_stretcher_offset
        side_front_offset, side_rear_offset = side_stretcher_offset
        front_bar_enabled, rear_bar_enabled, left_bar_enabled, right_bar_enabled = stretcher_enabled

        components = []
        legs = {}
        for leg_spec in leg_specs:
            leg = StretcherChairLegSet._leg(
                name=leg_spec["name"],
                leg_size=leg_spec["size"],
                center_layout=leg_spec["center_layout"],
                mount_height=leg_spec["mount_height"],
                rotation=leg_spec["rotation"],
            )
            legs[leg_spec["name"]] = leg
            components.append(leg)

        front_leg_length = legs["front_left_leg"].top_length
        front_leg_width = legs["front_left_leg"].top_width
        rear_leg_length = legs["rear_left_leg"].top_length
        rear_leg_width = legs["rear_left_leg"].top_width

        if front_bar_enabled == 1:
            front_bar = StretcherChairLegSet._cross_stretcher(
                name="front_cross_stretcher",
                left_leg=legs["front_left_leg"],
                right_leg=legs["front_right_leg"],
                offset=front_bar_offset,
                leg_length=front_leg_length,
                bar_height=front_rear_bar_height,
                bar_width=front_rear_bar_width,
            )
            if front_bar is not None:
                components.append(front_bar)

        if rear_bar_enabled == 1:
            rear_bar = StretcherChairLegSet._cross_stretcher(
                name="rear_cross_stretcher",
                left_leg=legs["rear_left_leg"],
                right_leg=legs["rear_right_leg"],
                offset=rear_bar_offset,
                leg_length=rear_leg_length,
                bar_height=front_rear_bar_height,
                bar_width=front_rear_bar_width,
            )
            if rear_bar is not None:
                components.append(rear_bar)

        if left_bar_enabled == 1:
            left_bar = StretcherChairLegSet._side_stretcher(
                name="left_side_stretcher",
                front_leg=legs["front_left_leg"],
                rear_leg=legs["rear_left_leg"],
                front_leg_width=front_leg_width,
                rear_leg_width=rear_leg_width,
                front_offset=side_front_offset,
                rear_offset=side_rear_offset,
                side_bar_length=side_bar_length,
                side_bar_height=side_bar_height,
            )
            if left_bar is not None:
                components.append(left_bar)

        if right_bar_enabled == 1:
            right_bar = StretcherChairLegSet._side_stretcher(
                name="right_side_stretcher",
                front_leg=legs["front_right_leg"],
                rear_leg=legs["rear_right_leg"],
                front_leg_width=front_leg_width,
                rear_leg_width=rear_leg_width,
                front_offset=side_front_offset,
                rear_offset=side_rear_offset,
                side_bar_length=side_bar_length,
                side_bar_height=side_bar_height,
            )
            if right_bar is not None:
                components.append(right_bar)

        return components

    @staticmethod
    def _distance(start_point, end_point):
        diff_x, diff_y, diff_z = end_point - start_point
        return sqrt(diff_x ** 2 + diff_y ** 2 + diff_z ** 2)

    @staticmethod
    def _cross_stretcher(
        name,
        left_leg,
        right_leg,
        offset,
        leg_length,
        bar_height,
        bar_width,
    ):
        left_mount = left_leg.world_point((0.0, offset, 0.0))
        right_mount = right_leg.world_point((0.0, offset, 0.0))
        span = StretcherChairLegSet._distance(left_mount, right_mount)
        if span <= 0:
            return None

        bar = Cuboid(
            height=bar_height,
            top_length=span - leg_length,
            top_width=bar_width,
        )
        bar.align_axis_between_points("x", left_mount, right_mount)
        return bar.with_name(name)

    @staticmethod
    def _side_stretcher(
        name,
        front_leg,
        rear_leg,
        front_leg_width,
        rear_leg_width,
        front_offset,
        rear_offset,
        side_bar_length,
        side_bar_height,
    ):
        front_mount = front_leg.world_point((0.0, front_offset, 0.0))
        rear_mount = rear_leg.world_point((0.0, rear_offset, 0.0))
        span = StretcherChairLegSet._distance(rear_mount, front_mount)
        if span <= 0:
            return None

        bar = Cuboid(
            height=side_bar_height,
            top_length=side_bar_length,
            top_width=span - (front_leg_width + rear_leg_width) / 2.0,
        )
        bar.align_axis_between_points("z", rear_mount, front_mount)
        return bar.with_name(name)


class BarstoolPedestalLeg(ConceptTemplate):
    def __init__(
        self,
        column_size,
        base_size,
        horizontal_tilt_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                column_size=column_size,
                base_size=base_size,
                horizontal_tilt=horizontal_tilt_degrees * _DEGREES_TO_RADIANS,
            )
        )

    @staticmethod
    def _build_components(column_size, base_size, horizontal_tilt):
        column_radius, column_height = column_size
        base_radius, base_height = base_size
        column = Cylinder(
            height=column_height,
            top_radius=column_radius,
            rotation=(horizontal_tilt, 0, 0),
        ).with_name("center_column")
        column_top_x, _, column_top_z = column.world_anchor("top_center")
        column.move_anchor_to("top_center", (column_top_x, 0.0, column_top_z))

        base = Cylinder(
            height=base_height,
            top_radius=base_radius,
            rotation=(horizontal_tilt, 0, 0),
        ).with_name("floor_base")
        base_top_x, base_top_y, _ = column.world_anchor("bottom_center")
        _, _, base_top_z = column.world_anchor("top_center")
        base.move_anchor_to("top_center", (base_top_x, base_top_y, base_top_z))
        return [column, base]


class SolidChairArmrest(ConceptTemplate):
    def __init__(
        self,
        armrest_size,
        armrest_separation,
        armrest_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                armrest_size=armrest_size,
                armrest_separation=armrest_separation,
                armrest_rotation=tuple(
                    angle * _DEGREES_TO_RADIANS for angle in armrest_rotation_degrees
                ),
            )
        )

    @staticmethod
    def _build_components(armrest_size, armrest_separation, armrest_rotation):
        armrest_length, armrest_height, armrest_width = armrest_size
        armrest_pitch, armrest_roll = armrest_rotation
        components = []
        for name, side_flag in (("left_armrest", 1), ("right_armrest", -1)):
            armrest = Cuboid(
                height=armrest_height,
                top_length=armrest_length,
                top_width=armrest_width,
                position=(-side_flag * armrest_separation / 2.0, 0.0, 0.0),
                rotation=(armrest_pitch, 0, side_flag * armrest_roll),
            ).with_name(name)
            mount_x, _, mount_z = armrest.world_anchor("bottom_back_center")
            armrest.move_anchor_to("bottom_back_center", (mount_x, 0.0, mount_z))
            components.append(armrest)
        return components


class OfficeChairArmrest(ConceptTemplate):
    def __init__(
        self,
        horizontal_support_size,
        vertical_support_size,
        support_contact_offset,
        vertical_support_rotation_degrees,
        horizontal_support_rotation_degrees,
        armrest_separation,
        armrest_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                horizontal_support_size=horizontal_support_size,
                vertical_support_size=vertical_support_size,
                support_contact_offset=support_contact_offset,
                vertical_support_rotation=vertical_support_rotation_degrees
                * _DEGREES_TO_RADIANS,
                horizontal_support_rotation=horizontal_support_rotation_degrees
                * _DEGREES_TO_RADIANS,
                armrest_separation=armrest_separation,
                armrest_rotation=armrest_rotation_degrees * _DEGREES_TO_RADIANS,
            )
        )

    @staticmethod
    def _build_components(
        horizontal_support_size,
        vertical_support_size,
        support_contact_offset,
        vertical_support_rotation,
        horizontal_support_rotation,
        armrest_separation,
        armrest_rotation,
    ):
        horizontal_length, horizontal_height, horizontal_width = horizontal_support_size
        vertical_length, vertical_height, vertical_width = vertical_support_size
        components = []
        vertical_supports = {}

        for name, side_flag in (("left_vertical_support", 1), ("right_vertical_support", -1)):
            vertical_support = Cuboid(
                height=vertical_height,
                top_length=vertical_length,
                top_width=vertical_width,
                position=(
                    -side_flag * armrest_separation / 2.0,
                    0.0,
                    support_contact_offset,
                ),
                rotation=(vertical_support_rotation, 0, side_flag * armrest_rotation),
                rotation_order="YXZ",
            ).with_name(name)
            mount_x, _, mount_z = vertical_support.world_anchor("bottom_center")
            vertical_support.move_anchor_to("bottom_center", (mount_x, 0.0, mount_z))
            components.append(vertical_support)
            vertical_supports[side_flag] = vertical_support

        for name, side_flag in (("left_horizontal_support", 1), ("right_horizontal_support", -1)):
            support = Cuboid(
                height=horizontal_height,
                top_length=horizontal_length,
                top_width=horizontal_width,
                rotation=(horizontal_support_rotation, 0, side_flag * armrest_rotation),
                rotation_order="YXZ",
            ).with_name(name)
            support_top = vertical_supports[side_flag].world_anchor("top_center")
            support.move_local_point_axes_to(
                (0.0, -horizontal_height / 2.0, support_contact_offset),
                support_top,
                ("x", "y"),
            )
            components.append(support)

        return components
