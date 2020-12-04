import psycopg2

#template for adding table to the database -- already added the tester table

connection = psycopg2.connect(user= "master",
                                        password= "gNh1GB4hW5MFqJvmthF2", 
                                        host= "asylum.catpmmwmrkhp.us-east-1.rds.amazonaws.com",
                                        port = "5432",  
                                        database = "asylum")
cursor = connection.cursor()

    #print POSTGRES Conn properties
print(connection.get_dsn_parameters(), "\n")


cursor.execute("""CREATE TABLE tester(
    case_id SERIAL PRIMARY KEY,
    hearing_date DATE,
    hearing_type TEXT,
    hearing_location TEXT,
    decision_date DATE,
    judge TEXT,
    outcome TEXT,
    protected_ground TEXT,
    social_group_type TEXT,
    country_origin TEXT)""")

connection.commit()
