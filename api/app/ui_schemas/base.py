from typing import Any

from pydantic import BaseModel

from app.models.ui_schemas import FieldHint, Submit, UiHints, UiSpec

REGISTRY: dict[str, UiSpec] = {}


def simplify(model: type[BaseModel]) -> dict[str, Any]:
    """Flatten Pydantic's JSON Schema for the renderer: Optional[X] (anyOf X|null)
    becomes X, and null defaults are dropped. Required-ness stays in `required`."""
    raw = model.model_json_schema()
    props: dict[str, Any] = {}
    for name, prop in raw.get("properties", {}).items():
        prop = dict(prop)
        if "anyOf" in prop:
            branches = [b for b in prop.pop("anyOf") if b.get("type") != "null"]
            if branches:
                prop = {**branches[0], **prop}
        if prop.get("default", 0) is None:
            prop.pop("default")
        props[name] = prop
    return {"type": "object", "title": raw.get("title"), "properties": props,
            "required": raw.get("required", [])}


def spec(name: str, title: str, model: type[BaseModel], method: str, path: str,
         fields: dict[str, dict] | None = None, order: list[str] | None = None,
         submit_label: str = "Save", success_message: str = "Saved") -> UiSpec:
    schema = simplify(model)
    ui = UiHints(order=order or list(schema["properties"]),
                 fields={k: FieldHint(**v) for k, v in (fields or {}).items()})
    REGISTRY[name] = UiSpec(name=name, title=title, submit=Submit(method=method, path=path),
                            schema=schema, ui=ui, submit_label=submit_label,
                            success_message=success_message)
    return REGISTRY[name]
