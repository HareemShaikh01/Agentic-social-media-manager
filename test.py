# test_flow_multiple_posts.py

import os
from app.utilities.format_prompt import build_full_prompt
from app.utilities.prompting_ai import generate_caption_and_image_prompt
import replicate

# ------------------ Hardcoded Input ------------------
input_data = {
    "client_id": "CLT-20251109-153407",
    "category_id": "CAT-20251104-01",
    "topics": ["jshddhfksjhjksh"],
    "number_of_posts": 3,
    "custom_prompt": "",
    "visual_style": "Poster / Ad Style",
    "reference_images": []
}

# ------------------ Step 1: Get topic title ------------------
# For this test, we'll mock the topic title
topic_title = "Smile Transformation Benefits"

# ------------------ Step 2: Build Prompt ------------------
prompt = build_full_prompt(
    client_id=input_data["client_id"],
    visual_style=input_data["visual_style"],
    topic_title=topic_title,
    number_of_posts=input_data["number_of_posts"]
)
print("=== Generated Prompt ===")
print(prompt)

# ------------------ Step 3: Get AI caption & image prompts ------------------
ai_outputs = generate_caption_and_image_prompt(prompt)
print("\n=== AI Outputs ===")
for i, post_data in enumerate(ai_outputs, start=1):
    print(f"\n--- Post {i} ---")
    print(post_data)

# ------------------ Step 4: Generate images via Nano Banana ------------------
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
if not replicate_api_token:
    raise ValueError("REPLICATE_API_TOKEN is not set in environment variables")

client = replicate.Client(api_token=replicate_api_token)

reference_images = input_data.get("reference_images", [])

final_posts = []

for i, post_data in enumerate(ai_outputs, start=1):
    image_prompt = post_data.get("image_prompt")
    if not image_prompt:
        raise ValueError(f"No image_prompt found for post {i}")

    output = client.run(
        "google/nano-banana",
        input={
            "prompt": image_prompt,
            "image_input": reference_images,
            "aspect_ratio": "9:16",
            "output_format": "jpg"
        }
    )

    # Extract image URL
    if isinstance(output, list):
        image_url = output[0].url if hasattr(output[0], "url") else str(output[0])
    elif hasattr(output, "url"):
        image_url = output.url
    else:
        image_url = str(output)

    final_posts.append({
        "post_id": f"POST-{i:03d}",
        "caption": post_data.get("caption"),
        "hashtags": post_data.get("hashtags"),
        "image_url": image_url
    })

# ------------------ Step 5: Print final result ------------------
print("\n=== Final Posts ===")
for post in final_posts:
    print(post)
