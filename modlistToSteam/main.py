from . import id_scraper as id_scraper
import sys
import os


def convert(MODLIST: str):
    modfile = f"/arma3/mods/{MODLIST}.html"
    assert os.path.exists(
        modfile), f"unable to locate the modlist {str(modfile)} in the arma3 mods folder."
    user = os.getenv("STEAM_USER")
    pw = os.getenv("STEAM_PASSWORD")

    if os.path.exists(f"/arma3/mods/{MODLIST}.txt"):
        os.remove(f"/arma3/mods/{MODLIST}.txt")
    f = open(f"/arma3/mods/{MODLIST}.txt", "a")
    f.write(f"login {user} {pw} \n")
    i = 0
    for id in id_scraper.getIds(modfile):
        i = i+1
        f.write(f"workshop_download_item 107410 {id} \n")
    print(f"FINISHED: added {i} mods to the file.")
    f.write("quit")
    f.close()
