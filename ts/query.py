from os import environ as env
from ts3.query import TS3ServerConnection

from .responses import *


class QueryClient(TS3ServerConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exec_("use", sid=kwargs.get("sid", 1))

    def get_own_client_id(self) -> int:
        return int(self.exec_("whoami").parsed[0]["client_id"])

    def get_server_info(self) -> ServerInfo:
        return ServerInfo(self.exec_("serverinfo").parsed[0])

    def get_channels(self) -> [Channel]:
        response = self.exec_("channellist", "flags", "icon").parsed
        return [Channel(ch) for ch in response]

    def get_online_clients(self) -> [Client]:
        response = self.exec_("clientlist", "uid", "away", "voice").parsed
        return [Client(cl) for cl in response]

    def get_db_clients(self):
        count = int(self.exec_("clientdblist", "count", duration=1).parsed[0]["count"])
        response = self.exec_("clientdblist", duration=count).parsed
        return [DatabaseClient(cl) for cl in response]

    def render(self) -> dict:
        own_id = self.get_own_client_id()

        return self.get_server_info().render(
            channels=self.get_channels(),
            clients=[cl for cl in self.get_online_clients() if cl.client_id != own_id],
            db_clients=self.get_db_clients()
        )


def ts3_uri_from_env():
    ssh = env.get("TS3_USE_SSH", "false").lower() in ("true", "1", "yes")
    proto = "ssh" if ssh else "telnet"

    user = env.get("TS3_USER", "serveradmin")
    pwd = env.get("TS3_PASSWORD", "")

    host = env.get("TS3_HOSTNAME", "localhost")
    port = env.get("TS3_PORT", "10011")

    return f"{proto}://{user}:{pwd}@{host}:{port}"


def get_query():
    return QueryClient(ts3_uri_from_env())
