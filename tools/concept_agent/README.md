# Runtime Tools

这个目录只保留 rewritten-only runtime 工具。

## visualize.py

从 rewritten 原生参数包实例化 concept，合并 object mesh，并可选择打开 Open3D viewer 或保存 OBJ/PNG。

```bash
python tools/concept_agent/release/visualize.py --category Bottle
python tools/concept_agent/release/visualize.py \
  --params code/code_rewritten/Bottle/rewritten_parameters/object_0010.json
python tools/concept_agent/release/visualize.py --category Bottle --save
```

默认行为：

- 成功时不打印完整 JSON report。
- 不传 `--save` 时不落盘。
- 不传 `--no-viewer` 时逐个打开 Open3D viewer。

常用参数：

- `--category <Category>`: 从 `code/code_rewritten/<Category>/rewritten_parameters/` 加载整包。
- `--params <path>`: 从目录包、`index.json`、单个 `object_XXXX.json` 或 `rewritten_parameters.pkl` 加载参数。
- `--save`: 保存 OBJ、PNG preview、preview sheet 和 render report。
- `--no-viewer`: 不打开 Open3D viewer，适合 CI 或无 GUI 环境。
- `--verbose`: 输出完整 JSON report。

## lib/

- `native_params.py`: rewritten 参数包读取、category module 加载、concept 实例化和 mesh 合并。
- `report_schema.py`: JSON report 序列化工具。
- `render_preview.py`: 保存 PNG preview 和 preview sheet。
