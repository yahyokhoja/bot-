from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from db import get_connection
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

# Инициализация чат-бота
chatbot = ChatBot(
    "FoodBot",
    read_only=True,
    logic_adapters=[
        "chatterbot.logic.BestMatch",
        "chatterbot.logic.MathematicalEvaluation"
    ]
)

# Обучение чат-бота (один раз при запуске)
corpus_trainer = ChatterBotCorpusTrainer(chatbot)
corpus_trainer.train("chatterbot.corpus.english")

# ======== WEB ROUTES ========

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def get_response():
    user_input = request.form["message"]
    bot_response = str(chatbot.get_response(user_input))
    return jsonify({"response": bot_response})

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "password":
            session["logged_in"] = True
            return redirect(url_for("admin_index"))
        return "Invalid username or password", 403
    return render_template("login.html")

@app.route("/admin")
def admin_index():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    return render_template("admin_index.html")

@app.route("/admin/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin_login"))

@app.route("/admin/orders")
def admin_orders():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, item_name, quantity, status, created_at 
        FROM orders 
        ORDER BY created_at DESC
    """)
    orders = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("orders.html", orders=orders)

@app.route("/admin/users")
def users():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, telegram_id, username, registration_date FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("users.html", users=users)

@app.route("/admin/settings", methods=["GET", "POST"])
def settings():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        new_name = request.form.get("name")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_settings SET name = %s WHERE id = 1", (new_name,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("settings"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM bot_settings WHERE id = 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    bot_name = row[0] if row else "FoodBot"
    return render_template("settings.html", bot_name=bot_name)

# ======== Функция для сохранения заказа и пользователя ========

def save_order(telegram_id, username, item_name, quantity):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Проверяем, есть ли пользователь
        cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        user = cursor.fetchone()

        # Если пользователя нет — создаём
        if user is None:
            cursor.execute("""
                INSERT INTO users (telegram_id, username, registration_date)
                VALUES (%s, %s, NOW())
                RETURNING id
            """, (telegram_id, username))
            user_id = cursor.fetchone()[0]
        else:
            user_id = user[0]

        # Сохраняем заказ
        cursor.execute("""
            INSERT INTO orders (user_id, item_name, quantity, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, item_name, quantity))

        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success"}, 201

    except psycopg2.errors.NumericValueOutOfRange:
        return {"error": "Значение слишком большое для integer поля"}, 400
    except Exception as e:
        return {"error": str(e)}, 500

# ======== API ========

@app.route('/api/orders', methods=['POST'])
def api_orders():
    data = request.get_json()
    try:
        telegram_id = int(data.get('user_id'))
        username = data.get('username', 'unknown')  # обязательно передавать username
        item_name = data.get('item_name')
        quantity = int(data.get('quantity'))
    except (ValueError, TypeError):
        return jsonify({"error": "Некорректные данные"}), 400

    result, status_code = save_order(telegram_id, username, item_name, quantity)
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True)
