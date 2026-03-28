import os
import sys
from flask import Flask, request, jsonify
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS PARA LA NUBE ---
# Esto asegura que PythonAnywhere encuentre tus llaves sin importar el directorio de trabajo
base_path = os.path.dirname(os.path.abspath(__file__))
ruta_json = os.path.join(base_path, 'credenciales.json')

# --- TUS LLAVES DE META ---
TOKEN_META = "EAAWu7PFUUc0BRJZBkT7LEGkZChgaWZA3ZBiaoVOvOelZBepMPfhE4q2XZAMAZAMVwEY294wt8jjaEZA0MHl9arWnYoGLz9QuaRHZAAuL3b5MZBI7I2oZBkMm4CvDDjixyf2ZBruphNBbHrbQKdPKEckZCJWIvx2dKbT8zEyNH5B6sx7P1vrFXM07pZA7yBeMUq5RSH2c5lIxtYgun7YTxeUazZAfvYWrdXMYJJet6ZBW3jIPn9w8LgSQZC44m1nG3BtBbLRiU4F5YUb9LjZBZB7QVQGC02ZCVgZDZD"
PHONE_NUMBER_ID = "986362287897636"
VERIFY_TOKEN = "horse_in_motion_2026"

# --- CONFIGURACIÓN GOOGLE SHEETS ---
def conectar_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(ruta_json, scope)
        cliente_sheets = gspread.authorize(creds)
        # El nombre debe coincidir con tu archivo en Drive
        return cliente_sheets.open("Leads_HorseInMotion").sheet1
    except Exception as e:
        print(f"⚠️ Error conectando a Sheets: {e}")
        return None

hoja_leads = conectar_sheets()

# --- MEMORIA DEL BOT ---
mensajes_procesados = set()
estado_usuarios = {}
datos_clientes = {}

def enviar_mensaje(numero_destino, texto):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN_META}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto}
    }
    try:
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

