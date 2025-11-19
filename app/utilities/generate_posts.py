import csv
from pathlib import Path
from datetime import datetime
import os
import replicate
from app.utilities.format_prompt import build_full_prompt
from app.utilities.prompting_ai import generate_caption_and_image_prompt
from typing import List, Optional
from pydantic import BaseModel
import uuid


class PostResponse(BaseModel):
    post_id: str
    caption: str
    hashtags: Optional[List[str]] = []
    image_url: str


POSTS_PATH = Path("app/Data/posts")
POSTS_CSV = POSTS_PATH / "management.csv"



def generate_post_id(index: int) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"POST-{date_str}-{unique_suffix}"


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
    reference_image: list[str] = [],
    number_of_posts: int = 1,
    custom_prompt: Optional[str] = None
) -> list[PostResponse]:

    from fastapi import HTTPException

    print("\n=================== PROCESS STARTED ===================")

    # ----- Load Topic Titles -----
    print("\n>>> CHECKPOINT 1: Loading Topics...")

    topic_titles = []
    TOPICS_CSV = Path("app/Data/topics/management.csv")

    if not TOPICS_CSV.exists():
        raise HTTPException(status_code=500, detail=f"{TOPICS_CSV} does not exist")

    with open(TOPICS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        topic_map = {row["topic_id"]: row["title"] for row in reader}

        print("Loaded Topic Map:", topic_map)

        for tid in topic_ids:
            if tid in topic_map:
                topic_titles.append(topic_map[tid])
            else:
                raise HTTPException(status_code=400, detail=f"Topic ID {tid} not found")

    print("Resolved Topics:", topic_titles)



    # ----- Load Client Name -----
    print("\n>>> CHECKPOINT 2: Loading Client Name...")

    CLIENTS_CSV = Path("app/Data/clients/management.csv")
    client_name = None

    with open(CLIENTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["client_id"] == client_id:
                client_name = row["client_name"]
                break

    print("Client Name Found:", client_name)

    if not client_name:
        raise HTTPException(status_code=400, detail=f"Client ID {client_id} not found")



    # ----- Build Prompt -----
    print("\n>>> CHECKPOINT 3: Building AI Prompt...")

    prompt = build_full_prompt(
        client_id=client_id,
        visual_style=visual_style,
        topic_titles=topic_titles,
        number_of_posts=number_of_posts,
    )

    print("\n----- BUILT PROMPT SENT TO AI -----")
    print(prompt)



    # ----- Generate captions + hashtags + image_prompt -----
    print("\n>>> CHECKPOINT 4: AI Generating Captions + Image Prompts...")

    ai_outputs = generate_caption_and_image_prompt(prompt)

    print("\n----- RAW AI OUTPUT -----")
    print(ai_outputs)



    # ----- Initialize Replicate -----
    print("\n>>> CHECKPOINT 5: Initializing Replicate...")

    replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

    if not replicate_api_token:
        raise HTTPException(status_code=500, detail="REPLICATE_API_TOKEN not set")

    client = replicate.Client(api_token=replicate_api_token)
    print("Replicate Client Initialized.")



    # ----- Start Generating Posts -----
    print("\n>>> CHECKPOINT 6: Generating Posts...")

    final_posts = []

    for i, post_data in enumerate(ai_outputs, start=1):
        print(f"\n\n================ POST {i} STARTED ================")

        post_id = generate_post_id(i)
        print("Post ID:", post_id)

        image_prompt = post_data.get("image_prompt")
        print("AI Image Prompt:", image_prompt)

        if not image_prompt:
            raise HTTPException(status_code=500, detail=f"No image_prompt for post {i}")



        # ----- Image Generation -----
        print("\n>>> CHECKPOINT 7: Sending Prompt to Nano Banana...")

        # Start with either custom prompt or AI-generated image prompt
        final_prompt = custom_prompt or image_prompt

        # If reference images are provided, append instruction
        if reference_image:
            final_prompt += " Must follow the design of the reference image."

        print("\n----- FINAL PROMPT SENT TO REPLICATE -----")
        print(final_prompt)

        print("Reference Images Given:", reference_image)

        output = client.run(
            "google/nano-banana",
            input={
                "prompt": final_prompt,
                "image_input": reference_image,
                "aspect_ratio": "4:5",
                "output_format": "jpg"
            }
        )


        print("\n----- RAW REPLICATE OUTPUT -----")
        print(output)



        # ----- Extract Image URL -----
        if isinstance(output, list):
            image_url = output[0].url if hasattr(output[0], "url") else str(output[0])
        elif hasattr(output, "url"):
            image_url = output.url
        else:
            image_url = str(output)

        print("Final Image URL:", image_url)



        hashtags = post_data.get("hashtags") or []
        print("Hashtags:", hashtags)

        # ----- Build Response -----
        final_posts.append(
            PostResponse(
                post_id=post_id,
                caption=post_data.get("caption"),
                hashtags=hashtags,
                image_url=image_url
            )
        )


        # ----- Save Metadata -----
        print("\n>>> CHECKPOINT 8: Saving Metadata to CSV...")

        save_post_metadata({
            "post_id": post_id,
            "client_id": client_id,
            "category_id": category_id,
            "topics": ",".join(topic_ids),
            "caption": post_data.get("caption"),
            "hashtags": ",".join(hashtags),
            "image_url": image_url,
            "finalized": False,
            "created_at": datetime.now().isoformat()
        })

        print("Metadata Saved.")



    print("\n=================== PROCESS COMPLETED ===================\n")
    return final_posts
