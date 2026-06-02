# Concept Template Runtime

这是 Concept Template V1 的 runtime-only 发行包。它只包含 concept template、原生参数包和 runtime 可视化工具；不包含 legacy 源码、legacy pkl 转换流程、rewrite 审计报告或开发期对比脚本。

相对 legacy 的优化目标和优化内容见 `REWRITE_OPTIMIZATION_SUMMARY.md`。

## 包结构

```text
code/
  geometry/          # runtime primitives、transform 和装配基础设施
  concepts/
    <Category>/
      __init__.py
      concept_template.py      # concept constructors
      parameters/    # object-level JSON 参数包
      parameters.pkl # 与 JSON 参数包等价的整包 pickle
      assembly_notes.md        # 如果该 category 有装配说明，则保留

tools/
  concept_agent/
    release/
      visualize.py             # runtime 可视化/导出入口
    lib/
      native_params.py         # 参数读取、实例化、mesh 合并
      report_schema.py         # JSON report 工具
      render_preview.py        # PNG preview 工具
```

## 安装依赖

建议在独立 Python 环境中安装：

```bash
pip install -r requirements.txt
```

`open3d` 只在打开 viewer 时需要；`pillow` 和 `trimesh` 只在 `--save` 生成 PNG/OBJ 时需要。

## 可视化

默认只打开 Open3D viewer，不保存文件。每次显示一个 object，关闭当前窗口后进入下一个 object。

```bash
python tools/concept_agent/release/visualize.py --category Bottle
```

只查看单个 object：

```bash
python tools/concept_agent/release/visualize.py \
  --params code/concepts/Bottle/parameters/object_0010.json
```

在无 GUI 环境做加载检查：

```bash
python tools/concept_agent/release/visualize.py \
  --params code/concepts/Bottle/parameters/object_0010.json \
  --no-viewer
```

保存 OBJ、PNG preview、preview sheet 和 render report：

```bash
python tools/concept_agent/release/visualize.py --category Bottle --save
```

保存目录：

```text
reports/<Category>_visualization/
```

## 参数包格式

- `parameters/` 是 object-level JSON 目录包。
- `index.json` 保存 category 摘要和 object 索引。
- 每个 `object_XXXX.json` 只保存一个完整 object，适合单独审阅、diff 和可视化。
- `parameters.pkl` 与 JSON 目录包内容等价，适合一次性加载整包。
- 每个 concept 的 `template` 是 concept class 名，`parameters` 是该 class constructor 的原生参数。

## Python 使用示例

```python
from tools.concept_agent.lib.native_params import (
    combine_instances,
    instantiate_object_concepts,
    load_category_module,
    load_parameter_package,
)

package = load_parameter_package(
    "code/concepts/Bottle/parameters/object_0010.json"
)
category_module = load_category_module(package["category"])
instances, events = instantiate_object_concepts(category_module, package["objects"][0])
if events:
    raise RuntimeError(events)

mesh = combine_instances(instances)
print(mesh.vertices.shape, mesh.faces.shape)
```

## 边界

- 本包不依赖 `code/code_original/`。
- 本包不提供 legacy-to-native 参数转换；发行包内的参数已经是 concept constructor 原生参数。
- 不应手工编辑 `parameters/` 或 `parameters.pkl`，除非重新生成并验证整套参数资产。
