scenario1 = {
    "user": "Peter",
    "climate": True,
    "transport": 25,
    "actions": {"restaurant" : 1, "cinema" : 0, "foodstore" : 0},
    "restaurant_pref":
    {
        "cuisine":{"FrenchCuisine":1.5}
    },

}
scenario2 = {
    "user": "Peter",
    "transport": 24,
    "actions": {"restaurant" : 1, "cinema" : 0, "foodstore" : 0},
    "restaurant_pref":
    {
        "pricerange": "Cheap"
    }
}
scenario3 = {
    "user": "Rebecca",
    "transport": 22,
    "actions": {"restaurant" : 0, "cinema" : 1, "foodstore" : 0},
    "movie_pref":
        {   "genre": {"horror": 0.3, "comedy": 0.2, "drama": 1.7, "romantic": 1.8},
            "date": ("Friday", 2.0),
            "startMovieBefore": (1820, 1.5),
            "startMovieAfter": (1820, 0.8),
            "finishMovieBefore": (2200, 1.6)
            },
}
scenario4= {
    "user": "Mark",
    "transport": 20,
    "actions": {"restaurant" : 1, "cinema" : 1, "foodstore" : 0},
    "restaurant_pref":
    {
        "pricerange": "Expensive",
        "cuisine":{"ItalianCuisine":1.5, "FrenchCuisine": 0.2}
    },
    "movie_pref":
        {   "genre": {"romantic": 0.1},
            "date": ("Tuesday", 2.0),
            },
}


""" scenario5 = {   "user": "Alice",
                "climate": True,
                "transport": 20,
                "actions": {"cinema" : 1, "restaurant" : 0, "foodstore" : 0},
                "day": "monday",
                "movie_pref":
                    {   "genre": {"scary": 0.2, "french": 0.7, "romantic": 2, "comedy": 2, "drama": 0.7, "superhero": 0.1},
                        "date": ("Tuesday", 1.5),
                        "startMovieBefore": (2000, 2.0),
                        "startMovieAfter": (1700, 1.5),
                        "finishMovieBefore": (2200, 1.3),
                        "duration": "long"},
                "restaurant_pref":
                    {   "cuisine": {"ItalianCuisine" : 1.5, "FrenchCuisine": 0.8, "TurkishCuisine": 0.5},
                        "pricerange": "Moderate",        }   }
"""
