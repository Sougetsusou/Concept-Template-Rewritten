from math import pi

from code.geometry import ConceptTemplate, Cuboid, Ring


DEGREES_TO_RADIANS = pi / 180.0


class RegularFoldingRack(ConceptTemplate):
    def __init__(
        self,
        rail_size,
        open_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                rail_size=rail_size,
                open_angle_degrees=open_angle_degrees,
            )
        )
        self.semantic = "Rack"

    @staticmethod
    def _build_components(rail_size, open_angle_degrees):
        rail_thickness, rail_length, rail_depth = rail_size
        open_angle = open_angle_degrees * DEGREES_TO_RADIANS

        lower_rail = Cuboid(
            height=rail_length,
            top_length=rail_thickness,
            top_width=rail_depth,
            rotation=(0.0, 0.0, open_angle),
        ).with_name("lower_folding_rail")
        lower_rail.move_anchor_to("top_left_center", (0.0, 0.0, 0.0))

        upper_rail = Cuboid(
            height=rail_length,
            top_length=rail_thickness,
            top_width=rail_depth,
            rotation=(0.0, 0.0, -open_angle),
        ).with_name("upper_folding_rail")
        upper_rail.move_anchor_to("bottom_left_center", (0.0, 0.0, 0.0))

        return [lower_rail, upper_rail]


class CurvedFoldingRack(ConceptTemplate):
    def __init__(
        self,
        rail_size,
        end_radius,
        end_arc_angle_degrees,
        open_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                rail_size=rail_size,
                end_radius=end_radius,
                end_arc_angle_degrees=end_arc_angle_degrees,
                open_angle_degrees=open_angle_degrees,
            )
        )
        self.semantic = "Rack"

    @classmethod
    def _build_components(
        cls,
        rail_size,
        end_radius,
        end_arc_angle_degrees,
        open_angle_degrees,
    ):
        rail_thickness, rail_length, rail_depth = rail_size
        open_angle = open_angle_degrees * DEGREES_TO_RADIANS
        end_arc_angle = end_arc_angle_degrees * DEGREES_TO_RADIANS

        lower_rail, upper_rail = RegularFoldingRack._build_components(
            rail_size=rail_size,
            open_angle_degrees=open_angle_degrees,
        )

        upper_end_center = cls._end_arc_center(
            rail=upper_rail,
            end_anchor="top_left_center",
            end_radius=end_radius,
        )
        upper_end_arc = Ring(
            height=rail_depth,
            outer_top_radius=end_radius,
            inner_top_radius=end_radius - rail_thickness,
            exist_angle=end_arc_angle,
            rotation=(pi / 2.0, 0.0, pi - open_angle),
        ).with_name("upper_end_arc")
        upper_end_arc.move_anchor_to("arc_origin", upper_end_center)

        lower_end_center = cls._end_arc_center(
            rail=lower_rail,
            end_anchor="bottom_left_center",
            end_radius=end_radius,
        )
        lower_end_arc = Ring(
            height=rail_depth,
            outer_top_radius=end_radius,
            inner_top_radius=end_radius - rail_thickness,
            exist_angle=end_arc_angle,
            rotation=(-pi / 2.0, 0.0, pi + open_angle),
        ).with_name("lower_end_arc")
        lower_end_arc.move_anchor_to("arc_origin", lower_end_center)

        return [lower_rail, upper_rail, upper_end_arc, lower_end_arc]

    @staticmethod
    def _end_arc_center(rail, end_anchor, end_radius):
        right_face_frame = rail.world_anchor_frame("right_center")
        return rail.world_anchor(end_anchor) + right_face_frame.normal * end_radius


class RegularFoldingHook(ConceptTemplate):
    def __init__(
        self,
        base_size,
        arm_size,
        arm_mount_offset,
        arm_rotation_degrees,
        hook_radius,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                base_size=base_size,
                arm_size=arm_size,
                arm_mount_offset=arm_mount_offset,
                arm_rotation_degrees=arm_rotation_degrees,
                hook_radius=hook_radius,
            )
        )
        self.semantic = "Hook"

    @staticmethod
    def _build_components(
        base_size,
        arm_size,
        arm_mount_offset,
        arm_rotation_degrees,
        hook_radius,
    ):
        base_length, base_height, base_depth = base_size
        arm_length, arm_height, arm_depth = arm_size
        arm_offset_y, arm_offset_z = arm_mount_offset
        arm_rotation = arm_rotation_degrees * DEGREES_TO_RADIANS

        base = Cuboid(
            height=base_height,
            top_length=base_length,
            top_width=base_depth,
        ).with_name("wall_base")
        base.move_anchor_to("right_center", (0.0, 0.0, 0.0))

        base_left_x, base_left_y, base_left_z = base.world_anchor("left_center")
        arm_mount = (
            base_left_x,
            base_left_y + arm_offset_y,
            base_left_z + arm_offset_z,
        )
        arm = Cuboid(
            height=arm_height,
            top_length=arm_length,
            top_width=arm_depth,
            rotation=(0.0, 0.0, -arm_rotation),
        ).with_name("slanted_hook_arm")
        arm.move_anchor_to("right_center", arm_mount)

        arm_tip_x, arm_tip_y, arm_tip_z = arm.world_anchor("top_left_center")
        hook_arc_center = (arm_tip_x, arm_tip_y - hook_radius, arm_tip_z)
        hook_arc = Ring(
            height=arm_depth,
            outer_top_radius=hook_radius,
            inner_top_radius=hook_radius - arm_height,
            exist_angle=pi,
            rotation=(pi / 2.0, 0.0, -pi / 2.0),
        ).with_name("lower_hook_arc")
        hook_arc.move_anchor_to("arc_origin", hook_arc_center)

        return [base, arm, hook_arc]
