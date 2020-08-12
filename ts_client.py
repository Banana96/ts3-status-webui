class ParsedResponse:
    def __init__(self, content=None):
        self.__content = content if content is not None else {}

    def get(self, item):
        return self.__content.get(item, None)

    def __repr__(self):
        return repr(self.__content)


class Client(ParsedResponse):
    @property
    def client_id(self) -> int:
        return int(self.get("clid"))

    @property
    def channel_id(self) -> int:
        return int(self.get("cid"))

    @property
    def db_id(self):
        return int(self.get("client_database_id"))

    @property
    def name(self) -> str:
        return self.get("client_nickname")

    @property
    def client_type(self):
        return int(self.get("client_type"))

    @property
    def afk(self):
        in_mute = int(self.get("client_input_muted"))
        out_mute = int(self.get("client_output_muted"))
        away = int(self.get("client_away"))

        return in_mute + out_mute + away > 0

    def render(self) -> dict:
        return {
            "id": self.client_id,
            "name": self.name,
            "type": self.client_type,
            "afk": self.afk,
        }

    def __str__(self):
        return self.name


class Channel(ParsedResponse):
    @property
    def channel_id(self) -> int:
        return int(self.get("cid"))

    @property
    def parent_ch_id(self) -> int:
        return int(self.get("pid"))

    @property
    def name(self) -> str:
        return self.get("channel_name")

    def render(self, channels, clients) -> dict:
        subs = [sub for sub in channels if sub.parent_ch_id == self.channel_id]
        cls = [cl for cl in clients if cl.channel_id == self.channel_id]

        ch_render = [sub.render(channels, clients) for sub in subs]
        ch_render = [ch for ch in ch_render if ch.get("rm_mark", False) is False]

        cl_render = [cl.render() for cl in cls]

        rm_mark = len(ch_render) == 0 and len(cl_render) == 0

        return {
            "id": self.channel_id,
            "parent_id": self.parent_ch_id,
            "name": self.name,
            "subchannels": ch_render,
            "clients": cl_render,
            "rm_mark": rm_mark
        }

    def __str__(self):
        return self.name


class ServerInfo(ParsedResponse):
    @property
    def name(self):
        return self.get("virtualserver_name")

    @property
    def client_port(self):
        return int(self.get("virtualserver_port"))

    def render(self, channels, clients) -> dict:
        root_chs = [ch for ch in channels if ch.parent_ch_id == 0]

        ch_render = [ch.render(channels, clients) for ch in root_chs]
        ch_render = [ch for ch in ch_render if ch["rm_mark"] is False]

        return {
            "name": self.name,
            "channels": ch_render
        }

    def __str__(self):
        return self.name


class QueryClient:
    def __init__(self, connection, sid=1):
        connection.exec_("use", sid=sid)
        self.conn = connection

    def get_own_client_id(self) -> int:
        return int(self.conn.exec_("whoami").parsed[0]["client_id"])

    def get_server_info(self) -> ServerInfo:
        return ServerInfo(self.conn.exec_("serverinfo").parsed[0])

    def get_channels(self) -> [Channel]:
        kwargs = {x: True for x in ["flags", "icon"]}
        response = self.conn.exec_("channellist", **kwargs).parsed
        return [Channel(c) for c in response]

    def get_clients(self) -> [Client]:
        response = self.conn.exec_("clientlist", "uid", "away", "voice", "times", "country").parsed
        return [Client(r) for r in response]

    def render(self) -> dict:
        return self.get_server_info().render(
            channels=self.get_channels(),
            clients=self.get_clients()
        )
