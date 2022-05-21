# Multicast sender
# Guidance:  https://stackoverflow.com/a/1794373
import socket

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
# MESSAGE = b'Hello, Multicast!'

# regarding socket.IP_MULTICAST_TTL
# ---------------------------------
# for all packets sent, after two hops on the network the packet will not
# be re-sent/broadcast (see https://www.tldp.org/HOWTO/Multicast-HOWTO-6.html)
MULTICAST_TTL = 2

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)


while True:
    MESSAGE = input("Introduzca el mensaje: ").encode("utf-8")
    sock.sendto(MESSAGE, (MCAST_GRP, MCAST_PORT))