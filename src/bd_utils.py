import os
from configparser import ConfigParser

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

from src.cls_GetData import GetEmployerData, HeadHunterHAPI


def config(filename="../database.ini", section="postgresql"):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            "Section {0} is not found in the {1} fil e.".format(section, filename)
        )
    return db


def create_database(database_name: str):
    # создание базы данных. Проверяется, если БД database_name существует, удаляется, затем БД database_name создается
    params = config()
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        cur.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(database_name)))
    except psycopg2.errors.InvalidCatalogName:
        print(f"База данных {database_name} не существует, пропускаем удаление.")

    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
    cur.close()
    conn.close()


def create_tables(name_database: str):
    # создание двух таблиц - работодатели и вакансии по работодателям
    params = config()
    conn = psycopg2.connect(dbname=name_database, **params)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS hh_employers (
                    id INT PRIMARY KEY,
                    name VARCHAR(255),
                    open_vacancies INT
                    );
        """
        )
    except psycopg2.errors:
        print(
            f"Ошибка при создании таблицы hh_employers в базе данных {name_database}."
        )

    try:
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS hh_vacancies (
                    id SERIAL PRIMARY KEY,
                    id_employer INT REFERENCES hh_employers(id),
                    id_vacancy INT,
                    name_vacancy VARCHAR(255),
                    salary INT
                    );
        """
        )
    except psycopg2.errors:
        print(
            f"Ошибка при создании таблицы hh_vacancies в базе данных {name_database}."
        )

    cur.close()
    conn.close()


def fill_data():
    # заполняет созданные в БД PostgreSQL таблицы данными о работодателях и их вакансиях

    load_dotenv()
    emps_name = os.getenv("EmpList")
    name_database = os.getenv("database_name")

    params = config()
    conn = psycopg2.connect(dbname=name_database, **params)
    conn.autocommit = True
    cur = conn.cursor()

    for emp in list(emps_name[1:-1].replace("'", "").split(",")):
        hh_emp_from_api = GetEmployerData()
        data_emp_list = hh_emp_from_api.get_data(emp)
        print(data_emp_list[0]["id"])
        print(data_emp_list[0])

        try:
            cur.execute(
                """
                    INSERT
                    INTO
                    public.hh_employers(
                        id, name, open_vacancies)
                    VALUES (%s, %s, %s)
            """,
                (
                    data_emp_list[0]["id"],
                    data_emp_list[0]["name"].strip(),
                    data_emp_list[0]["open_vacancies"],
                ),
            )
        except psycopg2.errors:
            print("Ошибка при записи данных в таблицу hh_employers.")

        hh_vac_from_api = HeadHunterHAPI()
        vac_list = hh_vac_from_api.get_vacancies(data_emp_list[0]["id"])
        for vac in vac_list:
            vac_salary = 0

            # Преобразуем 'None' в None для упрощения проверок
            salr_from = vac["salr_from"] if vac["salr_from"] != "None" else None
            salr_to = vac["salr_to"] if vac["salr_to"] != "None" else None

            # Инициализация переменной зарплаты
            vac_salary = None

            # Проверяем условия и вычисляем зарплату
            if salr_from is not None and salr_to is not None:
                vac_salary = (salr_from + salr_to) / 2
            elif salr_from is not None:
                vac_salary = salr_from
            elif salr_to is not None:
                vac_salary = salr_to

            # try:
            cur.execute(
                """
                    INSERT
                    INTO
                    public.hh_vacancies(
                        id_employer, id_vacancy, name_vacancy, salary)
                    VALUES (%s, %s, %s, %s)
            """,
                (data_emp_list[0]["id"], vac["id"], vac["name"], vac_salary),
            )
            # except psycopg2.errors:
            #     print(f"Ошибка при записи данных в таблицу hh_vacancies.")

        print(vac_list)

    cur.close()
    conn.close()


def clear_data():
    # удаляет данные из таблиц hh_employers и hh_vacancies
    load_dotenv()
    # emps_name = os.getenv("EmpList")
    name_database = os.getenv("database_name")

    params = config()
    conn = psycopg2.connect(dbname=name_database, **params)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        cur.execute("delete  FROM public.hh_vacancies")
        cur.execute("delete  FROM public.hh_employers")
    except psycopg2.errors:
        print("Ошибка при удалении данных из таблиц hh_employers и hh_vacancies.")



