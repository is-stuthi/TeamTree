"""Write api/openapi.json and api/ui_schemas_out/<name>.json (inputs for web `npm run gen`)."""
import json
import shutil
import sys
from pathlib import Path

API = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API))
from app.main import app  # noqa: E402
from app.ui_schemas import REGISTRY  # noqa: E402

(API / "openapi.json").write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")

out = API / "ui_schemas_out"
shutil.rmtree(out, ignore_errors=True)
out.mkdir()
for name, spec in REGISTRY.items():
    (out / f"{name}.json").write_text(spec.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
print(f"wrote openapi.json and {len(REGISTRY)} ui specs")
