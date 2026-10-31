"""Contract between the API and the static SchemaForm renderer (web)."""
from typing import Any, Literal

from pydantic import BaseModel, Field

Widget = Literal["text", "textarea", "number", "select", "remote-select", "date",
                 "checkbox", "tags", "password", "email"]


class FieldHint(BaseModel):
    widget: Widget | None = None
    label: str | None = None
    help: str | None = None
    placeholder: str | None = None
    rows: int | None = None
    source: str | None = Field(default=None, description="GET path for remote-select options")
    label_key: str | None = None
    value_key: str | None = None
    hidden: bool = False


class Submit(BaseModel):
    # GET = search form: the renderer navigates with the values as query params
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str = Field(description="API path; {field} placeholders are filled from values/params")


class UiHints(BaseModel):
    order: list[str]
    fields: dict[str, FieldHint] = {}


class UiSpec(BaseModel):
    name: str
    title: str
    submit: Submit
    submit_label: str = "Save"
    success_message: str = "Saved"
    schema_: dict[str, Any] = Field(alias="schema", serialization_alias="schema")
    ui: UiHints

    model_config = {"populate_by_name": True}
