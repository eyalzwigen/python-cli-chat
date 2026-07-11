from pyfiglet import Figlet
from textual.widgets import Label

class Title(Label):
    def __init__(self,text: str, font_size: str = "standard"):
        figlet = Figlet(font=font_size, width=300)
        rendered = figlet.renderText(text)
        super().__init__(rendered, id="title-text", markup=False)