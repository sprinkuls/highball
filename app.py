import threading

import flask
from flask import Flask, send_file, render_template

import background

app = Flask(__name__)

shared_state: dict = {
    "status_msg": "INITIAL STATUS MESSAGE",
}


@app.route("/index.html")
def index_dot_html():
    return flask.redirect("/")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return send_file("static/favicon.ico")


# ====================
# FUN
# ====================

@app.route("/status_msg")
def status_msg():
    return shared_state["status_msg"]


@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html")


if __name__ == "__main__":
    t_flask = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=1070, debug=False), daemon=True)
    t_background = threading.Thread(target=lambda: background.run(shared_state), daemon=True)

    t_flask.start()
    t_background.start()

    # uncomment this later
    t_flask.join()
    # while True:
    #     print(f"Background Status: {shared_state["status_msg"]}")
    #     sleep(1)

    # you can also just do this if the web server is the last thing you need to run, i think:
    # app.run(host="0.0.0.0", port=1070, debug=False)
