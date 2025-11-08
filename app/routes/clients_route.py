from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
import json, csv, shutil

router = APIRouter()


# ------------------ SCHEMAS ------------------

class ClientCreate(BaseModel):
    client_name: str
    focus: str
    services: str
    business_description: str
    audience: str
    writing_instructions: str
    tagline: str
    call_to_actions: list[str]
    caption_ending: str
    writing_samples: list[str]
    contact_info: str
    website: str
    number: str
    mail: str
    design_guide: dict
    logo_urls: list[str]


class UpdateClientData(BaseModel):
    client_id: str
    data: dict = Field(...)


class RemoveClientField(BaseModel):
    client_id: str
    field_name: str


# ------------------ HELPERS ------------------

CLIENT_ROOT = Path("app/Data/clients")
CLIENT_REG = CLIENT_ROOT / "management.csv"


def generate_client_id() -> str:
    return f"CLT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"


def ensure_csv_header():
    CLIENT_ROOT.mkdir(parents=True, exist_ok=True)
    if not CLIENT_REG.exists():
        with CLIENT_REG.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["client_id", "client_name", "tagline", "focus", "logo_urls"])


def client_name_exists(name: str) -> bool:
    if not CLIENT_REG.exists():
        return False
    with CLIENT_REG.open() as f:
        rows = csv.reader(f)
        next(rows, None)  # skip header
        return any(row and row[1].strip().lower() == name.lower() for row in rows)


def find_client_folder(client_id: str) -> Path | None:
    if not CLIENT_ROOT.exists():
        return None
    for folder in CLIENT_ROOT.iterdir():
        profile = folder / "profile.json"
        if profile.exists():
            if json.loads(profile.read_text()).get("client_id") == client_id:
                return folder
    return None


# ------------------ ENDPOINTS ------------------

@router.post("/create")
def create_client(payload: ClientCreate):
    ensure_csv_header()

    # ✅ Prevent duplicate client names
    if client_name_exists(payload.client_name):
        raise HTTPException(400, f"Client '{payload.client_name}' already exists.")

    client_id = generate_client_id()
    folder = CLIENT_ROOT / payload.client_name
    assets = folder / "assets"

    (assets / "logos").mkdir(parents=True, exist_ok=True)
    (assets / "reference_images").mkdir(parents=True, exist_ok=True)

    profile = payload.dict()
    profile["client_id"] = client_id
    (folder / "profile.json").write_text(json.dumps(profile, indent=4))

    with CLIENT_REG.open("a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([client_id, payload.client_name, payload.tagline, payload.focus, payload.logo_urls])

    return {"client_id": client_id, "status": "Client created successfully"}


@router.delete("/remove")
def remove_client(client_id: str = Query(...), delete_all_data: bool = Query(False)):
    if not CLIENT_REG.exists():
        raise HTTPException(404, "Client registry not found")

    rows = list(csv.reader(CLIENT_REG.open()))
    header, *data = rows
    updated = [r for r in data if r[0] != client_id]

    if len(data) == len(updated):
        raise HTTPException(404, "Client ID not found")

    with CLIENT_REG.open("w", newline="") as f:
        csv.writer(f).writerows([header] + updated)

    if delete_all_data:
        folder = find_client_folder(client_id)
        if folder:
            shutil.rmtree(folder, ignore_errors=True)

    return {"status": "Client and all data removed successfully"}


@router.post("/add-client-data")
def add_client_data(payload: UpdateClientData):
    folder = find_client_folder(payload.client_id)
    if not folder:
        raise HTTPException(404, "Client not found")

    profile_path = folder / "profile.json"
    profile = json.loads(profile_path.read_text())
    profile.update(payload.data)
    profile_path.write_text(json.dumps(profile, indent=4))

    return {"status": "Data added successfully"}


@router.delete("/remove-client-data")
def remove_client_data(payload: RemoveClientField):
    folder = find_client_folder(payload.client_id)
    if not folder:
        raise HTTPException(404, "Client not found")

    profile_path = folder / "profile.json"
    profile = json.loads(profile_path.read_text())

    if payload.field_name not in profile:
        raise HTTPException(400, "Field does not exist")

    del profile[payload.field_name]
    profile_path.write_text(json.dumps(profile, indent=4))
    return {"status": "Field removed successfully"}
