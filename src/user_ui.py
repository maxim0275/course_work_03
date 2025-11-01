import os

from dotenv import load_dotenv
from psycopg2 import OperationalError

from src.bd_utils import clear_data, create_database, create_tables, fill_data
from src.DBManager import DBManager


def user_interact() -> None:
    try:
        db = DBManager()
    except OperationalError:
        print("не удалось соединиться с базой данных")

    cond_keyword = ""
    user_answer = ""

    user_actions = [
        "",
        "1. Создать базу данных с таблицами",
        "2. Получить данные из hh.ru",
        "3. Получить список всех "
        "компаний и количество "
        "вакансий у каждой "
        "компании",
        "4. Получить список всех вакансий",
        "5. Получить среднюю зарплату по вакансиям",
        "6 Получить всех вакансий с зарплатой выше средней",
        "7. Ввести ключевое слово",
        "8. Получить вакансии с ключевым словом",
        "9. Выход",
    ]

    while user_answer != "9":
        print("Возможные действия:")
        print(user_actions[1])
        print(user_actions[2])
        print(user_actions[3])
        print(user_actions[4])
        print(user_actions[5])
        print(user_actions[6])
        print(user_actions[7])
        print(user_actions[8])
        print(user_actions[9])
        print("===============================================================")
        print("Текущие условия:")
        print(f"Фильтр для отбора по  ключевому слову: {cond_keyword}")
        print("===============================================================")
        print("Ожидается ввод пользователя: (1 .. 8): ____")

        user_answer = input()

        if user_answer == "1":
            print(user_actions[1])
            load_dotenv()
            database_name = os.getenv("database_name")
            try:
                db.close()
            except:
                "Нет соединения с баздой данных hh_data"

            create_database(database_name)
            create_tables(database_name)
            try:
                db = DBManager()
            except OperationalError:
                print("не удалось соединиться с базой данных")

        elif user_answer == "2":
            print(user_actions[2])
            clear_data()
            fill_data()
        elif user_answer == "3":
            print(user_actions[3])
            for dict_cv in db.get_companies_and_vacancies_count():
                print(dict_cv)
        elif user_answer == "4":
            print(user_actions[4])
            for dict_cv in db.get_all_vacancies():
                print(dict_cv)
        elif user_answer == "5":
            print(user_actions[5])
            print(db.get_avg_salary())
        elif user_answer == "6":
            print(user_actions[6])
            for dict_cv in db.get_vacancies_with_higher_salary():
                print(dict_cv)
        elif user_answer == "7":
            print(user_actions[7])
            cond_keyword = input()
        elif user_answer == "8":
            print(user_actions[8])
            for dict_cv in db.get_vacancies_with_keyword(cond_keyword):
                print(dict_cv)
        elif user_answer == "9":
            print(user_actions[9])

    db.close()
