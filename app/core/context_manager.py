import json
from pathlib import Path
from app.core.config import settings

class ContextManager:
    def __init__(self):
        self.storage_path = settings.DATA_DIR / "context" / "global_context.json"
        self.data = self._load_data()

    def _load_data(self):
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                return json.load(f)
        return {"providers": {}, "active_shop": None}

    def save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_shop(self, provider: str, shop_name: str, credentials: dict):
        if provider not in self.data["providers"]:
            self.data["providers"][provider] = {}
        self.data["providers"][provider][shop_name] = credentials
        self.save()

    def set_active(self, provider: str, shop_name: str):
        if provider in self.data["providers"] and shop_name in self.data["providers"][provider]:
            self.data["active_shop"] = {
                "provider": provider,
                "shop_name": shop_name,
                "credentials": self.data["providers"][provider][shop_name]
            }
            self.save()
            return True
        return False

    def clear_active(self):
        self.data["active_shop"] = None
        self.save()

    def get_active(self):
        return self.data.get("active_shop")

context_manager = ContextManager()