from core.entities.enums import HashMode
from core.utils import hex, mac, generate_klv, hash

class LoginInfo:
    def __init__(self):
        self.tank_id_name = None
        self.tank_id_pass = None
        self.requested_name = None
        self.ltoken = None
        self.token = None
        self.lmode = "1"
        self.f = "1"
        self.protocol = 225
        self.game_version = "5.4"
        self.fz = "21905432"
        self.cbits = "0"
        self.player_age = "20"
        self.gdpr = "2"
        self.category = "_-5100"
        self.total_play_time = "0"
        self.meta = None
        self.fhash = "-716928004"
        self.rid = hex(32, uppercase=True)
        self.platform_id = "0,1,1"
        self.device_version = "0"
        self.country = "us"
        self.mac = mac()
        self.wk = hex(32, uppercase=True)
        self.zf = "-1623530258"
        self.klv = generate_klv(self.protocol, self.game_version, self.rid)
        self.hash = hash(f"{self.mac}RT".encode("ascii"), HashMode.NullTerminated)
        self.hash2 = hash(f"{hex(16, uppercase=True)}RT".encode("ascii"), HashMode.NullTerminated)
        self.uuid = None
        self.user = None
        self.door_id = None
        self.aat = None
        self.fcm_token = None

    def build(self):
        fields = [
            ("tankIDName", self.tank_id_name),
            ("tankIDPass", self.tank_id_pass),
            ("requestedName", self.requested_name),
            ("f", self.f),
            ("protocol", self.protocol),
            ("game_version", self.game_version),
            ("fz", self.fz),
            ("cbits", self.cbits),
            ("player_age", self.player_age),
            ("GDPR", self.gdpr),
            ("FCMToken", self.fcm_token),
            ("category", self.category),
            ("totalPlaytime", self.total_play_time),
            ("klv", self.klv),
            ("hash2", self.hash2),
            ("meta", self.meta),
            ("fhash", self.fhash),
            ("rid", self.rid),
            ("platformID", self.platform_id),
            ("deviceVersion", self.device_version),
            ("country", self.country),
            ("hash", self.hash),
            ("mac", self.mac),
            ("wk", self.wk),
            ("zf", self.zf),
            ("lmode", self.lmode),
        ]
        return "\n".join(f"{k}|{v if v is not None else ''}" for k, v in fields)