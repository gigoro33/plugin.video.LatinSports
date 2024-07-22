from codequick import Route, Listitem, run
from resources.lib.chanels.teleXtrema import *

# Base items constructor
dict_constructor = [
    {"label": "TeleXtrema", "art": "https://www.telextrema.com/imge/telextrema.png", "url": "https://www.telextrema.com", "chanel": "TeleXtrema"},
    {"label": "Tu Canal Deportivo", "art": "", "url": "https://tucanaldeportivo.org/canales.php", "chanel": "canalDeportivo"}
]

@Route.register
def root(plugin):
    for elem in dict_constructor:
        item = Listitem("folder")
        item.label = elem["label"]
        item.art["thumb"] = elem["art"]
        if elem["chanel"] == "TeleXtrema":
            item.set_callback(listItemsTeleXtrema, url=elem["url"])
        elif elem["chanel"] == "canalDeportivo":
            item.set_callback(chanel_list, url=elem["url"], chanel=elem["chanel"])
        yield item

@Route.register
def chanel_list(plugin, url, chanel):
    if chanel == "TeleXtrema":
        set_callback(listItemsTeleXtrema(url, chanel))
    elif chanel == "canalDeportivo":
        none