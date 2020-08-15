from datetime import datetime


class ParsedResponse:
    def __init__(self, content=None):
        self.__content = content if content is not None else {}

    def get_str(self, item, default=None):
        return self.__content.get(item, default)

    def get_int(self, item):
        return int(self.get_str(item, 0))

    def get_bool(self, item):
        return bool(self.get_int(item))

    def get_datetime(self, item):
        return datetime.fromtimestamp(self.get_int(item))

    def __repr__(self):
        return repr(self.__content)


class Client(ParsedResponse):
    @property
    def client_id(self) -> int:
        return self.get_int("clid")

    @property
    def channel_id(self) -> int:
        return self.get_int("cid")

    @property
    def db_id(self) -> int:
        return self.get_int("client_database_id")

    @property
    def name(self) -> str:
        return self.get_str("client_nickname")

    @property
    def client_type(self) -> int:
        return self.get_int("client_type")

    @property
    def afk(self) -> bool:
        in_mute = self.get_int("client_input_muted")
        out_mute = self.get_int("client_output_muted")
        away = self.get_int("client_away")

        return in_mute + out_mute + away > 0

    def render(self) -> dict:
        return {
            "id": self.client_id,
            "db_id": self.db_id,
            "name": self.name,
            "type": self.client_type,
            "afk": self.afk,
        }

    def __str__(self):
        return self.name


class DatabaseClient(Client):
    @property
    def db_id(self) -> int:
        return self.get_int("cldbid")

    @property
    def first_visit(self) -> datetime:
        return self.get_datetime("client_created")
    
    @property
    def last_visit(self) -> datetime:
        return self.get_datetime("client_lastconnected")

    def render(self) -> dict:
        base_render = super().render()

        return {
            **base_render,
            "db_id": self.db_id,
            "last_visit": self.last_visit
        }


class Channel(ParsedResponse):
    @property
    def channel_id(self) -> int:
        return int(self.get_str("cid"))

    @property
    def parent_ch_id(self) -> int:
        return int(self.get_str("pid"))

    @property
    def name(self) -> str:
        return self.get_str("channel_name")

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
        return self.get_str("virtualserver_name")

    @property
    def client_port(self):
        return int(self.get_str("virtualserver_port"))

    def _render_recent_clients(self, clients, db_clients) -> list:
        online_db_ids = [cl.db_id for cl in clients]

        sorted_db_clients = sorted(
            db_clients,
            key=lambda cl: cl.last_visit,
            reverse=True
        )

        recent_clients = []
        dt_now = datetime.now()

        for db_cl in sorted_db_clients[:10]:
            online_time = None

            if db_cl.db_id in online_db_ids:
                online_time = dt_now - db_cl.last_visit

            recent_clients.append({
                "name": db_cl.name,
                "last_visit": db_cl.last_visit,
                "online_time": online_time,
            })

        return recent_clients

    def render(self, channels, clients, db_clients) -> dict:
        root_chs = [ch for ch in channels if ch.parent_ch_id == 0]

        ch_render = [ch.render(channels, clients) for ch in root_chs]
        ch_render = [ch for ch in ch_render if ch["rm_mark"] is False]

        last_clients = self._render_recent_clients(clients, db_clients)

        return {
            "name": self.name,
            "channels": ch_render,
            "last_clients": last_clients
        }

    def __str__(self):
        return self.name
