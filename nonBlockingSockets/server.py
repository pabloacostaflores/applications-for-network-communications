import socket
import struct
import sys

FORMAT = 'utf-8'

multicast_group = '224.3.29.71'
server_address = ('', 10000)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

############################################################
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
############################################################

# Bind to the server address
sock.bind(server_address)

# Tell the operating system to add the socket to the multicast group
# on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

clients, names = [], []

# Receive/respond loop
while True:
    print ('\nEsperando a recibir mensajes . . .')
    data, address = sock.recvfrom(1024)

    # if message is NAME
    if data == b'NAME':
        data, adrress = sock.recvfrom(1024)
        clients.append(address)
        names.append(data.decode(FORMAT))
        name = data.decode(FORMAT)
        nMemeber = f'{name} se ha unido al chat'
        for client in clients:
            namesList = 'list'
            for i in names:
                namesList = namesList + ',' + i
            sock.sendto(namesList.encode(FORMAT), client)

            sock.sendto(nMemeber.encode(FORMAT), client)
        print(f"{data.decode(FORMAT)} se ha conectado")
        continue
    
    message = data.decode(FORMAT)
    print ('%s bytes recibidos de: %s' % (len(data), address))
    print ('%s' % message)

    # separete the message
    dest = message.split('|$%|')[0]
    msg = message.split('|$%|')[1]

    for i in range(len(clients)):
        if dest != 'Todos':
            if names[i] == dest:
                msg = "(private) " + msg
                sock.sendto(msg.encode(FORMAT), clients[i])
                break
        else:
            sock.sendto(msg.encode(FORMAT), clients[i])

"""
    # send message
    for client in clients:
        sock.sendto(message.encode(FORMAT), client)
        print("Mensaje enviado a: ", client)
        #sock.sendto(data, client)
"""
"""
    # the list of clients
    print(clients)
    print(names)
"""
"""
    print (sys.stderr, 'sending acknowledgement to', address)
    #sock.sendto('ack'.encode("utf-8"), address)
    sock.sendto('ack'.encode("utf-8"), address)
"""