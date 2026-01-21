from core.client import Bot
from core.manager import load_from_file
from core.ffi import  enet_initialize

if enet_initialize() != 0:
    print("Failed to initialize ENet.")

if __name__ == "__main__":
    print("Enter your legacy account:")
    username = input("Input your GrowID: ")
    password = input("Input your password: ")

    items_database = load_from_file("cache/items.dat")

    bot = Bot(username=username, password=password, items_database=items_database)
    bot.connect()