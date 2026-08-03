# Guía de Publicación en GitHub Pages (Acceso Remoto)

Esta guía te ayudará a instalar Git por primera vez, vincular tu PC con tu cuenta de GitHub, y crear un nuevo repositorio para hospedar tu dashboard con contraseña para acceder desde cualquier celular o notebook.

---

## Paso 1: Instalar Git en tu PC

Dado que no tienes Git instalado en tu PC, debemos descargarlo para que el actualizador automático pueda subir los archivos a internet:

1. Ingresa a la página oficial: [Descargar Git para Windows](https://git-scm.com/download/win).
2. Haz clic en **"Click here to download"** (se descargará la versión de 64 bits para Windows).
3. Abre el archivo descargado e instálalo. Puedes dejar todas las opciones por defecto haciendo clic en **Next** (Siguiente) hasta finalizar la instalación.

---

## Paso 2: Crear el nuevo repositorio en tu cuenta de GitHub

1. Ingresa a [GitHub](https://github.com/) e inicia sesión con tu cuenta.
2. En la esquina superior derecha, haz clic en el botón **"+"** y selecciona **"New repository"** (Nuevo repositorio).
3. Configura el repositorio:
   - **Repository name**: Ponle un nombre, por ejemplo: `venta-mcba`.
   - **Public/Private**: Selecciona **Public** (Público). 
     > *Nota: No te preocupes por que sea público, ya que todos tus datos de ventas estarán fuertemente encriptados con contraseña militar (AES) antes de subirse. Nadie podrá ver tus datos de ventas sin la contraseña.*
   - **Initialize this repository with**: Deja todas las opciones desmarcadas (no agregues README ni .gitignore).
4. Haz clic en **"Create repository"** (Crear repositorio).
5. GitHub te mostrará una página con una serie de comandos. Deja esa página abierta, ya que necesitaremos la dirección web del repositorio (se parece a `https://github.com/tu-usuario/venta-mcba.git`).

---

## Paso 3: Inicializar la carpeta local y vincularla a GitHub

Para este paso, solo deberás abrir una terminal (PowerShell o CMD) en la carpeta de tu proyecto (`c:\Users\Matias\Mi unidad\antigravity\venta mcba`) y ejecutar los siguientes comandos por única vez (reemplaza `tu-usuario` por tu nombre de usuario real de GitHub):

```bash
# 1. Inicializar repositorio de Git local
git init

# 2. Configurar tu identidad en Git (usa el correo de tu cuenta de GitHub)
git config --global user.name "Comercial"
git config --global user.email "tu-correo-de-github@ejemplo.com"

# 3. Vincular con tu repositorio remoto de GitHub
git remote add origin https://github.com/tu-usuario/venta-mcba.git

# 4. Cambiar el nombre de la rama principal a "main"
git branch -M main
```

---

## Paso 4: Primer Envío y Autenticación

1. Ejecuta el archivo **`actualizar.bat`**. Este detectará que Git está configurado y procesará los datos, encriptándolos e intentando subirlos a GitHub.
2. Al ejecutar la subida por primera vez, Windows abrirá una pequeña ventana del **Git Credential Manager** pidiéndote iniciar sesión en GitHub.
3. Haz clic en **"Sign in with your browser"** (Iniciar sesión con tu navegador). Tu navegador web se abrirá pidiéndote autorizar la conexión. Haz clic en **Authorize** o ingresa tus datos.
4. Una vez autorizado, Git guardará tus credenciales en tu PC y subirá los archivos. A partir de este momento, **`actualizar.bat`** subirá todo automáticamente en un segundo sin volver a pedirte credenciales.

---

## Paso 5: Activar GitHub Pages (Tu enlace web)

Una vez subidos los archivos por primera vez, sigue estos pasos para activar tu página web:

1. Ve a la página de tu repositorio en GitHub (`https://github.com/tu-usuario/venta-mcba`).
2. Haz clic en la pestaña **"Settings"** (Configuración) en el menú superior del repositorio.
3. En el menú lateral izquierdo, haz clic en **"Pages"**.
4. En la sección **"Build and deployment"**, bajo **"Branch"**:
   - Cambia `None` por **`main`**.
   - Deja la carpeta en `/ (root)`.
   - Haz clic en el botón **"Save"** (Guardar).
5. Espera aproximadamente 1 minuto. Recarga la página de configuración y arriba verás un banner que dice:
   `"Your site is live at https://tu-usuario.github.io/venta-mcba/"`

¡Listo! Ese es tu enlace web para acceder al dashboard desde cualquier celular, tablet o computadora con la contraseña `Inf05201.`.
