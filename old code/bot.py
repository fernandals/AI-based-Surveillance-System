import requests

class Bot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.session = requests.Session()  # Mantém uma sessão para melhor desempenho

    def send_message(self, message: str) -> dict:
        url = f"{self.base_url}/sendMessage"
        print("a")
        payload = {"chat_id": self.chat_id, "text": message}
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()  # Lança exceção para códigos HTTP 4xx/5xx
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def send_photo(self, photo_path: str) -> dict:
        url = f"{self.base_url}/sendPhoto"
        try:
            with open(photo_path, 'rb') as photo_file:
                files = {'photo': photo_file}
                payload = {'chat_id': self.chat_id}
                response = self.session.post(url, data=payload, files=files)
                response.raise_for_status()
                return response.json()
        except (requests.RequestException, FileNotFoundError) as e:
            return {"error": str(e)}

    def __del__(self):
        self.session.close()  # Fecha a sessão ao destruir a instância