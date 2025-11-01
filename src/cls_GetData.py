from abc import ABC, abstractmethod
from typing import Any

from src.cls_HHAPI import HHConnectAPI
from src.utils import get_currency_rate


class GetVacAPI(ABC):
    """Абстрактный класс для получения вакансий с сайта с помощью API"""

    @abstractmethod
    def get_vacancies(self, key_word) -> None:
        """Метод для получения вакансий с сайта с помощью API"""
        pass


class HeadHunterHAPI(GetVacAPI):
    """Класс для получения вакансий с сайта с помощью API"""

    def __init__(self):
        self._answer = None

    def get_vacancies(self, id_employer: str) -> list:
        """Метод для получения вакансий с сайта с помощью API"""
        """ Метод получает вакансии по запросу, в зависимости от параметров. Если key_word=False,
        то запрос выполняется по всем вакансиям с указанной зарплатой
        """
        params = {
            "employer_id": id_employer,
            "currency": "RUR",
            "only_with_salary": "true",
            "page": 0,
            "per_page": 50,
        }

        # получить вакансии
        connect_api = HHConnectAPI()
        response = connect_api.connect_to_api("vacancies", params)

        vacancy_list = response.json()["items"]
        vacancy_cutted_list = []
        if response.status_code == 200 and len(vacancy_list) > 0:

            def cut_attr(vacancy_dict) -> dict[str, Any]:
                """Вернуть список со словарями только с указанными ключами"""
                return {k: vacancy_dict[k] for k in attr_dest}

            def convert_to_rur(src_val, koeff) -> float:
                """Если задан коэффициент, то вернуть сумму, умноженную на коэффициент"""
                if isinstance(src_val, int):
                    return src_val * koeff
                else:
                    return src_val

            def to_process_rate_curr(rate_curr) -> None:
                if rate_curr not in rates.keys():
                    queried_rate_curr = get_currency_rate(rate_curr)
                    if not queried_rate_curr:
                        print(
                            f"для валюты {rate_curr} не найден курс. Коэффициент преревода в рубли установлен в 1"
                        )
                        rates[rate_curr] = 1
                    else:
                        rates[rate_curr] = queried_rate_curr["result"]

            # вынести на первый уровень словаря
            #   name из area; from, to из salary
            rates = {"RUR": 1}
            for vacancy in vacancy_list:
                vacancy["area_name"] = vacancy.get("area").get("name", "нет")

                # обработать валюту вакансии. Если курса валюты нет в списке - запросить через API и добавить
                to_process_rate_curr(vacancy.get("salary").get("currency", "нет"))

                # если указаны числовые значения границ зарплат, то привести их к рублю
                vacancy["salr_from"] = convert_to_rur(
                    vacancy.get("salary").get("from", 0),
                    rates[vacancy.get("salary").get("currency", "нет")],
                )
                vacancy["salr_to"] = convert_to_rur(
                    vacancy.get("salary").get("to", 0),
                    rates[vacancy.get("salary").get("currency", "нет")],
                )

            # Оставить только нужные ключи в списке
            attr_dest = ["id", "name", "area_name", "salr_from", "salr_to"]
            vacancy_cutted_list = list(map(cut_attr, vacancy_list))

        return vacancy_cutted_list


class ABCGetEmployerData:
    """абстрактный класс для получения данных"""

    @abstractmethod
    def get_data(self):
        pass


class GetEmployerData(ABCGetEmployerData):
    """класс для получения данных"""

    def get_data(self, name_employer: str):
        """метод получения данных"""
        params = {"text": name_employer, "page": 0, "per_page": 50}

        # получить данные работодателя
        connect_api = HHConnectAPI()
        response = connect_api.connect_to_api("employers", params)

        employer_data_list = response.json()["items"]
        return employer_data_list
