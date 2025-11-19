# app/routers/posts.py
from fastapi import APIRouter,HTTPException
from app.utilities.generate_posts import generate_posts
from typing import List, Optional
from pydantic import BaseModel
from app.utilities.generate_posts import PostResponse
from pathlib import Path
from app.utilities.format_prompt import get_client_profile
import csv

router = APIRouter()

POSTS_CSV = Path("app/Data/posts/management.csv")

# ---------- MODELS ----------

class RemovePostModel(BaseModel):
    post_id: str


class FinalizePostModel(BaseModel):
    client_id: str
    post_ids: List[str]


class CreatePostRequest(BaseModel):
    client_id: str
    category_id: Optional[str] = None
    topics: List[str]
    number_of_posts: int = 1
    custom_prompt: Optional[str] = ""
    visual_style: str
    reference_image: Optional[List[str]] = []

class CreatePostResponse(BaseModel):
    posts: List[PostResponse]

def send_email(to_email: str, subject: str, body: str):
    print("\n📧 Sending Email To:", to_email)
    print("Subject:", subject)
    print("Body:\n", body)
    print("✅ Email sent simulation complete\n")


@router.post("/create", response_model=CreatePostResponse)
def create_post(request: CreatePostRequest):
    posts = generate_posts(
        client_id=request.client_id,
        category_id=request.category_id,
        topic_ids=request.topics,
        visual_style=request.visual_style,
        number_of_posts=request.number_of_posts,
        reference_image=request.reference_image,
        custom_prompt=request.custom_prompt
    )
    return CreatePostResponse(posts=posts)

@router.delete("/remove")
def remove_post(data: RemovePostModel):
    if not POSTS_CSV.exists():
        raise HTTPException(404, "Post database not found")

    with open(POSTS_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    new_rows = [row for row in rows if row["post_id"] != data.post_id]

    if len(new_rows) == len(rows):
        raise HTTPException(404, "Post ID not found")

    with open(POSTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(new_rows)

    return {"status": "Post deleted successfully"}


@router.post("/finalize-post")
def finalize_post(data: FinalizePostModel):
    if not POSTS_CSV.exists():
        raise HTTPException(404, "Post database not found")

    with open(POSTS_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    updated_rows = []
    posts_to_send = []

    for row in rows:
        if row["post_id"] in data.post_ids:
            row["finalized"] = "True"
            posts_to_send.append({
                "caption": row["caption"],
                "hashtags": row.get("hashtags", ""),
                "image_url": row["image_url"]
            })
        updated_rows.append(row)

    with open(POSTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(updated_rows)

    if not posts_to_send:
        raise HTTPException(404, "No matching post IDs found")


@router.get("/get-all-posts")
def get_all_posts():
    if not POSTS_CSV.exists():
        raise HTTPException(404, "No posts found")

    posts = []
    with open(POSTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # return all post fields, including finalized status if present
            posts.append({
                "post_id": row.get("post_id"),
                "client_id": row.get("client_id"),
                "category_id": row.get("category_id"),
                "topics": row.get("topics").split(",") if row.get("topics") else [],
                "caption": row.get("caption"),
                "hashtags": row.get("hashtags", ""),
                "image_url": row.get("image_url"),
                "visual_style": row.get("visual_style"),
                "finalized": row.get("finalized", "False")
            })

    if not posts:
        raise HTTPException(404, "No posts found")

    return {"posts": posts}

