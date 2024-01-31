import kivy
kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooser
from kivy.uix.widget import Widget
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.clock import Clock
import os


class King(Widget):
    b_done = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(King, self).__init__(**kwargs)

    def file_check(self, dt):
        self.b_done.search_benchmarks()


class BenchmarksDone(Widget):
    def __init__(self, **kwargs):
        super(BenchmarksDone, self).__init__(**kwargs)
        self.layout = StackLayout()
        self.benchs = []

    def search_benchmarks(self):
        print('WORKS')
        self.layout.clear_widgets()
        self.benchs = os.listdir("benchmarks/")
        for index, bench in enumerate(self.benchs):
            pass
            btn = Button(text=bench, width=40, size_hint=(None, 0.15))
            self.layout.add_widget(btn)


class portableBenchmarkApp(App):
    def build(self):
        app = King()
        Clock.schedule_interval(app.file_check, 3.0)
        return app


if __name__ == '__main__':
    portableBenchmarkApp().run()







