from math import pi

from code.geometry_rewritten import ConceptTemplate, Cuboid, Rectangular_Ring


DEGREES_TO_RADIANS = pi / 180.0
SHAVER_ROTATION_ORDER = "YXZ"


class LoopShaverBody(ConceptTemplate):
    def __init__(
        self,
        end_lengths,
        opening_length,
        frame_thickness,
        outer_depth,
        side_wall_thickness,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SHAVER_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                end_lengths=end_lengths,
                opening_length=opening_length,
                frame_thickness=frame_thickness,
                outer_depth=outer_depth,
                side_wall_thickness=side_wall_thickness,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        end_lengths,
        opening_length,
        frame_thickness,
        outer_depth,
        side_wall_thickness,
    ):
        top_end_length, bottom_end_length = end_lengths
        outer_length = top_end_length + opening_length + bottom_end_length
        opening_depth = outer_depth - side_wall_thickness * 2.0
        end_asymmetry_offset = (top_end_length - bottom_end_length) / 2.0

        body_loop = Rectangular_Ring(
            front_height=frame_thickness,
            outer_top_length=outer_length,
            outer_top_width=outer_depth,
            inner_top_length=opening_length,
            inner_top_width=opening_depth,
            inner_offset=(end_asymmetry_offset, 0.0),
            top_bottom_offset=(0.0, 0.0),
            position=(0.0, end_asymmetry_offset, 0.0),
            rotation=(0.0, 0.0, -pi / 2.0),
        ).with_name("body_loop")
        return [body_loop]


class TwoSegmentShaverBlade(ConceptTemplate):
    def __init__(
        self,
        root_segment_size,
        tip_segment_size,
        tip_vertical_offset,
        root_origin_offset,
        blade_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SHAVER_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                root_segment_size=root_segment_size,
                tip_segment_size=tip_segment_size,
                tip_vertical_offset=tip_vertical_offset,
                root_origin_offset=root_origin_offset,
                blade_rotation_degrees=blade_rotation_degrees,
            )
        )
        self.semantic = "Blade"

    @staticmethod
    def _build_components(
        root_segment_size,
        tip_segment_size,
        tip_vertical_offset,
        root_origin_offset,
        blade_rotation_degrees,
    ):
        root_length, root_height, root_depth = root_segment_size
        tip_length, tip_height, tip_depth = tip_segment_size
        root_origin_offset_x = root_origin_offset
        blade_rotation = -blade_rotation_degrees * DEGREES_TO_RADIANS

        root_segment = Cuboid(
            height=root_height,
            top_length=root_length,
            top_width=root_depth,
        ).with_name("root_blade_segment")
        root_pivot_on_top_face = (
            -root_length / 2.0 + root_origin_offset_x,
            root_height / 2.0,
            0.0,
        )
        root_segment.move_local_point_to(root_pivot_on_top_face, (0.0, 0.0, 0.0))

        tip_segment = Cuboid(
            height=tip_height,
            top_length=tip_length,
            top_width=tip_depth,
        ).with_name("tip_blade_segment")
        root_end_x, root_end_y, root_end_z = root_segment.world_anchor("right_center")
        tip_segment.move_anchor_to(
            "left_center",
            (
                root_end_x,
                root_end_y + tip_vertical_offset,
                root_end_z,
            ),
        )

        for segment in (root_segment, tip_segment):
            segment.rotate_about_point(
                pivot_point=(0.0, 0.0, 0.0),
                rotation=(0.0, 0.0, blade_rotation),
            )

        return [root_segment, tip_segment]
