#!/usr/bin/env python3
# th 2019
# loosely based on
# https://github.com/mraerino/zammad-smtp-receiver/blob/master/server.py

from http.server import BaseHTTPRequestHandler, HTTPServer
from subprocess import Popen, PIPE
import socketserver
import cgi
import os
import hashlib
import hmac
import sys

sys.stdout = sys.stderr

def verify_token(token, timestamp, signature):
    hmac_digest = hmac.new(key=os.environ['MAILGUN_API_KEY'].encode('utf-8'),
                           msg='{}{}'.format(timestamp, token).encode('utf-8'),
                           digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature.encode('utf-8'), hmac_digest.encode('utf-8'))

class S(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        print("new message")

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        if verify_token(form.getvalue('token'), form.getvalue('timestamp'), form.getvalue('signature')):
            print("token ok")
            message = form.getvalue('body-mime')
            cmd = "bundle exec rails r 'Channel::Driver::MailStdin.new(trusted: true)'"
            process = Popen(cmd, shell=True, cwd=os.environ['ZAMMAD_DIR'], stdin=PIPE)
            pipe = process.stdin
            pipe.write(message.encode('utf-8'))
            pipe.close()
            process.wait()

            if process.returncode == 0:
                print("processed")
                self._set_headers(200)
            else:
                print("not processed")
                self._set_headers(500)
        else:
            print("token not ok")
            self._set_headers(403)

def run(server_class=HTTPServer, handler_class=S, port=1337):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting get-mail...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
