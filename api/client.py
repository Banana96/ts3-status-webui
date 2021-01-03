from ts3.query import TS3ServerConnection

from api.models import *


class QueryClient(TS3ServerConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exec_("use", sid=kwargs.get("sid", 1))

    def get_server_info(self) -> ServerInfo:
        return ServerInfo(self.exec_("serverinfo").parsed[0])

    def get_channels(self) -> [Channel]:
        response = self.exec_("channellist", "flags", "icon").parsed
        return [Channel(ch) for ch in response]

    def get_online_clients(self) -> [Client]:
        response = self.exec_("clientlist", "uid", "away", "voice").parsed
        return [Client(cl) for cl in response if cl["client_type"] is "0"]

    def get_db_clients(self):
        count = int(self.exec_("clientdblist", "count", duration=1).parsed[0]["count"])
        response = self.exec_("clientdblist", duration=count).parsed
        return [DatabaseClient(cl) for cl in response]

    def render(self) -> dict:
        return self.get_server_info().render(
            channels=self.get_channels(),
            clients=[cl for cl in self.get_online_clients()],
            db_clients=self.get_db_clients()
        )
