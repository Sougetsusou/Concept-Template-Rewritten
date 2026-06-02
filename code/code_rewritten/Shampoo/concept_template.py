from math import cos, pi, sin

from code.geometry_rewritten import ConceptTemplate, Cuboid, Cylinder, Ring


SHAMPOO_ROTATION_ORDER = "YXZ"
DEGREES_TO_RADIANS = pi / 180.0


class StackedCylindricalShampooBody(ConceptTemplate):
    def __init__(
        self,
        profile_sections,
        z_radius_scale,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SHAMPOO_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                profile_sections=profile_sections,
                z_radius_scale=z_radius_scale,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(profile_sections, z_radius_scale):
        components = []
        previous_top_anchor = None

        for section_index, section in enumerate(profile_sections):
            height = section["height"]
            top_radius = section["top_radius"]
            bottom_radius = section["bottom_radius"]
            component = Cylinder(
                height=height,
                top_radius=top_radius,
                bottom_radius=bottom_radius,
                top_radius_z=top_radius * z_radius_scale,
                bottom_radius_z=bottom_radius * z_radius_scale,
            ).with_name(section.get("name", f"body_section_{section_index + 1}"))
            if previous_top_anchor is not None:
                component.move_anchor_to("bottom_center", previous_top_anchor)
            previous_top_anchor = component.world_anchor("top_center")
            components.append(component)

        return components


class CuboidalShampooBody(ConceptTemplate):
    def __init__(self, body_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SHAMPOO_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(self._build_components(body_size=body_size))
        self.semantic = "Body"

    @staticmethod
    def _build_components(body_size):
        body_length, body_height, body_width = body_size
        return [
            Cuboid(
                height=body_height,
                top_length=body_length,
                top_width=body_width,
            ).with_name("cuboidal_body")
        ]


class ToothpasteLikeShampooBody(ConceptTemplate):
    def __init__(
        self,
        top_radius,
        bottom_flat_length,
        height,
        bottom_thin_radius=1e-2,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SHAMPOO_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                top_radius=top_radius,
                bottom_flat_length=bottom_flat_length,
                height=height,
                bottom_thin_radius=bottom_thin_radius,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(
        top_radius,
        bottom_flat_length,
        height,
        bottom_thin_radius,
    ):
        return [
            Cylinder(
                height=height,
                top_radius=top_radius,
                bottom_radius=bottom_thin_radius,
                bottom_radius_z=bottom_flat_length / 2.0,
            ).with_name("flattened_tapered_body")
        ]


class RegularShampooNozzle(ConceptTemplate):
    def __init__(
        self,
        base_sections,
        nozzle_width,
        nozzle_height,
        nozzle_segments,
        nozzle_vertical_offset,
        yaw_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SHAMPOO_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                base_sections=base_sections,
                nozzle_width=nozzle_width,
                nozzle_height=nozzle_height,
                nozzle_segments=nozzle_segments,
                nozzle_vertical_offset=nozzle_vertical_offset,
                yaw_degrees=yaw_degrees,
            )
        )
        self.semantic = "Nozzle"

    @classmethod
    def _build_components(
        cls,
        base_sections,
        nozzle_width,
        nozzle_height,
        nozzle_segments,
        nozzle_vertical_offset,
        yaw_degrees,
    ):
        components, base_top_y, outer_radius = cls._build_base_stack(base_sections)
        components.extend(
            cls._build_nozzle_segments(
                base_top_y=base_top_y,
                outer_radius=outer_radius,
                nozzle_width=nozzle_width,
                nozzle_height=nozzle_height,
                nozzle_segments=nozzle_segments,
                nozzle_vertical_offset=nozzle_vertical_offset,
                yaw_degrees=yaw_degrees,
            )
        )
        return components

    @staticmethod
    def _build_base_stack(base_sections):
        components = []
        top_anchor = (0.0, 0.0, 0.0)
        base_top_y = 0.0
        outer_radius = 0.0

        for section_index, section in enumerate(base_sections):
            radius = section["radius"]
            height = section["height"]
            component = Cylinder(height=height, top_radius=radius).with_name(
                section.get("name", f"base_section_{section_index + 1}")
            )
            component.move_anchor_to("bottom_center", top_anchor)
            top_anchor = component.world_anchor("top_center")
            _, base_top_y, _ = top_anchor
            outer_radius = radius
            components.append(component)

        return components, base_top_y, outer_radius

    @staticmethod
    def _build_nozzle_segments(
        base_top_y,
        outer_radius,
        nozzle_width,
        nozzle_height,
        nozzle_segments,
        nozzle_vertical_offset,
        yaw_degrees,
    ):
        components = []
        attachment_y = base_top_y + nozzle_vertical_offset
        attachment_z = outer_radius
        yaw = yaw_degrees * DEGREES_TO_RADIANS

        for segment_index, segment in enumerate(nozzle_segments):
            segment_length = segment["length"]
            pitch = segment["pitch_degrees"] * DEGREES_TO_RADIANS
            start_point = (0.0, attachment_y, attachment_z)
            end_point = (
                0.0,
                attachment_y - segment_length * sin(pitch),
                attachment_z + segment_length * cos(pitch),
            )
            component = Cuboid(
                height=nozzle_height,
                top_length=nozzle_width,
                top_width=segment_length,
            ).with_name(segment.get("name", f"nozzle_segment_{segment_index + 1}"))
            component.align_axis_between_points("z", start_point, end_point)
            component.rotate_about_point((0.0, 0.0, 0.0), (0.0, yaw, 0.0))
            components.append(component)
            _, attachment_y, attachment_z = end_point

        return components


class CylindricalShampooCap(ConceptTemplate):
    def __init__(
        self,
        outer_profile,
        inner_profile,
        z_radius_scale,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SHAMPOO_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                outer_profile=outer_profile,
                inner_profile=inner_profile,
                z_radius_scale=z_radius_scale,
            )
        )
        self.semantic = "Cap"

    @staticmethod
    def _build_components(outer_profile, inner_profile, z_radius_scale):
        outer_top_radius, outer_bottom_radius, total_height = outer_profile
        inner_top_radius, inner_bottom_radius, hollow_depth = inner_profile

        shell = Ring(
            height=total_height,
            outer_top_radius=outer_top_radius,
            inner_top_radius=inner_top_radius,
            outer_bottom_radius=outer_bottom_radius,
            inner_bottom_radius=inner_bottom_radius,
            x_z_ratio=z_radius_scale,
            rotation=(0.0, pi / 2.0, 0.0),
        ).with_name("open_ring_shell")

        top_fill = Cylinder(
            height=total_height - hollow_depth,
            top_radius=outer_top_radius,
            bottom_radius=outer_top_radius,
            top_radius_z=outer_top_radius * z_radius_scale,
            bottom_radius_z=outer_top_radius * z_radius_scale,
        ).with_name("upper_closed_fill")
        top_fill.move_anchor_to("top_center", shell.world_anchor("axis_top_center"))

        return [shell, top_fill]


class RegularShampooCap(ConceptTemplate):
    def __init__(self, cap_radius, cap_height, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=SHAMPOO_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            [
                Cylinder(height=cap_height, top_radius=cap_radius).with_name(
                    "cylindrical_cap"
                )
            ]
        )
        self.semantic = "Cap"
