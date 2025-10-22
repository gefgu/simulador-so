from time import sleep
import customtkinter
from collections import deque

from config_handler import get_config_values
from gantt_diagram import GanttDiagram

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1920x1080")

        self.title("Simulador SO")

        self.gantt_diagram = None

    
    def create_gantt_diagram(self, current_time, tarefas):
        # Se criar um novo, tira o antigo
        if self.gantt_diagram:
            self.gantt_diagram.destroy()

        self.gantt_diagram = GanttDiagram(self, current_time, tarefas)
        self.gantt_diagram.pack(fill="both", expand=True)

    def redraw(self):
        if self.gantt_diagram:
            self.gantt_diagram.draw_grid()

def algoritmo(tarefas):
    tempo_atual = 0
    fila_tarefas_nao_ingressadas = deque(sorted(tarefas, key=lambda x: x["ingresso"]))
    fila_tarefas_prontas = deque()
    tarefa_em_execucao = None

    tarefas_executadas = []

    while fila_tarefas_nao_ingressadas or fila_tarefas_prontas:
        # Adiciona tarefas ingressadas na fila de prontas
        while (fila_tarefas_nao_ingressadas and
               fila_tarefas_nao_ingressadas[0]["ingresso"] <= tempo_atual):
            tarefa = fila_tarefas_nao_ingressadas.popleft()
            tarefa["tempo_restante"] = tarefa["duracao"]
            fila_tarefas_prontas.append(tarefa)

        # Se houver tarefas prontas, executa a próxima
        if fila_tarefas_prontas:
            tarefa_em_execucao = fila_tarefas_prontas.popleft()
            # Simula a execução da tarefa por 1 unidade de tempo
            tarefa_em_execucao["tempo_restante"] -= 1


            # Registra o tempo de execução
            if "tempos_de_execucao" not in tarefa_em_execucao:
                tarefa_em_execucao["tempos_de_execucao"] = []
            tarefa_em_execucao["tempos_de_execucao"].append(tempo_atual)

            # Se a tarefa ainda não terminou, re-adiciona na fila de prontas
            if tarefa_em_execucao["tempo_restante"] > 0:
                fila_tarefas_prontas.append(tarefa_em_execucao)
            else:
                tarefas_executadas.append(tarefa_em_execucao)

        tempo_atual += 1

    return tarefas_executadas


if __name__ == "__main__":
    config = get_config_values("config.txt")

    print(config)

    tarefas_executadas = algoritmo(config["tarefas"])

    print(tarefas_executadas)

    app = App()
    app.create_gantt_diagram(current_time=25, tarefas=tarefas_executadas)

    app.mainloop()