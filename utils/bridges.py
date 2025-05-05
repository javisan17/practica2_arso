import subprocess
from logger import setup_logger, get_logger


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
LXC Bridges
"""


def create_bridge(bridge_name):
    """
    Crear un bridge
    """

    logger.debug(f"Creando bridge {bridge_name}")
    result = subprocess.run(["lxc", "network", "info", bridge_name], capture_output=True, text=True)
    if "not found" in result.stderr:
        try:
            subprocess.run(["lxc", "network", "create", bridge_name], check=True)
            logger.info(f"Bridge creado: {bridge_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al crear el bridge {bridge_name}: {e}")
    else:
        logger.warning(f"El bridge {bridge_name} ya existe.")


def config_bridge(bridge_name, ipv4):
    """
    Configurar los bridges
    """

    try:
        #IPv4 a true y con dirección pasada por parámetro
        subprocess.run(["lxc", "network", "set", bridge_name, "ipv4.nat", "true"], check=True)
        subprocess.run(["lxc", "network", "set", bridge_name, "ipv4.address", ipv4], check=True)
        logger.info(f"{ipv4} asignada correctamente al bridge: {bridge_name}")

        #IPv6 a false 
        subprocess.run(["lxc", "network", "set", bridge_name, "ipv6.nat", "false"], check=True)
        subprocess.run(["lxc", "network", "set", bridge_name, "ipv6.address", "none"], check=True)

        #Configurar servidor DNS 
        subprocess.run(["lxc", "network", "set", bridge_name, "dns.domain", "lxd"], check=True)
        subprocess.run(["lxc", "network", "set", bridge_name, "dns.mode", "none"], check=True)
        logger.info(f"Bridge configurado correctamente: {bridge_name}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error al configurar el bridge {bridge_name}: {e}")


def attach_network(container, bridge, iface):
    """
    Conectar un contenedor a un bridge en una tarjeta de red (ethx)
    """

    logger.debug(f"Conectando {container} al bridge {bridge} usando {iface}")
    result = subprocess.run(["lxc", "config", "device", "show", container], capture_output=True, text=True)
    if iface not in result.stdout:
        try:
            subprocess.run(["lxc", "network", "attach", bridge, container, iface], check=True)
            logger.info(f"Conectado {container} al bridge {bridge} por {iface}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al conectar {container} a {bridge}: {e}")
    else:
        logger.warning(f"El contenedor {container} ya está conectado a {bridge} por {iface}")



###NO SE PUEDE DETACHEAR DA ERROR DE PERFIL. AL HEREDAR NO DEJA DETACHEAR
# def detach_network(container, bridge, iface):
#     """
#     Conectar un contenedor a un bridge en una tarjeta de red (ethx)
#     """

#     subprocess.run(["lxc", "network", "detach", bridge, container, iface], check=True)


def delete_bridge(bridge):
    """
    Eliminar un bridge
    """

    logger.debug(f"Intentando eliminar el bridge {bridge}")
    try:
        subprocess.run(["lxc", "network", "delete", bridge], check=True)
        logger.info(f"Bridge eliminado: {bridge}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al eliminar el bridge {bridge}: {e}")