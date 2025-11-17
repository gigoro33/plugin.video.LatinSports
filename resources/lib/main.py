from codequick import Route, Listitem, run
from resources.lib.chanels.tvporinternet import listItemsTvPorInternet
from resources.lib.chanels.tuCanalDeportivo import listItemsTuCanalDeportivo
from resources.lib.chanels.futbolLibre import listItemsFutbolLibre
from resources.lib.chanels.la14Hd import listItemsLa14Hd

# Base items constructor
dict_constructor = [
    {"label": "TV Por Internet", "art": "tvporinternetoficial.png", "chanel": "tvPorInternet"},
    {"label": "Tu Canal Deportivo", "art": "canalDeportivo.png", "chanel": "canalDeportivo"},
    {"label": "Futbol Libre HD", "art": "futbolLibre.png", "chanel": "futbolLibre"},
    {"label": "La 14 HD", "art": "la14hd.png", "chanel": "la14hd"},
    {"label": "Pelota Libre", "art": "pelotaLibre.png", "chanel": "pelotaLibre"}
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
        elif elem["chanel"] == "la14hd":
            item.set_callback(listItemsLa14Hd)
        # elif elem["chanel"] == "pelotaLibre":
        #     item.set_callback(listItemsLa14Hd)
        yield item