@app.route('/webhook', methods=['GET'])
def verificar_webhook():
    hub_mode = request.args.get('hub.mode')
    hub_verify_token = request.args.get('hub.verify_token')
    hub_challenge = request.args.get('hub.challenge')
    
    if hub_mode == 'subscribe' and hub_verify_token == VERIFY_TOKEN:
        return hub_challenge, 200
    return "Error de verificación", 403

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    global hoja_leads
    try:
        data = request.get_json()
        if 'entry' in data and 'changes' in data['entry'][0]:
            cambios = data['entry'][0]['changes'][0]['value']
            if 'messages' in cambios:
                mensaje_info = cambios['messages'][0]
                numero_cliente = mensaje_info['from']
                texto_recibido = mensaje_info['text']['body']
                mensaje_id = mensaje_info['id']
                
                # Filtro anti-spam
                if mensaje_id in mensajes_procesados:
                    return jsonify({"status": "success"}), 200
                mensajes_procesados.add(mensaje_id)
                
                # --- MÁQUINA DE ESTADOS ---
                if numero_cliente not in estado_usuarios:
                    enviar_mensaje(numero_cliente, "¡Hola! Soy el asistente virtual de Horse in Motion 🎬. Antes de agendar, queremos asegurar que estamos en la misma sintonía. Para empezar, ¿con quién tengo el gusto de hablar?")
                    estado_usuarios[numero_cliente] = "PASO_1"
                    datos_clientes[numero_cliente] = {} 
                
                elif estado_usuarios[numero_cliente] == "PASO_1":
                    datos_clientes[numero_cliente]["nombre"] = texto_recibido 
                    enviar_mensaje(numero_cliente, f"¡Mucho gusto, {texto_recibido}! ¿Sentís que la comunicación audiovisual actual de tu marca se percibe genérica, perdiendo conexión con el consumidor tico?\nA) Sí, nos falta ese 'sabor' local.\nB) No, ya tenemos una identidad local fuerte.")
                    estado_usuarios[numero_cliente] = "PASO_2"
                    
                elif estado_usuarios[numero_cliente] == "PASO_2":
                    datos_clientes[numero_cliente]["identidad"] = texto_recibido
                    enviar_mensaje(numero_cliente, "¿Cuentan actualmente con un Mapa de Identidad Verbal o su contenido se basa principalmente en estética visual?")
                    estado_usuarios[numero_cliente] = "PASO_3"

                elif estado_usuarios[numero_cliente] == "PASO_3":
                    datos_clientes[numero_cliente]["norte"] = texto_recibido
                    enviar_mensaje(numero_cliente, "¿Cuál es el objetivo principal de este proyecto?\n1. Diferenciarnos en la góndola / Punto de venta.\n2. Posicionamiento corporativo / Institucional.\n3. Contenido 'lifestyle' para redes sociales.")
                    estado_usuarios[numero_cliente] = "PASO_4"

                elif estado_usuarios[numero_cliente] == "PASO_4":
                    datos_clientes[numero_cliente]["objetivo"] = texto_recibido
                    enviar_mensaje(numero_cliente, "¿A quién estamos tratando de conquistar específicamente? (Ej: Sector HORECA, gerentes, público general, etc.)")
                    estado_usuarios[numero_cliente] = "PASO_5"

                elif estado_usuarios[numero_cliente] == "PASO_5":
                    datos_clientes[numero_cliente]["publico"] = texto_recibido
                    enviar_mensaje(numero_cliente, "¿En qué canales planean distribuir este contenido? (Ej: TV, Redes Sociales, Pauta Digital, etc.)")
                    estado_usuarios[numero_cliente] = "PASO_6"

                elif estado_usuarios[numero_cliente] == "PASO_6":
                    datos_clientes[numero_cliente]["alcance"] = texto_recibido
                    enviar_mensaje(numero_cliente, "Del 1 al 5, ¿qué tan importante es para la marca que el contenido refleje códigos socioculturales de Costa Rica?")
                    estado_usuarios[numero_cliente] = "PASO_7"

                elif estado_usuarios[numero_cliente] == "PASO_7":
                    datos_clientes[numero_cliente]["relevancia"] = texto_recibido
                    enviar_mensaje(numero_cliente, "¿Están buscando una productora para un video único (one-off) o un aliado estratégico para unificar el discurso a largo plazo?")
                    estado_usuarios[numero_cliente] = "PASO_8"

                elif estado_usuarios[numero_cliente] == "PASO_8":
                    datos_clientes[numero_cliente]["calidad"] = texto_recibido
                    enviar_mensaje(numero_cliente, "¿Para cuándo necesitan tener este material 'al aire' o listo para distribución?")
                    estado_usuarios[numero_cliente] = "PASO_9"

                elif estado_usuarios[numero_cliente] == "PASO_9":
                    datos_clientes[numero_cliente]["tiempo"] = texto_recibido
                    enviar_mensaje(numero_cliente, "Última pregunta: Para asegurar la calidad estratégica que ofrecemos, ¿el presupuesto estimado para este proyecto supera los $3000? (Respondé Sí o No)")
                    estado_usuarios[numero_cliente] = "PASO_10"

                elif estado_usuarios[numero_cliente] == "PASO_10":
                    respuesta_presupuesto = texto_recibido.strip().lower()
                    datos_clientes[numero_cliente]["presupuesto"] = respuesta_presupuesto
                    nombre_cliente = datos_clientes[numero_cliente].get("nombre", "Cliente")

                    # Intentar reconectar si la sesión de Sheets expiró
                    if hoja_leads is None: hoja_leads = conectar_sheets()

                    fila = [
                        nombre_cliente,
                        datos_clientes[numero_cliente].get("identidad", ""),
                        datos_clientes[numero_cliente].get("norte", ""),
                        datos_clientes[numero_cliente].get("objetivo", ""),
                        datos_clientes[numero_cliente].get("publico", ""),
                        datos_clientes[numero_cliente].get("alcance", ""),
                        datos_clientes[numero_cliente].get("relevancia", ""),
                        datos_clientes[numero_cliente].get("calidad", ""),
                        datos_clientes[numero_cliente].get("tiempo", ""),
                        respuesta_presupuesto
                    ]
                    
                    try:
                        hoja_leads.append_row(fila)
                    except Exception as e:
                        print(f"❌ Error guardando en Sheets: {e}")

                    # Bifurcación Lógica
                    if respuesta_presupuesto in ["si", "sí", "yes"]:
                        link_gcal = "https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ1IouPLHXfmYTq0ioduLAkFT8T49Da_aCeGhbE7SIYHEM2xlvHalQqFLUgxAkge15UACjCNYBCx"
                        enviar_mensaje(numero_cliente, f"¡Parece que hablamos el mismo idioma, {nombre_cliente}! 🚀 Aquí tenés el acceso al calendario de Luis Diego para agendar nuestra sesión de diagnóstico: {link_gcal}")
                    else:
                        enviar_mensaje(numero_cliente, f"¡Gracias, {nombre_cliente}! Por tus respuestas, vemos que tu marca está en una etapa diferente. Te invitamos a conocer más en nuestra web: https://horse-inmotion.com")

                    del estado_usuarios[numero_cliente]
                    del datos_clientes[numero_cliente]

        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"Error interno del servidor: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    # Esto solo corre si lo ejecutas localmente. PythonAnywhere usa el archivo WSGI.
    app.run(port=5000)