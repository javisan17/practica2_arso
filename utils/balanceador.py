import subprocess
from logger import setup_logger, get_logger
from consts import VM_NAMES


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