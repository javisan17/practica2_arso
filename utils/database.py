import subprocess
from logger import setup_logger, get_logger
from utils.containers import start_container

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
    Instala y modifica MongoDB en el contenedor name
    """

    logger.info(f"Iniciando instalación de MongoDB en {name}")

    try:
        start_container(name=name)
        subprocess.run(["lxc", "exec", name, "--", "apt", "update"], check=True)

        logger.debug("Instalando MongoDB")
        subprocess.run(["lxc", "exec", name, "--", "apt", "install", "-y", "mongodb"], check=True)

        #Modificamos el archivo mongodb.conf
        logger.debug("Modificando bind_ip de MongoDB")
        subprocess.run(["lxc", "exec", name, "--", "sed", "-i", "s/^bind_ip = 127.0.0.1$/bind_ip = 127.0.0.1,134.3.0.20/", "/etc/mongodb.conf"], check=True)

        #Reiniciar contenedor
        logger.debug(f"Reiniciando contenedor {name}")
        subprocess.run(["lxc", "restart", name], check=True)

        logger.info(f"MongoDB configurado con éxito en {name}")

    except subprocess.CalledProcessError as e:
        logger.critical(f"Error instalando/configurando MongoDB en {name}: {e}")
