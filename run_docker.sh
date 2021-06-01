service nginx restart
cd /becky/backend/
uwsgi --http :6701 --module becky.wsgi
#python3 manage.py runserver 0.0.0.0:6701
