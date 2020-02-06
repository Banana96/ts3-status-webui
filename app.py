from datetime import datetime, timedelta
from os import environ as env
from flask import *
from ts3.query import TS3Connection


def get_ts3_connection():
    conn = TS3Connection(
        host=env.get("TS3_HOSTNAME", "localhost"),
        port=env.get("TS3_PORT", 10011)
    )

    conn.login(
        client_login_name=env.get("TS3_USER", "serveradmin"),
        client_login_password=env.get("TS3_PASSWORD", "")
    )

    conn.use(sid=env.get("TS3_SID", 1))

    return conn


def get_client_dict(clid, clients):
    client = [cl for cl in clients if cl["clid"] == clid]

    if len(client) == 0:
        return {}

    client = client[0]

    return {"name": client["client_nickname"]}


def get_channel_dict(cid, channels, clients):
    channel = [c for c in channels if c["cid"] == cid]

    if len(channel) == 0:
        return {}

    channel = channel[0]

    sub_cids = [c["cid"] for c in channels if c["pid"] == cid]

    channel_data = {
        "name": channel["channel_name"],
        "subchannels": [get_channel_dict(sub_cid, channels, clients) for sub_cid in sub_cids],
        "clients": [get_client_dict(cl["clid"], clients) for cl in clients if cl["cid"] == cid]
    }

    if len(channel_data["clients"]) == 0:
        channel_data.pop("clients")

    if len(channel_data["subchannels"]) == 0:
        channel_data.pop("subchannels")

    return channel_data


app = Flask(__name__)
fetch_time = datetime(1970, 1, 1)
conn_data = {}


@app.route("/")
def index():
    global fetch_time, conn_data

    if datetime.now() - fetch_time >= timedelta(seconds=10):
        with get_ts3_connection() as conn:
            self_clid = conn.whoami().parsed[0]["client_id"]
            svinfo = conn.serverinfo().parsed[0]
            channels = conn.channellist().parsed
            clients = (c for c in conn.clientlist().parsed if c['clid'] != self_clid)

            fetch_time = datetime.now()

            root_cids = [c["cid"] for c in channels if c["pid"] == "0"]

            conn_data = {
                "server": {
                    "name": svinfo["virtualserver_name"],
                    "platform": svinfo["virtualserver_platform"],
                    "version": svinfo["virtualserver_version"],
                    "channels": [get_channel_dict(cid, channels, clients) for cid in root_cids],
                },
                "fetch_time": fetch_time.strftime("%Y-%d-%m %H:%M:%S")
            }

    if request.args.get("format", "") == "json":
        return jsonify(conn_data)

    return render_template("index.html", **conn_data)


if __name__ == "__main__":
    app.run()
