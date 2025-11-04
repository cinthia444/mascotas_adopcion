from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")


MONGO_URI = os.environ.get(
    "MONGO_URI", "mongodb+srv://lopezkucinthializethcbtis272_db_user:celuse7810@mascotas.pjrarpn.mongodb.net/mascotas")

try:
   
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=False,
        serverSelectionTimeoutMS=10000
    )
    db = client.get_default_database()
    print("Conexión segura establecida con MongoDB Atlas")
except Exception as e:
   
    print("Conexión segura falló, intentando modo escolar...")
try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=10000
    )
    db = client.get_default_database()
    print(" Conexión establecida con MongoDB Atlas (modo escolar sin SSL)")
except Exception as e:
    db = None
    print(" No se pudo conectar con MongoDB Atlas:", e)


@app.route("/")
def index():
    if db is None:
        flash("Error al obtener datos: la base de datos no está conectada.", "danger")
        return render_template("index.html", datos=[])
    try:
        datos = db.registros.find()
    except Exception as e:
        flash(f"Error al obtener datos: {e}", "danger")
        datos = []
    return render_template("index.html", datos=datos)

@app.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        campo1 = request.form.get("campo1", "").strip()
        campo2 = request.form.get("campo2", "").strip()

        if not campo1 or not campo2:
            flash("Completa todos los campos.", "danger")
            return redirect(url_for("create"))

        if db is not None:
            db.registros.insert_one({
                "campo1": campo1,
                "campo2": campo2
            })
            flash("Registro creado correctamente.", "success")
        else:
            flash("Error: Base de datos no conectada.", "danger")

        return redirect(url_for("index"))
    return render_template("create.html")

@app.route("/view/<id>")
def view(id):
    if db is None:
        flash("Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    dato = db.registros.find_one({"_id": ObjectId(id)})
    if not dato:
        flash("Registro no encontrado.", "warning")
        return redirect(url_for("index"))
    return render_template("view.html", dato=dato)

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    if db is None:
        flash("Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    dato = db.registros.find_one({"_id": ObjectId(id)})
    if not dato:
        flash("Registro no encontrado.", "warning")
        return redirect(url_for("index"))

    if request.method == "POST":
        campo1 = request.form.get("campo1", "").strip()
        campo2 = request.form.get("campo2", "").strip()

        if not campo1 or not campo2:
            flash("Completa todos los campos.", "danger")
            return redirect(url_for("edit", id=id))

        db.registros.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"campo1": campo1, "campo2": campo2}}
        )
        flash("Registro actualizado.", "info")
        return redirect(url_for("index"))

    return render_template("edit.html", dato=dato)

@app.route("/delete/<id>", methods=["POST"])
def delete(id):
    if db is None:
        flash("Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    db.registros.delete_one({"_id": ObjectId(id)})
    flash("Registro eliminado.", "secondary")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)


try:
    from datetime import datetime
    @app.context_processor
    def inject_current_year():
        return {'current_year': datetime.now().year}
except Exception:
    pass
