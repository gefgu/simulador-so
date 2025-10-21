from time import sleep
import customtkinter

from config_handler import get_config_values
from gantt_diagram import GanttDiagram

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1920x1080")

        self.title("Simulador SO")

        self.gantt_diagram = None

    
    def create_gantt_diagram(self, current_time, tarefas):
        # Se criar um novo, tira o antigo
        if self.gantt_diagram:
            self.gantt_diagram.destroy()

        self.gantt_diagram = GanttDiagram(self, current_time, tarefas)
        self.gantt_diagram.pack(fill="both", expand=True)

    def redraw(self):
        if self.gantt_diagram:
            self.gantt_diagram.draw_grid()

if __name__ == "__main__":
    config = get_config_values("config.txt")

    print(config)

    app = App()
    app.create_gantt_diagram(current_time=11, tarefas=config["tarefas"])
    
    app.mainloop()