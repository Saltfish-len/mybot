from graia.ariadne.message.chain import MessageChain
import requests
import json
import time


def fetch_BF1_Api(method, sessionId=None, params=None):
    base_url = "https://sparta-gw.battlelog.com/jsonrpc/pc/api"
    body = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": "233"
    }
    headers = {
        "content-Type": "application/json"
    }
    if sessionId is not None:
        headers["X-GatewaySession"] = sessionId
    response = requests.post(url=base_url, headers=headers, data=json.dumps(body))
    if response.status_code != 200:
        return None
    res = json.loads(str(response.content, encoding="utf-8"))
    return res


def check_session_time():
    with open('bf1config.json', 'r') as f:
        config = json.load(f)
    sessiontime = config["sessiontime"]
    return time.time() < sessiontime + 3600 * 12


def get_session():
    try:
        with open('bf1config.json', 'r') as f:
            config = json.load(f)
        remid = config["remid"]
        sid = config["sid"]
        session = config["session"]
        sessiontime = config["sessiontime"]
        base_url = "https://accounts.ea.com/connect/auth?response_type=code&locale=zh_CN&client_id=sparta-backend-as-user-pc"
        cookie = {"remind": remid, "sid": sid}
        response = requests.get(base_url, cookies=cookie, allow_redirects=False)

        authCode = str(response.headers["location"][30:])
        content = fetch_BF1_Api("Authentication.getEnvIdViaAuthCode", params={
            "authCode": authCode,
            "locale": "zh-tw"})
        config["session"] = session
        config["sessiontime"] = time.time() + 12*3600
        with open('bf1config.json', 'w') as f:
            json.dump(config, f)
        print("session updated")
        return content["result"]["sessionId"]
    except IOError:
        with open('bf1config.json', 'w') as f:
            json.dump({"remid": "xxxx", "sid": "XXXX", "session": "no need to modify, sessiontime also.",
                       "sessiontime": 0000, "serverId": {}, "viplist": {}}, f)
        print(
            "Fail to load config, config file has been created.\nPlease modify config.json and restart.\nPress enter to exit.")


def ban(session, serverId, person_name):
    res = fetch_BF1_Api("RSP.addServerBan", sessionId=session, params={"game": "tunguska",
                                                                       "serverId": serverId,
                                                                       "personaName": person_name})
    print(res)


def get_personaId(personaName):
    baseurl = f"https://api.gametools.network/bf1/player?name={personaName}&platform=pc"
    response = requests.get(baseurl)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        return 0


def get_serverId(session, gameId):
    with open('bf1config.json', 'r') as f:
        config = json.load(f)
    if str(gameId) in config["serverId"].keys():
        serverId = config["serverId"][str(gameId)]
        return serverId
    else:
        response = fetch_BF1_Api("GameServer.getFullServerDetails", sessionId=session, params={"game": "tunguska",
                                                                                               "gameId": gameId,
                                                                                               })
        if response:
            serverId = response["result"]["rspInfo"]["server"]["serverId"]
            config["serverId"][gameId] = serverId
            if str(serverId) not in config["viplist"].keys():
                config["viplist"][str(serverId)] = {}
            with open('bf1config.json', 'w') as f:
                json.dump(config, f)
            return serverId

def list_player(gameId):
    baseurl = f"https://api.gametools.network/bf1/players/?gameid={gameId}"
    response = requests.get(baseurl)
    if response.status_code != 200:
        return None
    res = response.json()
    map = res["serverinfo"]["level"][3:]
    team_one_name = res["teams"][0]["key"]
    team_one_players = res["teams"][0]["players"]
    team_two_name = res["teams"][1]["key"]
    team_two_players = res["teams"][1]["players"]
    return map,(team_one_name,team_two_name),(team_one_players,team_two_players)



def vip_add(session, serverId, personaName, days):
    personaName = personaName.lower()
    with open('bf1config.json', 'r') as f:
        config = json.load(f)

    if personaName in config["viplist"][str(serverId)].keys():
        config["viplist"][str(serverId)][personaName] += days * 3600 * 24
    else:
        response = fetch_BF1_Api("RSP.addServerVip", sessionId=session, params={"game": "tunguska",
                                                                                "serverId": serverId,
                                                                                "personaName": personaName,
                                                                                })
        if response is None:
            return None
        config["viplist"][str(serverId)][personaName] = time.time() + days * 3600 * 24
    with open('bf1config.json', 'w') as f:
        json.dump(config, f)
    return (config["viplist"][str(serverId)][personaName] - time.time()) // (3600 * 24)


def vip_remove(session, serverId, personaName):
    personaName = personaName.lower()
    response = fetch_BF1_Api("RSP.removeServerVip", sessionId=session, params={"game": "tunguska",
                                                                               "serverId": serverId,
                                                                               "personaId": get_personaId(personaName),
                                                                               })
    if response:
        with open('bf1config.json', 'r') as f:
            config = json.load(f)
        if personaName in config["viplist"][str(serverId)].keys():
            config["viplist"][str(serverId)].pop(personaName)
        with open('bf1config.json', 'w') as f:
            json.dump(config, f)
        return True
    else:
        return False


def vip_list(session, serverId):
    response = fetch_BF1_Api("RSP.getServerDetails", sessionId=session, params={"game": "tunguska",
                                                                                "serverId": serverId})
    if response:
        return "".join([f"{num}: {item['displayName']}\n" for num, item in enumerate(response["result"]["vipList"])])


def vip_check(session, serverId):
    with open('bf1config.json', 'r') as f:
        config = json.load(f)
    with open(fr"backup/{int(time.time())}.json","w") as f:
        json.dump(config,f)
    res = []
    count = 0
    config_copy = config["viplist"][str(serverId)].copy()
    for personaName, due_time in config_copy.items():
        if time.time() > due_time:
            if vip_remove(session, serverId, personaName):
                config["viplist"][str(serverId)].pop(personaName)
                count += 1
                time.sleep(0.1)
            else:
                res.append(personaName)
                time.sleep(0.1)
    with open('bf1config.json', 'w') as f:
        json.dump(config, f)
    return ("\n".join(res),count)


if __name__ == "__main__":
    list_player(7176779910897)