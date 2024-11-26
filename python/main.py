from flask import Flask, jsonify, send_file
import socket
import cv2
import base64
from io import BytesIO

app = Flask(__name__)

ip = '192.168.0.44'
porta = 2123

def enviaSolicitacao(trigger):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)  # Tempo limite para evitar bloqueios infinitos
            try:
                s.connect((ip, porta))
                print('Conectado com sucesso\n')
            except Exception as e:
                print(f'Impossível conectar: {e}\n')
                return None

            try:
                msg = trigger.encode()
                s.sendall(msg)
                print(f'Mensagem enviada: {msg}\n')
            except Exception as e:
                print(f'Erro ao enviar mensagem: {e}\n')
                return None

            try:
                resposta = b""
                while True:
                    try:
                        data = s.recv(1024)  # Recebe dados em blocos de 1024 bytes
                        if not data:
                            break  # Conexão fechada pelo servidor
                        resposta += data
                    except socket.timeout:
                        print("Timeout ao receber dados")
                        break

                print(f"Resposta recebida (bruta): {resposta}")

                # Dividir as mensagens usando o delimitador <ETX>
                mensagens = resposta.split(b'\x03')  # Divide as mensagens pelo <ETX>
                mensagens = [m.strip(b'\x02').decode() for m in mensagens if m.strip()]  # Remove <STX> e converte para string

                print(f"Mensagens decodificadas: {mensagens}")

                # Filtrar a mensagem relevante (ignorando 'OK')
                numeros = [m for m in mensagens if not m.startswith("OK")]
                numeros = "\n".join(numeros)  # Junta todas as partes numéricas, se houver mais de uma

                print(f"Números filtrados: {numeros}")
                return numeros

            except Exception as e:
                print(f'Erro ao processar a resposta: {e}\n')
                return None

    except Exception as e:
        print(f'Erro: {e}\n')
        return None


def captura_imagem_webcam():
    # Inicia a captura de vídeo
    cap = cv2.VideoCapture(0)  # 0 é geralmente a câmera padrão

    if not cap.isOpened():
        print("Erro ao acessar a câmera.")
        return None

    # Captura uma única imagem
    ret, frame = cap.read()
    cap.release()  # Libera a câmera após capturar a imagem

    if not ret:
        print("Falha ao capturar imagem.")
        return None

    # Converte a imagem para o formato PNG e depois para base64
    _, buffer = cv2.imencode('.png', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')  # Codifica a imagem para base64

    return img_base64


@app.route('/', methods=['GET'])
def serveNumeros():
    trigger = f'\x02trigger\x03'  # Trigger com STX e ETX
    numeros = enviaSolicitacao(trigger)

    # Captura a imagem da webcam
    img_base64 = captura_imagem_webcam()

    if numeros and img_base64:
        print("Números recebidos:", numeros)    
        return jsonify({
            'numeros': [numeros],
            'imagem': img_base64  # Imagem em base64
        }), 200
    else:
        return jsonify({'error': 'não foi possível obter os números ou capturar imagem'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
