from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Verificar que la solicitud tenga el encabezado 'Content-Type' correcto
        if request.headers['Content-Type'] == 'application/json':
            data = request.json  # Obtener los datos del pedido en formato JSON
            # Procesar los datos del pedido según tus necesidades
            # Puedes imprimirlos para verificar que se están recibiendo correctamente
            print(data)
            # Realizar aquí las acciones necesarias con los datos del pedido

            return jsonify({'message': 'Solicitud recibida correctamente'}), 200
        else:
            return jsonify({'error': 'Solicitud incorrecta'}), 400
    else:
        return jsonify({'error': 'Método no permitido'}), 405

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")
