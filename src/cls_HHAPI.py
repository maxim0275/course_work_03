import os
from abc import ABC, abstractmethod

import requests
from dotenv import load_dotenv


class ConnectAPI(ABC):
    """абстрактный класс для соединения с API"""

    @abstractmethod
    def connect_to_api(self, api: str, params: str) -> None:
        pass


class HHConnectAPI(ConnectAPI):
    """класс для соединения с API"""

    def connect_to_api(self, api: str, params: dict) -> None:
        """метод для соединения с API"""
        load_dotenv()
        url_site = os.getenv("HH_API")
        url_api = url_site + api

        try:
            # Выполнение GET-запроса к API
            response = requests.get(url_api, params=params)

            # Проверка успешности запроса
            response.raise_for_status()

            # Возврат JSON-ответа
            return response

        except requests.RequestException as e:
            # Обработка ошибок подключения
            print(f"Ошибка при подключении к API: {e}")
            return None
