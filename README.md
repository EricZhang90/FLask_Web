# PythonWeb

**Pre-condition:**

 1. MySQL installed

 2. A database named 'PythonWeb' is created in MySQL

 3. Setup all environment variables in environment_variables.txt


**Installation:**

  1. virtualvenv -ve

  2. source ve/bin/active

  3. pip install -r extentions.txt


**Sepup tables in DB:**

1. python manage.py shell

2. db.create_all()


**Setup Migration:**

1. python manage.py db init

2. python manage.py db migrate -m "initial migration"


**Use Migration:**

1. python manage.py db upgrade


**Run:**

1. python manage.py runserver --host 0.0.0.0


**Exit:**

1. ctrl + c
