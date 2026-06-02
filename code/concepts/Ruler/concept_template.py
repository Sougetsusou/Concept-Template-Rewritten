from math import pi

from code.geometry import ConceptTemplate, Cuboid, Cylinder


DEGREES_TO_RADIANS = pi / 180.0
RULER_ROTATION_ORDER = "YXZ"


class SymmetricalRulerBody(ConceptTemplate):
    def __init__(
        self,
        body_size,
        inner_anchor_offset_x,
        lateral_offset_z,
        body_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=RULER_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                body_size=body_size,
                inner_anchor_offset_x=inner_anchor_offset_x,
                lateral_offset_z=lateral_offset_z,
                body_rotation_degrees=body_rotation_degrees,
            )
        )
        self.semantic = "Ruler"

    @staticmethod
    def _build_components(
        body_size,
        inner_anchor_offset_x,
        lateral_offset_z,
        body_rotation_degrees,
    ):
        body_length, body_thickness, body_width = body_size
        body_rotation = body_rotation_degrees * DEGREES_TO_RADIANS
        components = []

        for name, rotation_z, inner_anchor, target_x, target_z in (
            (
                "left_body",
                body_rotation,
                "bottom_right_center",
                -inner_anchor_offset_x,
                -lateral_offset_z,
            ),
            (
                "right_body",
                -body_rotation,
                "bottom_left_center",
                inner_anchor_offset_x,
                lateral_offset_z,
            ),
        ):
            body = Cuboid(
                height=body_thickness,
                top_length=body_length,
                top_width=body_width,
                rotation=(0.0, 0.0, rotation_z),
            ).with_name(name)
            body.move_anchor_to(inner_anchor, (target_x, 0.0, target_z))
            components.append(body)

        return components


class AsymmetricalRulerBody(ConceptTemplate):
    def __init__(
        self,
        left_body_size,
        right_body_size,
        inner_anchor_offset_x,
        lateral_offset_z,
        body_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=RULER_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                left_body_size=left_body_size,
                right_body_size=right_body_size,
                inner_anchor_offset_x=inner_anchor_offset_x,
                lateral_offset_z=lateral_offset_z,
                body_rotation_degrees=body_rotation_degrees,
            )
        )
        self.semantic = "Ruler"

    @staticmethod
    def _build_components(
        left_body_size,
        right_body_size,
        inner_anchor_offset_x,
        lateral_offset_z,
        body_rotation_degrees,
    ):
        body_rotation = body_rotation_degrees * DEGREES_TO_RADIANS
        components = []

        for (
            name,
            body_size,
            rotation_z,
            inner_anchor,
            target_x,
            target_z,
        ) in (
            (
                "left_body",
                left_body_size,
                body_rotation,
                "bottom_right_center",
                -inner_anchor_offset_x,
                -lateral_offset_z,
            ),
            (
                "right_body",
                right_body_size,
                -body_rotation,
                "bottom_left_center",
                inner_anchor_offset_x,
                lateral_offset_z,
            ),
        ):
            body_length, body_thickness, body_width = body_size
            body = Cuboid(
                height=body_thickness,
                top_length=body_length,
                top_width=body_width,
                rotation=(0.0, 0.0, rotation_z),
            ).with_name(name)
            body.move_anchor_to(inner_anchor, (target_x, 0.0, target_z))
            components.append(body)

        return components


class CylindricalRulerShaft(ConceptTemplate):
    def __init__(self, shaft_radius, shaft_length, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=RULER_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            [
                Cylinder(
                    height=shaft_length,
                    top_radius=shaft_radius,
                    rotation=(pi / 2.0, 0.0, 0.0),
                ).with_name("shaft")
            ]
        )
        self.semantic = "Shaft"
