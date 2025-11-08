from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException
from pathlib import Path
from datetime import datetime
import csv, os, requests
from dotenv import load_dotenv

load_dotenv()
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

router = APIRouter()

# ------------------ PATHS ------------------
IMAGE_ROOT = Path("app/Data/images")
IMAGE_CSV = IMAGE_ROOT / "management.csv"
CLIENT_CSV = Path("app/Data/clients/management.csv")
IMAGE_ROOT.mkdir(parents=True, exist_ok=True)

# ------------------ HELPERS ------------------
def ensure_csv(path: Path, header: list[str]):
    if not path.exists():
        with path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

def generate_image_id() -> str:
    return f"IMG-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

def read_csv(path: Path):
    ensure_csv(path, ["image_id", "image_name", "url", "client_id"])
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_csv(path: Path, rows: list[dict]):
    if not rows:
        path.unlink(missing_ok=True)
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def client_exists(client_id: str) -> bool:
    if not CLIENT_CSV.exists():
        return False
    with CLIENT_CSV.open("r", newline="") as f:
        reader = csv.DictReader(f)
        return any(row["client_id"] == client_id for row in reader)

# ------------------ ENDPOINTS ------------------

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    image_name: str = Form(...),
    client_id: str = Form(...)
):
    """
    Uploads image to ImgBB, saves record in CSV, returns URL.
    """
    if not IMGBB_API_KEY:
        raise HTTPException(500, "ImgBB API key not found")

    if not client_exists(client_id):
        raise HTTPException(400, f"Client ID {client_id} does not exist")

    # Upload to ImgBB
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        params={"key": IMGBB_API_KEY, "name": image_name},
        files={"image": file.file}
    )

    if response.status_code != 200:
        raise HTTPException(500, f"ImgBB upload failed: {response.text}")

    data = response.json()
    if not data.get("success"):
        raise HTTPException(500, f"ImgBB upload failed: {data}")

    image_url = data["data"]["url"]
    image_id = generate_image_id()

    # Save record in CSV
    ensure_csv(IMAGE_CSV, ["image_id", "image_name", "url", "client_id"])
    with IMAGE_CSV.open("a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([image_id, image_name, image_url, client_id])

    return {
        "image_id": image_id,
        "url": image_url,
        "status": "Image uploaded and saved successfully"
    }


@router.get("/search")
def search_image(image_id: str = Query(None), image_name: str = Query(None)):
    """
    Search images by image_id or image_name
    """
    if not image_id and not image_name:
        raise HTTPException(400, "Provide at least image_id or image_name for search")

    records = read_csv(IMAGE_CSV)
    results = []

    for r in records:
        if image_id and r["image_id"] == image_id:
            results.append({"image_id": r["image_id"], "url": r["url"]})
        elif image_name and r["image_name"] == image_name:
            results.append({"image_id": r["image_id"], "url": r["url"]})

    return {"results": results}


@router.delete("/remove")
def remove_image(image_id: str = Query(...)):
    """
    Delete image record by image_id from CSV (ImgBB image remains)
    """
    records = read_csv(IMAGE_CSV)
    record = next((r for r in records if r["image_id"] == image_id), None)

    if not record:
        raise HTTPException(404, "Image ID not found")

    # Remove from CSV
    updated = [r for r in records if r["image_id"] != image_id]
    write_csv(IMAGE_CSV, updated)

    return {"status": "Image deleted successfully"}
