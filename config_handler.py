from tcb import TCB


def read_config(config_file):
    # Lê o arquivo de configuração e retorna um dicionário com os dados
    with open(config_file, 'r') as file:
        lines = file.readlines()

    # Processa a primeira linha para obter o nome do escalonador e o quantum
    nome_escalonador = lines[0].split(";")[0].strip().lower()
    quantum = int(lines[0].split(";")[1].strip())
    try:
        alpha = int(lines[0].split(";")[2].strip())
    except IndexError:
        alpha = 1


    # Processa as linhas seguintes para obter as tarefas
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
            lista_eventos=[],
        )
        tarefas.append(tarefa)
    

    return {
        "nome_escalonador": nome_escalonador,
        "quantum": quantum,
        "alpha": alpha,
        "tarefas": tarefas
    }