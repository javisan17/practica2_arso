import subprocess
from consts import VM_NAMES, NUM_SERVERS_FILE, IMAGE_DEFAULT, BRIDGES_IPV4, IP_LB, BRIDGES, MAX_SERVERS, MIN_SERVERS, IP_CL, IP_S, ALIAS_IMAGEN_SERVIDOR
from logger import setup_logger, get_logger
from utils.containers import create_container, start_container, stop_container, delete_container, config_container
from utils.image import create_image, delete_image, publish_image
from utils.bridges import create_bridge, config_bridge, attach_network, delete_bridge
from utils.file import save_num_servers, load_num_servers
from utils.balanceador import change_netplan, setup_haproxy
from utils.server_web import config_server, start_app, change_ip_files
from time import sleep
from utils.file import load_num_servers
from utils.validator import container_is_running, container_exists, validate_configure
from utils.database_remote import get_ip_local, get_ip_remote, deploy_remote_db


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
        stop_container(VM_NAMES["database"])
        logger.info("Todos los contenedores han sido parados")
    except Exception as e:
        logger.error(f"Error al parar contenedores: {e}", exc_info=True)


def create_server(image):
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
                create_container(name=name, image=image)
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
                logger.info("Reconfigurando el balanceador")
                setup_haproxy()
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
            start_app(name=name)
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
            setup_haproxy()
            logger.info(f"Servidor {name} detenido correctamente.")
        else:
            logger.info(f"Servidor {name} ya estaba detenido.")
    except Exception as e:
        logger.critical(f"Error crítico al parar servidor {name}: {e}", exc_info=True)


def enlarge():
    """
    Añade un servidor a la red y lo configura. NO SE SI COMPLETARLA
    """

    try:
        logger.info("Ampliando infraestructura con un nuevo servidor...")

        #Crear nuevo server por imagen
        publish_image(contenedor=VM_NAMES["servidores"][0], alias=ALIAS_IMAGEN_SERVIDOR)
        create_server(image=ALIAS_IMAGEN_SERVIDOR)

        #Obtiene el número de servidores y su nombre para iniciarlo 
        num=load_num_servers()
        name=VM_NAMES["servidores"][num]
        start_server(name=name)
        start_server(name=VM_NAMES["servidores"][0])

        #Reconfigura el haproxy del balanceador 
        setup_haproxy()

    except Exception as e:
        logger.critical(f"Error crítico al añadir el servidor: {e}", exc_info=True)


def configure_server(name):
    """
    Hace comprobaciones y configura el contenedor name como servidor
    """

    #Comprobar que existe ese contenedor
    if not container_exists():
        logger.error("Primero debes hacer un create_server. La infraestructura no está creada correctamente.")
        print("Error: Primero debes hacer un create_server.")
        return

    #Comprobar que el contenedor está en estado RUNNING
    if not container_is_running():
        logger.error("Ese contenedor deben estar en estado RUNNING.")
        print("Error: Antes debes hacer un start_server")
        return

    logger.info("Iniciando configuración del servidor")
    config_server(name=name)
    logger.info("Reconfigurando el balanceador")
    setup_haproxy()

    logger.info(f"Servidor {name} configurado correctamente")


def configure_remote(name):
    """
    Despliega la db remotamente
    """

    logger.debug("Comprobando que se ha ejecutado la orden configure")
    if not validate_configure():
        logger.error("La configuración base no está completa. Ejecuta 'configure' antes de 'configure_remote'.")
        print("Error: Antes debes hacer un configure")
        return

    #Obtener ip del equipo local y del remoto  
    ip_local = get_ip_local()
    ip_remote= get_ip_remote(name=name)
    
    #Desplegar la base de datos en remoto 
    deploy_remote_db(ip_local=ip_local, ip_remote=ip_remote)

    #Modificar la ip en los ficheros Node 
    num_servers=load_num_servers()
    for i in range(num_servers):
        change_ip_files(name=VM_NAMES['servidores'][i],ip=ip_remote)
        start_app(name=VM_NAMES['servidores'][i])

    
