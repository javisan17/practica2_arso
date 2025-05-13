import subprocess
from consts import VM_NAMES, NUM_SERVERS_FILE, IMAGE_DEFAULT, BRIDGES_IPV4, IP_LB, BRIDGES, MAX_SERVERS, MIN_SERVERS, IP_CL, IP_S, IP_DB
from logger import setup_logger, get_logger
from utils.containers import create_container, start_container, stop_container, delete_container, config_container
from utils.image import create_image, delete_image
from utils.bridges import create_bridge, config_bridge, attach_network, delete_bridge
from utils.file import save_num_servers
from utils.balanceador import change_netplan, config_lb, change_haproxy
from utils.server_web import config_server
from utils.database import install_mongoDB



"""
Inicializar LOGGINS
"""


setup_logger()
logger = get_logger()


"""
ORDENES
"""


def create_all(n_servers):
    """
    Crea la infraesctrutura de la red completa (CREATE)
    """

    logger.info(f"Iniciando creación de infraestructura con {n_servers} servidores")
    logger.debug(f"Parámetro recibido n_servers={n_servers}")

    try:
        logger.debug("Creando imagen base...")

        #Crear imagen
        create_image()

        logger.debug("Configurando y creando bridges...")

        #Crear bridges lxdbr0 y lxdbr1
        #create_bridge(bridge_name=BRIDGES["LAN1"])
        config_bridge(bridge_name=BRIDGES["LAN1"], ipv4=BRIDGES_IPV4["lxdbr0"])
        create_bridge(bridge_name=BRIDGES["LAN2"])
        config_bridge(bridge_name=BRIDGES["LAN2"], ipv4=BRIDGES_IPV4["lxdbr1"])

        logger.debug("Creando contenedores de servidores...")

        #Crear servidores
        for i in range(n_servers):
            create_container(name=VM_NAMES["servidores"][i])
            attach_network(container=VM_NAMES["servidores"][i], bridge=BRIDGES["LAN1"], iface="eth0")
            config_container(name=VM_NAMES["servidores"][i], iface="eth0", ip=IP_S[f"s{i+1}"])

            # start_container(name=VM_NAMES["servidores"][i])
            # config_server(name=VM_NAMES["servidores"][i])
            # stop_container(name=VM_NAMES["servidores"][i])

        #Guardar número de servidores
        save_num_servers(n_servers)
        logger.info("Número de servidores guardados correctamente")
        
        logger.debug("Creando balanceador...")

        #Crear balanceador
        create_container(name=VM_NAMES["balanceador"])
        attach_network(container=VM_NAMES["balanceador"], bridge=BRIDGES["LAN1"], iface="eth0")
        config_container(name=VM_NAMES["balanceador"], iface="eth0", ip=IP_LB["eth0"])
        attach_network(container=VM_NAMES["balanceador"], bridge=BRIDGES["LAN2"], iface="eth1")
        config_container(name=VM_NAMES["balanceador"], iface="eth1", ip=IP_LB["eth1"])

        #Cambiar el archivo 50-cloud-init.yaml para tener las dos subredes
        start_container(name=VM_NAMES["balanceador"])
        change_netplan(name=VM_NAMES["balanceador"])
        stop_container(name=VM_NAMES["balanceador"])
        logger.info("Balanceador configurado correctamente")

        logger.debug("Creando cliente...")

        #Crear cliente
        create_container(name=VM_NAMES["cliente"])
        attach_network(container=VM_NAMES["cliente"], bridge=BRIDGES["LAN2"], iface="eth1")
        config_container(name=VM_NAMES["cliente"], iface="eth1", ip=IP_CL)

        #Cambiar el archivo 50-cloud-init.yaml para tener la subred adecuada
        start_container(name=VM_NAMES["cliente"])
        change_netplan(name=VM_NAMES["cliente"])
        stop_container(name=VM_NAMES["cliente"])
        logger.info("Cliente configurado correctamente")

        #Crear base de datos
        create_container(name=VM_NAMES["database"])
        attach_network(container=VM_NAMES["database"], bridge=BRIDGES["LAN1"], iface="eth0")
        config_container(name=VM_NAMES["database"], iface="eth0", ip=IP_DB)

        logger.info("Infraestructura creada correctamente.")

    except Exception as e:
        logger.critical(f"Error crítico en creación de infraestructura: {e}", exc_info=True)


def start_all(n_servers):
    """
    Arrancar todos los contenedores
    """

    logger.info("Iniciando todos los contenedores")
    try:
        for i in range(n_servers):
            logger.debug(f"Arrancando servidor: {VM_NAMES['servidores'][i]}")
            start_container(name=VM_NAMES["servidores"][i])
        start_container(name=VM_NAMES["cliente"])
        start_container(name=VM_NAMES["balanceador"])
        start_container(name=VM_NAMES["database"])
        logger.info("Todos los contenedores han sido iniciados correctamente")
    except Exception as e:
        logger.error(f"Error al iniciar contenedores: {e}", exc_info=True)


def list_containers():
    """
    Listar los contenedor
    """

    logger.info("Listando contenedores")
    try:
        subprocess.run(["lxc", "list"])
        logger.debug("Comando 'lxc list' ejecutado correctamente")
    except Exception as e:
        logger.error(f"Error al listar contenedores: {e}", exc_info=True)


def delete_all(n_servers):
    """
    Eliminar todo (VM y conexiones)
    """

    logger.info("Eliminando toda la infraestructura")

    try:
        #Eliminar imagen
        delete_image()

        #Eliminar contenedores
        for i in range(n_servers):
            delete_container(name=VM_NAMES["servidores"][i])
        delete_container(name=VM_NAMES["cliente"])
        delete_container(name=VM_NAMES["balanceador"])
        delete_container(name=VM_NAMES["database"])
        logger.debug("Contenedores eliminados correctamente")


        #Eliminar conexiones (bridges). Se opta por no eliminar el bridge lxdbr0 por ser el bridge creado por el profile default
        delete_bridge(bridge=BRIDGES["LAN2"])

        logger.info("Eliminación completada.")
    except Exception as e:
        logger.critical(f"Fallo crítico al eliminar infraestructura: {e}", exc_info=True)


def configure_all(n_servers):
    """
    POSIBILIDADES: si ya hay servidores solo los configura y si no hay servidores, los crea y configura o si no los hay decir que antes el usuario deba ejecutar un create
    DE MOMENTO SOLO VOY A HACERLO CON CONFIGURAR YA SE AÑADIRÁN SI QUIERES
    """

    #Instalar MongoDB en la base de datos
    # start_container(name=VM_NAMES["database"])
    install_mongoDB(name=VM_NAMES["database"]) 
    # stop_container(name=VM_NAMES["database"])

    #Instalar el servicio de NodeJS en servidores 
    for i in range(n_servers):
        # start_container(name=VM_NAMES["servidores"][i])
        config_server(name=VM_NAMES["servidores"][i])
        # stop_container(name=VM_NAMES["servidores"][i])

    #Instalar y configurar el haproxy para la repartición de carga
    # start_container(name=VM_NAMES["balanceador"])
    config_lb()
    change_haproxy()
    # stop_container(name=VM_NAMES["balanceador"])
   
