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
        self.neigh = self.user.residesIn
        self.city = self.neigh.locatedIn
        self.poss_transports = self.ontology.search(type = self.ontology.Transportation)
        if (self.ontology.BikingImpairment in self.constraints):
            self.poss_transports.remove(self.ontology.Biking)
        if self.neigh not in self.ontology.search(hasTrainStation = "*"):
            self.poss_transports.remove(self.ontology.Train)
        if (self.ontology.noLicense in self.constraints):
            self.poss_transports.remove(self.ontology.ElectricCar)
            self.poss_transports.remove(self.ontology.GasolineCar)

    def get_restaurants(self, sc):
        options = {"scores" : {}, "good_reasons": {}, "bad_reasons": {}}

        climate = sc["climate"]
        max_duration = sc["transport"]

        restaurants = self.ontology.search(type = self.ontology.Restaurant)
        for res in restaurants:
            utility = 1
            good_reasons = []
            bad_reasons = []
            cuisine = res.servesCuisine

            #Check Cuisines
            if "cuisine" in sc["restaurant_pref"].keys():
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
            if "pricerange" in sc["restaurant_pref"].keys():
                pricerange = res.hasPriceClass
                if sc["restaurant_pref"]["pricerange"] == pricerange:
                    utility *= 1.2
                    good_reasons.append(" - This restaurant is in the {} pricerange".format(pricerange))
                else:
                    utility *= 0.8
                    bad_reasons.append(" - This restaurant is in the {} pricerange".format(pricerange))


            #Check meals on carbon footprint, allergies and nutrients
            vitamin_deficiencies = self.ontology.search(type = self.ontology.VitaminDeficiency)
            needed_vitamins = [vitamin_deficiency.needsVitamin for vitamin_deficiency in vitamin_deficiencies if vitamin_deficiency in self.constraints]

            meals = {}
            meals["scores"] = {}
            meals["reasons"] = {}
            for meal in cuisine.servesMeal:
                meal_score = 1
                meal_good_reasons = []
                meal_bad_reasons = []
                meal_carbon_footprint = 0
                meal_contain_allergy = False
                meal_proteins = 0
                meal_vitamins = set()
                for ing in meal.hasIngredient:
                    if ing.carbonFootprint:
                        meal_carbon_footprint += ing.carbonFootprint
                    if ing.containsAllergy:
                        for allergy in ing.containsAllergy:
                            if allergy in self.constraints:
                                meal_contain_allergy = True
                    if ing.gramsOfProteinPerMeal:
                        meal_proteins += ing.gramsOfProteinPerMeal
                    if ing.containsVitamin:
                        for vitamin in ing.containsVitamin:
                            meal_vitamins.add(vitamin)

                if climate:
                    if meal_carbon_footprint <= 20:
                        meal_score *= 1.5
                        meal_good_reasons.append("a low carbon footprint")
                    else: 
                        meal_score *= 0.7
                        meal_bad_reasons.append("a high carbon footprint")
            
                if meal_contain_allergy:
                    meal_score = 0
                else:
                    meal_good_reasons.append("does not affect your allergy(ies)")
                
                if self.ontology.proteinDeficiency in self.constraints:
                    if 30 <= meal_proteins:
                        meal_score *= 1.5
                        meal_good_reasons.append("a high amount of proteins")
                    else:
                        meal_score *= 0.5
                        meal_bad_reasons.append("a low amount of proteins")
            
            
                if needed_vitamins:
                    if set(needed_vitamins).issubset(meal_vitamins):
                        meal_score *= 1.5
                        meal_good_reasons.append("the right vitamins")
                    else: 
                        meal_score *= 0.5
                        meal_bad_reasons.append("does not have the right vitamins")
            
                meals["scores"][meal] = meal_score
                if meal_good_reasons or meal_bad_reasons:
                    reasons = " - The best meal this restaurant serves has "
                    if meal_good_reasons:
                        reasons += " and ".join(meal_good_reasons)
                    if meal_bad_reasons:
                        reasons += " but it " + " and ".join(meal_bad_reasons)
                    meals["reasons"][meal] = reasons
                else:
                    meals["reasons"][meal] = " - This restaurant has okay meals"


            best_meal, score = max(meals["scores"].items(), key = lambda k : k[1])
            new_utility = utility * score            
            if new_utility >= utility:
                good_reasons.append(meals["reasons"][best_meal])
            else:
                bad_reasons.append(meals["reasons"][best_meal])
            utility = new_utility


            #Check transportation  
            score_transports = self.check_transportation(sc["transport"], climate, res.locatedIn)            
            if score_transports["score"]:
                max_uti = max(score_transports["score"].values())
                max_transports = [trans for (trans, score) in score_transports["score"].items() if score == max_uti]
                new_utility = utility*max_uti
                if new_utility > utility:                    
                    good_trans = []
                    for trans in max_transports:
                        good_trans.append(score_transports["reason"][trans])
                    good_reasons.append(" - You can " + " or ".join(good_trans) + " to this restaurant.")
                else:
                    bad_trans = []
                    for trans in max_transports:
                        bad_trans.append(score_transports["reason"][trans])
                    bad_reasons.append(" - You can " + " or ".join(bad_trans) + " to this restaurant.")
                utility = new_utility
            else:
                utility = 0

            
            if utility != 0:
                location = [loc.cityName for loc in res.locatedIn]
                restaurant = res.restaurantName + " located in " + ", ".join(location)
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
            if "startMovieBefore" in sc["movie_pref"].keys():
                startBefore, startBeforeV=sc["movie_pref"]["startMovieBefore"]
            else:
                startBefore = None
            if "startMovieAfter" in sc["movie_pref"]:
                startAfter, startAfterV=sc["movie_pref"]["startMovieAfter"]
            else: 
                startAfter = None
            if "finishMovieBefore" in sc["movie_pref"]:
                finishBefore, finishBeforeV=sc["movie_pref"]["finishMovieBefore"]
            else: 
                finishBefore = None

            #check the day if correct
            if movProg.dayScheduleMovie == date:  #if the day is same
                new_utilitys = utilitys * dateV
                if new_utilitys > utilitys:
                    good_reasonsS.append(" - This movie will be today")
                if new_utilitys < utilitys:
                    bad_reasonsS.append(" - This movie will be on {}".format(date))
                utilitys = new_utilitys
            #check if movie starts before
            if startBefore:
                if movProg.scheduleMovieTime < startBefore:
                    new_utilitys = utilitys * startBeforeV
                    good_reasonsS.append(" - This movie will start before {}".format(startBefore))
                    utilitys = new_utilitys
                else:
                    new_utilitys = utilitys * (2-startBeforeV)
                    bad_reasonsS.append(" - This movie will not start before {}".format(startBefore))
                    utilitys = new_utilitys
            #check if movie starts after
            if startAfter:
                if movProg.scheduleMovieTime > startAfter:
                    new_utilitys = utilitys * startAfterV
                    good_reasonsS.append(" - This movie will start after {}".format(startAfter))
                    utilitys = new_utilitys
                else:
                    new_utilitys = utilitys * (2-startAfterV)
                    bad_reasonsS.append(" - This movie will not start after {}".format(startAfter))
                    utilitys = new_utilitys
            #evaluate duration of movie with time
            if finishBefore:
                m = movProg.presentingMovie
                if movProg.scheduleMovieTime+m.duration < finishBefore:
                    new_utilitys = utilitys * finishBeforeV
                    good_reasonsS.append(" - This movie will end before {}".format(finishBefore))
                    utilitys = new_utilitys
                else:
                    new_utilitys = utilitys * (2-finishBeforeV)
                    bad_reasonsS.append(" - This movie will not end before {}".format(finishBefore))
                    utilitys = new_utilitys

            #Check transportation  
            score_transports = self.check_transportation(sc["transport"], sc["climate"], movProg.scheduleMovie.locatedIn)            
            if score_transports["score"]:
                max_uti = max(score_transports["score"].values())
                max_transports = [trans for (trans, score) in score_transports["score"].items() if score == max_uti]
                new_utility = utilitys*max_uti
                if new_utility > utilitys:                    
                    good_trans = []
                    for trans in max_transports:
                        good_trans.append(score_transports["reason"][trans])
                    good_reasonsS.append(" - You can " + " or ".join(good_trans) + " to this cinema.")
                else:
                    bad_trans = []
                    for trans in max_transports:
                        bad_trans.append(score_transports["reason"][trans])
                    bad_reasonsS.append(" - You can " + " or ".join(bad_trans)  + " to this cinema.")
                utilitys = new_utility
            else:
                utility = 0

            #Adding movieProgram to the possibilities
            if utilitys != 0:
                movie_program_options["scores"][movProg] = utilitys
                movie_program_options["good_reasons"][movProg] = good_reasonsS
                movie_program_options["bad_reasons"][movProg] = bad_reasonsS


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
            if "duration" in sc["movie_pref"].keys():
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
            option = "{} played in {} at {}, {}".format(movie.nameMovie, movie_program.scheduleMovie.cinemaName, movie_program.dayScheduleMovie, movie_program.scheduleMovieTime)
            options["scores"][option] = movie_options["scores"][movie] * movie_program_options["scores"][movie_program]
            options["good_reasons"][option] = movie_options["good_reasons"][movie] + movie_program_options["good_reasons"][movie_program]
            options["bad_reasons"][option] = movie_options["bad_reasons"][movie] + movie_program_options["bad_reasons"][movie_program]

        return options
    
    
    def check_transportation(self, max_duration, climate, location):   
        score_transports = {}          
        score_transports["score"] = {}
        score_transports["reason"] = {}
        if climate:
            carbon_footprints = {}
        
        if self.neigh in location:
            #same neighbourhood
            for transport in self.poss_transports:
                if transport.sameNeighbourhoodDuration:
                    if max_duration < transport.sameNeighbourhoodDuration:
                        score_transports["score"][transport] = 1.5
                        score_transports["reason"][transport] = transport.action
                    else:
                        score_transports["score"][transport] = 0.8
                        score_transports["reason"][transport] = "{}, but it takes {} minutes".format(transport.action, transport.sameNeighbourhoodDuration)  
                    if climate:
                        carbon_footprints[transport] = transport.carbonFootprint           
                        
        elif self.city in location:
            #same city
            for transport in self.poss_transports:
                if transport.sameCityDuration:
                    if max_duration < transport.sameCityDuration:
                        score_transports["score"][transport] = 1.5
                        score_transports["reason"][transport] = transport.action
                    else:
                        score_transports["score"][transport] = 0.8
                        score_transports["reason"][transport] = "{}, but it takes {} minutes".format(transport.action, transport.sameCityDuration)
                    if climate:
                        carbon_footprints[transport] = transport.carbonFootprint           
        else:
            #other city
            for transport in self.poss_transports:
                if transport.otherCityDuration:
                    if max_duration < transport.otherCityDuration:
                        score_transports["score"][transport] = 1.2
                        score_transports["reason"][transport] = transport.action
                    else:
                        score_transports["score"][transport] = 0.8
                        score_transports["reason"][transport] = "{}, but it takes {} minutes".format(transport.action, transport.otherCityDuration)
                    if climate:
                        carbon_footprints[transport] = transport.carbonFootprint         
        
        if climate:
            max_value  = max([transport.carbonFootprint for transport in score_transports["score"].keys()])
            min_value  = min([transport.carbonFootprint for transport in score_transports["score"].keys()])
            for transport in score_transports["score"].keys():
                score_transports["score"][transport] *= 2 - (2*transport.carbonFootprint/max_value)
                if transport.carbonFootprint == min_value:
                    score_transports["reason"][transport] += ", this transportation has the lowest carbon footprint"
                else:
                    score_transports["reason"][transport] += ", but there is a transportation with a lower carbon footprint"

        return score_transports