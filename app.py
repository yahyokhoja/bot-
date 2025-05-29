from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Не забудь сменить на безопасный ключ

# Инициализация чат-бота
chatbot = ChatBot(
    "FoodBot",
    read_only=True,
    logic_adapters=[
        "chatterbot.logic.BestMatch",
        "chatterbot.logic.MathematicalEvaluation"
    ]
)

# Обучение на стандартном корпусе
corpus_trainer = ChatterBotCorpusTrainer(chatbot)
corpus_trainer.train("chatterbot.corpus.english")

# ======== WEB ROUTES ========

# Главная страница с ботом
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Получение ответа от бота
@app.route("/", methods=["POST"])
def get_response():
    user_input = request.form["message"]
    bot_response = str(chatbot.get_response(user_input))
    return jsonify({"response": bot_response})

# ======== ADMIN PANEL ========

# Авторизация администратора
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username == "admin" and password == "password":  # Пример, не использовать в проде
            session["logged_in"] = True
            return redirect(url_for("admin_index"))
        else:
            return "Invalid username or password", 403

    return render_template("login.html")

# Главная страница админки
@app.route("/admin", methods=["GET"])
def admin_index():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    return render_template("admin_index.html")

# Выход из админки
@app.route("/admin/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("admin_login"))

# Просмотр пользователей
@app.route("/admin/users", methods=["GET"])
def users():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template("users.html", users=users)

# Настройки бота
@app.route("/admin/settings", methods=["GET", "POST"])
def settings():
    # Проверяем, авторизован ли админ
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    
    if request.method == "POST":
        new_name = request.form.get("name")

        # Обновляем имя бота в базе
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute("UPDATE bot_settings SET name = ? WHERE id = 1", (new_name,))
        conn.commit()
        conn.close()

        return redirect(url_for("settings"))

    # GET: получаем текущее имя из базы
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM bot_settings WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    bot_name = row[0] if row else "FoodBot"

    return render_template("settings.html", bot_name=bot_name)
# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)
