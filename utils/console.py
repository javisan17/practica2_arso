import subprocess
from logger import setup_logger, get_logger
from consts import VM_NAMES



"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
CONSOLE
"""


def show_consoles(n_servers):
    """
    Mostrar por consola los contenedores
    """

    contenedores=[VM_NAMES["servidores"][i] for i in range(n_servers)] + [VM_NAMES["cliente"], VM_NAMES["balanceador"]]

    for c in contenedores:
        orden=f"lxc exec {c} bash"
        try:
            subprocess.Popen(["xterm", "-e", orden])
            logger.info(f"Consola del contenedor {c} abierta correctamente")
        except Exception as e:
            logger.error(f"Error al abrir consola para contenedor {c}: {e}")


def show_console(name):
    """
    Abrir la consola del contenedor dicho
    """

    try:
        orden=f"lxc exec {name} bash"
        subprocess.Popen(["xterm", "-e", orden])
        logger.info(f"Consola del contenedor {name} abierta correctamente")
    except Exception as e:
        logger.error(f"Error al abrir consola para {name}: {e}")


###ES UN POCO IRRELAVANTES PORQUE CUANDO SE PARAN LOS SERVIDORES LAS CONSOLAS SE CIERRAN AUTOMATICAMENTE
def close_consoles():
    """
    Cerrar las consolas de los contenedores
    """

    try:
        subprocess.run(["pkill", "xterm"], check=True)
        logger.info("Consolas cerradas correctamente")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al cerrar consolas: {e}")