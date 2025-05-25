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


def start_app(name):
    """
    Reinicia la app del servidor name
    """

    subprocess.run(["lxc", "exec", name, "--", "forever", "stopall"])
    subprocess.run(["lxc", "exec", name, "--", "forever", "start", "app/rest_server.js"])



def change_ip_files(name, ip):
    """
    Cambia la IP hardcodeada en los archivos de configuración de la app dentro del contenedor.
    Sustituye la IP antigua por la nueva en los archivos:
    - /app/rest_server.js
    - /app/md-seed-config.js
    """

    try:
        logger.info(f"Cambiando IP en archivos de configuración dentro del contenedor {name} a {ip}...")
        
        #Reemplazar IP en rest_server.js
        #subprocess.run(["lxc", "exec", name, "--", "sed", "-i", f"s/^await mongoose.connect('mongodb://134.3.0.20/bio_bbdd',{{ useNewUrlParser: true, useUnifiedTopology: true }})$/await mongoose.connect('mongodb:/{ip}//bio_bbdd',{{ useNewUrlParser: true, useUnifiedTopology: true }})", "/app/rest_server.js"], check=True)
        subprocess.run(["lxc", "exec", name, "--", "sed", "-i", f"s|mongodb://[0-9.]\+/bio_bbdd|mongodb://{ip}/bio_bbdd|", "/root/app/rest_server.js"], check=True)

        #Reemplazar IP en md-seed-config.js
        #subprocess.run(["lxc", "exec", name, "--", "sed", "-i", f"s/^const mongoURL = process.env.MONGO_URL || 'mongodb://134.3.0.20:27017/bio_bbdd';$/const mongoURL = process.env.MONGO_URL || 'mongodb://{ip}:27017/bio_bbdd';", "/app/md-seed-config.js"], check=True)
        subprocess.run(["lxc", "exec", name, "--", "sed", "-i", f"s|mongodb://[0-9.]\+:27017/bio_bbdd|mongodb://{ip}:27017/bio_bbdd|", "/root/app/md-seed-config.js"], check=True)

        logger.info("IP cambiada correctamente en los archivos de configuración.")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error al cambiar la IP en los archivos del contenedor {name}: {e}", exc_info=True)