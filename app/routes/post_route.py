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
    reference_images: Optional[List[str]] = []

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
        reference_images=request.reference_images
    )
    return CreatePostResponse(posts=posts)


@router.delete("/remove")
def remove_post(data: RemovePostModel):
    if not POSTS_CSV.exists():
        raise HTTPException(404, "Post database not found")

    rows = []
    deleted = False

    with open(POSTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    new_rows = [row for row in rows if row["post_id"] != data.post_id]

    if len(rows) == len(new_rows):
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

    client_profile = get_client_profile(data.client_id)
    client_email = client_profile.mail

    rows = []
    posts_to_send = []

    with open(POSTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    found_any = False

    for row in rows:
        if row["post_id"] in data.post_ids:
            row["finalized"] = "True"
            found_any = True

            posts_to_send.append({
                "caption": row["caption"],
                "hashtags": row.get("hashtags", ""),
                "image_url": row["image_url"]
            })

    if not found_any:
        raise HTTPException(404, "No matching post IDs found")

    # Write updated CSV
    with open(POSTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # Build email content
    email_body = "✅ Here are your finalized posts:\n\n"
    for i, post in enumerate(posts_to_send, 1):
        email_body += f"""
Post {i}:
Caption: {post['caption']}
Hashtags: {post['hashtags']}
Image: {post['image_url']}

------------------------
"""

    # Send Email (mock)
    send_email(
        to_email=client_email,
        subject="Your Finalized Social Media Posts ✅",
        body=email_body
    )

    return {"status": "Posts mailed successfully to client"}
