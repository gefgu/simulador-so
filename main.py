from time import sleep
import customtkinter
from collections import deque

from config_handler import get_config_values
from gantt_diagram import GanttDiagram
from sistema_operacional import SistemaOperacional

# Desacoplar a lógica do algoritmo da interface gráfica

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1920x1080")

        self.title("Simulador SO")

        self.gantt_diagram = None

        # Create main menu frame
        self.menu_frame = customtkinter.CTkFrame(self)
        self.menu_frame.pack(fill="both", expand=True)
        
        # Title
        self.title_label = customtkinter.CTkLabel(
            self.menu_frame,
            text="Simulador de SO",
            font=("Arial", 48, "bold")
        )
        self.title_label.pack(pady=(200, 50))
        
        # Start button
        self.start_button = customtkinter.CTkButton(
            self.menu_frame,
            text="Iniciar",
            font=("Arial", 24),
            width=200,
            height=60,
            command=self.iniciar_simulacao
        )
        self.start_button.pack(pady=20)

    def iniciar_simulacao(self):
        # Remover o menu
        self.menu_frame.destroy()

        # Iniciar a simulação
        config_file = "config.txt"  # Nome do arquivo de configuração
        self.sistema_operacional = SistemaOperacional(config_file)

        for i in range(100):
            self.sistema_operacional.executar_tick()
            current_time = self.sistema_operacional.get_relogio()
            tarefas = self.sistema_operacional.get_tarefas_ingressadas()
            self.create_gantt_diagram(current_time+1, tarefas)
            self.update()
            sleep(1)  # Pausa para visualizar a simulação

    
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
    app = App()
    app.mainloop()
    