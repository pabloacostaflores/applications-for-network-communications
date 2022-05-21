import socket
import tkinter
import tqdm
import os
import sys
import time
import wx
import tarfile
import pickle
import errno
import select
#from tqdm import tqdm # pip3 install tqdm

# name for the tarFile
tarName = "compressed.tar.gz"

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

# the ip address or hostname of the server, the receiver
host = socket.gethostbyname(socket.gethostname())
# the port, let's use 5001
port = 1234

#############################################
# for ziping the files
def compress(tar_file, members):
    """
    Adds files (`members`) to a tar_file and compress it
    """
    # open file for gzip compressed writing
    tar = tarfile.open(tar_file, mode="w:gz")
    # with progress bar
    # set the progress bar
    progress = tqdm.tqdm(members)
    for member in progress:
        # add file/folder/link to the tar file (compress)
        tar.add(member)
        # set the progress description of the progress bar
        progress.set_description(f"\nCompressing {member}")
    # close the file
    tar.close()
#############################################

######################################################
# function for decompressing the received tar file
def decompress(tar_file, path, members=None):
    """
    Extracts `tar_file` and puts the `members` to `path`.
    If members is None, all members on `tar_file` will be extracted.
    """
    tar = tarfile.open(tar_file, mode="r:gz")
    if members is None:
        members = tar.getmembers()
    # with progress bar
    # set the progress bar
    progress = tqdm.tqdm(members)
    for member in progress:
        tar.extract(member, path=path)
        # set the progress description of the progress bar
        progress.set_description(f"\nExtracting {member.name}")
    # or use this
    # tar.extractall(members=members, path=path)
    # close the file
    tar.close()
######################################################

#############################################
# for select the files with wx
def selectFiles():
    message = "Seleccionar archvios"
    defaultDir = ""
    defaultFile = ""
    wildcard = "Todos los archivos|*.*"
    style = wx.FD_OPEN | wx.FD_MULTIPLE
    app = wx.App()

    dialog = wx.FileDialog(None, message, defaultDir, defaultFile, wildcard, style)
    response = dialog.ShowModal()

    if response == wx.ID_OK:
        files = dialog.GetPaths()
        for file in files:
            print(f"Se enviaran los archivos {file}")
        return files

    dialog.Destroy()
#############################################

#############################################
# for select the files with wx
def selectDirs():
    message = "Seleccionar folders"
    defaultDir = ""
    style = wx.DD_DEFAULT_STYLE #| wx.DD_MULTIPLE
    app = wx.App()

    dialog = wx.DirDialog(None, message, defaultDir, style)
    response = dialog.ShowModal()

    if response == wx.ID_OK:
        # make it a list because it returns a string for one path
        dirs = [dialog.GetPath()]
        #for dir in dirs:
        #    print(f"Se enviaran las carpetas {dir}")
        return dirs

    dialog.Destroy()
#############################################

#############################################
# send files option
def sendFiles():

    # create the client socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"\n[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("\n[+] Connected.\n")
    s.setblocking(0)

    # for sending the selected option by the client
    try:
        s.send(f"{option}".encode())
    except socket.error as e:
        if e.errno != errno.EAGAIN:
            raise e
        print ('Blocking with'), len(option), ('remaining')
        select.select([], [s], [])  # This blocks until our socket is ready again

    #############################################
    #for calling the function and select files
    """
    # the name of file we want to send, make sure it exists
    filename = "prueba.txt"
    """
    # change between the two options and get the list of files
    if(option==2):
        listOfFiles = selectFiles()
    elif(option==3):
        listOfFiles = selectDirs()
    
    compress(tarName, listOfFiles)
    filename = tarName

    # get the file size
    filesize = os.path.getsize(filename)
    #############################################

    # send the filename and filesize
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"\nSending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            try:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in 
                # busy networks
                s.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
            except socket.error as e:
                if e.errno != errno.EAGAIN:
                    raise e
                print ('Blocking with'), len(bytes_read), ('remaining')
                select.select([], [s], [])  # This blocks until our socket is ready again
    # close the socket
    s.close()
    # delete the tar file when decompressed is compelete
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print("\nEl archivo no existe")
#############################################

#############################################
# see the files on ther server
def listFiles():
    # create the client socket
    s = socket.socket()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connecting to the server
    print(f"\n[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("\n[+] Connected.\n")
    s.setblocking(0)

    # for sending the selected option by the client
    #s.send(f"{option}".encode())
    try:
        s.send(f"{option}".encode())
    except socket.error as e:
        if e.errno != errno.EAGAIN:
            raise e
        print ('Blocking with'), len(option), ('remaining')
        select.select([], [s], [])  # This blocks until our socket is ready again

    ##################################################
    # receiving the txt file with the list of the paths
    # receive the file infos
    received = s.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)

    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"\nReceiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            try:
                # read 1024 bytes from the socket (receive)
                bytes_read = s.recv(BUFFER_SIZE)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
            except socket.error as e:
                if e.errno != errno.EAGAIN:
                    raise e
                print ('Blocking with'), len(bytes_read), ('remaining')
                select.select([], [s], [])  # This blocks until our socket is ready again

    # close the server socket
    s.close()

    print("\nLos archivos del servidor son los siguientes:")
    f = open(filename, 'r')
    paths = f.read()
    print(paths)
    f.close()

    # delete the txt file
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print("\nEl archivo no existe")
    ##################################################

    """
    # for receiving the list of files in string
    fileList = s.recv(BUFFER_SIZE)
    # Decode received data into UTF-8
    fileList = fileList.decode('utf-8')
    # Convert decoded data into list
    fileList = eval(fileList)
    

    print("\n En su nube se encuentran los siguientes archivos:\n")

    # print each element of the list
    for element in fileList:
        print(f"{element}")
    """

    # close the connection
    s.close()
