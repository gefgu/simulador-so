from tcb import TCB

# Para adicionar um novo algoritmo de escalonamento:
# 1. Adicione uma nova função na classe Escalonador seguindo o padrão das existentes.
# 2. Adicione a função ao dicionário self.algoritmos_disponiveis com a chave sendo o nome do algoritmo em minúsculas.
# 3. deve_preemptar() deve ser atualizado se o novo algoritmo causar preempção na chegada de novas tarefas.
# 4. get_preempcao_chegada() e get_preempcao_quantum() devem ser atualizados conforme necessário.
class Escalonador:
    def __init__(self, nome_escalonador: str, alpha: int = 1):
        self.nome_escalonador = nome_escalonador.strip().lower()

        # Dicionário para mapear algoritmo à função
        self.algoritmos_disponiveis = {
            "fifo": self.fifo,
            "srtf": self.srtf,
            "priop": self.prioridade_preemptiva,
            "priopenv": self.prioridade_envelhecimento
        }

        self.alpha = alpha  # Fator de envelhecimento para algoritmos que o utilizam

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
        tarefa['prioridade_dinamica'] = tarefa['prioridade']  # Inicializa prioridade dinâmica

    def deve_preemptar(self, tarefa_atual: TCB) -> bool:
        """Verifica se a tarefa atual deve ser preemptada por alguma tarefa na fila de prontas."""
        if not self.fila_tarefas_prontas:
            return False
        if self.nome_escalonador == "fifo":
            return False
        elif self.nome_escalonador == "srtf":
            return min(self.fila_tarefas_prontas, key=lambda t: t['tempo_restante'])["tempo_restante"] < tarefa_atual['tempo_restante']
        elif self.nome_escalonador == "priop":
            return max(self.fila_tarefas_prontas, key=lambda t: t['prioridade'])["prioridade"] > tarefa_atual['prioridade']
        elif self.nome_escalonador == "priopenv":
            for tarefa in self.fila_tarefas_prontas:
                tarefa['prioridade_dinamica'] += self.alpha  # Aplica envelhecimento
            tarefa_mais_prioritaria = max(self.fila_tarefas_prontas, key=lambda t: t['prioridade_dinamica'])
            return tarefa_mais_prioritaria["prioridade_dinamica"] > tarefa_atual['prioridade_dinamica']

        return False

    def fifo(self):
        """Algoritmo FIFO (First In, First Out):"""
        if self.fila_tarefas_prontas:
            return self.fila_tarefas_prontas.pop(0)  # Remove do início (índice 0)
        return None

    def srtf(self):
        """Algoritmo SRTF (Shortest Remaining Time First): Escolhe a tarefa com MENOR tempo restante."""
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
    
    def prioridade_envelhecimento(self):
        """
        Algoritmo de Prioridade com Envelhecimento (PRIOpENV):
        Escolhe a tarefa com MAIOR prioridade (maior número = maior prioridade).
        Em caso de empate, usa ordem FIFO (primeira que chegou na fila).
        Aplica envelhecimento aumentando a prioridade das tarefas na fila.
        """
        if not self.fila_tarefas_prontas:
            return None
        
        # Encontra a tarefa com maior prioridade
        # Em caso de empate, min() retorna a primeira (comportamento FIFO para empates)
        tarefa_escolhida = max(self.fila_tarefas_prontas, key=lambda t: t['prioridade_dinamica'])
        self.fila_tarefas_prontas.remove(tarefa_escolhida)
        return tarefa_escolhida
    
    def get_preempcao_chegada(self) -> bool:
        return self.nome_escalonador in ["srtf", "priop", "priopenv"]
    
    def get_preempcao_quantum(self) -> bool:
        return self.nome_escalonador in ["fifo"]