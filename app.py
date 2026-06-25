import threading

import flask
from flask import Flask, send_file, render_template

import background
from search_model import Search

app = Flask(__name__)

# shared state for Flask and the background thread; none of this is needed for the program to work,
# it's basically just fun to pass information the background thread has back out to the user via
# the web server responses
shared_state: dict = {
    "status_msg": "INITIAL STATUS MESSAGE",
    "exchange_rate": 1  # JPY to USD
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


@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html")


# ====================
# FUN
# ====================

@app.route("/status_msg")
def status_msg():
    return shared_state["status_msg"]


@app.route("/exchange_rate")
def exchange_rate():
    if exchange_rate == 0:
        return "0"
    else:
        return str(round(1 / shared_state["exchange_rate"], 2))


def add_sample_data():
    Search.create_search("HHKB Pro 1", ["PD-KB300", "PD-KB300B", "PD-KB300NL", "PD-KB300BN"])
    Search.create_search("Sony BKE", ["BVE-2000", "BKE-2010", "BVE-900", "BKE-2011", "BVE-9100A"])
    Search.create_search("JDL", ["jdl eku", "EKUJ5", "EKUJ9", "EKUJ8"])


if __name__ == "__main__":
    t_background = threading.Thread(target=lambda: background.run(shared_state), daemon=True)
    t_flask = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=1070, debug=False), daemon=True)

    t_background.start()
    t_flask.start()

    # uncomment this later
    t_flask.join()
    # while True:
    #     print(f"Background Status: {shared_state["status_msg"]}")
    #     sleep(1)

    # you can also just do this if the web server is the last thing you need to run, i think:
    # app.run(host="0.0.0.0", port=1070, debug=False)
