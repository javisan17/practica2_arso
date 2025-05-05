"""
JAVIER SÁNCHEZ MAYORAL
ENRIQUE GALINDO ALCOJOR
"""


import sys, subprocess
from logger import setup_logger, get_logger
from consts import VALID_ORDERS, DEFAULT_SERVERS, MIN_SERVERS, MAX_SERVERS, IMAGE_DEFAULT
from ordenes import create_all, start_all, list_containers, delete_all
from ordenes_opcionales import stop_all, create_server, delete_last_server, start_server, stop_server
from utils.file import save_num_servers, load_num_servers
from utils.console import show_consoles, show_console, close_consoles

def main():

    """
    Inicializar LOGGINS
    """

    setup_logger()
    logger = get_logger()


    if len(sys.argv) < 2:
        logger.error("Falta la orden. Uso: python3 pfinal1.py <orden> [número de servidores]")
        print("Uso: python3 pfinal1.py <orden> [número de servidores]")
        return

    orden = sys.argv[1]
    logger.info(f"Orden recibida: {orden}")

    if orden not in VALID_ORDERS:
        logger.error(f"Orden no válida: {orden}")
        print(f"Orden no válida. Usa alguna de: {VALID_ORDERS}")
        return


    #Determinar número de servidores
    if orden == "create":
        if len(sys.argv) == 3:
            try:
                n_servers = int(sys.argv[2])
                if not (MIN_SERVERS <= n_servers <= MAX_SERVERS):
                    raise ValueError()
                logger.info(f"Número de servidores especificado: {n_servers}")
            except ValueError:
                logger.error(f"Número de servidores fuera de rango: {sys.argv[2]}")
                print(f"El número de servidores debe estar entre {MIN_SERVERS} y {MAX_SERVERS}.")
                return
        else:
            #Para cuando no haya un número de servidores, se pone el default 
            n_servers = DEFAULT_SERVERS
            logger.info(f"No se especificó número de servidores. Se usará el valor por defecto: {n_servers}")
    else:
        #Para órdenes distintas de create, cargamos el número guardado
        try:
            n_servers = load_num_servers()
            logger.info(f"Se cargó número de servidores desde archivo: {n_servers}")
        except FileNotFoundError:
            logger.error("Archivo de configuración de servidores no encontrado.")
            print("No se ha encontrado información de servidores. Ejecuta primero 'create'.")
            return

    #ORDENES 

    match orden:
        case "create":
            create_all(n_servers=n_servers)

        case "start":
            start_all(n_servers=n_servers)
            show_consoles(n_servers=n_servers)

        case "list":
            list_containers()

        case "delete":
            delete_all(n_servers=n_servers)

        case "stop":
            stop_all(n_servers=n_servers)
            close_consoles()

        case "create_server":
            if n_servers < MAX_SERVERS:
                create_server()
                n_servers=n_servers+1
                save_num_servers(n_servers)
                logger.info(f"Nuevo número de servidores: {n_servers}")

            else:
                logger.warning("Límite máximo de servidores alcanzado")
                print("No se pueden crear más de 5 servidores.")

        case "delete_last_server":
            if n_servers > MIN_SERVERS:
                delete_last_server()
                n_servers=n_servers-1
                save_num_servers(n_servers)
                logger.info(f"Nuevo número de servidores: {n_servers}")

            else:
                logger.warning("Intento de eliminar servidor por debajo del mínimo")
                print("No se puede eliminar el servidor s1.")

        case "start_server":
            if len(sys.argv) < 3:
                logger.error("Falta el nombre del servidor en start_server")
                print("Uso: python3 pfinal1.py start_server <nombre_servidor>")
                sys.exit(1)
            name=sys.argv[2]
            logger.info(f"Iniciando servidor individual: {name}")
            start_server(name=name)
            show_console(name=name)

        case "stop_server":
            if len(sys.argv) < 3:
                logger.error("Falta el nombre del servidor en stop_server")
                print("Uso: python3 pfinal1.py stop_server <nombre_servidor>")
                sys.exit(1)
            name=sys.argv[2]
            logger.info(f"Deteniendo servidor individual: {name}")
            stop_server(name=name)
        

if __name__ == "__main__":
    main()