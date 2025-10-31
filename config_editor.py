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
        self.main_frame = frame
        self.voltar_callback = voltar_callback
        self.filename_entry = None
        self.original_config_file = config_file
        self.tasks_entries = []


        self.quantum = 2
        self.nome_escalonador = "FIFO"
        self.tarefas: list[TCB] = [cria_tarefa_padrao()]

        dados_config = read_config(config_file)
        if dados_config:
            self.quantum = dados_config["quantum"]
            self.nome_escalonador = dados_config["nome_escalonador"]
            self.tarefas = dados_config["tarefas"]

        self.menu_frame = customtkinter.CTkScrollableFrame(
            self.main_frame,
            width=1800,
            height=900
        )
        self.menu_frame.pack(fill="both", expand=True, padx=20, pady=20)



        self.cria_menu_edicao()

    def cria_menu_edicao(self):
        """Cria o menu de edição de configurações"""
        # Limpa frame anterior
        for widget in self.menu_frame.winfo_children():
            widget.destroy()


        title_label = customtkinter.CTkLabel(
            self.menu_frame, text="Configurações", font=("Arial", 48, "bold")
        )
        title_label.pack(pady=(200, 50))

        # Create algorithm and quantum pickers in the same row
        self.create_config_controls()

        self.create_task_list()

        buttons_frame = customtkinter.CTkFrame(self.menu_frame, fg_color="transparent")
        buttons_frame.pack(pady=40)

        add_button = customtkinter.CTkButton(
            buttons_frame, text="Adicionar Tarefa", font=("Arial", 24),
            width=200, height=60, command=self.adiciona_nova_tarefa
        )
        add_button.pack(side="left", padx=10)

        voltar_button = customtkinter.CTkButton(
            buttons_frame, text="Voltar", font=("Arial", 24),
            width=200, height=60, command=self.voltar_sem_salvar
        )
        voltar_button.pack(side="left", padx=10)

        salvar_button = customtkinter.CTkButton(
            buttons_frame, text="Salvar", font=("Arial", 24),
            width=200, height=60, command=self.voltar_e_salvar
        )
        salvar_button.pack(side="left", padx=10)

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

        filename_label = customtkinter.CTkLabel(
            controls_frame, text="Filename:", font=("Arial", 18)
        )
        filename_label.pack(side="left", padx=5)
        self.filename_entry = customtkinter.CTkEntry(
            controls_frame, width=300, font=("Arial", 18)
        )
        self.filename_entry.insert(0, "config_001.txt")
        self.filename_entry.pack(side="left", padx=5)

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
        self.tasks_entries = []  # Clear the list first
        for tarefa in self.tarefas:
            self.tasks_entries.append(self.create_task_config_row(tarefa))

    def remove_task_row(self, entries_dict):
        """Remove uma linha de tarefa do formulário"""
        # Remove from the tasks_entries list
        if entries_dict in self.tasks_entries:
            self.tasks_entries.remove(entries_dict)
        # Recreate the menu
        self.cria_menu_edicao()

    def adiciona_nova_tarefa(self):
        """Adiciona uma nova linha de tarefa ao formulário"""
        nova_tarefa = cria_tarefa_padrao()
        self.tarefas.append(nova_tarefa)
        self.cria_menu_edicao()

    def create_task_config_row(self, tarefa: TCB):
        """Cria uma linha com o espaço para o id, cor, ingresso, duração e prioridade da tarefa"""
        task_frame = customtkinter.CTkFrame(self.menu_frame, fg_color="transparent")
        task_frame.pack(pady=20)

        # Store references to the entries in a dictionary
        entries_dict = {}

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
        entries_dict['id'] = id_entry

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
        entries_dict['cor'] = color_entry

        # Ingresso
        ingresso_label = customtkinter.CTkLabel(
            task_frame, text="Ingresso:", font=("Arial", 18)
        )
        ingresso_label.pack(side="left", padx=5)
        ingresso_entry = customtkinter.CTkEntry(
            task_frame, width=100, font=("Arial", 18)
        )
        ingresso_entry.insert(0, str(tarefa["ingresso"]))
        ingresso_entry.pack(side="left", padx=5)
        entries_dict['ingresso'] = ingresso_entry

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
        entries_dict['duracao'] = duracao_entry

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
        entries_dict['prioridade'] = prioridade_entry

        remove_button = customtkinter.CTkButton(
            task_frame, text="Remover", font=("Arial", 18),
            width=100, height=40, command=lambda: self.remove_task_row(entries_dict)
        )
        remove_button.pack(side="left", padx=10)

        return entries_dict

    def voltar_sem_salvar(self):
        """Callback para voltar ao menu principal sem salvar as configurações"""
        self.menu_frame.destroy()
        self.voltar_callback(self.original_config_file)

    def voltar_e_salvar(self):
        """Callback para voltar ao menu principal e salvar as configurações"""
        filename = self.filename_entry.get()
        nome_escalonador = self.algorithm_picker.get()
        quantum = self.quantum

        with open(filename, 'w') as file:
            file.write(f"{nome_escalonador};{quantum}\n")
            for entries_dict in self.tasks_entries:
                id = entries_dict['id'].get()
                cor = entries_dict['cor'].get()
                ingresso = entries_dict['ingresso'].get()
                duracao = entries_dict['duracao'].get()
                prioridade = entries_dict['prioridade'].get()
                file.write(f"{id};{cor};{ingresso};{duracao};{prioridade};\n")

        self.menu_frame.destroy()
        self.voltar_callback(filename)