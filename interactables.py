import arcade

class Interactable(arcade.Sprite):
    def __init__(self, name) -> None:
        self.name = name

    def interact(self):
        print(f"You just interacted with {self.name}")

