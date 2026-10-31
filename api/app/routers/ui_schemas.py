"""Serves form specs for the web SchemaForm (public: specs contain no data)."""
from fastapi import APIRouter

from app.errors import ApiError
from app.models.ui_schemas import UiSpec
from app.ui_schemas import REGISTRY

router = APIRouter(prefix="/ui-schemas", tags=["ui_schemas"])


@router.get("", response_model=list[str])
async def list_specs():
    return sorted(REGISTRY)


@router.get("/{name}", response_model=UiSpec, response_model_by_alias=True)
async def get_spec(name: str):
    if name not in REGISTRY:
        raise ApiError(404, "UNKNOWN_FORM")
    return REGISTRY[name]
