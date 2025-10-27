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

        with open(config_file, 'r') as file:
            lines = file.readlines()

        # Lê escalonador e quantum no início do arquivo
        self.nome_escalonador = lines[0].split(";")[0].strip()
        self.quantum = int(lines[0].split(";")[1].strip())

        # Lê tarefas
        for line in lines[1:]:
            parts = line.strip().split(';')
            tarefa = TCB(
                id=parts[0],
                cor=parts[1],
                ingresso=int(parts[2]),
                duracao=int(parts[3]),
                prioridade=int(parts[4]),
                tempos_de_execucao=[],
                lista_eventos=[]
            )
            print(tarefa)

            eventos_str = parts[5] if len(parts) > 5 else ""
            if eventos_str:
                eventos_parts = eventos_str.split(';')
                for evento_str in eventos_parts:
                    evento_details = evento_str.split(':')
                    evento = {
                        "tipo": evento_details[0],
                        "inicio": int(evento_details[1].split('-')[0]),
                        "duracao": int(evento_details[1].split('-')[1])
                    }
                    tarefa["lista_eventos"].append(evento)

            self.tarefas.append(tarefa)

        # Para facilitar, armazena as TCBs em um dict {ingresso: [TCBs que começam nesse ingresso]}
        self.tarefas_no_ingresso = {}
        for tarefa in self.tarefas:
            if tarefa["ingresso"] not in self.tarefas_no_ingresso:
                self.tarefas_no_ingresso[tarefa["ingresso"]] = []
            self.tarefas_no_ingresso[tarefa["ingresso"]].append(tarefa)

        # Inicializa escalonador
        self.escalonador = Escalonador(self.nome_escalonador)

    def executar_tick(self):
        tarefa_foi_adicionada = False

        # Adiciona as tarefas ingressadas na fila de prontas
        if self.relogio in self.tarefas_no_ingresso: # Tem tarefa que começa nesse momento?
            
            tarefa_foi_adicionada = True
            for tarefa in self.tarefas_no_ingresso[self.relogio]:
                self.escalonador.adicionar_tarefa_pronta(tarefa)

            if (self.tarefa_executando is not None) and (self.chama_escalonador_entrada): # Se tiver uma tarefa em execução, coloca de volta na fila de prontas
                self.escalonador.adicionar_tarefa_pronta(self.tarefa_executando)
                self.tarefa_executando = None

        # PLACEHOLDER: Verifica se uma tarefa foi de suspensa (IO, Mutex) para o pronta (se sim, adiciona na fila de prontas)

        # Se houver uma nova tarefa ou acabar o quantum, manda para o algoritmo de escalonamento selecionado
        # (IMPLEMENTAR ALGORITMOS DE ESCALONAMENTO AQUI)
        if (tarefa_foi_adicionada and self.chama_escalonador_entrada) or (self.quantum_atual == 0):
            self.tarefa_executando = self.escalonador.escalonar()
            self.quantum_atual = 0

        if self.tarefa_executando is None:
            # Nenhuma tarefa para executar nesse tick
            self.relogio += 1
            self.quantum_atual = 0
            return

        # Conta a tarefa em execução como tendo sido executada por 1 unidade de tempo
        # (IMPLEMENTAR CONTAGEM DE TEMPO DE EXECUÇÃO AQUI)
        self.tarefa_executando["tempos_de_execucao"].append(self.relogio)

        # Verifica se a tarefa terminou
        if len(self.tarefa_executando["tempos_de_execucao"]) >= self.tarefa_executando["duracao"]:
            print(f"Tarefa {self.tarefa_executando['id']} terminou.")
            self.tarefas_finalizadas.append(self.tarefa_executando)
            self.tarefa_executando = None
            self.quantum_atual = 0  # Reset quantum
        else:
            # Tarefa não terminou, incrementa quantum
            self.quantum_atual += 1
            
            # Se quantum acabou, coloca tarefa de volta no final da fila
            if self.quantum_atual >= self.quantum:
                self.escalonador.adicionar_tarefa_pronta(self.tarefa_executando)
                self.tarefa_executando = None
                self.quantum_atual = 0
        
        self.relogio += 1

    def get_tarefas_ingressadas(self) -> list[TCB]:
        return [tarefa for tarefa in self.tarefas if tarefa["ingresso"] <= self.relogio] # Quais Tarefas já ingressaram no sistema

    def get_relogio(self) -> int:
        return self.relogio
    
    def simulacao_terminada(self) -> bool:
        return len(self.tarefas_finalizadas) == len(self.tarefas)