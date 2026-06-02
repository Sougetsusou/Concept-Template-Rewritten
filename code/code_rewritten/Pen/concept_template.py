from math import cos, pi, sin

from code.geometry_rewritten import ConceptTemplate, Cone, Cuboid, Cylinder, Ring


DEGREES_TO_RADIANS = pi / 180.0


class CylindricalPenBarrel(ConceptTemplate):
    def __init__(
        self,
        top_outer_radius,
        bottom_outer_radius,
        height,
        wall_thickness,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            [
                Ring(
                    height=height,
                    outer_top_radius=top_outer_radius,
                    inner_top_radius=top_outer_radius - wall_thickness,
                    outer_bottom_radius=bottom_outer_radius,
                    inner_bottom_radius=bottom_outer_radius - wall_thickness,
                ).with_name("barrel_shell")
            ]
        )
        self.semantic = "Body"


class DoubleLayerPenBarrel(ConceptTemplate):
    def __init__(
        self,
        main_top_outer_radius,
        main_bottom_outer_radius,
        main_height,
        bottom_bottom_outer_radius,
        bottom_height,
        wall_thickness,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                main_top_outer_radius=main_top_outer_radius,
                main_bottom_outer_radius=main_bottom_outer_radius,
                main_height=main_height,
                bottom_bottom_outer_radius=bottom_bottom_outer_radius,
                bottom_height=bottom_height,
                wall_thickness=wall_thickness,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(
        main_top_outer_radius,
        main_bottom_outer_radius,
        main_height,
        bottom_bottom_outer_radius,
        bottom_height,
        wall_thickness,
    ):
        main_shell = Ring(
            height=main_height,
            outer_top_radius=main_top_outer_radius,
            inner_top_radius=main_top_outer_radius - wall_thickness,
            outer_bottom_radius=main_bottom_outer_radius,
            inner_bottom_radius=main_bottom_outer_radius - wall_thickness,
        ).with_name("main_barrel_shell")

        bottom_shell = Ring(
            height=bottom_height,
            outer_top_radius=main_bottom_outer_radius,
            inner_top_radius=main_bottom_outer_radius - wall_thickness,
            outer_bottom_radius=bottom_bottom_outer_radius,
            inner_bottom_radius=bottom_bottom_outer_radius - wall_thickness,
        ).with_name("bottom_barrel_shell")
        bottom_shell.move_anchor_to(
            "axis_top_center",
            main_shell.world_anchor("axis_bottom_center"),
        )

        return [main_shell, bottom_shell]


class SinglePenCap(ConceptTemplate):
    def __init__(
        self,
        top_outer_radius,
        bottom_outer_radius,
        total_height,
        top_inner_radius,
        bottom_inner_radius,
        hollow_height,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                top_outer_radius=top_outer_radius,
                bottom_outer_radius=bottom_outer_radius,
                total_height=total_height,
                top_inner_radius=top_inner_radius,
                bottom_inner_radius=bottom_inner_radius,
                hollow_height=hollow_height,
            )
        )
        self.semantic = "Cap"

    @staticmethod
    def _joint_outer_radius(top_outer_radius, bottom_outer_radius, total_height, hollow_height):
        hollow_fraction = hollow_height / total_height
        return top_outer_radius * (1.0 - hollow_fraction) + bottom_outer_radius * hollow_fraction

    @classmethod
    def _build_components(
        cls,
        top_outer_radius,
        bottom_outer_radius,
        total_height,
        top_inner_radius,
        bottom_inner_radius,
        hollow_height,
    ):
        closed_height = total_height - hollow_height
        joint_outer_radius = cls._joint_outer_radius(
            top_outer_radius=top_outer_radius,
            bottom_outer_radius=bottom_outer_radius,
            total_height=total_height,
            hollow_height=hollow_height,
        )

        closed_base = Cylinder(
            height=closed_height,
            top_radius=joint_outer_radius,
            bottom_radius=bottom_outer_radius,
        ).with_name("closed_base")
        closed_base.move_anchor_to("bottom_center", (0.0, -total_height / 2.0, 0.0))

        hollow_shell = Ring(
            height=hollow_height,
            outer_top_radius=top_outer_radius,
            inner_top_radius=top_inner_radius,
            outer_bottom_radius=joint_outer_radius,
            inner_bottom_radius=bottom_inner_radius,
        ).with_name("upper_hollow_shell")
        hollow_shell.move_anchor_to(
            "axis_bottom_center",
            closed_base.world_anchor("top_center"),
        )

        return [closed_base, hollow_shell]


