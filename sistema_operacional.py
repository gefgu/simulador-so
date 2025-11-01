# Classe do Sistema Operacional

# INICIALIZAÇÃO DO SISTEMA OPERACIONAL

# Acontece depois do usuário clicar em "Iniciar Simulação"
# Lê o arquivo de configuração (e prepara as estruturas de dados para a simulação)
# Inicializa o relógio do sistema em 0


# LEITURA DA CONFIGURAÇÃO
# Define escalonador do sistema
# Define quantum do sistema
# Cria as TCBs das tarefas a partir dos dados lidos no arquivo de configuração
# Para facilitar, armazena as TCBs em um dict {ingresso: [TCBs que começam nesse ingresso]}


# FUNÇÕES DO SISTEMA OPERACIONAL

# EXECUTAR UM TICK DE RELÓGIO
# Adiciona as tarefas ingressadas na fila de prontas
# Verifica se uma tarefa foi de suspensa para o pronta (IO, Mutex) (se sim, adiciona na fila de prontas) -> PLACEHOLDER por enquanto
# Se houver uma nova tarefa ou acabar o quantum, manda para o algoritmo de escalonamento selecionado
# Atualiza o relógio do sistema em +1 
# Conta a tarefa em execução como tendo sido executada por 1 unidade de tempo
# Verifica se a tarefa em execução terminou (se sim, remove da fila de prontas)

# RETORNAR TAREFAS INGRESSADAS
# Retorna a lista de tarefas que já ingressaram no sistema (com base no relógio do sistema)


# OBSERVAÇÕES
# A fila (ou heap) de tarefas prontas será gerenciada pelo escalonador.

from config_handler import read_config
from escalonador import Escalonador
from tcb import TCB


class SistemaOperacional:
    def __init__(self, config_file: str):
        self.relogio = 0 # Inicializa o relógio do sistema
        self.quantum_atual = 0 # Contador do quantum atual
        self.nome_escalonador = "FIFO" # Tipo de escalonador (para ser definido na leitura do arquivo, padrão FIFO)
        self.quantum = 1 # Quantum do sistema (para ser definido na leitura do arquivo, padrão 1)
        self.tarefas: list[TCB] = [] # Lista de TCBs
        self.tarefa_executando: TCB | None = None # Tarefa que está em execução no momento
        self.tarefas_finalizadas: list[TCB] = [] # Lista de TCBs finalizadas
        self.chama_escalonador_entrada = False # Flag para chamar o escalonador quando uma nova tarefa entra

        dados_config = read_config(config_file)
        self.nome_escalonador = dados_config["nome_escalonador"]
        self.quantum = dados_config["quantum"]
        self.tarefas = dados_config["tarefas"]

        self.tarefas_no_ingresso = {}
        for tarefa in self.tarefas:
            if tarefa["ingresso"] not in self.tarefas_no_ingresso:
                self.tarefas_no_ingresso[tarefa["ingresso"]] = []
            self.tarefas_no_ingresso[tarefa["ingresso"]].append(tarefa)

        self.escalonador = Escalonador(self.nome_escalonador)
        self.tarefa_executando: TCB | None = None
        self.tarefas_finalizadas: list[TCB] = []

        # Define quais algoritmos causam preempção na CHEGADA de uma nova tarefa
        self.preempcao_por_chegada = self.nome_escalonador in ["srtf", "priop", "prioridade"]
        self.preempcao_por_quantum = self.nome_escalonador in ["fifo"]  # Round Robin é uma variação do FIFO

    def executar_tick(self):
        # 1. Adiciona novas tarefas que chegaram neste tick
        if self.relogio in self.tarefas_no_ingresso:
            novas_tarefas = self.tarefas_no_ingresso[self.relogio]
            for tarefa in novas_tarefas:
                self.escalonador.adicionar_tarefa_pronta(tarefa)
            
            # Verifica se alguma nova tarefa deve preemptar a atual (SRTF e Prioridade)
            if self.tarefa_executando and self.preempcao_por_chegada:
                deve_preemptar = False
                
                if self.nome_escalonador == "srtf":
                    # SRTF: preempta se há tarefa com menor tempo restante
                    menor_tempo_fila = min(self.escalonador.fila_tarefas_prontas, key=lambda t: t['tempo_restante'])['tempo_restante']
                    deve_preemptar = menor_tempo_fila < self.tarefa_executando['tempo_restante']
                    
                elif self.nome_escalonador == "priop":
                    # Prioridade: preempta se há tarefa com maior prioridade
                    maior_prioridade_fila = max(self.escalonador.fila_tarefas_prontas, key=lambda t: t['prioridade'])['prioridade']
                    deve_preemptar = maior_prioridade_fila > self.tarefa_executando['prioridade']
                
                if deve_preemptar:
                    # Preempção: coloca tarefa atual de volta na fila
                    self.escalonador.adicionar_tarefa_pronta(self.tarefa_executando)
                    self.tarefa_executando = None

        # 2. Se não há tarefa executando, chama o escalonador para escolher a próxima
        if self.tarefa_executando is None:
            self.tarefa_executando = self.escalonador.escalonar()
            self.quantum_atual = 0 # Reseta o quantum para a nova tarefa

        # 3. Se ainda assim não houver tarefa (fila vazia), apenas avança o relógio
        if self.tarefa_executando is None:
            self.relogio += 1
            return

        # 4. Executa a tarefa atual por um tick
        self.tarefa_executando["tempos_de_execucao"].append(self.relogio)
        if "tempo_restante" in self.tarefa_executando: # Para SRTF
             self.tarefa_executando["tempo_restante"] -= 1
        
        self.quantum_atual += 1

        # 5. Verifica se a tarefa terminou
        duracao_executada = len(self.tarefa_executando["tempos_de_execucao"])
        if duracao_executada >= self.tarefa_executando["duracao"]:
            print(f"Tarefa {self.tarefa_executando['id']} terminou.")
            self.tarefas_finalizadas.append(self.tarefa_executando)
            self.tarefa_executando = None # Libera a CPU
        
        # 6. Se não terminou, verifica se o quantum estourou (preempção do Round Robin)
        elif self.quantum_atual >= self.quantum and self.preempcao_por_quantum:
            self.escalonador.adicionar_tarefa_pronta(self.tarefa_executando)
            self.tarefa_executando = None # Libera a CPU para o próximo
            self.quantum_atual = 0

        # 7. Avança o relógio do sistema
        self.relogio += 1

    def get_tarefas_ingressadas(self) -> list[TCB]:
        return [tarefa for tarefa in self.tarefas if tarefa["ingresso"] <= self.relogio] # Quais Tarefas já ingressaram no sistema

    def get_relogio(self) -> int:
        return self.relogio
    
    def simulacao_terminada(self) -> bool:
        return len(self.tarefas_finalizadas) == len(self.tarefas)
    
    def get_tarefa_executando(self) -> TCB | None:
        return self.tarefa_executando