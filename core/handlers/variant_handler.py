from core.entities.enums import NetMessage, HashMode
from core.manager import load_from_file
from core.utils import VariantList, hash
from core.ffi import enet_peer_disconnect

class VariantHandler:
    @staticmethod
    def handle(client, data):
        variant_list = VariantList.deserialize(data)
        function_name = variant_list.variants[0].as_string()

        skip = {
            "OnClearItemTransforms",
            "OnSetItemTransform",
            "OnItemVariablesHasChanged",
        }

        if function_name not in skip:
            print(f"Handling variant function: {function_name}")

        match function_name:
            case "OnSendToServer":
                onSendToServer(client, variant_list)
            case "OnSuperMainStartAcceptLogonHrdxs47254722215a":
                onSuperMainStartAcceptLogonHrdxs47254722215a(client, variant_list)
            case "OnConsoleMessage":
                onConsoleMessage(variant_list)

def onSendToServer(client, var):
    port = var.get(1).as_int32()
    token = var.get(2).as_string()
    user_id = var.get(3).as_string()
    server_data = var.get(4).as_string().split('|')
    aat = var.get(5).as_string()

    client.redirected = True
    client.address = server_data[0]
    client.port = port
    client.login_info.token = token
    client.login_info.user = user_id
    client.login_info.door_id = server_data[1]
    client.login_info.uuid = server_data[2]
    client.login_info.aat = aat

    print(f"Redirecting to server {client.address}:{client.port} with token {token} and user ID {user_id}.")
    enet_peer_disconnect(client.peer, 0)

def onSuperMainStartAcceptLogonHrdxs47254722215a(client, var):
    server_hash = var.get(1).as_uint32()

    try:
        with open("cache/items.dat", "rb") as f:
            data = f.read()

        print("items.dat size:", len(data))
        hash_value = hash(data, HashMode.FixedLength, len(data)) & 0xFFFFFFFF

        if hash_value == server_hash:
            client.send_packet(NetMessage.GenericText, "action|enter_game\n")
            client.redirected = False

            try:
                client.items_database = load_from_file("cache/items.dat")
            except Exception as e:
                print(f"Failed to load items.dat: {e}")
                raise

            return

    except FileNotFoundError:
        print("Fetching server items.dat...")

    client.send_packet(NetMessage.GenericText, "action|refresh_item_data\n")

def onConsoleMessage(var):
    message = var.get(1).as_string()
    print(message)