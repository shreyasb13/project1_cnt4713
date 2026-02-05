# Help: https://www.eventhelix.com/networking/ftp/
# Help: https://www.eventhelix.com/networking/ftp/FTP_Port_21.pdf
# Help: https://realpython.com/python-sockets/
# Help: PASV mode may be easier in the long run. Active mode works 
# Reading: https://unix.stackexchange.com/questions/93566/ls-command-in-ftp-not-working
# Reading: https://stackoverflow.com/questions/14498331/what-should-be-the-ftp-response-to-pasv-command

#import socket module
from socket import *
import sys # In order to terminate the program

def quitFTP(clientSocket):
    # COMPLETE
    command = "QUIT" + "\r\n" #completed the QUIT command
    dataOut = command.encode("utf-8")
    clientSocket.sendall(dataOut)
    dataIn = clientSocket.recv(1024)
    data = dataIn.decode("utf-8")
    print(data)

def sendCommand(socket, command):
    dataOut = command.encode("utf-8")
    # Complete
    socket.sendall(dataOut) #create and send new socket
    dataIn = socket.recv(1024) #recieve the response in bytes
    data = dataIn.decode("utf-8") #decode the data
    return data #return the decoded data

def receiveData(clientSocket):
    dataIn = clientSocket.recv(1024)
    data = dataIn.decode("utf-8")
    return data

# If you use passive mode you may want to use this method but you have to complete it
# You will not be penalized if you don't
def modePASV(clientSocket):
    command = "PASV" + "\r\n"
    # Complete 
    #PORT is calculated (n1 x 256) + n2. n1 is the second to last number and n2 is the last number
    #IP is the first 4 numbers

    data = sendCommand(clientSocket, command)
    returnOfData = data
    parsed = returnOfData[returnOfData.find('(')+1 : returnOfData.find(')')]
    partsOfreturn = parsed.split(',')

    #find IP
    ip = (partsOfreturn[0] + "." + partsOfreturn[1] + "." + partsOfreturn[2] + "." + partsOfreturn[3])
    #find the other two numbers to calcuate the port 
    port = int(partsOfreturn[4]) * 256 + int(partsOfreturn[5]) #number 4 of the list is n1 and number 5 of the list is n2

    status = 0

    dataSocket = None #in case PASV fails 

    if data.startswith("227"):
        status = 227
        # Complete
        dataSocket = socket(AF_INET, SOCK_STREAM) #create new socket 
        dataSocket.connect((ip, port))
        
    return status, dataSocket

    
    
