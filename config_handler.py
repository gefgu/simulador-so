from tcb import TCB


def read_config(config_file):

    with open(config_file, 'r') as file:
        lines = file.readlines()

    nome_escalonador = lines[0].split(";")[0].strip().lower()
    quantum = int(lines[0].split(";")[1].strip())

    tarefas: list[TCB] = []
    for line in lines[1:]:
        parts = line.strip().split(';')
        duracao_tarefa = int(parts[3])
        tarefa = TCB(
            id=parts[0],
            cor=parts[1],
            ingresso=int(parts[2]),
            duracao=duracao_tarefa,
            prioridade=int(parts[4]),
            tempo_restante=duracao_tarefa, # Importante para SRTF
            tempos_de_execucao=[],
            lista_eventos=[]
        )
        tarefas.append(tarefa)
    

    return {
        "nome_escalonador": nome_escalonador,
        "quantum": quantum,
        "tarefas": tarefas
    }