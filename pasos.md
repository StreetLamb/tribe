Guía para Configurar Servidores Remotos y Entornos Virtuales


Para convertir tu archivo de Word en un documento adecuado para RMarkdown y hacer que sea legible, claro, entretenido y directo para el ámbito de la economía, lo primero es reorganizar las secciones con un enfoque paso a paso, usando encabezados claros y proporcionando descripciones concisas. A continuación te muestro una propuesta de estructura basada en el contenido extraído del archivo:

Título del documento
Guía para Configurar Servidores Remotos y Entornos Virtuales

1. Conexión y Generación de Llaves SSH
Para conectarte a un servidor remoto de forma segura, es fundamental generar un par de llaves SSH. A continuación, te muestro los pasos para realizar esta configuración en Windows PowerShell:

# Navegar al directorio de llaves
cd .\.ssh\
ls

# Generar un par de llaves
ssh-keygen -b 2048 -t rsa -C "tu_correo_ejemplo" -f tu_nombre

# Verificar que las llaves se han creado
cd .\.ssh\
ls

# Abrir y copiar la llave pública
notepad .\tu_nombre.pub

Utiliza la llave pública para autenticarte en el servidor. Una vez autenticado, puedes conectarte con:

ssh usuario@servidor -i .\.ssh\tu_nombre

2. Uso de WinSCP y Configuración de llaves en formato PPK
Si necesitas usar WinSCP para transferir archivos, es necesario convertir la llave SSH generada a formato PPK:

https://creodias.docs.cloudferro.com/en/latest/networking/How-to-convert-Linux-Openssh-key-to-Putty-format-on-Creodias.html

3. Configuración de VS Code para SSH
Puedes configurar el acceso SSH en Visual Studio Code siguiendo estos pasos:

Abre la configuración de host en c:\Users\tu_usuario\.ssh\config.

Añade la siguiente configuración en el archivo de texto:

Host tu_servidor
    HostName servidor.ejemplo.com
    User tu_usuario
    IdentityFile C:\Users\tu_usuario\.ssh\tu_nombre

Conéctate desde la terminal de VS Code seleccionando "Connect in current window".

4. Gestión de Entornos Virtuales y Librerías
Para evitar incompatibilidades entre librerías, es recomendable crear y activar un entorno virtual:

# Instalar y activar entorno virtual
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate

Si necesitas gestionar dependencias adicionales, como Poetry para proyectos en Python, sigue estos pasos:

# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3

# Verificar instalación
poetry --version

# Añadir nuevas librerías
poetry add reportlab=="^3.6.12"

5. Solución de Errores Comunes
Al trabajar con entornos de desarrollo, pueden surgir errores. Aquí algunos ejemplos y cómo solucionarlos:

Error con pip:
curl -sSL https://install.python-poetry.org | python3 -

Problemas con psycopg2:
sudo apt-get install libpq-dev
sudo poetry add psycopg2-binary

6. Subir Cambios con Git
Para contribuir en repositorios Git, puedes seguir estos pasos para configurar commits y subir cambios:

# Crear nueva rama y configuración de usuario
git checkout -b nueva_rama
git config --global user.name "TuNombre"
git config --global user.email "tu_correo@ejemplo.com"

# Subir los cambios
git push origin nueva_rama

7. Solución de Problemas con Docker
Si tienes problemas al interactuar con Docker y no tienes permisos, puedes ejecutar los siguientes comandos con permisos de superusuario:

sudo docker-compose -f docker-compose.yml -f docker-compose.local.yml down

En caso de que obtengas un error relacionado con permisos denegados, como:

permission denied while trying to connect to the Docker daemon socket

Debes agregar tu usuario al grupo de Docker

sudo usermod -aG docker tu_usuario

Luego, reinicia Docker para asegurarte de que no haya procesos "zombie":

sudo systemctl restart docker
sudo systemctl status docker

8. Crear y Gestionar Skills
En algunos casos, es posible que los archivos tengan permisos limitados que impidan la creación de nuevos archivos o la edición de existentes. Si te enfrentas a este problema, puedes cambiar los permisos del directorio o archivo deseado:

sudo chmod -R 775 /usr/dockerapps/tribe/backend/app/core/graph/skills

Para verificar los permisos después de cambiar:

ls -ld /usr/dockerapps/tribe/backend/app/core/graph/skills

9. Instalación de Dependencias en Sistemas Basados en Debian/Ubuntu
En distribuciones basadas en Debian o Ubuntu, es necesario instalar las herramientas de compilación requeridas, como GCC y las bibliotecas de desarrollo de Python. Ejecuta los siguientes comandos:

sudo apt update
sudo apt install build-essential python3-dev

10. Solución de Errores con psycopg2
Si obtienes errores al intentar instalar psycopg2 debido a la falta de herramientas de desarrollo en Linux, puedes instalar las dependencias necesarias con:
sudo apt-get install libpq-dev

Luego, instala psycopg2 usando Poetry:
sudo poetry add psycopg2-binary

12. Actualización de Versiones y Permisos en Poetry
Cuando trabajes con versiones específicas de paquetes en Poetry, asegúrate de especificar las versiones correctas para evitar errores. Por ejemplo, al añadir grpcio, puedes hacerlo así:
poetry add grpcio="^1.66.1"



