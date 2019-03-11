#!/usr/bin/env python3
# th 2019
# loosely based on
# https://github.com/mraerino/zammad-smtp-receiver/blob/master/server.py

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from subprocess import Popen, PIPE
import SocketServer
import cgi
import os
import hashlib, hmac

def verify_token(token, timestamp, signature):
    hmac_digest = hmac.new(key=os.environ['MAILGUN_API_KEY'],
                           msg='{}{}'.format(timestamp, token),
                           digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(unicode(signature), unicode(hmac_digest))

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        if verify_token(form.getvalue('token'), form.getvalue('timestamp'), form.getvalue('signature')):
            message = form['body-mime']
            pipe = Popen("echo bundle exec rails r 'Channel::Driver::MailStdin.new(trusted: true)'", shell=True, cwd=os.environ['ZAMMAD_DIR'], stdin=PIPE).stdin
            pipe.write(message.encode('utf-8'))
            pipe.close()
            self._set_headers()
            return
        
        self.send_response(500)
        
def run(server_class=HTTPServer, handler_class=S, port=1337):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting get-mail...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
