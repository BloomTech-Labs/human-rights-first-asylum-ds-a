The app folder houses the functional aspects of the app as well as the DB connection.

In building out the functionality of the app we gave the app folder a relatively 'flat' layout. For example, db.py file houses the DBAPI connection as well as the schemas and DB models. Other developers might have a preference to create separate files for the connection, schema and models.

However, for the sake of flexibility and convenience we housed those aspects in one file and left it open for further build-out by future developers working on the project.

The functionality of the db.py file is then routed to the main.py via the APIRouter. This facilitates running the functions in db.py from main.py and we thought the same set-up would be perfect for the other files in the app folder.

The folder set-up roughly follows the set-up described in the fastAPI README file which can be found at https://github.com/tiangolo/fastapi