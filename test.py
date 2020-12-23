import sqlalchemy
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv()

database_url = os.getenv('DATABASE_URL')

print('db url name', database_url)


engine = create_engine(database_url)

selQuery = """SELECT COUNT(*) FROM pdfs""" 
truncateQuery = """TRUNCATE TABLE pdfs"""
plainTextQuery = """SELECT plainText from pdfs;"""
print('initial values prior to wipe', engine.execute(selQuery).fetchall())

print(f'show plain text values')
results = engine.execute(plainTextQuery)
for x in results:
    print(x[0][:10])
infoQuery = '''select *
from INFORMATION_SCHEMA.COLUMNS
where TABLE_NAME='pdfs'
'''
engine.execute(truncateQuery)
dropQuery = '''DROP TABLE pdfs'''
createQuery = '''CREATE TABLE pdfs (
                plainText   text,
                judge       varchar(30),
                description text
);'''
# engine.execute(dropQuery)
# engine.execute(createQuery)
