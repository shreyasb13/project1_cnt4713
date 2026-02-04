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

    username = input("Enter the username: ")
    password = input("Enter the password: ")

    clientSocket = socket(AF_INET, SOCK_STREAM) # TCP socket
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
        print("Sending username")
        # COMPLETE
        dataIn = sendCommand(clientSocket, "USER "+username+"\r\n") #send the username and receive the response in the variable dataIn
        print(dataIn)

        print("Sending password")
        if dataIn.startswith("331"): #331 = need password
            status = 331
            # COMPLETE
            dataIn = sendCommand(clientSocket, "PASS "+password+"\r\n") #send the password and receive the response in the variable dataIn
            print(dataIn)

            if dataIn.startswith("230"): #230 = user was able to log in
                status = 230


    if status == 230:
        # It is your choice whether to use ACTIVE or PASV mode. In any event:
        # COMPLETE
        pasvStatus, dataSocket = modePASV(clientSocket)
        if pasvStatus == 227:
            while(status != 221): # while the server does not return QUIT status

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
                    command = "CWD " + userInput[2:] + "\r\n"
                elif userInput[:4] == "quit" and len(userInput) == 4:
                    command = "QUIT\r\n"
                else :
                    print("Invalid command! Enter 'help' to see available commands.")
                    continue

                data_in = sendCommand(clientSocket,command)
                status = int(data_in[:3])

                print("DEBUG Before data_in and status parsing\ndata_in: " + data_in + "\n" + "status: " + str(status))
                #Relevant Status codes:
                #150: File Status OK    125: Data connection already open   226: Closing data connection, requested file action successful
                #426: Connection closed; transfer ended abnormally   550: Requested action not taken; file not found or no access
                #250: Requested File Action Successful  221: Received QUIT command 226: Directory send OK.

                if status == 150 or status == 125: #File Status OK | Data connection already open
                    print(data_in[4:])
                    stream_data_in = receiveData(dataSocket)
                    print(stream_data_in)
                elif status == 250: #Requested File Action Successful
                    print(data_in[4:])
                elif status == 500: #Requested action not taken
                    print(data_in[4:])
                elif status == 221: #Received QUIT command
                    print(data_in[4:])
                elif status == 226: #Directory send OK.
                    print(data_in[4:])


        elif pasvStatus == 0 :
            print("Failed to enable PASV mode!\n")

    
    print("Disconnecting...")
    

    clientSocket.close()
    dataSocket.close()
    
    sys.exit()#Terminate the program after sending the corresponding data


def printHelp():
    cdHelp =\
        "cd\n"\
        "Changes the working directory\n"\
        "Usage: cd <directory>\n"

    lsHelp = \
        "ls\n"\
        "Displays the list of files and folders\n"\
        "Usage: ls <directory>\n"

    quitHelp = \
        "quit\n"\
        "Quits the program\n"\
        "Usage: quit\n"

    print("Available Commands:\n" +
          cdHelp +
          "\n" +
          lsHelp +
          "\n" +
          quitHelp
          )


main()

