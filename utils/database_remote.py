import subprocess
import socket
from logger import setup_logger, get_logger
from consts import VM_NAMES, PASSWORD, BRIDGES, BRIDGES_IPV4, PROXY, IP_DB
from utils.database import install_mongoDB


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
DATABASE REMOTE
"""


def get_ip_local():
    """
    Obtener la IP fisica del computador local
    """

    #Esta IP es la usada por defecto para salir hacia Internet, o conectarse a otros hosts
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))  # No se hace conexión real, solo para saber interfaz
        ip = s.getsockname()[0]

    finally:
        s.close()
    
    return ip


def get_ip_remote():
    """
    Obtener la IP fisica del computador remoto
    """

    try:
        #Primero obtenemos el nombre del ordenador remoto (ej:l178)
        nombre_remoto = socket.gethostname()

        #Lo añadimos al nombre de red (l178.lab.dit.upm.es)
        nombre_completo = f"{nombre_remoto}.lab.dit.upm.es"

        #Obtenemos la ip con este comando
        ip = socket.gethostbyname(nombre_completo)
        logger.info(f"Nombre remoto detectado: {nombre_completo} → IP: {ip}")
        return ip

    except Exception as e:
        logger.error(f"No se pudo obtener la IP remota: {e}")
        return None


def deploy_remote_db(ip_local, ip_remote):
    """
    Despliega y configura automáticamente un contenedor remoto con MongoDB.
    """

    try:
        logger.info("Configurando acceso remoto a LXD en ambos equipos")

        #Acceso remoto en local
        subprocess.run(["lxc", "config", "set", "core.https_address", f"{ip_local}:8443"], check=True)

        #Configuración remota usando ssh (requiere clave pública copiada al remoto)
        subprocess.run(["ssh", f"{ip_remote}", f"lxc config set core.https_address {ip_remote}:8443"], check=True)
        subprocess.run(["ssh", f"{ip_remote}", f"lxc config set core.trust_password {PASSWORD}"], check=True)

        #Conexión remota desde local
        subprocess.run(["lxc", "remote", "add", "remoto", f"{ip_remote}:8443", "--password", PASSWORD, "--accept-certificate"], check=True)

        logger.info("Configurando bridge remoto")
        subprocess.run(["lxc", "network", "set", f"remoto:{BRIDGES['LAN1']}", "ipv4.address", BRIDGES_IPV4["lxdbr0"]], check=True)
        subprocess.run(["lxc", "network", "set", f"remoto:{BRIDGES['LAN1']}", "ipv4.nat", "true"], check=True)

        logger.info("Creando contenedor remoto con MongoDB")
        subprocess.run(["lxc", "copy", VM_NAMES["database"], VM_NAMES["remote_db"]])

        #Corregir DNS en el contenedor remoto 'db'
        subprocess.run(["lxc", "exec", VM_NAMES["remote_db"], "--", "bash", "-c", "echo 'nameserver 8.8.8.8' > /etc/resolv.conf"], check=True)

        #Actualizar paquetes e instalar MongoDB
        install_mongoDB(name=VM_NAMES["remote_db"])

        logger.info("Configurando proxy para acceso a MongoDB")
        subprocess.run(["lxc", "config", "device", "add", VM_NAMES["remote_db"], PROXY, "proxy", f"listen=tcp:{ip_remota}:27017", f"connect=tcp{IP_DB}:27017"], check=True)

        logger.info("Base de datos remota desplegada correctamente")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error durante el despliegue de la BBDD remota: {e}")