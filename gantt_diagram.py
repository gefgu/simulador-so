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
        self.margin_top = 80
        self.margin_bottom = 80
        self.margin_right = 60

        # Recebe a quantidade de tarefas e o tempo máximo para configurar o diagrama de Gantt
        self.n_tarefas = len(tarefas)
        self.tarefas = tarefas

        # O tempo máximo deve ser usado para definir a escala do diagrama, e atualizado conforme necessário
        self.max_time = current_time + 1  # Adiciona uma margem extra

        self.create_gantt_chart()
        
        # Bind resize event
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.after_idle(self.draw_grid)

    def create_gantt_chart(self):
        self.canvas = customtkinter.CTkCanvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

    def _on_canvas_resize(self, event):
        # Redraw when canvas is resized
        self.draw_grid()

    def draw_grid(self):
        # Limpa o canvas antes de desenhar a grade
        self.canvas.delete("all")
        if self.max_time == 0 or self.n_tarefas == 0: # Não tem nada para desenhar ainda
            return

        # Get actual canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Don't draw if canvas hasn't been laid out yet
        if canvas_width <= 1 or canvas_height <= 1:
            return

        usable_width = canvas_width - self.margin_left - self.margin_right
        usable_height = canvas_height - self.margin_top - self.margin_bottom

        cell_width = usable_width / self.max_time
        cell_height = usable_height / self.n_tarefas

        # Desenha linhas horizontais
        for i in range(self.n_tarefas + 1):
            y = self.margin_top + i * cell_height
            if i == (self.n_tarefas):
                self.canvas.create_line(self.margin_left, y, canvas_width - self.margin_right, y, fill="black", width=2)
        
        # Desenha linhas verticais
        for j in range(self.max_time + 1):
            x = self.margin_left + j * cell_width
            if j == 0:
                self.canvas.create_line(x, self.margin_top, x, canvas_height - self.margin_bottom, fill="black", width=2)
            else:
                # Outras linha: cinza e pontilhada
                self.canvas.create_line(x, self.margin_top, x, canvas_height - self.margin_bottom, fill="gray", dash=(5, 3))

            # Desenha a linha preta dos ticks dos números
            self.canvas.create_line(x, canvas_height - self.margin_bottom, x, 
                                    canvas_height - self.margin_bottom + 16, fill="black", width=2)

            # Adiciona o número abaixo de cada coluna
            self.canvas.create_text(
                x, 
                canvas_height - self.margin_bottom + 40, 
                text=str(j), 
                fill="black", 
                font=("Arial", 32)
            )

        self.draw_tarefas(self.tarefas)

    def draw_tarefas(self, tarefas):
        n_linhas = len(tarefas)
        for i, tarefa in enumerate(tarefas):
            self.draw_tarefa_bar(
                linha=(n_linhas-1-i),  # Inverte a ordem das tarefas para desenhar de baixo para cima
                id=tarefa["id"],
                ingresso=tarefa["ingresso"],
                duracao=tarefa["duracao"],
                cor=tarefa["cor"],
                tempos_de_execucao=tarefa["tempos_de_execucao"]
            )

    def draw_tarefa_bar(self, linha, id, ingresso, duracao, cor, tempos_de_execucao):

        tempo_atual = self.max_time - 1

        # Get actual canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        usable_width = canvas_width - self.margin_left - self.margin_right
        usable_height = canvas_height - self.margin_top - self.margin_bottom

        cell_width = usable_width / self.max_time
        cell_height = usable_height / self.n_tarefas

        bar_margin = 24

        tarefa_foi_concluida = duracao == len(tempos_de_execucao)

        if tarefa_foi_concluida:
            tempo_termino = tempos_de_execucao[-1]
        else:
            tempo_termino = tempo_atual

        # Adiciona o ID da tarefa na esquerda
        y_center = self.margin_top + linha * cell_height + cell_height / 2
        self.canvas.create_text(
            self.margin_left - 60, 
            y_center, 
            text=format_id_with_subscript(self, id), 
            fill="black", 
            font=("Arial", 36, "bold")
        )

        # Desenha retângulos para cada unidade de tempo desde ingresso até término
        for tempo in range(ingresso, tempo_termino + 1):
            x0 = self.margin_left + tempo * cell_width
            y0 = (self.margin_top + linha * cell_height) + bar_margin
            x1 = x0 + cell_width
            y1 = (y0 + cell_height - (2 * bar_margin))
            
            # Se o tempo está na lista de execução, preenche com a cor, senão com branco
            if tempo in tempos_de_execucao:
                fill_color = cor
            else:
                fill_color = "white"
            
            border_width = 6

            # Cria o retângulo sem borda
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color, outline="")
            
            # Adiciona borda esquerda no primeiro retângulo
            if (tempo == ingresso) or number_in_start_sequence(tempo, tempos_de_execucao):
                self.canvas.create_line(x0, y0, x0, y1, fill='black', width=border_width)
            
            # Adiciona borda direita no último retângulo
            if (tempo == tempo_termino) or number_in_end_sequence(tempo, tempos_de_execucao):
                self.canvas.create_line(x1, y0, x1, y1, fill='black', width=border_width)
            
            # Adiciona bordas superior e inferior em todos
            self.canvas.create_line(x0, y0, x1, y0, fill='black', width=border_width)  # Top
            self.canvas.create_line(x0, y1, x1, y1, fill='black', width=border_width)  # Bottom


def number_in_start_sequence(x, seq):
    index_x = seq.index(x) if x in seq else -1
    if index_x == -1:
        return False
    
    if (index_x == 0) or (seq[index_x - 1] < x-1):
        return True

    return False

def number_in_end_sequence(x, seq):
    index_x = seq.index(x) if x in seq else -1
    if index_x == -1:
        return False
    
    if (index_x == len(seq)-1) or (seq[index_x + 1] > x+1):
        return True

    return False


# Apenas para embelezar o display do ID
# Fonte: COPILOT
def format_id_with_subscript(self, id_string):
    """Convert t_1 to t₁ using unicode subscripts"""
    subscript_map = {
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
    }
    
    if '_' in id_string:
        parts = id_string.split('_')
        base = parts[0]
        number = parts[1]
        subscript = ''.join(subscript_map.get(c, c) for c in number)
        return f"{base}{subscript}"
    
    return id_string