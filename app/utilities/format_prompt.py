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

def build_full_prompt(client_id: str, visual_style: str, topic_titles: list[str], number_of_posts: int = 1) -> str:
    client: ClientCreate = get_client_profile(client_id)
    topics_formatted = ", ".join(topic_titles)

    prompt = f"""
You are an AI expert in creating **social media content for businesses**.

Generate **{number_of_posts} posts** for **{client.client_name}**, each containing:
1. **caption**
2. **hashtags**
3. **image_prompt** fully actionable for nano-banana image generation.

### CLIENT INFO
- Services: {client.services}
- Audience: {client.audience}
- Tagline: {client.tagline}
- Brand Colors: {', '.join(client.design_guide.brand_colors)}
- Design Style: {client.design_guide.design_style}
- Image Mood: {client.design_guide.image_mood}
- Dos & Don'ts: {client.design_guide.dos_donts}
- Contact Info: {client.contact_info}, {client.website}, {client.number}, {client.mail}

### TOPICS
{topics_formatted}

## visual style demanded
The visual style should be: {visual_style}

### CAPTION RULES
- Short, engaging, audience-targeted, aligned with client tone.
- Include one relevant CTA from: {', '.join(client.call_to_actions)}
- End with: {client.caption_ending}
- Do not include hashtags inside caption.

### IMAGE PROMPT RULES
it should strictly follow this framework:
"generate social media post for x business which provide y services to z audience. Add contact details (website,number,mail). The visual style should be this. The design should incorporate these brand colors"

### OUTPUT FORMAT
Respond **strictly in JSON array**:

[
{{
  "caption": "Brighten your child's smile today! Keep their teeth happy and healthy with our expert dental care.",
  "hashtags": ["#DentalCare", "#HealthySmiles", "#KidsDentist"],
  "image_prompt": "Generate a vibrant social media post for Zuhd Dental which provides teeth whitening services to audiences aged 25 seeking confident, healthy smiles. Add contact details (https://zuhddental.com, +1 (872) 258-9898, care@zuhddental.com).The design should incorporate brand colors #E9E6DF, #7DA89A, and #1C1C1C. Must follow the design of the reference image."
}}
]

Generate **{number_of_posts} unique posts**, visually consistent with the client’s identity and topics.
"""
    return prompt
