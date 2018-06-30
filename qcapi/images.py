import requests
from .api import api_path

"""functions for getting requests streams of image data
this can be wrapped using BytesIO(request.content), and this BytesIO object can
be opened easily in PIL, or manually processed
"""

base = "https://stats.quake.com/{}/{}.{}"


class QCImages:

    @staticmethod
    def _get_resource_bytes(path, name, ext):
        return requests.get(base.format(path, name, ext)).content

    @staticmethod
    def get_icon_bytes(name):
        return QCImages._get_resource_bytes("icons", name, "png")

    @staticmethod
    def get_weapon_icon_bytes(name):
        return QCImages._get_resource_bytes("weapons", name, "png")

    @staticmethod
    def get_nameplate_bytes(name):
        return QCImages._get_resource_bytes("nameplates", name, "png")

    @staticmethod
    def get_champion_portrait_bytes(name):
        return QCImages._get_resource_bytes("champions", name, "png")

    @staticmethod
    def get_map_portrait_bytes(name):
        return QCImages._get_resource_bytes("maps", name, "jpg")

    @staticmethod
    def get_medal_bytes(name):
        return QCImages._get_resource_bytes("medals", name, "png")

    @staticmethod
    def get_rank_bytes(name):
        return QCImages._get_resource_bytes("ranks", name, "png")