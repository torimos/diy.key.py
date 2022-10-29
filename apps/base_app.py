from os import listdir,stat

class AppBase(object):
    def icon(self): pass
    def name(self) -> str: pass
    def run(self, arg): pass

class AppsBuilder(object):
  @staticmethod
  def load():
    apps = []
    path = "apps"
    for name in listdir(path):
        stats = stat(path + "/" + name)
        if stats[0] & 0x4000 and name != "shared":
            
            module = __import__("apps." + name + ".code")
            apps.append(getattr(getattr(module,name),"code").App())
    return apps
