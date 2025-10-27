import csv
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- Configuración de Firebase ---
cred = credentials.Certificate("clave_firebase.json")
firebase_admin.initialize_app(cred)

db = firestore.client()  # Conexión a Firestore


def subir_datos():
    """Lee el CSV y sube los datos a Firestore."""
    with open("datos_ambientales.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            fecha = row["fecha"]
            hora = row["hora"].replace(":", "-")

            # Colección estructurada por fecha
            doc_ref = db.collection("datos").document(fecha).collection("registros").document(hora)

            # Subir o actualizar los datos
            doc_ref.set({
                "fecha": fecha,
                "hora": row["hora"],
                "temperatura": float(row["temperatura"]),
                "humedad": float(row["humedad"]),
                "viento_kmh": float(row["viento_kmh"]),
                "timestamp": firestore.SERVER_TIMESTAMP  # Marca de tiempo automática
            })
    print("✅ Datos subidos/actualizados en Firestore.")


# --- Actualización automática cada 5 segundos ---
if __name__ == "__main__":
    print("Iniciando actualización automática de Firestore...")
    while True:
        try:
            subir_datos()
            time.sleep(5)  # Espera 5 segundos
        except KeyboardInterrupt:
            print("\nActualización detenida por el usuario.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)
