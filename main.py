import csv
import random
import os
from datetime import datetime, timedelta

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================
dias_minimos = 10           # Mínimo de días a asegurar en el archivo
intervalo = 30              # Intervalo en minutos
archivo = "datos_ambientales.csv"

# Rangos de variables simuladas
temp_min, temp_max = 19, 31      # °C
hum_min, hum_max = 80, 95        # %
viento_min, viento_max = 5, 12   # km/h

# Rango horario por día
hora_inicio = 6   # 06:00 AM
hora_fin = 23     # 23:30 PM

# ==============================
# FUNCIONES AUXILIARES
# ==============================

def leer_fechas_existentes(nombre_archivo):
    """Devuelve un set con las fechas (YYYY-MM-DD) ya presentes en el CSV."""
    if not os.path.exists(nombre_archivo):
        return set()
    fechas = set()
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        next(f)  # saltar encabezado
        for linea in f:
            partes = linea.strip().split(",")
            if len(partes) >= 1:
                fechas.add(partes[0])
    return fechas


def generar_datos_dia(dia, writer):
    """Genera los datos de un día completo y los escribe con el writer CSV."""
    inicio = datetime.combine(dia, datetime.min.time()).replace(hour=hora_inicio, minute=0)
    fin = datetime.combine(dia, datetime.min.time()).replace(hour=hora_fin, minute=30)
    actual = inicio

    while actual <= fin:
        hora = actual.hour

        # Patrón diario de temperatura
        if 6 <= hora <= 12:
            temperatura = random.uniform(temp_min, temp_max - 3)
        elif 12 < hora <= 17:
            temperatura = random.uniform(temp_max - 2, temp_max)
        else:
            temperatura = random.uniform(temp_min, temp_min + 4)

        # Ruido aleatorio
        temperatura += random.uniform(-0.5, 0.5)
        humedad = random.uniform(hum_min, hum_max)
        viento = random.uniform(viento_min, viento_max)

        writer.writerow([
            actual.strftime("%Y-%m-%d"),
            actual.strftime("%H:%M"),
            round(temperatura, 1),
            round(humedad, 1),
            round(viento, 1)
        ])

        actual += timedelta(minutes=intervalo)


# ==============================
# LÓGICA PRINCIPAL
# ==============================

# Crear archivo si no existe
nuevo_archivo = not os.path.exists(archivo)
if nuevo_archivo:
    with open(archivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fecha", "hora", "temperatura", "humedad", "viento_kmh"])
    print(f"📄 Archivo '{archivo}' creado.")

# Leer días existentes en el CSV
fechas_existentes = leer_fechas_existentes(archivo)

# Calcular rango de días a asegurar
hoy = datetime.now().date()
ultimo_dia = hoy - timedelta(days=1)  # hasta ayer (día completo)
primer_dia = ultimo_dia - timedelta(days=dias_minimos - 1)

# Determinar qué días faltan
dias_faltantes = []
fecha = primer_dia
while fecha <= ultimo_dia:
    if fecha.strftime("%Y-%m-%d") not in fechas_existentes:
        dias_faltantes.append(fecha)
    fecha += timedelta(days=1)

# Generar datos si faltan
if not dias_faltantes:
    print(f"⚠️ Ya existen datos para los últimos {dias_minimos} días. No se agregó nada nuevo.")
else:
    with open(archivo, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for dia in dias_faltantes:
            generar_datos_dia(dia, writer)
        print(f"✅ Datos generados para {len(dias_faltantes)} día(s):")
        print("   " + ", ".join([d.strftime("%Y-%m-%d") for d in dias_faltantes]))

print("✅ Archivo actualizado correctamente con datos sintéticos.")
