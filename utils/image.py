import subprocess
from consts import IMAGE_DEFAULT
from logger import setup_logger, get_logger


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
LXC IMAGE
"""


def create_image():
    """
    Crear una nueva imagen con el alias asignado
    """
    
    logger.debug("Verificando si la imagen ya está importada...")

    result = subprocess.run(["lxc", "image", "info", IMAGE_DEFAULT], capture_output=True, text=True)
    if "not found" in result.stderr:
        logger.info(f"La imagen {IMAGE_DEFAULT} no está importada. Se procederá a importarla.")
        try:
            subprocess.run(["lxc", "image", "import", "/mnt/vnx/repo/arso/ubuntu2004.tar.gz", "--alias", IMAGE_DEFAULT], check=True)
            logger.info(f"Imagen {IMAGE_DEFAULT} importada con éxito.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al importar la imagen {IMAGE_DEFAULT}: {e}")
    else:
        logger.warning(f"La imagen {IMAGE_DEFAULT} ya está disponible.")


def delete_image():
    """
    Eliminar imagen creada de ubuntu
    """

    logger.debug(f"Intentando eliminar la imagen {IMAGE_DEFAULT}...")
    try:
        subprocess.run(["lxc", "image", "delete", IMAGE_DEFAULT], check=True)
        logger.info("Imagen local eliminada con éxito.")
    except subprocess.CalledProcessError as e:
        logger.error(f"No se pudo eliminar la imagen {IMAGE_DEFAULT}: {e}")