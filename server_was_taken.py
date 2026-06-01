import http.server

DIR: str = './frontend'

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<!DOCTYPE html> <h1>hello world</h1>")
        elif self.path == "/favicon.ico":
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            with open(DIR + "/favicon.ico", 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<!DOCTYPE html> <h1>no path bro &lt;/3</h1>")

    def do_POST(self):
        self.send_response(200)
        self.end_headers()


def run():
    server = http.server.HTTPServer(('0.0.0.0', 1070), MyHandler) # IDE warning is false positive
    server.serve_forever()


if __name__ == "__main__":
    run()
