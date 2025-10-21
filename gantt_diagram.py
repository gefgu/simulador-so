import customtkinter

class GanttDiagram(customtkinter.CTkFrame):
    def __init__(self, master, n_processes, max_time):
        super().__init__(master)

        # Margins for labels
        self.margin_left = 80
        self.margin_top = 160
        self.margin_bottom = 160
        self.margin_right = 40

        # Recebe a quantidade de processos e o tempo máximo para configurar o diagrama de Gantt
        self.n_processes = n_processes
        
        # O tempo máximo deve ser usado para definir a escala do diagrama, e atualizado conforme necessário
        self.max_time = max_time


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
        cell_height = usable_height / self.n_processes

        # Desenha linhas horizontais
        for i in range(self.n_processes + 1):
            y = self.margin_top + i * cell_height
            if i == (self.n_processes):
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