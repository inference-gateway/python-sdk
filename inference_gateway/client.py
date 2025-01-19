import requests


class InferenceGatewayClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def list_models(self):
        response = requests.get(f"{self.base_url}/llms")
        response.raise_for_status()
        return response.json()

    def generate_content(self, provider, model, prompt):
        payload = {"modelName": model, "prompt": prompt}
        response = requests.post(f"{self.base_url}/llms/{provider}/generate", json=payload)
        response.raise_for_status()
        return response.json()
