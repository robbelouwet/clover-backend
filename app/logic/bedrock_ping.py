import json
import random
import socket


def ping_unconnected_bedrock(host, port):
    ping_id = random.randbytes(8)
    msg = b"\x01" + \
          ping_id + \
          b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78" + \
          b"\x00\x00\x00\x00\x00\x00\x00\x00"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg, (host, port))

    sock.settimeout(30.0)
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    parts = str(data).split(';')
    return {
        "gameId": parts[0],
        "description": parts[1],
        "protocolVersion": parts[2],
        "gameVersion": parts[3],
        "currentPlayers": parts[4],
        "maxPlayers": parts[5],
        "name": parts[7],
        "mode": parts[8]
    }


if __name__ == "__main__":
    print(json.dumps(ping_unconnected_bedrock(
        "dns-citroen.fmejaneph2d5cnb8.westeurope.azurecontainer.io",
        25565
    ), indent=4))

# {
#     "gameId": "b'\\x1c\\xa9\\x10\\xb1+\\xc78\\xbcp\\xa7N\\xee\\xed+|\\x1c\\x92\\x00\\xff\\xff\\x00\\xfe\\xfe\\xfe\\xfe\\xfd\\xfd\\xfd\\xfd\\x124Vx\\x00[MCPE",
#     "description": "Dedicated Server",
#     "protocolVersion": "662",
#     "gameVersion": "1.20.71",
#     "currentPlayers": "0",
#     "maxPlayers": "10",
#     "name": "world",
#     "mode": "Survival"
# }
