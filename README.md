# 1) Create and activate venv 
python -m venv venv 

venv\Scripts\activate 

# 2) Install dependencies 
pip install -r requirements.txt 

# 3) Create database tables 
python manage.py migrate 

# 4) Create admin login (if missing) 
python manage.py create_default_admin 

# 5) Bulk load CSVs into SQLite 
python manage.py load_who_data 

# 6) Run unit tests 
python manage.py test 

# 7) Start server 
python manage.py runserver
