  
#!/bin/bash

rm db-dev.sqlite3
rm profiles/migrations/0*_*.py
python manage.py makemigrations
python manage.py migrate
python manage.py refresh_fixtures --profiles=50