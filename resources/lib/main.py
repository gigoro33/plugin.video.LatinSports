from codequick import Route, Listitem, run
from resources.lib.chanels.teleXtrema import listItemsTeleXtrema
from resources.lib.chanels.tuCanalDeportivo import listItemsTuCanalDeportivo

# Base items constructor
dict_constructor = [
    {"label": "TeleXtrema", "art": "telextrema.png", "chanel": "TeleXtrema"},
    {"label": "Tu Canal Deportivo", "art": "canalDeportivo.png", "chanel": "canalDeportivo"}
]

@Route.register
def root(plugin):
    for elem in dict_constructor:
        item = Listitem()
        item.label = elem["label"]
        item.art.local_thumb(elem["art"])
        if elem["chanel"] == "TeleXtrema":
            item.set_callback(listItemsTeleXtrema)
        elif elem["chanel"] == "canalDeportivo":
            item.set_callback(listItemsTuCanalDeportivo)
        yield item