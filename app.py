import flask
from flask import Flask, send_file, render_template

app = Flask(__name__)


@app.route("/index.html")
def index_dot_html():
    return flask.redirect("/")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return send_file("static/favicon.ico")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1070)
