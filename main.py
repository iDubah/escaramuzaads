import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from flask import Flask

URL = "https://escaramuza.com.uy/agenda/actividades-en-escaramuza"
ARCHIVO_DATOS = "actividades.json"

# 🔧 Configura tu correo
EMAIL_EMISOR = "escaramuzascrap@gmail.com"
EMAIL_RECEPTOR = "santimar200404@gmail.com"  # puede ser el mismo
CONTRASENA = os.getenv(
    "EMAIL_PASSWORD")  # usa una variable de entorno en Replit

app = Flask(__name__)


def obtener_actividades():
    try:
        r = requests.get(URL, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        actividades = [
            a.get_text(strip=True)
            for a in soup.select("h2, h3, .event-title, .activity-title")
        ]

        if not actividades:
            print(
                "⚠️  No se encontraron actividades en la página (los selectores CSS pueden haber cambiado)"
            )

        return list(set(actividades))
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener actividades: {e}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado al procesar actividades: {e}")
        return []


def cargar_previas():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def guardar_actividades(actividades):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(actividades, f, ensure_ascii=False, indent=2)


def enviar_correo(nuevas):
    # (contenido de la función)
    print("Saltando envío de correo por prueba:", nuevas)
    return

def main():
    print("Revisando nuevas actividades...")
    actuales = obtener_actividades()
    if not actuales:
        print("⚠️  No se pudieron obtener actividades.")
        return
    previas = cargar_previas()
    nuevas = [a for a in actuales if a not in previas]
    if nuevas:
        print("¡Nuevas actividades detectadas!", nuevas)
        enviar_correo(nuevas)
        guardar_actividades(actuales)
    else:
        print("Sin novedades.")
        guardar_actividades(actuales)

@app.route("/check")
def check():
    try:
        main()
        return "✅ Revisión completada correctamente."
    except Exception as e:
        return f"❌ Error al ejecutar revisión: {e}"

def revisar_y_enviar():
    actuales = obtener_actividades()
    previas = cargar_previas()
    nuevas = [a for a in actuales if a not in previas]
    if nuevas:
        enviar_correo(nuevas)
        guardar_actividades(actuales)
        return f"✅ Nuevas actividades: {', '.join(nuevas)}"
    else:
        guardar_actividades(actuales)
        return "Sin novedades."


@app.route("/")
def home():
    return "Servidor activo. Usa /check para forzar revisión."



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
