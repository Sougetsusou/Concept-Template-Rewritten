from math import pi

from code.geometry_rewritten import ConceptTemplate, Cuboid, Cylinder


DOORHANDLE_ROTATION_ORDER = "YXZ"
CYLINDER_POINTS_OUTWARD = (pi / 2.0, 0.0, 0.0)


class LayeredCuboidDoorHandle(ConceptTemplate):
    def __init__(
        self,
        fixed_plate_size,
        vertical_grip_size,
        horizontal_grip_size,
        vertical_grip_offset,
        horizontal_grip_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DOORHANDLE_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                fixed_plate_size=fixed_plate_size,
                vertical_grip_size=vertical_grip_size,
                horizontal_grip_size=horizontal_grip_size,
                vertical_grip_offset=vertical_grip_offset,
                horizontal_grip_offset=horizontal_grip_offset,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(
        fixed_plate_size,
        vertical_grip_size,
        horizontal_grip_size,
        vertical_grip_offset,
        horizontal_grip_offset,
    ):
        fixed_plate_length, fixed_plate_height, fixed_plate_depth = fixed_plate_size
        vertical_grip_length, vertical_grip_height, vertical_grip_depth = vertical_grip_size
        horizontal_grip_length, horizontal_grip_height, horizontal_grip_depth = (
            horizontal_grip_size
        )
        vertical_offset_x, vertical_offset_y = vertical_grip_offset
        horizontal_offset_x, horizontal_offset_y = horizontal_grip_offset

        fixed_plate = Cuboid(
            height=fixed_plate_height,
            top_length=fixed_plate_length,
            top_width=fixed_plate_depth,
        ).with_name("fixed_plate")
        fixed_plate.move_anchor_to("back_center", (0.0, 0.0, 0.0))

        vertical_grip = Cuboid(
            height=vertical_grip_height,
            top_length=vertical_grip_length,
            top_width=vertical_grip_depth,
        ).with_name("vertical_grip")
        vertical_grip.move_anchor_to(
            "back_center",
            fixed_plate.world_anchor("front_center")
            + (vertical_offset_x, vertical_offset_y, 0.0),
        )

        horizontal_grip = Cuboid(
            height=horizontal_grip_height,
            top_length=horizontal_grip_length,
            top_width=horizontal_grip_depth,
        ).with_name("horizontal_grip")
        horizontal_grip.move_anchor_to(
            "back_center",
            vertical_grip.world_anchor("front_center")
            + (horizontal_offset_x, horizontal_offset_y, 0.0),
        )

        return [fixed_plate, vertical_grip, horizontal_grip]


class StackedCylindricalDoorKnob(ConceptTemplate):
    def __init__(
        self,
        fixed_base_size,
        neck_size,
        knob_size,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DOORHANDLE_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                fixed_base_size=fixed_base_size,
                neck_size=neck_size,
                knob_size=knob_size,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(fixed_base_size, neck_size, knob_size):
        fixed_base_radius, fixed_base_depth = fixed_base_size
        neck_radius, neck_depth = neck_size
        knob_radius, knob_depth = knob_size

        fixed_base = Cylinder(
            height=fixed_base_depth,
            top_radius=fixed_base_radius,
            bottom_radius=fixed_base_radius,
            rotation=CYLINDER_POINTS_OUTWARD,
        ).with_name("fixed_base")
        fixed_base.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        neck = Cylinder(
            height=neck_depth,
            top_radius=neck_radius,
            bottom_radius=neck_radius,
            rotation=CYLINDER_POINTS_OUTWARD,
        ).with_name("neck")
        neck.move_anchor_to("bottom_center", fixed_base.world_anchor("top_center"))

        knob = Cylinder(
            height=knob_depth,
            top_radius=knob_radius,
            bottom_radius=knob_radius,
            rotation=CYLINDER_POINTS_OUTWARD,
        ).with_name("knob")
        knob.move_anchor_to("bottom_center", neck.world_anchor("top_center"))

        return [fixed_base, neck, knob]


class TShapedDoorHandle(ConceptTemplate):
    def __init__(
        self,
        stem_size,
        crossbar_size,
        crossbar_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DOORHANDLE_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                stem_size=stem_size,
                crossbar_size=crossbar_size,
                crossbar_offset=crossbar_offset,
            )
        )
        self.semantic = "Handle"

    @staticmethod
    def _build_components(stem_size, crossbar_size, crossbar_offset):
        stem_diameter, stem_depth = stem_size
        crossbar_length, crossbar_height, crossbar_depth = crossbar_size
        crossbar_offset_x, crossbar_offset_y = crossbar_offset

        stem = Cylinder(
            height=stem_depth,
            top_radius=stem_diameter / 2.0,
            bottom_radius=stem_diameter / 2.0,
            rotation=CYLINDER_POINTS_OUTWARD,
        ).with_name("stem")
        stem.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        crossbar = Cuboid(
            height=crossbar_height,
            top_length=crossbar_length,
            top_width=crossbar_depth,
        ).with_name("crossbar")
        crossbar.move_anchor_to(
            "back_center",
            stem.world_anchor("top_center") + (crossbar_offset_x, crossbar_offset_y, 0.0),
        )

        return [stem, crossbar]
