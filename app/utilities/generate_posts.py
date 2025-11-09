import csv
from pathlib import Path
from datetime import datetime
import os
import replicate
from app.utilities.format_prompt import build_full_prompt
from app.utilities.prompting_ai import generate_caption_and_image_prompt
from typing import List, Optional
from pydantic import BaseModel

class PostResponse(BaseModel):
    post_id: str
    caption: str
    hashtags: Optional[List[str]] = []
    image_url: str


POSTS_PATH = Path("app/Data/posts")
POSTS_CSV = POSTS_PATH / "management.csv"

def generate_post_id(index: int) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    return f"POST-{date_str}-{str(index).zfill(2)}"

def save_post_metadata(post_dict: dict):
    POSTS_PATH.mkdir(parents=True, exist_ok=True)
    file_exists = POSTS_CSV.exists()
    with open(POSTS_CSV, "a", newline="", encoding="utf-8") as f:
        fieldnames = [
            "post_id", "client_id", "category_id", "topics", 
            "caption", "hashtags", "image_url", "finalized", "created_at"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(post_dict)

def generate_posts(
    client_id: str,
    category_id: str,
    topic_ids: list[str],
    visual_style: str,
    number_of_posts: int = 1,
    reference_images: list[str] = []
) -> list[PostResponse]:

    from fastapi import HTTPException

    # ----- Extract Topic Titles -----
    TOPICS_CSV = Path("app/Data/topics/management.csv")
    topic_titles = []
    if not TOPICS_CSV.exists():
        raise HTTPException(status_code=500, detail=f"{TOPICS_CSV} does not exist")

    with open(TOPICS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        topic_map = {row["topic_id"]: row["title"] for row in reader}
        for tid in topic_ids:
            if tid in topic_map:
                topic_titles.append(topic_map[tid])
            else:
                raise HTTPException(status_code=400, detail=f"Topic ID {tid} not found")

    # ----- Build AI prompt -----
    prompt = build_full_prompt(
        client_id=client_id,
        visual_style=visual_style,
        topic_titles=topic_titles,
        number_of_posts=number_of_posts
    )

    # ----- Get AI outputs -----
    ai_outputs = generate_caption_and_image_prompt(prompt)

    # ----- Initialize Replicate -----
    replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
    if not replicate_api_token:
        raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN not set in environment")
    client = replicate.Client(api_token=replicate_api_token)

    final_posts = []

    for i, post_data in enumerate(ai_outputs, start=1):
        post_id = generate_post_id(i)
        image_prompt = post_data.get("image_prompt")
        if not image_prompt:
            raise HTTPException(status_code=500, detail=f"No image_prompt for post {i}")

        output = client.run(
            "google/nano-banana",
            input={
                "prompt": image_prompt,
                "image_input": reference_images,
                "aspect_ratio": "9:16",
                "output_format": "jpg"
            }
        )

        if isinstance(output, list):
            image_url = output[0].url if hasattr(output[0], "url") else str(output[0])
        elif hasattr(output, "url"):
            image_url = output.url
        else:
            image_url = str(output)

        hashtags = post_data.get("hashtags") or []

        # ----- Build API Response Object -----
        post_response = PostResponse(
            post_id=post_id,
            caption=post_data.get("caption"),
            hashtags=hashtags,
            image_url=image_url
        )
        final_posts.append(post_response)

        # ----- Save to CSV -----
        save_post_metadata({
            "post_id": post_id,
            "client_id": client_id,
            "category_id": category_id,
            "topics": ",".join(topic_ids),
            "caption": post_data.get("caption"),
            "hashtags": ",".join(hashtags),  # ✅ saved properly now
            "image_url": image_url,
            "finalized": False,
            "created_at": datetime.now().isoformat()
        })

    return final_posts