def main():
    # COMPLETE
    clientSocket = socket(AF_INET, SOCK_STREAM)
    dataSocket = None
    # TCP socket
    # COMPLETE

    PORT = 21 #constant for the port according to the instructions
    HOST = ""
    if len(sys.argv) == 2:
        HOST = sys.argv[1] #COMPLETE... second parameter in the command line
    else:
        print("Usage: python myftp.py <server-name>\n")
        clientSocket.close()
        sys.exit()
    # COMPLETE

    clientSocket.connect((HOST, PORT)) #open TCP connection

    dataIn = receiveData(clientSocket)
    print(dataIn)

    status = 0
    
    if dataIn.startswith("220"): #220 = service ready
        status = 220
        username = input("Enter the username: ")
        print("Sending username")
        # COMPLETE
        dataIn = sendCommand(clientSocket, "USER "+username+"\r\n") #send the username and receive the response in the variable dataIn
        print(dataIn)
        
        password = input("Enter the password: ")
        print("Sending password")
        if dataIn.startswith("331"): #331 = need password
            status = 331
            # COMPLETE
            dataIn = sendCommand(clientSocket, "PASS "+password+"\r\n") #send the password and receive the response in the variable dataIn
            print(dataIn)

            if dataIn.startswith("230"): #230 = user was able to log in
                status = 230
            elif dataIn.startswith("530"): status = 530


    if status == 230:
        # It is your choice whether to use ACTIVE or PASV mode. In any event:
        # COMPLETE
        pasvStatus, dataSocket = modePASV(clientSocket)

        if pasvStatus == 227:
            while status != 221 and status != 0: # while the server does not return QUIT status

                # This entire block of code will be converted into a funtion later.
                userInput = input("")
                command = None

                # I don't use match (python switch statement) since it was implemented in python3.1, incase an old version of python is used.
                if userInput == "help":
                    printHelp()
                    continue
                elif len(userInput) == 2 and userInput == "ls":
                    command = "LIST" + "\r\n"
                elif userInput[:3] == "cd " and len(userInput) > 3:
                    command = "CWD " + userInput[3:] + "\r\n"
                elif userInput[:4] == "get " and len(userInput) > 4:
                    file_name = userInput[4:]
                    command = "RETR " + file_name + "\r\n"
                    data_in = sendCommand(clientSocket, command)
                    if data_in.startswith("150") or data_in.startswith("125"):
                        if receiveFile(file_name, clientSocket, dataSocket) == 0:
                            print("Command Failed. Fix error and try again!\n")
                            continue
                        next = receiveData(clientSocket)
                        print(next)
                        status, dataSocket = modePASV(clientSocket)
                        continue
                    else:
                        print(data_in)
                        continue
                elif userInput[:4] == "put " and len(userInput) > 4:
                    first_input_index = 4
                    second_input_index_relative_to_first_input = userInput[first_input_index:].find(" ") + 1
                    if second_input_index_relative_to_first_input == 0:
                        if sendFile(userInput[first_input_index:], clientSocket, dataSocket) == 0:
                            print("Command Failed. Fix error and try again!")
                            continue
                        command = "STOR " + userInput[4:] + "\r\n"
                    else:
                        if sendFile(userInput[4:][:second_input_index_relative_to_first_input-1], clientSocket, dataSocket) == 0:
                            print("Command Failed. Fix error and try again!\n")
                            continue
                        command = "STOR " + userInput[second_input_index_relative_to_first_input + first_input_index:]  + "\r\n"
                elif userInput[:7] == "delete " and len(userInput) > 7:
                    command = "DELE " + userInput[7:] + "\r\n"
                elif userInput[:4] == "quit" and len(userInput) == 4:
                    command = "QUIT\r\n"
                else :
                    print("Invalid command! Enter 'help' to see available commands.\n")
                    continue

                data_in = sendCommand(clientSocket,command)
                if not data_in :
                    status = -1
                    break
                status = int(data_in[:3])

                #print("DEBUG Before data_in and status parsing\ndata_in: " + data_in + "\n" + "status: " + str(status))
                #Relevant Status codes:
                #150: File Status OK    125: Data connection already open   226: Closing data connection, requested file action successful
                #426: Connection closed; transfer ended abnormally   550: Requested action not taken; file not found or no access
                #250: Requested File Action Successful  221: Received QUIT command 226: Directory send OK.

                if status == 150 or status == 125: #File Status OK | Data connection already open
                    if(command[:4] == "LIST"):
                        print(data_in[4:])
                        stream_data_in = receiveData(dataSocket)
                        afterword = receiveData(clientSocket)
                        print(stream_data_in)
                        print(afterword)
                        status, dataSocket = modePASV(clientSocket)
                    else:
                        afterword = receiveData(clientSocket)
                        print(afterword)
                        status, dataSocket = modePASV(clientSocket)
                elif status == 250: #Requested File Action Successful
                    print(data_in[4:])
                elif status == 500: #Requested action not taken
                    print(data_in[4:])
                elif status == 221: #Received QUIT command
                    print(data_in[4:])
                elif status == 226: #Directory send OK.
                    print(data_in[4:])
                elif status == 550: #Failed to change directory.
                    print(data_in[4:])
                elif status == 530:
                    print(data_in[4:])
                elif status == 450: #File Unavailable, likely due to it being in use.
                    print(data_in[4:])
                elif status == 452:
                    print(data_in[:])
                elif status == 550: #File Unavailable, likely due to lack of permissions or other client-required action that needs to be taken
                    print(data_in[:])


        elif pasvStatus == 0 :
            print("Failed to enable PASV mode!\n")

    print("Disconnecting...") if status == 221 else\
        print("Connection was lost! Exiting..") if status == -1 else\
            print("Failed to turn on PASV mode! Disconnecting...") if status == 0 else\
                print("Failed to login! Disconnecting...") if status == 530 else\
                print("Unexpected error! Exiting..")
    

    clientSocket.close()
    if dataSocket:
        dataSocket.close()
    
    sys.exit()#Terminate the program after sending the corresponding data

def sendFile(file_path,client_socket, data_socket):
    #type = "ASCII" if file_path[-3:0] == "txt" else
    type = "I" #Binary
    mode = "S"
    sendCommand(client_socket, "TYPE " + type + "\r\n")
    sendCommand(client_socket, "MODE " + mode + "\r\n")
    chunk_size = 4096
    try:
        with open(file_path,"rb") as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                data_socket.sendall(chunk)
        data_socket.close()
        return 1
    except IOError as error:
        print("Error opening or reading file: " + str(error))
        return 0

def receiveFile(file_name, client_socket, data_socket):
    type = "I"  # Binary 
    mode = "S"
    sendCommand(client_socket, "TYPE " + type + "\r\n")
    sendCommand(client_socket, "MODE " + mode + "\r\n")
    chunk_size = 4096
    bytes_received = 0
    try:
        with open(file_name, "wb") as file:
            while True:
                chunk = data_socket.recv(chunk_size)
                if not chunk:
                    break
                file.write(chunk)
                bytes_received += len(chunk)

        data_socket.close()
        print("Downloaded ", bytes_received, " bytes.")
        return 1
    except IOError as error:
        print("Error writing file: ", str(error))
        return 0

def printHelp():
    cdHelp =\
        "cd\n"\
        "Changes the working directory\n"\
        "Usage: cd <directory>\n"

    lsHelp = \
        "ls\n"\
        "Displays the list of files and folders\n"\
        "Usage: ls <directory>\n"

    getHelp = \
        "get\n" \
        "Downloads the specified file from the server to the device\n" \
        "Usage: get <directory>\n"

    putHelp = \
        "put\n" \
        "Uploads the specified file from the device to the server\n" \
        "Usage: put <directory> <optional-new-name>\n"

    deleteHelp = \
        "delete\n" \
        "Deletes the specified file from the server\n" \
        "Usage: delete <directory>\n"

    quitHelp = \
        "quit\n"\
        "Quits the program\n"\
        "Usage: quit\n"

    print("Available Commands:\n" +
          cdHelp +
          "\n" +
          lsHelp +
          "\n" +
          getHelp +
          "\n" +
          putHelp +
          "\n" +
          deleteHelp +
          "\n" +
          quitHelp
          )


main()




