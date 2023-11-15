from flask import Flask, request, jsonify
import threading
import ssl


#-----------------------------------------------------------------------------------------------------------------------------------
#SERVER WEBHOOK
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':
            data = request.json
            # Procesar los datos del pedido según tus necesidades
            print(data)
            # Realizar aquí las acciones necesarias con los datos del pedido
            return jsonify({'message': 'Solicitud recibida correctamente'}), 200
        else:
            return jsonify({'error': 'Solicitud incorrecta'}), 400
    else:
        return jsonify({'error': 'Método no permitido'}), 405

if __name__ == '__main__':
    # Antes de iniciar Flask, verifica si estás en el hilo principal
    if threading.current_thread() == threading.main_thread():
        app.run(debug=True, port=8501, host="0.0.0.0", ssl_context="adhoc")
    else:
        print("No puedes ejecutar la aplicación Flask en un subproceso secundario.")
