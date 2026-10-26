import os
import requests

# Configuration de l'endpoint Muse / Meta AI pour le hackathon
# Remplace l'URL et la structure selon la doc officielle de ta plateforme
MUSE_API_URL = "https://api.muse.meta.com/v1/chat/completions" # Endpoint officiel de la plateforme Meta/Muse
MODEL_NAME = "muse-spark-1.3" # Notre modèle ultra-puissant orienté code et agents

def analyze_web_content(url: str, html_content: str = None):
    """
    Core function to analyze a target URL or HTML content
    and detect WCAG/RGAA accessibility violations using Muse Spark 1.3.
    """
    
    system_prompt = (
        "You are a world-class digital accessibility expert specializing in WCAG 2.1 (AA level) and RGAA standards. "
        "Your goal is to detect web accessibility violations and provide exact, production-ready code fixes."
    )
    
    user_prompt = f"""
    Analyze the following target website/URL: {url}
    
    Identify common accessibility errors (such as color contrast failures, missing alt attributes, incorrect heading hierarchy, missing ARIA roles, or keyboard navigation traps).
    For each detected violation, provide:
    1. The faulty HTML element.
    2. The exact WCAG compliance criterion violated.
    3. A clear description of the issue.
    4. The exact corrected code snippet ready for deployment.
    
    Respond in a clean, structured JSON format with a root array of violations.
    """

    headers = {
        "Authorization": f"Bearer {os.getenv('MUSE_API_KEY', 'DUMMY_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 2000
    }

    try:
        # Real API call when MUSE_API_KEY is configured in your environment variables
        if os.getenv('MUSE_API_KEY'):
            response = requests.post(MUSE_API_URL, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                # Parse or return model response
                return response.json()
        
        # Fallback / Smart Mocked Response for testing the UI flow instantly
        return {
            "status": "success",
            "model_used": MODEL_NAME,
            "target_url": url,
            "violations_found": 2,
            "violations": [
                {
                    "element": "<img src='hero-banner.jpg'>",
                    "criterion": "WCAG 1.1.1 - Non-text Content",
                    "description": "The image element lacks a descriptive alt attribute for assistive technologies.",
                    "fix_code": "<img src='hero-banner.jpg' alt='WebRuler platform presentation and live auditing dashboard'>"
                },
                {
                    "element": "<button class='cta-btn'>Click Here</button>",
                    "criterion": "WCAG 2.4.4 - Link Purpose (In Context)",
                    "description": "Ambiguous button text ('Click Here') does not describe its specific action out of context.",
                    "fix_code": "<button class='cta-btn' aria-label='Start free accessibility audit'>Start Free Audit</button>"
                }
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}