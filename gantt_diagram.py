import customtkinter


class GanttDiagram(customtkinter.CTkFrame):
    """ 
    Tarefas são do formato:
        - "id"
        - cor (string em hexadecimal)
        - ingresso
        - duracao
        - prioridade
        - Adicionar uma lista com os momentos em que a tarefa executou.
    """

    def __init__(self, master, current_time, tarefas):
        super().__init__(master)

        # Margins for labels
        self.margin_left = 120
        self.margin_top = 160
        self.margin_bottom = 160
        self.margin_right = 60

        # Recebe a quantidade de tarefas e o tempo máximo para configurar o diagrama de Gantt
        self.n_tarefas = len(tarefas)
        self.tarefas = tarefas

        # O tempo máximo deve ser usado para definir a escala do diagrama, e atualizado conforme necessário
        self.max_time = current_time + 1  # Adiciona uma margem extra


        self.create_gantt_chart()
        self.after_idle(self.draw_grid)

    def create_gantt_chart(self):
        self.canvas = customtkinter.CTkCanvas(self, bg="white")

        self.canvas.pack(fill="both", expand=True)

    def draw_grid(self):
        # Limpa o canvas antes de desenhar a grade
        self.canvas.delete("all")

        # canvas_width = self.canvas.winfo_width()
        # canvas_height = self.canvas.winfo_height()
        canvas_width = 1920
        canvas_height = 1080


        usable_width = canvas_width - self.margin_left - self.margin_right
        usable_height = canvas_height - self.margin_top - self.margin_bottom

        print(usable_width, usable_height)
        cell_width = usable_width / self.max_time
        cell_height = usable_height / self.n_tarefas

        # Desenha linhas horizontais
        for i in range(self.n_tarefas + 1):
            y = self.margin_top + i * cell_height
            if i == (self.n_tarefas):
                self.canvas.create_line(self.margin_left, y, canvas_width - self.margin_right, y, fill="black")
            else:
                # Outras linha: cinza e pontilhada
                self.canvas.create_line(self.margin_left, y, canvas_width - self.margin_right, y, fill="gray", dash=(5, 3))
        

        # Desenha linhas verticais
        for j in range(self.max_time + 1):
            x = self.margin_left + j * cell_width
            if j == 0:
                self.canvas.create_line(x, self.margin_top, x, canvas_height - self.margin_bottom, fill="black")
            else:
                # Outras linha: cinza e pontilhada
                self.canvas.create_line(x, self.margin_top, x, canvas_height - self.margin_bottom, fill="gray", dash=(5, 3))

            # Adiciona o número abaixo de cada coluna
            self.canvas.create_text(
                x, 
                canvas_height - self.margin_bottom + 20, 
                text=str(j), 
                fill="black", 
                font=("Arial", 18)
            )

        self.draw_tarefas(self.tarefas)

    def draw_tarefas(self, tarefas):
        for i, tarefa in enumerate(tarefas):
            self.draw_tarefa_bar(
                linha=i,
                id=tarefa["id"],
                ingresso=tarefa["ingresso"],
                duracao=tarefa["duracao"],
                cor=tarefa["cor"]
            )

    def draw_tarefa_bar(self, linha, id, ingresso, duracao, cor):
        # canvas_width = self.canvas.winfo_width()
        # canvas_height = self.canvas.winfo_height()
        canvas_width = 1920
        canvas_height = 1080

        usable_width = canvas_width - self.margin_left - self.margin_right
        usable_height = canvas_height - self.margin_top - self.margin_bottom

        cell_width = usable_width / self.max_time
        cell_height = usable_height / self.n_tarefas

        bar_margin = 24

        x0 = self.margin_left + ingresso * cell_width
        y0 = (self.margin_top + linha * cell_height) + bar_margin
        x1 = x0 + duracao * cell_width
        y1 = (y0 + cell_height - (2 * bar_margin))

        self.canvas.create_rectangle(x0, y0, x1, y1, fill=cor, outline='black', width=4)

        # Adiciona o ID da tarefa na esquerda da primeira coluna
        self.canvas.create_text(
            self.margin_left - 60, 
            y0 + cell_height / 2, 
            text=f"{id}", 
            fill="black", 
            font=("Arial", 18)
        )