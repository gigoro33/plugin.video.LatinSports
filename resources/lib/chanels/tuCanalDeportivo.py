from bs4 import BeautifulSoup
from codequick import Route, Listitem, Resolver, utils
import requests
import re
from dateutil import tz, parser
from datetime import datetime
import base64
from urllib.parse import urlparse, parse_qs
import simplejson as json

url_constructor = utils.urljoin_partial("https://elcanaldeportivo.com")

@Route.register
def listItemsTuCanalDeportivo(plugin):
    # Base items constructor
    dict_main_section = [
        {"label": "Agenda Deportiva"},
        {"label": "Más Canales"}
    ]
    for elem in dict_main_section:
        item = Listitem()
        item.label = elem["label"]
        if elem["label"] == "Agenda Deportiva":
            item.set_callback(agendaDeportiva)
        elif elem["label"] == "Más Canales":
            item.set_callback(canales)
        yield item

@Route.register
def agendaDeportiva(plugin):
    url = url_constructor("partidos.json")
    response = requests.get(url)
    data = json.loads(response.text)
    # Zona local dinámica (la que tenga el sistema)
    local_zone = tz.tzlocal()
    # Obtener la fecha/hora actual local
    ahora_local = datetime.now(local_zone).date() # Fecha local actual (sin hora)

    # Filtrar: dejar SOLO partidos cuya hora sea >= ahora
    data = [p for p in data if hora_local(p).date() >= ahora_local]
    data = sorted(data, key=lambda p: parser.isoparse(p["hora_utc"])) #Ordenar por horas
    # Parse the html source
    for partido in data:
        item = Listitem()
        # Convertir a hora local
        dt_local = hora_local(partido)
        desc = f"{dt_local.strftime("%Y-%m-%d %H:%M")} {partido["liga"]} {partido["equipos"]}"

        # Set the plot info
        item.info["plot"] = desc
        item.label = desc
        item.art.thumb = url_constructor(partido["logo"])
        links_dic = {}
        for canal in partido["canales"]:
            links_dic[canal["nombre"]] = {
                "url": canal["url"],
                "desc": desc,
                "nom_canal": f"{canal["nombre"]} {canal["calidad"]}"
            }
        item.set_callback(canales_eventos, links=links_dic)
        # Return the listitem as a generator.
        yield item
            
@Route.register
def canales_eventos(plugin, links):
    for clave, link in links.items():
        item = Listitem()
        item.label = str(link["nom_canal"])
        item.info["plot"] = str(link["desc"])
        item.set_callback(play_video, url_base=str(link["url"]))
        yield item

@Route.register
def canales(plugin):
    url = url_constructor("/canales.php")
    response = requests.get(url)
    # Parse the html source
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all('div', {"class": "card-wrapper"})
    # Parse each video
    for elem in elements:
        soup2 = BeautifulSoup(str(elem), 'html.parser')
        elements2 = soup2.find_all('a')
        for elem2 in elements2:
            item = Listitem()
            # Set the thumbnail image of the video.
            item.art["thumb"] = elem.find("img").get("src")
            desc = elem.find("img").get("alt") if len(elem2.text.strip()) == 0 else elem2.text
            # Set the plot info
            item.info["plot"] = desc
            # Set the label info
            item.label = desc
            url_video = elem2.get('href')
            item.set_callback(play_video, url_base=url_video)
            # Return the listitem as a generator.
            yield item
            
@Resolver.register
def play_video(plugin, url_base):
    headers = {
        'Referer': url_constructor("")
    }
    response = requests.get(url_base, headers=headers) 
    soup = BeautifulSoup(response.text, "html.parser")
    url = soup.find('iframe').get("src")        
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    if soup.find('iframe'):
        url2 = soup.find('iframe').get("src")
        parsed_url = urlparse(url2)
        url_parameters = parse_qs(parsed_url.query)
        if "url" in url_parameters and 'http' not in url_parameters["url"][0]:
            return base64.b64decode(url_parameters["url"][0])
        elif "get" in url_parameters and 'http' in url_parameters["get"][0]:
            return url_parameters["get"][0]

    else:
        fid = soup.find('script', text=lambda text: text and 'fid' in text).text.split('"')[1]
        url2 = soup.find('body').find('script', src=lambda src: src and src.startswith('//'))["src"]
        url2 = "https:" + url2.replace(".js", '.php') + '?player=desktop&live=' + fid
        
        response = requests.get(url2, headers=headers)
        pattern = re.compile(r'return\(\[(.*?)\]', re.DOTALL)
        # Buscar coincidencias utilizando search
        match = pattern.search(response.text)
        # Obtener el valor del atributo src si hay coincidencia
        if match:                       
            url_video = match.group(1)
            url_video = url_video.replace(',', '').replace('\\', '').replace('"', '')
            url_video = url_video + "|Referer=" + url2
            return url_video

def hora_local(partido):
    utc_zone = tz.gettz("UTC")
    local_zone = tz.tzlocal()   # zona horaria dinámica (según el sistema)
    dt_utc = parser.isoparse(partido["hora_utc"]).replace(tzinfo=utc_zone)
    dt_local = dt_utc.astimezone(local_zone)
    return dt_local