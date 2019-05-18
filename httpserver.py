"""
 Implements a simple HTTP/1.0 Server

"""

import socket
import time
import threading
import json


image_type = ["png", "jpg"]


class Response:
    def __init__(self, connectionType="keep-alive", body='', contentType=None, status="Unknown", length=0):

        self.body = body
        self.status = status     # HTTP/1.0 200 OK, etc
        self.date = time.strftime("%a, %d %b %Y %H:%M:%S")
        self.contentType = contentType
        self.connectionType = connectionType
        self.length = length

    def get_string_response(self):
        response = self.status + "\n"
        response += 'Date: ' + self.date + "\n"
        response += 'Content-Length: {}'.format(self.length)+"\n"
        #   imagem/text
        if self.contentType is not None:
            response += 'Content-Type: {} '.format(self.contentType) + "\n"
        # Keep-Alive / Close
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
        self.verbo = get_content[0]      # Get / Post / Head

        self.path = get_content[1]
        if self.path == '/':
            self.path = '/index.html'

        #   Meter a basePath
        self.path = 'htdocs' + self.path

        #   Ir buscar o file name ao path
        arr = self.path.split('/')
        self.filename = arr[len(arr)-1]

        #   If is the post function, the file type is json
        if self.verbo == "POST":

            self.filetype = "application/json"
            self.path = ""
            self.post_content = headers[len(headers)-1]

        #   Get the file type (if is text or not)
        elif self.filename.split('.')[1] in image_type:
            self.filetype = '{}/{}'.format("images", self.filename.split('.')[1])
        #   Else is a text file
        else:
            self.filetype = "text/html"

        #   Get Connection type (close, keep-alive, etc)
        self.connectionType = headers[len(headers)-3].split(":")[1]


    def getContent(self):
        try:
            if self.verbo == "POST":

                line = self.post_content.split("&")

                array = []
                """
                json_file = open("./data.json", "r")
                data1 = json.load(json_file)
                print("DATA GUARDADA")
                # print(data1)
                json_file.close()
                array.append(json.dumps(data1))
                """
                print(array)

                dataAux = {}

                #   Put new data in the dict
                for l in line:
                    value = l.split("=")[1]     # value
                    key = l.split("=")[0]       # key
                    dataAux[key] = value        # add to the dictionary

                array.append(dataAux)
                # data = json.dumps(dataAux)
                print("POST AQUI")

                data = json.dumps(array)
                json_file = open("./data.json", "w")
                json.dump(data, json_file)
                json_file.close()

                data = json.loads(data)

                return json.dumps(data)

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

cache = {}

# def get_cache():


def add_log(client, request_url):
    f = open("log.txt", "a")
    f.write("IP = {} | URL = {}\n".format(client, request_url))
    f.close()


def handle_request(request, client):
    """Returns file content for client request"""

    # Parse headers
    print("Request:"+request)
    headers = request.split('\n')
    time.sleep(1)
    re = Request(headers=headers)

    add_log(client.getpeername(), re.path)

    try:
        if re.isPrivate():
            return Response(status="HTTP/1.0 403 Forbidden", body="Private link",
                            connectionType="close")

        body = re.getContent()

        if re.verbo == "HEAD":
            return Response(status="HTTP/1.0 200 OK", connectionType="close", length=len(body))

    #   If is a Bad Request
    except PermissionError:
        return Response(status="HTTP/1.0 400 Bad Request", body="Bad Request", connectionType="close")

    #   If the file doesn't exist
    except FileNotFoundError:
        return Response(status="HTTP/1.0 404 Not Found", body="File Not Found", connectionType="close")

    # Return response
    return Response(status="HTTP/1.0 200 OK", body=body, contentType=re.filetype,
                    connectionType=re.connectionType, length=len(body))


def close_connection(client_connection):
    client_connection.close()
    print('closing timer')


def client_handle(client_connection):
    while True:
        # Handle client request
        timer = threading.Timer(interval=10.0, function=close_connection, args=[client_connection])
        timer.start()

        try:
            request = client_connection.recv(1024).decode()
            content = handle_request(request, client_connection)

            timer.cancel()

            # Return HTTP response
            client_connection.sendall(content.get_string_response())

            if content.connectionType == "close":

                close_connection(client_connection)
                print('Closing in!')
                break

        except ConnectionAbortedError:
            print('Time out')
            break
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


def server_start():
    while True:
        # Wait for client connections
        client_connection, client_address = server_socket.accept()

        thread = threading.Thread(target=client_handle, args=(client_connection,))
        thread.start()
        #   client_connection.getpeername() to get the IP MA DUDE

    # Close socket
    server_socket.close()


server_start()