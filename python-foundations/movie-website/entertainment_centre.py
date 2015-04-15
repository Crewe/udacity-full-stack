import fresh_tomatoes
import media

inception = media.Movie(
    "Inception",
    "Your mind is the scene of crime",
    "https://upload.wikimedia.org/wikipedia/en/7/7f/Inception_ver3.jpg",
    "https://www.youtube.com/watch?v=8hP9D6kZseM")

bourne_identity = media.Movie(
    "Bourne Identity, The",
    "He was the perfect weapon until he became the target.",
    "https://upload.wikimedia.org/wikipedia/en/a/ae/BourneIdentityfilm.jpg",
    "https://www.youtube.com/watch?v=cD-uQreIwEk")

jurassic_park = media.Movie(
    "Jurassic Park",
    "An adventure 65 million years in the making.",
    "https://upload.wikimedia.org/wikipedia/en/c/c7/Jurassic_Park_3D.jpg",
    "https://www.youtube.com/watch?v=lc0UehYemQA")

kingsmen = media.Movie(
    "Kingsman: The Secret Service",
    "Her Majesty's Secret Service",
    "https://upload.wikimedia.org/wikipedia/en/8/8b/Kingsman_The_Secret_Service_poster.jpg",
    "https://www.youtube.com/watch?v=kl8F-8tR8to")

awkward_adventure = media.Movie(
    "My Awkward Sexual Adventure",
    """ 
    To win back his ex-girlfriend, a conservative accountant enlists the 
    help of an exotic dancer to guide him on a quest for sexual experience...""",
    "http://ia.media-imdb.com/images/M/MV5BMjI5MTYzOTMyNF5BMl5BanBnXkFtZTcwNTgwNDYzOQ@@._V1__SX1656_SY855_.jpg",
    "https://www.youtube.com/watch?v=2Tw-FF4-Fxk")

the_box = media.Movie(
    "Box, The",
    "You are the experiment.",
    "http://ia.media-imdb.com/images/M/MV5BMTI4MDA5NjIwM15BMl5BanBnXkFtZTcwNTA2MjY0Mg@@._V1__SX1656_SY855_.jpg",
    "https://www.youtube.com/watch?v=2Tw-FF4-Fxk")

interstellar = media.Movie(
    "Interstellar",
    "Mankind was born on Earth. It was never meant to die here.",
    "http://ia.media-imdb.com/images/M/MV5BMjIxNTU4MzY4MF5BMl5BanBnXkFtZTgwMzM4ODI3MjE@._V1__SX1656_SY855_.jpg",
    "https://www.youtube.com/watch?v=zSWdZVtXT7E")

gravity = media.Movie(
    "Gravity",
    "Don't Let Go.",
    "http://ia.media-imdb.com/images/M/MV5BNjE5MzYwMzYxMF5BMl5BanBnXkFtZTcwOTk4MTk0OQ@@._V1__SX1656_SY855_.jpg",
    "https://www.youtube.com/watch?v=OiTiKOy59o4")

the_cube = media.Movie(
    "Cube, The",
    "Don't look for a reason... Look for a way out.",
    "http://ia.media-imdb.com/images/M/MV5BMTAyMjI4NTEzNTNeQTJeQWpwZ15BbWU3MDY3NjIxMjE@._V1__SX1656_SY855_.jpg",
    "https://www.youtube.com/watch?v=HYoTGYT0-I4")


#media.Movie("", "", "", "")

movies = [inception, bourne_identity, interstellar,
          jurassic_park, kingsmen, awkward_adventure,
          the_box, gravity, the_cube]

fresh_tomatoes.open_movies_page(movies)
