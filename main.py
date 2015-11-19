__version__ = "1.0"

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

from connection import Connection
from accelerometer import Accelerometer
from accelerometer_delegate import AccelerometerDelegate

class UI(FloatLayout):

    def __init__(self, **kwargs):
        super(UI, self).__init__(**kwargs)
        self.lblAcce = Label(text="")
        self.add_widget(self.lblAcce)

    def update(self, txt):
        self.lblAcce.text = txt

class MainApp(App):

    connection = Connection()
    acc = Accelerometer()
    # another_acc = Accelerometer()

    def on_stop(self):
        self.connection.stop.set()
        self.acc.stop.set()
        # self.another_acc.stop.set()

    def build(self):
        ui = UI()

        # self.another_acc.configure_with(delegate=ui)
        # self.another_acc.start()

        self.connection.configure_with(delegate=ui)
        self.connection.start()

        acc_delegate = AccelerometerDelegate()
        acc_delegate.configure_with(connection=self.connection)

        self.acc.configure_with(delegate=acc_delegate)
        self.acc.start()

        return ui

if __name__ == '__main__':
    MainApp().run()
