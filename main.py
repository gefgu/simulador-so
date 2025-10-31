import customtkinter
from PIL import ImageGrab
from gantt_diagram import GanttDiagram
from sistema_operacional import SistemaOperacional
from datetime import datetime

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1920x1080")

        self.title("Simulador SO")

        self.gantt_diagram = None
        self.sistema_operacional = None

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
        config_file = "config_livro_rr.txt"  # Nome do arquivo de configuração
        self.sistema_operacional = SistemaOperacional(config_file)
        self.sistema_operacional.executar_tick()  # Executa o primeiro tick para iniciar a simulação

        # Create control frame for buttons
        self.control_frame = customtkinter.CTkFrame(self)
        self.control_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        # Create a sub-frame to hold buttons horizontally
        self.buttons_frame = customtkinter.CTkFrame(self.control_frame)
        self.buttons_frame.pack(pady=10)

        # Salvar imagem button
        self.screenshot_button = customtkinter.CTkButton(
            self.buttons_frame,
            text="Salvar imagem",
            font=("Arial", 18),
            width=200,
            height=50,
            command=self.take_screenshot
        )
        self.screenshot_button.pack(side="left", padx=10)

        # Avançar até o fim button
        self.run_to_end_button = customtkinter.CTkButton(
            self.buttons_frame,
            text="Avançar até o fim",
            font=("Arial", 18),
            width=200,
            height=50,
            command=self.avancar_ate_fim
        )
        self.run_to_end_button.pack(side="left", padx=10)


        # Próximo tick button
        self.next_tick_button = customtkinter.CTkButton(
            self.buttons_frame,
            text="Próximo tick",
            font=("Arial", 18),
            width=200,
            height=50,
            command=self.proximo_tick
        )
        self.next_tick_button.pack(side="left", padx=10)

        # Initial diagram
        self.atualizar_diagrama()

    def proximo_tick(self):
        """Execute one tick and update the diagram"""
        self.sistema_operacional.executar_tick()
        self.atualizar_diagrama()

        if (self.sistema_operacional.simulacao_terminada()):
            self.next_tick_button.configure(state="disabled")

    def avancar_ate_fim(self):
        """Run simulation until completion"""
        while not self.sistema_operacional.simulacao_terminada():
            self.sistema_operacional.executar_tick()
        
        self.atualizar_diagrama()
        self.update()
        self.next_tick_button.configure(state="disabled")
        self.run_to_end_button.configure(state="disabled")

    
    # Função para Tirar foto do diagrama de Gantt
    # Fonte: GitHub Copilot
    def take_screenshot(self):
        """Take a screenshot of the Gantt diagram"""
        if self.gantt_diagram and self.gantt_diagram.canvas:
            # Get canvas coordinates
            x = self.gantt_diagram.canvas.winfo_rootx()
            y = self.gantt_diagram.canvas.winfo_rooty()
            width = self.gantt_diagram.canvas.winfo_width()
            height = self.gantt_diagram.canvas.winfo_height()
            
            # Capture the canvas area
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            
            # Generate filename with timestamp
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gantt_diagram_{timestamp}.png"
            
            screenshot.save(filename)
            print(f"Screenshot saved as {filename}")

    def atualizar_diagrama(self):
        """Update the Gantt diagram with current state"""
        current_time = self.sistema_operacional.get_relogio()
        tarefas = self.sistema_operacional.get_tarefas_ingressadas()
        self.create_gantt_diagram(current_time-1, tarefas)

    def create_gantt_diagram(self, current_time, tarefas):
        # Se criar um novo, tira o antigo
        if self.gantt_diagram:
            self.gantt_diagram.destroy()

        self.gantt_diagram = GanttDiagram(self, current_time, tarefas)
        self.gantt_diagram.pack(fill="both", expand=True, padx=20, pady=(20, 0))

    def redraw(self):
        if self.gantt_diagram:
            self.gantt_diagram.draw_grid()

if __name__ == "__main__":
    app = App()
    app.mainloop()