#############################################

#############################################
# function for deleting the files
def deleteFiles():
    # create the client socket
    s = socket.socket()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"\n[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("\n[+] Connected.\n")
    s.setblocking(0)

    # ask the user for the complete path
    fileName = str(input('Escriba la ruta completa del archivo que desea eliminar: '))
    # send the complete path
    # s.send(f"{fileName}".encode())

    try:
        s.send(f"{fileName}".encode())
    except socket.error as e:
        if e.errno != errno.EAGAIN:
            raise e
        print ('Blocking with'), len(option), ('remaining')
        select.select([], [s], [])  # This blocks until our socket is ready again

    # check for the result of elimination
    result = s.recv(BUFFER_SIZE)
    # Decode received data into UTF-8
    result = result.decode('utf-8')
    # print the result
    print(result)

    s.close()
#############################################

#############################################
# for download the files passing the paths
def downloadFiles():
    # create the client socket
    s = socket.socket()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"\n[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("\n[+] Connected.\n")
    s.setblocking(0)

    # ask the user for the number of files to send
    numFilesToSend = int(input('¿Cuantos archivos desea descargar?: '))
    # send the complete path
    #s.send(f"{numFilesToSend}".encode())
    try:
        s.send(f"{numFilesToSend}".encode())
    except socket.error as e:
        if e.errno != errno.EAGAIN:
            raise e
        print ('Blocking with'), len(option), ('remaining')
        select.select([], [s], [])  # This blocks until our socket is ready again
    # create the list to send
    listOfFiles = []
    f = open('paths.txt', 'a')

    for x in range(numFilesToSend):
        path = str(input("Ingrese el directorio completo: "))
        listOfFiles.append(path)
    
    print("\nLos siguientes archivos se descargaran: ")
    for paths in listOfFiles:
        print(paths)
        f.write('\n' + str(paths))
    f.close()

    # set the name of the file to send
    pathsFile = "paths.txt"
    # get the file size
    filesize = os.path.getsize(pathsFile)

    # send the filename and filesize
    # s.send(f"{pathsFile}{SEPARATOR}{filesize}".encode())
    try:
        s.send(f"{pathsFile}{SEPARATOR}{filesize}".encode())
    except socket.error as e:
        if e.errno != errno.EAGAIN:
            raise e
        print ('Blocking with'), len(option), ('remaining')
        select.select([], [s], [])  # This blocks until our socket is ready again

    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"\nSending {pathsFile}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(pathsFile, "rb") as f:
        while True:
            try:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in 
                # busy networks
                s.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
            except socket.error as e:
                if e.errno != errno.EAGAIN:
                    raise e
                print ('Blocking with'), len(bytes_read), ('remaining')
                select.select([], [s], [])  # This blocks until our socket is ready again
    
    # delete the file when compelete
    if os.path.exists(pathsFile):
        os.remove(pathsFile)
    else:
        print("\nEl archivo no existe")
    
    s.close()
    s = socket.socket()
    print(f"\n[+] Connecting to {host}:{port}")
    s.connect((host, port))
    print("\n[+] Connected.\n")
    s.setblocking(0)

    # receive using client socket, not server socket
    received = s.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)

    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"\nReceiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            try:
                # read 1024 bytes from the socket (receive)
                bytes_read = s.recv(BUFFER_SIZE)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
            except socket.error as e:
                if e.errno != errno.EAGAIN:
                    raise e
                print ('Blocking with'), len(bytes_read), ('remaining')
                select.select([], [s], [])  # This blocks until our socket is ready again

    # close the server socket
    s.close()
    # decompressing the tar file
    decompress(filename, "Recibidos")

    # delete the tar file when decompressed is compelete
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print("\nEl archivo no existe")

#############################################

#############################################
# the posible options we can select
def options (option):
     # switch case for all the posible options
    if(option==1):
        print("\nUsted ha seleccionado ver sus archivos en la nube")
        listFiles()
    elif(option==2):
        print("\nUsted ha seleccionado subir archivos desde su ordenador")
        sendFiles()
        print("\n¡¡ARCHIVOS ENVIADOS!!")
    elif(option==3):
        print("\nUsted ha seleccionado subir carpetas desde su ordenador")
        sendFiles()
    elif(option==4):
        print("\nUsted ha seleccionado descargar archivos de la nube")
        listFiles()
        downloadFiles()
    elif(option==5):
        print("\nUsted ha seleccionado eliminar archivos de la nube")
        listFiles()
        deleteFiles()
    elif(option==6):
        print("\nUsted ha seleccionado terminar el programa")
        sys.exit("PROGRAMA TERMINADO")
    else:
        print("\nNo se ha seleccioando una opción válida")
        sys.exit()
#############################################

while(True):
    #######################################
    # description of all options
    print("BIENVENIDO A SU PROGRAMA DRIVE\n")
    print("Por favor seleccione la opción deseada")
    print("1.- Ver archivos en la nube")
    print("2.- Subir archivos desde mi ordenador")
    print("3.- Subir carpeta desde mi ordenador")
    print("4.- Descargar archivos de la nube")
    print("5.- Eliminar archivos de la nube")
    print("6.- Terminar programa")

    #######################################

    #######################################
    # the switch case for selecting the option
    option = int(input('\nIngrese la opcion deseada: '))
    options(option)
    input("\nPresione ENTER para continuar")
    os.system("cls")
    #######################################