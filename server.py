import socket
import json

HOST = "127.0.0.1"
PORT = 8080


def read_request(conn):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(1024)
        if not chunk:
            return None
        data += chunk

    head, _, body = data.partition(b"\r\n\r\n")
    head = head.decode("utf-8")


    length = 0
    for line in head.split("\r\n"):
        if line.lower().startswith("content-length:"):
            length = int(line.split(":")[1])

    while len(body) < length:
        chunk = conn.recv(1024)
        if not chunk:
            break
        body += chunk

    return head, body.decode("utf-8")


def parse_request(head):
    lines = head.split("\r\n")

    method, full_path, version = lines[0].split(" ")

    path, _, query_string = full_path.partition("?")

    query = {}
    if query_string:
        for pair in query_string.split("&"):
            key, _, value = pair.partition("=")
            query[key] = value

    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()

    return method, path, query, headers


def send_response(conn, status, content_type, body):
    if isinstance(body, str):
        body = body.encode("utf-8")

    head = "HTTP/1.1 " + status + "\r\n"
    head += "Content-Type: " + content_type + "\r\n"
    head += "Content-Length: " + str(len(body)) + "\r\n"
    head += "Connection: close\r\n"
    head += "\r\n"

    conn.sendall(head.encode("utf-8") + body)


def serve_file(conn, path):
    if path == "/":
        path = "/index.html"

    
    if ".." in path:
        send_response(conn, "404 Not Found", "text/plain", "404 Not Found")
        return

    if path.endswith(".css"):
        content_type = "text/css"
    else:
        content_type = "text/html; charset=utf-8"

    try:
        with open("static" + path, "rb") as file:
            content = file.read()
        send_response(conn, "200 OK", content_type, content)
    except OSError:
        send_response(conn, "404 Not Found", "text/plain", "404 Not Found")

def page(conn, query):
    page_id = query.get("id", "unknown")

    html = "<h1>Page " + page_id + "</h1>"
    html += "<p>Query parameters:</p><ul>"
    for key, value in query.items():
        html += "<li>" + key + " = " + value + "</li>"
    html += "</ul>"

    send_response(conn, "200 OK", "text/html; charset=utf-8", html)


def handle_post(conn, headers, body):
    if "application/json" not in headers.get("content-type", ""):
        send_response(conn, "415 Unsupported Media Type", "text/plain", "Send JSON please")
        return

    try:
        data = json.loads(body)
    except ValueError:
        answer = json.dumps({"error": "invalid JSON"})
        send_response(conn, "400 Bad Request", "application/json", answer)
        return

    answer = json.dumps({"message": "JSON received", "you_sent": data}, ensure_ascii=False)
    send_response(conn, "200 OK", "application/json; charset=utf-8", answer)


        
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
print("Server is running on http://" + HOST + ":" + str(PORT))



while True:
    conn, addr = server.accept()
    try:
        request = read_request(conn)
        if request:
            head, body = request
            method, path, query, headers = parse_request(head)

            print(method, path)
            print("Query:", query)
            print("Headers:", headers)
            print("Body:", body)

            if method == "GET" and path == "/page":
                page(conn, query)
            elif method == "GET":
                serve_file(conn, path)
            elif method == "POST" and path == "/api":
                handle_post(conn, headers, body)
            else:
                send_response(conn, "405 Method Not Allowed", "text/plain", "Method not allowed")
    except Exception as error:
        print("Error:", error)
        send_response(conn, "400 Bad Request", "text/plain", "Bad request")

    conn.close()