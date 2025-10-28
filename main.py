import csv
import random
import os
from datetime import datetime, timedelta

# ==============================
# CONFIGURACIÓN GENERAL (SIN CAMBIOS)
# ==============================
dias_minimos = 10           
intervalo = 30              # Intervalo en minutos
archivo = "datos_ambientales.csv"

# Rangos de variables simuladas
temp_min, temp_max = 19, 31      # °C
hum_min, hum_max = 80, 95        # %
viento_min, viento_max = 5, 12   # km/h

# Rango horario por día (solo para datos históricos)
hora_inicio = 6   # 06:00 AM
hora_fin = 23     # 23:30 PM

# ==============================
# FUNCIONES AUXILIARES (SIN CAMBIOS)
# ==============================

def leer_fechas_existentes(nombre_archivo):
    """Devuelve un set con las fechas (YYYY-MM-DD) ya presentes en el CSV."""
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
        # Lógica de simulación
        if 6 <= hora <= 12:
            temperatura = random.uniform(temp_min, temp_max - 3)
        elif 12 < hora <= 17:
            temperatura = random.uniform(temp_max - 2, temp_max)
        else:
            temperatura = random.uniform(temp_min, temp_min + 4)

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

def generar_registro_actual(writer):
    """Genera y escribe una sola fila para el momento actual."""
    
    ahora = datetime.now()
    
    # Lógica de simulación simple basada en la hora
    hora = ahora.hour
    if 6 <= hora <= 12:
        temperatura = random.uniform(temp_min, temp_max - 3)
    elif 12 < hora <= 17:
        temperatura = random.uniform(temp_max - 2, temp_max)
    else:
        temperatura = random.uniform(temp_min, temp_min + 4)

    temperatura += random.uniform(-0.5, 0.5)
    humedad = random.uniform(hum_min, hum_max)
    viento = random.uniform(viento_min, viento_max)

    writer.writerow([
        ahora.strftime("%Y-%m-%d"),
        ahora.strftime("%H:%M"), 
        round(temperatura, 1),
        round(humedad, 1),
        round(viento, 1)
    ])
    return 1 


# ==============================
# LÓGICA PRINCIPAL (MODIFICADA PARA OCTUBRE)
# ==============================

# 1. Crear archivo si no existe
archivo_existia = os.path.exists(archivo)

if not archivo_existia:
    with open(archivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fecha", "hora", "temperatura", "humedad", "viento_kmh"])
    print(f"Archivo '{archivo}' creado.")

# 2. Leer días existentes
if archivo_existia:
    fechas_existentes = leer_fechas_existentes(archivo)
else:
    fechas_existentes = set()

# 3. Calcular rango de días (Solo el mes actual, hasta ayer)
hoy = datetime.now().date()
ultimo_dia = hoy - timedelta(days=1) # El final del rango es AYER
primer_dia = hoy.replace(day=1)       # El inicio del rango es el DÍA 1 DEL MES ACTUAL (Octubre)

# 4. Determinar qué días faltan en el rango calculado
dias_faltantes = []
fecha = primer_dia
while fecha <= ultimo_dia:
    if fecha.strftime("%Y-%m-%d") not in fechas_existentes:
        dias_faltantes.append(fecha)
    fecha += timedelta(days=1)

# 5. Generar datos históricos si faltan
if not dias_faltantes:
    print(f"Ya existe historial completo del mes de Octubre (desde {primer_dia} hasta {ultimo_dia}).")
else:
    with open(archivo, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for dia in dias_faltantes:
            generar_datos_dia(dia, writer)
        print(f"Datos históricos generados para {len(dias_faltantes)} día(s), cubriendo el mes de Octubre.")

# 6. Siempre agregar un registro en vivo (para simular el sensor)
with open(archivo, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    generar_registro_actual(writer)
    print(f"Registro en vivo agregado al CSV: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
print("Archivo 'datos_ambientales.csv' actualizado correctamente.")
