import json
import urllib.error
import urllib.request

from django.conf import settings


class GeminiClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL

    @property
    def enabled(self):
        return bool(self.api_key)

    def generate_json(self, prompt):
        if not self.enabled:
            return None

        url = (
            f'https://generativelanguage.googleapis.com/v1beta/models/'
            f'{self.model}:generateContent?key={self.api_key}'
        )
        payload = json.dumps({
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {'response_mime_type': 'application/json'},
        }).encode('utf-8')
        request = urllib.request.Request(
            url,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = json.loads(response.read().decode('utf-8'))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return None

        try:
            text = raw['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            return None
