from math import pi

from code.geometry import ConceptTemplate, Cuboid, Cylinder, Ring, Sphere


GLUESTICK_ROTATION_ORDER = "YXZ"
DEGREES_TO_RADIANS = pi / 180.0


class CylindricalGlueStickBody(ConceptTemplate):
    def __init__(
        self,
        profile_size,
        z_radius_scale,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=GLUESTICK_ROTATION_ORDER,
            offset_first=True,
        )
        top_radius, bottom_radius, height = profile_size
        self._finalize_mesh(
            [
                Cylinder(
                    height=height,
                    top_radius=top_radius,
                    bottom_radius=bottom_radius,
                    top_radius_z=z_radius_scale * top_radius,
                    bottom_radius_z=z_radius_scale * bottom_radius,
                ).with_name("elliptical_cylindrical_body")
            ]
        )
        self.semantic = "Body"


class ToothpasteLikeGlueStickBody(ConceptTemplate):
    def __init__(
        self,
        top_radius,
        bottom_flat_length,
        height,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=GLUESTICK_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            [
                Cylinder(
                    height=height,
                    top_radius=top_radius,
                    bottom_radius=0.0,
                    bottom_radius_z=bottom_flat_length / 2.0,
                ).with_name("flattened_tapered_body")
            ]
        )
        self.semantic = "Body"


class CuboidalGlueStickBody(ConceptTemplate):
    def __init__(self, body_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=GLUESTICK_ROTATION_ORDER,
            offset_first=True,
        )
        length, width, height = body_size
        self._finalize_mesh(
            [
                Cuboid(
                    height=height,
                    top_length=length,
                    top_width=width,
                ).with_name("cuboidal_body")
            ]
        )
        self.semantic = "Body"


class DomedGlueStickCover(ConceptTemplate):
    def __init__(
        self,
        base_size,
        dome_radius,
        dome_exist_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=GLUESTICK_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                base_size=base_size,
                dome_radius=dome_radius,
                dome_exist_angle_degrees=dome_exist_angle_degrees,
            )
        )
        self.semantic = "Cover"

    @staticmethod
    def _build_components(base_size, dome_radius, dome_exist_angle_degrees):
        base_top_radius, base_bottom_radius, base_height = base_size
        dome_radius_x, dome_radius_y = dome_radius
        dome_angle = dome_exist_angle_degrees * DEGREES_TO_RADIANS

        base = Cylinder(
            height=base_height,
            top_radius=base_top_radius,
            bottom_radius=base_bottom_radius,
        ).with_name("cylindrical_cover_base")
        base.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        dome = Sphere(
            radius=dome_radius_x,
            radius_y=dome_radius_y,
            top_angle=0.0,
            bottom_angle=dome_angle,
        ).with_name("dome_cap")
        dome.move_anchor_to("bottom_pole", base.world_anchor("top_center"))

        return [base, dome]


class CylindricalGlueStickCover(ConceptTemplate):
    def __init__(
        self,
        outer_profile,
        inner_opening,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=GLUESTICK_ROTATION_ORDER,
            offset_first=True,
        )
        self._finalize_mesh(
            self._build_components(
                outer_profile=outer_profile,
                inner_opening=inner_opening,
            )
        )
        self.semantic = "Cover"

    @classmethod
    def _build_components(cls, outer_profile, inner_opening):
        outer_top_radius, outer_bottom_radius, total_height = outer_profile
        inner_top_radius, inner_bottom_radius, open_height = inner_opening
        closed_height = total_height - open_height
        split_outer_radius = cls._outer_radius_at_open_top(
            outer_top_radius=outer_top_radius,
            outer_bottom_radius=outer_bottom_radius,
            total_height=total_height,
            open_height=open_height,
        )

        open_ring = Ring(
            height=open_height,
            outer_top_radius=split_outer_radius,
            inner_top_radius=inner_top_radius,
            outer_bottom_radius=outer_bottom_radius,
            inner_bottom_radius=inner_bottom_radius,
        ).with_name("lower_open_ring")
        open_ring.move_anchor_to("axis_bottom_center", (0.0, 0.0, 0.0))

        closed_cap = Cylinder(
            height=closed_height,
            top_radius=outer_top_radius,
            bottom_radius=split_outer_radius,
        ).with_name("upper_closed_cap")
        closed_cap.move_anchor_to(
            "bottom_center",
            open_ring.world_anchor("axis_top_center"),
        )

        return [open_ring, closed_cap]

    @staticmethod
    def _outer_radius_at_open_top(
        outer_top_radius,
        outer_bottom_radius,
        total_height,
        open_height,
    ):
        closed_fraction = (total_height - open_height) / total_height
        return outer_top_radius + closed_fraction * (outer_bottom_radius - outer_top_radius)
