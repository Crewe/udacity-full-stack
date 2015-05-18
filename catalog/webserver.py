# webserver.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from RestaurantPages import list_restaurants
import cgi
import cgitb

cgitb.enable(display=0, logdir="logs")
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                session = DBSession()
                restaurants = session.query(Restaurant).all()

                output = ""
                output += "<html><body>"
                output += list_restaurants(restaurants)
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/new"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += """<form method='POST' enctype='multipart/form-data'
                          action='/restaurants'>
                          <h2>What is the restaurants name?</h2>
                          <input name='restaurant-name' type='text' />
                          <input type='submit' value='Add It' /></form>
                        """
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                
                restaurant_id = self.path.split('/')
                session = DBSession()
                restaurant = session.query(Restaurant).filter_by(id = restaurant_id[2]).one()
                if restaurant:
                    output = ""
                    output += "<html><body>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/edit' >" % restaurant_id[2]
                    output += """<h2>Edit %s?</h2>
                              <input name='restaurant-name' type='text' />
                              <input type='submit' value='Update It' /></form>
                            """ % restaurant.name
                    output += "</body></html>"
                    self.wfile.write(output)
                    print output 
                    return
            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                
                restaurant_id = self.path.split('/')
                session = DBSession()
                restaurant = session.query(Restaurant).filter_by(id = restaurant_id[2]).one()
                if restaurant:
                    output = ""
                    output += "<html><body>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/delete' >" % restaurant_id[2]
                    output += """<h2>Are you sure you wante to delete %s?</h2>
                              <input type='submit' value='Yep' /></form>
                            """ % restaurant.name
                    output += "</body></html>"
                    self.wfile.write(output)
                    print output
                return


        except IOError:
            self.send_error(404, "File Not Found %s", self.path)


    def do_POST(self):
        try:
            if self.path.endswith("/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                session = DBSession()
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant-name')
                    newRestaurant = Restaurant(name = messagecontent[0]) 
                    session.add(newRestaurant)
                    session.commit()
                    self.send_response(301)
                    self.send_header('content-type', 'text/html')
                    self.send_header('location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                session = DBSession()
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant-name')
                    restaurant_id = self.path.split('/')
                    restaurant = session.query(Restaurant).filter_by(id = restaurant_id[2]).one()
                    if restaurant:
                        session.delete(restaurant)
                        session.commit()
                        self.send_response(301)
                        self.send_header('content-type', 'text/html')
                        self.send_header('location', '/restaurants')
                        self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                session = DBSession()
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant-name')
                    restaurant_id = self.path.split('/')
                    restaurant = session.query(Restaurant).filter_by(id = restaurant_id[2]).one()
                    if restaurant:
                        restaurant.name = messagecontent[0] 
                        session.add(restaurant)
                        session.commit()
                        self.send_response(301)
                        self.send_header('content-type', 'text/html')
                        self.send_header('location', '/restaurants')
                        self.end_headers()

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