class TrifoldPenClip(ConceptTemplate):
    def __init__(
        self,
        root_size,
        middle_size,
        tip_size,
        root_to_middle_drop,
        tip_return_drop,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                root_size=root_size,
                middle_size=middle_size,
                tip_size=tip_size,
                root_to_middle_drop=root_to_middle_drop,
                tip_return_drop=tip_return_drop,
            )
        )
        self.semantic = "Clip"

    @staticmethod
    def _build_components(root_size, middle_size, tip_size, root_to_middle_drop, tip_return_drop):
        root_length, root_height, root_depth = root_size
        middle_length, middle_height, middle_depth = middle_size
        tip_length, tip_height, tip_depth = tip_size

        root = Cuboid(
            height=root_height,
            top_length=root_length,
            top_width=root_depth,
        ).with_name("root_segment")
        root.move_anchor_to("top_back_center", (0.0, 0.0, 0.0))

        middle = Cuboid(
            height=middle_height,
            top_length=middle_length,
            top_width=middle_depth,
        ).with_name("middle_segment")
        root_front_x, root_front_y, root_front_z = root.world_anchor("top_front_center")
        middle.move_anchor_to(
            "top_back_center",
            (
                root_front_x,
                root_front_y - root_to_middle_drop,
                root_front_z,
            ),
        )

        tip = Cuboid(
            height=tip_height,
            top_length=tip_length,
            top_width=tip_depth,
        ).with_name("return_tip")
        middle_bottom_x, middle_bottom_y, middle_bottom_z = middle.world_anchor(
            "bottom_back_center"
        )
        tip.move_anchor_to(
            "bottom_front_center",
            (
                middle_bottom_x,
                middle_bottom_y - tip_return_drop,
                middle_bottom_z,
            ),
        )

        return [root, middle, tip]


class CurvedPenClip(ConceptTemplate):
    def __init__(
        self,
        outer_radius,
        inner_radius,
        thickness,
        arc_angle_degrees,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                outer_radius=outer_radius,
                inner_radius=inner_radius,
                thickness=thickness,
                arc_angle_degrees=arc_angle_degrees,
            )
        )
        self.semantic = "Clip"

    @staticmethod
    def _build_components(outer_radius, inner_radius, thickness, arc_angle_degrees):
        arc_angle = arc_angle_degrees * DEGREES_TO_RADIANS
        clip_arc = Ring(
            height=thickness,
            outer_top_radius=outer_radius,
            inner_top_radius=inner_radius,
            exist_angle=arc_angle,
            rotation=(0.0, -pi / 2.0 + arc_angle / 2.0, pi / 2.0),
        ).with_name("curved_clip_arc")
        clip_arc.move_anchor_to(
            "arc_origin",
            (
                0.0,
                -outer_radius * sin(arc_angle / 2.0),
                -outer_radius * cos(arc_angle / 2.0),
            ),
        )
        return [clip_arc]


class CylindricalPenButton(ConceptTemplate):
    def __init__(
        self,
        top_radius,
        bottom_radius,
        height,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        button = Cylinder(
            height=height,
            top_radius=top_radius,
            bottom_radius=bottom_radius,
        ).with_name("button_cylinder")
        button.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))
        self._finalize_mesh([button])
        self.semantic = "Button"


class BistratalPenButton(ConceptTemplate):
    def __init__(
        self,
        bottom_top_radius,
        bottom_bottom_radius,
        bottom_height,
        top_top_radius,
        top_bottom_radius,
        top_height,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                bottom_top_radius=bottom_top_radius,
                bottom_bottom_radius=bottom_bottom_radius,
                bottom_height=bottom_height,
                top_top_radius=top_top_radius,
                top_bottom_radius=top_bottom_radius,
                top_height=top_height,
            )
        )
        self.semantic = "Button"

    @staticmethod
    def _build_components(
        bottom_top_radius,
        bottom_bottom_radius,
        bottom_height,
        top_top_radius,
        top_bottom_radius,
        top_height,
    ):
        lower = Cylinder(
            height=bottom_height,
            top_radius=bottom_top_radius,
            bottom_radius=bottom_bottom_radius,
        ).with_name("lower_button_layer")
        lower.move_anchor_to("bottom_center", (0.0, 0.0, 0.0))

        upper = Cylinder(
            height=top_height,
            top_radius=top_top_radius,
            bottom_radius=top_bottom_radius,
        ).with_name("upper_button_layer")
        upper.move_anchor_to("bottom_center", lower.world_anchor("top_center"))

        return [lower, upper]


class CylindricalPenRefill(ConceptTemplate):
    def __init__(
        self,
        refill_radius,
        refill_height,
        tip_radius,
        connector_height,
        cone_height,
        tip_offset,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(position=position, rotation=rotation)
        self._finalize_mesh(
            self._build_components(
                refill_radius=refill_radius,
                refill_height=refill_height,
                tip_radius=tip_radius,
                connector_height=connector_height,
                cone_height=cone_height,
                tip_offset=tip_offset,
            )
        )
        self.semantic = "Refill"

    @staticmethod
    def _build_components(
        refill_radius,
        refill_height,
        tip_radius,
        connector_height,
        cone_height,
        tip_offset,
    ):
        refill_body = Cylinder(
            height=refill_height,
            top_radius=refill_radius,
        ).with_name("refill_body")

        connector = Cylinder(
            height=connector_height,
            top_radius=tip_radius,
        ).with_name("tip_connector")
        connector.move_anchor_to(
            "top_center",
            refill_body.world_anchor("bottom_center"),
        )

        cone_tip = Cone(
            radius=tip_radius,
            height=cone_height,
            tip_offset=tip_offset,
            rotation=(0.0, 0.0, pi),
        ).with_name("writing_cone_tip")
        cone_tip.move_anchor_to(
            "base_center",
            connector.world_anchor("bottom_center"),
        )

        return [refill_body, connector, cone_tip]
