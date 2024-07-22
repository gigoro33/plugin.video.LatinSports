from bs4 import BeautifulSoup
from codequick import Route, Listitem, Resolver
import requests
import re
import base64
from urllib.parse import urlparse
import resources.lib.jsunpack as jsunpack

@Route.register
def listItemsTeleXtrema(plugin, url):    
    # Request the online resource.
    response = requests.get(url)

    # Parse the html source
    soup = BeautifulSoup(response.text, 'html.parser')

    elements = soup.find_all('div', {"class": "canal-item"})

    # Parse each video
    for elem in elements:
        item = Listitem()
        # Set the thumbnail image of the video.
        item.art["thumb"] = elem.find("img").get("src")
        # Set the plot info
        item.info["plot"] = elem.find("h4").text
        # Set the label info
        item.label = elem.find("h4").text
        url_video = elem.find('a').get('href')
        item.set_callback(play_video, url=url_video)
        # Return the listitem as a generator.
        yield item

def extraer_iframe(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    elem = soup.find('iframe', {"id": "iframe"})
    headers = {
        'Referer': 'https://www.telextrema.com'
    }
    response = requests.request("GET", elem.get("src"), headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    elem = soup.find('iframe')
    return elem.get("src")

def obtener_url_base(url):
    parsed_url = urlparse(url)
    url_base = parsed_url.scheme + "://" + parsed_url.netloc
    return url_base
        
@Resolver.register
def play_video(plugin, url):
    url = extraer_iframe(url)
    stream_url = ''
    headers = {
        'Referer': 'https://www.telextrema.com'
    }

    response = requests.request("GET", url, headers=headers)
    # Parse the html source
    if response.status_code == 200:
        html = response.text
        packer = re.compile('(eval\(function\(p,a,c,k,e,(?:r|d).*)')
        packeds = packer.findall(html)
        unpacked = ''
        if packeds:
            for packed in packeds:
                packed = packed.replace('\\\\','\\')
                unpacked += jsunpack.unpack(packed)
        if unpacked:
            try:
                vidmultibase64 = re.findall('mariocscryptold\("([^"]+)"',unpacked,re.DOTALL+re.I)[0]
            except:
                vidmultibase64 = re.findall('\("([^"]+)"',unpacked,re.DOTALL)[0]
            for x in range(10):
                try:
                    
                    vidmultibase64 = base64.b64decode(vidmultibase64).decode("utf-8")
                    if 'http' in vidmultibase64:
                        
                        stream_url = vidmultibase64
                        break
                except:
                    pass
                    
        if stream_url:
            headers.update({'referer': obtener_url_base(url)})

            # html = request_sess(stream_url, 'get', headers=headers)
            if '404 not found' in html.lower():
                xbmcgui.Dialog().notification('[B]Error[/B]', 'Stream is OFFLINE!!!',xbmcgui.NOTIFICATION_INFO, 6000,False)
                sys.exit(1)
            else:
                # certificate_data = "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"
                stream_url += '|Referer=' + obtener_url_base(url)
                # hdrs = 'User-Agent='+UAx+'&Referer='+urllib_parse.quote_plus(nturl3)
    return stream_url