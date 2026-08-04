import os
import sys
import json
import datetime
import webbrowser
import pandas as pd
import base64
import hashlib
import subprocess

def encrypt_data(data_str, password):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import padding
    
    # Derive key using SHA-256
    key = hashlib.sha256(password.encode('utf-8')).digest()
    
    # Generate random 16-byte IV
    iv = os.urandom(16)
    
    # Pad plaintext (PKCS7)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data_str.encode('utf-8')) + padder.finalize()
    
    # Encrypt (AES-CBC)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Prepend IV to ciphertext and base64 encode
    combined = iv + ciphertext
    return base64.b64encode(combined).decode('utf-8')

def git_push():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(script_dir, ".git")):
        print("\n[AVISO GITHUB] Git no está inicializado en esta carpeta.")
        print("Sigue los pasos en 'INSTRUCCIONES_GITHUB.md' para poder acceder de forma remota.")
        return
        
    print("\n[GITHUB] Detectado repositorio Git. Subiendo cambios a GitHub...")
    try:
        subprocess.run(["git", "add", "."], cwd=script_dir, check=True)
        commit_msg = f"Actualizacion automatica de ventas - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=script_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result = subprocess.run(["git", "push", "origin", "main", "--force"], cwd=script_dir, capture_output=True, text=True)
        if result.returncode == 0:
            print("¡Cambios subidos a GitHub exitosamente!")
        else:
            print("[AVISO GITHUB] No se pudo subir automáticamente a GitHub. Esto suele suceder si aún no has completado la autenticación de Git por primera vez en la PC.")
            print("Detalles del error:")
            print(result.stderr)
    except Exception as e:
        print(f"[ERROR GITHUB] Ocurrió un error al ejecutar los comandos de Git: {e}")


def clean_string(val):
    if not isinstance(val, str):
        if pd.isnull(val):
            return ""
        return str(val).strip()
    
    # Correct CP850 character encoding issues (165 -> Ñ, 167 -> º)
    val = val.replace(chr(165), 'Ñ').replace(chr(167), 'º')
    return val.strip()

