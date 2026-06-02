"""Complete rewritten primitive set with persistent local geometry.

The primitive mesh kernels are implemented natively in this module.  The
public class signatures still match the legacy templates, but no rewritten
primitive imports or calls ``code.geometry_template``.
"""

import numpy as np

from .base import GeometryTemplate


CYLINDER_SEGMENTS = 256
SPHERE_LATITUDE_SEGMENTS = 64
SPHERE_LONGITUDE_SEGMENTS = 64
TORUS_CENTER_SEGMENTS = 64
TORUS_TUBE_SEGMENTS = 64


def _list(values):
    return list(values)


def _init_native(instance, local_vertices, faces, position, rotation, rotation_order):
    GeometryTemplate.__init__(
        instance,
        local_vertices=local_vertices,
        faces=faces,
        position=position,
        rotation=rotation,
        rotation_order=rotation_order,
    )


def _face_center(vertices, indices):
    return np.mean(vertices[np.asarray(indices, dtype=int)], axis=0)


def _register_box_anchors(instance, prefix="", indices=None):
    if indices is None:
        indices = list(range(8))
    indices = list(indices)
    v = instance.local_vertices
    names_to_indices = {
        "top_center": [indices[i] for i in [0, 1, 2, 3]],
        "bottom_center": [indices[i] for i in [4, 5, 6, 7]],
        "front_center": [indices[i] for i in [0, 1, 4, 5]],
        "back_center": [indices[i] for i in [2, 3, 6, 7]],
        "left_center": [indices[i] for i in [0, 2, 4, 6]],
        "right_center": [indices[i] for i in [1, 3, 5, 7]],
    }
    normals = {
        "top_center": [0, 1, 0],
        "bottom_center": [0, -1, 0],
        "front_center": [0, 0, 1],
        "back_center": [0, 0, -1],
        "left_center": [-1, 0, 0],
        "right_center": [1, 0, 0],
    }
    for name, anchor_indices in names_to_indices.items():
        instance._set_anchor(
            f"{prefix}{name}",
            _face_center(v, anchor_indices),
            normal=normals[name],
        )

    corner_indices = {
        "top_front_left": indices[0],
        "top_front_right": indices[1],
        "top_back_left": indices[2],
        "top_back_right": indices[3],
        "bottom_front_left": indices[4],
        "bottom_front_right": indices[5],
        "bottom_back_left": indices[6],
        "bottom_back_right": indices[7],
    }
    for name, vertex_index in corner_indices.items():
        instance._set_anchor(f"{prefix}{name}", v[vertex_index])

    edge_indices = {
        "top_front_center": [indices[i] for i in [0, 1]],
        "top_back_center": [indices[i] for i in [2, 3]],
        "top_left_center": [indices[i] for i in [0, 2]],
        "top_right_center": [indices[i] for i in [1, 3]],
        "bottom_front_center": [indices[i] for i in [4, 5]],
        "bottom_back_center": [indices[i] for i in [6, 7]],
        "bottom_left_center": [indices[i] for i in [4, 6]],
        "bottom_right_center": [indices[i] for i in [5, 7]],
        "front_left_center": [indices[i] for i in [0, 4]],
        "front_right_center": [indices[i] for i in [1, 5]],
        "back_left_center": [indices[i] for i in [2, 6]],
        "back_right_center": [indices[i] for i in [3, 7]],
    }
    for name, anchor_indices in edge_indices.items():
        instance._set_anchor(f"{prefix}{name}", _face_center(v, anchor_indices))


def _cuboid_mesh(
    height,
    top_length,
    top_width,
    bottom_length,
    bottom_width,
    top_offset,
    back_height,
):
    vertices = np.array(
        [
            [-1 / 2, 1 / 2, 1 / 2],
            [1 / 2, 1 / 2, 1 / 2],
            [-1 / 2, 1 / 2, -1 / 2],
            [1 / 2, 1 / 2, -1 / 2],
            [-1 / 2, -1 / 2, 1 / 2],
            [1 / 2, -1 / 2, 1 / 2],
            [-1 / 2, -1 / 2, -1 / 2],
            [1 / 2, -1 / 2, -1 / 2],
        ]
    )
    faces = np.array(
        [
            [0, 1, 2],
            [1, 3, 2],
            [4, 6, 5],
            [5, 6, 7],
            [0, 4, 5],
            [0, 5, 1],
            [2, 7, 6],
            [2, 3, 7],
            [0, 6, 4],
            [0, 2, 6],
            [1, 5, 7],
            [1, 7, 3],
        ]
    )
    vertices_resize = np.array(
        [
            [top_length, height, top_width],
            [top_length, height, top_width],
            [top_length, back_height, top_width],
            [top_length, back_height, top_width],
            [bottom_length, height, bottom_width],
            [bottom_length, height, bottom_width],
            [bottom_length, back_height, bottom_width],
            [bottom_length, back_height, bottom_width],
        ]
    )
    vertices = vertices * vertices_resize
    vertices_offset = np.array(
        [
            [top_offset[0], 0, top_offset[1]],
            [top_offset[0], 0, top_offset[1]],
            [top_offset[0], (back_height - height) / 2, top_offset[1]],
            [top_offset[0], (back_height - height) / 2, top_offset[1]],
            [0, 0, 0],
            [0, 0, 0],
            [0, (back_height - height) / 2, 0],
            [0, (back_height - height) / 2, 0],
        ]
    )
    return vertices + vertices_offset, faces


