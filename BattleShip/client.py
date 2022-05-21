#!usr/bin/python

import socket	#for sockets
import sys	#for exit
import os

print("BIENVENIDO AL JUEGO DE BATALLA NAVAL")

print ("""
                                     # #  ( )
                                  ___#_#___|__
                              _  |____________|  _
                       _=====| | |            | | |==== _
                 =====| |.---------------------------. | |====
   <--------------------'   .  .  .  .  .  .  .  .   '--------------/
     \                SEGUNDA PRACTICA - BATALLA NAVAL             /
      \                     POR PABLO ACOSTA                      /
       \                        JOSE JUAN SUAREZ                 /
        \_______________________________________________________/
  wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
   wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww 
""")

'''
	udp socket client
	Silver Moon
'''

UDP_IP = "localhost"  # localhost
UDP_PORT = 1234
rows = 10
columns = 10

print("UDP objetivo IP:", UDP_IP)
print("UDP objetivo puerto:", UDP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

############################################
# filling the matrix
def fillMatrix(clientBoard):
    for i in range(rows):
        row = []
        for j in range(columns):
            row.append(0)
        clientBoard.append(row)
############################################

############################################
def printBoard(clientBoard):
    print("\nTu tablero:\n")
    # print the matrix
    for line in clientBoard:
        print('  '.join(map(str, line)))
############################################

############################################
def printSboard(serverBoard):
   print("\nEl tablero del servidor:\n")
   # print the matrix
   for line in serverBoard:
      print('  '.join(map(str, line)))
############################################

############################################
def countShips(list, symbol):
    count = 0
    for i in range(len(list)):
        for j in range(len(list[i])):
            if list[i][j] == symbol:
                count += 1
    return count
############################################

############################################
def areCellsEmpty(board, x, y, nCells, direction):
    # check if the cells are empty
    if direction == 0:
        for i in range(nCells):
            if board[x][y + i] != 0:
                print("Hay casillas ya ocupadas, vuelva a intentarlo")
                return False
    elif direction == 1:
        for i in range(nCells):
            if board[x + i][y] != 0:
                print("Hay casillas ya ocupadas, vuelva a intentarlo")
                return False
    else:
        print("Direccion invalida")
        return False
    return True

def isCellEmpty(board, x, y):
    if board[x][y] == 0:
        return True
    else:
        print("La casilla ya esta ocupada")
        return False
############################################

############################################
# place the boats on the board
def place(board, nCells, symbol):
    # get the coordinates
    x = int(input("Introduce la fila: "))
    y = int(input("Introduce la columna: "))
    print(""" Escriba 0 si se desea desplazar hacia la derecha horizontalmente
              o escriba 1 si se desea desplzar hacia abajo verticalmente """)
    direction = int(input("Direccion: "))

    # place the boat
    # horizontal
    if direction == 0:
        # check if the coordinates are valid
        if x < 0 or y < 0 or x >= rows or y + nCells > rows:
            print("Coordenadas invalidas, intente otra vez")
            return False
        if (not isCellEmpty(board, x, y)):
            return False
        if(areCellsEmpty(board, x, y, nCells, direction)):
            for i in range(nCells):
                board[x][y + i] = symbol
            return True

    # vertical
    elif direction == 1:
        # check if the coordinates are valid
        if y < 0 or x < 0 or y >= columns or x + nCells > columns:
            print("Coordenadas invalidas, intente otra vez")
            return False
        if (not isCellEmpty(board, x, y)):
            return False
        if(areCellsEmpty(board, x, y, nCells, direction)):
            for i in range(nCells):
                board[x + i][y] = symbol
            return True
    else:
        print("Direccion invalida")
        return False

    return True
############################################

############################################
def shoot():
    count = 0
    while(count < 3):
        printBoard(clientBoard)
        #print("\nEl tablero del servidor es el siguiente:")
        printSboard(serverBoard)
        # send the row
        r = input("\nIntroduzca la fila: ")
        sock.sendto(r.encode("UTF-8"), (UDP_IP, UDP_PORT))
        # send the column
        c = input("Introduzca la columna: ")
        sock.sendto(c.encode("UTF-8"), (UDP_IP, UDP_PORT))

        # receive the result
        data, addr = sock.recvfrom(1024)
        result = data.decode("UTF-8")
        print(f"\nEl servidor {addr} dice: ", data.decode("UTF-8"))

        if result == "a" or result == "c" or result == "d" or result == "s":
            print("\nHas acertado")
            serverBoard[int(r)][int(c)] = "X"
        if result == "Has acabado con los af":
            print("\nHas acertado y has destruido el acorazado")
            serverBoard[int(r)][int(c)] = "X"
        if result == "Has acabado con los cf":
            print("\nHas acertado y has destruido los cruceros")
            serverBoard[int(r)][int(c)] = "X"
        if result == "Has acabado con los df":
            print("\nHas acertado y has destruido los destructores")
            serverBoard[int(r)][int(c)] = "X"
        if result == "Has acabado con los sf":
            print("\nHas acertado y has destruido el submarino")
            serverBoard[int(r)][int(c)] = "X"
        if result == "SE ACABO EL JUEGO":
            print("\nHAS GANADO, EL SERVIDOR SE HA QUEDADO SIN BARCOS")
        elif result == "Has fallado el tiro":
            print("\nHas fallado")
            serverBoard[int(r)][int(c)] = "F"
            break
        count += 1
        input("\nPresione ENTER para continuar")
        os.system("cls")
        printSboard(serverBoard)
############################################

############################################
def registerShoots(clientBoard):
    shoots = 0
    while(shoots < 3):
        # receive the row
        data, addr = sock.recvfrom(1024)
        r = int(data.decode("UTF-8"))
        # receive the column
        data, addr = sock.recvfrom(1024)
        c = int(data.decode("UTF-8"))

        print(f"\nEl servidor ha disparado en la fila {r}, columna {c}")
        #clientBoard[r][c] = 'X'

        # send the result
        if clientBoard[r][c] == "a" or clientBoard[r][c] == "c" or clientBoard[r][c] == "d" or clientBoard[r][c] == "s":
            print("El servidor ha acertado\n")
            if countShips(clientBoard, clientBoard[r][c]) == 1:
                if countShips(clientBoard, "X") == 20:
                    print("EL SERVIDOR HA GANADO")
                    sock.sendto("SE ACABO EL JUEGO".encode("UTF-8"), (UDP_IP, UDP_PORT))
                    clientBoard[r][c] = 'X'
                    printBoard(clientBoard)
                    input("\nPresione ENTER para continuar")
                    os.system("cls")
                    #print("El tablero del servidor es el siguiente:")
                    #printSboard(clientBoard)
                    exit()
                else:
                    end = "Has acabado con los " + clientBoard[r][c] + "f"
                    sock.sendto(end.encode("UTF-8"), (UDP_IP, UDP_PORT))
                    clientBoard[r][c] = 'X'
                    printBoard(clientBoard)
                    input("\nPresione ENTER para continuar")
                    os.system("cls")
                    #print("El tablero del servidor es el siguiente:")
                    #printSboard(clientBoard)
            else:
                sock.sendto(clientBoard[r][c].encode("UTF-8"), (UDP_IP, UDP_PORT))
                clientBoard[r][c] = 'X'
                printBoard(clientBoard)
                input("\nPresione ENTER para continuar")
                os.system("cls")
                #print("El tablero del servidor es el siguiente:")
                #printSboard(clientBoard)
        else:
            print("El servidor ha fallado\n")
            sock.sendto("Has fallado el tiro".encode("UTF-8"), (UDP_IP, UDP_PORT))
            clientBoard[r][c] = 'F'
            printBoard(clientBoard)
            input("\nPresione ENTER para continuar")
            os.system("cls")
            break
        shoots += 1
############################################
input("\nPresione ENTER para continuar")
os.system("cls")
#while True:
# ask the server to play
MESSAGE1 = "¡¡HOLA!!, ¿JUGAMOS?"
sock.sendto(MESSAGE1.encode("UTF-8"), (UDP_IP, UDP_PORT))
print("\nLe he preguntado al servidor si quiere jugar\n")

# receive message from server
data, addr = sock.recvfrom(1024)
print("Se ha recibido un mensaje")
print(f"El servidor {addr} dice: ", data.decode("UTF-8"))

# send my name to server
MESSAGE2 = input("\nIntroduzca su nombre: ")
sock.sendto(MESSAGE2.encode("UTF-8"), (UDP_IP, UDP_PORT))
print("Se ha enviado el nombre de usuario\n")

#receive message from server
data, addr = sock.recvfrom(1024)
print("Se ha recibido un mensaje")
print(f"El servidor {addr} dice: ", data.decode("UTF-8"))

############################################
#clientBoard[0][0] = 'X'

# create the matrixs for the game board
clientBoard = []
serverBoard = []
# create the matrix and fill with 0s
fillMatrix(clientBoard)
fillMatrix(serverBoard)

# print the initial game board
#printBoard(clientBoard)

############################################
while(countShips(clientBoard, "a") < 4):
    printBoard(clientBoard)
    print("\nColoca tu acorazado")
    place(clientBoard, 4, "a")
    #printBoard(clientBoard)
    input("\nPresione ENTER para continuar")
    os.system("cls")
while(countShips(clientBoard, "c") < 6):
    printBoard(clientBoard)
    print("\nColoca tu crucero")
    place(clientBoard, 3, "c")
    #printBoard(clientBoard)
    input("\nPresione ENTER para continuar")
    os.system("cls")
while(countShips(clientBoard, "d") < 6):
    printBoard(clientBoard)
    print("\nColoca tu destructor")
    place(clientBoard, 2, "d")
    #printBoard(clientBoard)
    input("\nPresione ENTER para continuar")
    os.system("cls")
while(countShips(clientBoard, "s") < 5):
    printBoard(clientBoard)
    print("\nColoca tu submarino")
    place(clientBoard, 5, "s")
    #printBoard(clientBoard)
    input("\nPresione ENTER para continuar")
    os.system("cls")
############################################

# tell the server i´ve filled my board
MESSAGE3 = "¡¡Ya he colocado mis barcos!!"
sock.sendto(MESSAGE3.encode("UTF-8"), (UDP_IP, UDP_PORT))
print("\nMensaje enviado al servidor: ¡He colocado mis barcos!\n")

# receive message from server
data, addr = sock.recvfrom(1024)
print(f"El servidor {addr} dice: ", data.decode("UTF-8"))

while True:
    # who starts the game
    data, addr = sock.recvfrom(1024)
    print(f"\nEl servidor {addr} dice: ", data.decode("UTF-8"))
    if data.decode("UTF-8") == "¡¡ES TU TURNO!!, ¡¡TIRA!!":
        shoot()
        registerShoots(clientBoard)
    elif data.decode("UTF-8") == "¡¡ES MI TURNO!!, ¡¡TIRARE!!":
        registerShoots(clientBoard)
        shoot()
    #exit()