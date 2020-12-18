import sqlalchemy
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv()

database_url = os.getenv('DATABASE_URL')

print('db url name', database_url)


engine = create_engine(database_url)

query = """SELECT * FROM pdfs""" 
truncateQuery = """TRUNCATE TABLE pdfs"""
# engine.execute(truncateQuery)

infoQuery = '''select *
from INFORMATION_SCHEMA.COLUMNS
where TABLE_NAME='pdfs'
'''
dropQuery = '''DROP TABLE pdfs'''
createQuery = '''CREATE TABLE pdfs (
                plainText   text,
                judge       varchar(30),
                description text
);'''
# engine.execute(dropQuery)
# engine.execute(createQuery)
print(engine.execute(query).fetchall())