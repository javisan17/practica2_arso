import subprocess
from logger import setup_logger, get_logger
from consts import VM_NAMES, IP_S, PUERTO_S, MAX_SERVERS
from utils.containers import start_container
from time import sleep


"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
LB
"""


# def change_netplan_manual(name):
#     """
#     Cambiar el archivo 50-cloud-init.yaml a mano desde un nano del contenedor name (qué será o el balanceador o el cliente)
#     """

#     subprocess.run(["lxc", "exec", name , "--", "nano", "/etc/netplan/50-cloud-init.yaml"], check=True)


def change_netplan(name):
    """
    Cambiar el archivo 50-cloud-init.yaml automáticamente del contenedor name (qué será o el balanceador o el cliente)
    """

    logger.debug(f"Iniciando cambio de netplan en {name}")

    if name not in [VM_NAMES["balanceador"], VM_NAMES["cliente"]]:
        logger.warning(f"{name} no es un contenedor válido para cambiar el netplan.")
        return

    try:
        #Desactivar cloud-init (lo pone en el archivo 50-cloud-init.yaml)
        logger.debug(f"Desactivando cloud-init en {name}")
        subprocess.run(f"lxc exec {name} -- bash -c 'echo \"network: {{config: disabled}}\" > /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg'", shell=True, check=True)

        #Crear una copia de seguridad del archivo original
        logger.debug(f"Creando copia de seguridad del archivo netplan original en {name}")
        subprocess.run(f"lxc exec {name} -- cp /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.bak", shell=True, check=True)

        #Configuración según el tipo de contenedor
        if name == VM_NAMES["balanceador"]:
            logger.debug(f"Configurando interfaces eth0 y eth1 para balanceador {name}")
            netplan_config = """
            network:
                version: 2
                ethernets:
                    eth0:
                        dhcp4: true
                    eth1:
                        dhcp4: true
            """
        elif name == VM_NAMES["cliente"]:
            logger.debug(f"Configurando interfaz eth1 para cliente {name}")
            netplan_config = """
            network:
                version: 2
                ethernets:
                    eth1:
                        dhcp4: true
            """

        #Escribir nueva configuración
        logger.debug(f"Escribiendo nueva configuración de netplan en {name}")
        subprocess.run(f"echo \"{netplan_config}\" | lxc exec {name} -- tee /etc/netplan/50-cloud-init.yaml", shell=True, check=True)

        #Reiniciar contenedor
        logger.debug(f"Reiniciando contenedor {name} para aplicar cambios")
        subprocess.run(f"lxc restart {name}", shell=True, check=True)

        logger.info(f"Configuración de red aplicada correctamente en el contenedor {name}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error cambiando la configuración de red en {name}: {e}")


def install_haproxy():
    """
    Configura el balanceador instalando el haproxy
    """

    logger.info("Instalando haproxy en el balanceador")
    try:
        subprocess.run(["lxc", "exec", VM_NAMES["balanceador"], "--", "apt", "update"], check=True)
        subprocess.run(["lxc", "exec", VM_NAMES["balanceador"], "--", "apt", "install", "-y", "haproxy"], check=True)

    except subprocess.CalledProcessError as e:
        logger.critical(f"Error en instalación de haproxy: {e}")


def setup_haproxy():
    """
    Configura el balanceador del sistema escribiendo el archivo haproxy.cfg con las IPs de los servidores
    """


    #Construir dinámicamente las entradas del backend según servidores existentes
    backend_servers = ""
    for i in range(MAX_SERVERS):
        name = VM_NAMES["servidores"][i]
        result = subprocess.run(["lxc", "info", name], capture_output=True, text=True)
        if "not found" not in result.stderr:
            backend_servers += f"        server webserver{i+1} {IP_S[name]}:{PUERTO_S}\n"

    if not backend_servers:
        logger.warning("No hay servidores configurados para HAProxy. Abortando configuración.")
        return

    logger.debug("Generando archivo de configuración haproxy.cfg")
    haproxy_config = f"""
    global
        log /dev/log local0
        log /dev/log local1 notice
        chroot /var/lib/haproxy
        stats socket /run/haproxy/admin.sock mode 660 level admin
        stats timeout 30s
        user haproxy
        group haproxy
        daemon
    
        # Default SSL material locations
            ca-base /etc/ssl/certs
            crt-base /etc/ssl/private
        # Default ciphers to use on SSL-enabled listening sockets.
        # For more information, see ciphers(1SSL). This list is from:
        # https://hynek.me/articles/hardening-your-web-servers-ssl-ciphers/
        ssl-default-bind-ciphers ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS
        ssl-default-bind-options no-sslv3

    defaults
        log global
        mode http
        option httplog
        option dontlognull
        timeout connect 5000
        timeout client 50000
        timeout server 50000
        errorfile 400 /etc/haproxy/errors/400.http
        errorfile 403 /etc/haproxy/errors/403.http
        errorfile 408 /etc/haproxy/errors/408.http
        errorfile 500 /etc/haproxy/errors/500.http
        errorfile 502 /etc/haproxy/errors/502.http
        errorfile 503 /etc/haproxy/errors/503.http
        errorfile 504 /etc/haproxy/errors/504.http

    frontend firstbalance
        bind *:80
        option forwardfor
        default_backend webservers

    backend webservers
        balance roundrobin
{backend_servers}
        option httpchk
    """

    try:

        #Escribir nueva configuración
        logger.debug("Escribiendo configuración de haproxy en el contenedor")
        subprocess.run(f"echo \"{haproxy_config}\" | lxc exec {VM_NAMES['balanceador']} -- tee /etc/haproxy/haproxy.cfg", shell=True, check=True)

        #Verificar si el archivo es correcto
        logger.debug("Validando archivo haproxy.cfg")
        subprocess.run(["lxc", "exec", VM_NAMES["balanceador"], "--", "haproxy", "-f", "/etc/haproxy/haproxy.cfg", "-c"], check=True)

        #Reiniciar el servicio del balanceador
        logger.debug("Iniciando servicio de haproxy")
        subprocess.run(["lxc", "exec", VM_NAMES["balanceador"], "--", "service", "haproxy", "restart"], check=True)
        logger.info("Haproxy instalado y configurado correctamente.")

    except subprocess.CalledProcessError as e:
        logger.critical(f"Error en configuración de HAProxy: {e}")