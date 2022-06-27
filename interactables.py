import arcade

class Interactable(arcade.Sprite):

    def interact(self):
        getattr(self, self.properties["oninteract"], self.not_implimented)()

    def body(self):
        print("ewww you touched a ded dude")

    def not_implimented(self):
        raise NotImplemented("object does not have oninteract in Tiled, check if spelled correctly.")


    