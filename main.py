import customtkinter

from config_handler import get_config_values
from gantt_diagram import GanttDiagram

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1920x1080")

        self.title("Simulador SO")

        self.gantt_diagram = None

    
    def create_gantt_diagram(self, n_processes, max_time):
        self.gantt_diagram = GanttDiagram(self, n_processes, max_time)
        self.gantt_diagram.pack(fill="both", expand=True)

if __name__ == "__main__":
    config = get_config_values("config.txt")

    print(config)

    app = App()
    app.create_gantt_diagram(n_processes=len(config["tarefas"]), max_time=15)
    app.mainloop()