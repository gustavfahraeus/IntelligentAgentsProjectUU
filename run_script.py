from agent import Agent
from scenarios import *
import operator

def main():
    agent = Agent()
    scenario = scenario1
    actions = {}

    if scenario["actions"]["cinema"] == 1:
        actions["movie"] = agent.get_movies(scenario)

    if scenario["actions"]["restaurant"] == 1:
        actions["restaurant"] = agent.get_restaurants(scenario)

    if scenario["actions"]["foodstore"] == 1:
        actions["food store"] = agent.get_foodstores(scenario)

    for action, options in actions.items():
        scores = options["scores"]
        #Change to top 3!
        max_value = max(scores.values())
        good_options = [option for option, score in scores.items() if score == max_value]
        
        for suggestion in good_options:
            print("A good {} is {}, because:".format(action, suggestion))
            print(*options["good_reasons"][suggestion], sep = "\n")
            if options["bad_reasons"][suggestion]:
                print("But it is not a perfect option, because:")
                print(*options["bad_reasons"][suggestion], sep = "\n")

if __name__ == "__main__":
    main()