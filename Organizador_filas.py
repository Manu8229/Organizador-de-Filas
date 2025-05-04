import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from datetime import datetime
import queue

class Cliente:
    """Classe para representar um cliente na fila"""
    def __init__(self, numero):
        self.numero = numero
        self.hora_chegada = datetime.now()
        self.tempo_atendimento = random.randint(3, 8) * 60  # Em segundos
        self.atendido = False
    
    def __str__(self):
        return f"Senha: {self.numero:04d} - Chegada: {self.hora_chegada.strftime('%H:%M:%S')}"

class GerenciadorFila:
    """Classe para gerenciar a fila de atendimento"""
    def __init__(self):
        self.fila = queue.Queue()
        self.cliente_atual = None
        self.senha_counter = 1
        self.historico = []
        self.tempo_inicio_atendimento = None
    
    def gerar_senha(self):
        """Gera uma nova senha e adiciona à fila"""
        cliente = Cliente(self.senha_counter)
        self.fila.put(cliente)
        self.senha_counter += 1
        return cliente
    
    def chamar_proximo(self):
        """Chama o próximo cliente da fila"""
        if self.cliente_atual is not None:
            return None  # Já tem alguém sendo atendido
        
        if not self.fila.empty():
            self.cliente_atual = self.fila.get()
            self.tempo_inicio_atendimento = time.time()
            return self.cliente_atual
        return None
    
    def finalizar_atendimento(self):
        """Finaliza o atendimento do cliente atual"""
        if self.cliente_atual:
            self.cliente_atual.atendido = True
            self.historico.append(self.cliente_atual)
            tempo_atendimento = time.time() - self.tempo_inicio_atendimento
            self.cliente_atual = None
            return tempo_atendimento
        return 0
    
    def tempo_restante_atendimento(self):
        """Calcula o tempo restante de atendimento"""
        if self.cliente_atual and self.tempo_inicio_atendimento:
            tempo_decorrido = time.time() - self.tempo_inicio_atendimento
            return max(0, self.cliente_atual.tempo_atendimento - tempo_decorrido)
        return 0
    
    def fila_vazia(self):
        """Verifica se a fila está vazia"""
        return self.fila.empty() and self.cliente_atual is None

