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

        # Estrutura para gerenciar Mutexes
        # Formato: {mutex_id: {"dono": TCB | None, "fila_espera": list[TCB]}}
        self.mutexes: dict[int, dict] = {}

        # Rastreia em quais ticks houve sorteio para desempate
        self.ticks_com_sorteio: set[int] = set()

        # Define quais algoritmos causam preempção na CHEGADA de uma nova tarefa
        self.preempcao_por_chegada = self.escalonador.get_preempcao_chegada()
        self.preempcao_por_quantum = self.escalonador.get_preempcao_quantum()

    def _obter_ou_criar_mutex(self, mutex_id: int) -> dict:
        """Obtém um mutex existente ou cria um novo se não existir."""
        if mutex_id not in self.mutexes:
            self.mutexes[mutex_id] = {"dono": None, "fila_espera": []}
        return self.mutexes[mutex_id]

    def _solicitar_mutex(self, tarefa: TCB, mutex_id: int) -> bool:
        """
        Tenta adquirir o mutex para a tarefa.
        Retorna True se o mutex foi adquirido, False se a tarefa foi bloqueada.
        """
        mutex = self._obter_ou_criar_mutex(mutex_id)
        
        if mutex["dono"] is None:
            # Mutex está livre, a tarefa pode adquirir
            mutex["dono"] = tarefa
            print(f"Tarefa {tarefa['id']} adquiriu mutex {mutex_id}")
            return True
        elif mutex["dono"]["id"] == tarefa["id"]:
            # A tarefa já possui o mutex (reentrância - opcional, mas seguro)
            print(f"Tarefa {tarefa['id']} já possui mutex {mutex_id}")
            return True
        else:
            # Mutex está ocupado, bloqueia a tarefa
            mutex["fila_espera"].append(tarefa)
            print(f"Tarefa {tarefa['id']} bloqueada aguardando mutex {mutex_id} (dono: {mutex['dono']['id']})")
            return False

    def _liberar_mutex(self, tarefa: TCB, mutex_id: int):
        """
        Libera o mutex e acorda a próxima tarefa na fila de espera, se houver.
        """
        mutex = self._obter_ou_criar_mutex(mutex_id)
        
        if mutex["dono"] is None:
            print(f"Aviso: Tarefa {tarefa['id']} tentou liberar mutex {mutex_id} que já está livre")
            return
        
        if mutex["dono"]["id"] != tarefa["id"]:
            print(f"Aviso: Tarefa {tarefa['id']} tentou liberar mutex {mutex_id} que pertence a {mutex['dono']['id']}")
            return
        
        print(f"Tarefa {tarefa['id']} liberou mutex {mutex_id}")
        
        if mutex["fila_espera"]:
            # Acorda a próxima tarefa na fila de espera
            proxima_tarefa = mutex["fila_espera"].pop(0)
            mutex["dono"] = proxima_tarefa
            print(f"Tarefa {proxima_tarefa['id']} acordada e adquiriu mutex {mutex_id}")
            # Coloca a tarefa de volta na fila de prontas
            self.escalonador.adicionar_tarefa_pronta(proxima_tarefa)
        else:
            # Ninguém esperando, libera o mutex
            mutex["dono"] = None

    def _processar_eventos_mutex(self, tarefa: TCB, tempo_execucao_tarefa: int) -> bool:
        """
        Processa eventos de mutex (ML e MU) para o tempo de execução atual.
        Retorna True se a tarefa foi bloqueada, False caso contrário.
        """
        if not tarefa["lista_eventos"]:
            return False
        
        tarefa_bloqueada = False
        
        for evento in tarefa["lista_eventos"]:
            if evento["inicio"] == tempo_execucao_tarefa:
                if evento["tipo"] == "ML":
                    # Solicitar mutex
                    if not self._solicitar_mutex(tarefa, evento["mutex_id"]):
                        # Tarefa foi bloqueada
                        tarefa_bloqueada = True
                        break  # Não processa mais eventos se bloqueou
                elif evento["tipo"] == "MU":
                    # Liberar mutex
                    self._liberar_mutex(tarefa, evento["mutex_id"])
        
        return tarefa_bloqueada

    def _escalonar(self):
        """Chama o escalonador para escolher a próxima tarefa a executar."""
        self.escalonador.set_tarefa_atual(self.tarefa_executando)
        self.tarefa_executando = self.escalonador.escalonar()
        self.quantum_atual = 0
        
        # Registra se houve sorteio neste tick
        if self.escalonador.houve_sorteio():
            self.ticks_com_sorteio.add(self.relogio)

    def executar_tick(self):
        # 0. Processa todas as tarefas na fila de I/O
        tarefas_voltaram_de_io = False
        if self.fila_IO:
            tarefas_IO_concluidas = []
            for tarefa_io in self.fila_IO:
                evento = tarefa_io.get("evento_io_ativo")
                if evento and evento["tempo_restante"] > 0:
                    evento["tempo_restante"] -= 1
                    if evento["tempo_restante"] <= 0:
                        tarefa_io["evento_io_ativo"] = None
                        tarefas_IO_concluidas.append(tarefa_io)
            
            for tarefa_concluida in tarefas_IO_concluidas:
                self.fila_IO.remove(tarefa_concluida)
                self.escalonador.adicionar_tarefa_pronta(tarefa_concluida)
                tarefas_voltaram_de_io = True

        # 1. Adiciona novas tarefas que chegaram neste tick
        novas_tarefas_chegaram = False
        if self.relogio in self.tarefas_no_ingresso:
            novas_tarefas = self.tarefas_no_ingresso[self.relogio]
            novas_tarefas_chegaram = len(novas_tarefas) > 0
            for tarefa in novas_tarefas:
                tarefa['prioridade_dinamica'] = tarefa['prioridade']
                self.escalonador.adicionar_tarefa_pronta(tarefa)
        
        # 2. Verifica preempção por chegada (SRTF, PRIOP, PRIOPEnv)
        if self.tarefa_executando and self.preempcao_por_chegada:
            verificar_preempcao = novas_tarefas_chegaram or tarefas_voltaram_de_io
            
            if verificar_preempcao:
                deve_preemptar = self.escalonador.deve_preemptar(self.tarefa_executando)
                if deve_preemptar:
                    self.escalonador.adicionar_tarefa_pronta(self.tarefa_executando)
                    self.tarefa_executando = None
                    self._escalonar()  # Chama escalonador após preempção

        # 3. Se não há tarefa executando, chama o escalonador
        if self.tarefa_executando is None:
            self._escalonar()

        # 3. Se ainda assim não houver tarefa (fila vazia), apenas avança o relógio
        if self.tarefa_executando is None:
            self.relogio += 1
            return

        # 4. Executa a tarefa atual por um tick
        self.tarefa_executando["tempos_de_execucao"].append(self.relogio)
        if "tempo_restante" in self.tarefa_executando: # Para SRTF
            self.tarefa_executando["tempo_restante"] -= 1
        
        # Calcula o tempo de execução relativo da tarefa (para eventos)
        tempo_execucao_tarefa = len(self.tarefa_executando["tempos_de_execucao"])
        
        # 5.1 Processa eventos de mutex (ML e MU)
        if self.tarefa_executando["lista_eventos"]:
            tarefa_bloqueada_mutex = self._processar_eventos_mutex(self.tarefa_executando, tempo_execucao_tarefa)
            
            if tarefa_bloqueada_mutex:
                # Tarefa foi bloqueada aguardando mutex
                self.tarefa_executando = None
                self.quantum_atual = 0
                self._escalonar()  # Chama escalonador após bloqueio por mutex
                self.relogio += 1
                return
        
        # 5.2 Processa eventos de I/O
        if self.tarefa_executando["lista_eventos"]:
            for evento in self.tarefa_executando["lista_eventos"]:
                if evento["tipo"] == "IO":
                    inicio_evento = evento["inicio"]
                    if tempo_execucao_tarefa == inicio_evento:
                        self.tarefa_executando["evento_io_ativo"] = evento
                        self.fila_IO.append(self.tarefa_executando)
                        self.tarefa_executando = None
                        self.quantum_atual = 0
                        self._escalonar()  # Chama escalonador após I/O
                        self.relogio += 1
                        return
        
        self.quantum_atual += 1

        # 6. Verifica se a tarefa terminou
        duracao_executada = len(self.tarefa_executando["tempos_de_execucao"])
        if duracao_executada >= self.tarefa_executando["duracao"]:
            print(f"Tarefa {self.tarefa_executando['id']} terminou.")
            self.tarefas_finalizadas.append(self.tarefa_executando)
            self.tarefa_executando = None
            self._escalonar()  # Chama escalonador após término
        
        # 7. Se não terminou, verifica se o quantum estourou
        elif self.quantum_atual >= self.quantum and self.preempcao_por_quantum:
            self.escalonador.adicionar_tarefa_pronta(self.tarefa_executando)
            self.tarefa_executando = None
            self.quantum_atual = 0
            self._escalonar()  # Chama escalonador após quantum

        # 8. Aplica envelhecimento a todas as tarefas na fila de prontas
        self.escalonador.aplicar_envelhecimento()

        # 9. Avança o relógio do sistema
        self.relogio += 1

    def get_tarefas_ingressadas(self) -> list[TCB]:
        return [tarefa for tarefa in self.tarefas if tarefa["ingresso"] <= self.relogio] # Quais Tarefas já ingressaram no sistema

    def get_relogio(self) -> int:
        return self.relogio
    
    def simulacao_terminada(self) -> bool:
        return len(self.tarefas_finalizadas) == len(self.tarefas)
    
    def get_tarefa_executando(self) -> TCB | None:
        return self.tarefa_executando
    
    