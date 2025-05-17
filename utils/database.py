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


# def install_mongoDB(name):
#     """
#     FUNCIONA PERO NO ENTIENDO
#     """

#     logger.debug(f"Iniciando instalación de MongoDB en {name}")
    
#     # Actualiza e instala dependencias necesarias
#     subprocess.run(["lxc", "exec", name, "--", "apt", "update"], check=True)
#     subprocess.run(["lxc", "exec", name, "--", "apt", "install", "-y", "gnupg", "curl"], check=True)

#     # Importa la clave pública del repositorio
#     subprocess.run([
#         "lxc", "exec", name, "--", "bash", "-c",
#         "curl -fsSL https://pgp.mongodb.com/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.0.gpg"
#     ], check=True)

#     # Crea el archivo del repositorio
#     subprocess.run([
#         "lxc", "exec", name, "--", "bash", "-c",
#         'echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" > /etc/apt/sources.list.d/mongodb-org-6.0.list'
#     ], check=True)

#     # Actualiza repositorios e instala MongoDB
#     subprocess.run(["lxc", "exec", name, "--", "apt", "update"], check=True)
#     subprocess.run(["lxc", "exec", name, "--", "apt", "install", "-y", "mongodb-org"], check=True)

#     logger.info(f"MongoDB instalado correctamente en {name}")


