# geometry Primitive Handout

本文是 `code/geometry/` 的操作速查。category 重写时应先用这里列出的 primitive、anchor 和 transform 能力表达装配关系；只有这里缺少通用能力时，才考虑新增 primitive anchor 或 primitive/base transform API。

## 基本约定

- primitive 保存 `local_vertices`、`faces`、`position`、`rotation`、`rotation_order`。
- `vertices` 是动态世界坐标视图；修改 transform 不会改写 `local_vertices`。
- geometry primitive 的旋转角单位是弧度。
- `ConceptTemplate` 的 concept 级 `rotation` 是角度，会在最终 `vertices` 视图中转换为弧度。
- 局部坐标约定保持 legacy 兼容：大多数竖向 primitive 的主高度轴是 local Y。

## 通用 Primitive API

所有 primitive 都继承以下能力：

```python
part.anchor_names()
part.local_anchor("name")
part.world_anchor("name")
part.local_anchor_frame("name")
part.world_anchor_frame("name")
part.world_point(local_point)
part.world_vertices()
part.local_bounds()
part.world_bounds()
```

transform 操作：

```python
part.set_transform(position=..., rotation=..., rotation_order=...)
part.set_rotation_matrix(matrix)
part.with_name("semantic_name")
part.move_anchor_to("source_anchor", target_point)
part.move_local_point_to(local_point, target_point)
part.move_local_point_axes_to(local_point, target_point, ("x", "y"))
part.move_anchor_axis_to("source_anchor", target_value, "x")
part.align_axis_between_points("y", start_point, end_point)
part.rotate_about_point(pivot_point, rotation, rotation_order="XYZ")
part.reflect_across_coordinate_plane("z")
```

优先级说明：

- 首选 `move_anchor_to()`，它表达完整 3D 锚点对齐。
- 当接触点是 primitive 表面上的参数化局部点、但不是稳定公共 anchor 时，使用 `move_local_point_to()`。
- 当一个部件需要保留某些布局轴，只在部分坐标轴上对齐局部接触点时，使用 `move_local_point_axes_to()`，并在 concept 测试中明确验证被保留的轴。
- `world_anchor()` 和 `world_point()` 会使用当前 transform 动态计算，不需要 concept 层手算旋转后的坐标。
- `move_anchor_axis_to()` 只适合保留 legacy 单轴投影对齐或极少数 parity 场景，不应作为新装配逻辑的默认写法。
- `set_rotation_matrix()` 用于欧拉三元组难以表达的复合旋转；它仍然保持 primitive 的 local mesh 和 anchor 模型。
- `align_axis_between_points()` 用于表达杆件/管件的某条局部轴连接两个安装点；primitive 的尺寸仍由构造参数决定。
- `rotate_about_point()` 用于表达夹口、翻盖等绕父坐标系中某个 pivot 开合的关系。
- `reflect_across_coordinate_plane()` 用于表达关于 `x=0` / `y=0` / `z=0` 坐标平面的镜像复制，并会同步反转 face winding。

transform 工具：

```python
rotate_y(point_or_points, angle)
radial_array_frames(
    count,
    center_point,
    item_rotation=(0.0, 0.0, 0.0),
    radial_axis="y",
    angle_sign=1.0,
    post_rotation_steps=(),
)
```

`radial_array_frames()` 用于表达等角径向阵列。它返回每个阵列项的
`RadialArrayFrame(index, angle, position, rotation_matrix)`；concept 层可以把
`position` 传给 primitive，把 `rotation_matrix` 传给 `set_rotation_matrix()`。
适用场景是星形脚、轮辐、圆周分布的把手/装饰件等“同一局部部件绕轴重复”的关系。
它只生成 frame，不创建 mesh，也不承担 category 专属尺寸推导。

anchor 选择规则：

- 先判断装配关系是点接触、边线接触、面接触还是 bbox 对齐，再选择对应 anchor。
- 不要因为某个 anchor 的坐标方便，就把边中心当成面中心、把 bbox anchor 当成真实表面 anchor。
- 如果一个部件要贴到另一个部件的面，应优先使用 `front_center`、`back_center`、`top_center`、`bottom_center` 等面中心；只有真实语义是边线时才使用 `bottom_back_center`、`back_left_center` 这类边中心。
- 对非零 delta 的可视化，先检查 anchor 是否语义选错，再判断是否是可接受的 legacy 近似差异。

## 通用 BBox Anchor

所有 primitive 都支持这些 bbox anchor：

- `center`, `bbox_center`
- `bbox_top_center`, `bbox_bottom_center`
- `bbox_left_center`, `bbox_right_center`
- `bbox_front_center`, `bbox_back_center`
- `bbox_top_front_left`, `bbox_top_front_right`
- `bbox_top_back_left`, `bbox_top_back_right`
- `bbox_bottom_front_left`, `bbox_bottom_front_right`
- `bbox_bottom_back_left`, `bbox_bottom_back_right`

