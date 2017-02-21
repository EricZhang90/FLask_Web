# PythonWeb  - A Web Server#

* Currently running in: http://eric909.pythonanywhere.com/

## Deployment: ##

*__Pre-condition:__*

 1. MySQL installed

 2. A database named 'PythonWeb' is created in MySQL

 3. Setup all environment variables in environment_variables.txt

 4. Git installed


*__Installation:__*

  1. git clone https://github.com/EricZhang90/PythonWeb.git

  2. virtualvenv -ve

  3. source ve/bin/active    [Make sure this command is run everytime]

  4. For development environmemt: pip install -r extentions/dev.txt
  
     For production environment: pip install -r extentions/prod.txt


*__Setup tables in DB:__*

1. python manage.py shell

2. db.create_all()


*__Setup Migration:__*

1. rm -rf migrations

2. python manage.py db init

3. python manage.py db migrate -m "initial migration"


*__Use Migration:__*

1. python manage.py db migrate

2. python manage.py db upgrade


*__Run:__*

1. python manage.py runserver --host 0.0.0.0


*__Exit:__*

1. ctrl + c
