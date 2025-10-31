import customtkinter


class ConfigEditor(customtkinter.CTkFrame):
    def __init__(self, master, frame, config_file: str, voltar_callback):
        super().__init__(master)

        self.algorithm_picker = None
        self.quantum_entry = None

        self.quantum_value = 2

        self.menu_frame = frame
        self.voltar_callback = voltar_callback
        self.cria_menu_edicao()

    def cria_menu_edicao(self):
        title_label = customtkinter.CTkLabel(
            self.menu_frame, text="Configurações", font=("Arial", 48, "bold")
        )
        title_label.pack(pady=(200, 50))

        # Create algorithm and quantum pickers in the same row
        self.create_config_controls()

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
            text=str(self.quantum_value),
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
        self.quantum_value += 1
        self.quantum_entry.configure(text=str(self.quantum_value))

    def decrement_quantum(self):
        """Decrease quantum value (minimum 1)"""
        if self.quantum_value > 1:
            self.quantum_value -= 1
            self.quantum_entry.configure(text=str(self.quantum_value))

    def get_quantum(self):
        """Get current quantum value"""
        return self.quantum_value

    def get_algorithm(self):
        """Get selected algorithm"""
        return self.algorithm_picker.get()