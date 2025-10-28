import csv
import firebase_admin
from firebase_admin import credentials, firestore
import time
from datetime import datetime
import os
from io import StringIO

# --- Configuración de Firebase ---
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    cred = credentials.Certificate("clave_firebase.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"ERROR: Fallo al inicializar Firebase: {e}")
    exit()

# =========================================================================
# FUNCIONES
# =========================================================================

def get_last_csv_row(file_path):
    """Lee y devuelve SOLO la última fila del CSV."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if len(lines) <= 1:
            return None
        
        # Lógica para leer solo la última línea
        last_line = lines[-1].strip()
        csv_data = StringIO(lines[0] + last_line + '\n')
        reader = csv.DictReader(csv_data)
        return next(reader)
    except Exception:
        return None

def subir_ultimo_registro():
    """Sube SOLO el último registro del CSV."""
    row = get_last_csv_row("datos_ambientales.csv")
    
    if not row:
        return

    try:
        fecha_str = row["fecha"]
        hora_str = row["hora"]
        
        # Crear ID y data
        document_id = f"{fecha_str}_{hora_str.replace(':', '-')}"
        doc_ref = db.collection("datos").document(document_id)

        data = {
            "fecha": fecha_str,
            "hora": hora_str,
            "temperatura": float(row["temperatura"]),
            "humedad": float(row["humedad"]),
            "viento_kmh": float(row["viento_kmh"]),
            "timestamp_subida": firestore.SERVER_TIMESTAMP
        }
        
        # Subida individual (rápida porque es solo 1 registro)
        doc_ref.set(data)
        
        print(f"SUBIDA EXITOSA (Vivo). Documento ID: {document_id}")

    except Exception as e:
        print(f"ERROR: Fallo en la subida en vivo: {e}")


# ==============================
# BUCLE PRINCIPAL DE EJECUCIÓN
# ==============================
if __name__ == "__main__":
    print("\n[INICIANDO ACTUALIZACIÓN EN VIVO (cada 5 segundos)]")
    while True:
        try:
            subir_ultimo_registro()
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nActualizacion detenida por el usuario.")
            break
        except Exception as e:
            print(f"ERROR no manejado en bucle: {e}")
            time.sleep(5)
