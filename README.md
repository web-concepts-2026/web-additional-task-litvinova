# Basic HTTP server

Simple HTTP server in Python. 
The server reads the request, gets the method, path, query parameters, headers and body, and sends a response.

## How to run

python3 server.py

Open http://127.0.0.1:8080 in browser.

## Pages

- `/` - main page (index.html + styles.css)
- `/page?id=5` - shows query parameters
- `POST /api` - send JSON, get JSON back

## Test POST

curl -X POST -H "Content-Type: application/json" -d '{"name": "test"}' http://127.0.0.1:8080/api