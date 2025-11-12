from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import csv

router = APIRouter()

# ------------------ SCHEMAS ------------------

class CategoryCreate(BaseModel):
    category_name: str

class TopicCreate(BaseModel):
    category_id: str
    title: str
    description: str

# ------------------ PATHS ------------------

CATEGORY_ROOT = Path("app/Data/categories")
CATEGORY_CSV = CATEGORY_ROOT / "management.csv"

TOPIC_ROOT = Path("app/Data/topics")
TOPIC_CSV = TOPIC_ROOT / "management.csv"

# ------------------ HELPERS ------------------

def ensure_csv(path: Path, header: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

def generate_category_id() -> str:
    return f"CAT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

def generate_topic_id() -> str:
    return f"TOP-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

def category_exists(category_id: str) -> bool:
    ensure_csv(CATEGORY_CSV, ["category_id", "category_name"])
    with CATEGORY_CSV.open() as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row and row[0].strip() == category_id.strip():
                return True
    return False

def category_name_exists(category_name: str) -> bool:
    ensure_csv(CATEGORY_CSV, ["category_id", "category_name"])
    with CATEGORY_CSV.open() as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row and row[1].strip().lower() == category_name.strip().lower():
                return True
    return False

# ------------------ ENDPOINTS ------------------

@router.post("/create-category")
def create_category(payload: CategoryCreate):
    if category_name_exists(payload.category_name):
        raise HTTPException(400, f"Category '{payload.category_name}' already exists.")

    category_id = generate_category_id()
    ensure_csv(CATEGORY_CSV, ["category_id", "category_name"])

    with CATEGORY_CSV.open("a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([category_id, payload.category_name])

    return {"category_id": category_id, "status": "Category created successfully"}


@router.post("/create-topic")
def create_topic(payload: TopicCreate):
    if not category_exists(payload.category_id):
        raise HTTPException(404, "Category not found")

    ensure_csv(TOPIC_CSV, ["topic_id", "category_id", "title", "description"])
    topic_id = generate_topic_id()

    with TOPIC_CSV.open("a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([topic_id, payload.category_id.strip(), payload.title, payload.description])

    return {"topic_id": topic_id, "status": "Topic created successfully"}


@router.get("/search-topics")
def search_topics(category_id: str = Query(...)):
    ensure_csv(TOPIC_CSV, ["topic_id", "category_id", "title", "description"])
    topics = []

    with TOPIC_CSV.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["category_id"].strip() == category_id.strip():
                topics.append({
                    "topic_id": row["topic_id"],
                    "title": row["title"],
                    "description": row["description"]
                })

    return {"topics": topics}

@router.get("/get-all-categories")
def get_all_categories():
    ensure_csv(CATEGORY_CSV, ["category_id", "category_name"])
    categories = []

    with CATEGORY_CSV.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["category_id"] and row["category_name"]:
                categories.append({
                    "category_id": row["category_id"].strip(),
                    "category_name": row["category_name"].strip()
                })

    return {"categories": categories}



@router.get("/get-all-topics")
def get_all_topics():
    ensure_csv(TOPIC_CSV, ["topic_id", "category_id", "title", "description"])
    topics = []

    with TOPIC_CSV.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            topics.append(row)

    return {"topics": topics}


@router.delete("/remove-topic")
def remove_topic(topic_id: str = Query(...)):
    ensure_csv(TOPIC_CSV, ["topic_id", "category_id", "title", "description"])

    rows = list(csv.reader(TOPIC_CSV.open()))
    header, *data = rows
    updated = [r for r in data if r[0].strip() != topic_id.strip()]

    if len(data) == len(updated):
        raise HTTPException(404, "Topic ID not found")

    with TOPIC_CSV.open("w", newline="") as f:
        csv.writer(f).writerows([header] + updated)

    return {"status": "Topic removed successfully"}


@router.delete("/remove-category")
def remove_category(category_id: str = Query(...)):
    ensure_csv(CATEGORY_CSV, ["category_id", "category_name"])
    ensure_csv(TOPIC_CSV, ["topic_id", "category_id", "title", "description"])

    rows = list(csv.reader(CATEGORY_CSV.open()))
    header, *data = rows
    updated = [r for r in data if r[0].strip() != category_id.strip()]

    if len(data) == len(updated):
        raise HTTPException(404, "Category ID not found")

    with CATEGORY_CSV.open("w", newline="") as f:
        csv.writer(f).writerows([header] + updated)

    # Remove all related topics
    topic_rows = list(csv.reader(TOPIC_CSV.open()))
    topic_header, *topic_data = topic_rows
    topic_updated = [r for r in topic_data if r[1].strip() != category_id.strip()]

    with TOPIC_CSV.open("w", newline="") as f:
        csv.writer(f).writerows([topic_header] + topic_updated)

    return {"status": "Category and all topics removed successfully"}
