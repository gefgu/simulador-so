
def get_config_values(config_file: str):
    """
    Reads a configuration file and returns in a dict:
        - "escalonador":
        - "quantum"
        - tarefas (lista de dicionários)
        id;cor;ingresso;duracao;prioridade;lista_eventos
          - "id"
          - cor (string em hexadecimal)
          - ingresso
          - duracao
          - prioridade
          - lista_eventos (lista de dicionários)
            - tipo
            - inicio
            - duracao
        

    Args:
        config_file (str): Path to the configuration file.
    """

    config_values = {
        "escalonador": None,
        "quantum": None,
        "tarefas": []
    }

    with open(config_file, 'r') as file:
        lines = file.readlines()

    # Read escalonador and quantum
    config_values["escalonador"] = lines[0].split(";")[0].strip()
    config_values["quantum"] = int(lines[0].split(";")[1].strip())

    # Read tasks
    for line in lines[1:]:
        parts = line.strip().split(';')
        tarefa = {
            "id": parts[0],
            "cor": parts[1],
            "ingresso": int(parts[2]),
            "duracao": int(parts[3]),
            "prioridade": int(parts[4]),
            "lista_eventos": []
        }

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

        config_values["tarefas"].append(tarefa)

    return config_values