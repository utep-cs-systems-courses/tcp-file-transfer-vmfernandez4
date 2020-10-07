import os, socket, sys

sys.path.append("../lib")  # for params
import params

HOST = "127.0.0.1"
PATH_FILES = "./ReceivedFiles"
CONFIRM_MSG = "file %s received from %s"


def write_file(filename, byte, conn, addr):
    try:
        # create file to write
        file_writer = open(filename, 'w+b')

        # receive and write data
        i = 0
        data = ''.encode()
        while i < byte:
            data = conn.recv(1024)
            if not data:
                break
            i += len(data)
        bytearray(data)
        file_writer.write(data)

        # close and print confirmation msg on server
        file_writer.close()
        print(CONFIRM_MSG % (filename, addr))
    except FileNotFoundError:
        print("ERROR: file not found")
        # send failed status
        conn.sendall(str(0).encode())
        sys.exit(1)


def server():
    switchesVarDefaults = (
        (('-l', '--listenPort'), 'listenPort', 50001),
        (('-d', '--debug'), "debug", False),  # boolean (set if present)
        (('-?', '--usage'), "usage", False),  # boolean (set if present)
    )

    paramMap = params.parseParams(switchesVarDefaults)
    debug, listenPort = paramMap['debug'], paramMap['listenPort']

    if paramMap['usage']:
        params.usage()

    bind_addr = (HOST, listenPort)

    # creating listening socket
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # associating socket with host and port number
    listen_socket.bind(bind_addr)

    # "makes" listening socket with max connection to 5
    listen_socket.listen(5)
    print("listening on: ", bind_addr)

    # move to directory to receive files
    os.chdir(PATH_FILES)

    while True:
        # connection and tuple for client address (host, port)
        conn, addr = listen_socket.accept()

        # check connection and client address exist otherwise exit
        if not conn or not addr:
            sys.exit(1)

        if not os.fork():
            print("connection rec'd from", addr)
            # receive file name first
            data = conn.recv(1024)
            filename = data.decode()

            # file byte size
            data_byte = conn.recv(1024).decode()
            try:
                data_byte = int(data_byte)
            except ValueError:
                print("ERROR: byte size not received")
                # send failed status
                conn.sendall(str(0).encode())
                sys.exit(1)

            # if filename was provided, write it
            if filename:
                write_file(filename, data_byte, conn, addr)
                # send successful status
                conn.sendall(str(1).encode())
                sys.exit(0)
            else:
                print("ERROR: empty filename")
                # send failed status
                conn.sendall(str(0).encode())
                sys.exit(1)


if __name__ == "__main__":
    server()