`bbox_` anchor 表示当前 primitive 局部顶点包围盒上的点。它适合对齐整体外包络，但不一定等于真实曲面上的语义点。需要真实表面、边、端点时，优先使用 primitive 自己注册的 surface anchor。

## Primitive Anchor 清单

### Cuboid

构造：

```python
Cuboid(
    height,
    top_length,
    top_width=None,
    bottom_length=None,
    bottom_width=None,
    top_offset=(0, 0),
    back_height=None,
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    rotation_order="XYZ",
)
```

局部语义：高度沿 local Y，length 沿 local X，width 沿 local Z。

surface anchors：

- `top_center`, `bottom_center`
- `front_center`, `back_center`
- `left_center`, `right_center`
- `top_front_left`, `top_front_right`, `top_back_left`, `top_back_right`
- `bottom_front_left`, `bottom_front_right`, `bottom_back_left`, `bottom_back_right`
- `top_front_center`, `top_back_center`, `top_left_center`, `top_right_center`
- `bottom_front_center`, `bottom_back_center`, `bottom_left_center`, `bottom_right_center`
- `front_left_center`, `front_right_center`, `back_left_center`, `back_right_center`

额外操作：

```python
bar.align_axis_between_points("z", start_point, end_point)
pipe.align_axis_between_points("y", start_point, end_point)
```

该方法把指定局部轴对齐到两点方向，并把 primitive center 放到两点中点。杆件或管件长度、厚度仍由构造参数决定。

### Sphere

构造：

```python
Sphere(
    radius,
    top_angle=0,
    bottom_angle=np.pi,
    radius_y=None,
    radius_z=None,
    longitude_angle=np.pi * 2,
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    rotation_order="XYZ",
)
```

surface anchors：

- `top_pole`
- `bottom_pole`

### Cylinder

构造：

```python
Cylinder(
    height,
    top_radius,
    bottom_radius=None,
    top_radius_z=None,
    bottom_radius_z=None,
    is_half=False,
    is_quarter=False,
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    rotation_order="XYZ",
)
```

局部语义：高度沿 local Y；支持圆柱、椭圆柱、锥台、半柱和四分之一柱。

surface anchors：

- `top_center`
- `bottom_center`
- `half_flat_center` / `flat_back_center`（仅 `is_half=True`，表示半圆柱平直切面中心）

### Trianguler_Prism

构造：

```python
Trianguler_Prism(
    height,
    top_radius,
    bottom_radius=None,
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    rotation_order="XYZ",
)
```

surface anchors：

- `top_center`
- `bottom_center`

### Cone

构造：

```python
Cone(
    radius,
    height,
    tip_offset=(0, 0),
    radius_z=None,
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    rotation_order="XYZ",
)
```

surface anchors：

- `base_center`
- `bottom_center`
- `tip`
- `apex`
- `top_center`

`tip`、`apex`、`top_center` 指向同一个锥尖语义点。

### Rectangular_Ring

构造：

```python
Rectangular_Ring(
    front_height,
    outer_top_length,
    outer_top_width,
    inner_top_length,
    inner_top_width,
    inner_offset=(0, 0),
    outer_bottom_length=None,
    outer_bottom_width=None,
    inner_bottom_length=None,
    inner_bottom_width=None,
    back_height=None,
    top_bottom_offset=(0, 0),
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    rotation_order="XYZ",
)
```

surface anchors：

- `outer_` + Cuboid surface anchor 名称
- `inner_` + Cuboid surface anchor 名称

常用示例：

- `outer_top_center`, `outer_bottom_center`
- `outer_front_center`, `outer_back_center`
- `inner_top_center`, `inner_bottom_center`
- `outer_top_front_center`, `inner_bottom_back_center`
- `outer_top_front_left`, `inner_bottom_back_right`

### Ring

构造：

```python
Ring(
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
    inner_offset=(0, 0),
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    rotation_order="XYZ",
)
```

surface anchors：

- `axis_top_center`, `axis_bottom_center`
- `arc_origin`, `arc_center`
- `centerline_start`, `centerline_end`
- `outer_top_start`, `outer_bottom_start`
- `inner_top_start`, `inner_bottom_start`
- `outer_top_end`, `outer_bottom_end`
- `inner_top_end`, `inner_bottom_end`
- `outer_mid_start`, `outer_mid_end`
- `inner_mid_start`, `inner_mid_end`

注意：`axis_top_center` / `axis_bottom_center` 是中心轴上的构造锚点，适合完整环壳体沿 Y 轴堆叠；它们不是实际曲面点。需要整体外包络时使用 `bbox_top_center` / `bbox_bottom_center`；需要半环端点或中心线端点时使用 start/end 系列 anchor。

### Torus

构造：

```python
Torus(
    central_radius,
    start_torus_radius,
    exist_angle=np.pi * 2,
    end_torus_radius=None,
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    rotation_order="XYZ",
)
```

