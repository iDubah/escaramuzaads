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
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                contenido = f.read().strip()
                if not contenido:
                    return []
                return json.loads(contenido)
        except (json.JSONDecodeError, ValueError):
            print("⚠️ Archivo JSON dañado o vacío. Se reiniciará.")
            return []
    return []


def guardar_actividades(actividades):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(actividades, f, ensure_ascii=False, indent=2)


def enviar_correo(nuevas):
    api_key = os.getenv("BREVO_API_KEY")
    if not api_key:
        print("⚠️ No se configuró BREVO_API_KEY. No se enviará correo.")
        return

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    data = {
        "sender": {"name": "Escaramuza Bot", "email": "escaramuzascrap@gmail.com"},
        "to": [{"email": "santimar200404@gmail.com"}],
        "subject": "🆕 Nuevas actividades en Escaramuza",
        "textContent": "Se han publicado nuevas actividades:\n\n" + "\n".join(nuevas)
                       + "\n\n👉 https://escaramuza.com.uy/agenda/actividades-en-escaramuza"
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("📧 Correo enviado con éxito vía Brevo.")
    else:
        print(f"❌ Error al enviar correo: {response.text}")

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
