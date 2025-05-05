import logging

def setup_logger():
    """
    Configurar el sistema de logs
    """

    logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("static/files/pfinal.log"),
        logging.StreamHandler()
    ])

    
def get_logger():
    """
    Devuelve el logger configurado.
    """

    return logging.getLogger("arso")