import socket
import struct
import sys
import os

#message = input("Enter message: ").encode("utf-8")
multicast_group = ('224.3.29.71', 10000)

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set a timeout so the socket does not block indefinitely when trying
# to receive data.
sock.settimeout(0.2)

# Set the time-to-live for messages to 1 so they do not go past the
# local network segment.
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

while True:

    message = input("Enter message: ").encode("utf-8")

    try:

        # Send data to the multicast group
        print (sys.stderr, 'sending "%s"' % message)
        sent = sock.sendto(message, multicast_group)

        # Look for responses from all recipients
        while True:
            print (sys.stderr, 'waiting to receive')
            try:
                data, server = sock.recvfrom(16)
            except socket.timeout:
                print (sys.stderr, 'timed out, no more responses')
                #os.system("PAUSE")
                break
            else:
                print (sys.stderr, 'received "%s" from %s' % (data.decode("utf-8"), server))

    except:
        print("ERROR")
"""                
    finally:
        print (sys.stderr, 'closing socket')
        sock.close()
"""