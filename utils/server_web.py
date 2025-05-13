import subprocess
from consts import IMAGE_DEFAULT, NODE_JS_FILE, APP_WEB_FILE, VM_NAMES
from logger import setup_logger, get_logger


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()

"""

"""

def config_server(name):
    """
    Configura los servidores web de los contenedores (Apache y NodeJS)
    """

    #Instalar servidor web Apache
    subprocess.run(["lxc", "exec", name, "--", "apt", "update"], check=True)
    subprocess.run(["lxc", "exec", name, "--", "apt", "install", "-y", "apache2"], check=True)

    #Instalar servicio NodeJS
    subprocess.run(["lxc", "file", "push", NODE_JS_FILE, f"{name}/root/install.sh"], check=True)
    subprocess.run(["lxc", "exec", name, "--", "chmod", "+x", "install.sh"], check=True)
    subprocess.run(["lxc", "file", "push", "-r", APP_WEB_FILE, f"{name}/root/"], check=True)
    subprocess.run(["lxc", "exec", name, "--", "tar", "-oxvf", "app.tar.gz"], check=True)                   ### CON ESTA app.tar.gz deberiamos hacer algo
    subprocess.run(["lxc", "exec", name,  "--", "./install.sh"], check=True)                                ### IGUAL AQUI 
    subprocess.run(["lxc", "restart", name], check=True)
    subprocess.run(["lxc", "exec", name, "--", "forever", "start", "app/rest_server.js"], check=True)       ### IGUAL AQUI 