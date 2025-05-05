import subprocess
from consts import VM_NAMES, NUM_SERVERS_FILE, IMAGE_DEFAULT, BRIDGES_IPV4, IP_LB, BRIDGES, MAX_SERVERS, MIN_SERVERS, IP_CL, IP_S
from logger import setup_logger, get_logger
from utils.containers import create_container, start_container, stop_container, delete_container, config_container
from utils.image import create_image, delete_image
from utils.bridges import create_bridge, config_bridge, attach_network, delete_bridge
from utils.file import save_num_servers
from utils.balanceador import change_netplan


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
ORDENES OPCIONALES
"""


def stop_all(n_servers):
    """
    Parar todos los contenedores
    """

    logger.info("Parando todos los contenedores")

    try:
        for i in range(n_servers):
            stop_container(VM_NAMES["servidores"][i])
        stop_container(VM_NAMES["cliente"])
        stop_container(VM_NAMES["balanceador"])
        logger.info("Todos los contenedores han sido parados")
    except Exception as e:
        logger.error(f"Error al parar contenedores: {e}", exc_info=True)


def create_server():
    """
    Crear el siguiente servidor disponible entre s1 y s5.
    """

    logger.info("Buscando servidor libre para crear...")

    try:
        for i in range(MAX_SERVERS):
            name = VM_NAMES["servidores"][i]
            logger.debug(f"Verificando si existe el contenedor {name}")
            result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
            if "not found" in result.stderr:
                logger.info(f"Creando nuevo servidor disponible: {name}")
                create_container(name=name)
                attach_network(container=name, bridge=BRIDGES["LAN1"], iface="eth0")
                ip=IP_S[name]
                config_container(name=name, iface="eth0", ip=ip)
                logger.info(f"Servidor {name} creado correctamente con IP {ip} ")
                return

        logger.warning(f"Ya existen {MAX_SERVERS}  servidores. No se puede crear más.")
    except Exception as e:
        logger.critical(f"Error crítico al crear servidor: {e}", exc_info=True)


def delete_last_server():
    """
    Eliminar el ultimo servidor disponible entre s2 y s5.
    """

    logger.info("Buscando último servidor para eliminar...")

    try:
        for i in reversed(range(1, MAX_SERVERS)):
            name = VM_NAMES["servidores"][i]
            result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
            if "not found" not in result.stderr:
                logger.info(f"Eliminando servidor: {name}")
                delete_container(name=name)
                logger.info(f"Servidor {name} eliminado correctamente.")
                return

        logger.warning("No hay servidores s2 a s5 creados. No se puede eliminar ninguno. El servidor s1 siempre debe estar disponible.")
    except Exception as e:
        logger.critical(f"Error al eliminar servidor: {e}", exc_info=True)


def start_server(name):
    """
    Arrancar el servidor de nombre que se pase por parámetro
    """

    logger.info(f"Solicitado arrancar servidor: {name}")

    #Verificar que el nombre está en la lista permitida
    if name not in VM_NAMES["servidores"]:
        logger.error(f"Nombre de servidor inválido: {name}")
        return

    try:
        #Verificar si el contenedor existe
        result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
        if "not found" in result.stderr:
            logger.warning(f"El contenedor {name} no existe.")
            return

        #Verificar si está corriendo
        if "Status: RUNNING" in result.stdout:
            logger.info(f"Servidor {name} ya está corriendo.")
        else:
            start_container(name=name)
            logger.info(f"Servidor {name} corriendo correctamente.")
    except Exception as e:
        logger.critical(f"Error crítico al arrancar servidor {name}: {e}", exc_info=True)


def stop_server(name):
    """
    Detener el servidor de nombre que se pase por parámetro
    """

    logger.info(f"Solicitado parar servidor: {name}")

    #Verificar que el nombre está en la lista permitida
    if name not in VM_NAMES["servidores"]:
        logger.error(f"Nombre de servidor inválido: {name}")
        return

    try:
        #Verificar si el contenedor existe
        result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
        if "not found" in result.stderr:
            logger.warning(f"El contenedor {name} no existe.")
            return

        #Verificar si está corriendo
        if "Status: RUNNING" in result.stdout:
            stop_container(name)
            logger.info(f"Servidor {name} detenido correctamente.")
        else:
            logger.info(f"Servidor {name} ya estaba detenido.")
    except Exception as e:
        logger.critical(f"Error crítico al parar servidor {name}: {e}", exc_info=True)