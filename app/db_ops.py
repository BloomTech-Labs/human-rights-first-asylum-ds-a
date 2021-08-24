import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
import plotly.express as px


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
    decision_type TEXT,
    application_type TEXT,
    decision_date TEXT,
    country_of_origin TEXT,
    outcome TEXT,
    case_origin_state TEXT,
    case_origin_city TEXT,
    protected_grounds TEXT,
    type_of_violence TEXT,
    gender TEXT,
    credibility TEXT,
    check_for_one_year TEXT);""")


def get_table():
    return db_query("""SELECT * FROM ds_cases;""")


def reset_table():
    db_action("""DROP TABLE ds_cases;""")
    initialize_db()


def delete_by_id(_id):
    db_action(f"""DELETE FROM ds_cases WHERE id = {_id};""")


def get_judge_df(judge_name: str) -> pd.DataFrame:
    """
    Returns judge case data from ds_cases table based on judge
    name as a filter.
    """
    judge_name = "%" + judge_name + "%"
    conn = psycopg2.connect(db_url)
    curs = conn.cursor()
    curs.execute(f"""SELECT * FROM ds_cases
                 WHERE panel_members LIKE {fix_str(judge_name)}
                 AND decision_type = 'Initial';""")
    cols = [k[0] for k in curs.description]
    rows = curs.fetchall()
    df = pd.DataFrame(rows, columns = cols)
    curs.close()
    conn.close()
    return df
