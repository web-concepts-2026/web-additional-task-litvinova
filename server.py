import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 8080))
server.listen()
print("Listening on http://127.0.0.1:8080")

while True:
    conn, addr = server.accept()
    data = conn.recv(4096)
    print(data.decode())
    conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nHello")
    conn.close()