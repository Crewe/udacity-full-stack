# webserver.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>HELLO RYAN"
                output += """<form method='POST' enctype='multipart/form-data'
                          action='/hello'>
                          <h2>What do you want me to say?</h2>
                          <input name='message' type='text' />
                          <input type='submit' value='Say It!' /></form>
                        """
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/ohayou"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                output = ""
                output += """<html><body>&#x304A;&#x306F;&#x3068;&#x3046;<br />
                             <a href='/hello'>Back to hello.</a>
                          """
                output += """<form method='POST' enctype='multipart/form-data'
                          action='/hello'>
                          <h2>What do you want me to say?</h2>
                          <input name='message' type='text' />
                          <input type='submit' value='Say It!' /></form>
                        """
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, "File Not Found %s", self.path)


    def do_POST(self):
        try:
            self.send_response(301)
            self.end_headers()

            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')

            output = ""
            output += "<HTML><body>"
            output += "<h2>Okay, how about this:</h2>"
            output += "<h1>%s</h1>" % messagecontent[0]
        
            output += """<form method='POST' enctype='multipart/form-data'
                          action='/hello'>
                          <h2>What do you want me to say?</h2>
                          <input name='message' type='text' />
                          <input type='submit' value='Say It!' /></form>
                        """
            output += "</body></HTML>"
            print output
            self.wfile.write(output)
            print output

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print "The server is running on port %s" % port
        server.serve_forever()


    except KeyboardInterrupt:
        print "^C entered, stopping the web server..."
        server.socket.close()

if __name__ == '__main__':
    main()
