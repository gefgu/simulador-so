import customtkinter
from PIL import ImageGrab
from config_editor import ConfigEditor
from gantt_diagram import GanttDiagram
from sistema_operacional import SistemaOperacional
import copy  # Importante para salvar o histórico de estados
from datetime import datetime
from tkinter import filedialog

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1920x1080")
        self.title("Simulador SO")

        self.gantt_diagram = None
        self.sistema_operacional = None
        self.historico_estados = []  # Para guardar os "snapshots" da simulação
        self.config_file = "config_padrao.txt"
        self.config_editor = None
        self.config_frame = None

        # Widgets da tela de simulação (declarados aqui para fácil acesso)
        self.simulation_frame = None
        self.info_frame = None
        self.control_frame = None
        self.relogio_label = None
        self.algoritmo_label = None
        self.tarefa_exec_label = None
        
        self.prev_tick_button = None
        self.next_tick_button = None
        self.run_to_end_button = None

        self.selected_file_label = None

        self.create_menu_frame()

    def create_menu_frame(self):
        """Cria e exibe a tela de menu inicial."""
        self.menu_frame = customtkinter.CTkFrame(self)
        self.menu_frame.pack(fill="both", expand=True)
        
        title_label = customtkinter.CTkLabel(
            self.menu_frame, text="Simulador de SO", font=("Arial", 48, "bold")
        )
        title_label.pack(pady=(200, 50))
        
        start_button = customtkinter.CTkButton(
            self.menu_frame, text="Iniciar Simulação", font=("Arial", 24),
            width=250, height=60, command=self.iniciar_simulacao
        )
        start_button.pack(pady=80)

        self.selected_file_label = customtkinter.CTkButton(
            self.menu_frame, text="Nenhum arquivo selecionado", 
            font=("Arial", 18), command=self.seleciona_config,
             width=250, height=60
        )
        self.selected_file_label.pack(pady=(0, 60))

        config_editor_button = customtkinter.CTkButton(
            self.menu_frame, text="Abrir Configuração", font=("Arial", 24),
            width=250, height=60, command=self.cria_menu_edicao
        )
        config_editor_button.pack(pady=80)

    def iniciar_simulacao(self):
        """Inicia a simulação, destruindo o menu e construindo a UI de simulação."""
        self.menu_frame.destroy()
        self.historico_estados = []  # Limpa o histórico para uma nova simulação

        self.sistema_operacional = SistemaOperacional(self.config_file)

        # --- Construção da Interface de Simulação ---
        self.simulation_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.simulation_frame.pack(fill="both", expand=True)
        
        # -- 1. Frame de Informações (Topo) --
        self.info_frame = customtkinter.CTkFrame(self.simulation_frame, height=60)
        self.info_frame.pack(side="top", fill="x", padx=20, pady=(20, 0))

        self.relogio_label = customtkinter.CTkLabel(self.info_frame, text="Tick: 0", font=("Arial", 18))
        self.relogio_label.pack(side="left", padx=20)
        
        self.algoritmo_label = customtkinter.CTkLabel(self.info_frame, text=f"Algoritmo: {self.sistema_operacional.nome_escalonador.upper()}", font=("Arial", 18))
        self.algoritmo_label.pack(side="left", padx=20)
        
        self.tarefa_exec_label = customtkinter.CTkLabel(self.info_frame, text="Executando: Nenhuma", font=("Arial", 18))
        self.tarefa_exec_label.pack(side="left", padx=20)

        # -- 2. Frame de Controles (Baixo) --
        self.control_frame = customtkinter.CTkFrame(self.simulation_frame)
        self.control_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        buttons_frame = customtkinter.CTkFrame(self.control_frame)
        buttons_frame.pack(pady=10)
        
        # Botão: Voltar ao Menu
        reset_button = customtkinter.CTkButton(
            buttons_frame, text="Voltar ao Menu", font=("Arial", 18), width=200, height=50, command=self.resetar_simulacao
        )
        reset_button.pack(side="left", padx=10)

        # Botão: Regredir Tick
        self.prev_tick_button = customtkinter.CTkButton(
            buttons_frame, text="< Regredir Tick", font=("Arial", 18), width=200, height=50, command=self.tick_anterior, state="disabled"
        )
        self.prev_tick_button.pack(side="left", padx=10)

        # Botão: Próximo Tick
        self.next_tick_button = customtkinter.CTkButton(
            buttons_frame, text="Próximo Tick >", font=("Arial", 18), width=200, height=50, command=self.proximo_tick
        )
        self.next_tick_button.pack(side="left", padx=10)
        
        # Botão: Avançar até o Fim
        self.run_to_end_button = customtkinter.CTkButton(
            buttons_frame, text="Avançar até o Fim", font=("Arial", 18), width=200, height=50, command=self.avancar_ate_fim
        )
        self.run_to_end_button.pack(side="left", padx=10)

        # Botão: Salvar Imagem
        screenshot_button = customtkinter.CTkButton(
            buttons_frame, text="Salvar Imagem", font=("Arial", 18), width=200, height=50, command=self.take_screenshot
        )
        screenshot_button.pack(side="left", padx=10)

        # Inicia e exibe o estado inicial (tick 0)
        self.atualizar_diagrama()

    def proximo_tick(self):
        """Salva o estado atual, executa um tick e atualiza a UI."""
        if not self.sistema_operacional.simulacao_terminada():
            # Salva o estado ATUAL antes de executar o próximo tick
            try:
                self.historico_estados.append(copy.deepcopy(self.sistema_operacional)) # Adicionar um método que funcione com o Queue depois
            except Exception as e:
                print(f"Erro ao salvar estado para histórico: {e}")
            finally:
                self.sistema_operacional.executar_tick()
                self.atualizar_diagrama()

        # Atualiza o estado dos botões
        if self.sistema_operacional.simulacao_terminada():
            self.next_tick_button.configure(state="disabled")
            self.run_to_end_button.configure(state="disabled")
        
        self.prev_tick_button.configure(state="normal") # Sempre podemos regredir depois de avançar

    def tick_anterior(self):
        """Restaura o estado anterior do histórico e atualiza a UI."""
        if self.historico_estados:
            # Pega o último estado salvo e o restaura
            self.sistema_operacional = self.historico_estados.pop()
            self.atualizar_diagrama()

        # Atualiza o estado dos botões
        if not self.historico_estados:
            self.prev_tick_button.configure(state="disabled") # Desabilita se não há mais histórico
        
        self.next_tick_button.configure(state="normal") # Sempre podemos avançar depois de regredir
        self.run_to_end_button.configure(state="normal")

    def avancar_ate_fim(self):
        """Executa a simulação até o fim, salvando cada passo no histórico."""
        while not self.sistema_operacional.simulacao_terminada():
            # Ainda salvamos o histórico para poder regredir passo a passo depois
            try:
                self.historico_estados.append(copy.deepcopy(self.sistema_operacional)) # Adicionar um método que funcione com o Queue depois
            except Exception as e:
                print(f"Erro ao salvar estado para histórico: {e}")
            finally:
                self.sistema_operacional.executar_tick()

        self.atualizar_diagrama()
        self.update() # Força a atualização da UI
        
        # Desabilita botões de avanço
        self.next_tick_button.configure(state="disabled")
        self.run_to_end_button.configure(state="disabled")
        self.prev_tick_button.configure(state="normal") # Garante que podemos regredir

    def resetar_simulacao(self):
        """Destrói a UI da simulação e volta para o menu principal."""
        if self.simulation_frame:
            self.simulation_frame.destroy()

        self.gantt_diagram = None
        self.sistema_operacional = None
        self.historico_estados = []
        
        self.create_menu_frame()

    def atualizar_diagrama(self):
        """Atualiza o diagrama de Gantt e todas as informações na tela."""
        so = self.sistema_operacional
        current_time = so.get_relogio()
        tarefas = so.get_tarefas_ingressadas()
        tarefa_executando = so.get_tarefa_executando()
        
        # Atualiza labels de informação
        self.relogio_label.configure(text=f"Tick: {current_time}")
        if tarefa_executando:
            self.tarefa_exec_label.configure(text=f"Executando: {tarefa_executando['id']}")
        else:
            self.tarefa_exec_label.configure(text="Executando: Nenhuma")

        # Recria o diagrama de Gantt
        if self.gantt_diagram:
            self.gantt_diagram.destroy()

        # O diagrama deve ser filho do simulation_frame
        self.gantt_diagram = GanttDiagram(self.simulation_frame, current_time, tarefas)
        # Usa .pack() para colocar o diagrama
        self.gantt_diagram.pack(fill="both", expand=True, padx=20, pady=10)
        # Coloca o diagrama abaixo do info_frame e acima do control_frame
        self.gantt_diagram.tkraise()
        self.control_frame.tkraise()

    def seleciona_config(self):
        file_path = filedialog.askopenfilename(
            title="Selecione um arquivo de configuração",
            initialdir=".",  # Changed from "/" to current directory
            filetypes=[("Text files", "*.txt")],  # Fixed format
            initialfile="./config_padrao.txt"
        )
        if file_path:
            print(f"Arquivo selecionado: {file_path}")
            self.config_file = file_path  # Save the selected file path
            self.selected_file_label.configure(text=f"Selecionado: {file_path.split('/')[-1]}")  # Show only filename

    def take_screenshot(self):
        """Tira um screenshot da área do diagrama de Gantt."""
        if self.gantt_diagram and self.gantt_diagram.canvas:
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
            print(f"Screenshot salvo como {filename}")

    def volta_menu_edicao(self):
        self.config_frame.destroy()
        self.create_menu_frame()

    def cria_menu_edicao(self):
        self.menu_frame.destroy()
        self.config_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.config_frame.pack(fill="both", expand=True)

        self.config_editor = ConfigEditor(self, self.config_frame, 
                                          self.volta_menu_edicao, self.config_file)

if __name__ == "__main__":
    app = App()
    app.mainloop()