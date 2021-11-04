from agent import Agent
from scenarios import *

def main():
    agent = Agent()
    scenario = scenario2
    actions = {}

    agent.get_user(scenario["user"])

    if scenario["actions"]["cinema"] == 1:
        actions["movie"] = agent.get_movies(scenario)

    if scenario["actions"]["restaurant"] == 1:
        actions["restaurant"] = agent.get_restaurants(scenario)

    #if scenario["actions"]["foodstore"] == 1:
    #    actions["food store"] = agent.get_foodstores(scenario)

    for action, options in actions.items():
        scores = options["scores"]
        good_options = sorted(scores, key=scores.get, reverse=True)[:2]

        if good_options:        
            print("The best {} is {}".format(action, good_options[0]))
            if options["good_reasons"][good_options[0]]:
                print("Reasons for this {} are:".format(action))
                print(*options["good_reasons"][good_options[0]], sep = "\n")
            if options["bad_reasons"][good_options[0]]:
                print("But it is not a perfect option, because:")
                print(*options["bad_reasons"][good_options[0]], sep = "\n")

            print("\n")

            print("An alternative {} is {}".format(action, good_options[1]))
            if options["good_reasons"][good_options[1]]:
                print("Reasons for this {} are:".format(action))
                print(*options["good_reasons"][good_options[1]], sep = "\n")
            if options["bad_reasons"][good_options[1]]:
                print("But it is not a perfect option, because:")
                print(*options["bad_reasons"][good_options[1]], sep = "\n")
            
            print("\n")
        else:
            print("There are no good {} for your preferences".format(action))
            print("\n")

if __name__ == "__main__":
    main()