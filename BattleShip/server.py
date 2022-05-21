#!usr/bin/python

import socket
import sys
import os
import random

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
	Simple udp socket server
'''

UDP_IP = "localhost" # = 0.0.0.0 u IPv4
UDP_PORT = 1234
rows = 10
columns = 10

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
print("Socket creado")
sock.bind((UDP_IP, UDP_PORT))

############################################
def printBoard(serverBoard):
   print("\nMi tablero:\n")
   # print the matrix
   for line in serverBoard:
      print('  '.join(map(str, line)))
############################################

############################################
def printCboard(clientBoard):
   print("\nEl tablero del cliente:\n")
   # print the matrix
   for line in clientBoard:
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
def fillMatrix(serverBoard):
   for i in range(rows):
      row = []
      for j in range(columns):
         row.append(0)
      serverBoard.append(row)
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
############################################

############################################
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
   x = random.randint(0, rows - 1)
   y = random.randint(0, columns - 1)
   direction = random.randint(0, 1)
   print(f"Se ha seleccioando la fila {x}, la columna {y} y direccion {direction}\n")

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
def registerShoots(serverBoard):
   shoots = 0
   while(shoots < 3):
      # receive the row
      data, addr = sock.recvfrom(1024)
      r = int(data.decode("UTF-8"))
      # receive the column
      data, addr = sock.recvfrom(1024)
      c = int(data.decode("UTF-8"))

      print(f"El cliente ha disparado en la fila {r}, columna {c}")
      #serverBoard[r][c] = 'X'

      # send the result
      if serverBoard[r][c] == "a" or serverBoard[r][c] == "c" or serverBoard[r][c] == "d" or serverBoard[r][c] == "s":
         print("El cliente ha acertado\n")
         if countShips(serverBoard, serverBoard[r][c]) == 1: 
            if countShips(serverBoard, "X") == 20:
               print("\nEL CLIENTE HA GANADO\n")
               sock.sendto("SE ACABO EL JUEGO".encode("UTF-8"), addr)
               serverBoard[r][c] = 'X'
               printBoard(serverBoard)
               os.system("cls")
               #print("El tablero del cliente es el siguiente:")
               #printCboard(clientBoard)
               exit()
            else:
               end = "Has acabado con los " + serverBoard[r][c] + "f"
               sock.sendto(end.encode("UTF-8"), addr)
               serverBoard[r][c] = 'X'
               printBoard(serverBoard)
               os.system("cls")
               #print("El tablero del cliente es el siguiente:")
               #printCboard(clientBoard)
         else:
            sock.sendto(serverBoard[r][c].encode("UTF-8"), addr)
            serverBoard[r][c] = 'X'
            printBoard(serverBoard)
            os.system("cls")
            #print("El tablero del cliente es el siguiente:")
            #printCboard(clientBoard)
      else:
         print("\nEl cliente ha fallado")
         sock.sendto("Has fallado el tiro".encode("UTF-8"), addr)
         serverBoard[r][c] = 'F'
         os.system("cls")
         break
      shoots += 1
############################################

############################################
def shoot(addr):
   count = 0
   while(count < 3):
      printCboard(clientBoard)
      printBoard(serverBoard)
      # send the row
      r = str(random.randint(0, rows - 1))
      sock.sendto(r.encode("UTF-8"), addr)
      # send the column
      c = str(random.randint(0, columns - 1))
      sock.sendto(c.encode("UTF-8"), addr)

      # receive the result
      data, addr = sock.recvfrom(1024)
      result = data.decode("UTF-8")
      print(f"El cliente {addr} dice: ", data.decode("UTF-8"))

      if result == "a" or result == "c" or result == "d" or result == "s":
         print("\nSe ha acertado")
         clientBoard[int(r)][int(c)] = "X"
      if result == "Has acabado con los af":
         print("\nSe ha acertado y destruido el acorazado")
         clientBoard[int(r)][int(c)] = "X"
      if result == "Has acabado con los cf":
         print("\nSe ha acertado y destruido los cruceros")
         clientBoard[int(r)][int(c)] = "X"
      if result == "Has acabado con los df":
         print("\nSe ha acertado y destruido un destructor")
         clientBoard[int(r)][int(c)] = "X"
      if result == "Has acabado con los sf":
         print("\nSe ha acertado y destruido el submarino")
         clientBoard[int(r)][int(c)] = "X"
      if result == "SE ACABO EL JUEGO":
         print("\nHAS GANADO, EL CLIENTE SE HA QUEDADO SIN BARCOS\n")
      elif result == "Has fallado el tiro":
         print("\nSe ha fallado el tiro")
         clientBoard[int(r)][int(c)] = "F"
         break
      count += 1
      #input("\nPresione ENTER para continuar")
      os.system("cls")
      printCboard(clientBoard)
############################################

while True:
   input("\nPresione ENTER para continuar")
   os.system("cls")
   print ("Esperando cliente")
   data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
   print("Mensaje recibido:", data.decode("UTF-8"), "de", addr)

   RESPONSE1 = "Hola cliente, ¡¡JUGUEMOS!!, ¿Cuál es tu nombre?"
   # Envio de respuesta
   sock.sendto(RESPONSE1.encode("UTF-8"), addr)
   print ("He preguntado al cliente cual es su nombre . . .\n")

   # receive the player name
   data, addr = sock.recvfrom(1024)
   playerName = data.decode("UTF-8")
   print ("Nombre del jugador:", playerName)

   # asking to start the game
   RESPONSE2 = "¡HOLA "+playerName+"! por favor llena tu tablero, yo hare lo mismo"
   sock.sendto(RESPONSE2.encode("UTF-8"), addr)
   print("\nLe he pedido al servidor que llene su tablero . . .")

   # waiting for the player to respond
   print ("Esperando a que el jugador llene su tablero . . .")
   data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
   print("El cliente dice: ", data.decode("UTF-8"), "de", addr)
   print("El jugador ha llenado su tablero, ¡¡COMENCEMOS!!:", data.decode("UTF-8"), "de", addr)

   ############################################

   # create the server board
   serverBoard = []
   # create the client board
   clientBoard = []

   # create the matrixs and fill with 0s
   fillMatrix(serverBoard)
   fillMatrix(clientBoard)
   # print the board
   printBoard(serverBoard)

   ############################################
   while(countShips(serverBoard, "a") < 4):
      printBoard(serverBoard)
      print("\nColoca tu acorazado")
      place(serverBoard, 4, "a")
      #printBoard(serverBoard)
      os.system("cls")
   while(countShips(serverBoard, "c") < 6):
      printBoard(serverBoard)
      print("\nColoca tu crucero")
      place(serverBoard, 3, "c")
      #printBoard(serverBoard)
      os.system("cls")
   while(countShips(serverBoard, "d") < 6):
      printBoard(serverBoard)
      print("\nColoca tu destructor")
      place(serverBoard, 2, "d")
      #printBoard(serverBoard)
      os.system("cls")
   while(countShips(serverBoard, "s") < 5):
      printBoard(serverBoard)
      print("\nColoca tu submarino")
      place(serverBoard, 5, "s")
      #printBoard(serverBoard)
      os.system("cls")
   ############################################

   # tell the client my board is full and ready to play
   RESPONSE3 = "Mi tablero esta lleno, comienza el juego"
   sock.sendto(RESPONSE3.encode("UTF-8"), addr)
   print("\nHe dicho al cliente que mi tablero esta lleno")

   shift = random.randint(0, 1)

   ############################################
   # game
   while True:
      if(shift == 0):
         SHIFT = "¡¡ES TU TURNO!!, ¡¡TIRA!!"
         print("\nEl cliente empieza . . .")
         sock.sendto(SHIFT.encode("UTF-8"), addr)
         registerShoots(serverBoard)
         shoot(addr)
      elif(shift == 1):
         SHIFT = "¡¡ES MI TURNO!!, ¡¡TIRARE!!"
         print("\nYo empiezo . . .")
         sock.sendto(SHIFT.encode("UTF-8"), addr)
         shoot(addr)
         registerShoots(serverBoard)
      #exit()