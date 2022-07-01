import arcade

class Interactable(arcade.Sprite):
    def __init__(self, **kwargs):
        self.show_text = False
        super().__init__(**kwargs)

    def interact(self):
        getattr(self, self.properties["oninteract"], self.not_implimented)()

    def body(self):
        print("ewww you touched a ded dude")

    def not_implimented(self):
        raise NotImplemented("object does not have oninteract in Tiled, check if spelled correctly.")

    def draw_text(self):
        self.show_text = True
        print('d')

        



    