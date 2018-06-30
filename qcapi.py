import requests
from types import SimpleNamespace

ranktable = {
    2100: "Elite_01",
    2025: "Diamond_05",
    1950: "Diamond_04",
    1875: "Diamond_03",
    1800: "Diamond_02",
    1725: "Diamond_01",
    1650: "Gold_05",
    1575: "Gold_04",
    1500: "Gold_03",
    1425: "Gold_02",
    1350: "Gold_01",
    1275: "Silver_05",
    1200: "Silver_04",
    1125: "Silver_03",
    1050: "Silver_02",
    975: "Silver_01",
    900: "Bronze_05",
    825: "Bronze_04",
    750: "Bronze_03",
    675: "Bronze_02",
    0: "Bronze_01"
}


class QCPlayer(object):
    @staticmethod
    def exists(name):
        query = requests.get(
            "https://stats.quake.com/api/v1/Player/Search?term={}"
            .format(name))
        if query.status_code != 200:
            raise Error("Could not get API resource")
        else:
            data = query.json()
            for match in data:
                if match["entityName"] == name:
                    return True
            return False

    @staticmethod
    def from_name(name):
        query = requests.get(
            "https://stats.quake.com/api/v1/Player/Stats?name={}".format(name))
        if query.status_code != 200:
            raise Error("Could not get API resource")
        data = query.json()
        return QCPlayer(data)

    def __init__(self, model):
        self.model = SimpleNamespace(**model)

    def get_rank_data(self, mode):
        return self.model.playerRatings[mode]

    def get_rank(self, mode):
        return self.model.playerRatings[mode]["rating"]

    def get_rank_name(self, mode):
        rank = self.get_rank(mode)
        for value in ranktable:
            if rank >= value:
                return ranktable[value]
        return "Zero_01"

    def get_icon(self):
        return self.model.namePlateId

    def get_nameplate(self):
        return self.model.iconId

    def get_level(self):
        return model.playerLevelState["level"]

    def get_experience(self):
        return model.playerLevelState["exp"]

    def matches_iterator(self):
        for m in self.model.matches:
            yield SimpleNamespace(**m)


class QCRatingData(object):
    def __init__(self, d):
        self.model = SimpleNamespace(**d)

    def get_rating(self):
        return self.model.rating

    def get_deviation(self):
        return self.model.deviation

    def get_update_time(self):
        return self.model.lastUpdated

    def history_iterator(self):
        for m in self.model.history:
            yield SimpleNamespace(**m)


class QCGamesSummary(object):
    def __init__(self, list):
        self.list = list

    @staticmethod
    def from_name(name):
       query = requests.get("https://stats.quake.com/api/v1/Player/GamesSummary?name={}".format(name))

