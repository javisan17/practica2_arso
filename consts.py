"""
CONSTS
"""

VALID_ORDERS=['create', 'start', 'list', 'delete', 'stop', 'create_server', 'delete_last_server', 'start_server', 'stop_server', 'configure', 'enlarge', 'configure_server', 'configure_remote']
NUM_SERVERS_FILE="static/files/num_serves.txt"
DEFAULT_SERVERS=2
MIN_SERVERS=1
MAX_SERVERS=5

IMAGE_DEFAULT="ubuntu2004"
ALIAS_IMAGEN_SERVIDOR="servidor"

#Nombres

VM_NAMES={
    "cliente": "cl",
    "balanceador": "lb",
    "servidores": ["s1", "s2", "s3", "s4", "s5"],
    "database": "db",
    "remote_db": "remote:db"
}

BRIDGES={
    "LAN1": "lxdbr0",
    "LAN2": "lxdbr1"
}


#IPs

BRIDGES_IPV4={
    "lxdbr0": "134.3.0.1/24",
    "lxdbr1": "134.3.1.1/24"
}

IP_LB={
    "eth0": "134.3.0.10",
    "eth1": "134.3.1.10"
}

IP_CL="134.3.1.11"

IP_S={
    "s1": "134.3.0.11",
    "s2": "134.3.0.12",
    "s3": "134.3.0.13",
    "s4": "134.3.0.14",
    "s5": "134.3.0.15"
}

PUERTO_S=8001

IP_DB="134.3.0.20"

#Rutas de archivos

# NODE_JS_FILE="static/files/install.sh"

# APP_WEB_FILE="static/files/app.tar.gz"

import os

# Ruta absoluta a la raíz del proyecto (donde está pfinal2.py)
PROJECT_ROOT = os.path.abspath(os.path.abspath(__file__) + "/..")

# Ruta absoluta a la carpeta static/files
STATIC_FILES = os.path.join(PROJECT_ROOT, "static", "files")

# Archivos importantes
APP_WEB_FILE = os.path.join(STATIC_FILES, "app.tar.gz")
NODE_JS_FILE = os.path.join(STATIC_FILES, "install.sh")


#Remoto
REMOTO="remoto"
PASSWORD="mypass"
PROXY="myproxy"