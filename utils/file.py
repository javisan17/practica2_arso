from consts import NUM_SERVERS_FILE
from logger import setup_logger, get_logger

"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
FILE
"""


def save_num_servers(n):
    """
    Guardar el número de servidores en un archivo NUM_SERVERS_FILE
    """

    logger.debug(f"Intentando guardar el número de servidores: {n}")
    try:
        with open(NUM_SERVERS_FILE, "w") as file:
            file.write(str(n))
        logger.info(f"Número de servidores {n} guardados correctamente en {NUM_SERVERS_FILE}.")
    except Exception as e:
        logger.error(f"No se pudo guardar el número de servidores: {e}")


def load_num_servers():
    """
    Cargar el número de servidores del archivo NUM_SERVERS_FILE
    """
    
    logger.debug(f"Leyendo el número de servidores desde {NUM_SERVERS_FILE}...")
    try:
        with open(NUM_SERVERS_FILE, "r") as file:
            n = int(file.read())
        logger.info(f"Número de servidores {n} cargados correctamente.")
        return n
    except FileNotFoundError:
        logger.warning(f"Archivo {NUM_SERVERS_FILE} no encontrado. Retornando valor por defecto (0).")
        return 0
    except Exception as e:
        logger.error(f"Error al leer el número de servidores: {e}")
        return 0