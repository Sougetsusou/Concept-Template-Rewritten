# geometry_rewritten 设计说明

本目录提供一套新的 geometry template。目标是完整覆盖 `code/geometry_template.py`
中的 primitive，同时修正旧实现中“创建时立即覆盖顶点坐标”的建模方式。

具体 primitive anchor、推荐装配模式、transform 工具和禁止写法见
`PRIMITIVE_HANDOUT.md`。category 重写时应把该 handout 作为 geometry API
操作速查。

## 覆盖范围

当前覆盖全部 legacy primitive：

- `Cuboid`
- `Sphere`
- `Cylinder`
- `Trianguler_Prism`
- `Cone`
- `Rectangular_Ring`
- `Ring`
- `Torus`
- `Box_Cylinder_Ring`
- `Cylinder_Box_Ring`

构造参数、默认值、主轴约定和 mesh shape kernel 均对齐旧实现。当前实现已经
移除对 `code.geometry_template` 的运行时依赖，所有 primitive 都在
`primitives.py` 中原生生成 `local_vertices` 和 `faces`。测试仍会与 legacy 输出
逐点比较，用于防止迁移期间发生意外几何漂移。

## 坐标分层

每个 primitive 同时保留：

- `local_vertices`: primitive 自身局部坐标系中的顶点。
- `position`, `rotation`, `rotation_order`: 从 local 到父级坐标系的变换。
- `vertices`: 动态属性，返回变换后的顶点，用于 mesh 导出和组合。

因此，修改 transform 不会破坏 local mesh：

```python
box = Cuboid(2, 3, 4)
local_before = box.local_vertices.copy()
box.set_transform(position=[1, 2, 3], rotation=[0.1, 0.2, 0.3])
assert (box.local_vertices == local_before).all()
```

## Anchor 设计

所有 primitive 都支持：

```python
part.local_anchor("name")
part.world_anchor("name")
part.local_anchor_frame("name")
part.world_anchor_frame("name")
part.anchor_names()
part.world_point(local_point)
```

通用 bbox anchor 均带 `bbox_` 前缀，例如：

- `bbox_center`
- `bbox_top_center`
- `bbox_bottom_center`
- `bbox_top_front_left`

具有明确表面语义的 primitive 会额外注册 surface anchors。例如：

- `Cuboid`: `top_center`, `bottom_center`, `front_center`, 8 个真实角点等。
- `Cylinder`: `top_center`, `bottom_center`；半圆柱还提供
  `half_flat_center` / `flat_back_center` 表示平直切面中心。
- `Cone`: `base_center`, `tip`, `apex`。
- `Torus`: `start_center`, `end_center`。
- ring 类 primitive: outer/inner start/end、`arc_origin`、`arc_center`、
  `axis_top_center`、`axis_bottom_center`、`centerline_start`、
  `centerline_end` 等锚点。

`world_anchor()` 会使用当前 transform 动态计算，因此 primitive 旋转或平移后，
anchor 不需要外部重新手算。

primitive 也可以直接以 anchor 驱动自身 transform：

```python
lower = Ring(...).with_name("lower_open_ring")
upper = Cylinder(...).with_name("upper_closed_cap")
upper.move_anchor_to("bottom_center", lower.world_anchor("axis_top_center"))
```

需要表达“已经放置好的部件绕父坐标系 pivot 开合”时，使用 `rotate_about_point()`；
需要表达镜像副本时，使用 `reflect_across_coordinate_plane()`，它会同步翻转 face
winding：

```python
jaw.rotate_about_point((0.0, 0.0, 0.0), (-angle, 0.0, 0.0))
mirrored_jaw.reflect_across_coordinate_plane("z")
```

如果 legacy 几何只对齐某个轴向投影，可使用单轴 anchor 对齐：

```python
leg = Cuboid(..., rotation=(pitch, yaw, roll))
leg.move_anchor_axis_to("top_center", 0.0, "y")
```

