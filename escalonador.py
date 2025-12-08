from tcb import TCB
import random

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
            "rr": self.fifo,  # RR usa mesma lógica do FIFO, preempção por quantum
            "srtf": self.srtf,
            "priop": self.prioridade_preemptiva,
            "priopenv": self.prioridade_envelhecimento
        }

        self.alpha = alpha  # Fator de envelhecimento para algoritmos que o utilizam
        self.tarefa_atual = None  # Referência à tarefa atualmente em execução (para desempate)
        self.ultimo_sorteio = False  # Flag para indicar se houve sorteio no último escalonamento

        # Escolhe a estrutura de dados correta para a fila de prontas
        # Usamos lista para todos os algoritmos para evitar problemas com copy.deepcopy()
        self.fila_tarefas_prontas = []  # Lista funciona para FIFO, SRTF e outros

    def set_tarefa_atual(self, tarefa: TCB | None):
        """Define a tarefa atualmente em execução (usado para regras de desempate)."""
        self.tarefa_atual = tarefa

    def escalonar(self):
        self.ultimo_sorteio = False  # Reset flag de sorteio
        if self.nome_escalonador in self.algoritmos_disponiveis:
            return self.algoritmos_disponiveis[self.nome_escalonador]()
        else:
            print(f"Escalonador '{self.nome_escalonador}' não reconhecido. Usando FIFO como padrão.")
            return self.fifo()
        
    def adicionar_tarefa_pronta(self, tarefa: TCB):
        self.fila_tarefas_prontas.append(tarefa)
        # Não reseta prioridade dinâmica aqui - só quando é escalonada

    def _desempatar(self, candidatas: list[TCB], usar_prioridade_estatica: bool = False) -> TCB:
        """
        Aplica regras de desempate conforme requisitos:
        Para PRIOPEnv: (1) maior prioridade estática, (2) tarefa já executando, (3) ingresso mais antigo, (4) menor duração, (5) sorteio
        Para outros: (1) tarefa já executando, (2) ingresso mais antigo, (3) menor duração, (4) sorteio
        """
        if len(candidatas) == 1:
            return candidatas[0]
        
        # Critério 1 (só para PRIOPEnv): Maior prioridade estática
        if usar_prioridade_estatica:
            max_prioridade = max(t['prioridade'] for t in candidatas)
            candidatas = [t for t in candidatas if t['prioridade'] == max_prioridade]
            if len(candidatas) == 1:
                return candidatas[0]
        
        # Critério 2: Tarefa já executando (evita troca de contexto desnecessária)
        if self.tarefa_atual and self.tarefa_atual in candidatas:
            return self.tarefa_atual
        
        # Critério 3: Ingresso mais antigo (quem chegou antes)
        min_ingresso = min(t['ingresso'] for t in candidatas)
        candidatas = [t for t in candidatas if t['ingresso'] == min_ingresso]
        if len(candidatas) == 1:
            return candidatas[0]
        
        # Critério 4: Menor duração
        min_duracao = min(t['duracao'] for t in candidatas)
        candidatas = [t for t in candidatas if t['duracao'] == min_duracao]
        if len(candidatas) == 1:
            return candidatas[0]
        
        # Critério 5: Sorteio
        self.ultimo_sorteio = True
        print(f"Desempate por sorteio entre: {[t['id'] for t in candidatas]}")
        return random.choice(candidatas)

    def deve_preemptar(self, tarefa_atual: TCB) -> bool:
        """Verifica se a tarefa atual deve ser preemptada por alguma tarefa na fila de prontas."""
        if not self.fila_tarefas_prontas:
            return False
        if self.nome_escalonador in ["fifo", "rr"]:
            return False
        elif self.nome_escalonador == "srtf":
            menor_tempo = min(t['tempo_restante'] for t in self.fila_tarefas_prontas)
            return menor_tempo < tarefa_atual['tempo_restante']
        elif self.nome_escalonador == "priop":
            maior_prioridade = max(t['prioridade'] for t in self.fila_tarefas_prontas)
            return maior_prioridade > tarefa_atual['prioridade']
        elif self.nome_escalonador == "priopenv":
            # NÃO aplica envelhecimento aqui - isso é feito no sistema_operacional
            # Apenas verifica se alguma tarefa tem prioridade dinâmica maior
            maior_prioridade_din = max(t['prioridade_dinamica'] for t in self.fila_tarefas_prontas)
            return maior_prioridade_din > tarefa_atual['prioridade_dinamica']

        return False

    def fifo(self):
        """Algoritmo FIFO/RR (First In, First Out / Round Robin):"""
        if self.fila_tarefas_prontas:
            tarefa = self.fila_tarefas_prontas.pop(0)  # Remove do início (índice 0)
            return tarefa
        return None

    def srtf(self):
        """
        Algoritmo SRTF (Shortest Remaining Time First): Escolhe a tarefa com MENOR tempo restante.
        Desempate: (1) tarefa já executando, (2) ingresso mais antigo, (3) menor duração, (4) sorteio
        """
        if not self.fila_tarefas_prontas:
            return None
        
        # Encontra o menor tempo restante
        menor_tempo = min(t['tempo_restante'] for t in self.fila_tarefas_prontas)
        candidatas = [t for t in self.fila_tarefas_prontas if t['tempo_restante'] == menor_tempo]
        
        # Aplica regras de desempate
        tarefa_escolhida = self._desempatar(candidatas, usar_prioridade_estatica=False)
        self.fila_tarefas_prontas.remove(tarefa_escolhida)
        return tarefa_escolhida

    def prioridade_preemptiva(self):
        """
        Algoritmo de Prioridade Preemptiva (PRIOp):
        Escolhe a tarefa com MAIOR prioridade (maior número = maior prioridade).
        Desempate: (1) tarefa já executando, (2) ingresso mais antigo, (3) menor duração, (4) sorteio
        """
        if not self.fila_tarefas_prontas:
            return None
        
        # Encontra a maior prioridade
        maior_prioridade = max(t['prioridade'] for t in self.fila_tarefas_prontas)
        candidatas = [t for t in self.fila_tarefas_prontas if t['prioridade'] == maior_prioridade]
        
        # Aplica regras de desempate (sem usar prioridade estática pois já é o critério principal)
        tarefa_escolhida = self._desempatar(candidatas, usar_prioridade_estatica=False)
        self.fila_tarefas_prontas.remove(tarefa_escolhida)
        return tarefa_escolhida
    
    def prioridade_envelhecimento(self):
        """
        Algoritmo de Prioridade com Envelhecimento (PRIOpENV):
        Escolhe a tarefa com MAIOR prioridade dinâmica.
        Desempate: (1) maior prioridade estática, (2) tarefa já executando, (3) ingresso mais antigo, (4) menor duração, (5) sorteio
        Reseta a prioridade dinâmica da tarefa escolhida para a prioridade estática.
        """
        if not self.fila_tarefas_prontas:
            return None
        
        # Encontra a maior prioridade dinâmica
        maior_prioridade_din = max(t['prioridade_dinamica'] for t in self.fila_tarefas_prontas)
        candidatas = [t for t in self.fila_tarefas_prontas if t['prioridade_dinamica'] == maior_prioridade_din]
        
        # Aplica regras de desempate (usa prioridade estática como primeiro critério)
        tarefa_escolhida = self._desempatar(candidatas, usar_prioridade_estatica=True)
        self.fila_tarefas_prontas.remove(tarefa_escolhida)
        
        # Reseta a prioridade dinâmica para a prioridade estática
        tarefa_escolhida['prioridade_dinamica'] = tarefa_escolhida['prioridade']
        
        return tarefa_escolhida
    
    def get_preempcao_chegada(self) -> bool:
        return self.nome_escalonador in ["srtf", "priop", "priopenv"]
    
    def get_preempcao_quantum(self) -> bool:
        # PRIOPEnv também usa quantum para limitar tempo de execução contínua
        return self.nome_escalonador in ["fifo", "rr", "priopenv"]
    
    def aplicar_envelhecimento(self):
        """Aplica envelhecimento (aging) a todas as tarefas na fila de prontas.
        Deve ser chamado uma vez por tick pelo sistema operacional."""
        if self.nome_escalonador == "priopenv":
            for tarefa in self.fila_tarefas_prontas:
                tarefa['prioridade_dinamica'] += self.alpha
    
    def houve_sorteio(self) -> bool:
        """Retorna True se o último escalonamento foi decidido por sorteio."""
        return self.ultimo_sorteio