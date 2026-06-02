from math import cos, pi, sin, tan

import numpy as np

from code.geometry_rewritten import ConceptTemplate, Cuboid, Cylinder, transform_direction


DEGREES_TO_RADIANS = pi / 180.0
DISPENSER_ROTATION_ORDER = "YXZ"


class StackedDispenserBody(ConceptTemplate):
    def __init__(self, profile_sections, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPENSER_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(profile_sections=profile_sections))
        self.semantic = "Body"

    @staticmethod
    def _build_components(profile_sections):
        components = []
        previous_top_anchor = None

        for section_index, section in enumerate(profile_sections):
            section_primitive = Cylinder(
                height=section["height"],
                top_radius=section["top_radius"],
                bottom_radius=section["bottom_radius"],
            ).with_name(section["name"])

            if section_index > 0:
                section_primitive.move_anchor_to("bottom_center", previous_top_anchor)

            previous_top_anchor = section_primitive.world_anchor("top_center")
            components.append(section_primitive)

        return components


class RectangularDispenserBody(ConceptTemplate):
    def __init__(self, body_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPENSER_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(body_size=body_size))
        self.semantic = "Body"

    @staticmethod
    def _build_components(body_size):
        body_length, body_height, body_depth = body_size
        body = Cuboid(
            height=body_height,
            top_length=body_length,
            top_width=body_depth,
        ).with_name("rectangular_body")
        return [body]


class PressDispenserNozzle(ConceptTemplate):
    def __init__(
        self,
        base_sections,
        nozzle_cross_section,
        nozzle_lengths,
        nozzle_count,
        nozzle_offset,
        nozzle_rotations_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPENSER_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                base_sections=base_sections,
                nozzle_cross_section=nozzle_cross_section,
                nozzle_lengths=nozzle_lengths,
                nozzle_count=nozzle_count,
                nozzle_offset=nozzle_offset,
                nozzle_rotations_degrees=nozzle_rotations_degrees,
            )
        )
        self.semantic = "Nozzle"

    @classmethod
    def _build_components(
        cls,
        base_sections,
        nozzle_cross_section,
        nozzle_lengths,
        nozzle_count,
        nozzle_offset,
        nozzle_rotations_degrees,
    ):
        components = []
        current_top_anchor = np.array([0.0, 0.0, 0.0])
        current_radius = 0.0

        for section in base_sections:
            current_radius = section["radius"]
            base = Cylinder(
                height=section["height"],
                top_radius=current_radius,
            ).with_name(section["name"])
            base.move_anchor_to("bottom_center", current_top_anchor)
            current_top_anchor = base.world_anchor("top_center")
            components.append(base)

        nozzle_width, nozzle_height = nozzle_cross_section
        _, base_top_y, _ = current_top_anchor
        first_mount = (0.0, base_top_y + nozzle_offset, current_radius)
        first_segment = cls._nozzle_segment(
            name="outlet_segment_1",
            nozzle_width=nozzle_width,
            nozzle_height=nozzle_height,
            nozzle_length=nozzle_lengths[0],
            nozzle_rotation_degrees=nozzle_rotations_degrees[0],
        )
        first_segment.move_anchor_to("back_center", first_mount)
        components.append(first_segment)

        if int(nozzle_count) == 2:
            second_segment = cls._nozzle_segment(
                name="outlet_segment_2",
                nozzle_width=nozzle_width,
                nozzle_height=nozzle_height,
                nozzle_length=nozzle_lengths[1],
                nozzle_rotation_degrees=nozzle_rotations_degrees[1],
            )
            second_segment.move_anchor_to(
                "back_center",
                first_segment.world_anchor("front_center"),
            )
            components.append(second_segment)

        return components

    @staticmethod
    def _nozzle_segment(
        name,
        nozzle_width,
        nozzle_height,
        nozzle_length,
        nozzle_rotation_degrees,
    ):
        return Cuboid(
            height=nozzle_height,
            top_length=nozzle_width,
            top_width=nozzle_length,
            rotation=(nozzle_rotation_degrees * DEGREES_TO_RADIANS, 0.0, 0.0),
        ).with_name(name)


