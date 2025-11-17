import requests
import simplejson as json
from codequick import Route, Listitem, Resolver, utils
import re

# Base url constructor
url_constructor = utils.urljoin_partial("https://la14hd.com/")

@Route.register
def listItemsLa14Hd(plugin): 
     # Request the online resource.
    url = url_constructor("status.json")
    response = requests.get(url)
    response.encoding = 'utf-8'

    data = json.loads(response.text)

    canales_links = []

    for region, canales in data.items():
        for item in canales:
            canal = item.get("Canal")
            link = item.get("Link")
            estado = item.get("Estado")
            canales_links.append({"Canal": canal, "Link": link, "Estado": estado})

    # Mostrar resultado
    for cl in canales_links:
        color = "lawngreen" if cl["Estado"] == "Activo" else "orangered"
        item = Listitem()
        # Set the thumbnail image of the video.
        item.art["thumb"] = cl["Canal"]
        # Set the plot info
        item.info["plot"] = cl["Canal"]
        # Set the label info
        item.label = f"{cl["Canal"]} - [COLOR {color}]{cl["Estado"]}[/COLOR]"
        item.info["title"] = f"{cl["Canal"]} - [COLOR {color}]{cl["Estado"]}[/COLOR]"
        item.set_callback(play_video, url=cl["Link"])
        # Return the listitem as a generator.
        yield item

@Resolver.register
def play_video(plugin, url):
    stream_url = ''
    headers = {
        'Referer': url_constructor("")
    }

    response = requests.get(url, headers=headers)
    # Parse the html source
    if response.status_code == 200:
        html = response.text
        # Expresión regular para encontrar la variable src y capturar su valor
        match = re.search(r'playbackURL\s*=\s*"([^"]+)"', html)

        # Buscar la coincidencia en el texto
        if match:
            stream_url = match.group(1)
        # else:
            #  xbmcgui.Dialog().notification('[B]Error[/B]', 'Stream is OFFLINE!!!',xbmcgui.NOTIFICATION_INFO, 6000,False)
            #     sys.exit(1)
    return stream_url