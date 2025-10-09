from src.config.settings import AppSettings
from src.shared.tools.api_clients.impl.kp_api_external_client import KpExternalAPIClient


class API:
    def __init__(self, settings: AppSettings):
        api_settings = settings.EXTERNAL_API_SETTINGS
        base_url = api_settings.API_BASE_URL
        token = api_settings.API_ACCESS_TOKEN
        self._client = KpExternalAPIClient(base_url, token)

    def get_client(self):
        return self._client
