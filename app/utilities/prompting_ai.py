import openai
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openaiapikey = os.getenv("OPENAI_API_KEY")
if not openaiapikey:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

def generate_caption_and_image_prompt(prompt: str) -> list[dict]:
    """
    Sends a prompt to OpenAI and expects an array of objects in JSON format.
    Each object should contain:
      - caption
      - hashtags
      - image_prompt

    Returns a list of dicts.
    """
    client = OpenAI(api_key=openaiapikey)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional social media content and design assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600  # increased to allow multiple posts
    )

    output_text = response.choices[0].message.content.strip()

    try:
        data = json.loads(output_text)

        # Validate the structure: must be a list of dicts
        if not isinstance(data, list):
            raise ValueError("AI output is not a list. Expected an array of objects.")
        if not all(isinstance(item, dict) for item in data):
            raise ValueError("Some items in the AI output array are not objects.")
        
        # Optional: check required keys in each dict
        required_keys = {"caption", "hashtags", "image_prompt"}
        for i, item in enumerate(data):
            missing_keys = required_keys - item.keys()
            if missing_keys:
                raise ValueError(f"Item {i} is missing keys: {missing_keys}")

    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {e}\nRaw output: {output_text}")

    return data
