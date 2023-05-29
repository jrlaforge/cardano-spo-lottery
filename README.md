# Cardano Spo Lottery

```
source venv/bin/activate
pip install -r requirements.txt
pip install -e src/

make test
```

### Run 

FLASK_APP=entrypoints/flask_app.py FLASK_DEBUG=1 flask run --port=4500


docker-compose build && docker-compose up -d && docker-compose logs


### Alembic 

Edit alembic.ini
alembic revision --autogenerate -m "Add min live stake"
alembic current
alembic upgrade head


alembic downgrade -1