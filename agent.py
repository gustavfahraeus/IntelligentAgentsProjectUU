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
        options = {"scores" : {}, "reasons": {}}

        restaurants = self.ontology.search(type = self.ontology.Restaurant)
        for res in restaurants:
            utility = 1
            reasons = []

            #Check Cuisines
            for key, value in sc["restaurant_pref"]["cuisine"].items():
                if key == "ItalianCuisine":
                    resI = self.ontology.search(servesCuisine = self.ontology.ItalianCuisine)
                    if res in list(resI):
                        new_utility = value * utility
                        if new_utility > utility:
                            reasons.append(" - This restaurant has an Italian Cuisine")
                        utility = new_utility

                if key == "FrenchCuisine":
                    resF = self.ontology.search(servesCuisine = self.ontology.FrenchCuisine)
                    if res in list(resF):
                        new_utility *= value                        
                        if new_utility > utility:
                            reasons.append(" - This restaurant has an French Cuisine")
                        utility = new_utility

                if key == "TurkishCuisine":
                    resT = self.ontology.search(servesCuisine = self.ontology.TurkishCuisine)
                    if res in list(resT):
                        new_utility *= value                        
                        if new_utility > utility:
                            reasons.append(" - This restaurant has an Turkish Cuisine")
                        utility = new_utility
            

            #Check allergy:
            users = self.ontology.search(user = "*")
            user = [u for u in users if u.name[0] == sc["user"]][0]
            self.ontology.search(hasAllergy = "*")

            if utility != 0:
                restaurant = res.restaurantName[0]
                options["scores"][restaurant] = utility
                options["reasons"][restaurant] = reasons
        
        return options





