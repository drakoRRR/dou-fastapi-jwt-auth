# FastAPI JWT Authorization

## Installation
1. Fill .env file, by example:
```angular2html
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=

POSTGRES_DB_TEST=
POSTGRES_TEST_USER=
POSTGRES_TEST_PASSWORD=
DB_TEST_HOST=
DB_TEST_PORT=

DEBUG=
SECRET_KEY=

ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
REFRESH_TOKEN_EXPIRE_DAYS=
```
2. Use `make up` to start project 
3. Run tests with `make test` to check if everything is correct

By this url you can achieve API Documentation: `http://127.0.0.1:5000/api/docs`