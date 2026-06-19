import requests

from endpoints.models.error_models import AuthErrorResponse, ErrorResponse
from helper.configuration_manager import ConfigurationManager


class BaseEndpoint:
    def __init__(self, session: requests.Session):
        self.session = session
        self.base_url = ConfigurationManager.api_url()

    def _raise_for_error(self, response: requests.Response) -> None:
        if response.ok:
            return
        if response.status_code == 401:
            raise PermissionError(AuthErrorResponse.model_validate(response.json()).error)
        raise ValueError(ErrorResponse.model_validate(response.json()).message)

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(f"{self.base_url}/{path}", **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.session.post(f"{self.base_url}/{path}", **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.session.put(f"{self.base_url}/{path}", **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.session.delete(f"{self.base_url}/{path}", **kwargs)
