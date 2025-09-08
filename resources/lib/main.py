from codequick import Route, Listitem, run
from resources.lib.chanels.tvporinternet import listItemsTvPorInternet
from resources.lib.chanels.tuCanalDeportivo import listItemsTuCanalDeportivo
from resources.lib.chanels.futbolLibre import listItemsFutbolLibre

# Base items constructor
dict_constructor = [
    {"label": "TV Por Internet", "art": "tvporinternetoficial.png", "chanel": "tvPorInternet"},
    {"label": "Tu Canal Deportivo", "art": "canalDeportivo.png", "chanel": "canalDeportivo"},
    {"label": "Futbol Libre HD", "art": "futbolLibre.png", "chanel": "futbolLibre"}
]

@Route.register
def root(plugin):
    for elem in dict_constructor:
        item = Listitem()
        item.label = elem["label"]
        item.art.local_thumb(elem["art"])
        if elem["chanel"] == "tvPorInternet":
            item.set_callback(listItemsTvPorInternet)
        elif elem["chanel"] == "canalDeportivo":
            item.set_callback(listItemsTuCanalDeportivo)
        elif elem["chanel"] == "futbolLibre":
            item.set_callback(listItemsFutbolLibre)
        yield item