from datetime import datetime, timedelta
from os import environ as env
from flask import *
from ts3.query import TS3ServerConnection

from ts_client import QueryClient

app = Flask(__name__)
fetch_time = datetime(1970, 1, 1)
conn_data = {}


def get_ts3_connection():
    ssh = env.get("TS3_USE_SSH", "false").lower() in ("true", "1", "yes")
    user = env.get("TS3_USER", "serveradmin")
    pwd = env.get("TS3_PASSWORD", "")
    host = env.get("TS3_HOSTNAME", "localhost")
    port = env.get("TS3_PORT", "10011")
    sid = env.get("TS3_SID", "1")

    conn_str = f"{'ssh' if ssh else 'telnet'}://{user}:{pwd}@{host}:{port}"

    conn = TS3ServerConnection(conn_str)
    conn.exec_("use", sid=sid)

    return conn


@app.route("/")
def index():
    global fetch_time, conn_data

    if datetime.now() - fetch_time >= timedelta(seconds=1):
        with get_ts3_connection() as conn:
            qc = QueryClient(conn)

            fetch_time = datetime.now()

            conn_data = {
                "server": qc.render(),
                "fetch_time": fetch_time.strftime("%Y-%d-%m %H:%M:%S")
            }

    if request.args.get("format", "") == "json":
        return jsonify(conn_data)

    return render_template("index.html", **conn_data)


if __name__ == "__main__":
    app.run()