def _sphere_mesh(radius, top_angle, bottom_angle, radius_y, radius_z, longitude_angle):
    vertices = []
    for _ in range(SPHERE_LATITUDE_SEGMENTS + 1):
        for _ in range(SPHERE_LONGITUDE_SEGMENTS + 1):
            vertices.append([0, 0, 0])
    vertices.append([0, 0, 0])
    vertices.append([0, 0, 0])
    vertices = np.array(vertices)

    faces = []
    for i in range(SPHERE_LATITUDE_SEGMENTS):
        for j in range(SPHERE_LONGITUDE_SEGMENTS):
            faces.append(
                [
                    (SPHERE_LONGITUDE_SEGMENTS + 1) * i + j,
                    (SPHERE_LONGITUDE_SEGMENTS + 1) * i + j + 1,
                    (SPHERE_LONGITUDE_SEGMENTS + 1) * (i + 1) + j + 1,
                ]
            )
            faces.append(
                [
                    (SPHERE_LONGITUDE_SEGMENTS + 1) * i + j,
                    (SPHERE_LONGITUDE_SEGMENTS + 1) * (i + 1) + j + 1,
                    (SPHERE_LONGITUDE_SEGMENTS + 1) * (i + 1) + j,
                ]
            )
    for i in range(SPHERE_LONGITUDE_SEGMENTS):
        faces.append(
            [
                (SPHERE_LATITUDE_SEGMENTS + 1) * (SPHERE_LONGITUDE_SEGMENTS + 1),
                i + 1,
                i,
            ]
        )
        faces.append(
            [
                (SPHERE_LATITUDE_SEGMENTS + 1) * (SPHERE_LONGITUDE_SEGMENTS + 1)
                + 1,
                SPHERE_LATITUDE_SEGMENTS * (SPHERE_LONGITUDE_SEGMENTS + 1) + i,
                SPHERE_LATITUDE_SEGMENTS * (SPHERE_LONGITUDE_SEGMENTS + 1) + i + 1,
            ]
        )

    radius_offset = None
    for i in range(SPHERE_LATITUDE_SEGMENTS + 1):
        rotation_radius_tmp = (
            bottom_angle - top_angle
        ) / SPHERE_LATITUDE_SEGMENTS * i + top_angle
        radius_offset_tmp = np.array(
            [
                radius * np.sin(rotation_radius_tmp),
                radius_y * np.cos(rotation_radius_tmp),
                radius_z * np.sin(rotation_radius_tmp),
            ]
        )
        radius_offset_tmp = np.tile(
            radius_offset_tmp[None, :], (SPHERE_LONGITUDE_SEGMENTS + 1, 1)
        )
        if radius_offset is None:
            radius_offset = radius_offset_tmp
        else:
            radius_offset = np.concatenate((radius_offset, radius_offset_tmp), axis=0)

    central_angle = None
    for i in range(SPHERE_LONGITUDE_SEGMENTS + 1):
        rotation_longitude_tmp = longitude_angle / SPHERE_LONGITUDE_SEGMENTS * i
        central_angle_tmp = np.array(
            [np.cos(rotation_longitude_tmp), 1, np.sin(rotation_longitude_tmp)]
        )
        if central_angle is None:
            central_angle = central_angle_tmp
        elif i == 1:
            central_angle = np.array([central_angle, central_angle_tmp])
        else:
            central_angle = np.concatenate((central_angle, central_angle_tmp[None, :]), axis=0)
    central_angle = np.tile(
        central_angle,
        (int((vertices.shape[0]) / (SPHERE_LONGITUDE_SEGMENTS + 1)), 1),
    )
    radius_offset *= central_angle

    top_center = np.array([0, radius_y * np.cos(top_angle), 0])
    bottom_center = np.array([0, radius_y * np.cos(bottom_angle), 0])
    radius_offset = np.concatenate((radius_offset, np.array([top_center, bottom_center])), axis=0)

    return vertices + radius_offset, np.array(faces)


def _cylinder_mesh(
    height,
    top_radius,
    bottom_radius,
    top_radius_z,
    bottom_radius_z,
    is_half,
    is_quarter,
):
    vertices = [[0, 1 / 2, 0], [0, -1 / 2, 0]]
    for i in range(CYLINDER_SEGMENTS + 1):
        rotation_tmp = np.pi * 2 / CYLINDER_SEGMENTS * i
        if is_half:
            rotation_tmp = rotation_tmp / 2
        elif is_quarter:
            rotation_tmp = rotation_tmp / 4
        vertices.append([np.cos(rotation_tmp), 1 / 2, np.sin(rotation_tmp)])
        vertices.append([np.cos(rotation_tmp), -1 / 2, np.sin(rotation_tmp)])
    vertices = np.array(vertices)

    faces = [[1, 0, 3], [0, 2, 3]]
    for i in range(CYLINDER_SEGMENTS):
        faces.append([2 * i + 2, 2 * i + 4, 2 * i + 3])
        faces.append([2 * i + 5, 2 * i + 3, 2 * i + 4])
        faces.append([2 * i + 2, 0, 2 * i + 4])
        faces.append([1, 2 * i + 3, 2 * i + 5])
    faces.append([0, 1, 2 * (CYLINDER_SEGMENTS + 1) + 1])
    faces.append([2 * (CYLINDER_SEGMENTS + 1) + 1, 0, 2 * (CYLINDER_SEGMENTS + 1)])

    vertices_resize = np.array(
        [
            [top_radius, height, top_radius_z],
            [bottom_radius, height, bottom_radius_z],
        ]
    )
    vertices_resize = np.tile(vertices_resize, (int(vertices.shape[0] / 2), 1))
    return vertices * vertices_resize, np.array(faces)


def _trianguler_prism_mesh(height, top_radius, bottom_radius):
    vertices = [[0, 1 / 2, 0], [0, -1 / 2, 0]]
    num_of_segment = 3
    for i in range(num_of_segment + 1):
        rotation_tmp = np.pi * 2 / num_of_segment * i
        vertices.append([np.cos(rotation_tmp), 1 / 2, np.sin(rotation_tmp)])
        vertices.append([np.cos(rotation_tmp), -1 / 2, np.sin(rotation_tmp)])
    vertices = np.array(vertices)

    faces = []
    for i in range(num_of_segment):
        faces.append([2 * i + 2, 2 * i + 4, 2 * i + 3])
        faces.append([2 * i + 5, 2 * i + 3, 2 * i + 4])
        faces.append([2 * i + 2, 0, 2 * i + 4])
        faces.append([1, 2 * i + 3, 2 * i + 5])

    vertices_resize = np.array(
        [[top_radius, height, top_radius], [bottom_radius, height, bottom_radius]]
    )
    vertices_resize = np.tile(vertices_resize, (int(vertices.shape[0] / 2), 1))
    return vertices * vertices_resize, np.array(faces)


