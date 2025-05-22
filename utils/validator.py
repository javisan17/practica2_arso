import subprocess
from logger import setup_logger, get_logger
from utils.file import load_num_servers
from consts import VM_NAMES


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
Validador
"""


def check_infrastructure_created():
    """
    Verifica que la infraestructura esté creada según el contenido de num_servers.txt y VM_NAMES
    """

    try:
        n_servers = load_num_servers()
    except Exception as e:
        logger.error(f"No se pudo leer num_servers.txt: {e}")
        return False

    #Obtener lista de contenedores existentes
    try:
        output = subprocess.check_output(['lxc', 'list', '--format', 'csv', '-c', 'n'], text=True)
        existing_containers = [line.strip() for line in output.splitlines()]
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al obtener lista de contenedores: {e}")
        return False

    #Comprobar contenedores esenciales
    required = [VM_NAMES['cliente'], VM_NAMES['database'], VM_NAMES['balanceador']]
    required+= VM_NAMES['servidores'][:n_servers]

    for container in required:
        if container not in existing_containers:
            logger.warning(f"Contenedor faltante: {container}")
            return False

    return True


def check_all_running():
    """
    Verifica que todos los contenedores requeridos estén en estado RUNNING
    """

    try:
        n_servers=load_num_servers()
    except Exception as e:
        logger.error(f"No se pudo leer num_servers.txt: {e}")
        return False

    #Obtener estados de los contenedores
    try:
        output = subprocess.check_output(['lxc', 'list', '--format', 'csv', '-c', 'ns'], text=True)
        #output tiene formato: nombre_contenedor,estado
        containers_status = dict(line.split(',') for line in output.strip().splitlines())
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al obtener el estado de los contenedores: {e}")
        return False

    #Contenedores que deben estar en RUNNING
    required = [VM_NAMES['cliente'], VM_NAMES['database'], VM_NAMES['balanceador']]
    required += VM_NAMES['servidores'][:n_servers]

    not_running = [name for name in required if containers_status.get(name) != "RUNNING"]
    
    if not_running:
        for c in not_running:
            logger.warning(f"El contenedor {c} no está en estado RUNNING")
        return False

    return True


def container_exists(name):
    """
    Verifica si un contenedor con el nombre dado existe en LXC.
    """

    result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
    return "not found" not in result.stderr.lower()


def container_is_running(name):
    """
    Verifica si un contenedor está en estado RUNNING.
    """
    
    result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
    return "Status: RUNNING" in result.stdout