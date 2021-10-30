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

    def get_user(self, name):
        self.user = self.ontology.search(type = self.ontology.User, userName = name)[0]
        self.constraints = self.user.hasConstraint

    def get_restaurants(self, sc):
        options = {"scores" : {}, "good_reasons": {}, "bad_reasons": {}}

        restaurants = self.ontology.search(type = self.ontology.Restaurant)
        for res in restaurants:
            utility = 1
            good_reasons = []
            bad_reasons = []

            #Check Cuisines
            cuisine = res.servesCuisine
            for key, value in sc["restaurant_pref"]["cuisine"].items():
                if key == "ItalianCuisine":
                    if cuisine == self.ontology.ItalianCuisine:
                        new_utility = value * utility
                        if new_utility > utility:
                            good_reasons.append(" - This restaurant has an Italian Cuisine")
                        if new_utility < utility:
                            bad_reasons.append(" - This restaurant has an Italian Cuisine")
                        utility = new_utility

                if key == "FrenchCuisine":
                    if cuisine == self.ontology.FrenchCuisine:
                        new_utility *= value                        
                        if new_utility > utility:
                            good_reasons.append(" - This restaurant has an French Cuisine")
                        if new_utility < utility:
                            bad_reasons.append(" - This restaurant has an French Cuisine")
                        utility = new_utility

                if key == "TurkishCuisine":
                    if cuisine == self.ontology.TurkishCuisine:
                        new_utility *= value                        
                        if new_utility > utility:
                            good_reasons.append(" - This restaurant has an Turkish Cuisine")
                        if new_utility < utility:
                            good_reasons.append(" - This restaurant has an Turkish Cuisine")
                        utility = new_utility
            

            #Check allergy
            #allergies = self.ontology.search(type = self.ontology.Allergy, inHasConstraint = self.user)            

            #Check nutrients

            #Check pricerange
            pricerange = res.hasPriceClass 
            if sc["restaurant_pref"]["pricerange"] == pricerange:
                utility *= 1.2
                good_reasons.append(" - This restaurant is in the {} pricerange".format(pricerange))
            else:
                utility *= 0.8
                bad_reasons.append(" - This restaurant is in the {} pricerange".format(pricerange))


            #Check co2
            #if sc["climate"]:
            #    meals_co2 = []
            #    for meal in cuisine.servesMeal:
            #        co2 = 0
            #        for ing in cuisine.hasIngredient:
            #            co2 += ing.carbonFootprint
            #        meals_co2.append(co2)
            #   if sc["climate"] > min(meals_co2):
            #       utility *= 1.5
            #       good_reasons.append(" - This restaurant serves at least one meal with an acceptable carbon footprint")
            #   else:
            #       utility *= 0.5
            #       bad_reasons.append(" - This restaurant serves no meals with acceptable caron footprints")

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
            for genre, value in sc["movie_pref"]["genre"].items():
                if movie.genreMovie[0] == genre:
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
        

        return options




            









