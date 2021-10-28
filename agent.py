from owlready2 import *
from pprint import pprint
owlready2.JAVA_EXE = "C:/Users/xelfj/Downloads/Protege-5.5.0-win/Protege-5.5.0/jre/bin/java.exe" # Change this to whatever on your own system. Don't know how to work around this yet.

# We are developing a utility based Agent.
class Agent:

    def __init__(self):
        # Load the desired ontology using the path file
        self.ontology = get_ontology('./group11.owl').load()

        with self.ontology:
            sync_reasoner()

    def get_restaurants(self, sc):
        options = {"scores" : {}, "good_reasons": {}, "bad_reasons": {}}

        restaurants = self.ontology.search(type = self.ontology.Restaurant)
        for res in restaurants:
            utility = 1
            good_reasons = []
            bad_reasons = []

            #Check Cuisines
            for key, value in sc["restaurant_pref"]["cuisine"].items():
                if key == "ItalianCuisine":
                    resI = self.ontology.search(servesCuisine = self.ontology.ItalianCuisine)
                    if res in list(resI):
                        new_utility = value * utility
                        if new_utility > utility:
                            good_reasons.append(" - This restaurant has an Italian Cuisine")
                        if new_utility < utility:
                            bad_reasons.append(" - This restaurant has an Italian Cuisine")
                        utility = new_utility

                if key == "FrenchCuisine":
                    resF = self.ontology.search(servesCuisine = self.ontology.FrenchCuisine)
                    if res in list(resF):
                        new_utility *= value                        
                        if new_utility > utility:
                            good_reasons.append(" - This restaurant has an French Cuisine")
                        if new_utility < utility:
                            bad_reasons.append(" - This restaurant has an French Cuisine")
                        utility = new_utility

                if key == "TurkishCuisine":
                    resT = self.ontology.search(servesCuisine = self.ontology.TurkishCuisine)
                    if res in list(resT):
                        new_utility *= value                        
                        if new_utility > utility:
                            good_reasons.append(" - This restaurant has an Turkish Cuisine")
                        if new_utility < utility:
                            good_reasons.append(" - This restaurant has an Turkish Cuisine")
                        utility = new_utility
            

            #Check allergy
            #users = self.ontology.search(user = "*")
            #user = [u for u in users if u.name[0] == sc["user"]][0]
            #print(self.ontology.search(hasAllergy = "*"))

            #Check nutrients

            #Check pricerange

            if utility != 0:
                restaurant = res.restaurantName[0]
                options["scores"][restaurant] = utility
                options["good_reasons"][restaurant] = good_reasons
                options["bad_reasons"][restaurant] = bad_reasons
        
        return options

    def get_movies(self, sc):
        options = {"scores" : {}, "good_reasons": {}, "bad_reasons": {}}

        #Get movies that are at the right time
        movies = self.ontology.search(type = self.ontology.Movie)

        for movie in movies:
            utility = 1
            good_reasons = []
            bad_reasons = []

            #Check genre
            for genre, value in sc["movie_pref"]["genre"]:
                if movie.genre[0] == genre:
                    new_utility = utility * value
                    if new_utility > utility:
                        good_reasons.append(" - This movie is a {}".format(genre))
                    if new_utility < utility:
                        bad_reasons.append(" - This movie is a {}".format(genre))
                    utility = new_utility

            #Check for duration
            duration = movie.duration[0]
            if sc["movie_pref"]["duration"] == "short":
                if duration <= 90:
                    utility *= 1.7
                    good_reasons.append(" - The duration of this movie is {}, which is a short movie".format(movie.duration[0]))
                if duration > 120:
                    utility *= 0.4
                    bad_reasons.append(" - The duration of this movie is {}, which is a long movie".format(movie.duration[0]))
            if sc["movie_pref"]["duration"] == "average":
                if duration > 90 & duration <= 120:
                    utility *= 1.7
                    good_reasons.append(" - The duration of this movie is {}, which is a average movie".format(movie.duration[0]))
            if sc["movie_pref"]["duration"] == "long":
                if duration <= 90:
                    utility *= 0.4
                    bad_reasons.append(" - The duration of this movie is {}, which is a short movie".format(movie.duration[0]))
                if duration > 120:
                    utility *= 1.7
                    good_reasons.append(" - The duration of this movie is {}, which is a long movie".format(movie.duration[0]))
            


            #Adding movie to the options
            if utility != 0:
                movie_name = movie.nameMovie[0]
                options["scores"][movie_name] = utility
                options["good_reasons"][movie_name] = good_reasons
                options["bad_reasons"][movie_name] = bad_reasons




            









