import csv
import json
from pathlib import Path
from pydantic import BaseModel
from typing import List

# -------------------- Pydantic Models --------------------

class DesignGuide(BaseModel):
    brand_colors: List[str]
    typography: str
    design_style: str
    image_mood: str
    dos_donts: str
    reference_links: List[str]
    asset_notes: str
    format_preferences: List[str]
    design_checkpoints: str

class ClientCreate(BaseModel):
    client_name: str
    focus: str
    services: str
    business_description: str
    audience: str
    writing_instructions: str
    tagline: str
    call_to_actions: List[str]
    caption_ending: str
    writing_samples: List[str]
    contact_info: str
    website: str
    number: str
    mail: str
    design_guide: DesignGuide
    logo_urls: List[str]
    client_id: str


# -------------------- Paths --------------------

BASE_PATH = Path("app/Data/clients")

def get_client_name_from_csv(client_id: str) -> str:
    csv_path = BASE_PATH / "management.csv"
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["client_id"] == client_id:
                return row["client_name"]
    raise ValueError(f"Client ID {client_id} not found in management.csv")

def get_client_profile(client_id: str) -> ClientCreate:
    client_name = get_client_name_from_csv(client_id)
    json_path = BASE_PATH / client_name / "profile.json"
    if not json_path.exists():
        raise FileNotFoundError(f"profile.json not found for client: {client_name}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ClientCreate(**data)


# -------------------- Prompt Builder --------------------

# -------------------- Prompt Builder --------------------

def build_full_prompt(client_id: str, visual_style: str, topic_titles: list[str], number_of_posts: int = 1) -> str:
    """
    Build a full prompt for the AI to generate multiple posts.

    Args:
        client_id: ID of the client
        visual_style: Design style (e.g., Poster / Ad Style)
        topic_titles: List of topic titles to include in the posts
        number_of_posts: Number of posts to generate

    Returns:
        str: Prompt string
    """
    client: ClientCreate = get_client_profile(client_id)
    
    topics_formatted = ", ".join(topic_titles)
    
    prompt = f"""
You are a professional social media content and design assistant.

Your job is to create **{number_of_posts} social media posts** (captions and layout plans) based on the client details below.

---

### CLIENT INFORMATION
- Name: {client.client_name}
- Focus / Industry: {client.focus}
- Services: {client.services}
- Description: {client.business_description}
- Audience: {client.audience}
- Writing Style: {client.writing_instructions}
- Tagline: {client.tagline}
- Call To Actions: {', '.join(client.call_to_actions)}
- Caption Ending: {client.caption_ending}
- Writing Samples: {', '.join(client.writing_samples)}
- Contact Info: {client.contact_info}
- Website: {client.website}
- Number: {client.number}
- Mail: {client.mail}
- Logo URLs: {', '.join(client.logo_urls)}

---

### DESIGN INFORMATION
- Brand Colors: {', '.join(client.design_guide.brand_colors)}
- Typography: {client.design_guide.typography}
- Design Style: {client.design_guide.design_style}
- Image Mood: {client.design_guide.image_mood}
- Dos & Don'ts: {client.design_guide.dos_donts}
- Reference Links: {', '.join(client.design_guide.reference_links)}
- Asset Notes: {client.design_guide.asset_notes}
- Format Preferences: {', '.join(client.design_guide.format_preferences)}
- Design Checkpoints: {client.design_guide.design_checkpoints}
- Visual Style: {visual_style}
- Topics: [{topics_formatted}]

---

### IMPORTANT INSTRUCTIONS
- Respond **STRICTLY in JSON format**.
- Return an **array of exactly {number_of_posts} objects**.
- Do NOT include any extra text, explanation, or notes outside the JSON array.
- Each object MUST strictly follow the template below:

[
{{
  "caption": "Short caption suitable for Instagram",
  "hashtags": ["#brand", "#service", "#city"],
  "image_prompt": "Image generation prompt for design model",
  "layout_notes": "How the text and visuals should be placed"
}}
]

- Each object in the array should be **unique** and suitable for posting independently.
"""
    return prompt
