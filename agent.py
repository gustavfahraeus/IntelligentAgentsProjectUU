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
            sync_reasoner(infer_property_values=True)

    def get_user(self, name):
        self.user = self.ontology.search(type = self.ontology.User, userName = name)[0]
        self.constraints = self.user.hasConstraint

    def get_restaurants(self, sc):
        options = {"scores" : {}, "good_reasons": {}, "bad_reasons": {}}

        climate = sc["climate"]
        neigh = self.user.residesIn
        city = neigh.locatedIn
        max_duration = sc["transport"]
        poss_transports = self.ontology.search(type = self.ontology.Transportation)
        if (self.ontology.BikingImpairment in self.constraints):
            poss_transports.remove(self.ontology.Biking)

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
                        new_utility = value * utility                      
                        if new_utility > utility:
                            good_reasons.append(" - This restaurant has an French Cuisine")
                        if new_utility < utility:
                            bad_reasons.append(" - This restaurant has an French Cuisine")
                        utility = new_utility

                if key == "TurkishCuisine":
                    if cuisine == self.ontology.TurkishCuisine:
                        new_utility = value * utility                       
                        if new_utility > utility:
                            good_reasons.append(" - This restaurant has an Turkish Cuisine")
                        if new_utility < utility:
                            good_reasons.append(" - This restaurant has an Turkish Cuisine")
                        utility = new_utility

            #Check pricerange
            pricerange = res.hasPriceClass
            if sc["restaurant_pref"]["pricerange"] == pricerange:
                utility *= 1.2
                good_reasons.append(" - This restaurant is in the {} pricerange".format(pricerange))
            else:
                utility *= 0.8
                bad_reasons.append(" - This restaurant is in the {} pricerange".format(pricerange))


            #Check meals on carbon footprint, allergies and nutrients
            meals_co2 = []
            meals_allergy = []
            meals_protein = []
            meals_vitamins = []
            for meal in cuisine.servesMeal:
                carbon_footprint = 0
                meal_contain = False
                proteins = 0
                vitamins = set()
                for ing in meal.hasIngredient:
                    if ing.carbonFootprint:
                        carbon_footprint += ing.carbonFootprint
                    if ing.containsAllergy:
                        for allergy in ing.containsAllergy:
                            if allergy in self.constraints:
                                meal_contain = True
                    if ing.gramsOfProteinPerMeal:
                        proteins += ing.gramsOfProteinPerMeal
                    if ing.containsVitamin:
                        for vitamin in ing.containsVitamin:
                            vitamins.add(vitamin)
                       
                meals_co2.append(carbon_footprint)
                meals_allergy.append(meal_contain)
                meals_protein.append(proteins)
                meals_vitamins.append(vitamins)

            if climate: 
                if climate > min(meals_co2):
                   utility *= 1.5
                   good_reasons.append(" - This restaurant serves at least one meal with an acceptable carbon footprint")
                else:
                   utility *= 0.5
                   bad_reasons.append(" - This restaurant serves no meals with acceptable caron footprints")
            
            if meals_allergy:
                if all(meals_allergy):
                    utility = 0
                else:
                    good_reasons.append(" - This restaurant can handle your allergy")
            
            if self.ontology.proteinDeficiency in self.constraints:
                if 30 <= max(meals_protein):
                    utility *= 1.5
                    good_reasons.append(" - This restaurant serves at least one high protein meal")
                else:
                    utility *= 0.5
                    bad_reasons.append(" - This restaurant serves no high protein meal")
            
            vitamin_deficiencies = self.ontology.search(type = self.ontology.VitaminDeficiency)
            needed_vitamins = [vitamin_deficiency.needsVitamin for vitamin_deficiency in vitamin_deficiencies if vitamin_deficiency in self.constraints]
            if needed_vitamins:
                right_vitamins = False
                for meal_vitamins in meals_vitamins:
                    if set(needed_vitamins).issubset(meal_vitamins):
                        right_vitamins = True
                        break
                if right_vitamins:    
                    utility *= 1.5
                    good_reasons.append(" - This restaurant serves at least one meal with the right vitamins")
                else: 
                    utility *= 0.5
                    bad_reasons.append(" - This restaurant serves no meal with the right vitamins")


            #Check transportation  
            score_transports = self.check_transportation(sc["transport"], climate, res.locatedIn)            
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
        movie_options = {"scores" : {}, "good_reasons": {}, "bad_reasons": {}}    #options for movies
        movie_program_options = {"scores" : {}, "good_reasons": {}, "bad_reasons": {}}   #options for moviePrograms

        #Get movies and programs
        movies = self.ontology.search(type = self.ontology.Movie)
        moviePrograms = self.ontology.search(type = self.ontology.MovieProgram)

        #.......movie Programs..........
        for movProg in moviePrograms:
            utilitys = 1
            good_reasonsS = []
            bad_reasonsS = []

            date, dateV = sc["movie_pref"]["date"]
            startBefore, startBeforeV=sc["movie_pref"]["startMovieBefore"]
            startAfter, startAfterV=sc["movie_pref"]["startMovieAfter"]
            finishBefore, finishBeforeV=sc["movie_pref"]["finishMovieBefore"]

            #check the day if correct
            if movProg.dayScheduleMovie[0] == date:  #if the day is same
                new_utilitys = utilitys * dateV
                if new_utilitys > utilitys:
                    good_reasonsS.append(" - This movie will be today")
                if new_utilitys < utilitys:
                    bad_reasonsS.append(" - This movie will be on {}".format(date))
                utilitys = new_utilitys
            #check if movie starts before
            if movProg.scheduleMovieTime < startBefore:
                new_utilitys = utilitys * startBeforeV
                good_reasonsS.append(" - This movie will start before {}".format(startBefore))
                utilitys = new_utilitys
            else:
                new_utilitys = utilitys * (2-startBeforeV)
                bad_reasonsS.append(" - This movie will start before {}".format(startBefore))
                utilitys = new_utilitys
            #check if movie starts after
            if movProg.scheduleMovieTime > startAfter:
                new_utilitys = utilitys * startAfterV
                good_reasonsS.append(" - This movie will start after {}".format(startAfter))
                utilitys = new_utilitys
            else:
                new_utilitys = utilitys * (2-startAfterV)
                bad_reasonsS.append(" - This movie will start after {}".format(startAfter))
                utilitys = new_utilitys
            #evaluate duration of movie with time
            for m in movies:    #have to take movie property duration, to compare with moviePrograms
                if movProg.presentingMovie == m:   #IMPORTANT: CHECK CONNECTION! BETWEEN MOVIE AND MOVIEPROGRAM    movProg.name == m
                    if movProg.scheduleMovieTime+m.duration < finishBefore:
                        new_utilitys = utilitys * finishBeforeV
                        good_reasonsS.append(" - This movie will end before {}".format(finishBefore))
                        utilitys = new_utilitys
                    else:
                        new_utilitys = utilitys * (2-finishBeforeV)
                        bad_reasonsS.append(" - This movie will not end before {}".format(finishBefore))
                        utilitys = new_utilitys


            #Adding movieProgram to the possibilities
            if utilitys != 0:
                movie_program_options["scores"][movProg] = utilitys
                movie_program_options["good_reasons"][movProg] = good_reasonsS
                movie_program_options["bad_reasons"][movProg] = bad_reasonsS

        #end of moviePrograms :(

        #.....movies........
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
            duration = movie.duration
            if sc["movie_pref"]["duration"] == "short":
                if duration <= 90:
                    utility *= 1.7
                    good_reasons.append(" - The duration of this movie is {}, which is a short movie".format(duration))
                if duration > 120:
                    utility *= 0.4
                    bad_reasons.append(" - The duration of this movie is {}, which is a long movie".format(duration))
            if sc["movie_pref"]["duration"] == "average":
                if duration > 90 & duration <= 120:
                    utility *= 1.7
                    good_reasons.append(" - The duration of this movie is {}, which is a average movie".format(duration))
            if sc["movie_pref"]["duration"] == "long":
                if duration <= 90:
                    utility *= 0.4
                    bad_reasons.append(" - The duration of this movie is {}, which is a short movie".format(duration))
                if duration > 120:
                    utility *= 1.7
                    good_reasons.append(" - The duration of this movie is {}, which is a long movie".format(duration))


            #Adding movie to the options
            if utility != 0:
                movie_options["scores"][movie] = utility
                movie_options["good_reasons"][movie] = good_reasons
                movie_options["bad_reasons"][movie] = bad_reasons

        #go through all moviePrograms and combine value with their movies value - update options
        options = {"scores" : {}, "good_reasons": {}, "bad_reasons": {}}
        for movie_program in movie_program_options["scores"].keys():
            movie = movie_program.presentingMovie
            #option = "{} played in {} at {}, {}".format(movie.nameMovie, movie_program.presentedIn.CinemaName, movie_program.dayScheduleMovie, movie_program.timeSchedaleMovie)
            option = "{} played in at {}, {}".format(movie.nameMovie, movie_program.dayScheduleMovie, movie_program.scheduleMovieTime)
            options["scores"][option] = movie_options["scores"][movie] * movie_program_options["scores"][movie_program]
            options["good_reasons"][option] = movie_options["good_reasons"][movie] + movie_program_options["good_reasons"][movie_program]
            options["bad_reasons"][option] = movie_options["bad_reasons"][movie] + movie_program_options["bad_reasons"][movie_program]

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