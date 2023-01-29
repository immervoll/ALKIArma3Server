import requests
from bs4 import BeautifulSoup


def getIds(modfile="/arma3/mods/modlist.html"):
    modlist = open(modfile,"r" )
    soup = BeautifulSoup(modlist, "html.parser")


    modids =[]
    for link in soup.find_all("a"):
        if "id=" in format(link.get("href")):
            id = format(link.get("href")).replace("http://steamcommunity.com/sharedfiles/filedetails/?id=", "")
            id = id.replace("https://steamcommunity.com/sharedfiles/filedetails/?id=", "")
            print(f"Found Mod Id: {id}")
            modids.append(id)
    return(modids)
