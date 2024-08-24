python3 -m venv venv
source env/bin/activate
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic --no-input
cd /var/www/html/cw_8
deactivate
