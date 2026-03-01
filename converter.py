from flask import Flask, render_template, request, send_file
import pandas as pd
import io

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/procesar", methods=["POST"])
def procesar():

    table = request.form["tabla"]
    action = request.form["accion"]
    file = request.files["archivo"]

    df = pd.read_excel(file)

    queries = []

    for _, row in df.iterrows():

        if action == "insert":
            columns = ", ".join(df.columns)
            values = ", ".join([f"'{str(v)}'" for v in row])
            sql = f"INSERT INTO {table} ({columns}) VALUES ({values});"

        elif action == "update":
            if "id" not in df.columns:
                return "Error: Para UPDATE, el archivo debe contener una columna 'id'.", 400
            set_values = ", ".join(
                [f"{col} = '{row[col]}'" for col in df.columns if col != "id"]
            )
            sql = f"UPDATE {table} SET {set_values} WHERE id = '{row['id']}';"

        queries.append(sql)

    # Unir todas las queries
    contenido_sql = "\n".join(queries)

    # Crear archivo en memoria
    buffer = io.BytesIO()
    buffer.write(contenido_sql.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{table}.sql",
        mimetype="text/sql"
    )


if __name__ == "__main__":
    app.run(debug=True)
