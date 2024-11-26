from flask import Flask, jsonify
import socket

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

@app.route('/numeros', methods = ['GET'])
def serveNumeros():
    trigger = f'\x02trigger\x03'  # Trigger com STX e ETX
    numeros = enviaSolicitacao(trigger)

    if numeros:
        print("Números recebidos:", numeros)    
        return jsonify({'numeros': [numeros]}), 200

    else:
        return jsonify({'error': 'nao foi possivel obter os numeros'}), 500

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0', port = 5000)