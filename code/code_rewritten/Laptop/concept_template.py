from math import pi

from code.geometry_rewritten import ConceptTemplate, Cuboid, Cylinder


DEGREES_TO_RADIANS = pi / 180.0


class RegularLaptopBase(ConceptTemplate):
    def __init__(self, base_size, position=(0, 0, 0), rotation=(0, 0, 0)):
        super().__init__(position=position, rotation=rotation)
        base_length, base_height, base_depth = base_size
        self._finalize_mesh(
            [
                Cuboid(
                    height=base_height,
                    top_length=base_length,
                    top_width=base_depth,
                ).with_name("single_laptop_base")
            ]
        )
        self.semantic = "Base"


class TiltedLaptopScreen(ConceptTemplate):
    def __init__(
        self,
        screen_size,
        hinge_projection_offset,
        screen_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                screen_size=screen_size,
                hinge_projection_offset=hinge_projection_offset,
                screen_rotation_degrees=screen_rotation_degrees,
            )
        )
        self.semantic = "Screen"

    @staticmethod
    def _build_components(
        screen_size,
        hinge_projection_offset,
        screen_rotation_degrees,
    ):
        screen_length, screen_height, screen_depth = screen_size
        hinge_projection_y, screen_center_z = hinge_projection_offset
        screen_rotation = screen_rotation_degrees * DEGREES_TO_RADIANS

        screen = Cuboid(
            height=screen_height,
            top_length=screen_length,
            top_width=screen_depth,
            position=(0.0, 0.0, screen_center_z),
            rotation=(screen_rotation, 0.0, 0.0),
        ).with_name("tilted_screen_panel")
        screen.move_local_point_axes_to(
            (0.0, -screen_height / 2.0, 0.0),
            (0.0, hinge_projection_y, screen_center_z),
            ("y",),
        )
        return [screen]


class CuboidalLaptopConnector(ConceptTemplate):
    def __init__(
        self,
        connector_count,
        connector_size,
        connector_gaps,
        start_offset,
        connector_rotation_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                connector_count=connector_count,
                connector_size=connector_size,
                connector_gaps=connector_gaps,
                start_offset=start_offset,
                connector_rotation_degrees=connector_rotation_degrees,
            )
        )
        self.semantic = "Connector"

    @staticmethod
    def _build_components(
        connector_count,
        connector_size,
        connector_gaps,
        start_offset,
        connector_rotation_degrees,
    ):
        count = int(round(connector_count))
        connector_length, connector_height, connector_depth = connector_size
        start_x, center_y, center_z = start_offset
        connector_rotation = connector_rotation_degrees * DEGREES_TO_RADIANS

        components = []
        cursor_x = start_x
        gap_iter = iter(connector_gaps)
        for connector_index in range(count):
            connector = Cuboid(
                height=connector_height,
                top_length=connector_length,
                top_width=connector_depth,
                rotation=(connector_rotation, 0.0, 0.0),
            ).with_name(f"cuboidal_connector_{connector_index + 1}")
            connector.move_anchor_to("left_center", (cursor_x, center_y, center_z))
            components.append(connector)

            if connector_index < count - 1:
                cursor_x += connector_length + next(gap_iter)

        return components


class CylindricalLaptopConnector(ConceptTemplate):
    def __init__(
        self,
        connector_count,
        connector_radius,
        connector_length,
        connector_gaps,
        start_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                connector_count=connector_count,
                connector_radius=connector_radius,
                connector_length=connector_length,
                connector_gaps=connector_gaps,
                start_offset=start_offset,
            )
        )
        self.semantic = "Connector"

    @staticmethod
    def _build_components(
        connector_count,
        connector_radius,
        connector_length,
        connector_gaps,
        start_offset,
    ):
        count = int(round(connector_count))
        start_x, center_y, center_z = start_offset

        components = []
        cursor_x = start_x
        gap_iter = iter(connector_gaps)
        for connector_index in range(count):
            connector = Cylinder(
                height=connector_length,
                top_radius=connector_radius,
            ).with_name(f"cylindrical_connector_{connector_index + 1}")
            connector.align_axis_between_points(
                "y",
                (cursor_x + connector_length, center_y, center_z),
                (cursor_x, center_y, center_z),
            )
            components.append(connector)

            if connector_index < count - 1:
                cursor_x += connector_length + next(gap_iter)

        return components
