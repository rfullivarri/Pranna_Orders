from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import io

#df_app = pd.read_csv('df_app.csv')

def etiquetas(df_app):
    font = ImageFont.truetype("Fonts/coolvetica condensed rg.otf", 50)
    font1 = ImageFont.truetype("Fonts/Gobold Light.otf", 30)
    color = (0, 0, 0)
    x,y = 270,265
    x1,y1 = x,(y+100)

    x2,y2 = (x+120),530
    x3,y3 = (x+120),600
    x4,y4 = (x+120),670

    x5,y5 = (x+550),530
    x6,y6 = (x+550),600
    x7,y7 = (x+550),670

    etiquetas_images = []

    for i in range(len(df_app)):
        image = Image.open('image/pranna_e_bw4.png') 
        draw = ImageDraw.Draw(image)

        nombre = df_app['Nombre'].iloc[i]
        direccion = df_app['Dirección1'].iloc[i] +" "+ str(df_app['Dirección2'].iloc[i])
        alubias = df_app['Alubias'].iloc[i]
        espinaca = df_app['Espinaca'].iloc[i]
        garbanzos = df_app['Garbanzos'].iloc[i]
        sueca = df_app['Sueca'].iloc[i]
        lentejas = df_app['Lentejas'].iloc[i]
        setas = df_app['Setas'].iloc[i]

        # Superpone el texto en la imagen
        texto1 = f"{nombre}"
        texto2 = f"{direccion}"

        texto3 = f"{lentejas}"
        texto4 = f"{garbanzos}"
        texto5 = f"{setas}"

        texto6 = f"{espinaca}"
        texto7 = f"{alubias}"
        texto8 = f"{sueca}"


        draw.text((x, y), texto1, fill=color, font=font)
        draw.text((x1, y1), texto2, fill=color, font=font)

        draw.text((x2, y2), texto3, fill=color, font=font1)
        draw.text((x3, y3), texto4, fill=color, font=font1)
        draw.text((x4, y4), texto5, fill=color, font=font1)

        draw.text((x5, y5), texto6, fill=color, font=font1)
        draw.text((x6, y6), texto7, fill=color, font=font1)
        draw.text((x7, y7), texto8, fill=color, font=font1)

        img_buffer = io.BytesIO()
        image.save(img_buffer, format="PNG")
        img_bytes = img_buffer.getvalue()
        etiquetas_images.append(img_bytes)
    
    return etiquetas_images
    
        # # Guarda la imagen con el texto superpuesto
        # image.save(f'Etiquetas/Pedido de: {nombre}.png')
        # # Cierra la imagen

    #image.close()
