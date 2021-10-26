from owlready2 import *
from pprint import pprint
owlready2.JAVA_EXE = "c:/users/gfahr/onedrive/Dokument/Protege-5.5.0/jre/bin/java.exe" # Change this to whatever on your own system. Don't know how to work around this yet.

# We are developing a utility based Agent.
class Agent:

    def __init__(self):
        # Load the desired ontology using the path file
        self.ontology = get_ontology('./group11.owl').load()
        print(self.ontology.search(iri = '*Constraint'))

        with self.ontology:
            sync_reasoner()



