from bs4 import BeautifulSoup
from codequick import Route, Listitem, Resolver, utils
import requests
import xbmc
import re
import xbmcgui
from urllib.parse import urlparse

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
            
def obtener_url_base(url):
    parsed_url = urlparse(url)
    url_base = parsed_url.scheme + "://" + parsed_url.netloc
    return url_base
            
@Resolver.register
def play_video(plugin, url_base):
    headers = {
        'Referer': url_constructor("")
    }

    response = requests.get(url_base, headers=headers)

    # Verificar si la solicitud fue exitosa (código de estado 200)
    html_content = response.text
    # Patrón de expresión regular para extraer el valor del atributo src en el iframe
    pattern = re.compile(r'<div\s+class="video-container"\s*>\s*<iframe[^>]*src="([^"]+)"[^>]*>', re.DOTALL)

    # Buscar coincidencias utilizando search
    match = pattern.search(html_content)

    # Obtener el valor del atributo src si hay coincidencia
    if match:
        src_value = match.group(1)

        headers = {
            'Referer': url_constructor("")
        }

        response = requests.request("GET", src_value, headers=headers)

        if response.status_code == 200:
                html_content = response.text

                #  Expresión regular para extraer el atributo src del script que contiene la url del stream
                pattern = re.compile(r'<script\s+type="text/javascript"\s+src=["\']?([^"\'>]+)["\']?\s*>', re.DOTALL)

                # Buscar el src del script
                match = pattern.search(html_content)

                # Si se encuentra el src, extraerlo
                if match:
                    # src = obtener_url_base("https:" + match.group(1))
                    src = "https:" + match.group(1).replace('js', 'php')
                else:
                    xbmc.log("No se encontró el atributo src en el script. URL: " + src_value, xbmc.LOGERROR)
                    xbmcgui.Dialog().notification('[B]Error[/B]', 'No se encontró el atributo src en el script.',xbmcgui.NOTIFICATION_INFO, 6000,False)
                    sys.exit(1)
                    
                # Patrón de expresión regular para extraer el valor del atributo src en el iframe
                pattern = re.compile(r'fid="(.*?)"', re.DOTALL)

                # Buscar coincidencias utilizando search
                match = pattern.search(html_content)

                # Obtener el valor del atributo src si hay coincidencia
                if match:
                    fid = match.group(1)

                    headers = {
                        'Referer': obtener_url_base(url_base)
                    }

                    response = requests.get(src +"?player=desktop&live="+fid, headers=headers)

                    if response.status_code == 200:
                            html_content = response.text
                            # Patrón de expresión regular para extraer el valor del atributo src en el iframe
                            pattern = re.compile(r'return\(\[(.*?)\]', re.DOTALL)

                            # Buscar coincidencias utilizando search
                            match = pattern.search(html_content)

                            # Obtener el valor del atributo src si hay coincidencia
                            if match:
                                    
                                url_video = match.group(1)
                                url_video = url_video.replace(',', '').replace('\\', '').replace('"', '')
                                url_video = url_video + "|Referer=" + obtener_url_base(src)
                                return url_video
                            else:
                                xbmc.log("No se encontró el valor de src en el código HTML. URL: " + src +"?player=desktop&live="+fid, xbmc.LOGERROR)
                                xbmcgui.Dialog().notification('[B]Error[/B]', 'No se encontró el valor de src en el código HTML..',xbmcgui.NOTIFICATION_INFO, 6000,False)
                                sys.exit(1)
                    else:
                        raise ValueError(f"Error al hacer la solicitud. Código de estado: {response.status_code}")
                else:
                    xbmc.log("No se encontró el valor de Id del canal en el código HTML. URL: " + src_value, xbmc.LOGERROR)
                    xbmcgui.Dialog().notification('[B]Error[/B]', 'No se encontró el valor de src en el código HTML.',xbmcgui.NOTIFICATION_INFO, 6000,False)
                    sys.exit(1)
        else:
            raise ValueError(f"Error al hacer la solicitud. Código de estado: {response.status_code}")

    else:
        raise ValueError(f"No se encontró el valor de src en el código HTML.")