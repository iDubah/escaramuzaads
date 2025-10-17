import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

URL = "https://escaramuza.com.uy/agenda/actividades-en-escaramuza"
ARCHIVO_DATOS = "actividades.json"

# 🔧 Configura tu correo
EMAIL_EMISOR = "escaramuzascrap@gmail.com"
EMAIL_RECEPTOR = "santimar200404@gmail.com"  # puede ser el mismo
CONTRASENA = os.getenv("escaramuzasanti!")  # usa una variable de entorno en Replit

def obtener_actividades():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")
    actividades = [a.get_text(strip=True) for a in soup.select("h2, h3, .event-title, .activity-title")]
    return list(set(actividades))

def cargar_previas():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_actividades(actividades):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(actividades, f, ensure_ascii=False, indent=2)

def enviar_correo(nuevas):
    asunto = "🆕 Nuevas actividades en Escaramuza"
    cuerpo = "Se han publicado nuevas actividades:\n\n" + "\n".join(nuevas) + "\n\n👉 " + URL

    msg = MIMEMultipart()
    msg["From"] = EMAIL_EMISOR
    msg["To"] = EMAIL_RECEPTOR
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_EMISOR, CONTRASENA)
        server.send_message(msg)

    print("Correo enviado con éxito.")

def main():
    print("Revisando nuevas actividades...")
    actuales = obtener_actividades()
    previas = cargar_previas()

    nuevas = [a for a in actuales if a not in previas]
    if nuevas:
        print("¡Nuevas actividades detectadas!", nuevas)
        enviar_correo(nuevas)
        guardar_actividades(actuales)
    else:
        print("Sin novedades.")
        guardar_actividades(actuales)

if __name__ == "__main__":
    main()