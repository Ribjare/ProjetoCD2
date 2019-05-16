"""
 Implements a simple HTTP/1.0 Server

"""

import socket
import time
import threading


image_type = ["png", "jpg"]


class Response:
    def __init__(self, body, connectionType, length=None, type=None, status="Unknown"):

        self.body = body
        self.status = status     # HTTP/1.0 200 OK, etc
        self.date = time.strftime("%a, %d %b %Y %H:%M:%S")
        self.contentLength = length
        self.contentType = type
        self.connectionType = connectionType

    def get_string_response(self):
        response = self.status + "\n"
        response += self.date + "\n"
        response += self.contentLength+"\n"
        response += self.contentType+"\n"
        response += self.connectionType+"\n"
        response += "\n"
        response.encode()
        if isinstance(self.body, bytes):
            response += self.body
        else:
            response += self.body.enconde()

        return response

class Request:
    def __init__(self, headers):

        self.headers = headers

        get_content = headers[0].split()

        #   Get filename
        self.path = get_content[1]
        print(get_content)
        if self.path == '/':
            self.path = 'htdocs' + '/index.html'

        #   Ir buscar o file name ao path
        arr = self.path.split('/')
        self.filename = arr[len(arr)-1]

        #   Get the file type (if is text or not)
        if self.filename.split('.')[1] in image_type:
            self.filetype = self.filename.split('.')[1]
        else:
            self.filetype = "text"

        #   Get Connection type (close, keep-alive, etc)
        self.connectionType = headers[len(headers)-3].split(":")[1]

    def getContent(self):
        try:
            if self.filetype != "text":
                with open(self.path, 'rb') as fin:
                    return fin.read()
            else:
                with open(self.path) as fin:
                    return fin.read()

        except FileNotFoundError:
            raise FileNotFoundError

    def isPrivate(self):
        if "/private/" in self.path:
            return True
        return False


def handle_request(request):
    """Returns file content for client request"""

    # Parse headers
    print(request)
    headers = request.split('\n')

    re = Request(headers=headers)
    try:
        if re.isPrivate():
            return Response(status="HTTP/1.0 403 Forbidden", body="Private link",
                            connectionType="close")

        body = re.getContent()

    #   If is a Bad Request
    except PermissionError:
        return Response(status="HTTP/1.0 400 Bad Request", body="Bad Request", connectionType="close")

    #   If the file doesn't exist
    except FileNotFoundError:
        return Response(status="HTTP/1.0 404 Not Found", body="File Not Found", connectionType="close")

    # Return response
    return Response(status="HTTP/1.0 200 OK", body=body, length=len(body), type=re.filetype,
                    connectionType=re.connectionType)


def handle_response(content):
    """Returns byte-encoded HTTP response."""


    """
    # Build HTTP response
    if content:

        response = 'HTTP/1.0 200 OK\n'.encode()
        response += f'Content-Length:{len(content)}\n'.encode()

        if isinstance(content, bytes):
            response += f'Content-Type:{"image/jpeg"}\n\n'.encode()
            response += content     # because it's already enconded
        else:
            response += f'Content-Type:{"text/html"}\n\n'.encode()
            response += content.encode()

    else:
        response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'.encode()

    # Return encoded response
    """
    return response


def close_connection(client_connection):
    client_connection.close();


def client_handle(client_connection):
    while True:
        # Handle client request
        request = client_connection.recv(1024).decode()

        content = handle_request(request)

        # Prepare byte-encoded HTTP response
        response = handle_response(content)

        # Return HTTP response
        client_connection.sendall(response)


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

    thread = threading.Thread(target=client_handle, args=(client_connection,))
    thread.start()

    time.sleep(5)
    client_connection.close()

# Close socket
server_socket.close()
