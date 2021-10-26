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
        options = {}

        restaurants = self.ontology.search(type = self.ontology.Restaurant)
        for res in restaurants:
            utility = 1
            for (key, value) in sc["#restaurant_pref"]:
                if key in properties:
                    utility *= value
            
            if utility != 0:
                options[res] = utility
        
        return options





