import subprocess
from logger import setup_logger, get_logger
from utils.containers import stop_container

"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
DATABASE
"""

def install_mongoDB(name):
    """
    Instala y modifica mongodb en el contenedor name
    """

    logger.debug(f"Iniciando cambio de netplan en {name}")
    subprocess.run(["lxc", "exec", name, "--", "apt", "update"], check=True)
    subprocess.run(["lxc", "exec", name, "--", "apt", "install", "-y", "mongodb"], check=True)
    logger.info(f"MongoDB instalado correctamente en {name}")

    #Modificamos el archivo mongodb.conf 
    subprocess.run(["lxc", "exec", name, "--", "sed", "-i", "s/^bind_ip = 127.0.0.1$/bind_ip = 127.0.0.1,134.3.0.20/", "/etc/mongodb.conf"], check=True)
    logger.info(f"Archivo mongodb.conf modificado correctamente en {name}")

    #Reiniciar contenedor
    logger.debug(f"Reiniciando contenedor {name} para aplicar cambios")
    subprocess.run(f"lxc restart {name}", shell=True, check=True)
    stop_container(name)

    logger.info(f"Configuración de mongodb aplicada correctamente en el contenedor {name}")


