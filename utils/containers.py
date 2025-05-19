import subprocess
from consts import IMAGE_DEFAULT
from logger import setup_logger, get_logger


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
LXC CONTAINERS
"""


def create_container(name, image):
    """
    Crear un contenedor a partir de una imagen
    """
    
    logger.debug(f"Intentando crear el contenedor {name}")
    result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
    if "not found" in result.stderr:
        try:
            subprocess.run(["lxc", "init", image, name], check=True)
            logger.info(f"Contenedor {name} creado con éxito.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al crear el contenedor {name}: {e}")
    else:
        logger.warning(f"El contenedor {name} ya existe.")

    ###CREAR VACIO DA PROBLEMAS
    #subprocess.run(["lxc", "config", "device", "remove", "name", "eth0"], check=True)


def start_container(name):
    """
    Arrancar un contenedor
    """

    logger.debug(f"Iniciando verificación de estado del contenedor {name}")
    try:
        result = subprocess.run(["lxc", "info", name], check=True, capture_output=True, text=True)
        if "Status: RUNNING" in result.stdout:
            logger.info(f"Contenedor {name} ya está en ejecución.")
            return
        elif "Status: STOPPED" in result.stdout:
            subprocess.run(["lxc", "start", name], check=True)
            logger.info(f"Contenedor iniciado: {name}")
        else:
            logger.warning(f"Estado desconocido para el contenedor {name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al iniciar el contenedor {name}: {e}")


def stop_container(name):
    """
    Detener un contenedor
    """

    logger.debug(f"Verificando estado antes de detener {name}")
    state = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
    if "Status: STOPPED" in state.stdout:
        logger.info(f"Contenedor {name} ya está detenido.")
        return
    elif "Status: RUNNING" in state.stdout:
        try:
            subprocess.run(["lxc", "stop", name], check=True)
            logger.info(f"Contenedor parado: {name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"No se pudo detener el contenedor {name}: {e}")


def delete_container(name):
    """
    Eliminar un contenedor
    """
    
    logger.debug(f"Eliminando contenedor {name}")
    try:
        subprocess.run(["lxc", "delete", name, "--force"], check=True)
        logger.info(f"Contenedor eliminado: {name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al eliminar el contenedor {name}: {e}")


def config_container(name, iface, ip):
    """
    Configurar un contenedor en una red
    """

    logger.debug(f"Configurando red para {name}: iface={iface}, ip={ip}")
    try:
        subprocess.run(["lxc", "config", "device", "set", name, iface, "ipv4.address", ip], check=True)
        logger.info(f"Contenedor {name} conectado a {iface} con IP {ip}")
    except subprocess.CalledProcessError as e:
        logger.error(f"No se pudo configurar la red del contenedor {name}: {e}")