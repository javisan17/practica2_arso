cd /root

echo "ARSO - Instalando requisitos: NodeJS y npm"

apt update
sleep 1

apt-get install -y build-essential
sleep 2

curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sleep 1

sudo apt-get install -y nodejs
sleep 2

echo "ARSO - Instalando paquetes npm"

cd /root/app

npm install
sleep 1

npm install forever -g
sleep 1

echo "ARSO - Populando la Bases de Datos MongoDB"

npm run seed
