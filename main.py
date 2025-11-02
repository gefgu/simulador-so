import customtkinter
from config_editor import ConfigEditor
from simulacao_frame import SimulacaoFrame
from tkinter import filedialog

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # Inicialização da janela principal
        self.geometry("1920x1080")
        self.title("Simulador SO")

        self.config_file = "config_padrao.txt"
        self.config_selected = False
        self.config_editor = None
        self.config_frame = None
        self.simulacao_frame = None

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

        button_text = "Selecionar Arquivo de Configuração (Atual: Padrão)"
        if self.config_selected:
            button_text = f"Selecionado: {self.config_file.split('/')[-1]}"
        self.selected_file_label = customtkinter.CTkButton(
            self.menu_frame, text=button_text, 
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
        self.simulacao_frame = SimulacaoFrame(self, self.reseta_simulacao)
        self.simulacao_frame.create_simulation_ui(self.config_file)
        self.simulacao_frame.pack(fill="both", expand=True)

    def seleciona_config(self):
        """Abre um diálogo para selecionar um arquivo de configuração."""
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
            self.config_selected = True

    def reseta_simulacao(self):
        """Reseta a simulação, destruindo a UI de simulação e retornando ao menu."""
        if self.simulacao_frame:
            self.simulacao_frame.destroy()
            self.simulacao_frame = None
        self.create_menu_frame()

    def volta_menu_edicao(self, config_file: str):
        """Volta ao menu principal após editar a configuração."""
        self.config_file = config_file
        self.config_selected = True
        if self.config_frame:
            self.config_frame.destroy()
            self.config_frame = None
        self.create_menu_frame()

    def cria_menu_edicao(self):
        """Cria a interface para edição de configuração."""
        if self.menu_frame:
            self.menu_frame.destroy()
            self.menu_frame = None

        if self.config_frame:
            self.config_frame.destroy()
            self.config_frame = None

        self.config_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.config_frame.pack(fill="both", expand=True)

        self.config_editor = ConfigEditor(self, 
                                          self.config_frame, 
                                          self.volta_menu_edicao, 
                                          self.config_file)

if __name__ == "__main__":
    app = App()
    app.mainloop()