from SocketUtils.general import ServerInfo
from entities import User

def main():
    print("Welcome to Python Chat Room!")
    server_add = input("Enter your server address: ")
    server_port = int(input("Enter your server port: "))

    server_info = ServerInfo(server_add, server_port)
    username = input("Enter Username: ")
    paraphrase = input("Enter Paraphrase: ")
    client = User(username=username, paraphrase=paraphrase, server_info=server_info)



if __name__ == "__main__":
    main()