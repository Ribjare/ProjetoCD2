"""
 Implements a simple HTTP/1.0 Server

"""

import socket

# define errors
File_Not_Found = 404


def handle_request(request):
    # Get the first line of the request (Ex: GET /ipsum.html HTTP/1.1)
    strLines = request.split("\n")
    print(strLines[0])
    # Split the content of first line (Ex: [‘GET’, ‘/ipsum.html’, ‘HTTP..’])
    headers = strLines[0].split()
    print(headers)
    try:
        # Open the file
        if headers[1] == "/":
            file = open("./htdocs/index.html")
        else:
            file = open("./htdocs/" + headers[1], "r")
        # Read contents
        read = file.read()
        # Close file
        file.close()
        # Return contents
        return read
    except FileNotFoundError:
        return File_Not_Found


# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print('Listening on port %s ...' % SERVER_PORT)

while True:
    # Wait for client connections
    client_connection, client_address = server_socket.accept()

    # Handle client request
    request = client_connection.recv(1024).decode()
    print(request)
    content = handle_request(request)
    if content == File_Not_Found:
        response = "HTTP/1.0 404 NOT FOUND\n\nFile not found"
    else:
        # Send HTTP response
        response = 'HTTP/1.0 200 OK\n\n'
        response += content

    # file.close()
    client_connection.sendall(response.encode())
    client_connection.close()

# Close socket
server_socket.close()
