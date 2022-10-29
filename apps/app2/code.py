from apps.base_app import AppBase

class App(AppBase):
    def icon(self):
        return 135 # gamepad
    def name(self) -> str:
        return "My2ndApp"
    def run(self, arg):
        print(f"Hi {arg}. Welcome to {self.name()}")
