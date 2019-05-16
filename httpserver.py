"""
 Implements a simple HTTP/1.0 Server

"""

import socket
import time
import threading


image_type = ["png", "jpg"]


class Response:
    def __init__(self, body, connectionType, contentType=None, status="Unknown"):

        self.body = body
        self.status = status     # HTTP/1.0 200 OK, etc
        self.date = time.strftime("%a, %d %b %Y %H:%M:%S")
        self.contentType = contentType
        self.connectionType = connectionType

    def get_string_response(self):
        response = self.status + "\n"
        response += 'Date: ' + self.date + "\n"
        response += 'Content-Length: {}'.format(len(self.body))+"\n"

        if self.contentType is not None:
            response += 'Content-Type: {} '.format(self.contentType) + "\n"

        response += 'Connection: ' + self.connectionType+"\n\n"

        if isinstance(self.body, bytes):
            final = response.encode()
            final += self.body
        else:
            response += self.body
            final = response.encode()

        print(response)
        return final


class Request:
    def __init__(self, headers):

        self.headers = headers

        get_content = headers[0].split()

        #   Get filename
        print('Content: ')
        print(get_content)

        self.path = get_content[1]
        if self.path == '/':
            self.path = '/index.html'
        self.path = 'htdocs' + self.path

        #   Ir buscar o file name ao path
        arr = self.path.split('/')
        self.filename = arr[len(arr)-1]

        #   Get the file type (if is text or not)
        if self.filename.split('.')[1] in image_type:
            self.filetype = '{}/{}'.format("images", self.filename.split('.')[1])
        else:
            self.filetype = "text/html"

        #   Get Connection type (close, keep-alive, etc)
        self.connectionType = headers[len(headers)-3].split(":")[1]

    def getContent(self):
        try:
            print(self.path)
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
    print("Request:"+request)
    headers = request.split('\n')
    time.sleep(1)
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
    return Response(status="HTTP/1.0 200 OK", body=body, contentType=re.filetype,
                    connectionType=re.connectionType)


def close_connection(client_connection):
    client_connection.close()


def client_handle(client_connection):
    while True:
    # Handle client request
        request = client_connection.recv(1024).decode()

        content = handle_request(request)

    # Return HTTP response
        client_connection.sendall(content.get_string_response())
    # break


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
    #   client_connection.getpeername() to get the IP MA DUDE



# Close socket
server_socket.close()
