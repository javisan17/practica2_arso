import subprocess
import socket
from logger import setup_logger, get_logger
from consts import VM_NAMES, PASSWORD, BRIDGES, BRIDGES_IPV4, PROXY, IP_DB, REMOTO
from utils.database import install_mongoDB
from utils.bridges import config_bridge
from utils.containers import stop_container
from utils.validator import container_is_running


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

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # IP usada por defecto para salir hacia Internet y conectarse a otros hosts
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            logger.info(f"IP local detectada: {ip}")
            return ip
    except Exception as e:
        logger.error(f"No se pudo obtener la IP local: {e}")
        return None



def get_ip_remote(name):
    """
    Obtener la IP fisica del computador remoto. El parámetro name debe ser ej. l022
    """

    try:
        #Se obtiene el nombre de red del ordenador remoto
        nombre_completo = f"{name}.lab.dit.upm.es"
        #Se obtiene su IP
        ip = socket.gethostbyname(nombre_completo)
        logger.info(f"Nombre remoto detectado: {nombre_completo} cuya IP: {ip}")
        return ip
    except socket.gaierror as e:
        logger.error(f"No se pudo resolver el nombre {name}: {e}")
    except Exception as e:
        logger.error(f"Error al obtener la IP remota de {name}: {e}")
    return None


def deploy_remote_db(ip_local, ip_remote):
    """
    Despliega y configura automáticamente un contenedor remoto con MongoDB.
    """

    try:
        logger.info("Configurando acceso remoto a LXD en ambos equipos")
        

        #Configuración remota usando ssh (requiere clave pública copiada al remoto)
        subprocess.run(["ssh", f"{ip_remote}", f"lxc config set core.https_address {ip_remote}:8443"], check=True)
        subprocess.run(["ssh", f"{ip_remote}", f"lxc config set core.trust_password {PASSWORD}"], check=True)

        #Conexión remota desde local
        subprocess.run([f"lxc", "config", "set", "core.https_address", f"{ip_local}:8443"], check=True)
        
        #Comprobar si ya existe un remote que se llame remoto, se podría hacer como una función y luego llamarla aquí
        logger.info("Conectando al LXD remoto desde local")
        result = subprocess.run(["lxc", "remote", "list"], capture_output=True, text=True)
        if REMOTO in result.stdout:
            subprocess.run(["lxc", "remote", "remove", REMOTO], check=True)

        subprocess.run(["lxc", "remote", "add", REMOTO, f"{ip_remote}:8443", "--password", PASSWORD, "--accept-certificate"], check=True)

        #Configuración del bridge remoto 
        logger.info("Configurando bridge remoto")

        subprocess.run(["lxc", "network", "set", f"{REMOTO}:{BRIDGES['LAN1']}", "ipv4.address", BRIDGES_IPV4["lxdbr0"]], check=True)
        subprocess.run(["lxc", "network", "set", f"{REMOTO}:{BRIDGES['LAN1']}", "ipv4.nat", "true"], check=True)

        #logger.info("Creando contenedor remoto con MongoDB")
        #subprocess.run(["lxc", "copy", VM_NAMES["database"], VM_NAMES["remote_db"]])

        #Corregir DNS en el contenedor remoto 'db'
        #subprocess.run(["lxc", "exec", VM_NAMES["remote_db"], "--", "bash", "-c", "echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf"], check=True)

        #Actualizar paquetes e instalar MongoDB
        #install_mongoDB(name=VM_NAMES["remote_db"])

        #Copiar el contenedor db al equipo remoto
        result = subprocess.run(["lxc", "list", f"{REMOTO}:{VM_NAMES['database']}"], capture_output=True, text=True)
        if VM_NAMES['database'] in result.stdout:
            logger.info(f"El contenedor {VM_NAMES['database']} ya existe en remoto. No se copia.")
            return
        if container_is_running(VM_NAMES["database"]):
            logger.info(f"El contenedor '{VM_NAMES['database']}' está en ejecución. Deteniéndolo...")
            stop_container(name=VM_NAMES['database'])
        else:
            logger.info(f"El contenedor '{VM_NAMES['database']}' ya está detenido.")
        subprocess.run(["lxc", "copy", VM_NAMES['database'], f"{REMOTO}:{VM_NAMES['database']}"], check=True)
        logger.info("Base de datos copiada al equipo remoto")

        #Crear proxy para acceso remoto a la base de datos
        logger.info("Configurando proxy para acceso a MongoDB")
        subprocess.run(["lxc", "config", "device", "add", f"{REMOTO}:{VM_NAMES['database']}", PROXY, "proxy", f"listen=tcp:{ip_remote}:27017", f"connect=tcp:{IP_DB}:27017"], check=True)

        logger.info("Base de datos remota desplegada correctamente")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error durante el despliegue de la BBDD remota: {e}")


