import logging
import os

from dotenv import load_dotenv
from requests import request

utils_logger = logging.getLogger("utils")
utils_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
)
path_to_file: str = os.path.join(os.path.dirname(__file__), "../logs/utils.log")
file_handler = logging.FileHandler(path_to_file, encoding="utf-8", mode="w")
file_handler.setFormatter(formatter)
utils_logger.addHandler(file_handler)


def get_currency_rate(currency):
    """
    возвращает через вызов API курс валюты по отношению к рублю
    :rtype: object
    """
    payload = {}
    load_dotenv()
    api_key = os.getenv("API_KEY1")
    headers = {"access_key": api_key}
    url_for_rates = f"https://api.currencylayer.com/convert?access_key={api_key}&from={currency}&to=RUB&amount=1"
    response = request("GET", url_for_rates, headers=headers, data=payload)
    if response.status_code == 200:
        result_json = response.json()
    else:
        utils_logger.warning(
            f"при получении курса валюты {currency} "
            f"получен ответ {response.status_code}: {response.content}"
        )
        return []
    return result_json
