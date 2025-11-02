import copy
import customtkinter
from sistema_operacional import SistemaOperacional
from gantt_diagram import GanttDiagram
import platform
import os
import subprocess
from datetime import datetime
from PIL import ImageGrab, Image  # type: ignore
import copy  # Importante para salvar o histórico de estados
from image_helper import convert_ps_to_png, convert_ps_to_png_pillow, convert_ps_to_png_pillow_with_white_bg, convert_ps_to_png_with_white_bg

class SimulacaoFrame(customtkinter.CTkFrame):
    def __init__(self, master, voltar_ao_menu_callback):
        super().__init__(master)

        self.voltar_ao_menu_callback = voltar_ao_menu_callback
        self.gantt_diagram = None
        self.sistema_operacional = None
        self.historico_estados = []  # Para guardar os "snapshots" da simulação

        # Widgets da tela de simulação (declarados aqui para fácil acesso)
        self.simulation_frame = None
        self.info_frame = None
        self.control_frame = None
        self.relogio_label = None
        self.algoritmo_label = None
        self.tarefa_exec_label = None
        self.prev_tick_button = None
        self.next_tick_button = None
        self.run_to_end_button = None


    def create_simulation_ui(self, config_file: str):
        self.sistema_operacional = SistemaOperacional(config_file)
        self.historico_estados = []  # Limpa o histórico para uma nova simulação

        # --- Construção da Interface de Simulação ---
        self.simulation_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.simulation_frame.pack(fill="both", expand=True)
        
        # -- 1. Frame de Informações (Topo) --
        self.info_frame = customtkinter.CTkFrame(self.simulation_frame, height=60)
        self.info_frame.pack(side="top", fill="x", padx=20, pady=(20, 0))

        self.relogio_label = customtkinter.CTkLabel(self.info_frame, text="Tick: 0", font=("Arial", 18))
        self.relogio_label.pack(side="left", padx=20)
        
        self.algoritmo_label = customtkinter.CTkLabel(self.info_frame, text=f"Algoritmo: {self.sistema_operacional.nome_escalonador.upper()}", font=("Arial", 18))
        self.algoritmo_label.pack(side="left", padx=20)
        
        self.tarefa_exec_label = customtkinter.CTkLabel(self.info_frame, text="Executando: Nenhuma", font=("Arial", 18))
        self.tarefa_exec_label.pack(side="left", padx=20)

        # -- 2. Frame Principal (Centro) - Split entre Gantt e Inspeção de TCBs --
        main_content_frame = customtkinter.CTkFrame(self.simulation_frame, fg_color="transparent")
        main_content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Frame esquerdo: Gantt Diagram
        self.gantt_frame = customtkinter.CTkFrame(main_content_frame)
        self.gantt_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Frame direito: Painel de Inspeção TCB
        self.tcb_panel_frame = customtkinter.CTkFrame(main_content_frame, width=400)
        self.tcb_panel_frame.pack(side="right", fill="y", padx=(10, 0))
        self.tcb_panel_frame.pack_propagate(False)  # Mantém largura fixa
        
        # Título do painel TCB
        tcb_title = customtkinter.CTkLabel(
            self.tcb_panel_frame, text="Inspeção de TCBs", font=("Arial", 20, "bold")
        )
        tcb_title.pack(pady=(10, 5))
        
        # Scrollable frame para as informações das tarefas
        self.tcb_scrollable = customtkinter.CTkScrollableFrame(
            self.tcb_panel_frame, label_text="Estado das Tarefas"
        )
        self.tcb_scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        # -- 3. Frame de Controles (Baixo) --
        self.control_frame = customtkinter.CTkFrame(self.simulation_frame)
        self.control_frame.pack(side="bottom", fill="x", padx=20, pady=20)

        buttons_frame = customtkinter.CTkFrame(self.control_frame)
        buttons_frame.pack(pady=10)
        
        # Botão: Voltar ao Menu
        reset_button = customtkinter.CTkButton(
            buttons_frame, text="Voltar ao Menu", font=("Arial", 18), width=200, height=50, command=self.resetar_simulacao
        )
        reset_button.pack(side="left", padx=10)

        # Botão: Regredir Tick
        self.prev_tick_button = customtkinter.CTkButton(
            buttons_frame, text="< Regredir Tick", font=("Arial", 18), width=200, height=50, command=self.tick_anterior, state="disabled"
        )
        self.prev_tick_button.pack(side="left", padx=10)

        # Botão: Próximo Tick
        self.next_tick_button = customtkinter.CTkButton(
            buttons_frame, text="Próximo Tick >", font=("Arial", 18), width=200, height=50, command=self.proximo_tick
        )
        self.next_tick_button.pack(side="left", padx=10)
        
        # Botão: Avançar até o Fim
        self.run_to_end_button = customtkinter.CTkButton(
            buttons_frame, text="Avançar até o Fim", font=("Arial", 18), width=200, height=50, command=self.avancar_ate_fim
        )
        self.run_to_end_button.pack(side="left", padx=10)

        # Botão: Salvar Imagem
        screenshot_button = customtkinter.CTkButton(
            buttons_frame, text="Salvar Imagem", font=("Arial", 18), width=200, height=50, command=self.take_screenshot
        )
        screenshot_button.pack(side="left", padx=10)

        # Inicia e exibe o estado inicial (tick 0)
        self.atualizar_diagrama()

    def proximo_tick(self):
        """Salva o estado atual, executa um tick e atualiza a UI."""
        if not self.sistema_operacional.simulacao_terminada():
            # Salva o estado ATUAL antes de executar o próximo tick
            try:
                self.historico_estados.append(copy.deepcopy(self.sistema_operacional)) # Adicionar um método que funcione com o Queue depois
            except Exception as e:
                print(f"Erro ao salvar estado para histórico: {e}")
            finally:
                self.sistema_operacional.executar_tick()
                self.atualizar_diagrama()

        # Atualiza o estado dos botões
        if self.sistema_operacional.simulacao_terminada():
            self.next_tick_button.configure(state="disabled")
            self.run_to_end_button.configure(state="disabled")
        
        self.prev_tick_button.configure(state="normal") # Sempre podemos regredir depois de avançar

    def tick_anterior(self):
        """Restaura o estado anterior do histórico e atualiza a UI."""
        if self.historico_estados:
            # Pega o último estado salvo e o restaura
            self.sistema_operacional = self.historico_estados.pop()
            self.atualizar_diagrama()

        # Atualiza o estado dos botões
        if not self.historico_estados:
            self.prev_tick_button.configure(state="disabled") # Desabilita se não há mais histórico
        
        self.next_tick_button.configure(state="normal") # Sempre podemos avançar depois de regredir
        self.run_to_end_button.configure(state="normal")

    def atualizar_diagrama(self):
        """Atualiza o diagrama de Gantt e todas as informações na tela."""
        so = self.sistema_operacional
        current_time = so.get_relogio()
        tarefas = so.get_tarefas_ingressadas()
        tarefa_executando = so.get_tarefa_executando()
        
        # Atualiza labels de informação
        self.relogio_label.configure(text=f"Tick: {current_time}")
        if tarefa_executando:
            self.tarefa_exec_label.configure(text=f"Executando: {tarefa_executando['id']}")
        else:
            self.tarefa_exec_label.configure(text="Executando: Nenhuma")

        # Recria o diagrama de Gantt no frame correto
        if self.gantt_diagram:
            self.gantt_diagram.destroy()

        self.gantt_diagram = GanttDiagram(self.gantt_frame, current_time, tarefas)
        self.gantt_diagram.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Atualiza o painel de inspeção de TCBs
        self.atualizar_painel_tcb()

    def avancar_ate_fim(self):
        """Executa a simulação até o fim, salvando cada passo no histórico."""
        while not self.sistema_operacional.simulacao_terminada():
            # Ainda salvamos o histórico para poder regredir passo a passo depois
            try:
                self.historico_estados.append(copy.deepcopy(self.sistema_operacional)) # Adicionar um método que funcione com o Queue depois
            except Exception as e:
                print(f"Erro ao salvar estado para histórico: {e}")
            finally:
                self.sistema_operacional.executar_tick()

        self.atualizar_diagrama()
        self.update() # Força a atualização da UI
        
        # Desabilita botões de avanço
        self.next_tick_button.configure(state="disabled")
        self.run_to_end_button.configure(state="disabled")
        self.prev_tick_button.configure(state="normal") # Garante que podemos regredir

    def resetar_simulacao(self):
        """Destrói a UI da simulação e volta para o menu principal."""
        if self.simulation_frame:
            self.simulation_frame.destroy()

        self.gantt_diagram = None
        self.sistema_operacional = None
        self.historico_estados = []
        
        self.voltar_ao_menu_callback()


    def atualizar_painel_tcb(self):
        """Atualiza o painel de inspeção das TCBs com informações em tempo real."""
        # Limpa o conteúdo anterior
        for widget in self.tcb_scrollable.winfo_children():
            widget.destroy()
        
        so = self.sistema_operacional
        tarefa_executando = so.get_tarefa_executando()
        fila_prontas = so.escalonador.fila_tarefas_prontas
        todas_tarefas = so.tarefas
        tarefas_finalizadas = so.tarefas_finalizadas
        
        # Função para determinar estado da tarefa
        def get_estado_tarefa(tarefa):
            if tarefa in tarefas_finalizadas:
                return "FINALIZADA", "#4CAF50"  # Verde
            elif tarefa == tarefa_executando:
                return "EXECUTANDO", "#2196F3"  # Azul
            elif tarefa in fila_prontas:
                return "PRONTA", "#FF9800"      # Laranja
            elif tarefa['ingresso'] <= so.relogio:
                return "INGRESSANDO", "#9C27B0"   # Roxo
            else:
                return "AGUARDANDO", "#757575"  # Cinza
        
        # Informações gerais do sistema
        info_frame = customtkinter.CTkFrame(self.tcb_scrollable)
        info_frame.pack(fill="x", padx=5, pady=5)
        
        info_label = customtkinter.CTkLabel(
            info_frame, 
            text=f"🕒 Tick: {so.relogio} | 🔧 {so.nome_escalonador.upper()}\n"
                 f"⚙️ Quantum: {so.quantum} | 🏃 Ativas: {len(fila_prontas)}\n"
                 f"✅ Finalizadas: {len(tarefas_finalizadas)}/{len(todas_tarefas)}",
            font=("Arial", 12, "bold"),
            justify="left"
        )
        info_label.pack(padx=10, pady=10)
        
        # Separador
        separator = customtkinter.CTkFrame(self.tcb_scrollable, height=2)
        separator.pack(fill="x", padx=5, pady=5)
        
        # Lista todas as tarefas com suas informações
        for tarefa in todas_tarefas:
            estado, cor = get_estado_tarefa(tarefa)
            
            # Frame principal da tarefa
            tarefa_frame = customtkinter.CTkFrame(
                self.tcb_scrollable, 
                fg_color=cor, 
                corner_radius=8
            )
            tarefa_frame.pack(fill="x", padx=5, pady=3)
            
            # Header da tarefa
            header_frame = customtkinter.CTkFrame(tarefa_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=5)
            
            task_id_label = customtkinter.CTkLabel(
                header_frame,
                text=f"📋 {tarefa['id']} ({estado})",
                font=("Arial", 14, "bold"),
                text_color="white"
            )
            task_id_label.pack(side="left")
            
            # Detalhes da tarefa
            details_text = f"⏰ Ingresso: {tarefa['ingresso']}\n"
            details_text += f"⏱️ Duração: {tarefa['duracao']}\n"
            details_text += f"⭐ Prioridade: {tarefa['prioridade']}\n"
            
            if 'tempo_restante' in tarefa and so.nome_escalonador == 'srtf':
                details_text += f"⏳ Restante: {tarefa['tempo_restante']}\n"
            
            executed_ticks = len(tarefa['tempos_de_execucao'])
            details_text += f"✔️ Executado: {executed_ticks}/{tarefa['duracao']} ticks\n"
            
            if tarefa['tempos_de_execucao']:
                recent_ticks = tarefa['tempos_de_execucao'][-3:]  # Últimos 3 ticks
                details_text += f"🔄 Últimos ticks: {recent_ticks}"
            
            details_label = customtkinter.CTkLabel(
                tarefa_frame,
                text=details_text,
                font=("Consolas", 10),
                text_color="white",
                justify="left"
            )
            details_label.pack(padx=10, pady=(0, 10), anchor="w")
        
        # Informações da fila de prontas
        if fila_prontas:
            fila_frame = customtkinter.CTkFrame(self.tcb_scrollable)
            fila_frame.pack(fill="x", padx=5, pady=10)
            
            fila_title = customtkinter.CTkLabel(
                fila_frame,
                text="🚦 Fila de Prontas:",
                font=("Arial", 12, "bold")
            )
            fila_title.pack(pady=5)
            
            fila_text = " → ".join([f"{t['id']}(p{t['prioridade']})" for t in fila_prontas])
            fila_label = customtkinter.CTkLabel(
                fila_frame,
                text=fila_text,
                font=("Consolas", 10),
                wraplength=350
            )
            fila_label.pack(padx=10, pady=(0, 10))


    def take_screenshot(self):
        """Salva o diagrama de Gantt como PNG de forma universal (Windows/Linux/macOS)."""
        if not self.gantt_diagram or not self.gantt_diagram.canvas:
            print("❌ Erro: Nenhum diagrama de Gantt disponível para capturar.")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_filename = f"gantt_diagram_{timestamp}.png"
        sistema = platform.system().lower()
        
        print(f"🖥️ Sistema detectado: {platform.system()}")
        print(f"📸 Salvando como: {final_filename}")
        
        # Força fundo branco no canvas
        try:
            original_bg = self.gantt_diagram.canvas.cget("bg")
            self.gantt_diagram.canvas.configure(bg="white")
            self.gantt_diagram.canvas.update()
            print("🎨 Fundo do canvas configurado para branco")
        except Exception as e:
            print(f"⚠️ Erro ao configurar fundo branco: {e}")
        
        # === MÉTODO 1: PIL ImageGrab (Windows/macOS prioritário) ===
        if sistema in ['windows', 'darwin']:  # Windows ou macOS
            try:
                
                print("🔄 Tentando captura direta com PIL...")
                
                x = self.gantt_diagram.canvas.winfo_rootx()
                y = self.gantt_diagram.canvas.winfo_rooty()
                width = self.gantt_diagram.canvas.winfo_width()
                height = self.gantt_diagram.canvas.winfo_height()
                
                screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
                
                # Garante fundo branco na imagem
                if screenshot.mode == 'RGBA':
                    background = Image.new('RGB', screenshot.size, (255, 255, 255))
                    background.paste(screenshot, mask=screenshot.split()[-1])
                    screenshot = background
                elif screenshot.mode != 'RGB':
                    screenshot = screenshot.convert('RGB')
                
                screenshot.save(final_filename)
                print(f"✅ Imagem salva com fundo branco: {final_filename}")
                return
                
            except Exception as e:
                print(f"⚠️ PIL falhou: {e}")
                print("🔄 Tentando método alternativo...")
        
        # === MÉTODO 2: Linux ou fallback - PostScript + conversão ===
        try:
            print("🔄 Gerando PostScript temporário...")
            temp_ps = f"temp_{timestamp}.eps"
            
            # Gera PostScript
            self.gantt_diagram.canvas.postscript(file=temp_ps)
            print(f"✅ PostScript gerado: {temp_ps}")
            
            # Tenta conversão com fundo branco usando ImageMagick
            if convert_ps_to_png_with_white_bg(temp_ps, final_filename):
                # Remove arquivo temporário
                try:
                    os.remove(temp_ps)
                    print(f"🗑️ Arquivo temporário removido: {temp_ps}")
                except:
                    pass
                return
            
            # Se ImageMagick falhou, tenta Pillow com fundo branco
            if convert_ps_to_png_pillow_with_white_bg(temp_ps, final_filename):
                try:
                    os.remove(temp_ps)
                except:
                    pass
                return
                
            print(f"⚠️ Conversão com fundo branco falhou. Arquivo PostScript mantido: {temp_ps}")
            print(f"💡 Para converter manualmente: convert -background white -flatten {temp_ps} {final_filename}")
            
        except Exception as e:
            print(f"❌ Método PostScript falhou: {e}")
        
        # === MÉTODO 3: SVG como último recurso ===
        try:
            print("🔄 Gerando SVG como alternativa...")
            svg_filename = f"gantt_diagram_{timestamp}.svg"
            self.export_gantt_as_svg(svg_filename)
            print(f"✅ Diagrama exportado como SVG: {svg_filename}")
            print(f"💡 Para converter para PNG: convert -background white {svg_filename} {final_filename}")
            return
            
        except Exception as e:
            print(f"❌ Exportação SVG falhou: {e}")
            
        print("❌ Todos os métodos falharam. Verifique permissões e dependências.")
 
    def export_gantt_as_svg(self, filename):
        """Exporta o diagrama de Gantt como arquivo SVG."""
        so = self.sistema_operacional
        tarefas = so.get_tarefas_ingressadas()
        current_time = so.get_relogio()
        
        # Configurações do SVG
        width = 1000
        height = len(tarefas) * 80 + 150
        margin_left = 120
        margin_top = 80
        cell_width = (width - margin_left - 60) / (current_time + 1)
        cell_height = 50
        
        # Gera conteúdo SVG
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="white"/>
  
  <!-- Grid lines -->'''
        
        # Linhas horizontais
        for i in range(len(tarefas) + 1):
            y = margin_top + i * (cell_height + 10)
            svg_content += f'\n  <line x1="{margin_left}" y1="{y}" x2="{width-60}" y2="{y}" stroke="gray" stroke-width="1"/>'
        
        # Linhas verticais e números
        for j in range(current_time + 2):
            x = margin_left + j * cell_width
            svg_content += f'\n  <line x1="{x}" y1="{margin_top}" x2="{x}" y2="{margin_top + len(tarefas) * (cell_height + 10)}" stroke="gray" stroke-width="1" stroke-dasharray="5,3"/>'
            svg_content += f'\n  <text x="{x}" y="{margin_top + len(tarefas) * (cell_height + 10) + 30}" text-anchor="middle" font-family="Arial" font-size="14">{j}</text>'
        
        # Desenha tarefas
        for i, tarefa in enumerate(reversed(tarefas)):
            y = margin_top + i * (cell_height + 10)
            
            # Nome da tarefa
            task_name = tarefa["id"].replace("_", "₋") if "_" in tarefa["id"] else tarefa["id"]
            svg_content += f'\n  <text x="{margin_left - 10}" y="{y + cell_height/2 + 5}" text-anchor="end" font-family="Arial" font-size="16" font-weight="bold">{task_name}</text>'
            
            # Retângulos da tarefa
            tempo_atual = current_time
            if tarefa["duracao"] == len(tarefa["tempos_de_execucao"]):
                tempo_termino = tarefa["tempos_de_execucao"][-1] if tarefa["tempos_de_execucao"] else tempo_atual
            else:
                tempo_termino = tempo_atual
                
            for tempo in range(tarefa["ingresso"], tempo_termino + 1):
                x = margin_left + tempo * cell_width
                
                if tempo in tarefa["tempos_de_execucao"]:
                    fill_color = tarefa["cor"]
                else:
                    fill_color = "white"
                
                svg_content += f'\n  <rect x="{x}" y="{y + 5}" width="{cell_width}" height="{cell_height}" fill="{fill_color}" stroke="black" stroke-width="2"/>'
        
        svg_content += '\n</svg>'
        
        # Escreve arquivo
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        