"""Abstract Gui Module - serves as interface reference"""
import sys

class UserGui:
    def __init__(self):
        if self.__class__ == UserGui:
            raise "class UserGui is abstract!"
    def set_model(self, model): self.model = model


class RoomGui:
    def __init___(self):
        if self.__class__ == RoomGui:
            raise "class RoomGui is abstract!"
    def set_model(self, model): self.model = model
    

class MainGui:
    def __init__(self, argv):
        if self.__class__ == MainGui:
            raise "class MainGui is abstract!"
        self.center = None
    def run(self):
        pass
    def quit(self):
        self.center.quit()
        sys.exit(0)
    def connect(self):
        pass
