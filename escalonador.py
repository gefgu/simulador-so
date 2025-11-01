# ESCALONADOR

# INIT
# Recebe nome do escalonador desejado e salva
# Processa string: lowercase, tira whitespaces

# Execuação
# Usa um dicionário para chamar a função correta de escalonamento
# Caso contrário, usa FIFO como padrão (e notifica erro)
from tcb import TCB


# Fazer com vetor agora, depois atualizar para usar fila de prioridade (heap)
class Escalonador:
    def __init__(self, nome_escalonador: str):
        self.nome_escalonador = nome_escalonador.strip().lower()

        # Dicionário para mapear algoritmo à função
        self.algoritmos_disponiveis = {
            "fifo": self.fifo,
            "srtf": self.srtf,
            "priop": self.prioridade_preemptiva,
        }

        # Escolhe a estrutura de dados correta para a fila de prontas
        # Usamos lista para todos os algoritmos para evitar problemas com copy.deepcopy()
        self.fila_tarefas_prontas = []  # Lista funciona para FIFO, SRTF e outros

    def escalonar(self):
        if self.nome_escalonador in self.algoritmos_disponiveis:
            return self.algoritmos_disponiveis[self.nome_escalonador]()
        else:
            print(f"Escalonador '{self.nome_escalonador}' não reconhecido. Usando FIFO como padrão.")
            return self.fifo()
        
    def adicionar_tarefa_pronta(self, tarefa: TCB):
        self.fila_tarefas_prontas.append(tarefa)

    def fifo(self):
        if self.fila_tarefas_prontas:
            return self.fila_tarefas_prontas.pop(0)  # Remove do início (índice 0)
        return None

    def srtf(self, tarefa_executando=None):
        if not self.fila_tarefas_prontas:
            return None
        
        tarefa_escolhida = min(self.fila_tarefas_prontas, key=lambda t: t['tempo_restante'])
        self.fila_tarefas_prontas.remove(tarefa_escolhida)
        return tarefa_escolhida

    def prioridade_preemptiva(self):
        """
        Algoritmo de Prioridade Preemptiva (PRIOp):
        Escolhe a tarefa com MAIOR prioridade (maior número = maior prioridade).
        Em caso de empate, usa ordem FIFO (primeira que chegou na fila).
        """
        if not self.fila_tarefas_prontas:
            return None
        
        # Encontra a tarefa com maior prioridade
        # Em caso de empate, min() retorna a primeira (comportamento FIFO para empates)
        tarefa_escolhida = max(self.fila_tarefas_prontas, key=lambda t: t['prioridade'])
        self.fila_tarefas_prontas.remove(tarefa_escolhida)
        return tarefa_escolhida