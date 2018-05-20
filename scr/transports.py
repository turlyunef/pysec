import json
#Десериализует _env
def get_env():
    try:
        with open('../env.json','r') as flow:
            env = json.load(flow)
    except FileNotFoundError:
        raise AuthError()
    return env
