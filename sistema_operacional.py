# Classe do Sistema Operacional
from config_handler import read_config
from escalonador import Escalonador
from tcb import TCB


class SistemaOperacional:
    def __init__(self, config_file: str):
        """Inicializa o sistema operacional lendo a configuração do arquivo e adicionando todas as variáveis necessárias."""

        self.relogio = 0 # Inicializa o relógio do sistema
        self.quantum_atual = 0 # Contador do quantum atual
        self.nome_escalonador = "FIFO" # Tipo de escalonador (para ser definido na leitura do arquivo, padrão FIFO)
        self.quantum = 1 # Quantum do sistema (para ser definido na leitura do arquivo, padrão 1)
        self.tarefas: list[TCB] = [] # Lista de TCBs
        self.tarefa_executando: TCB | None = None # Tarefa que está em execução no momento
        self.tarefas_finalizadas: list[TCB] = [] # Lista de TCBs finalizadas
        self.chama_escalonador_entrada = False # Flag para chamar o escalonador quando uma nova tarefa entra
        self.ultima_tarefa_executada: TCB | None = None # Última tarefa que foi executada (para visualização)
        self.alpha = 1  # Fator de envelhecimento (para algoritmos que o utilizam)

        try: 
            dados_config = read_config(config_file)
        except Exception as e:
            raise Exception(f"Erro ao ler o arquivo de configuração: {e}")


        # print(dados_config)
        self.nome_escalonador = dados_config["nome_escalonador"]
        self.quantum = dados_config["quantum"]
        self.tarefas = dados_config["tarefas"]
        self.alpha = dados_config["alpha"]

        # Organiza as tarefas por tempo de ingresso para facilitar a adição ao sistema
        self.tarefas_no_ingresso = {}
        for tarefa in self.tarefas:
            if tarefa["ingresso"] not in self.tarefas_no_ingresso:
                self.tarefas_no_ingresso[tarefa["ingresso"]] = []
            self.tarefas_no_ingresso[tarefa["ingresso"]].append(tarefa)

        # Inicializa o escalonador
        self.escalonador = Escalonador(self.nome_escalonador, alpha=self.alpha)
        self.tarefa_executando: TCB | None = None
        self.tarefas_finalizadas: list[TCB] = []
        self.fila_IO: list[TCB] = []

        # Define quais algoritmos causam preempção na CHEGADA de uma nova tarefa
        self.preempcao_por_chegada = self.escalonador.get_preempcao_chegada()
        self.preempcao_por_quantum = self.escalonador.get_preempcao_quantum()

    def executar_tick(self):
        if self.fila_IO:
            # Verifica se alguma tarefa na fila de I/O terminou seu evento
            tarefas_IO_concluidas = []
            for tarefa_io in self.fila_IO:
                for evento in tarefa_io["lista_eventos"]:
                    if evento["tipo"] == "IO" and evento["tempo_restante"] > 0:
                        tempo_restante = evento["tempo_restante"] - 1
                        if tempo_restante <= 0:
                            tarefas_IO_concluidas.append(tarefa_io)
                            break
                        break  # Só processa um evento por tick
                break  # Só processa uma tarefa de I/O por tick
            
            for tarefa_concluida in tarefas_IO_concluidas:
                self.fila_IO.remove(tarefa_concluida)
                self.escalonador.adicionar_tarefa_pronta(tarefa_concluida)

        # 1. Adiciona novas tarefas que chegaram neste tick
        if self.relogio in self.tarefas_no_ingresso:
            novas_tarefas = self.tarefas_no_ingresso[self.relogio]
            for tarefa in novas_tarefas:
                self.escalonador.adicionar_tarefa_pronta(tarefa)
            
        # Verifica se alguma nova tarefa deve preemptar a atual (SRTF e Prioridade)
        if self.tarefa_executando and self.preempcao_por_chegada:
            deve_preemptar = self.escalonador.deve_preemptar(self.tarefa_executando)

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
            if self.tarefa_executando["lista_eventos"]:
                for evento in self.tarefa_executando["lista_eventos"]:
                    if evento["tipo"] == "IO":
                        inicio_evento = evento["inicio"]
                        if len(self.tarefa_executando["tempos_de_execucao"]) == inicio_evento:
                            # Move a tarefa para a fila de I/O
                            self.fila_IO.append(self.tarefa_executando)
                            self.tarefa_executando = None
                            self.quantum_atual = 0
                            self.relogio += 1
                            return
        
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
    
    