surface anchors：

- `start_center`
- `end_center`

### Box_Cylinder_Ring

构造：

```python
Box_Cylinder_Ring(
    outer_height,
    outer_length,
    outer_width,
    inner_radius,
    inner_cylinder_offset=(0, 0),
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    rotation_order="XYZ",
)
```

surface anchors：

- `outer_` + Cuboid surface anchor 名称
- `inner_front_center`
- `inner_back_center`

### Cylinder_Box_Ring

构造：

```python
Cylinder_Box_Ring(
    outer_radius,
    outer_height,
    inner_length,
    inner_width,
    inner_cuboid_offset=(0, 0),
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    rotation_order="XYZ",
)
```

surface anchors：

- `inner_` + Cuboid surface anchor 名称
- `outer_front_center`
- `outer_back_center`

## Transform 工具

从 `code.geometry` 可导入：

```python
rotation_matrix(rotation, rotation_order="XYZ")
apply_transform(points, position, rotation, rotation_order="XYZ", offset_first=False)
inverse_apply_transform(points, position, rotation, rotation_order="XYZ", offset_first=False)
transform_direction(direction, rotation, rotation_order="XYZ")
rotate_y(points, angle)
radial_array_frames(...)
get_rodrigues_matrix(axis, angle)
RadialArrayFrame(index, angle, position, rotation_matrix)
Transform(position, rotation, rotation_order="XYZ")
```

使用边界：

- `rotate_y()` 只做绕 Y 轴的布局点旋转，不带平移。
- `apply_transform()` / `inverse_apply_transform()` 用于点集转换；需要复刻 legacy 先平移再旋转的整体姿态时，可使用 `offset_first=True`。
- `transform_direction()` 用于方向向量转换，不加平移。
- `radial_array_frames()` 用于同一局部部件绕轴等角重复，返回每个阵列项的位置和旋转矩阵。
- `rotation_matrix()` 应主要用于 geometry 层能力扩展或确实需要复合矩阵的场景；category concept 不应反复用它手算 anchor。

## 推荐装配模式

直接 anchor 贴合：

```python
child.move_anchor_to("bottom_center", parent.world_anchor("top_center"))
```

保留 center-layout 参数语义，同时用 anchor 装到安装高度：

```python
leg = Cuboid(
    height=leg_height,
    top_length=leg_length,
    top_width=leg_width,
    position=(center_x, 0.0, center_z),
    rotation=leg_rotation,
)
top_x, _, top_z = leg.world_anchor("top_center")
leg.move_anchor_to("top_center", (top_x, mount_height, top_z))
```

这里没有手算旋转矩阵；center-layout 仍然是参数语义，mount height 由 anchor 操作表达。读取坐标时应显式解包，不写 `top[0]` 这类下标。

使用局部语义点作为安装点：

```python
front_mount = front_leg.world_point((0.0, front_offset, 0.0))
rear_mount = rear_leg.world_point((0.0, rear_offset, 0.0))
```

把局部语义点移动到目标点：

```python
pad.move_local_point_to((0.0, -pad_height / 2.0, contact_depth), support_top)
```

连接两个安装点：

```python
span = np.linalg.norm(front_mount - rear_mount)
bar = Cuboid(height=bar_height, top_length=bar_thickness, top_width=span)
bar.align_axis_between_points("z", rear_mount, front_mount)
```

复合旋转兜底：

```python
part.set_rotation_matrix(compound_matrix)
```

径向阵列：

```python
for frame in radial_array_frames(count, center_point, item_rotation=(tilt, 0.0, 0.0)):
    part = Cuboid(..., position=frame.position)
    part.set_rotation_matrix(frame.rotation_matrix)
```

## 不推荐写法

- 在 concept 层用旋转矩阵手算 `top_center`、角点或端点。
- 用 `point[0]`、`point[1]`、`point[2]` 访问 anchor 坐标；应解包成命名变量。
- 为 primitive 包一层临时 `MeshComponent`。
- 把单个 category 的私有布局公式沉淀进 `code.geometry`。
- 默认使用 `move_anchor_axis_to()` 表达新设计。
- 因某个 category 暂时需要就新增共享 relation；应先判断能否补 primitive anchor 或 primitive/base transform 能力。

## 何时请求新增 Anchor

遇到以下情况，应先提出新增 anchor 请求，再继续 category 实现：

- 同一表面点、端点、边角或中心线点在多个 class/category 中重复出现。
- 当前必须反复使用 `world_point((...))` 或旋转矩阵才能得到一个稳定 primitive 语义点。
- 该点属于 primitive 自身的几何语义，而不是某个 category 的布局规则。
- 新 anchor 能直接替代 legacy 中一段“旋转后的坐标点”计算。

请求应说明：

- anchor 名称。
- local 坐标或局部几何语义。
- 会替代哪段 legacy 公式。
- 会帮助哪些 category/class。
