#python3 -m venv venv
#source env/bin/activate
#pip3 install -r requirements.txt
#python3 manage.py migrate
#python3 manage.py collectstatic --no-input

docker-compose up --build -d
docker-compose exec app python manage.py migrate
#dockerdocmpose exec app python manage.py createsuperuser
