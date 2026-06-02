from math import pi

from code.geometry import ConceptTemplate, Cuboid


STORAGE_FURNITURE_ROTATION_ORDER = "XYZ"
DEGREES_TO_RADIANS = pi / 180.0


class PartitionedStorageFurnitureBody(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        back_panel_thickness,
        side_wall_thickness,
        base_panel_thickness,
        lid_spec=None,
        horizontal_shelf_specs=(),
        partition_bay_specs=(),
        additional_panel_specs=(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=STORAGE_FURNITURE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                back_panel_thickness=back_panel_thickness,
                side_wall_thickness=side_wall_thickness,
                base_panel_thickness=base_panel_thickness,
                lid_spec=lid_spec,
                horizontal_shelf_specs=horizontal_shelf_specs,
                partition_bay_specs=partition_bay_specs,
                additional_panel_specs=additional_panel_specs,
            )
        )
        self.semantic = "Body"

    @staticmethod
    def _build_components(
        outer_size,
        back_panel_thickness,
        side_wall_thickness,
        base_panel_thickness,
        lid_spec,
        horizontal_shelf_specs,
        partition_bay_specs,
        additional_panel_specs,
    ):
        outer_length, outer_height, outer_depth = outer_size
        inner_length = outer_length - 2.0 * side_wall_thickness

        components = []
        for name, side_anchor, target_x in (
            ("left_side_wall", "left_center", -outer_length / 2.0),
            ("right_side_wall", "right_center", outer_length / 2.0),
        ):
            side_wall = Cuboid(
                height=outer_height,
                top_length=side_wall_thickness,
                top_width=outer_depth,
            ).with_name(name)
            side_wall.move_anchor_to(side_anchor, (target_x, 0.0, 0.0))
            components.append(side_wall)

        base_panel = Cuboid(
            height=base_panel_thickness,
            top_length=inner_length,
            top_width=outer_depth,
        ).with_name("base_panel")
        base_panel.move_anchor_to(
            "bottom_center",
            (0.0, -outer_height / 2.0, 0.0),
        )
        components.append(base_panel)

        back_panel = Cuboid(
            height=outer_height,
            top_length=outer_length,
            top_width=back_panel_thickness,
        ).with_name("back_panel")
        back_panel.move_anchor_to(
            "back_center",
            (0.0, 0.0, -outer_depth / 2.0),
        )
        components.append(back_panel)

        if lid_spec is not None:
            lid_length, lid_height, lid_depth = lid_spec["size"]
            lid_offset_x, lid_offset_y, lid_offset_z = lid_spec["offset"]
            lid = Cuboid(
                height=lid_height,
                top_length=lid_length,
                top_width=lid_depth,
            ).with_name("top_lid")
            lid.move_anchor_to(
                "bottom_center",
                (
                    lid_offset_x,
                    outer_height / 2.0 + lid_offset_y,
                    back_panel_thickness / 2.0 + lid_offset_z,
                ),
            )
            components.append(lid)

        for shelf_index, shelf_spec in enumerate(horizontal_shelf_specs):
            shelf = Cuboid(
                height=shelf_spec["thickness"],
                top_length=inner_length,
                top_width=outer_depth,
            ).with_name(f"horizontal_shelf_{shelf_index + 1}")
            shelf.move_anchor_to(
                "center",
                (
                    0.0,
                    outer_height / 2.0 - shelf_spec["center_offset_from_top"],
                    0.0,
                ),
            )
            components.append(shelf)

        for bay_index, bay_spec in enumerate(partition_bay_specs):
            partition_count = int(bay_spec["partition_count"])
            partition_thickness_x, partition_depth = bay_spec["partition_size"]
            first_center_offset_x = bay_spec["first_center_offset_from_inner_left"]
            partition_interval_x = bay_spec["partition_interval_x"]
            for partition_index in range(partition_count):
                center_x = (
                    -outer_length / 2.0
                    + side_wall_thickness
                    + first_center_offset_x
                    + partition_index * partition_interval_x
                )
                partition = Cuboid(
                    height=bay_spec["height"],
                    top_length=partition_thickness_x,
                    top_width=partition_depth,
                ).with_name(f"bay_{bay_index + 1}_vertical_partition_{partition_index + 1}")
                partition.move_anchor_to(
                    "center",
                    (center_x, bay_spec["center_y"], 0.0),
                )
                components.append(partition)

        for panel_index, panel_spec in enumerate(additional_panel_specs):
            panel_length, panel_height, panel_depth = panel_spec["size"]
            rotation_x, rotation_y, rotation_z = panel_spec["rotation_degrees"]
            panel = Cuboid(
                height=panel_height,
                top_length=panel_length,
                top_width=panel_depth,
                position=panel_spec["center"],
                rotation=(
                    rotation_x * DEGREES_TO_RADIANS,
                    rotation_y * DEGREES_TO_RADIANS,
                    rotation_z * DEGREES_TO_RADIANS,
                ),
            ).with_name(f"additional_panel_{panel_index + 1}")
            components.append(panel)

        return components


