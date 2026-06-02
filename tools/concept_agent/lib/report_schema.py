import json
import traceback as traceback_module
from pathlib import Path


def make_event(
    stage,
    status="failed",
    class_name=None,
    case_index=None,
    error_type=None,
    message=None,
    traceback=None,
    suggestion=None,
):
    event = {
        "stage": stage,
        "status": status,
    }
    if class_name is not None:
        event["class_name"] = class_name
    if case_index is not None:
        event["case_index"] = case_index
    if error_type is not None:
        event["error_type"] = error_type
    if message is not None:
        event["message"] = str(message)
    if traceback is not None:
        event["traceback"] = str(traceback)
    if suggestion is not None:
        event["suggestion"] = str(suggestion)
    return event


def event_from_exception(stage, exc, class_name=None, case_index=None, suggestion=None):
    return make_event(
        stage=stage,
        class_name=class_name,
        case_index=case_index,
        error_type=type(exc).__name__,
        message=str(exc),
        traceback=traceback_module.format_exc(),
        suggestion=suggestion,
    )


def to_jsonable(value):
    try:
        import numpy as np
    except Exception:
        np = None

    if np is not None:
        if isinstance(value, np.ndarray):
            return [to_jsonable(item) for item in value.tolist()]
        if isinstance(value, np.generic):
            return value.item()

    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(to_jsonable(data), indent=2, ensure_ascii=False, sort_keys=False),
        encoding="utf-8",
    )
