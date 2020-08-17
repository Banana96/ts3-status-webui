from datetime import datetime, timedelta
from os import environ as env

from flask import Flask, request, jsonify, render_template

from ts.query import get_query
from .utils import format_td, format_diff

app = Flask(__name__)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.add_template_filter(format_td, "td2str")
app.add_template_filter(format_diff, "diff2str")

fetch_time = datetime(1970, 1, 1)
server_state = {}


@app.route("/")
def index():
    global fetch_time, server_state

    if datetime.now() - fetch_time >= timedelta(seconds=5):
        fetch_time = datetime.now()

        with get_query() as qc:
            server_state = {
                "server": qc.render(),
                "fetch_time": fetch_time.strftime("%Y-%d-%m %H:%M:%S")
            }

    if request.args.get("format", "") == "json":
        return jsonify(server_state)

    return render_template("index.html", **{
        **server_state,
        "ts3_addr": env.get("TS3_HOSTNAME", "localhost")
    })


if __name__ == "__main__":
    app.run()
