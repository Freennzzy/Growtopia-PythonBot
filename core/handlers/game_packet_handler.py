import ctypes
import zlib
from .variant_handler import VariantHandler
from core.entities.enums import NetGamePacket, NetMessage
from core.manager import load_from_file
from core.ffi import TankPacket

class GamePacketHandler:
    @staticmethod
    def handle(client, packet):
        tank_data_ptr = ctypes.cast(packet, ctypes.POINTER(TankPacket))
        tank_data = tank_data_ptr.contents
        tank_type = NetGamePacket(tank_data.type)
        extended_data = ctypes.string_at(packet + ctypes.sizeof(TankPacket), tank_data.extended_data_length)

        match tank_type:
            case NetGamePacket.CallFunction:
                onCallFunction(client, extended_data)
            case NetGamePacket.SendMapData:
                onSendMapData(client, extended_data)
            case NetGamePacket.SendInventoryState:
                onSendInventoryState(client, extended_data)
            case NetGamePacket.SendItemDatabaseData:
                onSendItemDatabaseData(client, extended_data)
            case NetGamePacket.PingRequest:
                onPingRequest(client, tank_data)

def onCallFunction(client, data):
    VariantHandler.handle(client, data)

def onSendMapData(client, data):
    with open("cache/world.dat", "wb") as f:
        f.write(data)

    try:
        client.world.parse(data, client.items_database)
    except Exception as e:
        print(f"Failed to parse world: {e}")
        raise

def onSendInventoryState(client, data):
    client.inventory.parse(data)

def onSendItemDatabaseData(client, data):
    decoder = zlib.decompress(data)
    with open("cache/items.dat", "wb") as f:
        f.write(decoder)

    client.send_packet(NetMessage.GenericText, "action|enter_game\n")
    client.redirected = False

    try:
        client.items_database = load_from_file("cache/items.dat")
    except Exception as e:
        print(f"Failed to load items.dat: {e}")
        raise

def onPingRequest(client, data):
    print("Received PingRequest, sending PingReply.")
    tank_packet = TankPacket()
    tank_packet.type = NetGamePacket.PingReply.value
    tank_packet.vector_x = 64.0
    tank_packet.vector_y = 64.0
    tank_packet.vector_x2 = 1000.0
    tank_packet.vector_y2 = 250.0
    tank_packet.value = data.value + 5000
    client.send_packet_raw(tank_packet)