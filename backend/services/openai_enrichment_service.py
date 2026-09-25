"""Service OpenAI pour enrichir le texte astrologique"""

import os
import httpx
from typing import Dict, Any, Optional

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = 'gpt-4o-mini'  # Modèle rapide et économique


def enrich_window_text(window_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enrichit une fenêtre de rencontre avec du texte poétique et inspirant."""
    
    if not OPENAI_API_KEY:
        print("⚠️  OPENAI_API_KEY non configurée")
        return window_data
    
    try:
        kind = window_data.get('kind', 'Fenêtre')
        period = window_data.get('period', '')
        original_text = window_data.get('text', '')
        
        prompt = f"""Tu es Solena, la voix bienveillante et poétique de Plume Astrale.

Transforme cette information astrologique en un texte inspirant, rassurant et mystique qui captive le lecteur.

**Données astrologique:**
- Nom de la fenêtre: {kind}
- Période: {period}
- Description originale: {original_text}

**Ton requis:**
- Inspirant, rassurant, poétique, bienveillant, optimiste, élégant, mystique mais crédible
- Motivant, calme, introspectif
- Le lecteur doit ressentir: espoir, curiosité, sérénité, enthousiasme, reconnexion avec lui-même

**Format:**
Écris un paragraphe de 120-150 mots qui:
1. Commence par une phrase captivante et poétique
2. Explique l'énergie cosmique en termes accessibles mais profonds
3. Donne un sentiment de confiance et de possibilité
4. Termine par une invitation à l'action douce et inspirante

N'utilise pas de listes à puces. Écris en prose fluide et élégante.
Utilise un français raffiné, avec des métaphores cosmiques subtiles."""
        
        response = httpx.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': OPENAI_MODEL,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Tu es Solena, la voix de Plume Astrale. Ton écriture est poétique, bienveillante et inspirante.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.8,  # Créatif mais cohérent
                'max_tokens': 400,
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            enriched_text = data['choices'][0]['message']['content'].strip()
            
            window_data['text'] = enriched_text
            window_data['text_enriched'] = True
            print(f"✅ {kind}: Texte enrichi par OpenAI")
            return window_data
        else:
            print(f"⚠️  Erreur OpenAI {response.status_code}: {response.text}")
            return window_data
    
    except Exception as e:
        print(f"⚠️  Erreur lors de l'enrichissement: {e}")
        return window_data


def enrich_all_windows(windows_data: list) -> list:
    """Enrichit toutes les fenêtres."""
    return [enrich_window_text(window) for window in windows_data]


def generate_transits_summary(transits_data: Dict[str, Any], birth_city: str) -> str:
    """Génère un résumé poétique des transits actuels."""
    
    if not OPENAI_API_KEY:
        return "Les énergies cosmiques sont en mouvement à ton avantage."
    
    try:
        prompt = f"""Tu es Solena de Plume Astrale.

À partir de ces données astrales, crée un résumé poétique et inspirant (100-120 mots) sur les énergies actuelles pour quelqu'un vivant à {birth_city}.

**Données de transits:**
{str(transits_data)}

Le texte doit:
- Être poétique et mystique
- Inspirer confiance et espoir
- Parler des énergies de Vénus, Jupiter et la Lune
- Être personnel et touchant
- Utiliser un ton calme et bienveillant"""
        
        response = httpx.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': OPENAI_MODEL,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Tu es Solena, la voix poétique et bienveillante de Plume Astrale.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.8,
                'max_tokens': 300,
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        else:
            return "Les énergies cosmiques te soutiennent dans ta quête."
    
    except Exception as e:
        print(f"⚠️  Erreur: {e}")
        return "L'univers t'apporte ses bénédictions."


def generate_daily_affirmations(birth_name: str, birth_sign: str) -> list:
    """Génère des affirmations quotidiennes personnalisées et inspirantes."""
    
    if not OPENAI_API_KEY:
        return [
            "Je suis magnétique et attirant(e).",
            "L'univers m'apporte la rencontre parfaite.",
        ]
    
    try:
        prompt = f"""Tu es Solena de Plume Astrale.

Crée 5 affirmations quotidiennes courtes, puissantes et inspirantes pour {birth_name} (signe: {birth_sign}).

**Critères:**
- Chacune: 8-12 mots maximum
- Personnel et résonnant
- Poétique mais direct
- Inspire confiance, espoir, connexion avec soi-même
- Ton bienveillant et motivant

Format: Une affirmation par ligne, sans numérotation."""
        
        response = httpx.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': OPENAI_MODEL,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Tu es Solena, la voix de Plume Astrale. Tes affirmations sont poétiques, puissantes et transformatrices.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.8,
                'max_tokens': 300,
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            text = data['choices'][0]['message']['content'].strip()
            affirmations = [line.strip() for line in text.split('\n') if line.strip()]
            print(f"✅ {len(affirmations)} affirmations générées par OpenAI")
            return affirmations
        else:
            return []
    
    except Exception as e:
        print(f"⚠️  Erreur: {e}")
        return []
