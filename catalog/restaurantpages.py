# RestaurantPages.py

def list_restaurants(restaurants):
    output = ""
    output += "<h2>Restaurants</h2>"
    output += '<div id="menu">'
    output += '<div class="menu-button"><a href="./new"> Make A New Restaurant </a></div>'
    output += "</div>"
    for restaurant in restaurants:
        output += '<div id="rest-%s" class="restaurant">' % restaurant.id
        output += '<div class="restaurant-name">%s</div>' % restaurant.name
        output += '<span class="button-edit"><a href="/restaurant/%s/edit"> Edit </a></span>' % restaurant.id
        output += '<span class="button-delete"><a href="/restaurant/%s/delete"> Delete </a></span>' % restaurant.id
        output += '</div>'
    return output
