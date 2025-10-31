import customtkinter

from config_handler import read_config
from tcb import TCB

def cria_tarefa_padrao() -> TCB:
    """Cria uma tarefa padrão para preencher os campos inicialmente"""
    return TCB(
        id="T1",
        cor="#FF0000",
        ingresso=0,
        duracao=5,
        prioridade=1,
        tempo_restante=5,
        tempos_de_execucao=[],
        lista_eventos=[]
    )


class ConfigEditor(customtkinter.CTkFrame):
    def __init__(self, master, frame, voltar_callback, config_file: str):
        super().__init__(master)

        self.algorithm_picker = None
        self.quantum_entry = None
        self.menu_frame = frame
        self.voltar_callback = voltar_callback



        self.quantum = 2
        self.nome_escalonador = "FIFO"
        self.tarefas: list[TCB] = [cria_tarefa_padrao()]

        dados_config = read_config(config_file)
        if dados_config:
            self.quantum = dados_config["quantum"]
            self.nome_escalonador = dados_config["nome_escalonador"]
            self.tarefas = dados_config["tarefas"]

        self.cria_menu_edicao()

    def cria_menu_edicao(self):
        title_label = customtkinter.CTkLabel(
            self.menu_frame, text="Configurações", font=("Arial", 48, "bold")
        )
        title_label.pack(pady=(200, 50))

        # Create algorithm and quantum pickers in the same row
        self.create_config_controls()

        self.create_task_list()

        voltar_button = customtkinter.CTkButton(
            self.menu_frame, text="Voltar", font=("Arial", 24),
            width=250, height=60, command=self.voltar_callback
        )
        voltar_button.pack(pady=80)

    def create_config_controls(self):
        """Creates algorithm picker and quantum picker in the same row"""
        # Main horizontal frame
        controls_frame = customtkinter.CTkFrame(self.menu_frame, fg_color="transparent")
        controls_frame.pack(pady=20)

        # Algorithm section (left side)
        algorithm_section = customtkinter.CTkFrame(controls_frame, fg_color="transparent")
        algorithm_section.pack(side="left", padx=30)

        algorithm_label = customtkinter.CTkLabel(
            algorithm_section, text="Algoritmo:", font=("Arial", 18)
        )
        algorithm_label.pack(pady=(0, 10))

        self.algorithm_picker = customtkinter.CTkOptionMenu(
            algorithm_section, 
            values=["FIFO", "SRTF"], 
            font=("Arial", 24),
            width=200,
            height=50
        )
        self.algorithm_picker.pack()

        # Quantum section (right side)
        quantum_section = customtkinter.CTkFrame(controls_frame, fg_color="transparent")
        quantum_section.pack(side="left", padx=30)

        quantum_label = customtkinter.CTkLabel(
            quantum_section, text="Quantum:", font=("Arial", 18)
        )
        quantum_label.pack(pady=(0, 10))

        # Quantum controls frame
        quantum_controls = customtkinter.CTkFrame(quantum_section, fg_color="transparent")
        quantum_controls.pack()

        # Decrement button
        decrement_button = customtkinter.CTkButton(
            quantum_controls,
            text="-",
            font=("Arial", 24, "bold"),
            width=50,
            height=50,
            command=self.decrement_quantum
        )
        decrement_button.pack(side="left", padx=5)

        # Quantum display
        self.quantum_entry = customtkinter.CTkLabel(
            quantum_controls,
            text=str(self.quantum),
            font=("Arial", 32, "bold"),
            width=100,
            height=50
        )
        self.quantum_entry.pack(side="left", padx=10)

        # Increment button
        increment_button = customtkinter.CTkButton(
            quantum_controls,
            text="+",
            font=("Arial", 24, "bold"),
            width=50,
            height=50,
            command=self.increment_quantum
        )
        increment_button.pack(side="left", padx=5)

    def increment_quantum(self):
        """Increase quantum value"""
        self.quantum += 1
        self.quantum_entry.configure(text=str(self.quantum))

    def decrement_quantum(self):
        """Decrease quantum value (minimum 1)"""
        if self.quantum > 1:
            self.quantum -= 1
            self.quantum_entry.configure(text=str(self.quantum))


    def create_task_list(self):
        """Cria o fórmulário da lista de tarefas atualmente sendo configuradas"""
        for tarefa in self.tarefas:
            self.create_task_config_row(tarefa)

    def create_task_config_row(self, tarefa: TCB):
        """Cria uma linha com o espaço para o id, cor, ingresso, duração e prioridade da tarefa"""
        task_frame = customtkinter.CTkFrame(self.menu_frame, fg_color="transparent")
        task_frame.pack(pady=20)

        # ID
        id_label = customtkinter.CTkLabel(
            task_frame, text="ID:", font=("Arial", 18)
        )
        id_label.pack(side="left", padx=5)
        id_entry = customtkinter.CTkEntry(
            task_frame, width=100, font=("Arial", 18)
        )
        id_entry.insert(0, tarefa["id"])
        id_entry.pack(side="left", padx=5)

        # Cor
        color_label = customtkinter.CTkLabel(
            task_frame, text="Cor:", font=("Arial", 18)
        )
        color_label.pack(side="left", padx=5)
        color_entry = customtkinter.CTkEntry(
            task_frame, width=100, font=("Arial", 18)
        )
        color_entry.insert(0, tarefa["cor"])
        color_entry.pack(side="left", padx=5)

        # Ingress
        ingresso_label = customtkinter.CTkLabel(
            task_frame, text="Ingresso:", font=("Arial", 18)
        )
        ingresso_label.pack(side="left", padx=5)
        ingresso_entry = customtkinter.CTkEntry(
            task_frame, width=100, font=("Arial", 18)
        )
        ingresso_entry.insert(0, str(tarefa["ingresso"]))
        ingresso_entry.pack(side="left", padx=5)

        # Duração
        duracao_label = customtkinter.CTkLabel(
            task_frame, text="Duração:", font=("Arial", 18)
        )
        duracao_label.pack(side="left", padx=5)
        duracao_entry = customtkinter.CTkEntry(
            task_frame, width=100, font=("Arial", 18) 
        )
        duracao_entry.insert(0, str(tarefa["duracao"]))
        duracao_entry.pack(side="left", padx=5)

        # Prioridade
        prioridade_label = customtkinter.CTkLabel(
            task_frame, text="Prioridade:", font=("Arial", 18)
        )
        prioridade_label.pack(side="left", padx=5)
        prioridade_entry = customtkinter.CTkEntry(
            task_frame, width=100, font=("Arial", 18)
        )
        prioridade_entry.insert(0, str(tarefa["prioridade"]))
        prioridade_entry.pack(side="left", padx=5)

    def get_quantum(self):
        """Get current quantum value"""
        return self.quantum

    def get_algorithm(self):
        """Get selected algorithm"""
        return self.algorithm_picker.get()