class EnclosedStorageFurnitureLegFrame(ConceptTemplate):
    def __init__(
        self,
        outer_size,
        side_wall_thickness,
        front_back_wall_thickness,
        additional_leg_specs=(),
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=STORAGE_FURNITURE_ROTATION_ORDER,
        )
        self._finalize_mesh(
            self._build_components(
                outer_size=outer_size,
                side_wall_thickness=side_wall_thickness,
                front_back_wall_thickness=front_back_wall_thickness,
                additional_leg_specs=additional_leg_specs,
            )
        )
        self.semantic = "Leg"

    @staticmethod
    def _build_components(
        outer_size,
        side_wall_thickness,
        front_back_wall_thickness,
        additional_leg_specs,
    ):
        outer_length, outer_height, outer_depth = outer_size
        components = []

        if not (outer_length <= 0.01 and outer_depth <= 0.01):
            for name, side_anchor, target_x in (
                ("left_frame_wall", "left_center", -outer_length / 2.0),
                ("right_frame_wall", "right_center", outer_length / 2.0),
            ):
                side_wall = Cuboid(
                    height=outer_height,
                    top_length=side_wall_thickness,
                    top_width=outer_depth,
                ).with_name(name)
                side_wall.move_anchor_to(side_anchor, (target_x, 0.0, 0.0))
                components.append(side_wall)

            for name, face_anchor, target_z in (
                ("back_frame_wall", "back_center", -outer_depth / 2.0),
                ("front_frame_wall", "front_center", outer_depth / 2.0),
            ):
                face_wall = Cuboid(
                    height=outer_height,
                    top_length=outer_length,
                    top_width=front_back_wall_thickness,
                ).with_name(name)
                face_wall.move_anchor_to(face_anchor, (0.0, 0.0, target_z))
                components.append(face_wall)

        for leg_index, leg_spec in enumerate(additional_leg_specs):
            leg_length, leg_height, leg_depth = leg_spec["size"]
            rotation_x, rotation_y, rotation_z = leg_spec["rotation_degrees"]
            leg = Cuboid(
                height=leg_height,
                top_length=leg_length,
                top_width=leg_depth,
                position=leg_spec["center"],
                rotation=(
                    rotation_x * DEGREES_TO_RADIANS,
                    rotation_y * DEGREES_TO_RADIANS,
                    rotation_z * DEGREES_TO_RADIANS,
                ),
            ).with_name(f"additional_leg_{leg_index + 1}")
            components.append(leg)

        return components


class StorageFurnitureDoorSet(ConceptTemplate):
    def __init__(
        self,
        door_specs,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=STORAGE_FURNITURE_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(door_specs=door_specs))
        self.semantic = "Door"

    @staticmethod
    def _build_components(door_specs):
        components = []
        for door_index, door_spec in enumerate(door_specs):
            door_length, door_height, door_depth = door_spec["door_size"]
            handle_length, handle_height, handle_depth = door_spec["handle_size"]
            handle_offset_x, handle_offset_y = door_spec["handle_offset"]
            center_x, center_y, center_z = door_spec["center"]
            door_yaw = door_spec["yaw_degrees"] * DEGREES_TO_RADIANS

            door = Cuboid(
                height=door_height,
                top_length=door_length,
                top_width=door_depth,
                position=(center_x, center_y, center_z),
                rotation=(0.0, door_yaw, 0.0),
            ).with_name(f"door_{door_index + 1}_panel")
            components.append(door)

            handle = Cuboid(
                height=handle_height,
                top_length=handle_length,
                top_width=handle_depth,
                position=(center_x, center_y, center_z),
                rotation=(0.0, door_yaw, 0.0),
            ).with_name(f"door_{door_index + 1}_handle")
            handle.move_anchor_to(
                "back_center",
                door.world_point((handle_offset_x, handle_offset_y, door_depth / 2.0)),
            )
            components.append(handle)

        return components


