# Finance API

REST API для учета личных финансов.

## Стек
- Python 3.13
- FastAPI
- Pandas
- Pydantic

## Функции
- Добавление записей (POST /transactions)
- Получение списка (GET /transactions)
- Расчет баланса (GET /balance)
- Удаление последней записи (DELETE /transactions/last)

## Как запустить
pip install -r requirements.txt
uvicorn api_finance:app --reload
