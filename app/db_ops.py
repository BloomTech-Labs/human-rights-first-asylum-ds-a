import os
import pandas as pd
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
    uuid VARCHAR(256),
    panel_members VARCHAR(256),
    decision_type VARCHAR(256),
    application_type VARCHAR(256),
    decision_date VARCHAR(256),
    country_of_origin VARCHAR(256),
    outcome VARCHAR(256),
    case_origin_state VARCHAR(256),
    case_origin_city VARCHAR(256),
    protected_grounds VARCHAR(256),
    type_of_persecution VARCHAR(256),
    gender VARCHAR(256),
    credibility VARCHAR(256),
    check_for_one_year VARCHAR(256));""")


def get_table():
    return db_query("""SELECT * FROM ds_cases;""")


def reset_table():
    db_action("""DROP TABLE ds_cases;""")
    initialize_db()


def delete_by_id(_id):
    db_action(f"""DELETE FROM ds_cases WHERE id = {_id};""")


def get_df() -> pd.DataFrame:
    conn = psycopg2.connect(db_url)
    curs = conn.cursor()
    curs.execute("SELECT * FROM cases;")
    cols = [k[0] for k in curs.description]
    rows = curs.fetchall()
    df = pd.DataFrame(rows, columns=cols)
    curs.close()
    conn.close()
    return df
