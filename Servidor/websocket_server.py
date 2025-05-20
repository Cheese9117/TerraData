import asyncio
import websockets
import json

# Variable global para almacenar los últimos datos recibidos del ESP32
latest_esp32_data = {"humedad": "Cargando...", "valor_analogico": "Cargando..."}
connected_clients = set()

async def send_latest_data(websocket):
    """Envía los últimos datos del ESP32 a un cliente WebSocket."""
    try:
        await websocket.send(json.dumps(latest_esp32_data))
    except websockets.exceptions.ConnectionClosedError:
        pass
    except Exception as e:
        print(f"Error al enviar datos al cliente: {e}")

async def handler(websocket):  # <-- solo un argumento
    """
    Maneja las conexiones WebSocket entrantes y procesa los datos del ESP32.
    """
    print(f"Cliente conectado: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Mensaje recibido: {message}")
            try:
                data = json.loads(message)
                # Si el mensaje es una petición de datos desde la web
                if data.get("request") == "latest_data":
                    await send_latest_data(websocket)
                    continue

                humedad_porcentaje = data.get("humedad")
                valor_analogico = data.get("valor_analogico")

                if humedad_porcentaje is not None and valor_analogico is not None:
                    global latest_esp32_data
                    latest_esp32_data["humedad"] = humedad_porcentaje
                    latest_esp32_data["valor_analogico"] = valor_analogico
                    print(f"Humedad recibida: {humedad_porcentaje}%")
                    print(f"Valor analógico recibido: {valor_analogico}")
                    await asyncio.gather(*[send_latest_data(client) for client in connected_clients])
                else:
                    print("Formato de datos JSON desconocido o incompleto.")
            except json.JSONDecodeError:
                print("Error al decodificar JSON.")

    except websockets.exceptions.ConnectionClosedError:
        print(f"Cliente desconectado inesperadamente: {websocket.remote_address}")
    except websockets.exceptions.ConnectionClosedOK:
        print(f"Cliente desconectado correctamente: {websocket.remote_address}")
    finally:
        connected_clients.discard(websocket)
        print(f"Conexión con {websocket.remote_address} cerrada.")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Servidor WebSocket iniciado en ws://0.0.0.0:8765 (esperando conexiones)")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())