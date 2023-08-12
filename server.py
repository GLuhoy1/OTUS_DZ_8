import socket
import re
from http import HTTPStatus

BROWSERS = ['Mozilla', 'Chrome', 'Safari', 'Edge', 'Opera']


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip


def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 0))
    free_port = s.getsockname()[1]
    s.close()
    return free_port


HOST = get_local_ip()
PORT = find_free_port()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_s:
    srv_addr = (HOST, PORT)
    server_s.bind(srv_addr)
    server_s.listen(1)
    print(f'Server start on: {HOST}:{PORT}')
    print(f'Example request link\n '
          f'http://{HOST}:{PORT}/?status=404 ')

    while True:
        print('Waiting for a new connection')

        conn, raddr = server_s.accept()
        print(f'Connection from {raddr}')

        data = conn.recv(2048)
        text = data.decode('utf-8')

        if text:
            http_method = 'GET'
            http_status = HTTPStatus.OK
            status_match = re.search(r'/\?status=(\d+)', text)
            if status_match:
                status_code = int(status_match.group(1))
                try:
                    http_status = HTTPStatus(status_code)
                except ValueError:
                    pass

            headers = {}
            lines = text.split('\r\n')
            for line in lines[1:]:
                if line:
                    header_name, header_value = line.split(': ', 1)
                    headers[header_name] = header_value

            response_body = f"Request Method: {http_method}\n"
            response_body += f"Request Source: {raddr[0]}:{raddr[1]}\n"
            response_body += f"Response Status: {http_status.value} {http_status.phrase}\n"

            for header_name, header_value in headers.items():
                response_body += f"{header_name}: {header_value}\n"

            response = f"HTTP/1.1 {http_status.value} {http_status.phrase}\r\n"
            response += "Content-Type: text/plain\r\n"
            response += f"Content-Length: {len(response_body.encode('utf-8'))}\r\n"
            response += "\r\n"
            response += response_body

            conn.send(response.encode('utf-8'))
        else:
            break

        conn.close()
