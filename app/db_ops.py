import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()
db_url = os.getenv('DB_URL')


def db_action(sql_action: str):
    """ DB Setter - Performs a DB action returns None """
    conn = psycopg2.connect(db_url)
    curs = conn.cursor()
    curs.execute(sql_action)
    conn.commit()
    curs.close()
    conn.close()


def db_query(sql_query) -> list:
    """ DB Getter - Returns query results as a list """
    conn = psycopg2.connect(db_url)
    curs = conn.cursor()
    curs.execute(sql_query)
    results = curs.fetchall()
    curs.close()
    conn.close()
    return results


def fix_str(s):
    return repr(s.replace("'", "’"))


def insert_case(case_data: dict):
    db_action(f"""INSERT INTO ds_cases
    ({', '.join(case_data.keys())})
    VALUES ({', '.join(map(fix_str, case_data.values()))});""")


def initialize_db():
    """ Database table initialization - only required once """
    db_action(f"""CREATE TABLE IF NOT EXISTS ds_cases (
    id SERIAL PRIMARY KEY NOT NULL,
    uuid TEXT,
    panel_members TEXT,
    hearing_type TEXT,
    application_type TEXT,
    date TEXT,
    country_of_origin TEXT,
    outcome TEXT,
    case_origin_state TEXT,
    case_origin_city TEXT,
    protected_grounds TEXT,
    type_of_violence TEXT,
    gender TEXT,
    indigenous_group TEXT,
    applicant_language TEXT,
    credibility TEXT,
    check_for_one_year TEXT);""")


def get_table():
    return db_query("""SELECT * FROM ds_cases;""")


def reset_table():
    db_action("""DROP TABLE ds_cases;""")
    initialize_db()


if __name__ == '__main__':
    reset_table()
    print(get_table())
