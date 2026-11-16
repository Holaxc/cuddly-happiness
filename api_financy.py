from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
from datetime import datetime
import uvicorn

app = FastAPI(title="Finance Tracker")

DATA_FILE = "finance_data.csv"

# Создаем файл, если его нет
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Дата", "Тип", "Категория", "Сумма", "Комментарий"])
    df.to_csv(DATA_FILE, index=False)

# --- ВСТРОЕННЫЙ HTML ШАБЛОН ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Finance Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f1115; color: #f3f4f6; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; color: #4f46e5; }
        .card { background-color: #181c24; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
        .stats { display: flex; justify-content: space-around; margin-bottom: 20px; }
        .stat-box { text-align: center; }
        .stat-box h3 { margin: 5px 0; color: #9ca3af; font-size: 14px; }
        .stat-box p { margin: 0; font-size: 24px; font-weight: bold; }
        .income { color: #10b981; }
        .expense { color: #ef4444; }
        .balance { color: #4f46e5; }
        form { display: flex; flex-direction: column; gap: 10px; }
        input, select { padding: 10px; border-radius: 8px; border: 1px solid #333; background-color: #0f1115; color: white; }
        button { padding: 12px; border: none; border-radius: 8px; background-color: #4f46e5; color: white; font-weight: bold; cursor: pointer; }
        button:hover { background-color: #4338ca; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #333; }
        th { color: #9ca3af; font-size: 12px; text-transform: uppercase; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💰 Finance Tracker</h1>
        
        <div class="card stats">
            <div class="stat-box">
                <h3>Доходы</h3>
                <p class="income">{{ total_income }} ₽</p>
            </div>
            <div class="stat-box">
                <h3>Расходы</h3>
                <p class="expense">{{ total_expense }} ₽</p>
            </div>
            <div class="stat-box">
                <h3>Баланс</h3>
                <p class="balance">{{ balance }} ₽</p>
            </div>
        </div>

        <div class="card">
            <h2>Добавить запись</h2>
            <form action="/add" method="post">
                <select name="type" required>
                    <option value="Доход">Доход</option>
                    <option value="Расход">Расход</option>
                </select>
                <input type="text" name="category" placeholder="Категория" required>
                <input type="number" step="0.01" name="amount" placeholder="Сумма" required>
                <input type="text" name="comment" placeholder="Комментарий">
                <button type="submit">Добавить</button>
            </form>
        </div>

        <div class="card">
            <h2>История операций</h2>
            <table>
                <thead>
                    <tr><th>Дата</th><th>Тип</th><th>Категория</th><th>Сумма</th><th>Комментарий</th></tr>
                </thead>
                <tbody>
                    {% for row in transactions %}
                    <tr>
                        <td>{{ row['Дата'] }}</td><td>{{ row['Тип'] }}</td><td>{{ row['Категория'] }}</td><td>{{ row['Сумма'] }} ₽</td><td>{{ row['Комментарий'] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

# Мы используем Jinja2, но передаем шаблон как строку
templates = Jinja2Templates(directory=".")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    df = pd.read_csv(DATA_FILE)
    total_income = df[df["Тип"] == "Доход"]["Сумма"].sum()
    total_expense = df[df["Тип"] == "Расход"]["Сумма"].sum()
    balance = total_income - total_expense
    
    df_sorted = df.sort_values("Дата", ascending=False).to_dict(orient="records")
    
    # Рендерим HTML напрямую из строки
    html_content = templates.get_template("index.html").render(
        request=request, 
        total_income=round(total_income, 2), 
        total_expense=round(total_expense, 2), 
        balance=round(balance, 2), 
        transactions=df_sorted
    ) if os.path.exists("templates/index.html") else HTML_TEMPLATE.replace("{{ total_income }}", str(round(total_income, 2))).replace("{{ total_expense }}", str(round(total_expense, 2))).replace("{{ balance }}", str(round(balance, 2))).replace("{% for row in transactions %}", "").replace("{% endfor %}", "")
    
    # Если шаблон не найден, используем костыльный метод (просто возвращаем строку с подставленными данными)
    # Для простоты, давай просто вернем HTML-строку с подставленными данными вручную (без Jinja2 циклов)
    
    # Упрощенный рендеринг (без циклов, просто чтобы работало)
    rows_html = ""
    for row in df_sorted:
        rows_html += f"<tr><td>{row['Дата']}</td><td>{row['Тип']}</td><td>{row['Категория']}</td><td>{row['Сумма']} ₽</td><td>{row['Комментарий']}</td></tr>"
    
    final_html = HTML_TEMPLATE.replace("{{ total_income }}", str(round(total_income, 2)))\
                              .replace("{{ total_expense }}", str(round(total_expense, 2)))\
                              .replace("{{ balance }}", str(round(balance, 2)))\
                              .replace("{% for row in transactions %}", "")\
                              .replace("{% endfor %}", "")\
                              .replace("<tr><td>{{ row['Дата'] }}</td><td>{{ row['Тип'] }}</td><td>{{ row['Категория'] }}</td><td>{{ row['Сумма'] }} ₽</td><td>{{ row['Комментарий'] }}</td></tr>", rows_html)
    
    return HTMLResponse(content=final_html)

@app.post("/add")
def add_transaction(type: str = Form(...), category: str = Form(...), amount: float = Form(...), comment: str = Form("")):
    new_row = pd.DataFrame({
        "Дата": [datetime.now().strftime("%Y-%m-%d")],
        "Тип": [type],
        "Категория": [category],
        "Сумма": [amount],
        "Комментарий": [comment]
    })
    new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    print("Запуск сервера... Откройте http://127.0.0.1:8000 в браузере")
    uvicorn.run(app, host="127.0.0.1", port=8000)