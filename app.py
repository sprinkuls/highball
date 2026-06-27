import os
import sys
import threading

import flask
from flask import Flask, send_file, render_template, abort

import background
from search_model import Search, SearchTerm

app = Flask(__name__)

# shared state for Flask and the background thread; none of this is needed for the program to work,
# it's basically just fun to pass information the background thread has back out to the user via
# the web server responses
shared_state: dict = {
    "status_msg": "INITIAL STATUS MESSAGE",
    "exchange_rate": 1  # JPY to USD
}


@app.route("/favicon.ico")
def favicon():
    return send_file("static/favicon.ico")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("page_not_found.html"), 404


# ====================
# PATHS! ENDPOINTS!
# ====================

@app.route("/")
def index():
    return flask.redirect("/searches")


# ====================

@app.route("/searches")
def searches():
    return render_template("index.html", searches=Search.get_all_searches())


# ====================

@app.route("/searches", methods=["POST"])
def add_search():
    new_id = Search.create_search("", [])
    if new_id is None:
        abort(500)
    else:
        return render_template("table_row.html", search=Search(new_id, "", []))


@app.route("/searches/<search_id>", methods=["PATCH"])
def rename_search(search_id=0):
    pass


@app.route("/searches/<search_id>", methods=["DELETE"])
def remove_search(search_id=0):
    ret = Search.delete_search(search_id)
    if ret is None:
        abort(404)
    else:
        return "", 200


# ====================

@app.route("/searches/<search_id>/terms", methods=["POST"])
def add_term_to_search(search_id=0):
    # need to return html for the new element that has the ID of the
    new_id = Search.create_search_term(search_id, "")
    if new_id is None:
        abort(500)
    else:
        return render_template("term.html", st=SearchTerm(new_id, ""), search_id=search_id)


# ====================

@app.route("/searches/<search_id>/terms/<term_id>", methods=["PATCH"])
def rename_search_term(search_id=0, term_id=0):
    pass


@app.route("/searches/<search_id>/terms/<term_id>", methods=["DELETE"])
def remove_term_from_search(search_id=0, term_id=0):
    ret = Search.delete_search_term(search_id, term_id)
    if ret is None:
        abort(404)
    else:
        return "", 200


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


def add_mock_data():
    Search.create_search("Sony BKE", ["BVE-2000", "BKE-2010", "BVE-900", "BKE-2011", "BVE-9100A"])
    Search.create_search("HHKB Pro 1", ["PD-KB300", "PD-KB300B", "PD-KB300NL", "PD-KB300BN"])
    Search.create_search("JDL", ["jdl eku", "EKUJ5", "EKUJ9", "EKUJ8"])


if __name__ == "__main__":
    print("Hello, __main__!")

    if len(sys.argv) == 2 and sys.argv[1] == "demo":
        try:
            os.remove("searches.db")
        except OSError:
            pass

        Search.init_db()

        print("adding mock data...")
        add_mock_data()

        print("current db contents:")
        all_searches = Search.get_all_searches()
        for x in all_searches:
            print(x)

        test_id = 1
        print(f"removing the search with id {test_id} from the db...")
        if not Search.delete_search(test_id):
            raise Exception

        print("current db contents:")
        all_searches = Search.get_all_searches()
        for x in all_searches:
            print(x)

        print("getting search with id = 1...")
        id_1 = Search.get_search(1)
        print(id_1)

    else:
        try:
            os.remove("searches.db")
        except OSError:
            pass

        print("initializing db...")
        Search.init_db()
        print("adding mock data...")
        add_mock_data()

        print("starting background thread...")
        threading.Thread(target=lambda: background.run(shared_state), daemon=True).start()
        app.run(host="0.0.0.0", port=1070, debug=False)
