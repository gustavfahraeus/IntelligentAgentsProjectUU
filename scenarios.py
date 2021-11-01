scenario1 = {   "user": "Alice",
                "climate": 20,
                "transport": 20,
                "actions": {"cinema" : 1, "restaurant" : 0, "foodstore" : 0},
                "day": "monday",    #added by Juri/ to decide, what day it is
                "movie_pref":
                    {   "genre": {"scary": 0.2, "french": 0.7, "romantic": 2, "comedy": 2, "drama": 0.7, "superhero": 0.1},
                        "date": ("Tuesday", 1.5),
                        "startMovieBefore": (2000, 2),
                        "startMovieAfter": (1700, 1.5),
                        "finishMovieBefore": (2200, 1.3),
                        "duration": "long"},
                "restaurant_pref":
                    {   "cuisine": {"ItalianCuisine" : 1.5, "FrenchCuisine": 0.8, "TurkishCuisine": 0.5},
                        "pricerange": "Moderate",        }   }
