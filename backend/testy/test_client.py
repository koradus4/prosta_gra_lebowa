import websocket

def on_message(ws, message):
    print(f"Otrzymano wiadomość: {message}")

def on_error(ws, error):
    print(f"Wystąpił błąd: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Połączenie zamknięte")

def on_open(ws):
    print("Połączenie otwarte")
    ws.send("Testowa wiadomość")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "ws://127.0.0.1:5000/game",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()