class SprayDispenserNozzle(ConceptTemplate):
    def __init__(
        self,
        bottom_size,
        middle_size,
        head_size,
        head_forward_offset,
        head_rotation_degrees,
        outlet_size,
        handle_size,
        handle_offset,
        handle_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=DISPENSER_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                bottom_size=bottom_size,
                middle_size=middle_size,
                head_size=head_size,
                head_forward_offset=head_forward_offset,
                head_rotation_degrees=head_rotation_degrees,
                outlet_size=outlet_size,
                handle_size=handle_size,
                handle_offset=handle_offset,
                handle_rotation_degrees=handle_rotation_degrees,
            )
        )
        self.semantic = "Nozzle"

    @classmethod
    def _build_components(
        cls,
        bottom_size,
        middle_size,
        head_size,
        head_forward_offset,
        head_rotation_degrees,
        outlet_size,
        handle_size,
        handle_offset,
        handle_rotation_degrees,
    ):
        bottom_radius, bottom_height = bottom_size
        middle_length, middle_height, middle_depth = middle_size
        head_length, head_height, head_depth = head_size
        outlet_radius, outlet_length = outlet_size
        handle_length, handle_height, handle_depth = handle_size
        head_angle = head_rotation_degrees * DEGREES_TO_RADIANS
        handle_angle = handle_rotation_degrees * DEGREES_TO_RADIANS

        bottom = Cylinder(
            height=bottom_height,
            top_radius=bottom_radius,
        ).with_name("bottom_cylinder")
        bottom.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        middle = Cuboid(
            height=middle_height,
            top_length=middle_length,
            top_width=middle_depth,
        ).with_name("middle_body")
        middle.move_anchor_to("bottom_center", bottom.world_anchor("top_center"))

        _, middle_top_y, _ = middle.world_anchor("top_center")
        head_base_y = middle_top_y + head_height / 2.0
        head_y_compensation = -head_forward_offset * tan(head_angle)
        head = Cuboid(
            height=head_height,
            top_length=head_length,
            top_width=head_depth,
            position=(
                0.0,
                head_base_y
                + head_y_compensation
                + head_forward_offset * sin(head_angle),
                head_forward_offset * cos(head_angle),
            ),
            rotation=(head_angle, 0.0, 0.0),
        ).with_name("sloped_head")

        outlet = Cylinder(
            height=outlet_length,
            top_radius=outlet_radius,
            rotation=(head_angle + pi / 2.0, 0.0, 0.0),
        ).with_name("front_outlet")
        outlet.move_anchor_to(
            "bottom_center",
            cls._head_local_point_to_world(
                local_point=(
                    0.0,
                    0.0,
                    head_forward_offset + head_depth / 2.0,
                ),
                head_base_y=head_base_y,
                head_y_compensation=head_y_compensation,
                head_angle=head_angle,
            ),
        )

        handle = Cuboid(
            height=handle_height,
            top_length=handle_length,
            top_width=handle_depth,
            rotation=(head_angle + handle_angle, 0.0, 0.0),
        ).with_name("trigger_handle")
        handle.move_anchor_to(
            "top_center",
            cls._head_local_point_to_world(
                local_point=(
                    0.0,
                    -head_height / 2.0,
                    head_forward_offset
                    + head_depth / 2.0
                    + handle_offset
                    - handle_depth / 2.0,
                ),
                head_base_y=head_base_y,
                head_y_compensation=head_y_compensation,
                head_angle=head_angle,
            ),
        )

        return [bottom, middle, head, outlet, handle]

    @staticmethod
    def _head_local_point_to_world(
        local_point,
        head_base_y,
        head_y_compensation,
        head_angle,
    ):
        offset = transform_direction(local_point, (head_angle, 0.0, 0.0))
        offset_x, offset_y, offset_z = offset
        return (
            float(offset_x),
            float(head_base_y + head_y_compensation + offset_y),
            float(offset_z),
        )
