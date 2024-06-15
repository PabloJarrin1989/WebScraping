import requests
from bs4 import BeautifulSoup
import pandas as pd
from telegram import Bot
import asyncio

# URL de la página de Mercado Libre
url = "https://listado.mercadolibre.com.ec/celulares#D[A:celulares]"

# Realizar la solicitud GET
response = requests.get(url)

# Crear un objeto BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Encontrar los listados de productos
products = soup.find_all('li', class_='ui-search-layout__item')

# Listas para almacenar la información
names = []
prices = []
shippings = []
stars = []
colors = []

# Extraer la información de cada producto
for product in products:
    name = product.find('h2', class_='ui-search-item__title').text
    price = product.find('span', class_='andes-money-amount__fraction').text
    shipping_info = product.find('p', class_='ui-search-item__shipping ui-search-item__shipping--free')
    shipping = shipping_info.text if shipping_info else 'No free shipping'
    star_info = product.find('div', class_='ui-search-reviews__ratings')
    star = star_info.text.strip() if star_info else 'No ratings'
    color_info = product.find('span', class_='ui-search-item__color')
    color = color_info.text if color_info else 'No color info'

    # Añadir la información a las listas
    names.append(name)
    prices.append(price)
    shippings.append(shipping)
    stars.append(star)
    colors.append(color)

# Crear un DataFrame
df = pd.DataFrame({
    'Name': names,
    'Price': prices,
    'Shipping': shippings,
    'Stars': stars,
    'Colors': colors
})

# Convertir el DataFrame a un string
df_string = df.to_string()

# Tu token de acceso del bot de Telegram
TELEGRAM_TOKEN = '7308086074:AAHxIWSRAZH26L29ZKFygxNfZJGx66z9dt4'

# Obtener el CHAT ID
url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
response = requests.get(url)
data = response.json()

if 'result' in data and len(data['result']) > 0:
    chat_id = data['result'][0]['message']['chat']['id']
    print(f"Usando CHAT ID: {chat_id}")

    # Crear un bot
    bot = Bot(token=TELEGRAM_TOKEN)

    # Función para dividir el mensaje en partes más pequeñas
    def split_message(message, max_length=4096):
        parts = []
        while len(message) > max_length:
            split_at = message.rfind('\n', 0, max_length)
            if split_at == -1:
                split_at = max_length
            parts.append(message[:split_at])
            message = message[split_at:]
        parts.append(message)
        return parts

    # Dividir el DataFrame en varias partes si es necesario
    messages = split_message(df_string)

    async def send_messages():
        for message in messages:
            await bot.send_message(chat_id=chat_id, text=message)
            await asyncio.sleep(1)  # Esperar un segundo entre mensajes para evitar límites de tasa

    # Ejecutar la función asíncrona
    asyncio.run(send_messages())
else:
    print("No se encontraron actualizaciones. Asegúrate de haber enviado un mensaje al bot.")