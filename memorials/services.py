import requests
import json
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class GroqService:
    """Service for generating tribute text using Groq Cloud"""
    
    @staticmethod
    def generate_tribute(name, relationship, memories):
        """Generate a concise, faithful tribute"""
        try:
            if not getattr(settings, 'GROQ_API_KEY', None):
                raise ValueError("GROQ_API_KEY is not configured")

            headers = {
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            }

            prompt = (
                f"Write a concise tribute for {name}, my {relationship}. "
                f"Use only these memories: {memories}. "
                "120–180 words. Accurate, sincere, respectful. "
                "Do not invent details. Keep it simple and meaningful."
            )

            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 300,
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content'].strip()

        except Exception as e:
            logger.error(f"Error generating tribute: {e}")
            return "We encountered an issue while generating your tribute. Please try again later."

class AIHordeService:
    """Service for generating symbolic images using AI Horde"""
    
    @staticmethod
    def generate_memorial_image(prompt):
        """Generate a memorial image based on a prompt"""
        try:
            headers = {
                "apikey": settings.AI_HORDE_API_KEY,
                "Content-Type": "application/json"
            }
            
            # Cartoon/illustration-first enhanced prompt (respectful, accurate, stylized)
            enhanced_prompt = (
                "A respectful, serene memorial portrait as a soft cartoon/illustration. "
                f"Subject details: {prompt}. "
                "Style: clean line art, cel shading, gentle pastel colors, soft lighting, "
                "subtle starry or floral background, high clarity, symmetrical face, elegant composition. "
                "Professional illustration quality, no text or watermark."
            )
            
            # Strong negative prompt to improve accuracy and reduce artifacts
            negative_prompt = (
                "nsfw, gore, violence, harsh shadows, lowres, blurry, noisy, deformed, "
                "mutated, extra fingers, extra limbs, crossed eyes, bad anatomy, bad hands, "
                "text, caption, watermark, signature, logo, frames, border, jpeg artifacts"
            )
            
            payload = {
                "prompt": enhanced_prompt,
                "params": {
                    "steps": 34,
                    "width": 768,
                    "height": 768,
                    "sampler_name": "k_euler_a",
                    "cfg_scale": 8.0,
                    "clip_skip": 2,
                    "karras": True,
                    "seed": None,
                    "tiling": False,
                    "denoise": 1.0,
                    "post_processing": ["RealESRGAN_x4plus_anime_6B"],
                    "control_type": None,
                    "prompt": enhanced_prompt,
                    "negative_prompt": negative_prompt
                },
                "nsfw": False,
                "censor_nsfw": True,
                # Prefer anime/cartoon capable models; Horde will fallback if unavailable
                "models": [
                    "anythingv4.5",
                    "ToonYou",
                    "MeinaMix",
                    "stable_diffusion"
                ]
            }
            
            # Submit generation request
            submit_response = requests.post(
                "https://aihorde.net/api/v2/generate/async",
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            submit_response.raise_for_status()
            task_id = submit_response.json().get("id")
            if not task_id:
                raise Exception("Failed to get task ID from AI Horde.")
            
            # Poll for results with timeout
            for _ in range(36):  # ~3 minutes at 5s interval
                check_response = requests.get(
                    f"https://aihorde.net/api/v2/generate/check/{task_id}",
                    headers=headers,
                    timeout=20
                )
                check_response.raise_for_status()
                status = check_response.json()
                
                if status.get("done", False):
                    # Get the image results
                    result = requests.get(
                        f"https://aihorde.net/api/v2/generate/status/{task_id}",
                        headers=headers,
                        timeout=30
                    )
                    result.raise_for_status()
                    data = result.json()
                    gens = data.get("generations") or []
                    if gens and "img" in gens[0]:
                        return gens[0]["img"]
                    return None
                
                time.sleep(5)  # Check every 5 seconds
            
            return None
        
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None
            return None
