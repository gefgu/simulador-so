# ESCALONADOR

# INIT
# Recebe nome do escalonador desejado e salva
# Processa string: lowercase, tira whitespaces

# Execuação
# Usa um dicionário para chamar a função correta de escalonamento
# Caso contrário, usa FIFO como padrão (e notifica erro)
import queue
from tcb import TCB


# Fazer com vetor agora, depois atualizar para usar fila de prioridade (heap)
class Escalonador:
    def __init__(self, nome_escalonador: str):
        self.nome_escalonador = nome_escalonador.strip().lower()

        # Dicionário para mapear algoritmo à função
        self.algoritmos_disponiveis = {
            "fifo": self.fifo,
            "srtf": self.srtf,
        }

        # Escolhe a estrutura de dados correta para a fila de prontas
        if self.nome_escalonador == "srtf":
            self.fila_tarefas_prontas = []  # SRTF usa lista para encontrar o mínimo
        else:
            self.fila_tarefas_prontas = queue.Queue() # FIFO/RR usa uma fila real

    def escalonar(self):
        if self.nome_escalonador in self.algoritmos_disponiveis:
            return self.algoritmos_disponiveis[self.nome_escalonador]()
        else:
            print(f"Escalonador '{self.nome_escalonador}' não reconhecido. Usando FIFO como padrão.")
            return self.fifo()
        
    def adicionar_tarefa_pronta(self, tarefa: TCB):
        if isinstance(self.fila_tarefas_prontas, queue.Queue):
            self.fila_tarefas_prontas.put(tarefa)
        else:
            self.fila_tarefas_prontas.append(tarefa)

    def fifo(self):
        # Esta função agora serve para o Round Robin
        if not self.fila_tarefas_prontas.empty():
            return self.fila_tarefas_prontas.get()
        return None

    def srtf(self):
        if not self.fila_tarefas_prontas:
            return None
        
        tarefa_escolhida = min(self.fila_tarefas_prontas, key=lambda t: t['tempo_restante'])
        self.fila_tarefas_prontas.remove(tarefa_escolhida)
        return tarefa_escolhida