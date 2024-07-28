from bs4 import BeautifulSoup
from codequick import Route, Listitem, Resolver, utils
import requests
import re
from dateutil import tz, parser
from datetime import datetime
import base64
from urllib.parse import urlparse, parse_qs

url_constructor = utils.urljoin_partial("https://tucanaldeportivo.org")

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
    url = url_constructor("/agenda.php")
    response = requests.get(url)
    # Parse the html source
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all('li', class_=True)
    for elem in elements:
        item = Listitem()
        
        hora = elem.find('a', href="#").find('span').get_text(strip=True) #Extract hour    
        hora_utc2 = parser.parse(hora).time() 
        zona_horaria_utc2 = tz.gettz('UTC+2') # Definir la zona horaria UTC+2
        zona_horaria_utc5 = tz.gettz() # Obtener la zona horaria del usuario
        fecha_referencia = datetime.now() # Crear un objeto datetime combinando la hora UTC+2 con una fecha de referencia
        hora_utc2_dt = fecha_referencia.replace(hour=hora_utc2.hour, minute=hora_utc2.minute, tzinfo=zona_horaria_utc2)
        hora_utcUsua_dt = hora_utc2_dt.astimezone(zona_horaria_utc5) # Cambiar la zona horaria de UTC+2 a UTC del usuario
        hora = hora_utcUsua_dt.time().strftime("%H:%M") # Extraer la hora en formato time
        
        elem.find('a', href="#").find('span').extract() #Remove span tag with hour
        desc = hora + " " + elem.find('a', href="#").get_text(strip=True)
        # Set the plot info
        item.info["plot"] = desc
        # Set the label info
        item.label = desc
        links_dic = {}
        links = elem.find("ul").find_all('li', class_=False)
        for idx, link in enumerate(links, start=1):
            links_dic[f"enlace_{idx}"] = {
                "url": link.find('a').get("href"),
                "desc": desc,
                "nom_canal": link.find('a').get_text(strip=True)
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