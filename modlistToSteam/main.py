import id_scraper
import sys
import os


def convert():
    pack_name = "active"
    modfile = "./active.html"
    assert os.path.exists(
        modfile), f"unable to locate the modlist html at {str(modfile)}"
    user = os.getenv("STEAM_USER")
    pw = os.getenv("STEAM_PASSWORD")

    if os.path.exists("./modlistupdater_active.txt"):
        os.remove("./modlistupdater_active.txt")
    f = open(f"modlistupdater_{pack_name}.txt", "a")
    f.write(f"login {user} {pw} \n")
    i = 0
    for id in id_scraper.getIds(modfile):
        i = i+1
        f.write(f"workshop_download_item 107410 {id} \n")
    print(f"FINISHED: added {i} mods to the file.")
    f.write("quit")
    f.close()
