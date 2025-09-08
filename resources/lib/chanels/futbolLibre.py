from bs4 import BeautifulSoup
from codequick import Route, Listitem, Resolver, utils
import requests
import re
import base64
from urllib.parse import urlparse
import resources.lib.jsunpack as jsunpack

# Base url constructor
url_constructor = utils.urljoin_partial("https://www.futbollibre2.com/")


@Route.register
def listItemsFutbolLibre(plugin):    
    # Request the online resource.
    url = url_constructor("")
    response = requests.get(url)
    response.encoding = 'utf-8'
    
    # Parse the html source
    soup = BeautifulSoup(response.text, 'html.parser')

    elements = soup.find_all('a', {"class": "channel-link"})

    # Parse each video
    for elem in elements:
        item = Listitem()
        # Set the thumbnail image of the video.
        item.art["thumb"] = url_constructor(elem.find("img").get("src"))
        # Set the plot info
        item.info["plot"] = elem.find("p").text
        # Set the label info
        item.label = elem.find("p").text
        url_opt = elem.get('href')
        item.set_callback(listItemsOPtionStreams, url=url_opt, plot=item.info["plot"], art=item.art["thumb"])
        # Return the listitem as a generator.
        yield item

@Route.register
def listItemsOPtionStreams(plugin,url, plot, art):
    response = requests.get(url)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    elements = soup.find_all('a', target='player')
    
    for elem in elements:
        item = Listitem()
        item.art["thumb"] = art
        item.info["plot"] = plot
        item.label = elem.text
        url_video = elem.get("href")
        item.set_callback(play_video, url=url_video)
        yield item

def get_iframe_url(url):
    headers = {
        'Referer': url_constructor("")
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    elem = soup.find('iframe', {"class": "embed-responsive-item"})
    return elem.get("src")

def get_base_url(url):
    parsed_url = urlparse(url)
    url_base = parsed_url.scheme + "://" + parsed_url.netloc
    return url_base
        
@Resolver.register
def play_video(plugin, url):
    url = get_iframe_url(url)
    stream_url = ''
    headers = {
        'Referer': url_constructor("")
    }

    response = requests.get(url, headers=headers)
    # Parse the html source
    if response.status_code == 200:
        html = response.text
        # Expresión regular para encontrar la variable src y capturar su valor
        pattern = r'var\s+src\s*=\s*"([^"]+)"'

        # Buscar la coincidencia en el texto
        stream_url = re.search(pattern, html)
                    
        if stream_url:
            headers.update({'referer': get_base_url(url)})

            # html = request_sess(stream_url, 'get', headers=headers)
            if '404 not found' in html.lower():
                xbmcgui.Dialog().notification('[B]Error[/B]', 'Stream is OFFLINE!!!',xbmcgui.NOTIFICATION_INFO, 6000,False)
                sys.exit(1)
            else:
                stream_url = stream_url.group(1)
                # certificate_data = "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"
                stream_url += '|Referer=' + get_base_url(url)
                # hdrs = 'User-Agent='+UAx+'&Referer='+urllib_parse.quote_plus(nturl3)
    return stream_url