如果 legacy 几何确实由多段旋转矩阵复合而成，且无法用单个欧拉三元组表达，可把
复合矩阵设置到 primitive transform 上：

```python
spoke = Cuboid(...).with_name("radial_spoke")
spoke.set_rotation_matrix(compound_matrix)
```

这仍然保留 primitive 的 `local_vertices`，不会创建中间 mesh adapter。

基础 transform 工具也可以用于 concept 层的布局点变换。例如 `rotate_y(point, angle)`
表示绕 Y 轴旋转一个或一批 3D 点，不带平移；它和
`apply_transform(points, (0, 0, 0), (0, angle, 0))` 使用同一套旋转约定。
如果某个 legacy concept 的最终姿态是“先整体平移再旋转”，`ConceptTemplate` 可显式
设置 `rotation_order` 和 `offset_first=True` 来保留该 category 的姿态约定。

当关系本身是“同一个局部部件绕某个轴等角重复”时，使用
`radial_array_frames()` 生成每个阵列项的 `position` 和 `rotation_matrix`：

```python
for frame in radial_array_frames(
    count=spoke_count,
    center_point=(0.0, center_y, radial_distance),
    item_rotation=(tilt, 0.0, 0.0),
    radial_axis="y",
):
    spoke = Cuboid(..., position=frame.position)
    spoke.set_rotation_matrix(frame.rotation_matrix)
```

这个工具只表达径向 frame 阵列；每个部件的尺寸、anchor 接触和 category 专属偏移仍由
concept class 自己决定。

primitive 提供两点轴向对齐能力，用于表达“这根长方体杆件或圆柱管件连接两个安装点”：

```python
span = np.linalg.norm(end_mount - start_mount)
bar = Cuboid(height=bar_height, top_length=bar_length, top_width=span)
bar.align_axis_between_points("z", start_mount, end_mount)

pipe = Cylinder(height=pipe_length, top_radius=pipe_radius)
pipe.align_axis_between_points("y", start_mount, end_mount)
```

这个方法只负责把指定局部轴旋转到两点方向并把中心放到中点；杆件或管件的尺寸仍由
构造参数决定。

这里不会把 primitive 先降级成中间 mesh 组件；concept 层可以直接组合 primitive，
最终导出时统一读取每个 primitive 的 `vertices` 和 `faces`。

## 共享关系边界

本包当前的稳定边界是 primitive、anchor、transform 和 assembly。category 重写的
默认路径应是：

1. 用 primitive 表达局部 shape kernel。
2. 用 `local_anchor()`、`world_anchor()`、`move_anchor_to()` 和必要的 primitive/base
   transform API 表达装配。
3. 把只属于当前物体的半径插值、分段高度、布局比例等形状推导保留在该 category
   的 `concept_template.py` 私有 helper 中。

不要把 category 专属布局公式直接提升到 `code.geometry_rewritten`。如果发现某个
关系无法用现有 anchor 表达，优先提出新增 primitive anchor 或 primitive/base
transform 能力；只有同一关系在多个 category 中反复出现、语义稳定，并经过人工确认
后，才可以新增共享 relation helper。

如果工作区中出现 `relations.py`，它应被视为实验性候选，不是新 category 的默认
依赖入口。特别是带有具体 category 语义的函数、临时 mesh adapter、或绕过 primitive
transform 模型的组件包装，都不属于本包稳定公共 API。

## Assembly 设计

`assembly.py` 提供 `ConceptTemplate` 和 `combine_components()`，用于把多个 rewritten
primitive 合并成一个 concept mesh。category 代码应直接从本包导入：

```python
from code.geometry_rewritten import ConceptTemplate, Cylinder, Ring
```

`ConceptTemplate` 保留 concept 级 `local_vertices`，`vertices` 是应用最终
`position`/`rotation` 后的动态视图。这样 category 目录只需要描述 semantic
recipe，不再维护自己的 geometry/common wrapper。
