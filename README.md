# 🎬 Bot de WhatsApp - Horse in Motion (Lead Scoring)

Este repositorio contiene el código fuente del proyecto de investigación para el curso de **Programación II** de la **Universidad Internacional de las Américas (UIA)**.

## 👥 Equipo de Desarrollo
* Carlos Guevara Enciso
* Naigel Graham Obando
* Ariela Molina Rojas
* Fernanda Durán Camacho

## 🚀 Descripción del Proyecto
Implementación de un asistente virtual (Chatbot) en WhatsApp utilizando la **WhatsApp Cloud API (Meta)** y **Python (Flask)**. 

El bot actúa como el primer filtro comercial para la productora audiovisual *Horse in Motion*, interactuando con los clientes mediante un flujo de "Lead Scoring" de 10 preguntas. Evalúa el presupuesto y necesidades del cliente, y posteriormente inyecta los datos de forma estructurada en **Google Sheets**. Si el prospecto es calificado, el sistema genera un enlace automatizado de **Google Calendar** para agendar una reunión diagnóstica.

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.10+
* **Framework Web:** Flask
* **APIs:** Meta Graph API (WhatsApp), Google Sheets API, Google Drive API.
* **Despliegue/Túnel:** Ngrok / PythonAnywhere

## ⚠️ Nota de Seguridad
Por motivos de seguridad, los archivos de credenciales (`credenciales.json`) y los Tokens de acceso de Meta han sido omitidos de este repositorio. Para ejecutar el código localmente, es necesario proveer sus propias llaves en la cabecera del archivo `HorseInMotion_Bot.py`.