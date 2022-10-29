from apps.base_app import AppBase

class App(AppBase):
    def icon(self):
        return 154 # key
    def name(self) -> str:
        return "Passwords\nManager"
    def run(self, arg):
        print(f"Hi {arg}. Welcome to {self.name()}")