class AppOrganizadorFila(tk.Tk):
    """Classe principal da aplicação"""
    def __init__(self):
        super().__init__()
        
        self.title("Organizador de Fila de Atendimento")
        self.geometry("800x600")
        self.resizable(True, True)
        
        self.gerenciador = GerenciadorFila()
        self.tempo_atualizacao = 1000  # ms
        
        self.criar_widgets()
        self.atualizar_interface()
        
        # Simulação automática de chegada de clientes
        self.simular_chegada_clientes()
    
    def criar_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame do cliente atual
        frame_atual = ttk.LabelFrame(main_frame, text="Cliente em Atendimento", padding="10")
        frame_atual.pack(fill=tk.X, pady=5)
        
        self.lbl_cliente_atual = ttk.Label(frame_atual, text="Nenhum cliente em atendimento", font=('Arial', 14))
        self.lbl_cliente_atual.pack()
        
        self.lbl_tempo_restante = ttk.Label(frame_atual, text="Tempo restante: 0 segundos", font=('Arial', 12))
        self.lbl_tempo_restante.pack()
        
        # Frame de controle
        frame_controle = ttk.Frame(main_frame, padding="10")
        frame_controle.pack(fill=tk.X, pady=5)
        
        btn_adicionar = ttk.Button(frame_controle, text="Adicionar Cliente", command=self.adicionar_cliente)
        btn_adicionar.pack(side=tk.LEFT, padx=5)
        
        btn_proximo = ttk.Button(frame_controle, text="Atender Próximo", command=self.atender_proximo)
        btn_proximo.pack(side=tk.LEFT, padx=5)
        
        btn_finalizar = ttk.Button(frame_controle, text="Finalizar Atendimento", command=self.finalizar_atendimento)
        btn_finalizar.pack(side=tk.LEFT, padx=5)
        
        # Frame da fila de espera
        frame_fila = ttk.LabelFrame(main_frame, text="Fila de Espera", padding="10")
        frame_fila.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.tree_fila = ttk.Treeview(frame_fila, columns=('senha', 'hora_chegada'), show='headings')
        self.tree_fila.heading('senha', text='Senha')
        self.tree_fila.heading('hora_chegada', text='Hora de Chegada')
        self.tree_fila.column('senha', width=100)
        self.tree_fila.column('hora_chegada', width=200)
        
        scrollbar = ttk.Scrollbar(frame_fila, orient=tk.VERTICAL, command=self.tree_fila.yview)
        self.tree_fila.configure(yscroll=scrollbar.set)
        
        self.tree_fila.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame do histórico
        frame_historico = ttk.LabelFrame(main_frame, text="Histórico de Atendimento", padding="10")
        frame_historico.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.tree_historico = ttk.Treeview(frame_historico, columns=('senha', 'hora_chegada', 'atendido'), show='headings')
        self.tree_historico.heading('senha', text='Senha')
        self.tree_historico.heading('hora_chegada', text='Hora de Chegada')
        self.tree_historico.heading('atendido', text='Atendido')
        self.tree_historico.column('senha', width=100)
        self.tree_historico.column('hora_chegada', width=200)
        self.tree_historico.column('atendido', width=100)
        
        scrollbar_hist = ttk.Scrollbar(frame_historico, orient=tk.VERTICAL, command=self.tree_historico.yview)
        self.tree_historico.configure(yscroll=scrollbar_hist.set)
        
        self.tree_historico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_hist.pack(side=tk.RIGHT, fill=tk.Y)
    
    def adicionar_cliente(self):
        """Adiciona um novo cliente à fila"""
        cliente = self.gerenciador.gerar_senha()
        self.tree_fila.insert('', tk.END, values=(f"{cliente.numero:04d}", cliente.hora_chegada.strftime('%H:%M:%S')))
        self.atualizar_interface()
    
    def atender_proximo(self):
        """Chama o próximo cliente da fila"""
        cliente = self.gerenciador.chamar_proximo()
        if cliente:
            self.lbl_cliente_atual.config(text=f"Atendendo: Senha {cliente.numero:04d}")
            # Remove o primeiro item da treeview
            if self.tree_fila.get_children():
                self.tree_fila.delete(self.tree_fila.get_children()[0])
        else:
            if self.gerenciador.cliente_atual:
                messagebox.showinfo("Informação", "Já há um cliente em atendimento!")
            else:
                messagebox.showinfo("Informação", "Não há clientes na fila!")
        
        self.atualizar_interface()
    
    def finalizar_atendimento(self):
        """Finaliza o atendimento do cliente atual"""
        tempo = self.gerenciador.finalizar_atendimento()
        if tempo > 0:
            cliente = self.gerenciador.historico[-1]
            self.tree_historico.insert('', tk.END, values=(
                f"{cliente.numero:04d}", 
                cliente.hora_chegada.strftime('%H:%M:%S'), 
                "Sim"
            ))
            self.lbl_cliente_atual.config(text="Nenhum cliente em atendimento")
            messagebox.showinfo("Atendimento Finalizado", 
                              f"Atendimento da senha {cliente.numero:04d} finalizado em {int(tempo)} segundos.")
        else:
            messagebox.showinfo("Informação", "Nenhum cliente em atendimento para finalizar!")
        
        self.atualizar_interface()
    
    def atualizar_interface(self):
        """Atualiza a interface periodicamente"""
        # Atualiza o tempo restante
        tempo_restante = self.gerenciador.tempo_restante_atendimento()
        self.lbl_tempo_restante.config(text=f"Tempo restante: {int(tempo_restante)} segundos")
        
        # Agenda a próxima atualização
        self.after(self.tempo_atualizacao, self.atualizar_interface)
    
    def simular_chegada_clientes(self):
        """Simula a chegada aleatória de clientes"""
        if random.random() < 0.3:  # 30% de chance de chegar um novo cliente
            self.adicionar_cliente()
        
        # Agenda a próxima simulação
        intervalo = random.randint(5, 15) * 1000  # Entre 5 e 15 segundos
        self.after(intervalo, self.simular_chegada_clientes)

if __name__ == "__main__":
    app = AppOrganizadorFila()
    app.mainloop()