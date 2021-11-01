from owlready2 import *
from pprint import pprint
import operator
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
        self.neigh = self.user.residesIn
        self.city = self.neigh.locatedIn
        self.poss_transports = self.ontology.search(type = self.ontology.Transportation)        
        if (self.ontology.BikingImpairment in self.constraints):
            self.poss_transports.remove(self.ontology.Biking)

    def get_restaurants(self, sc):
        options = {"scores" : {}, "good_reasons": {}, "bad_reasons": {}}
        
        climate = sc["climate"]        
        
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

            #Check nutrients

            #Check pricerange
            pricerange = res.hasPriceClass 
            if sc["restaurant_pref"]["pricerange"] == pricerange:
                utility *= 1.2
                good_reasons.append(" - This restaurant is in the {} pricerange".format(pricerange))
            else:
                utility *= 0.8
                bad_reasons.append(" - This restaurant is in the {} pricerange".format(pricerange))


            #Check co2 and allergies of meals
            if climate:
                meals_co2 = []
                meals_allergy = []
                for meal in cuisine.servesMeal:
                    co2 = 0
                    meal_contain = False
                    for ing in meal.hasIngredient:
                        if ing.carbonFootprint: #change this in ontology so every ingredient has an carbonFootprint
                            co2 += ing.carbonFootprint
                        if ing.containsAllergy:
                            for allergy in ing.containsAllergy:
                                if allergy in self.constraints:
                                    meal_contain = True
                           
                    meals_co2.append(co2)
                    meals_allergy.append(meal_contain)

                if climate > min(meals_co2):
                   utility *= 1.5
                   good_reasons.append(" - This restaurant serves at least one meal with an acceptable carbon footprint")
                else:
                   utility *= 0.5
                   bad_reasons.append(" - This restaurant serves no meals with acceptable caron footprints")
                
                if meals_allergy:
                    if all(meals_allergy):
                        print(res)
                        utility = 0
                    else:
                        good_reasons.append(" - This restaurant can handle your allergy")
                
            

            #Check transportation  
            score_transports = self.check_transportation(sc["transport"], climate, res)            
            if score_transports["score"]:
                max_uti = max(score_transports["score"].values())
                max_transports = [trans for (trans, score) in score_transports["score"].items() if score == max_uti]
                new_utility = utility*max_uti
                if new_utility > utility:
                    for trans in max_transports:
                        good_reasons.append(score_transports["reason"][trans])
                else:
                    for trans in max_transports:
                        bad_reasons.append(score_transports["reason"][trans])
                utility = new_utility
            else:
                utility = 0




            if utility != 0:
                restaurant = res.restaurantName
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

    def check_transportation(self, max_duration, climate, location):   
        score_transports = {}          
        score_transports["score"] = {}
        score_transports["reason"] = {}

        if self.neigh in location:
            #same neighbourhood
            for transport in self.poss_transports:
                if transport.sameNeighbourhoodDuration:
                    if (max_duration < transport.sameNeighbourhoodDuration) & (climate > transport.carbonFootprint):
                        score_transports["score"][transport] = 1.5
                        score_transports["reason"][transport] = " - You can {} to this restaurant".format(transport.action)
                    elif climate > transport.carbonFootprint:
                        score_transports["score"][transport] = 0.8
                        score_transports["reason"][transport] = " - You can {} to this restaurant, but it takes {} minutes".format(transport.action, transport.sameNeighbourhoodDuration)
                    elif  max_duration < transport.sameNeighbourhoodDuration:
                        score_transports["score"][transport] = 0.8
                        score_transports["reason"][transport] = " - You can {} to this restaurant, but it has a carbon footprint of {}".format(transport.action, transport.carbonFootprint)                  
                        
        elif self.city in location:
            #same city
            for transport in self.poss_transports:
                if transport.sameCityDuration:
                    if (max_duration < transport.sameCityDuration) & (climate > transport.carbonFootprint):
                        score_transports["score"][transport] = 1.5
                        score_transports["reason"][transport] = " - You can {} to this restaurant".format(transport.action)
                    elif climate > transport.carbonFootprint:
                        score_transports["score"][transport] = 0.8
                        score_transports["reason"][transport] = " - You can {} to this restaurant, but it takes {} minutes".format(transport.action, transport.sameCityDuration)
                    elif  max_duration < transport.sameCityDuration:
                        score_transports["score"][transport] = 0.8
                        score_transports["reason"][transport] = " - You can {} to this restaurant, but it has a carbon footprint of {}".format(transport.action, transport.carbonFootprint)
        else:
            #other city
            for transport in self.poss_transports:
                if transport.otherCityDuration:
                    if (max_duration < transport.otherCityDuration) & (climate > transport.carbonFootprint):
                        score_transports["score"][transport] = 1.5
                        score_transports["reason"][transport] = " - You can {} to this restaurant".format(transport.action)
                    elif climate > transport.carbonFootprint:
                        score_transports["score"][transport] = 0.8
                        score_transports["reason"][transport] = " - You can {} to this restaurant, but it takes {} minutes".format(transport.action, transport.otherCityDuration)
                    elif  max_duration < transport.otherCityDuration:
                        score_transports["score"][transport] = 0.8
                        score_transports["reason"][transport] = " - You can {} to this restaurant, but it has a carbon footprint of {}".format(transport.action, transport.carbonFootprint)         
        
        return score_transports