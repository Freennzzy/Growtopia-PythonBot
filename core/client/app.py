import ctypes
from core.ffi import enet_host_create, enet_host_use_crc32, enet_host_use_new_packet, enet_host_compress_with_range_coder, ENetAddress, enet_address_set_host, enet_host_connect, enet_host_service, ENetEvent, ENetEventType, ENetPacket, enet_packet_create, enet_peer_disconnect, enet_peer_send, enet_packet_destroy
from .inventory import Inventory
from .login_info import LoginInfo
from .login import fetch_login_urls, login_via_growid
from .server_data import fetch_server_data
from core.entities.enums import LoginMethod, NetMessage
from core.handlers import NetMessageHandler
from core.manager import World

class Bot:
    def __init__(self, login_method=LoginMethod.LEGACY, username=None, password=None, items_database=None):
        if login_method is LoginMethod.LEGACY and (username is None or password is None):
            raise ValueError("Username and password must be provided for LEGACY login method.")

        self.address = None
        self.port = None
        self.redirected = False
        self.login_method = login_method
        self.username = username
        self.password = password
        self.login_info = LoginInfo()
        self.login_urls = None
        self.items_database = items_database
        self.inventory = Inventory()
        self.world = World.new()
        self.peer = None
        self.host = enet_host_create(None, 1, 2, 0, 0)

        if self.host is None:
            print("An error occurred while trying to create an ENet client host.")
            return

        enet_host_use_new_packet(self.host)
        enet_host_use_crc32(self.host)
        enet_host_compress_with_range_coder(self.host)

    def connect(self):
        if self.redirected:
            enet_addr = ENetAddress()
            if enet_address_set_host(ctypes.byref(enet_addr), self.address.encode('utf-8')) != 0:
                print("Failed to set host address.")
                return
            enet_addr.port = int(self.port)
        else:
            server_data = fetch_server_data(self.login_info.protocol, self.login_info.game_version)
            self.login_info.meta = server_data['meta']
            self.login_urls = fetch_login_urls(self.login_info.build())
            self.login_info.ltoken = login_via_growid(self.login_urls['growtopia'], self.username, self.password)

            enet_addr = ENetAddress()
            if enet_address_set_host(ctypes.byref(enet_addr), server_data['server'].encode('utf-8')) != 0:
                print("Failed to set host address.")
                return
            enet_addr.port = int(server_data['port'])

        self.peer = enet_host_connect(self.host, ctypes.byref(enet_addr), 2, 0)
        if self.peer is None:
            print("Failed to create a connection to the server.")
        
        self.loop()

    def loop(self):
        event = ENetEvent()
        while True:
            if enet_host_service(self.host, ctypes.byref(event), 250) > 0:
                match event.type:
                    case ENetEventType.CONNECT:
                        print("Connected to server.")
                    case ENetEventType.RECEIVE:
                        packet = ctypes.cast(event.packet, ctypes.POINTER(ENetPacket)).contents
                        NetMessageHandler.handle(self, packet)
                        enet_packet_destroy(event.packet)
                    case ENetEventType.DISCONNECT:
                        print("Disconnected from server.")
                        if self.redirected:
                            print("Redirecting to redirected server...")
                        self.connect()
                        break
                    case ENetEventType.DISCONNECT_TIMEOUT:
                        print("Connection timed out.")
                        break

    def disconnect(self):
        enet_peer_disconnect(self.peer, 0)

    def send_packet(self, packet_type, data):
        packet = enet_packet_create(None, 4 + len(data), 1)
        packet_type_ptr = ctypes.cast(packet.contents.data, ctypes.POINTER(ctypes.c_uint32))
        packet_type_ptr[0] = packet_type.value
        data_start = ctypes.addressof(packet.contents.data.contents) + 4
        ctypes.memmove(data_start, data.encode("utf-8"), len(data))
        if enet_peer_send(self.peer, 0, packet) < 0:
            print("Failed to send packet.")
        else:
            print(f"Sent packet of type: {packet_type.name}")

    def send_packet_raw(self, tank_packet):
        packet = enet_packet_create(None, 4 + ctypes.sizeof(tank_packet) + tank_packet.extended_data_length, 1)
        packet_type_ptr = ctypes.cast(packet.contents.data, ctypes.POINTER(ctypes.c_uint32))
        packet_type_ptr[0] = NetMessage.GamePacket.value
        data_start = ctypes.addressof(packet.contents.data.contents) + 4
        ctypes.memmove(data_start, ctypes.byref(tank_packet), ctypes.sizeof(tank_packet))
        if enet_peer_send(self.peer, 0, packet) < 0:
            print("Failed to send raw packet.")
        else:
            print("Sent raw packet successfully.")

    def warp(self, world_name: str):
        self.send_packet(NetMessage.GameMessage, f"action|join_request\nname|{world_name}\ninvitedWorld|0\n")

    def leave(self):
        self.send_packet(NetMessage.GameMessage, "action|quit_to_exit\n")