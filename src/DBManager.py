import os
from typing import List, Optional, Tuple

import psycopg2
from dotenv import load_dotenv

from src.bd_utils import config


class DBManager:
    def __init__(self) -> None:
        load_dotenv()
        name_database = os.getenv("database_name")

        params = config()
        self.connection = psycopg2.connect(dbname=name_database, **params)
        self.cursor = self.connection.cursor()

    def get_companies_and_vacancies_count(self) -> List[Tuple[int, str, int]]:
        query = """
        SELECT e.id, e.name, COUNT(v.id_vacancy) AS open_vacancies
        FROM public.hh_employers e
        LEFT JOIN public.hh_vacancies v ON e.id = v.id_employer
        GROUP BY e.id, e.name;
        """
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        # Преобразуем список кортежей в список словарей для удобства
        companies_count_list = [
            {"id": row[0], "name": row[1], "open_vacancies": row[2]} for row in results
        ]

        return companies_count_list

    def get_all_vacancies(self) -> List[Tuple[int, str, str, Optional[float]]]:
        query = """
        SELECT v.id, e.name AS company_name, v.name_vacancy, v.salary
        FROM public.hh_vacancies v
        JOIN public.hh_employers e ON v.id_employer = e.id;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_avg_salary(self) -> Optional[float]:
        query = """
        SELECT AVG(salary) FROM public.hh_vacancies WHERE salary IS NOT NULL;
        """
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]  # Возвращаем только одно значение

    def get_vacancies_with_higher_salary(
        self,
    ) -> List[Tuple[int, str, str, Optional[float]]]:
        avg_salary = self.get_avg_salary()
        query = """
        SELECT v.id, e.name AS company_name, v.name_vacancy, v.salary
        FROM public.hh_vacancies v
        JOIN public.hh_employers e ON v.id_employer = e.id
        WHERE v.salary > %s;
        """
        self.cursor.execute(query, (avg_salary,))
        return self.cursor.fetchall()

    def get_vacancies_with_keyword(
        self, keyword: str
    ) -> List[Tuple[int, str, str, Optional[float]]]:
        query = """
        SELECT v.id, e.name AS company_name, v.name_vacancy, v.salary
        FROM public.hh_vacancies v
        JOIN public.hh_employers e ON v.id_employer = e.id
        WHERE v.name_vacancy ILIKE %s;
        """
        self.cursor.execute(query, (f"%{keyword}%",))
        return self.cursor.fetchall()

    def close(self) -> None:
        self.cursor.close()
        self.connection.close()


# Пример использования
# if __name__ == "__main__":
# db = DBManager()

# print(db.get_companies_and_vacancies_count())
# print(db.get_all_vacancies())
# print(db.get_avg_salary())
# print(db.get_vacancies_with_higher_salary())
# print(db.get_vacancies_with_keyword('специалист'))

# db.close()