def parse_date(val):
    if pd.isnull(val):
        return None
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.strftime('%Y-%m-%d')
    if isinstance(val, pd.Timestamp):
        return val.strftime('%Y-%m-%d')
    
    # Try parsing string
    val_str = str(val).strip()
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d/%m/%y', '%d-%m-%Y', '%d-%m-%y'):
        try:
            dt = datetime.datetime.strptime(val_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
            
    # Try pandas parser as fallback
    try:
        dt = pd.to_datetime(val_str)
        if pd.notnull(dt):
            return dt.strftime('%Y-%m-%d')
    except:
        pass
        
    return val_str

def main():
    print("Iniciando actualizacion de datos desde planillas Excel...")
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List all excel files in this directory
    files = [f for f in os.listdir(script_dir) if f.endswith('.xlsx') and not f.startswith('~$')]
    
    if not files:
        print("No se encontraron archivos Excel (.xlsx) en esta carpeta.")
        input("Presione Enter para salir...")
        sys.exit(1)
        
    print(f"Archivos encontrados: {len(files)}")
    
    consolidated_data = []
    
    for file_name in files:
        file_path = os.path.join(script_dir, file_name)
        print(f"Procesando: {file_name} ...")
        try:
            # Load the sheet without headers first to locate the header row
            df = pd.read_excel(file_path, header=None)
            
            # Find the header row by searching for 'fecha', 'especie', 'nomprv'
            header_row_idx = None
            for idx in range(len(df)):
                row_vals = [str(x).strip().lower() for x in df.iloc[idx].values]
                if 'fecha' in row_vals and 'especie' in row_vals and 'nomprv' in row_vals:
                    header_row_idx = idx
                    break
            
            if header_row_idx is None:
                print(f"  [AVISO] No se encontro la fila de cabecera en {file_name}. Se omitira este archivo.")
                continue
                
            # Parse columns and data
            headers = [str(x).strip() for x in df.iloc[header_row_idx].values]
            data_df = df.iloc[header_row_idx+1:].copy()
            data_df.columns = headers
            
            # Filter rows: remove null dates, null products, and total rows
            data_df = data_df[data_df['fecha'].notnull()]
            data_df = data_df[data_df['especie'].notnull()]
            data_df = data_df[~data_df['especie'].astype(str).str.strip().str.lower().str.startswith('total')]
            
            # Process and clean each cell
            for _, row in data_df.iterrows():
                try:
                    fecha = parse_date(row.get('fecha'))
                    if not fecha:
                        continue
                        
                    especie = clean_string(row.get('especie'))
                    variedad = clean_string(row.get('variedad'))
                    zp = clean_string(row.get('zp'))
                    calidad = clean_string(row.get('calidad'))
                    present = clean_string(row.get('present'))
                    tamano = clean_string(row.get('tamano'))
                    nomenv = clean_string(row.get('nomenv'))
                    nomprv = clean_string(row.get('nomprv'))
                    
                    # Unificar proveedor "BONELLA", "JORGE ALCIDES BONELLA" y "JOSE ALCID"
                    nomprv_upper = nomprv.upper()
                    if (
                        nomprv_upper == "BONELLA" or 
                        nomprv_upper == "JORGE ALCIDES BONELLA" or 
                        nomprv_upper == "JOSE ALCID" or
                        ("BONELLA" in nomprv_upper and ("JORGE" in nomprv_upper or "ALCIDES" in nomprv_upper)) or
                        ("JOSE" in nomprv_upper and "ALCID" in nomprv_upper)
                    ):
                        nomprv = "BONELLA, JORGE ALCIDES"
                    
                    # Numeric conversions with fallback to 0
                    try:
                        ventas = int(row.get('ventas', 0))
                    except:
                        ventas = 0
                        
                    try:
                        recaudado = float(row.get('recaudado', 0.0))
                    except:
                        recaudado = 0.0
                        
                    try:
                        promedio = float(row.get('promedio', 0.0))
                    except:
                        promedio = 0.0
                        
                    guia = str(row.get('it1', '')).strip()
                    # Remove trailing decimal in ticket/guide if imported as float (e.g. "160577.0")
                    if guia.endswith('.0'):
                        guia = guia[:-2]
                        
                    lote = str(row.get('it2', '')).strip()
                    if lote.endswith('.0'):
                        lote = lote[:-2]
                        
                    # Separar productos por variedad si son tomate o cherry
                    especie_upper = especie.upper()
                    if (especie_upper in ["TOMATE", "CHERRY", "CHERRY RAC"]) and variedad:
                        especie = f"{especie} {variedad}"
                        
                    consolidated_data.append({
                        'fecha': fecha,
                        'guia': guia,
                        'lote': lote,
                        'producto': especie,
                        'variedad': variedad,
                        'procedencia': zp,
                        'calidad': calidad,
                        'presentacion': present,
                        'tamano': tamano,
                        'envase': nomenv,
                        'proveedor': nomprv,
                        'bultos': ventas,
                        'recaudado': recaudado,
                        'promedio': promedio,
                        'origen_archivo': file_name
                    })
                except Exception as row_err:
                    print(f"  [AVISO] Error procesando una fila en {file_name}: {row_err}")
                    
        except Exception as e:
            print(f"  [ERROR] No se pudo procesar el archivo {file_name}: {e}")
            
    if not consolidated_data:
        print("No se pudieron extraer datos validos de los archivos Excel.")
        input("Presione Enter para salir...")
        sys.exit(1)
        
    # Convert back to DataFrame to de-duplicate records
    df_all = pd.DataFrame(consolidated_data)
    initial_len = len(df_all)
    
    # De-duplicate: Keep first record for duplicates in key columns
    df_all = df_all.drop_duplicates(subset=[
        'fecha', 'guia', 'lote', 'producto', 'variedad', 
        'procedencia', 'calidad', 'envase', 'proveedor', 
        'bultos', 'recaudado'
    ])
    
    final_len = len(df_all)
    print(f"Total registros leidos: {initial_len}. Duplicados eliminados: {initial_len - final_len}.")
    print(f"Total registros unicos: {final_len}.")
    
    # Sort data by Date descending, then Product
    df_all = df_all.sort_values(by=['fecha', 'producto'], ascending=[False, True])
    
    # Convert data back to list of dicts
    cleaned_records = df_all.to_dict(orient='records')
    
    # Encrypt the records to a JSON string using password
    json_str = json.dumps(cleaned_records, ensure_ascii=False)
    try:
        encrypted_b64 = encrypt_data(json_str, "Inf05201.")
    except Exception as enc_err:
        print(f"Error encriptando los datos: {enc_err}")
        print("Asegurese de tener instalada la libreria 'cryptography' (se instala corriendo actualizar.bat).")
        input("Presione Enter para salir...")
        sys.exit(1)
    
    # Write to javascript database file
    js_content = f"""// Archivo generado automaticamente por el actualizador con encriptacion AES.
// Ultima actualizacion: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

window.encryptedData = "{encrypted_b64}";
window.lastUpdate = "{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}";
"""
    
    output_js_path = os.path.join(script_dir, "dashboard_data.js")
    try:
        with open(output_js_path, "w", encoding="utf-8") as f:
            f.write(js_content)
        print(f"Base de datos encriptada correctamente en: {output_js_path}")
    except Exception as e:
        print(f"Error escribiendo el archivo de datos: {e}")
        input("Presione Enter para salir...")
        sys.exit(1)
        
    # Push updates to GitHub Pages
    git_push()
        
    # Open dashboard in browser
    html_path = os.path.join(script_dir, "index.html")
    if os.path.exists(html_path):
        print("Abriendo el dashboard en el navegador...")
        webbrowser.open('file://' + os.path.realpath(html_path))
    else:
        print(f"[AVISO] No se encontro el archivo 'index.html' en la carpeta.")
        
    print("Proceso completado exitosamente!")
    # Wait a moment before exit
    import time
    time.sleep(2)

if __name__ == '__main__':
    main()
