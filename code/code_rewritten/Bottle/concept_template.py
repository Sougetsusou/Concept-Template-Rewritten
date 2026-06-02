from code.geometry_rewritten import ConceptTemplate, Cylinder, Ring


class StackedBottleBody(ConceptTemplate):
    def __init__(self, profile_sections, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(self._build_profile_components(profile_sections))

    @staticmethod
    def _build_profile_components(profile_sections):
        components = []
        previous_top_anchor = None

        for section in profile_sections:
            height = section["height"]
            section_primitive = Cylinder(
                height=height,
                top_radius=section["top_radius"],
                bottom_radius=section["bottom_radius"],
            ).with_name(section["name"])

            if previous_top_anchor is not None:
                section_primitive.move_anchor_to("bottom_center", previous_top_anchor)

            previous_top_anchor = section_primitive.world_anchor("top_center")
            components.append(section_primitive)

        return components


class CylindricalBottleLid(ConceptTemplate):
    def __init__(
        self,
        top_outer_radius,
        bottom_outer_radius,
        total_height,
        top_inner_radius,
        bottom_inner_radius,
        open_ring_height,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_lid_components(
                top_outer_radius=top_outer_radius,
                bottom_outer_radius=bottom_outer_radius,
                total_height=total_height,
                top_inner_radius=top_inner_radius,
                bottom_inner_radius=bottom_inner_radius,
                open_ring_height=open_ring_height,
            )
        )

    @staticmethod
    def _outer_radius_at_ring_top(
        top_outer_radius,
        bottom_outer_radius,
        total_height,
        open_ring_height,
    ):
        ring_fraction = open_ring_height / total_height
        return bottom_outer_radius * (1.0 - ring_fraction) + top_outer_radius * ring_fraction

    @classmethod
    def _build_lid_components(
        cls,
        top_outer_radius,
        bottom_outer_radius,
        total_height,
        top_inner_radius,
        bottom_inner_radius,
        open_ring_height,
    ):
        top_cap_height = total_height - open_ring_height
        ring_top_outer_radius = cls._outer_radius_at_ring_top(
            top_outer_radius=top_outer_radius,
            bottom_outer_radius=bottom_outer_radius,
            total_height=total_height,
            open_ring_height=open_ring_height,
        )

        lower_ring = Ring(
            height=open_ring_height,
            outer_top_radius=ring_top_outer_radius,
            inner_top_radius=top_inner_radius,
            outer_bottom_radius=bottom_outer_radius,
            inner_bottom_radius=bottom_inner_radius,
        ).with_name("lower_open_ring")
        lower_ring.move_anchor_to("axis_bottom_center", (0, -total_height / 2.0, 0))

        upper_cap = Cylinder(
            height=top_cap_height,
            top_radius=top_outer_radius,
            bottom_radius=ring_top_outer_radius,
        ).with_name("upper_closed_cap")
        upper_cap.move_anchor_to("bottom_center", lower_ring.world_anchor("axis_top_center"))

        return [lower_ring, upper_cap]
