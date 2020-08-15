from os import environ as env
from datetime import datetime, timedelta
from flask import Flask, request, g, jsonify, render_template

from ts.query import get_query
from .utils import format_td, format_diff

app = Flask(__name__)

app.add_template_filter(format_td, "td2str")
app.add_template_filter(format_diff, "diff2str")


@app.route("/")
def index():
    if "fetch_time" not in g:
        g.fetch_time = datetime(1970, 1, 1)

    if datetime.now() - g.fetch_time >= timedelta(seconds=5):
        with get_query() as qc:
            g.fetch_time = datetime.now()

            g.server_state = {
                "server": qc.render(),
                "fetch_time": g.fetch_time.strftime("%Y-%d-%m %H:%M:%S")
            }

    if request.args.get("format", "") == "json":
        return jsonify(g.server_state)

    return render_template("index.html", **{
        **g.server_state,
        "ts3_addr": env.get("TS3_HOSTNAME", "localhost")
    })


if __name__ == "__main__":
    app.run()
