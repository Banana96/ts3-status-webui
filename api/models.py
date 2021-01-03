from datetime import datetime

from django.conf import settings


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
    def has_input_disabled(self) -> bool:
        return self.get_bool("client_input_muted")

    @property
    def has_output_disabled(self):
        return self.get_bool("client_output_muted")

    @property
    def has_input_muted(self) -> bool:
        return self.get_bool("client_input_muted")

    @property
    def has_output_muted(self):
        return self.get_bool("client_output_muted")

    @property
    def is_away(self):
        return self.get_bool("client_away")

    @property
    def is_talking(self) -> bool:
        return self.get_bool("client_flag_talking")

    def render(self) -> dict:
        return {
            "id": self.client_id,
            "db_id": self.db_id,
            "name": self.name,
            "type": self.client_type,
            "input_muted": self.has_input_muted,
            "output_muted": self.has_output_muted,
            "talking": self.is_talking,
            "away": self.is_away,
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

    @property
    def is_default(self) -> bool:
        return self.get_bool("channel_flag_default")

    def render(self, clients) -> dict:
        cls = [cl for cl in clients if cl.channel_id == self.channel_id]
        cl_render = [cl.render() for cl in cls]

        return {
            "id": self.channel_id,
            "parent_id": self.parent_ch_id,
            "name": self.name,
            "clients": cl_render,
            "is_default": self.is_default,
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

        for db_cl in sorted_db_clients[:settings.TS3_TOPLIST_LEN]:
            online_time = None

            if db_cl.db_id in online_db_ids:
                online_time = dt_now - db_cl.last_visit

            recent_clients.append({
                **db_cl.render(),
                "online_time": online_time,
            })

        return sorted(
            recent_clients,
            key=lambda cl: cl["online_time"] is None
        )

    def render(self, channels, clients, db_clients) -> dict:
        return {
            "name": self.name,
            "channels": [ch.render(clients) for ch in channels],
            "last_clients": self._render_recent_clients(clients, db_clients)
        }

    def __str__(self):
        return self.name
