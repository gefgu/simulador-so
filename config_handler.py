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
        parts = [p for p in parts if p.strip()]
        duracao_tarefa = int(parts[3])
        tam_config = len(parts)
        lista_eventos = []
        if tam_config > 5:
            for i in range(5, tam_config):
                evento_str = parts[i].strip()
                print(evento_str)
                
                # Verifica o tipo de evento
                if evento_str.startswith("IO"):
                    # Formato: IO:xx-yy (inicio-duracao)
                    evento_name = "IO"
                    evento_info = evento_str.split(':')[1].split('-')
                    evento = {
                        "tipo": evento_name,
                        "inicio": int(evento_info[0]),
                        "duracao": int(evento_info[1]),
                        "tempo_restante": int(evento_info[1]),
                        "mutex_id": -1,  # Não aplicável para IO
                    }
                elif evento_str.startswith("ML"):
                    # Formato: MLxx:00 (mutex_id:tempo)
                    # Extrai o ID do mutex (após "ML" e antes de ":")
                    evento_name = "ML"
                    partes = evento_str[2:].split(':')  # Remove "ML" do início
                    mutex_id = int(partes[0])
                    inicio = int(partes[1])
                    evento = {
                        "tipo": evento_name,
                        "inicio": inicio,
                        "duracao": 0,
                        "tempo_restante": 0,
                        "mutex_id": mutex_id,
                    }
                elif evento_str.startswith("MU"):
                    # Formato: MUxx:00 (mutex_id:tempo)
                    # Extrai o ID do mutex (após "MU" e antes de ":")
                    evento_name = "MU"
                    partes = evento_str[2:].split(':')  # Remove "MU" do início
                    mutex_id = int(partes[0])
                    inicio = int(partes[1])
                    evento = {
                        "tipo": evento_name,
                        "inicio": inicio,
                        "duracao": 0,
                        "tempo_restante": 0,
                        "mutex_id": mutex_id,
                    }
                else:
                    # Formato antigo genérico (fallback)
                    evento_name = evento_str.split(':')[0]
                    evento_info = evento_str.split(':')[1].split('-')
                    evento = {
                        "tipo": evento_name,
                        "inicio": int(evento_info[0]),
                        "duracao": int(evento_info[1]),
                        "tempo_restante": int(evento_info[1]),
                        "mutex_id": -1,
                    }
                    
                print(f"Evento parsed: {evento}")
                lista_eventos.append(evento)
        prioridade_tarefa = int(parts[4])
        tarefa = TCB(
            id=parts[0],
            cor=parts[1],
            ingresso=int(parts[2]),
            duracao=duracao_tarefa,
            prioridade=prioridade_tarefa,
            prioridade_dinamica=prioridade_tarefa,  # Inicializa com a prioridade estática
            tempo_restante=duracao_tarefa, # Importante para SRTF
            tempos_de_execucao=[],
            lista_eventos=lista_eventos,
            evento_io_ativo=None,  # Nenhum evento de I/O ativo inicialmente
        )
        tarefas.append(tarefa)
    

    return {
        "nome_escalonador": nome_escalonador,
        "quantum": quantum,
        "alpha": alpha,
        "tarefas": tarefas
    }