class StorageFurnitureDrawerSet(ConceptTemplate):
    def __init__(
        self,
        drawer_specs,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=STORAGE_FURNITURE_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(drawer_specs=drawer_specs))
        self.semantic = "Drawer"

    @staticmethod
    def _build_components(drawer_specs):
        components = []
        for drawer_index, drawer_spec in enumerate(drawer_specs):
            drawer_length, drawer_height, drawer_depth = drawer_spec["drawer_size"]
            bottom_thickness = drawer_spec["bottom_thickness"]
            front_length, front_height, front_depth = drawer_spec["front_panel_size"]
            front_offset_y = drawer_spec["front_panel_offset_y"]
            side_wall_thickness = drawer_spec["side_wall_thickness"]
            front_back_wall_thickness = drawer_spec["front_back_wall_thickness"]
            center_x, center_y, center_z = drawer_spec["center"]

            for name, side_anchor, target_x in (
                ("left_wall", "left_center", center_x - drawer_length / 2.0),
                ("right_wall", "right_center", center_x + drawer_length / 2.0),
            ):
                side_wall = Cuboid(
                    height=drawer_height,
                    top_length=side_wall_thickness,
                    top_width=drawer_depth,
                ).with_name(f"drawer_{drawer_index + 1}_{name}")
                side_wall.move_anchor_to(side_anchor, (target_x, center_y, center_z))
                components.append(side_wall)

            inner_wall_length = drawer_length - 2.0 * side_wall_thickness
            for name, face_anchor, target_z in (
                ("front_inner_wall", "front_center", center_z + drawer_depth / 2.0),
                ("back_inner_wall", "back_center", center_z - drawer_depth / 2.0),
            ):
                face_wall = Cuboid(
                    height=drawer_height,
                    top_length=inner_wall_length,
                    top_width=front_back_wall_thickness,
                ).with_name(f"drawer_{drawer_index + 1}_{name}")
                face_wall.move_anchor_to(face_anchor, (center_x, center_y, target_z))
                components.append(face_wall)

            bottom_panel = Cuboid(
                height=bottom_thickness,
                top_length=drawer_length,
                top_width=drawer_depth,
            ).with_name(f"drawer_{drawer_index + 1}_bottom_panel")
            bottom_panel.move_anchor_to(
                "top_center",
                (center_x, center_y - drawer_height / 2.0, center_z),
            )
            components.append(bottom_panel)

            front_panel = Cuboid(
                height=front_height,
                top_length=front_length,
                top_width=front_depth,
            ).with_name(f"drawer_{drawer_index + 1}_front_panel")
            front_panel.move_anchor_to(
                "back_center",
                (
                    center_x,
                    center_y + front_offset_y,
                    center_z + drawer_depth / 2.0,
                ),
            )
            components.append(front_panel)

            handle_count = int(drawer_spec["handle_count"])
            handle_length, handle_height, handle_depth = drawer_spec["handle_size"]
            handle_offset_x, handle_offset_y = drawer_spec["handle_offset"]
            handle_spacing = drawer_spec["handle_spacing"]
            for handle_index in range(handle_count):
                if handle_count == 2:
                    side_sign = 1.0 if handle_index == 0 else -1.0
                else:
                    side_sign = 0.0
                handle = Cuboid(
                    height=handle_height,
                    top_length=handle_length,
                    top_width=handle_depth,
                ).with_name(f"drawer_{drawer_index + 1}_handle_{handle_index + 1}")
                handle.move_anchor_to(
                    "back_center",
                    (
                        center_x + handle_offset_x + side_sign * handle_spacing / 2.0,
                        center_y + handle_offset_y,
                        center_z + drawer_depth / 2.0 + front_depth,
                    ),
                )
                components.append(handle)

        return components


class StorageFurnitureFrontPanelSet(ConceptTemplate):
    def __init__(
        self,
        panel_specs,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
    ):
        super().__init__(
            position=position,
            rotation=rotation,
            rotation_order=STORAGE_FURNITURE_ROTATION_ORDER,
        )
        self._finalize_mesh(self._build_components(panel_specs=panel_specs))
        self.semantic = "Panel"

    @staticmethod
    def _build_components(panel_specs):
        components = []
        for panel_index, panel_spec in enumerate(panel_specs):
            panel_length, panel_height, panel_depth = panel_spec["size"]
            panel = Cuboid(
                height=panel_height,
                top_length=panel_length,
                top_width=panel_depth,
                position=panel_spec["center"],
            ).with_name(f"front_panel_{panel_index + 1}")
            components.append(panel)
        return components
