import socket
import pyautogui
import io
import sys

pyautogui.FAILSAFE = False

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 69))
server_socket.listen(1)

print("server running!")
message_format = "{cmd};{options};{data}"


def form(cmd, msg_data, options=""):
    return message_format.format(cmd=cmd, options=options, data=msg_data)


def main():
    close = False
    while not close:
        client_socket, client_address = server_socket.accept()
        try:
            print("client connected", client_address)
            while True:
                got = client_socket.recv(1024).decode('utf-8')
                cmd, options, data = got.split(";")
                if got.count(";") != 2:
                    client_socket.send(form("error_code", "invalid use").encode('utf-8'))
                    continue
                if cmd == "echo":
                    client_socket.send(form("echo_message", data).encode('utf-8'))
                elif cmd == "quit":
                    client_socket.send(form("quit", "").encode('utf-8'))
                    break
                elif cmd == "mouse":
                    if options == "":
                        continue
                    if "click" in options:
                        if data != "":
                            x, y = data.split(", ")
                            pyautogui.click(int(x), int(y))
                        else:
                            pyautogui.click()
                        client_socket.send(form("notification", "clicked!").encode('utf-8'))
                    elif "move" in options:
                        x, y = data.split(", ")
                        pyautogui.moveTo(int(x), int(y))
                        client_socket.send(form("notification", f"moved mouse to ({x}, {y})").encode('utf-8'))
                    elif "scroll" in options:
                        amount = int(data)
                        pyautogui.scroll(amount)
                        client_socket.send(form("notification", f"scrolled by {amount}").encode('utf-8'))
                elif cmd == "screen":
                    screen = pyautogui.screenshot()
                    img_byte_arr = io.BytesIO()
                    screen.save(img_byte_arr, format="jpeg")
                    client_socket.send(form("screenshot", str(sys.getsizeof(img_byte_arr)),
                                            f"{screen.size[0]}, {screen.size[1]}").encode('utf-8'))
                    client_socket.send(img_byte_arr.getvalue())
                    client_socket.send(b"image done transferring")
                elif cmd == "gss":
                    screen = pyautogui.screenshot()
                    client_socket.send(form("screenshot", f"{screen.size[0]}, {screen.size[1]}").encode('utf-8'))
                elif cmd == "system":
                    if "shut down" in options:
                        client_socket.send(form("quit", data).encode('utf-8'))
                        close = True
                        break
                else:
                    client_socket.send("error_code", "command not recognized")
        except (ConnectionAbortedError, ConnectionResetError, ConnectionError, ConnectionRefusedError):
            pass
        client_socket.close()
        print(client_address, "has disconnected")
    server_socket.close()
    print("server closing")


if __name__ == "__main__":
    main()
