from flask import Flask, render_template, request, redirect, session, url_for
from flask_bootstrap import Bootstrap
import qrcode
import os
import json

# Configuração do Flask
app = Flask(__name__)
app.secret_key = "sua_chave_secreta"  # Necessário para sessões
Bootstrap(app)

# Nome do arquivo de armazenamento
DATA_FILE = "tasks.json"

# Carregar tarefas do arquivo JSON
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Salvar tarefas no arquivo JSON
def save_tasks(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

tasks_db = load_tasks()  # Banco de dados em memória

# Página inicial (com autenticação)
@app.route("/", methods=["GET", "POST"])
def todo_list():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    global tasks_db

    # Pega ou inicializa as tarefas do usuário
    tasks = tasks_db.get(user, [])

    if request.method == "POST":
        new_task = request.form.get("task")
        if new_task:
            tasks.append(new_task)
            tasks_db[user] = tasks
            save_tasks(tasks_db)
        return redirect("/")
    return render_template("todo.html", tasks=tasks, user=user)

# Remover tarefa
@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    global tasks_db

    tasks = tasks_db.get(user, [])
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        tasks_db[user] = tasks
        save_tasks(tasks_db)
    return redirect("/")

# Página de QR Code
@app.route("/qrcode")
def generate_qrcode():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    list_url = request.url_root
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(list_url)
    qr.make(fit=True)
    img_path = f"static/{user}_qrcode.png"
    os.makedirs("static", exist_ok=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(img_path)
    return render_template("qrcode.html", user=user)

# Login do usuário
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        if user:
            session["user"] = user
            return redirect("/")
    return render_template("login.html")

# Logout do usuário
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
