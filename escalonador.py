# ESCALONADOR

# INIT
# Recebe nome do escalonador desejado e salva
# Processa string: lowercase, tira whitespaces

# Execuação
# Usa um dicionário para chamar a função correta de escalonamento
# Caso contrário, usa FIFO como padrão (e notifica erro)
import queue
from tcb import TCB
# import heapq


# Fazer com vetor agora, depois atualizar para usar fila de prioridade (heap)
class Escalonador:
    def __init__(self, nome_escalonador: str):
        self.nome_escalonador = nome_escalonador.strip().lower()
        self.algoritmos_disponiveis = {
            "fifo": self.fifo,
            # Outros algoritmos podem ser adicionados aqui
        }
        self.estrutura_fila = {
            "fifo": queue.Queue,
            # Outros algoritmos podem ser adicionados aqui
        }

        self.fila_tarefas_prontas = self.estrutura_fila.get(self.nome_escalonador, queue.Queue)()

    def escalonar(self):
        if self.nome_escalonador in self.algoritmos_disponiveis:
            return self.algoritmos_disponiveis[self.nome_escalonador]()
        else:
            print(f"Escalonador '{self.nome_escalonador}' não reconhecido. Usando FIFO como padrão.")
            return self.fifo()
        
    def adicionar_tarefa_pronta(self, tarefa: TCB):
        # Adicionar tarefa na fila de prontas para heap também.
        self.fila_tarefas_prontas.put(tarefa)

    def fifo(self):
        if not self.fila_tarefas_prontas.empty():
            return self.fila_tarefas_prontas.get()
        return None