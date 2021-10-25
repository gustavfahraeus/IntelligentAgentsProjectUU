from agent import Agent

def get_scenario(i):
    scenario = {}

    filename = "scenarios/scenario{}.txt".format(i)
    with open(filename) as f:
        dic = ""
        for line in f:
            if "#" in line:
                dic = line.strip()
                scenario[dic] = {}
            else:
                (key, value) = line.split(" ")
                scenario[dic][key] = value.strip()
    
    return scenario

def main():
    agent = Agent()
    scenario = get_scenario(1)
    print(scenario)

if __name__ == "__main__":
    main()