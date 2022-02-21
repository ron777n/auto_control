import socket
import io
import kivy
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget

message_format = "{cmd};{options};{data}"

form = lambda cmd, msg_data, options="": message_format.format(cmd=cmd, options=options, data=msg_data)


def get_kivy_image_from_bytes(image_bytes, file_extension):
    buf = io.BytesIO(image_bytes)
    cim = CoreImage(buf, ext=file_extension)
    return Image(texture=cim.texture)


my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect(("10.0.0.30", 69))


def echo(msg):
    my_socket.send(("echo;;"+msg).encode())
    return my_socket.recv(1024)


# class Touch(Widget):

ww, wh = Window.size
my_socket.send("gss;;".encode("utf-8"))
server_x, server_y = [int(val) for val in my_socket.recv(1024).decode("utf-8").split(";")[2].split(", ")]


class MainWin(Screen):
    msg = "screen;;"
    put = 0

    def __init__(self):
        super().__init__()
        self.cols = 2

        my_socket.send(self.msg.encode())
        my_socket.recv(1024).decode()
        data = my_socket.recv(16384*16*4)
        self.img = 0
        self.update_screen()

    def update_screen(self):
        try:
            my_socket.send(self.msg.encode())
            my_socket.recv(2048)
            image_chunk = my_socket.recv(2048)
            new_img = image_chunk
            while b"image done transferring" not in image_chunk:
                image_chunk = my_socket.recv(2048)
                new_img += image_chunk
            new_img = new_img[:-len("image done transferring")]
            new_img = get_kivy_image_from_bytes(new_img, "jpeg")
            if self.img:
                self.remove_widget(self.img)
            self.img = new_img
            self.img.allow_stretch = True
            self.img.keep_ratio = False
            self.add_widget(self.img)

        except Exception as e:
            print(type(e))
            print(e)

    def on_touch_down(self, touch):
        tw, th = touch.spos
        x, y = server_x/ww*(ww*tw), server_y/wh*(wh-wh*th)
        if not touch.is_double_tap:
            my_socket.send(form("mouse", f"{int(x)}, {int(y)}", "move").encode())
        else:
            print("egg")
            my_socket.send(form("mouse", f"{int(x)}, {int(y)}", "click").encode())
        my_socket.recv(1024)
        self.put = touch.spos[1]

    def on_touch_move(self, touch):
        change = int(server_y/wh*(wh*(self.put-touch.spos[1])))
        my_socket.send(form("mouse", change, "scroll").encode())
        my_socket.recv(1024)
        self.put = touch.spos[1]

    def on_touch_up(self, touch): self.update_screen()


class communicationApp(App):
    def build(self):
        return MainWin()


def main():
    communicationApp().run()


def command_line():
    # my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # my_socket.connect(("10.0.0.30", 69))  # 127.0.0.1
    cmd = ""
    while True:
        msg = input("Enter your message:\n")
        my_socket.send(msg.encode())
        if msg.startswith("screen"):
            got = my_socket.recv(1024).decode()
            data = my_socket.recv(16384*16*4)
        else:
            got = my_socket.recv(1024).decode()
            if got.count(";") < 2:
                continue
            cmd, options, data = got.split(";")
        print(type(data))
        print(data)
        if cmd == "quit":
            break

    my_socket.close()


if __name__ == '__main__':
    main()

