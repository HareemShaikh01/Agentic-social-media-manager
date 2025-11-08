from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv, dotenv_values, set_key

router = APIRouter()

load_dotenv()
ENV_PATH = ".env"

class EnvKeys(BaseModel):
    openai_api_key: str
    imgbb_api_key: str
    mail_api_key: str  # (Brevo or any mail service)

@router.post("/set")
def set_env_keys(keys: EnvKeys):
    try:
        set_key(ENV_PATH, "OPENAI_API_KEY", keys.openai_api_key)
        set_key(ENV_PATH, "IMGBB_API_KEY", keys.imgbb_api_key)
        set_key(ENV_PATH, "MAIL_API_KEY", keys.mail_api_key)

        return {"status": "success", "message": "API keys saved securely ✅"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def mask_key(key: str):
    if not key or len(key) < 6:
        return "Not Set"
    return key[:3] + "*****" + key[-3:]


@router.get("/get")
def get_env_keys():
    env_vars = dotenv_values(ENV_PATH)

    return {
        "openai_api_key": mask_key(env_vars.get("OPENAI_API_KEY")),
        "imgbb_api_key": mask_key(env_vars.get("IMGBB_API_KEY")),
        "mail_api_key": mask_key(env_vars.get("MAIL_API_KEY")),
    }
