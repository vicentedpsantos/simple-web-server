from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import cgi

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    try:
      if self.path.endswith("/restaurants"):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        restaurants = session.query(Restaurant).all()

        output = ""
        output += "<a href='restaurants/new'>Create New Restaurant</a>"
        output += "<html><body><h1>List of Current Restaurants: </h1>"

        for restaurant in restaurants:
          output += "<p> %s </p>" % restaurant.name
          output += "<a href='restaurants/%s/edit'>Edit</a><br>" % restaurant.id
          output += "<a href='restaurants/%s/delete'>Delete</a>" % restaurant.id

        output+= "</body></html>"
        self.wfile.write(output)
        print output
        return
      
      if self.path.endswith("/restaurants/new"):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        output = ""
        output += "<html><body><br>"
        output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h3>Please enter the name of the new restaurant below: </h3><br><input name="restaurantName" type="text"><input type="submit" value="Submit"> </form>'''
        output += "</body></html>"
        self.wfile.write(output)
        print output
        return
      
      if self.path.endswith("/edit"):
        restaurantIDPath = self.path.split("/")[2]
        myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
        if myRestaurantQuery:
          self.send_response(200)
          self.send_header('Content-type', 'text/html')
          self.end_headers()
          output = "<html><body>"
          output += "<h1>"
          output += myRestaurantQuery.name
          output += "</h1>"
          output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/edit' >" % restaurantIDPath
          output += "<input name = 'newRestaurantName' type='text' placeholder = '%s' >" % myRestaurantQuery.name
          output += "<input type = 'submit' value = 'Rename'>"
          output += "</form>"
          output += "</body></html>"

          self.wfile.write(output)
      
      if self.path.endswith("/delete"):
        restaurantIDPath = self.path.split("/")[2]
        myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
        if myRestaurantQuery:
          self.send_response(200)
          self.send_header('Content-type', 'text/html')
          self.end_headers()
          output = ""
          output += "<html><body>"
          output += "<h1>Are you sure you want to delete %s?" % myRestaurantQuery.name
          output += "<form method='POST' enctype = 'multipart/form-data' action = '/restaurants/%s/delete'>" % restaurantIDPath
          output += "<input type = 'submit' value = 'Delete'>"
          output += "</form>"
          output += "</body></html>"

          self.wfile.write(output)


    except IOError:
      self.send_error(404, "File Not Found %s" % self.path)

  def do_POST(self):
      try:
        if self.path.endswith("/edit"):
          ctype, pdict = cgi.parse_header(
          self.headers.getheader('content-type'))
          if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(self.rfile, pdict)
            messagecontent = fields.get('newRestaurantName')
            restaurantIDPath = self.path.split("/")[2]

            myRestaurantQuery = session.query(Restaurant).filter_by(
            id=restaurantIDPath).one()
            if myRestaurantQuery != []:
              myRestaurantQuery.name = messagecontent[0]
              session.add(myRestaurantQuery)
              session.commit()
              self.send_response(301)
              self.send_header('Content-type', 'text/html')
              self.send_header('Location', '/restaurants')
              self.end_headers()

        if self.path.endswith("/restaurants/new"):
          ctype, pdict = cgi.parse_header(
          self.headers.getheader('content-type'))
          if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(self.rfile, pdict)
            messagecontent = fields.get('restaurantName')

            # Create new Restaurant Object
            newRestaurant = Restaurant(name=messagecontent[0])
            session.add(newRestaurant)
            session.commit()

            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()
        
        if self.path.endswith("/delete"):
          restaurantIDPath = self.path.split("/")[2]
          myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
          if myRestaurantQuery:
            session.delete(myRestaurantQuery)
            session.commit()
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()

      except:
          pass

def main():
  try:
    port = 8080
    server = HTTPServer(('',port), webServerHandler)
    print "Web server is running on port %s" % port
    server.serve_forever()

  except KeyboardInterrupt:
    print "Ctrl+C entered, stopping webserver..."
    server.socket.close()

if __name__ == '__main__':
  main()