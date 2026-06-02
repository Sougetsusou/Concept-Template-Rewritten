# Rewritten 优化目标与内容

这份发行包中的 rewritten concept template 不是对 legacy 源码的逐行整理，而是对原有几何模板体系的一次语义化重构。目标是在保留原始 category 表达范围的基础上，让几何构造、参数含义和数据消费方式更清晰、更稳定。

## 优化目标

### 1. 让几何装配从公式堆叠变成语义装配

legacy 代码中大量位置计算来自 primitive 只能通过中心点、旋转和局部补偿间接定位。构件之间的关系经常表现为复杂的三角函数、矩阵补偿和手写坐标偏移。

rewritten 版本的目标是把这些隐含关系改写为更直接的装配语义，例如：

- 将一个构件的 `top_center`、`bottom_center` 或边界 anchor 对齐到另一个构件的对应位置。
- 用 `move_anchor_to()`、`move_anchor_axis_to()`、`align_axis_between_points()` 等操作表达连接、堆叠、贴合和跨点对齐。
- 只在表达真实形状推导时保留数学计算，例如弧段半径、倾斜截面、径向阵列角度。

### 2. 让参数成为 rewritten constructor 的原生输入

legacy 参数通常同时承担采样、布局、补偿和历史实现细节。rewritten 参数包的目标是让每个 concept 的参数直接对应 rewritten class constructor，而不是运行时再依赖 legacy pkl 或旧 mapper 推断。

因此发行包中的 `parameters/` 和 `parameters.pkl` 已经是可直接消费的数据资产：

- 每个 object 单独保存为 `object_XXXX.json`。
- 每个 concept 记录 rewritten class 名和 constructor 参数。
- 可视化、实例化和 mesh 合并直接读取 rewritten 参数包。

### 3. 降低 category 代码中的 legacy 习惯残留

legacy 代码中常见的复杂性包括：

- 先旋转 primitive，再在外部重新计算它的某个表面点。
- 用中心点布局表达本应由端点、顶面或接触面表达的装配关系。
- 将几何构造、参数适配和可视化比较混在同一层逻辑中。
- 对同一种空间模式重复写多份方向变体代码。

rewritten 版本尽量把这些逻辑拆清：

- primitive 负责本地几何、transform 和 anchor。
- concept template 负责 category 内的几何装配语义。
- rewritten parameter package 负责保存可消费的 object 参数。
- release 工具只负责读取、实例化、可视化和导出。

### 4. 保留必要的几何表达，而不是追求机械简化

并非所有三角函数或矩阵运算都应删除。rewritten 的原则是：

- 如果计算是在描述构件自身形状，例如倾斜面、弧形把手、球面/环形截面，它应保留在对应 class 内。
- 如果计算是在弥补 primitive 没有 anchor 或 transform 能力，它应尽量下沉到 geometry runtime。
- 如果 legacy oracle 体现的是明显设计错误，rewritten 可以按更合理的几何语义修正，并通过 assembly notes 或 cleanup audit 留痕。

## 优化内容

### 统一 geometry runtime

新增并统一使用 `code/geometry/`：

- primitive 保留本地几何定义，并通过 transform 输出 world mesh。
- primitive 暴露 anchor，用于中心、顶面、底面、边界、轴线和角点类定位。
- transform 工具支持旋转、方向变换、绕点旋转、镜像、径向阵列和跨点对齐。
- category concept 不再需要在每个 class 里重复手写同类空间关系。

### 改写 category concept template

每个 `code/concepts/<Category>/concept_template.py` 都围绕 rewritten primitive 和 anchor 装配重写：

- 用语义化 class 名表达模板意图。
- 用构件组件列表构造 object mesh。
- 用 anchor 对齐表达堆叠、贴合、连接、横撑、把手、门板、开孔、凹陷面板等结构。
- 对少量复杂模式保留 category-local 几何推导，而不是把它们伪装成通用关系。

### 生成 rewritten 原生参数包

每个 category 都包含：

```text
parameters/
  index.json
  object_XXXX.json
parameters.pkl
```

这些参数包支持：

- 逐 object 审阅和可视化。
- 直接实例化 rewritten concept。
- 不依赖 legacy pkl。
- 不依赖 mapper。

### 精简发行工具

发行包只保留 runtime 消费所需工具：

- `visualize.py`: 从 rewritten 参数包加载 object，逐个打开 Open3D viewer，或用 `--save` 导出 OBJ/PNG/report。
- `native_params.py`: 读取 rewritten 参数包、加载 category module、实例化 concept、合并 mesh。
- `render_preview.py` 和 `report_schema.py`: 保存 preview 和 JSON report。

开发期工具、legacy 对比工具、mapper、audit/report 文件不包含在发行包中。

## 相比 legacy 的结果

rewritten 版本的主要收益是：

- 几何关系更可读：装配意图由 anchor 和 transform 表达，而不是散落在外部坐标公式里。
- 参数更可消费：object-level rewritten 参数包可直接驱动构造和可视化。
- runtime 边界更清楚：发行包不需要 legacy 源码、legacy pkl 或转换脚本。
- 扩展更稳定：新增 category 时优先复用 geometry runtime 和已形成的装配模式，而不是复制旧公式。
- 设计错误更容易识别：当 legacy 几何 oracle 与合理装配语义冲突时，rewritten 可以记录并修正，而不是盲目复刻。

总体上，rewritten 的目标不是让代码“更短”，而是让参数化几何从历史实现细节中解耦，变成可以审阅、复用、验证和发行的 runtime asset。
