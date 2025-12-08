# TASK CONTROL BLOCK (TCB)

# Deve conter
# - ID da tarefa
# - Cor da tarefa
# - Tempo de ingresso
# - Duração total
# - Prioridade
# - Uma lista com os momentos que a tarefa foi executada
# - Lista de Eventos

from typing import TypedDict


class Evento(TypedDict):
    tipo: str  # "IO", "ML" (Mutex Lock), "MU" (Mutex Unlock)
    inicio: int
    duracao: int  # Para IO; para ML/MU é 0
    tempo_restante: int  # Para IO; para ML/MU é 0
    mutex_id: int  # ID do mutex (apenas para ML e MU)

class TCB(TypedDict):
    id: str
    cor: str
    ingresso: int
    duracao: int
    prioridade: int
    prioridade_dinamica: int
    tempo_restante: int
    tempos_de_execucao: list[int]
    lista_eventos: list[Evento]  # Lista de dicionários (tipo, inicio, duracao)
    evento_io_ativo: Evento | None  # Evento de I/O atualmente em processamento

