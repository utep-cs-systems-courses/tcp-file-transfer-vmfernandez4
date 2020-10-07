import os, re, socket, sys
from stat import * 

sys.path.append("../lib")  # for params
import params

PATH_FILES = "FilesToSend/"
CONFIRM_MSG = "File %s received by the server"
REJECT_MSG = "File %s could not be received by the server. Try again"


def client():
    switchesVarDefaults = (
        (('-s', '--server'), 'server', "127.0.0.1:50001"),
        (('-d', '--debug'), "debug", False),  # boolean (set if present)
        (('-?', '--usage'), "usage", False),  # boolean (set if present)
    )

    paramMap = params.parseParams(switchesVarDefaults)

    server, usage, debug = paramMap["server"], paramMap["usage"], paramMap["debug"]

    if usage:
        params.usage()

    try:
        serverHost, serverPort = re.split(":", server)
        serverPort = int(serverPort)
    except:
        print("Can't parse server:port from '%s'" % server)
        sys.exit(1)

    addr_port = (serverHost, serverPort)

    # create socket object
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.connect(addr_port)

    while True:
        filename = input("> ")
        filename.strip()

        if filename == "exit":
            sys.exit(0)
        else:
            if not filename:
                continue
            elif os.path.exists(PATH_FILES + filename):
                # send file name
                listen_socket.sendall(filename.encode())
                file_content = open(PATH_FILES + filename, "rb")

                # send file size
                listen_socket.sendall(str(os.stat(PATH_FILES + filename).st_size).encode())

                # send file content
                while True:
                    data = file_content.read(1024)
                    listen_socket.sendall(data)
                    if not data:
                        break
                file_content.close()

                # check if server received file
                status = int(listen_socket.recv(1024).decode())
                # successful transfer
                if status:
                    print(CONFIRM_MSG % filename)
                    sys.exit(0)
                # failed transfer
                else:
                    print(REJECT_MSG % filename)
                    sys.exit(1)
            # file not found
            else:
                print("ERROR: file %s not found" % filename)


if __name__ == "__main__":
    client()