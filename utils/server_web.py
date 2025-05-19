import subprocess
from consts import IMAGE_DEFAULT, NODE_JS_FILE, APP_WEB_FILE, VM_NAMES
from logger import setup_logger, get_logger
import os
from time import sleep
from utils.containers import start_container


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()

"""
SERVER WEB
"""

def config_server(name):
    """
    Configura los servidores web de los contenedores s1-s5 (Apache y NodeJS)
    """

    logger.info(f"Iniciando configuración del servidor web {name}")

    try:
        #Instalar servidor web Apache
        logger.debug(f"Actualizando paquetes en {name}")
        subprocess.run(["lxc", "exec", name, "--", "apt", "update"], check=True)

        logger.debug(f"Instalando Apache en {name}")
        subprocess.run(["lxc", "exec", name, "--", "apt", "install", "-y", "apache2"], check=True)

        if not os.path.isfile(NODE_JS_FILE):
            logger.error(f"Archivo de instalación Node.js no encontrado: {NODE_JS_FILE}")
            return

        #Instalar servicio NodeJS
        logger.debug("Transfiriendo script de instalación Node.js")
        subprocess.run(["lxc", "file", "push", NODE_JS_FILE, f"{name}/root/install.sh"], check=True)
        subprocess.run(["lxc", "exec", name, "--", "chmod", "+x", "/root/install.sh"], check=True)

        logger.debug("Transfiriendo aplicación web")
        subprocess.run(["lxc", "file", "push", "-r", APP_WEB_FILE, f"{name}/root/"], check=True)

        logger.debug("Extrayendo el contenido de app.tar.gz")
        subprocess.run(["lxc", "exec", name, "--", "tar", "-oxvf", "app.tar.gz"], check=True)

        logger.debug("Ejecutando instalación Node.js")
        subprocess.run(["lxc", "exec", name, "--", "/root/install.sh"], check=True)

        logger.debug("Reiniciando servidor")
        subprocess.run(["lxc", "restart", name], check=True)

        logger.debug("Iniciando servidor Node.js con forever")
        subprocess.run(["lxc", "exec", name, "--", "forever", "start", "app/rest_server.js"], check=True)

        logger.info(f"Servidor web {name} configurado con éxito.")

    except subprocess.CalledProcessError as e:
        logger.critical(f"Error al configurar el servidor {name}: {e}")