def _cone_mesh(radius, height, tip_offset, radius_z):
    vertices = [[0, 0, 0], [0, 0, 0]]
    for _ in range(CYLINDER_SEGMENTS + 1):
        vertices.append([0, 0, 0])
    vertices = np.array(vertices)

    faces = []
    for i in range(CYLINDER_SEGMENTS):
        faces.append([0, i + 2, i + 3])
        faces.append([1, i + 3, i + 2])

    vertices_resize = np.array([[0, 0, 0], [tip_offset[0], height, tip_offset[1]]])
    for i in range(CYLINDER_SEGMENTS + 1):
        rotation_tmp = np.pi * 2 / CYLINDER_SEGMENTS * i
        size_tmp = np.array(
            [radius * np.cos(rotation_tmp), 0, radius_z * np.sin(rotation_tmp)]
        )
        vertices_resize = np.concatenate([vertices_resize, size_tmp[None, :]], axis=0)
    return vertices + vertices_resize, np.array(faces)


def _rectangular_ring_mesh(
    front_height,
    outer_top_length,
    outer_top_width,
    inner_top_length,
    inner_top_width,
    inner_offset,
    outer_bottom_length,
    outer_bottom_width,
    inner_bottom_length,
    inner_bottom_width,
    back_height,
    top_bottom_offset,
):
    vertices = np.array(
        [
            [-1 / 2, 1 / 2, 1 / 2],
            [1 / 2, 1 / 2, 1 / 2],
            [-1 / 2, 1 / 2, -1 / 2],
            [1 / 2, 1 / 2, -1 / 2],
            [-1 / 2, -1 / 2, 1 / 2],
            [1 / 2, -1 / 2, 1 / 2],
            [-1 / 2, -1 / 2, -1 / 2],
            [1 / 2, -1 / 2, -1 / 2],
            [-1 / 2, 1 / 2, 1 / 2],
            [1 / 2, 1 / 2, 1 / 2],
            [-1 / 2, 1 / 2, -1 / 2],
            [1 / 2, 1 / 2, -1 / 2],
            [-1 / 2, -1 / 2, 1 / 2],
            [1 / 2, -1 / 2, 1 / 2],
            [-1 / 2, -1 / 2, -1 / 2],
            [1 / 2, -1 / 2, -1 / 2],
        ]
    )
    faces = np.array(
        [
            [0, 4, 5],
            [0, 5, 1],
            [2, 7, 6],
            [2, 3, 7],
            [0, 6, 4],
            [0, 2, 6],
            [1, 5, 7],
            [1, 7, 3],
            [4 + 8, 0 + 8, 5 + 8],
            [5 + 8, 0 + 8, 1 + 8],
            [7 + 8, 2 + 8, 6 + 8],
            [3 + 8, 2 + 8, 7 + 8],
            [6 + 8, 0 + 8, 4 + 8],
            [2 + 8, 0 + 8, 6 + 8],
            [5 + 8, 1 + 8, 7 + 8],
            [7 + 8, 1 + 8, 3 + 8],
            [0, 1, 1 + 8],
            [1 + 8, 0 + 8, 0],
            [1, 3, 3 + 8],
            [3 + 8, 1 + 8, 1],
            [3, 2, 2 + 8],
            [2 + 8, 3 + 8, 3],
            [2, 0, 0 + 8],
            [0 + 8, 2 + 8, 2],
            [5, 4, 5 + 8],
            [4 + 8, 5 + 8, 4],
            [7, 5, 7 + 8],
            [5 + 8, 7 + 8, 5],
            [6, 7, 6 + 8],
            [7 + 8, 6 + 8, 7],
            [4, 6, 4 + 8],
            [6 + 8, 4 + 8, 6],
        ]
    )
    vertices_resize = np.array(
        [
            [outer_top_length, front_height, outer_top_width],
            [outer_top_length, front_height, outer_top_width],
            [outer_top_length, back_height, outer_top_width],
            [outer_top_length, back_height, outer_top_width],
            [outer_bottom_length, front_height, outer_bottom_width],
            [outer_bottom_length, front_height, outer_bottom_width],
            [outer_bottom_length, back_height, outer_bottom_width],
            [outer_bottom_length, back_height, outer_bottom_width],
            [inner_top_length, front_height, inner_top_width],
            [inner_top_length, front_height, inner_top_width],
            [inner_top_length, back_height, inner_top_width],
            [inner_top_length, back_height, inner_top_width],
            [inner_bottom_length, front_height, inner_bottom_width],
            [inner_bottom_length, front_height, inner_bottom_width],
            [inner_bottom_length, back_height, inner_bottom_width],
            [inner_bottom_length, back_height, inner_bottom_width],
        ]
    )
    vertices = vertices * vertices_resize
    vertices_offset = np.array(
        [
            [0, 0, 0],
            [0, 0, 0],
            [0, (back_height - front_height) / 2, 0],
            [0, (back_height - front_height) / 2, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, (back_height - front_height) / 2, 0],
            [0, (back_height - front_height) / 2, 0],
            [inner_offset[0], 0, inner_offset[1]],
            [inner_offset[0], 0, inner_offset[1]],
            [inner_offset[0], (back_height - front_height) / 2, inner_offset[1]],
            [inner_offset[0], (back_height - front_height) / 2, inner_offset[1]],
            [inner_offset[0], 0, inner_offset[1]],
            [inner_offset[0], 0, inner_offset[1]],
            [inner_offset[0], (back_height - front_height) / 2, inner_offset[1]],
            [inner_offset[0], (back_height - front_height) / 2, inner_offset[1]],
        ]
    )
    vertices = vertices + vertices_offset
    vertices_top_offset = np.array(
        [
            [top_bottom_offset[0], 0, top_bottom_offset[1]],
            [top_bottom_offset[0], 0, top_bottom_offset[1]],
            [top_bottom_offset[0], 0, top_bottom_offset[1]],
            [top_bottom_offset[0], 0, top_bottom_offset[1]],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [top_bottom_offset[0], 0, top_bottom_offset[1]],
            [top_bottom_offset[0], 0, top_bottom_offset[1]],
            [top_bottom_offset[0], 0, top_bottom_offset[1]],
            [top_bottom_offset[0], 0, top_bottom_offset[1]],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
    )
    return vertices + vertices_top_offset, faces


def _ring_mesh(
    height,
    outer_top_radius,
    inner_top_radius,
    exist_angle,
    outer_bottom_radius,
    inner_bottom_radius,
    back_height,
    generatrix_offset,
    x_z_ratio,
    inner_x_z_ratio,
    inner_offset,
):
    vertices = []
    for _ in range(CYLINDER_SEGMENTS + 1):
        vertices.append([0, 0, 0])
        vertices.append([0, 0, 0])
        vertices.append([0, 0, 0])
        vertices.append([0, 0, 0])
    vertices = np.array(vertices)

    faces = [[0, 1, 2], [1, 3, 2]]
    for i in range(CYLINDER_SEGMENTS):
        faces.append([4 * i + 0, 4 * i + 2, 4 * (i + 1) + 2])
        faces.append([4 * i + 0, 4 * (i + 1) + 2, 4 * (i + 1)])
        faces.append([4 * i + 1, 4 * (i + 1) + 3, 4 * i + 3])
        faces.append([4 * i + 1, 4 * (i + 1) + 1, 4 * (i + 1) + 3])
        faces.append([4 * i + 1, 4 * i + 0, 4 * (i + 1) + 0])
        faces.append([4 * i + 1, 4 * (i + 1) + 0, 4 * (i + 1) + 1])
        faces.append([4 * (i + 1) + 2, 4 * i + 2, 4 * i + 3])
        faces.append([4 * (i + 1) + 2, 4 * i + 3, 4 * (i + 1) + 3])
    faces.append([CYLINDER_SEGMENTS * 4 + 0, CYLINDER_SEGMENTS * 4 + 2, CYLINDER_SEGMENTS * 4 + 1])
    faces.append([CYLINDER_SEGMENTS * 4 + 1, CYLINDER_SEGMENTS * 4 + 2, CYLINDER_SEGMENTS * 4 + 3])

    size = None
    for i in range(CYLINDER_SEGMENTS + 1):
        rotation_tmp = exist_angle / CYLINDER_SEGMENTS * i
        top_y = height / 2 + (back_height / 2 + generatrix_offset - height / 2) / (
            outer_top_radius * 2
        ) * (outer_top_radius * (1 - np.cos(rotation_tmp)))
        bottom_y = -height / 2 + (
            -back_height / 2 + generatrix_offset + height / 2
        ) / (outer_bottom_radius * 2) * (
            outer_bottom_radius * (1 - np.cos(rotation_tmp))
        )
        top_outer_vert = np.array(
            [
                outer_top_radius * x_z_ratio * np.cos(rotation_tmp),
                top_y,
                outer_top_radius * np.sin(rotation_tmp),
            ]
        )
        bottom_outer_vert = np.array(
            [
                outer_bottom_radius * x_z_ratio * np.cos(rotation_tmp),
                bottom_y,
                outer_bottom_radius * np.sin(rotation_tmp),
            ]
        )

        sur_delta_y = top_y - height / 2
        sur_delta_y_new = min(
            sur_delta_y,
            (back_height / 2 + generatrix_offset - height / 2) - sur_delta_y,
        )
        sur_y_gap = (
            back_height / 2 + generatrix_offset - height / 2
        ) - sur_delta_y_new * 2
        section_chord = np.sqrt(
            (outer_top_radius * 2) * (outer_top_radius * 2) + sur_y_gap * sur_y_gap
        )
        delta_chord = (
            section_chord
            * (outer_top_radius - inner_top_radius)
            / (outer_top_radius * 2)
        )
        delta_y = np.sqrt(
            np.abs(
                delta_chord * delta_chord
                - (outer_top_radius - inner_top_radius)
                * (outer_top_radius - inner_top_radius)
            )
        )
        if sur_delta_y > (
            (back_height / 2 + generatrix_offset - height / 2) - sur_delta_y
        ):
            delta_y = -delta_y
        top_inner_vert = np.array(
            [
                inner_top_radius * inner_x_z_ratio * np.cos(rotation_tmp),
                top_y + delta_y,
                inner_top_radius * np.sin(rotation_tmp),
            ]
        )
        top_inner_vert += np.array([0, inner_offset[1], -inner_offset[0]])

        sur_delta_y = bottom_y + height / 2
        sur_delta_y_new = max(
            sur_delta_y,
            (-back_height / 2 + generatrix_offset + height / 2) - sur_delta_y,
        )
        sur_y_gap = (
            -back_height / 2 + generatrix_offset + height / 2
        ) - sur_delta_y_new * 2
        section_chord = np.sqrt(
            (outer_bottom_radius * 2) * (outer_bottom_radius * 2)
            + sur_y_gap * sur_y_gap
        )
        delta_chord = (
            section_chord
            * (outer_bottom_radius - inner_bottom_radius)
            / (outer_bottom_radius * 2)
        )
        delta_y = np.sqrt(
            np.abs(
                delta_chord * delta_chord
                - (outer_bottom_radius - inner_bottom_radius)
                * (outer_bottom_radius - inner_bottom_radius)
            )
        )
        if sur_delta_y > (
            (-back_height / 2 + generatrix_offset + height / 2) - sur_delta_y
        ):
            delta_y = -delta_y
        bottom_inner_vert = np.array(
            [
                inner_bottom_radius * inner_x_z_ratio * np.cos(rotation_tmp),
                bottom_y + delta_y,
                inner_bottom_radius * np.sin(rotation_tmp),
            ]
        )
        bottom_inner_vert += np.array([0, inner_offset[1], -inner_offset[0]])

        size_tmp = np.array(
            [top_outer_vert, bottom_outer_vert, top_inner_vert, bottom_inner_vert]
        )
        if size is None:
            size = size_tmp
        else:
            size = np.concatenate((size, size_tmp), axis=0)

    return vertices + size, np.array(faces)


def _torus_mesh(central_radius, start_torus_radius, exist_angle, end_torus_radius):
    vertices = [[0, 0, 0], [0, 0, 0]]
    for _ in range(TORUS_CENTER_SEGMENTS + 1):
        for _ in range(TORUS_TUBE_SEGMENTS + 1):
            vertices.append([0, 0, 0])
    vertices = np.array(vertices)

    faces = []
    for i in range(TORUS_TUBE_SEGMENTS):
        faces.append([0, 2 + i + 1, 2 + i])
        faces.append(
            [
                1,
                2 + (TORUS_CENTER_SEGMENTS + 1) * TORUS_TUBE_SEGMENTS + i,
                2 + (TORUS_CENTER_SEGMENTS + 1) * TORUS_TUBE_SEGMENTS + i + 1,
            ]
        )

    for i in range(TORUS_CENTER_SEGMENTS):
        for j in range(TORUS_TUBE_SEGMENTS):
            faces.append(
                [
                    2 + (TORUS_TUBE_SEGMENTS + 1) * i + j + 1,
                    2 + (TORUS_TUBE_SEGMENTS + 1) * (i + 1) + j,
                    2 + (TORUS_TUBE_SEGMENTS + 1) * i + j,
                ]
            )
            faces.append(
                [
                    2 + (TORUS_TUBE_SEGMENTS + 1) * i + j + 1,
                    2 + (TORUS_TUBE_SEGMENTS + 1) * (i + 1) + j + 1,
                    2 + (TORUS_TUBE_SEGMENTS + 1) * (i + 1) + j,
                ]
            )

    size = np.array(
        [
            [central_radius, 0, 0],
            [
                central_radius * np.cos(exist_angle),
                0,
                central_radius * np.sin(exist_angle),
            ],
        ]
    )
    for i in range(TORUS_CENTER_SEGMENTS + 1):
        rotation_center_tmp = exist_angle / TORUS_CENTER_SEGMENTS * i
        outer_torus_radius_tmp = (
            start_torus_radius * (TORUS_CENTER_SEGMENTS - i) + end_torus_radius * i
        ) / TORUS_CENTER_SEGMENTS
        for j in range(TORUS_TUBE_SEGMENTS + 1):
            rotation_torus_tmp = np.pi * 2 / TORUS_TUBE_SEGMENTS * j
            outer_total_length = central_radius + outer_torus_radius_tmp * np.cos(
                rotation_torus_tmp
            )
            outer_size_tmp = np.array(
                [
                    outer_total_length * np.cos(rotation_center_tmp),
                    outer_torus_radius_tmp * np.sin(rotation_torus_tmp),
                    outer_total_length * np.sin(rotation_center_tmp),
                ]
            )
            size = np.concatenate((size, outer_size_tmp[None, :]), axis=0)

    return vertices + size, np.array(faces)


def _box_cylinder_ring_mesh(
    outer_height,
    outer_length,
    outer_width,
    inner_radius,
    inner_cylinder_offset,
):
    vertices = [
        [-1 / 2, 1 / 2, 1 / 2],
        [1 / 2, 1 / 2, 1 / 2],
        [-1 / 2, 1 / 2, -1 / 2],
        [1 / 2, 1 / 2, -1 / 2],
        [-1 / 2, -1 / 2, 1 / 2],
        [1 / 2, -1 / 2, 1 / 2],
        [-1 / 2, -1 / 2, -1 / 2],
        [1 / 2, -1 / 2, -1 / 2],
    ]
    for i in range(CYLINDER_SEGMENTS + 1):
        rotation_tmp = np.pi * 2 / CYLINDER_SEGMENTS * i
        vertices.append([np.cos(rotation_tmp), np.sin(rotation_tmp), 1 / 2])
        vertices.append([np.cos(rotation_tmp), np.sin(rotation_tmp), -1 / 2])
    vertices = np.array(vertices)

    faces = [
        [0, 1, 2],
        [1, 3, 2],
        [4, 6, 5],
        [5, 6, 7],
        [0, 6, 4],
        [0, 2, 6],
        [1, 5, 7],
        [1, 7, 3],
        [1, 0, 8 + CYLINDER_SEGMENTS / 4 * 1 * 2],
        [0, 4, 8 + CYLINDER_SEGMENTS / 4 * 2 * 2],
        [4, 5, 8 + CYLINDER_SEGMENTS / 4 * 3 * 2],
        [5, 1, 8 + CYLINDER_SEGMENTS / 4 * 4 * 2],
    ]
    label = [1, 0, 4, 5]
    for i in range(CYLINDER_SEGMENTS):
        faces.append([label[int(i * 4 / CYLINDER_SEGMENTS)], 8 + (i + 1) * 2, 8 + i * 2])

    faces.extend(
        [
            [2, 3, 8 + CYLINDER_SEGMENTS / 4 * 1 * 2 + 1],
            [6, 2, 8 + CYLINDER_SEGMENTS / 4 * 2 * 2 + 1],
            [7, 6, 8 + CYLINDER_SEGMENTS / 4 * 3 * 2 + 1],
            [3, 7, 8 + CYLINDER_SEGMENTS / 4 * 4 * 2 + 1],
        ]
    )
    label = [3, 2, 6, 7]
    for i in range(CYLINDER_SEGMENTS):
        faces.append([label[int(i * 4 / CYLINDER_SEGMENTS)], 8 + i * 2 + 1, 8 + (i + 1) * 2 + 1])

    for i in range(CYLINDER_SEGMENTS):
        faces.append([8 + i * 2, 8 + (i + 1) * 2, 8 + i * 2 + 1])
        faces.append([8 + i * 2 + 1, 8 + (i + 1) * 2, 8 + (i + 1) * 2 + 1])

    outer_size = np.tile(
        np.array([outer_length, outer_height, outer_width])[None, :], (8, 1)
    )
    inner_size = np.tile(
        np.array([inner_radius, inner_radius, outer_width])[None, :],
        (vertices.shape[0] - 8, 1),
    )
    vertices = vertices * np.concatenate((outer_size, inner_size), axis=0)

    outer_offset = np.tile(np.array([0, 0, 0])[None, :], (8, 1))
    inner_offset = np.tile(
        np.array([inner_cylinder_offset[0], inner_cylinder_offset[1], 0])[None, :],
        (vertices.shape[0] - 8, 1),
    )
    return vertices + np.concatenate((outer_offset, inner_offset), axis=0), np.array(faces)


def _cylinder_box_ring_mesh(
    outer_radius,
    outer_height,
    inner_length,
    inner_width,
    inner_cuboid_offset,
):
    vertices = [
        [-1 / 2, 1 / 2, 1 / 2],
        [1 / 2, 1 / 2, 1 / 2],
        [-1 / 2, 1 / 2, -1 / 2],
        [1 / 2, 1 / 2, -1 / 2],
        [-1 / 2, -1 / 2, 1 / 2],
        [1 / 2, -1 / 2, 1 / 2],
        [-1 / 2, -1 / 2, -1 / 2],
        [1 / 2, -1 / 2, -1 / 2],
    ]
    for i in range(CYLINDER_SEGMENTS + 1):
        rotation_tmp = np.pi * 2 / CYLINDER_SEGMENTS * i
        vertices.append([np.cos(rotation_tmp), np.sin(rotation_tmp), 1 / 2])
        vertices.append([np.cos(rotation_tmp), np.sin(rotation_tmp), -1 / 2])
    vertices = np.array(vertices)

    faces = [
        [0, 2, 1],
        [1, 2, 3],
        [4, 5, 6],
        [5, 7, 6],
        [0, 4, 6],
        [0, 6, 2],
        [1, 7, 5],
        [1, 3, 7],
        [0, 1, 8 + CYLINDER_SEGMENTS / 4 * 1 * 2],
        [4, 0, 8 + CYLINDER_SEGMENTS / 4 * 2 * 2],
        [5, 4, 8 + CYLINDER_SEGMENTS / 4 * 3 * 2],
        [1, 5, 8 + CYLINDER_SEGMENTS / 4 * 4 * 2],
    ]
    label = [1, 0, 4, 5]
    for i in range(CYLINDER_SEGMENTS):
        faces.append([label[int(i * 4 / CYLINDER_SEGMENTS)], 8 + i * 2, 8 + (i + 1) * 2])

    faces.extend(
        [
            [3, 2, 8 + CYLINDER_SEGMENTS / 4 * 1 * 2 + 1],
            [2, 6, 8 + CYLINDER_SEGMENTS / 4 * 2 * 2 + 1],
            [6, 7, 8 + CYLINDER_SEGMENTS / 4 * 3 * 2 + 1],
            [7, 3, 8 + CYLINDER_SEGMENTS / 4 * 4 * 2 + 1],
        ]
    )
    label = [3, 2, 6, 7]
    for i in range(CYLINDER_SEGMENTS):
        faces.append([label[int(i * 4 / CYLINDER_SEGMENTS)], 8 + (i + 1) * 2 + 1, 8 + i * 2 + 1])

    for i in range(CYLINDER_SEGMENTS):
        faces.append([8 + (i + 1) * 2, 8 + i * 2, 8 + i * 2 + 1])
        faces.append([8 + (i + 1) * 2 + 1, 8 + (i + 1) * 2, 8 + i * 2 + 1])

    inner_size = np.tile(np.array([inner_length, inner_width, outer_height])[None, :], (8, 1))
    outer_size = np.tile(
        np.array([outer_radius, outer_radius, outer_height])[None, :],
        (vertices.shape[0] - 8, 1),
    )
    vertices = vertices * np.concatenate((inner_size, outer_size), axis=0)

    inner_offset = np.tile(
        np.array([inner_cuboid_offset[0], inner_cuboid_offset[1], 0])[None, :],
        (8, 1),
    )
    outer_offset = np.tile(np.array([0, 0, 0])[None, :], (vertices.shape[0] - 8, 1))
    return vertices + np.concatenate((inner_offset, outer_offset), axis=0), np.array(faces)


class Cuboid(GeometryTemplate):
    def __init__(
        self,
        height,
        top_length,
        top_width=None,
        bottom_length=None,
        bottom_width=None,
        top_offset=[0, 0],
        back_height=None,
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        rotation_order="XYZ",
    ):
        if top_width is None:
            top_width = top_length
        if bottom_length is None:
            bottom_length = top_length
        if bottom_width is None:
            bottom_width = top_width
        if back_height is None:
            back_height = height

        vertices, faces = _cuboid_mesh(
            height,
            top_length,
            top_width,
            bottom_length,
            bottom_width,
            _list(top_offset),
            back_height,
        )
        _init_native(self, vertices, faces, position, rotation, rotation_order)

        self.height = height
        self.top_length = top_length
        self.top_width = top_width
        self.bottom_length = bottom_length
        self.bottom_width = bottom_width
        self.top_offset = _list(top_offset)
        self.back_height = back_height

        _register_box_anchors(self)


class Sphere(GeometryTemplate):
    def __init__(
        self,
        radius,
        top_angle=0,
        bottom_angle=np.pi,
        radius_y=None,
        radius_z=None,
        longitude_angle=np.pi * 2,
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        rotation_order="XYZ",
    ):
        if radius_y is None:
            radius_y = radius
        if radius_z is None:
            radius_z = radius

        vertices, faces = _sphere_mesh(
            radius,
            top_angle,
            bottom_angle,
            radius_y,
            radius_z,
            longitude_angle,
        )
        _init_native(self, vertices, faces, position, rotation, rotation_order)

        self.radius = radius
        self.top_angle = top_angle
        self.bottom_angle = bottom_angle
        self.radius_y = radius_y
        self.radius_z = radius_z
        self.longitude_angle = longitude_angle

        self._set_anchor("top_pole", self.local_vertices[-2], normal=[0, 1, 0])
        self._set_anchor("bottom_pole", self.local_vertices[-1], normal=[0, -1, 0])


class Cylinder(GeometryTemplate):
    def __init__(
        self,
        height,
        top_radius,
        bottom_radius=None,
        top_radius_z=None,
        bottom_radius_z=None,
        is_half=False,
        is_quarter=False,
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        rotation_order="XYZ",
    ):
        if bottom_radius is None:
            bottom_radius = top_radius
        if top_radius_z is None:
            top_radius_z = top_radius
        if bottom_radius_z is None:
            bottom_radius_z = bottom_radius

        vertices, faces = _cylinder_mesh(
            height,
            top_radius,
            bottom_radius,
            top_radius_z,
            bottom_radius_z,
            is_half,
            is_quarter,
        )
        _init_native(self, vertices, faces, position, rotation, rotation_order)

        self.height = height
        self.top_radius = top_radius
        self.bottom_radius = bottom_radius
        self.top_radius_z = top_radius_z
        self.bottom_radius_z = bottom_radius_z
        self.is_half = is_half
        self.is_quarter = is_quarter

        self._set_anchor("top_center", self.local_vertices[0], normal=[0, 1, 0])
        self._set_anchor("bottom_center", self.local_vertices[1], normal=[0, -1, 0])
        if is_half:
            self._set_anchor("half_flat_center", [0.0, 0.0, 0.0], normal=[0, 0, -1])
            self._set_anchor_alias("flat_back_center", "half_flat_center")


class Trianguler_Prism(GeometryTemplate):
    def __init__(
        self,
        height,
        top_radius,
        bottom_radius=None,
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        rotation_order="XYZ",
    ):
        if bottom_radius is None:
            bottom_radius = top_radius

        vertices, faces = _trianguler_prism_mesh(height, top_radius, bottom_radius)
        _init_native(self, vertices, faces, position, rotation, rotation_order)

        self.height = height
        self.top_radius = top_radius
        self.bottom_radius = bottom_radius

        self._set_anchor("top_center", self.local_vertices[0], normal=[0, 1, 0])
        self._set_anchor("bottom_center", self.local_vertices[1], normal=[0, -1, 0])


class Cone(GeometryTemplate):
    def __init__(
        self,
        radius,
        height,
        tip_offset=[0, 0],
        radius_z=None,
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        rotation_order="XYZ",
    ):
        if radius_z is None:
            radius_z = radius

        vertices, faces = _cone_mesh(radius, height, _list(tip_offset), radius_z)
        _init_native(self, vertices, faces, position, rotation, rotation_order)

        self.radius = radius
        self.height = height
        self.tip_offset = _list(tip_offset)
        self.radius_z = radius_z

        self._set_anchor("base_center", self.local_vertices[0], normal=[0, -1, 0])
        self._set_anchor("bottom_center", self.local_vertices[0], normal=[0, -1, 0])
        self._set_anchor("tip", self.local_vertices[1], normal=[0, 1, 0])
        self._set_anchor_alias("apex", "tip")
        self._set_anchor_alias("top_center", "tip")


class Rectangular_Ring(GeometryTemplate):
    def __init__(
        self,
        front_height,
        outer_top_length,
        outer_top_width,
        inner_top_length,
        inner_top_width,
        inner_offset=[0, 0],
        outer_bottom_length=None,
        outer_bottom_width=None,
        inner_bottom_length=None,
        inner_bottom_width=None,
        back_height=None,
        top_bottom_offset=[0, 0],
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        rotation_order="XYZ",
    ):
        if outer_bottom_length is None:
            outer_bottom_length = outer_top_length
        if outer_bottom_width is None:
            outer_bottom_width = outer_top_width
        if inner_bottom_length is None:
            inner_bottom_length = inner_top_length
        if inner_bottom_width is None:
            inner_bottom_width = inner_top_width
        if back_height is None:
            back_height = front_height

        vertices, faces = _rectangular_ring_mesh(
            front_height,
            outer_top_length,
            outer_top_width,
            inner_top_length,
            inner_top_width,
            _list(inner_offset),
            outer_bottom_length,
            outer_bottom_width,
            inner_bottom_length,
            inner_bottom_width,
            back_height,
            _list(top_bottom_offset),
        )
        _init_native(self, vertices, faces, position, rotation, rotation_order)

        self.front_height = front_height
        self.outer_top_length = outer_top_length
        self.outer_top_width = outer_top_width
        self.inner_top_length = inner_top_length
        self.inner_top_width = inner_top_width
        self.inner_offset = _list(inner_offset)
        self.outer_bottom_length = outer_bottom_length
        self.outer_bottom_width = outer_bottom_width
        self.inner_bottom_length = inner_bottom_length
        self.inner_bottom_width = inner_bottom_width
        self.back_height = back_height
        self.top_bottom_offset = _list(top_bottom_offset)

        _register_box_anchors(self, prefix="outer_", indices=range(8))
        _register_box_anchors(self, prefix="inner_", indices=range(8, 16))


class Ring(GeometryTemplate):
    def __init__(
        self,
        height,
        outer_top_radius,
        inner_top_radius,
        exist_angle=np.pi * 2,
        outer_bottom_radius=None,
        inner_bottom_radius=None,
        back_height=None,
        generatrix_offset=0,
        x_z_ratio=1,
        inner_x_z_ratio=None,
        inner_offset=[0, 0],
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        rotation_order="XYZ",
    ):
        if outer_bottom_radius is None:
            outer_bottom_radius = outer_top_radius
        if inner_bottom_radius is None:
            inner_bottom_radius = inner_top_radius
        if back_height is None:
            back_height = height
        if inner_x_z_ratio is None:
            inner_x_z_ratio = x_z_ratio

        vertices, faces = _ring_mesh(
            height,
            outer_top_radius,
            inner_top_radius,
            exist_angle,
            outer_bottom_radius,
            inner_bottom_radius,
            back_height,
            generatrix_offset,
            x_z_ratio,
            inner_x_z_ratio,
            _list(inner_offset),
        )
        _init_native(self, vertices, faces, position, rotation, rotation_order)

        self.height = height
        self.outer_top_radius = outer_top_radius
        self.inner_top_radius = inner_top_radius
        self.exist_angle = exist_angle
        self.outer_bottom_radius = outer_bottom_radius
        self.inner_bottom_radius = inner_bottom_radius
        self.back_height = back_height
        self.generatrix_offset = generatrix_offset
        self.x_z_ratio = x_z_ratio
        self.inner_x_z_ratio = inner_x_z_ratio
        self.inner_offset = _list(inner_offset)

        self._set_anchor(
            "axis_top_center",
            np.array([0.0, height / 2.0, 0.0]),
            normal=[0, 1, 0],
        )
        self._set_anchor(
            "axis_bottom_center",
            np.array([0.0, -height / 2.0, 0.0]),
            normal=[0, -1, 0],
        )
        self._set_anchor("arc_origin", np.array([0.0, 0.0, 0.0]))
        self._set_anchor_alias("arc_center", "arc_origin")
        self._set_anchor("centerline_start", np.mean(self.local_vertices[:4], axis=0))
        self._set_anchor("centerline_end", np.mean(self.local_vertices[-4:], axis=0))
        self._set_anchor("outer_top_start", self.local_vertices[0])
        self._set_anchor("outer_bottom_start", self.local_vertices[1])
        self._set_anchor("inner_top_start", self.local_vertices[2])
        self._set_anchor("inner_bottom_start", self.local_vertices[3])
        self._set_anchor("outer_top_end", self.local_vertices[-4])
        self._set_anchor("outer_bottom_end", self.local_vertices[-3])
        self._set_anchor("inner_top_end", self.local_vertices[-2])
        self._set_anchor("inner_bottom_end", self.local_vertices[-1])
        self._set_anchor("outer_mid_start", np.mean(self.local_vertices[[0, 1]], axis=0))
        self._set_anchor("inner_mid_start", np.mean(self.local_vertices[[2, 3]], axis=0))
        self._set_anchor("outer_mid_end", np.mean(self.local_vertices[[-4, -3]], axis=0))
        self._set_anchor("inner_mid_end", np.mean(self.local_vertices[[-2, -1]], axis=0))


class Torus(GeometryTemplate):
    def __init__(
        self,
        central_radius,
        start_torus_radius,
        exist_angle=np.pi * 2,
        end_torus_radius=None,
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        rotation_order="XYZ",
    ):
        if end_torus_radius is None:
            end_torus_radius = start_torus_radius

        vertices, faces = _torus_mesh(
            central_radius, start_torus_radius, exist_angle, end_torus_radius
        )
        _init_native(self, vertices, faces, position, rotation, rotation_order)

        self.central_radius = central_radius
        self.start_torus_radius = start_torus_radius
        self.exist_angle = exist_angle
        self.end_torus_radius = end_torus_radius

        self._set_anchor("start_center", self.local_vertices[0])
        self._set_anchor("end_center", self.local_vertices[1])


class Box_Cylinder_Ring(GeometryTemplate):
    def __init__(
        self,
        outer_height,
        outer_length,
        outer_width,
        inner_radius,
        inner_cylinder_offset=[0, 0],
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        rotation_order="XYZ",
    ):
        vertices, faces = _box_cylinder_ring_mesh(
            outer_height,
            outer_length,
            outer_width,
            inner_radius,
            _list(inner_cylinder_offset),
        )
        _init_native(self, vertices, faces, position, rotation, rotation_order)

        self.outer_height = outer_height
        self.outer_length = outer_length
        self.outer_width = outer_width
        self.inner_radius = inner_radius
        self.inner_cylinder_offset = _list(inner_cylinder_offset)

        _register_box_anchors(self, prefix="outer_", indices=range(8))
        self._set_anchor("inner_front_center", np.mean(self.local_vertices[8::2], axis=0))
        self._set_anchor("inner_back_center", np.mean(self.local_vertices[9::2], axis=0))


class Cylinder_Box_Ring(GeometryTemplate):
    def __init__(
        self,
        outer_radius,
        outer_height,
        inner_length,
        inner_width,
        inner_cuboid_offset=[0, 0],
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        rotation_order="XYZ",
    ):
        vertices, faces = _cylinder_box_ring_mesh(
            outer_radius,
            outer_height,
            inner_length,
            inner_width,
            _list(inner_cuboid_offset),
        )
        _init_native(self, vertices, faces, position, rotation, rotation_order)

        self.outer_radius = outer_radius
        self.outer_height = outer_height
        self.inner_length = inner_length
        self.inner_width = inner_width
        self.inner_cuboid_offset = _list(inner_cuboid_offset)

        _register_box_anchors(self, prefix="inner_", indices=range(8))
        self._set_anchor("outer_front_center", np.mean(self.local_vertices[8::2], axis=0))
        self._set_anchor("outer_back_center", np.mean(self.local_vertices[9::2], axis=0))
