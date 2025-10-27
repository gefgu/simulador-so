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
    tipo: str
    inicio: int
    duracao: int

class TCB(TypedDict):
    id: str
    cor: str
    ingresso: int
    duracao: int
    prioridade: int
    tempos_de_execucao: list[int]
    lista_eventos: list[Evento]  # Lista de dicionários (tipo, inicio, duracao)

