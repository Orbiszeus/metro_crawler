import json
import os
import random


class UserAgent:
    def __init__(self):
        file_path = os.path.join("/Users/orbiszeus/metro_analyst/utils", "utilsuser_agent_list.json")

    @staticmethod
    def load(file):
        """loads the data  from supplied json file"""
        with open(file) as fp:
            data = json.load(fp)
        if not data:
            print("Empty {} file".format(file))
            raise
        return data['browsers']

    def user_agent(self):
        """returns an user agent selected randomly from the  provided data"""
        browser = random.choice([*self.user_agents])
        return random.choice(self.user_agents[browser])


if __name__ == '__main__':
    pro = UserAgent()
    print(pro.user_agent())