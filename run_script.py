from agent import Agent
from scenarios import *

def main():
    agent = Agent()
    scenario = scenario1
    options= {}

    if scenario["actions"]["cinema"] == 1:
        options["movies"] = agent.get_movies()

    if scenario["actions"]["restaurant"] == 1:
        options["restaurant"] = agent.get_restaurants(scenario)

    if scenario["actions"]["foodstore"] == 1:
        options["foodstore"] = agent.get_foodstores()

    print(options)

if __name__ == "__main__":
    main()