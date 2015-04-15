import webbrowser


class Movie():

    """ The Movie class. Has general details about movies such
            as it's title short synopsis, it's poster image, and
            trailer video URL to name a few. """

    # A list of ratings that can be applied to the movie
    VALID_RATINGS = ["G", "PG", "PG-13", "R"]

    def __init__(self, movie_title, movie_storyline,
                 poster_image, trailer_youtube):

        self.title = movie_title
        self.storyline = movie_storyline
        self.poster_image_url = poster_image
        self.trailer_youtube_url = trailer_youtube


    def show_trailer(self):
        """Opens the default browser to show the web page."""
        webbrowser.open(self.trailer_youtube_url)
