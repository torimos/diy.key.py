from apps.base_app import AppBase

class App(AppBase):
    def icon(self):
        return 75 #android
    def name(self) -> str:
        return "My3rdApp"
    def run(self, arg):
        print(f"Hi {arg}. Welcome to {self.name()}")
