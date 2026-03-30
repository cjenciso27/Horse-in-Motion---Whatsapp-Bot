import os
import sys
from flask import Flask, request, jsonify
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS (PARA RENDER Y LOCAL) ---
# Render guarda los Secret Files en /etc/secrets/
ruta_render = '/etc/secrets/credenciales.json'
ruta_local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credenciales.json')

# Si existe la ruta de Render, la usamos; si no, buscamos el archivo local
if os.path.exists(ruta_render):
    ruta_json = ruta_render
    print("🚀 Entorno: Render (Secret Files)")
else:
    ruta_json = ruta_local
    print("🏠 Entorno: Local / Desarrollo")

# --- TUS LLAVES DE META ---
TOKEN_META = "EAAWu7PFUUc0BRP9yDa4ZAxf0Ey7E5M4KBCoLSdNDVJhlhjZCjrBKvNvhRO3ZABwiNicJgd4oBXcKQ5vZCKvtOvYq9JU3qnIbAoA2uqD2qKxEt8WUp8cZB0exjvmkiO98TAvT0nTQFsxGBubBF0PqgjR8j9YZAGI5qVogJD5ATIk3cnt0egPuwgDgnbnZAGfHQVaSOrhyVhhlZCgl96b3jmsgRNKGcbkSY12QcIWW5UmnX9rZBWk5SNkjxu4k6IMKwGbowmGK1FkcsZBtJoRmnlDgZDZD"
PHONE_NUMBER_ID = "986362287897636"
VERIFY_TOKEN = "horse_in_motion_2026"

# --- CONFIGURACIÓN GOOGLE SHEETS ---
def conectar_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(ruta_json, scope)
        cliente_sheets = gspread.authorize(creds)
        # Asegurate de que el nombre de la hoja sea exacto
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
        response = requests.post(url, headers=headers, json=data)
        # ESTO ES CLAVE: Ver qué responde Meta
        print(f"DEBUG META: Status {response.status_code} - Resposta: {response.text}")
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

@app.route('/webhook', methods=['GET'])
def verificar_webhook():
    hub_mode = request.args.get('hub.mode')
    hub_verify_token = request.args.get('hub.verify_token')
    hub_challenge = request.args.get('hub.challenge')
    
    if hub_mode == 'subscribe' and hub_verify_token == VERIFY_TOKEN:
        return hub_challenge, 200
    return "Error de Verificación", 403

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
                
                # --- MÁQUINA DE ESTADOS (Lead Scoring) ---
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
                    enviar_mensaje(numero_cliente, "¿Cuál es el objetivo principal de este proyecto?\n1. Diferenciarnos en la góndola.\n2. Posicionamiento corporativo.\n3. Contenido 'lifestyle' para redes sociales.")
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
                    enviar_mensaje(numero_cliente, "¿Están buscando una productora para un video único o un aliado estratégico?")
                    estado_usuarios[numero_cliente] = "PASO_8"

                elif estado_usuarios[numero_cliente] == "PASO_8":
                    datos_clientes[numero_cliente]["calidad"] = texto_recibido
                    enviar_mensaje(numero_cliente, "¿Para cuándo necesitan tener este material listo?")
                    estado_usuarios[numero_cliente] = "PASO_9"

                elif estado_usuarios[numero_cliente] == "PASO_9":
                    datos_clientes[numero_cliente]["tiempo"] = texto_recibido
                    enviar_mensaje(numero_cliente, "Última pregunta: ¿el presupuesto estimado para este proyecto supera los $3000? (Respondé Sí o No)")
                    estado_usuarios[numero_cliente] = "PASO_10"

                elif estado_usuarios[numero_cliente] == "PASO_10":
                    resp_p = texto_recibido.strip().lower()
                    datos_clientes[numero_cliente]["presupuesto"] = resp_p
                    nombre_cliente = datos_clientes[numero_cliente].get("nombre", "Cliente")

                    # Reconexión automática si falla
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
                        resp_p
                    ]
                    
                    try:
                        hoja_leads.append_row(fila)
                        print("✅ Lead guardado exitosamente.")
                    except Exception as e:
                        print(f"❌ Error en Sheets: {e}")

                    if resp_p in ["si", "sí", "yes"]:
                        link_gcal = "https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ1IouPLHXfmYTq0ioduLAkFT8T49Da_aCeGhbE7SIYHEM2xlvHalQqFLUgxAkge15UACjCNYBCx"
                        enviar_mensaje(numero_cliente, f"¡Hablamos el mismo idioma, {nombre_cliente}! 🚀 Agendá tu sesión aquí: {link_gcal}")
                    else:
                        enviar_mensaje(numero_cliente, f"¡Gracias, {nombre_cliente}! Te invitamos a conocer más en nuestra web: https://horse-inmotion.com")

                    del estado_usuarios[numero_cliente]
                    del datos_clientes[numero_cliente]

        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error interno: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    # Puerto dinámico para Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
