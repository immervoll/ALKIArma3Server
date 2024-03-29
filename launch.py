import subprocess
import os
import shutil
import re
import modlistToSteam.main
from progress.bar import Bar
from progress.spinner import Spinner

print("starting pre laumch procedure..")

CONFIG_FILE = os.environ["ARMA_CONFIG"]
KEYS = "/arma3/keys"
ACTIVEMODPACK = os.environ["ALKI_MODPACKNAME"].lower()

os.makedirs("root/Steam/steamapps", exist_ok=True)
os.makedirs("/arma3", exist_ok=True)
os.system("rm -R /arma3/mods/*/")
for file in os.listdir("/arma3/mods/"):
    os.rename("/arma3/mods/" + file, "/arma3/mods/" + file.lower())
if os.path.isfile(f"/arma3/mods/{ACTIVEMODPACK}.html") and not os.path.isfile(f"/arma3/mods/{ACTIVEMODPACK}.txt"):
    modlistToSteam.main.convert(ACTIVEMODPACK)
    print("### converted modlist to steamcmd script ###")

if os.path.isfile(f"/arma3/mods/{ACTIVEMODPACK}.txt"):
    with open(f"/arma3/mods/{ACTIVEMODPACK}.txt") as file_in:
        lines = []
        for line in file_in:
            if "workshop_download_item" in line:
                lines.append(line.replace(
                    "workshop_download_item 107410 ", "").strip())
                print(f"found {line}")

    bar = Bar('Downloading Mods', max=len(lines))
    p = subprocess.Popen(f"/steamcmd/steamcmd.sh +runscript /arma3/mods/{ACTIVEMODPACK}.txt", shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    while p.stdout is not None:
        line = p.stdout.readline()
        if line.startswith("Success. Downloaded item"):
            bar.next()
        if not line:
            print("\n")
            p.stdout.flush()
            bar.finish()
            break

    with Bar('Transfering Mods', max=len(lines)) as bar:
        for line in lines:
            os.system(
                f"cp -R /root/Steam/steamapps/workshop/content/107410/{line} /arma3/mods/")
            bar.next()
        bar.finish()
    print("renaming mods to avoid conflicts")
    os.system(
        "cd /arma3/mods && find . -depth -exec rename 's/(.*)\/([^\/]*)/$1\/\L$2/' {} \;")
    print("### mods updated ###")
    print(f"active mods: {lines}")
    print("### starting arma3 ###")

if not os.path.exists(KEYS) or not os.path.isdir(KEYS):
    if os.path.exists(KEYS):
        os.remove(KEYS)
    os.makedirs(KEYS)
    print("created server keys")

steamcmd = ["/steamcmd/steamcmd.sh"]
steamcmd.extend(["+force_install_dir", "/arma3"])
steamcmd.extend(["+login", os.environ["STEAM_USER"],
                os.environ["STEAM_PASSWORD"]])
steamcmd.extend(["+app_update", "233780"])
if "STEAM_BRANCH" in os.environ and len(os.environ["STEAM_BRANCH"]) > 0:
    steamcmd.extend(["-beta", os.environ["STEAM_BRANCH"]])
if "STEAM_BRANCH_PASSWORD" in os.environ and len(os.environ["STEAM_BRANCH_PASSWORD"]) > 0:
    steamcmd.extend(["-betapassword", os.environ["STEAM_BRANCH_PASSWORD"]])
steamcmd.extend(["validate", "+quit"])
subprocess.call(steamcmd)


def mods(d):
    launch = "\""
    mods = [os.path.join(d, o) for o in os.listdir(
        d) if os.path.isdir(os.path.join(d, o))]
    for m in mods:
        launch += m+";"
        keysdir = os.path.join(m, "keys")
        if os.path.exists(keysdir):
            keys = [os.path.join(keysdir, o) for o in os.listdir(
                keysdir) if os.path.isdir(os.path.join(keysdir, o)) == False]
            for k in keys:
                shutil.copy2(k, KEYS)
        else:
            print("Missing keys:", keysdir)

    return launch


launch = "{} -limitFPS={} -world={}".format(
    os.environ["ARMA_BINARY"], os.environ["ARMA_LIMITFPS"], os.environ["ARMA_WORLD"])

modstoload = ""
if os.path.exists("/arma3/mods"):
    modstoload = mods("/arma3/mods")
if os.environ["ARMA_DLC"] != "":
    modstoload += os.environ["ARMA_DLC"]+";\""
launch += f" -mod={modstoload}"


clients = int(os.environ["HEADLESS_CLIENTS"])

print("Headless Clients:", clients)

if clients != 0:
    with open("/arma3/configs/{}".format(CONFIG_FILE)) as config:
        data = config.read()
        regex = r"(.+?)(?:\s+)?=(?:\s+)?(.+?)(?:$|\/|;)"

        config_values = {}

        matches = re.finditer(regex, data, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            config_values[match.group(1).lower()] = match.group(2)

        if not "headlessclients[]" in config_values:
            data += "\nheadlessclients[] = {\"127.0.0.1\"};\n"
        if not "localclient[]" in config_values:
            data += "\nlocalclient[] = {\"127.0.0.1\"};\n"

        with open("/tmp/arma3.cfg", "w") as tmp_config:
            tmp_config.write(data)
        launch += " -config=\"/tmp/arma3.cfg\""

    client_launch = launch
    client_launch += " -client -connect=127.0.0.1"
    if "password" in config_values:
        client_launch += " -password={}".format(config_values["password"])

    for i in range(0, clients):
        print("LAUNCHING ARMA CLIENT {} WITH".format(i), client_launch)
        subprocess.Popen(client_launch, shell=True)

else:
    launch += " -config=\"/arma3/configs/{}\"".format(CONFIG_FILE)

launch += " -port={} -name=\"{}\" -profiles=\"/arma3/configs/profiles\"".format(
    os.environ["PORT"], os.environ["ARMA_PROFILE"])

if os.path.exists("servermods"):
    launch += f" -serverMod={modstoload}"

print("LAUNCHING ARMA SERVER WITH", launch, flush=True)
os.system(launch)
