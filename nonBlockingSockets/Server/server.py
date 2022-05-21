import socket
#import tqdm
from tqdm import tqdm # pip3 install tqdm
import shutil
import os
import sys
import tarfile
import pickle

# device's IP address
SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 1234
# receive 4096 bytes each time
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
tarName = "compressed.tar.gz"

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
    progress = tqdm(members)
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
# for ziping the files
def compress(tar_file, members):
    """
    Adds files (`members`) to a tar_file and compress it
    """
    # open file for gzip compressed writing
    tar = tarfile.open(tar_file, mode="w:gz")
    # with progress bar
    # set the progress bar
    progress = tqdm(members)
    for member in progress:
        # add file/folder/link to the tar file (compress)
        tar.add(member)
        # set the progress description of the progress bar
        progress.set_description(f"\nCompressing {member}")
    # close the file
    tar.close()
#############################################

######################################################
# receiving the compressed file
def receiveFile():
    # receive the file infos
    # receive using client socket, not server socket
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)

    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm(range(filesize), f"\nReceiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

    # close the client socket
    client_socket.close()
    # close the server socket
    s.close()
    # decompressing the tar file
    decompress(filename, "Recibidos")

    # delete the tar file when decompressed is compelete
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print("\nEl archivo no existe")
######################################################

######################################################
# functions for listing the files and directories of the current path
def listPath():
    path = os.getcwd()
    # List of files in complete directory
    file_list = []
    
    # create new txt file for sending the list os path
    f = open('paths.txt', 'a')

    """
        Loop to extract files inside a directory
    
        path --> Name of each directory
        folders --> List of subdirectories inside current 'path'
        files --> List of files inside current 'path'
    
    """
    for path, folders, files in os.walk(path):
        for file in files:
            file_list.append(os.path.join(path, file))
    
    print("\nLos archivos que hay en el directorio son los siguientes:\n")
    # Loop to print each filename separately
    for filename in file_list:
        print(filename)
        f.write('\n' + str(filename))
    f.close()

    ##################################################
    # send the files    
    # the name of file we want to send, make sure it exists
    filename = "paths.txt"
    
    # get the file size
    filesize = os.path.getsize(filename)
    #############################################

    # send the filename and filesize
    client_socket.send(f"{filename}{SEPARATOR}{filesize}".encode())

    # start sending the file
    progress = tqdm(range(filesize), f"\nSending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            client_socket.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    
    # close the socket
    client_socket.close()
    # delete the file when compelete
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print("\nEl archivo no existe")
    ##################################################

    """
    # For sending the list to the client 
    # convert to string
    file_list = str(file_list)
    # encode string
    file_list = file_list.encode()
    # send encoded string version of the List
    client_socket.send(file_list)
    """

    # closing the connection
    client_socket.close()
    s.close()
######################################################

###################################################
# deleting a path or a directory
def deletePathOrDir():
    # do the connection again because it is closed by calling listPath()
    s = socket.socket()
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    print(f"\n[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    # accept connection if there is any
    client_socket, address = s.accept() 
    # if below code is executed, that means the sender is connected
    print(f"\n[+] {address} is connected.")

    # receiving the filename to delete
    fileNameToDelete = client_socket.recv(BUFFER_SIZE)
    fileNameToDelete = fileNameToDelete.decode('utf-8')
    
    print(f"\nEl archivo {fileNameToDelete} se eliminara")
    
    # checking the file to exist for deleting and verification if is a file or dir
    if os.path.exists(fileNameToDelete):
        # if the path exist and is a file
        if(os.path.isfile(fileNameToDelete)):
            os.remove(fileNameToDelete)
            client_socket.send("\nEl archivo se ha eliminado con exito".encode())
        # if the path exists and is a dir
        elif(os.path.isdir(fileNameToDelete)):
            # for deleting the dir and all its content
            shutil.rmtree(fileNameToDelete)
            client_socket.send("\nEl directorio se ha eliminado con exito".encode())
    else:
        # if the file does not exists
        client_socket.send("\nEl archivo no existe".encode())

    client_socket.close()
    s.close()
###################################################

###################################################
# for sending the files to client
def sendFiles():
    
    # do the connection again because it is closed by calling listPath()
    s = socket.socket()
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    print(f"\n[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    # accept connection if there is any
    client_socket, address = s.accept() 
    # if below code is executed, that means the sender is connected
    print(f"\n[+] {address} is connected.")

    #############################################
    # receiving the number of files
    numOfFiles = client_socket.recv(BUFFER_SIZE)
    numOfFiles = numOfFiles.decode('utf-8')
    print(f"\nSe han seleccionado {numOfFiles} archivos")

    # receiving the txt file with the list of the paths
    # receive the file infos
    # receive using client socket, not server socket
    received = client_socket.recv(BUFFER_SIZE).decode()
    pathsFilename, PFfilesize = received.split(SEPARATOR)
    # remove absolute path if there is
    pathsFilename = os.path.basename(pathsFilename)
    # convert to integer
    PFfilesize = int(PFfilesize)

    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm(range(PFfilesize), f"\nReceiving {pathsFilename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(pathsFilename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

    client_socket.close()
    # accept connection if there is any
    client_socket, address = s.accept() 
    # if below code is executed, that means the sender is connected
    print(f"\n[+] {address} is connected.")

    fileList = []

    print("\nLos archivos a enviar son los siguientes:")
    
    #create the file list
    with open(pathsFilename) as fname:
        lines = fname.readlines()
        for line in lines:
            fileList.append(line.strip('\n'))
    del fileList[0]
    print("La lista completa es:")
    print(fileList)
    
    # delete the txt file
    if os.path.exists(pathsFilename):
        os.remove(pathsFilename)
    else:
        print("\nEl archivo no existe")

    compress(tarName, fileList)
    filename = tarName

    # get the file size
    filesize = os.path.getsize(filename)
    #############################################

    # send the filename and filesize
    client_socket.send(f"{filename}{SEPARATOR}{filesize}".encode())

    # start sending the file
    progress = tqdm(range(filesize), f"\nSending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            client_socket.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

    # delete the tar file when decompressed is compelete
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print("\nEl archivo no existe")
    
    client_socket.close()
    s.close()
###################################################

while True:
    ##################################################
    # create the server socket
    # TCP socket
    s = socket.socket()

    # bind the socket to our local address
    s.bind((SERVER_HOST, SERVER_PORT))

    # enabling our server to accept connections
    # 5 here is the number of unaccepted connections that
    # the system will allow before refusing new connections
    s.listen(5)
    print(f"\n[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    # accept connection if there is any
    client_socket, address = s.accept() 
    # if below code is executed, that means the sender is connected
    print(f"\n[+] {address} is connected.")

    ##################################################

    # receive the selected option by the client
    option = int(client_socket.recv(BUFFER_SIZE).decode())
    print(f"\nSe selecciono la opción: {option}")

    if(option == 1):
        listPath()
    elif(option == 2):
        receiveFile()
    elif(option == 3):
        receiveFile()
    elif(option == 4):
        listPath()
        sendFiles()
    elif(option == 5):
        listPath()
        deletePathOrDir()
    else:
        print("\nNo se ha seleccionado una opcion valida")
        sys.exit()