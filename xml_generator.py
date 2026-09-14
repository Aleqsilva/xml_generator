import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

class XMLGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de XML para Painéis de Controle")
        self.root.geometry("600x900")
        self.root.wm_attributes('-transparentcolor', 'blue')
        self.root.configure(bg='#f0f0f0')
        
        # Icone
        try:
            self.root.iconbitmap('favicon.ico')
        except:
            pass
        
        # Registrar função de validação para bits
        self.vcmd = (self.root.register(self.validate_bit_input), '%P')
        
        # Configurar estilo
        self.setup_style()
        
        # Variáveis
        self.filename = tk.StringVar(value="")
        
        # Listas para armazenar os componentes
        self.signals = []
        self.switches = []
        self.blocks = []
        self.warnings = []
        self.customs = []

        # Sistema de controle de bits únicos separado por categoria
        self.used_bits = {
            'controls': {},  # Bits de controle (ABRIR, FECHAR, NORMAL, REVERSO, BLOQUEAR, DESBLOQUEAR, TOGGLE)
            'indications': {}  # Bits de indicação (GREEN, YELLOW, RED, BLUE, FLASHRED)
        }
        
        self.create_widgets()
    
    def validate_bit_input(self, value):
        """Valida entrada de bits: apenas números positivos ou zero"""
        if value == "":  # Permite campo vazio
            return True
        try:
            num = int(value)
            return num >= 0  # Permite apenas números >= 0
        except ValueError:
            return False  # Rejeita texto não numérico
    
    def setup_style(self):
        """Configura o estilo visual da aplicação"""
        style = ttk.Style()
        
        # Configurar tema
        style.theme_use('winnative')
        
        # Cores do Sistema
        colors = {
            'primary': '#073359',      # Azul escuro institucional
            'secondary': '#093773',    # Azul médio institucional
            'accent': '#FFFF00',       # Amarelo institucional
            'success': '#28a745',      # Verde para sucesso
            'warning': '#ffc107',      # Amarelo para avisos
            'danger': '#dc3545',       # Vermelho para erros
            'light': '#f8f9fa',        # Cinza muito claro
            'dark': '#343a40'          # Cinza escuro
        }

        try:
            style.configure('Primary.TButton',
                           font=('Segoe UI', 9),
                           padding=(10, 5))
            
            style.configure('Success.TButton',
                           font=('Segoe UI', 9, 'bold'),
                           padding=(15, 8))
            
            style.map('Success.TButton',
                     background=[('active', colors['success'])])
            
            style.configure('Custom.TEntry',
                           fieldbackground='#f0f0f0',
                           borderwidth=1,
                           relief='solid')
            
            # Estilo para cabeçalhos das seções
            style.configure('ConfigHeader.TLabelframe',
                           relief='solid',
                           borderwidth=2,
                           bordercolor='black',
                           foreground='#f0f0f0')
            
            style.configure('ConfigHeader.TLabelframe.Label',
                           font=('Segoe UI', 11, 'bold'),
                           foreground='black')
            
            # Estilos para fundo branco e frames cinza
            style.configure('WhiteBackground.TFrame',
                           background='#f0f0f0')
            
            style.configure('GrayBackground.TLabelframe',
                           background='#f0f0f0',
                           relief='solid',
                           borderwidth=1,
                           bordercolor='#d0d0d0')
            
            style.configure('GrayBackground.TLabelframe.Label',
                           font=('Segoe UI', 11, 'bold'),
                           background='#f0f0f0',
                           foreground='black')
            
            # Configurar elementos internos para serem transparentes
            style.configure('Transparent.TFrame',
                           background='#f0f0f0')
            
            style.configure('Transparent.TLabel',
                           background='#f0f0f0')
            
            # Manter botões e entries com fundo padrão/branco
            style.configure('Custom.TEntry',
                           fieldbackground='white',
                           borderwidth=1,
                           relief='solid',
                           background='white')
            
            # Estilo para campos desabilitados
            style.configure('Disabled.TEntry',
                           fieldbackground='#e9e9e9',
                           borderwidth=1,
                           relief='solid',
                           background='#e9e9e9',
                           foreground='#666666')
        except:
            pass
    
    def create_widgets(self):
        # Header com logo/título
        header_frame = tk.Frame(self.root, bg='#1e3a5f', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        try:
            logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
            if os.path.exists(logo_path):
                from PIL import Image, ImageTk
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((60, 60), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = tk.Label(header_frame, image=logo_photo, bg='#1e3a5f')
                logo_label.image = logo_photo  # Manter referência da imagem
                logo_label.pack(side=tk.LEFT, padx=10, pady=10)
        except ImportError:
            pass
        
        # Subtítulo
        subtitle_label = tk.Label(header_frame, 
                                 text="Gerador de XML para Painéis de Controle", 
                                 font=('Segoe UI', 12),
                                 fg='#7bb3f0', 
                                 bg='#1e3a5f')
        subtitle_label.pack(side=tk.LEFT, padx=(0, 20), pady=20)

        # Frame principal com scroll
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(main_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='WhiteBackground.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configurações gerais
        config_frame = ttk.LabelFrame(scrollable_frame, text="Configurações", 
                                     padding=15, style='GrayBackground.TLabelframe')
        config_frame.pack(fill=tk.X, pady=(20, 15), padx=30)

        # Criar grid interno para melhor organização
        config_inner = ttk.Frame(config_frame, style='Transparent.TFrame')
        config_inner.pack(fill=tk.X)
        
        # Nome do arquivo
        file_frame = ttk.Frame(config_inner, style='Transparent.TFrame')
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="Nome do arquivo:", 
                 font=('Segoe UI', 10), style='Transparent.TLabel').pack(side=tk.LEFT, padx=(0, 0))
        
        filename_entry = ttk.Entry(file_frame, textvariable=self.filename, 
                                  width=15, style='Custom.TEntry', font=('Segoe UI', 10))
        filename_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(file_frame, text=".xml", 
                 font=('Segoe UI', 10, 'bold'), style='Transparent.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão de carregar arquivo
        ttk.Button(file_frame, text="Carregar XML", 
                  command=self.load_xml_file, style='Primary.TButton').pack(side=tk.LEFT)
        
        # Settings fields com layout em grid melhorado
        self.inhibit_bit = tk.StringVar(value="1")
        self.location_number = tk.StringVar(value="")
        self.firstkey_bit = tk.StringVar(value="")
        self.numberbits = tk.StringVar(value="8")
        
        # Primeira linha
        row1 = ttk.Frame(config_inner, style='Transparent.TFrame')
        row1.pack(fill=tk.X, pady=(0, 10))
        
        # Inhibit bit
        inhibit_frame = ttk.Frame(row1, style='Transparent.TFrame')
        inhibit_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(inhibit_frame, text="Inhibit bit:", 
                 font=('Segoe UI', 10), style='Transparent.TLabel').pack(anchor=tk.W)
        inhibit_entry = ttk.Entry(inhibit_frame, textvariable=self.inhibit_bit, width=12, 
                 style='Disabled.TEntry', state='disabled')
        inhibit_entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Location number
        location_frame = ttk.Frame(row1, style='Transparent.TFrame')
        location_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 0))
        ttk.Label(location_frame, text="Location number:", 
                 font=('Segoe UI', 10), style='Transparent.TLabel').pack(anchor=tk.W)
        location_entry = ttk.Entry(location_frame, textvariable=self.location_number, width=12, 
                 style='Custom.TEntry', validate='key', validatecommand=self.vcmd)
        location_entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Segunda linha
        row2 = ttk.Frame(config_inner, style='Transparent.TFrame')
        row2.pack(fill=tk.X)
        
        # First key bit
        firstkey_frame = ttk.Frame(row2, style='Transparent.TFrame')
        firstkey_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(firstkey_frame, text="First key bit:", 
                 font=('Segoe UI', 10), style='Transparent.TLabel').pack(anchor=tk.W)
        firstkey_entry = ttk.Entry(firstkey_frame, textvariable=self.firstkey_bit, width=12, 
                 style='Custom.TEntry', validate='key', validatecommand=self.vcmd)
        firstkey_entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Number bits
        numberbits_frame = ttk.Frame(row2, style='Transparent.TFrame')
        numberbits_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 0))
        ttk.Label(numberbits_frame, text="Number bits:", 
                 font=('Segoe UI', 10), style='Transparent.TLabel').pack(anchor=tk.W)
        numberbits_entry = ttk.Entry(numberbits_frame, textvariable=self.numberbits, width=12, 
                 style='Disabled.TEntry', state='disabled')
        numberbits_entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Nota explicativa para campos bloqueados
        note_frame = ttk.Frame(config_inner, style='Transparent.TFrame')
        note_frame.pack(fill=tk.X, pady=(10, 0))
        note_label = tk.Label(note_frame, 
                             text="💡 Inhibit bit e Number bits são valores fixos do sistema", 
                             font=('Segoe UI', 8, 'italic'), 
                             fg='#666666',
                             bg='#f0f0f0')
        note_label.pack(anchor=tk.W)
        
        # Sinais
        signals_frame = ttk.LabelFrame(scrollable_frame, text="Sinais", 
                                      padding=15, style='GrayBackground.TLabelframe')
        signals_frame.pack(fill=tk.X, pady=(0, 15), padx=30)
        
        # Entry rápida para sinais
        signals_entry_frame = ttk.Frame(signals_frame, style='Transparent.TFrame')
        signals_entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(signals_entry_frame, text="Nome dos Sinais (separado por vírgula, ex: S10D, S2E, S4EA/S4EB):", 
                 font=('Segoe UI', 10), style='Transparent.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        self.signals_entry = tk.Text(signals_entry_frame, height=3, wrap=tk.WORD, 
                                    font=('Segoe UI', 9), relief='solid', bd=1)
        self.signals_entry.pack(fill=tk.X, pady=(0, 5))
        
        signals_buttons_frame = ttk.Frame(signals_frame, style='Transparent.TFrame')
        signals_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(signals_buttons_frame, text="➕ Adicionar Sinais", 
                  command=self.add_signals_batch, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(signals_buttons_frame, text="➕ Individual", 
                  command=self.add_signal, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(signals_buttons_frame, text="➖ Remover", 
                  command=self.remove_signal, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(signals_buttons_frame, text="Limpar", 
                  command=self.clear_signals, style='Primary.TButton').pack(side=tk.LEFT)
        
        # Listbox com scroll
        list_frame = ttk.Frame(signals_frame, style='Transparent.TFrame')
        list_frame.pack(fill=tk.X)
        
        self.signals_listbox = tk.Listbox(list_frame, height=4, font=('Segoe UI', 9),
                                         relief='solid', bd=1, selectmode=tk.SINGLE)
        signals_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.signals_listbox.yview)
        self.signals_listbox.configure(yscrollcommand=signals_scroll.set)
        
        # Adicionar duplo clique para editar
        self.signals_listbox.bind("<Double-1>", lambda e: self.on_signal_double_click())
        
        self.signals_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        signals_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Nota explicativa para sinais duplos
        signals_note_frame = ttk.Frame(signals_frame, style='Transparent.TFrame')
        signals_note_frame.pack(fill=tk.X, pady=(5, 0))
        signals_note_label = tk.Label(signals_note_frame, 
                                     text="💡 Sinais duplos (ex: S18DA/S18DB) podem compartilhar bits de controle", 
                                     font=('Segoe UI', 8, 'italic'), 
                                     fg='#666666',
                                     bg='#f0f0f0')
        signals_note_label.pack(anchor=tk.W)

        # Chaves (Switches)
        switches_frame = ttk.LabelFrame(scrollable_frame, text="Chaves (SW)", 
                                       padding=15, style='GrayBackground.TLabelframe')
        switches_frame.pack(fill=tk.X, pady=(0, 15), padx=30)
        
        # Entry rápida para chaves
        switches_entry_frame = ttk.Frame(switches_frame, style='Transparent.TFrame')
        switches_entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(switches_entry_frame, text="Nomes das Chaves (separados por vírgula, ex: SW1A, SW1B, SW2):", 
                 font=('Segoe UI', 10), style='Transparent.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        self.switches_entry = tk.Text(switches_entry_frame, height=3, wrap=tk.WORD, 
                                     font=('Segoe UI', 9), relief='solid', bd=1)
        self.switches_entry.pack(fill=tk.X, pady=(0, 5))
        
        switches_buttons_frame = ttk.Frame(switches_frame, style='Transparent.TFrame')
        switches_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(switches_buttons_frame, text="➕ Adicionar Chaves", 
                  command=self.add_switches_batch, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(switches_buttons_frame, text="➕ Individual",
                  command=self.add_switch, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(switches_buttons_frame, text="➖ Remover", 
                  command=self.remove_switch, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(switches_buttons_frame, text="Limpar", 
                  command=self.clear_switches, style='Primary.TButton').pack(side=tk.LEFT)
        
        # Listbox com scroll
        switches_list_frame = ttk.Frame(switches_frame, style='Transparent.TFrame')
        switches_list_frame.pack(fill=tk.X)
        
        self.switches_listbox = tk.Listbox(switches_list_frame, height=4, font=('Segoe UI', 9),
                                          relief='solid', bd=1, selectmode=tk.SINGLE)
        switches_scroll = ttk.Scrollbar(switches_list_frame, orient="vertical", command=self.switches_listbox.yview)
        self.switches_listbox.configure(yscrollcommand=switches_scroll.set)
        
        # Adicionar duplo clique para editar
        self.switches_listbox.bind("<Double-1>", lambda e: self.on_switch_double_click())
        
        self.switches_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        switches_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bloqueios (PBs)
        blocks_frame = ttk.LabelFrame(scrollable_frame, text="Bloqueios (TB)", 
                                     padding=15, style='GrayBackground.TLabelframe')
        blocks_frame.pack(fill=tk.X, pady=(0, 15), padx=30)
        
        # Entry rápida para bloqueios
        blocks_entry_frame = ttk.Frame(blocks_frame, style='Transparent.TFrame')
        blocks_entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(blocks_entry_frame, text="Nomes dos Bloqueios (separados por vírgula, ex: TB1A, TB4D, TB6E):", 
                 font=('Segoe UI', 10), style='Transparent.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        self.blocks_entry = tk.Text(blocks_entry_frame, height=3, wrap=tk.WORD, 
                                   font=('Segoe UI', 9), relief='solid', bd=1)
        self.blocks_entry.pack(fill=tk.X, pady=(0, 5))
        
        blocks_buttons_frame = ttk.Frame(blocks_frame, style='Transparent.TFrame')
        blocks_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(blocks_buttons_frame, text="➕ Adicionar Bloqueios", 
                  command=self.add_blocks_batch, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(blocks_buttons_frame, text="➕ Individual", 
                  command=self.add_block, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(blocks_buttons_frame, text="➖ Remover", 
                  command=self.remove_block, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(blocks_buttons_frame, text="Limpar", 
                  command=self.clear_blocks, style='Primary.TButton').pack(side=tk.LEFT)
        
        # Listbox com scroll
        blocks_list_frame = ttk.Frame(blocks_frame, style='Transparent.TFrame')
        blocks_list_frame.pack(fill=tk.X)
        
        self.blocks_listbox = tk.Listbox(blocks_list_frame, height=4, font=('Segoe UI', 9),
                                        relief='solid', bd=1, selectmode=tk.SINGLE)
        blocks_scroll = ttk.Scrollbar(blocks_list_frame, orient="vertical", command=self.blocks_listbox.yview)
        self.blocks_listbox.configure(yscrollcommand=blocks_scroll.set)
        
        # Adicionar duplo clique para editar
        self.blocks_listbox.bind("<Double-1>", lambda e: self.on_block_double_click())
        
        self.blocks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        blocks_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Warnings
        warnings_frame = ttk.LabelFrame(scrollable_frame, text="Avisos", 
                                       padding=15, style='GrayBackground.TLabelframe')
        warnings_frame.pack(fill=tk.X, pady=(0, 15), padx=30)
        
        warnings_buttons_frame = ttk.Frame(warnings_frame, style='Transparent.TFrame')
        warnings_buttons_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(warnings_buttons_frame, text="➕ Individual", 
                  command=self.add_warning, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(warnings_buttons_frame, text="➖ Remover", 
                  command=self.remove_warning, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(warnings_buttons_frame, text="Limpar", 
                  command=self.clear_warnings, style='Primary.TButton').pack(side=tk.LEFT)
        
        # Listbox com scroll
        warnings_list_frame = ttk.Frame(warnings_frame, style='Transparent.TFrame')
        warnings_list_frame.pack(fill=tk.X)
        
        self.warnings_listbox = tk.Listbox(warnings_list_frame, height=4, font=('Segoe UI', 9),
                                          relief='solid', bd=1, selectmode=tk.SINGLE)
        warnings_scroll = ttk.Scrollbar(warnings_list_frame, orient="vertical", command=self.warnings_listbox.yview)
        self.warnings_listbox.configure(yscrollcommand=warnings_scroll.set)
        
        # Adicionar duplo clique para editar
        self.warnings_listbox.bind("<Double-1>", lambda e: self.on_warning_double_click())
        
        self.warnings_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        warnings_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Customs
        customs_frame = ttk.LabelFrame(scrollable_frame, text="Opções Customizadas", 
                                       padding=15, style='GrayBackground.TLabelframe')
        customs_frame.pack(fill=tk.X, pady=(0, 15), padx=30)
        
        customs_buttons_frame = ttk.Frame(customs_frame, style='Transparent.TFrame')
        customs_buttons_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(customs_buttons_frame, text="➕ Individual", 
                  command=self.add_custom, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(customs_buttons_frame, text="➖ Remover", 
                  command=self.remove_custom, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(customs_buttons_frame, text="Limpar", 
                  command=self.clear_customs, style='Primary.TButton').pack(side=tk.LEFT)
        
        # Listbox com scroll
        customs_list_frame = ttk.Frame(customs_frame, style='Transparent.TFrame')
        customs_list_frame.pack(fill=tk.X)
        
        self.customs_listbox = tk.Listbox(customs_list_frame, height=4, font=('Segoe UI', 9),
                                          relief='solid', bd=1, selectmode=tk.SINGLE)
        customs_scroll = ttk.Scrollbar(customs_list_frame, orient="vertical", command=self.customs_listbox.yview)
        self.customs_listbox.configure(yscrollcommand=customs_scroll.set)
        
        # Adicionar duplo clique para editar
        self.customs_listbox.bind("<Double-1>", lambda e: self.on_custom_double_click())
        
        self.customs_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        customs_scroll.pack(side=tk.RIGHT, fill=tk.Y)

       # Separador visual
        separator = ttk.Separator(scrollable_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=20)
        
        # Botão Adicionar TUDO
        add_all_frame = ttk.Frame(scrollable_frame, style='WhiteBackground.TFrame')
        add_all_frame.pack(fill=tk.X, pady=(0, 15), padx=30)
        
        # Centralizar o botão Adicionar TUDO
        center_add_all = ttk.Frame(add_all_frame, style='WhiteBackground.TFrame')
        center_add_all.pack(anchor=tk.CENTER)
        
        add_all_btn = ttk.Button(center_add_all, text="ADICIONAR TUDO", 
                                command=self.add_all_items, 
                                style='Success.TButton')
        add_all_btn.pack()
        
        # Nota explicativa para Adicionar TUDO
        add_all_note = tk.Label(add_all_frame, 
                               text="💡 Adiciona todos os itens (Sinais, Chaves e Bloqueios) de uma só vez",
                               bg = "#f0f0f0",
                               font=('Segoe UI', 8))
        add_all_note.pack(pady=(5, 0))
        
        # Separador visual
        separator2 = ttk.Separator(scrollable_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=20)
        
        # Botões principais com design moderno
        buttons_frame = ttk.Frame(scrollable_frame, style='WhiteBackground.TFrame')
        buttons_frame.pack(fill=tk.X, pady=(10, 0), padx=30)
        
        # Frame para centralizar botões
        center_buttons = ttk.Frame(buttons_frame, style='WhiteBackground.TFrame')
        center_buttons.pack(anchor=tk.CENTER)
        
        # Botão principal (Gerar XML)
        main_btn = ttk.Button(center_buttons, text="GERAR XML", 
                             command=self.generate_xml, 
                             style='Success.TButton')
        main_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Botão salvar
        save_btn = ttk.Button(center_buttons, text="Salvar como...", 
                             command=self.save_xml, 
                             style='Primary.TButton')
        save_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Botão limpar
        clear_btn = ttk.Button(center_buttons, text="Limpar Tudo", 
                              command=lambda: self.clear_all(isLoad=False), 
                              style='Primary.TButton')
        clear_btn.pack(side=tk.LEFT)
        
        # Adicionar espaço no final
        end_space = ttk.Frame(scrollable_frame, style='WhiteBackground.TFrame')
        end_space.pack(fill=tk.X, pady=20)
        
        # Pack canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel para scroll suave
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Adicionar rodapé
        footer_frame = tk.Frame(self.root, bg='#1e3a5f', height=30)
        footer_frame.pack(fill=tk.X)
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(footer_frame, 
                               text="Gerador de XML para Painéis de Controle - GEEEE © 2025", 
                               font=('Segoe UI', 8),
                               fg='#7bb3f0', 
                               bg='#1e3a5f')
        footer_label.pack(pady=8)
    
    def add_signals_batch(self):
        """Adiciona múltiplos sinais de uma vez"""
        text = self.signals_entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Aviso", "Digite os nomes dos sinais separados por vírgula.")
            return
        
        names = [name.strip().upper() for name in text.split(',') if name.strip()]
        if not names:
            messagebox.showwarning("Aviso", "Nenhum nome válido encontrado.")
            return
        
        # Verificar duplicatas dentro da própria lista
        seen_names = set()
        internal_duplicates = []
        unique_names = []
        
        for name in names:
            if name in seen_names:
                internal_duplicates.append(name)
            else:
                seen_names.add(name)
                unique_names.append(name)
        
        if internal_duplicates:
            duplicate_msg = f"Nomes repetidos na entrada:\n\n"
            for dup_name in set(internal_duplicates):
                count = names.count(dup_name)
                duplicate_msg += f"• '{dup_name}' aparece {count + 1} vezes\n"
            duplicate_msg += f"\n💡 Cada nome deve aparecer apenas uma vez na lista."
            messagebox.showerror("Erro", duplicate_msg)
            return
        
        # Validar nomes únicos contra itens existentes
        duplicates = []
        for name in unique_names:
            is_unique, error_msg = self.validate_unique_name('signal', name)
            if not is_unique:
                duplicates.append(f"• {name}: {error_msg}")
        
        if duplicates:
            duplicate_msg = "Nomes duplicados encontrados:\n\n" + "\n".join(duplicates)
            messagebox.showerror("Erro", duplicate_msg)
            return
        
        # Adicionar sinais sem bits (serão configurados individualmente)
        added_count = 0
        for name in unique_names:
            signal_data = {"name": name}
            self.signals.append(signal_data)
            added_count += 1
        
        self.update_signals_list()
        self.signals_entry.delete("1.0", tk.END)
        messagebox.showinfo("Sucesso", f"{added_count} sinal(is) adicionado(s) com sucesso!\n\nConfigure os bits individualmente usando 'Individual'.")
    
    def add_switches_batch(self):
        """Adiciona múltiplas chaves de uma vez"""
        text = self.switches_entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Aviso", "Digite os nomes das chaves separados por vírgula.")
            return
        
        names = [name.strip().upper() for name in text.split(',') if name.strip()]
        if not names:
            messagebox.showwarning("Aviso", "Nenhum nome válido encontrado.")
            return
        
        # Verificar duplicatas dentro da própria lista
        seen_names = set()
        internal_duplicates = []
        unique_names = []
        
        for name in names:
            if name in seen_names:
                internal_duplicates.append(name)
            else:
                seen_names.add(name)
                unique_names.append(name)
        
        if internal_duplicates:
            duplicate_msg = f"Nomes repetidos na entrada:\n\n"
            for dup_name in set(internal_duplicates):
                count = names.count(dup_name)
                duplicate_msg += f"• '{dup_name}' aparece {count + 1} vezes\n"
            duplicate_msg += f"\n💡 Cada nome deve aparecer apenas uma vez na lista."
            messagebox.showerror("Erro", duplicate_msg)
            return
        
        # Validar nomes únicos contra itens existentes
        duplicates = []
        for name in unique_names:
            is_unique, error_msg = self.validate_unique_name('switch', name)
            if not is_unique:
                duplicates.append(f"• {name}: {error_msg}")
        
        if duplicates:
            duplicate_msg = "Nomes duplicados encontrados:\n\n" + "\n".join(duplicates)
            messagebox.showerror("Erro", duplicate_msg)
            return
        
        # Adicionar chaves sem bits (serão configurados individualmente)
        added_count = 0
        for name in unique_names:
            switch_data = {"name": name}
            self.switches.append(switch_data)
            added_count += 1
        
        self.update_switches_list()
        self.switches_entry.delete("1.0", tk.END)

        messagebox.showinfo("Sucesso", f"{added_count} chave(s) adicionada(s) com sucesso!\n\nConfigure os bits individualmente usando 'Individual'.")
    
    def add_blocks_batch(self):
        """Adiciona múltiplos bloqueios de uma vez"""
        text = self.blocks_entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Aviso", "Digite os nomes dos bloqueios separados por vírgula.")
            return
        
        names = [name.strip().upper() for name in text.split(',') if name.strip()]
        if not names:
            messagebox.showwarning("Aviso", "Nenhum nome válido encontrado.")
            return
        
        # Verificar duplicatas dentro da própria lista
        seen_names = set()
        internal_duplicates = []
        unique_names = []
        
        for name in names:
            if name in seen_names:
                internal_duplicates.append(name)
            else:
                seen_names.add(name)
                unique_names.append(name)
        
        if internal_duplicates:
            duplicate_msg = f"Nomes repetidos na entrada:\n\n"
            for dup_name in set(internal_duplicates):
                count = names.count(dup_name)
                duplicate_msg += f"• '{dup_name}' aparece {count + 1} vezes\n"
            duplicate_msg += f"\n💡 Cada nome deve aparecer apenas uma vez na lista."
            messagebox.showerror("Erro", duplicate_msg)
            return
        
        # Validar nomes únicos contra itens existentes
        duplicates = []
        for name in unique_names:
            is_unique, error_msg = self.validate_unique_name('block', name)
            if not is_unique:
                duplicates.append(f"• {name}: {error_msg}")
        
        if duplicates:
            duplicate_msg = "Nomes duplicados encontrados:\n\n" + "\n".join(duplicates)
            messagebox.showerror("Erro", duplicate_msg)
            return
        
        # Adicionar bloqueios sem bits (serão configurados individualmente)
        added_count = 0
        for name in unique_names:
            block_data = {"name": name}
            self.blocks.append(block_data)
            added_count += 1
        
        self.update_blocks_list()
        self.blocks_entry.delete("1.0", tk.END)
        messagebox.showinfo("Sucesso", f"{added_count} bloqueio(s) adicionado(s) com sucesso!\n\nConfigure os bits individualmente usando 'Individual'.")

    def add_all_items(self):
        """Adiciona todos os itens (Sinais, Chaves e Bloqueios e Avisos) de uma vez"""
        # Coletar todos os nomes primeiro
        all_names = []
        signals_added = 0
        switches_added = 0
        blocks_added = 0
        warnings_added = 0
        
        # Processar sinais
        signals_text = self.signals_entry.get("1.0", tk.END).strip()
        signal_names = []
        if signals_text:
            signal_names = [name.strip().upper() for name in signals_text.split(',') if name.strip()]
        
        # Processar chaves
        switches_text = self.switches_entry.get("1.0", tk.END).strip()
        switch_names = []
        if switches_text:
            switch_names = [name.strip().upper() for name in switches_text.split(',') if name.strip()]
        
        # Processar bloqueios
        blocks_text = self.blocks_entry.get("1.0", tk.END).strip()
        block_names = []
        if blocks_text:
            block_names = [name.strip().upper() for name in blocks_text.split(',') if name.strip()]

        # Verificar duplicatas internas em cada categoria
        all_internal_duplicates = []
        
        # Verificar duplicatas nos sinais
        if signal_names:
            seen_signals = set()
            signal_duplicates = []
            unique_signal_names = []
            for name in signal_names:
                if name in seen_signals:
                    signal_duplicates.append(name)
                else:
                    seen_signals.add(name)
                    unique_signal_names.append(name)
            if signal_duplicates:
                for dup_name in set(signal_duplicates):
                    count = signal_names.count(dup_name)
                    all_internal_duplicates.append(f"• Sinal '{dup_name}' aparece {count + 1} vezes")
            signal_names = unique_signal_names
        
        # Verificar duplicatas nas chaves
        if switch_names:
            seen_switches = set()
            switch_duplicates = []
            unique_switch_names = []
            for name in switch_names:
                if name in seen_switches:
                    switch_duplicates.append(name)
                else:
                    seen_switches.add(name)
                    unique_switch_names.append(name)
            if switch_duplicates:
                for dup_name in set(switch_duplicates):
                    count = switch_names.count(dup_name)
                    all_internal_duplicates.append(f"• Chave '{dup_name}' aparece {count + 1} vezes")
            switch_names = unique_switch_names
        
        # Verificar duplicatas nos bloqueios
        if block_names:
            seen_blocks = set()
            block_duplicates = []
            unique_block_names = []
            for name in block_names:
                if name in seen_blocks:
                    block_duplicates.append(name)
                else:
                    seen_blocks.add(name)
                    unique_block_names.append(name)
            if block_duplicates:
                for dup_name in set(block_duplicates):
                    count = block_names.count(dup_name)
                    all_internal_duplicates.append(f"• Bloqueio '{dup_name}' aparece {count + 1} vezes")
            block_names = unique_block_names

        # Verificar duplicatas entre categorias (mesmo nome em categorias diferentes)
        all_unique_names = signal_names + switch_names + block_names
        cross_category_duplicates = []
        
        # Verificar se o mesmo nome aparece em categorias diferentes
        for signal_name in signal_names:
            if signal_name in switch_names:
                cross_category_duplicates.append(f"• '{signal_name}' aparece como Sinal e Chave")
            if signal_name in block_names:
                cross_category_duplicates.append(f"• '{signal_name}' aparece como Sinal e Bloqueio")
        
        for switch_name in switch_names:
            if switch_name in block_names:
                cross_category_duplicates.append(f"• '{switch_name}' aparece como Chave e Bloqueio")
        
        # Mostrar erros de duplicatas internas
        if all_internal_duplicates or cross_category_duplicates:
            error_msg = "Nomes repetidos encontrados:\n\n"
            if all_internal_duplicates:
                error_msg += "Repetições na mesma categoria:\n"
                error_msg += "\n".join(all_internal_duplicates)
                error_msg += "\n\n"
            if cross_category_duplicates:
                error_msg += "Repetições entre categorias:\n"
                error_msg += "\n".join(set(cross_category_duplicates))
                error_msg += "\n\n"
            error_msg += "💡 Cada nome deve aparecer apenas uma vez no total."
            messagebox.showerror("Erro", error_msg)
            return
        
        # Criar lista final para validação contra itens existentes
        all_names = []
        all_names.extend([('signal', name) for name in signal_names])
        all_names.extend([('switch', name) for name in switch_names])
        all_names.extend([('block', name) for name in block_names])
        if not all_names:
            messagebox.showwarning("Aviso", "Nenhum item foi encontrado para adicionar.\n\nDigite os nomes nos campos acima antes de usar 'Adicionar TUDO'.")
            return
        
        # Validar nomes únicos contra itens existentes
        duplicates = []
        for item_type, name in all_names:
            is_unique, error_msg = self.validate_unique_name(item_type, name)
            if not is_unique:
                type_name = {"signal": "Sinal", "switch": "Chave", "block": "Bloqueio", "warning": "Aviso"}[item_type]
                duplicates.append(f"• {type_name} {name}: {error_msg}")
        
        if duplicates:
            duplicate_msg = "Nomes duplicados encontrados:\n\n" + "\n".join(duplicates)
            messagebox.showerror("Erro", duplicate_msg)
            return
        
        # Adicionar os itens após validação
        for name in signal_names:
            signal_data = {"name": name}
            self.signals.append(signal_data)
            signals_added += 1
        if signal_names:
            self.signals_entry.delete("1.0", tk.END)
        
        for name in switch_names:
            switch_data = {"name": name}
            self.switches.append(switch_data)
            switches_added += 1
        if switch_names:
            self.switches_entry.delete("1.0", tk.END)
        
        for name in block_names:
            block_data = {"name": name}
            self.blocks.append(block_data)
            blocks_added += 1
        if block_names:
            self.blocks_entry.delete("1.0", tk.END)
        
        # Atualizar todas as listas
        self.update_signals_list()
        self.update_switches_list()
        self.update_blocks_list()
        self.update_warnings_list()
        
        # Mostrar resultado
        total_added = signals_added + switches_added + blocks_added + warnings_added
        result_message = f"Itens adicionados com sucesso! \n\n"
        if signals_added > 0:
            result_message += f"Sinais: {signals_added}\n"
        if switches_added > 0:
            result_message += f"Chaves: {switches_added}\n"
        if blocks_added > 0:
            result_message += f"Bloqueios: {blocks_added}\n"
        result_message += f"\nTotal: {total_added} item(s)"
        result_message += f"\n\nConfigure os bits individualmente usando o botão 'Individual' de cada seção."
        
        messagebox.showinfo("Sucesso", result_message)
    
    def clear_signals(self):
        has_data = (len(self.signals) > 0)
        if has_data:
            if messagebox.askokcancel("Limpar Sinais", "Todos os sinais serão removidos.\n Você tem certeza que deseja remover todos os sinais?"):
                """Limpa toda a lista de signals"""
                self.signals.clear()
                self.update_signals_list()
                # Reconstruir registro de bits
                self.rebuild_bits_registry()
        else:
            messagebox.showinfo("Limpar Sinais", "Não há sinais para remover.")

    def clear_switches(self):
        """Limpa toda a lista de chaves"""
        has_data = (len(self.switches) > 0)
        if has_data:
            if messagebox.askokcancel("Limpar Chaves", "Todos os chaves serão removidos.\n Você tem certeza que deseja remover todos os chaves?"):
                """Limpa toda a lista de chaves"""
                self.switches.clear()
                self.update_switches_list()
                # Reconstruir registro de bits
                self.rebuild_bits_registry()
        else:
            messagebox.showinfo("Limpar Chaves", "Não há chaves para remover.")

    def clear_blocks(self):
        """Limpa toda a lista de bloqueios"""
        has_data = (len(self.blocks) > 0)
        if has_data:
            if messagebox.askokcancel("Limpar Bloqueios", "Todos os bloqueios serão removidos.\n Você tem certeza que deseja remover todos os bloqueios?"):
                """Limpa toda a lista de bloqueios"""
                self.blocks.clear()
                self.update_blocks_list()
                # Reconstruir registro de bits
                self.rebuild_bits_registry()
        else:
            messagebox.showinfo("Limpar Bloqueios", "Não há bloqueios para remover.")

    def clear_warnings(self):
        """Limpa toda a lista de avisos"""
        has_data = (len(self.warnings) > 0)
        if has_data:
            if messagebox.askokcancel("Limpar Avisos", "Todos os avisos serão removidos.\n Você tem certeza que deseja remover todos os avisos?"):
                """Limpa toda a lista de avisos"""
                self.warnings.clear()
                self.update_warnings_list()
                # Reconstruir registro de bits
                self.rebuild_bits_registry()
        else:
            messagebox.showinfo("Limpar Avisos", "Não há avisos para remover.")

    def clear_customs(self):
        """Limpa toda a lista de opções customizadas"""
        has_data = (len(self.customs) > 0)
        if has_data:
            if messagebox.askokcancel("Limpar Opções Customizadas", "Todas as opções customizadas serão removidas.\n Você tem certeza que deseja remover todas as opções customizadas?"):
                """Limpa toda a lista de opções customizadas"""
                self.customs.clear()
                self.update_customs_list()
                # Reconstruir registro de bits
                self.rebuild_bits_registry()
        else:
            messagebox.showinfo("Limpar Opções Customizadas", "Não há opções customizadas para remover.")

    def add_signal(self):
        try:
            dialog = SignalDialog(self.root, True)  # Sempre incluir bits
            self.root.wait_window(dialog.dialog)
            if dialog.result:
                # Validar nome único
                is_unique, error_msg = self.validate_unique_name('signal', dialog.result['name'])
                if not is_unique:
                    messagebox.showerror("Erro", error_msg)
                    return
                
                # Validar bits únicos
                conflicts = self.validate_bits('signal', dialog.result['name'], dialog.result)
                if conflicts:
                    action = self.show_bit_conflict_dialog(conflicts)
                    if action == 'cancel':
                        return  # Usuário cancelou
                    elif action == 'edit':
                        # Editar o item existente com conflito
                        self.edit_conflicting_item(conflicts[0])
                        return
                
                # Registrar bits antes de adicionar
                self._register_item_bits('signal', dialog.result['name'], dialog.result)
                
                self.signals.append(dialog.result)
                self.update_signals_list()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar sinal: {str(e)}")
    
    def remove_signal(self):
        selection = self.signals_listbox.curselection()
        if selection:
            self.signals.pop(selection[0])
            self.update_signals_list()
            # Reconstruir registro de bits após remoção
            self.rebuild_bits_registry()
        else:
            messagebox.showwarning("Aviso", "Selecione um sinal para remover.")
    
    def update_signals_list(self):
        self.signals_listbox.delete(0, tk.END)
        for signal in self.signals:
            display_text = signal['name']
            # Sempre mostrar informações dos bits
            abrir = signal.get('abrir_bit', '')
            fechar = signal.get('fechar_bit', '')
            green = signal.get('green_bit', '')
            yellow = signal.get('yellow_bit', '')
            red = signal.get('red_bit', '')
            blue = signal.get('blue_bit', '')
            flashred = signal.get('flash_red_bit', '')
            display_text += f" | ABRIR:{abrir} FECHAR:{fechar} GREEN:{green} YELLOW:{yellow} RED:{red} BLUE:{blue} FLASHRED:{flashred}"
            self.signals_listbox.insert(tk.END, display_text)
        self.signals_listbox.yview_moveto(1.0)

    
    def add_switch(self):
        try:
            dialog = SwitchDialog(self.root, True)  # Sempre incluir bits
            self.root.wait_window(dialog.dialog)
            if dialog.result:
                # Validar nome único
                is_unique, error_msg = self.validate_unique_name('switch', dialog.result['name'])
                if not is_unique:
                    messagebox.showerror("Erro", error_msg)
                    return
                
                # Validar bits únicos
                conflicts = self.validate_bits('switch', dialog.result['name'], dialog.result)
                if conflicts:
                    action = self.show_bit_conflict_dialog(conflicts)
                    if action == 'cancel':
                        return  # Usuário cancelou
                    elif action == 'edit':
                        # Editar o item existente com conflito
                        self.edit_conflicting_item(conflicts[0])
                        return
                
                # Registrar bits antes de adicionar
                self._register_item_bits('switch', dialog.result['name'], dialog.result)
                
                self.switches.append(dialog.result)
                self.update_switches_list()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar chave: {str(e)}")
    
    def remove_switch(self):
        selection = self.switches_listbox.curselection()
        if selection:
            self.switches.pop(selection[0])
            self.update_switches_list()
            # Reconstruir registro de bits após remoção
            self.rebuild_bits_registry()
        else:
            messagebox.showwarning("Aviso", "Selecione uma chave para remover.")
    
    def update_switches_list(self):
        self.switches_listbox.delete(0, tk.END)
        for switch in self.switches:
            display_text = switch['name']
            # Sempre mostrar informações dos bits
            normal = switch.get('normal_bit', '')
            reverso = switch.get('reverso_bit', '')
            bloquear = switch.get('bloquear_bit', '')
            desbloquear = switch.get('desbloquear_bit', '')
            display_text += f" | NORMAL:{normal} REVERSO:{reverso} BLOQUEAR:{bloquear} DESBLOQUEAR:{desbloquear}"
            self.switches_listbox.insert(tk.END, display_text)
        self.switches_listbox.yview_moveto(1.0)
    
    def add_block(self):
        try:
            dialog = BlockDialog(self.root, True)  # Sempre incluir bits
            self.root.wait_window(dialog.dialog)
            if dialog.result:
                # Validar nome único
                is_unique, error_msg = self.validate_unique_name('block', dialog.result['name'])
                if not is_unique:
                    messagebox.showerror("Erro", error_msg)
                    return
                
                # Validar bits únicos
                conflicts = self.validate_bits('block', dialog.result['name'], dialog.result)
                if conflicts:
                    action = self.show_bit_conflict_dialog(conflicts)
                    if action == 'cancel':
                        return  # Usuário cancelou
                    elif action == 'edit':
                        # Editar o item existente com conflito
                        self.edit_conflicting_item(conflicts[0])
                        return
                
                # Registrar bits antes de adicionar  
                self._register_item_bits('block', dialog.result['name'], dialog.result)
                
                self.blocks.append(dialog.result)
                self.update_blocks_list()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar bloqueio: {str(e)}")
    
    def remove_block(self):
        selection = self.blocks_listbox.curselection()
        if selection:
            self.blocks.pop(selection[0])
            self.update_blocks_list()
            # Reconstruir registro de bits após remoção
            self.rebuild_bits_registry()
        else:
            messagebox.showwarning("Aviso", "Selecione um bloqueio para remover.")
    
    def update_blocks_list(self):
        self.blocks_listbox.delete(0, tk.END)
        for block in self.blocks:
            display_text = block['name']
            # Sempre mostrar informações dos bits
            bloquear = block.get('bloquear_bit', '')
            desbloquear = block.get('desbloquear_bit', '')
            blue = block.get('blue_bit', '')
            display_text += f" | BLOQUEAR:{bloquear} DESBLOQUEAR:{desbloquear} BLUE:{blue}"
            self.blocks_listbox.insert(tk.END, display_text)
        self.blocks_listbox.yview_moveto(1.0)

    def add_warning(self):
        try:
            dialog = WarningDialog(self.root, True)  # Sempre incluir bits
            self.root.wait_window(dialog.dialog)
            if dialog.result:
                # Validar nome único
                is_unique, error_msg = self.validate_unique_name('warning', dialog.result['name'])
                if not is_unique:
                    messagebox.showerror("Erro", error_msg)
                    return
                
                self.warnings.append(dialog.result)
                self.update_warnings_list()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar aviso: {str(e)}")

    def remove_warning(self):
        selection = self.warnings_listbox.curselection()
        if selection:
            self.warnings.pop(selection[0])
            self.update_warnings_list()
            # Reconstruir registro de bits após remoção
            self.rebuild_bits_registry()
        else:
            messagebox.showwarning("Aviso", "Selecione um aviso para remover.")

    def update_warnings_list(self):
        self.warnings_listbox.delete(0, tk.END)
        for warning in self.warnings:
            display_text = warning['name']
            # Sempre mostrar informações dos bits
            ativar = warning.get('ativar_bit', '')
            estado_ativar = warning.get('estado_ativar')
            som_estado = warning.get('som')
            desativar = warning.get('desativar_bit', '')
            estado_desativar = warning.get('estado_desativar')
            display_text += f" | ATIVAR:{ativar} ESTADO:{estado_ativar} SOM:{som_estado} DESATIVAR:{desativar} ESTADO:{estado_desativar}"
            self.warnings_listbox.insert(tk.END, display_text)
        self.warnings_listbox.yview_moveto(1.0)

    def add_custom(self):
        try:
            dialog = CustomDialog(self.root, True)  # Sempre incluir bits
            self.root.wait_window(dialog.dialog)
            if dialog.result:
                # Validar nome único
                is_unique, error_msg = self.validate_unique_name('custom', dialog.result['name'])
                if not is_unique:
                    messagebox.showerror("Erro", error_msg)
                    return
                
                self.customs.append(dialog.result)
                self.update_customs_list()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar opção customizada: {str(e)}")

    def remove_custom(self):
        selection = self.customs_listbox.curselection()
        if selection:
            self.customs.pop(selection[0])
            self.update_customs_list()
            # Reconstruir registro de bits após remoção
            self.rebuild_bits_registry()
        else:
            messagebox.showwarning("Aviso", "Selecione uma opção customizada para remover.")

    def update_customs_list(self):
        self.customs_listbox.delete(0, tk.END)
        for custom in self.customs:
            display_text = custom['name']
            # Sempre mostrar informações dos bits
            custom_bit = custom.get('custom_bit', '')
            display_text += f" | bit:{custom_bit}"
            self.customs_listbox.insert(tk.END, display_text)
        self.customs_listbox.yview_moveto(1.0)

    def clear_all(self, isLoad=False):
        # Verificar se há dados para limpar
        has_data = (len(self.signals) > 0 or len(self.switches) > 0 or len(self.blocks) > 0 or len(self.warnings) > 0 or len(self.customs) > 0) and (
                   self.signals_entry.get("1.0", tk.END).strip() or
                   self.switches_entry.get("1.0", tk.END).strip() or
                   self.blocks_entry.get("1.0", tk.END).strip() or
                   self.warnings_entry.get("1.0", tk.END).strip() or
                   self.customs_entry.get("1.0", tk.END).strip() or
                   self.location_number.get().strip() or
                   self.firstkey_bit.get().strip())
        
        if not has_data and isLoad:
            return

        if not has_data:
            messagebox.showinfo("Info", "Não há dados para limpar.")
            return
        
        # Confirmar a ação
        response = messagebox.askyesno(
            "Confirmar Limpeza", 
            "Tem certeza que deseja limpar TODOS os dados?\n\n"
            "Esta ação irá remover:\n"
            "• Todos os sinais adicionados\n"
            "• Todas as chaves adicionadas\n"
            "• Todos os bloqueios adicionados\n"
            "• Textos nos campos de entrada\n"
            "• Configurações técnicas (Location number e First key bit)\n\n"
            "Esta ação não pode ser desfeita!",
            icon='warning'
        )
        
        if not response:
            return  # Usuário cancelou
        
        # Executar limpeza
        self.signals.clear()
        self.switches.clear()
        self.blocks.clear()
        self.warnings.clear()
        self.signals_entry.delete("1.0", tk.END)
        self.switches_entry.delete("1.0", tk.END)
        self.blocks_entry.delete("1.0", tk.END)
        self.warnings_entry.delete("1.0", tk.END)
        self.customs_entry.delete("1.0", tk.END)
        
        # Limpar campos de configuração técnica
        self.location_number.set("")
        self.firstkey_bit.set("")
        
        self.update_signals_list()
        self.update_switches_list()
        self.update_blocks_list()
        self.update_warnings_list()
        self.update_customs_list()
        # Limpar controle de bits únicos
        self.used_bits = {
            'controls': {},
            'indications': {}
        }
        
        messagebox.showinfo("✅ Sucesso", "Todos os dados foram limpos com sucesso!")
    
    def rebuild_bits_registry(self):
        """Reconstrói o registro de bits usados com base nos itens existentes"""
        self.used_bits = {
            'controls': {},
            'indications': {}
        }
        
        # Processar sinais
        for signal in self.signals:
            self._register_item_bits('signal', signal['name'], signal)
        
        # Processar chaves
        for switch in self.switches:
            self._register_item_bits('switch', switch['name'], switch)
        
        # Processar bloqueios
        for block in self.blocks:
            self._register_item_bits('block', block['name'], block)

        # Processar opções personalizadas
        for custom in self.customs:
            self._register_item_bits('custom', custom['name'], custom)

    def _register_item_bits(self, item_type, item_name, item_data):
        """Registra os bits de um item no controle de bits únicos separado por categoria"""
        # Definir mapeamento de bits por categoria
        conflicts = {}
        bit_categories = {
            'signal': {
                'controls': ['abrir_bit', 'fechar_bit'],
                'indications': ['green_bit', 'yellow_bit', 'red_bit', 'blue_bit', 'flashred_bit']
            },
            'switch': {
                'controls': ['normal_bit', 'reverso_bit', 'bloquear_bit', 'desbloquear_bit'],
                'indications': []
            },
            'block': {
                'controls': ['bloquear_bit', 'desbloquear_bit'],
                'indications': ['blue_bit']
            },
            'custom': {
                'controls': ['custom_bit'],
                'indications': []
            }
        }
        
        categories = bit_categories.get(item_type, {'controls': [], 'indications': []})
        
        # Checar conflitos internos dentro do próprio item (mesmo bit usado em 2 campos
        # da mesma categoria). Isso garante que, por exemplo, não se atribua o mesmo
        # número de bit para GREEN e BLUE do mesmo sinal.
        # Só verificamos duplicidade dentro da mesma categoria (controls x indications).
        for cat_name in ('controls', 'indications'):
            seen = {}
            for bit_type in categories.get(cat_name, []):
                bit_value = item_data.get(bit_type, '').strip()
                if not bit_value:
                    continue
                if bit_value in seen:
                    # Reportar conflito interno: bit já usado em outro campo deste item
                    conflicts.append({
                        'bit_value': bit_value,
                        'category': 'controle' if cat_name == 'controls' else 'indicação',
                        'new_type': item_type,
                        'new_name': item_name,
                        'new_bit_type': bit_type.replace('_bit', '').upper(),
                        'existing_type': 'interno',
                        'existing_name': item_name,
                        'existing_bit_type': seen[bit_value].replace('_bit', '').upper()
                    })
                else:
                    seen[bit_value] = bit_type
        
        # Registrar bits de controle
        for bit_type in categories['controls']:
            bit_value = item_data.get(bit_type, '').strip()
            if bit_value:
                self.used_bits['controls'][bit_value] = {
                    'type': item_type,
                    'name': item_name,
                    'bit_type': bit_type.replace('_bit', '').upper()
                }
        
        # Registrar bits de indicação
        for bit_type in categories['indications']:
            bit_value = item_data.get(bit_type, '').strip()
            if bit_value:
                self.used_bits['indications'][bit_value] = {
                    'type': item_type,
                    'name': item_name,
                    'bit_type': bit_type.replace('_bit', '').upper()
                }
    
    def _are_paired_signals(self, signal_name1, signal_name2):
        """
        Verifica se dois sinais são sinais duplos (pares A/B)
        Exemplo: S18DA e S18DB são sinais duplos
        Não considera sinais direcionais como S18E e S18D como pares
        """
        if not signal_name1 or not signal_name2:
            return False
        
        # Verificar se ambos terminam com uma única letra
        if len(signal_name1) < 2 or len(signal_name2) < 2:
            return False
        
        # Extrair a base e o sufixo (última letra)
        base1 = signal_name1[:-1]
        base2 = signal_name2[:-1]
        suffix1 = signal_name1[-1]
        suffix2 = signal_name2[-1]
        
        # Se as bases são iguais e os sufixos são diferentes
        if base1 == base2 and suffix1 != suffix2 and suffix1.isalpha() and suffix2.isalpha():
            # Verificar se são sinais direcionais conhecidos
            # Sinais direcionais comuns: D (direita), E (esquerda)
            directional_letters = {'D', 'E'}
            
            # Se ambos os sufixos são letras direcionais conhecidas, não são pares A/B
            if suffix1.upper() in directional_letters and suffix2.upper() in directional_letters:
                return False
            
            # Se pelo menos um dos sufixos é A ou B, são pares válidos
            ab_letters = {'A', 'B'}
            if suffix1.upper() in ab_letters or suffix2.upper() in ab_letters:
                return True
            
            # Para outros casos (letras não direcionais), aceitar apenas se sequenciais
            if abs(ord(suffix1.upper()) - ord(suffix2.upper())) == 1:
                return True
        
        return False

    def validate_bits(self, item_type, item_name, item_data):
        """Valida se os bits do item são únicos dentro de suas respectivas categorias"""
        conflicts = []
        
        # Definir mapeamento de bits por categoria
        bit_categories = {
            'signal': {
                'controls': ['abrir_bit', 'fechar_bit'],
                'indications': ['green_bit', 'yellow_bit', 'red_bit', 'blue_bit']
            },
            'switch': {
                'controls': ['normal_bit', 'reverso_bit', 'bloquear_bit', 'desbloquear_bit'],
                'indications': []
            },
            'custom': {
                'controls': ['custom_bit'],
                'indications': []
            },
            'block': {
                'controls': ['bloquear_bit', 'desbloquear_bit'],
                'indications': ['blue_bit']
            },
        }
        
        categories = bit_categories.get(item_type, {'controls': [], 'indications': []})
        
        # Validar bits de controle
        for bit_type in categories['controls']:
            bit_value = item_data.get(bit_type, '').strip()
            if bit_value and bit_value in self.used_bits['controls']:
                existing = self.used_bits['controls'][bit_value]
                # Permitir se for o mesmo item sendo editado
                if not (existing['type'] == item_type and existing['name'] == item_name):
                    # Exceção: Permitir compartilhamento de bits de controle entre sinais duplos (A/B)
                    if (item_type == 'signal' and existing['type'] == 'signal' and 
                        self._are_paired_signals(item_name, existing['name'])):
                        # Sinais duplos podem compartilhar bits de controle, não é conflito
                        continue
                    
                    conflicts.append({
                        'bit_value': bit_value,
                        'category': 'controle',
                        'new_type': item_type,
                        'new_name': item_name,
                        'new_bit_type': bit_type.replace('_bit', '').upper(),
                        'existing_type': existing['type'],
                        'existing_name': existing['name'],
                        'existing_bit_type': existing['bit_type']
                    })
        
        # Validar bits de indicação
        for bit_type in categories['indications']:
            bit_value = item_data.get(bit_type, '').strip()
            if bit_value and bit_value in self.used_bits['indications']:
                existing = self.used_bits['indications'][bit_value]
                # Permitir se for o mesmo item sendo editado
                if not (existing['type'] == item_type and existing['name'] == item_name):
                    # Exceção: Permitir compartilhamento de bits azuis entre sinais duplos (A/B)
                    if (item_type == 'signal' and existing['type'] == 'signal' and 
                        bit_type == 'blue_bit' and
                        self._are_paired_signals(item_name, existing['name'])):
                        # Sinais duplos podem compartilhar bits azuis, não é conflito
                        continue
                    
                    conflicts.append({
                        'bit_value': bit_value,
                        'category': 'indicação',
                        'new_type': item_type,
                        'new_name': item_name,
                        'new_bit_type': bit_type.replace('_bit', '').upper(),
                        'existing_type': existing['type'],
                        'existing_name': existing['name'],
                        'existing_bit_type': existing['bit_type']
                    })
        
        return conflicts
    
    def validate_unique_name(self, item_type, item_name, exclude_index=None):
        """Valida se o nome do item é único"""
        collections = {
            'signal': self.signals,
            'switch': self.switches,
            'block': self.blocks,
            'warning': self.warnings
        }
        
        collection = collections.get(item_type, [])
        for i, item in enumerate(collection):
            if exclude_index is not None and i == exclude_index:
                continue
            if item['name'].upper() == item_name.upper():
                return False, f"{item_type.title()} '{item_name}' já existe!"
        
        # Verificar em outras coleções também
        all_names = []
        for other_type, items in collections.items():
            if other_type == item_type:
                continue
            all_names.extend([item['name'].upper() for item in items])
        
        if item_name.upper() in all_names:
            return False, f"Nome '{item_name}' já existe em outro tipo de item!"
        
        return True, ""
    
    def edit_conflicting_item(self, conflict):
        """Edita o item que possui o bit conflitante"""
        try:
            existing_type = conflict['existing_type']
            existing_name = conflict['existing_name']
            
            # Encontrar o item existente
            collections = {
                'signal': self.signals,
                'switch': self.switches,
                'block': self.blocks,
                'custom': self.customs
            }
            
            collection = collections[existing_type]
            item_index = None
            existing_item = None
            
            for i, item in enumerate(collection):
                if item['name'] == existing_name:
                    item_index = i
                    existing_item = item
                    break
            
            if existing_item is None:
                messagebox.showerror("Erro", "Item não encontrado para edição!")
                return
            
            # Abrir diálogo de edição
            self.edit_item(existing_type, item_index)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar item: {str(e)}")
    
    def edit_item(self, item_type, item_index):
        """Edita um item existente"""
        try:
            collections = {
                'signal': (self.signals, SignalDialog),
                'switch': (self.switches, SwitchDialog),
                'block': (self.blocks, BlockDialog),
                'warning': (self.warnings, WarningDialog),
                'custom': (self.customs, CustomDialog)
            }
            
            collection, dialog_class = collections[item_type]
            current_item = collection[item_index]
            
            # Criar diálogo com dados atuais
            dialog = dialog_class(self.root, True)
            
            # Preencher campos com dados existentes
            dialog.name_var.set(current_item['name'])
            
            # Preencher bits se existirem
            bit_mappings = {
                'signal': ['abrir_bit', 'fechar_bit', 'green_bit', 'yellow_bit', 'red_bit', 'blue_bit', 'flashred_bit'],
                'switch': ['normal_bit', 'reverso_bit', 'bloquear_bit', 'desbloquear_bit'],
                'block': ['bloquear_bit', 'desbloquear_bit', 'blue_bit'],
                'warning': ['ativar_bit', 'desativar_bit'],
                'custom': ['custom_bit']
            }

            for bit_field in bit_mappings.get(item_type, []):
                if hasattr(dialog, bit_field.replace('_bit', '_var')):
                    var = getattr(dialog, bit_field.replace('_bit', '_var'))
                    var.set(current_item.get(bit_field, ''))
            
            self.root.wait_window(dialog.dialog)
            
            if dialog.result:
                # Validar nome único (excluindo o item atual)
                is_unique, error_msg = self.validate_unique_name(item_type, dialog.result['name'], item_index)
                if not is_unique:
                    messagebox.showerror("Erro", error_msg)
                    return
                
                # Validar bits únicos (excluindo o item atual)
                conflicts = self.validate_bits(item_type, dialog.result['name'], dialog.result)
                # Filtrar conflitos que sejam com o próprio item
                conflicts = [c for c in conflicts if not (c['existing_type'] == item_type and c['existing_name'] == current_item['name'])]
                
                if conflicts:
                    action = self.show_bit_conflict_dialog(conflicts)
                    if action == 'cancel':
                        return
                    elif action == 'edit':
                        self.edit_conflicting_item(conflicts[0])
                        return
                
                # Atualizar item
                collection[item_index] = dialog.result
                
                # Reconstruir registro de bits
                self.rebuild_bits_registry()
                
                # Atualizar lista
                if item_type == 'signal':
                    self.update_signals_list()
                elif item_type == 'switch':
                    self.update_switches_list()
                elif item_type == 'block':
                    self.update_blocks_list()
                elif item_type == 'custom':
                    self.update_customs_list()
                elif item_type == 'warning':
                    self.update_warnings_list()

                messagebox.showinfo("Sucesso", f"{item_type.title()} '{dialog.result['name']}' editado com sucesso!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar {item_type}: {str(e)}")
    
    def on_signal_double_click(self):
        """Trata duplo clique na lista de sinais"""
        selection = self.signals_listbox.curselection()
        if selection:
            self.edit_item('signal', selection[0])
    
    def on_switch_double_click(self):
        """Trata duplo clique na lista de chaves"""
        selection = self.switches_listbox.curselection()
        if selection:
            self.edit_item('switch', selection[0])
    
    def on_block_double_click(self):
        """Trata duplo clique na lista de bloqueios"""
        selection = self.blocks_listbox.curselection()
        if selection:
            self.edit_item('block', selection[0])
    
    def on_warning_double_click(self):
        """Trata duplo clique na lista de warnings"""
        selection = self.warnings_listbox.curselection()
        if selection:
            self.edit_item('warning', selection[0])

    def on_custom_double_click(self):
        """Trata duplo clique na lista de customs"""
        selection = self.customs_listbox.curselection()
        if selection:
            self.edit_item('custom', selection[0])
    
    def show_bit_conflict_dialog(self, conflicts):
        """Mostra diálogo para resolver conflitos de bits"""
        if not conflicts:
            return True
        
        # Criar janela de conflito
        conflict_window = tk.Toplevel(self.root)
        conflict_window.title("Conflito de Bits - GEEEE")
        conflict_window.geometry("700x500")
        conflict_window.configure(bg='#f0f0f0')
        conflict_window.transient(self.root)
        conflict_window.grab_set()
        
        result = {'action': 'cancel'}
        
        # Header
        header_frame = tk.Frame(conflict_window, bg='#dc3545', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                               text="Bits Duplicados Detectados", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='#f0f0f0', 
                               bg='#dc3545')
        header_label.pack(pady=15)
        
        # Frame principal
        main_frame = ttk.Frame(conflict_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Explicação
        explanation = tk.Label(main_frame, 
                              text="Os seguintes bits já estão sendo usados por outros itens.\nCada bit deve ser único dentro de sua categoria (controles ou indicações):",
                              font=('Segoe UI', 10),
                              bg='#f0f0f0',
                              justify=tk.LEFT)
        explanation.pack(anchor=tk.W, pady=(0, 15))
        
        # Lista de conflitos
        conflicts_frame = ttk.LabelFrame(main_frame, text="Conflitos Encontrados", padding=10, style='Config.TLabelframe')
        conflicts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Scrollable frame para conflitos
        canvas = tk.Canvas(conflicts_frame, bg='white', height=200)
        scrollbar = ttk.Scrollbar(conflicts_frame, orient="vertical", command=canvas.yview)
        scrollable_conflicts = ttk.Frame(canvas)
        
        scrollable_conflicts.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_conflicts, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar cada conflito
        for i, conflict in enumerate(conflicts):
            conflict_frame = tk.Frame(scrollable_conflicts, bg='#fff3cd', relief='solid', bd=1)
            conflict_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Título do conflito
            category_text = conflict.get('category', 'categoria desconhecida')
            title_label = tk.Label(conflict_frame, 
                                  text=f"🔴 Bit '{conflict['bit_value']}' duplicado (categoria: {category_text}):",
                                  font=('Segoe UI', 9, 'bold'),
                                  bg='#fff3cd',
                                  fg='#856404')
            title_label.pack(anchor=tk.W, padx=10, pady=(5, 0))
            
            # Detalhes
            details_text = f"• Tentando usar em: {conflict['new_type'].title()} '{conflict['new_name']}' - Bit {conflict['new_bit_type']} ({category_text})\n"
            details_text += f"• Já usado em: {conflict['existing_type'].title()} '{conflict['existing_name']}' - Bit {conflict['existing_bit_type']} ({category_text})"
            
            details_label = tk.Label(conflict_frame,
                                   text=details_text,
                                   font=('Segoe UI', 8),
                                   bg='#fff3cd',
                                   fg='#856404',
                                   justify=tk.LEFT)
            details_label.pack(anchor=tk.W, padx=20, pady=(0, 5))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
        center_buttons = ttk.Frame(buttons_frame)
        center_buttons.pack(anchor=tk.CENTER)
        
        def cancel_action():
            result['action'] = 'cancel'
            conflict_window.destroy()
        
        def edit_action():
            result['action'] = 'edit'
            conflict_window.destroy()

        ttk.Button(center_buttons, text="Cancelar Adição", 
                  command=cancel_action, style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(center_buttons, text="Editar Item Existente", 
                  command=edit_action, style='Success.TButton').pack(side=tk.LEFT)
        ttk.Button(center_buttons, text="Ignorar Duplicata",
                  command=lambda: [conflict_window.destroy(), result.update({'action': 'ignore'})],
                  style='Primary.TButton').pack(side=tk.LEFT, padx=(10, 0))
        
        # Centralizar janela
        conflict_window.update_idletasks()
        x = (conflict_window.winfo_screenwidth() // 2) - (conflict_window.winfo_width() // 2)
        y = (conflict_window.winfo_screenheight() // 2) - (conflict_window.winfo_height() // 2)
        conflict_window.geometry(f"+{x}+{y}")
        
        # Aguardar resposta
        self.root.wait_window(conflict_window)
        
        return result['action']
    
    def save_xml(self):
        """Gera e salva o XML diretamente"""
        try:
            # Verificar se há conteúdo para salvar
            if not self.signals and not self.switches and not self.blocks:
                messagebox.showwarning("Aviso", "Adicione pelo menos um item antes de salvar!")
                return
            
            # Gerar o XML
            xml_str = self.generate_xml_string()
            
            # Criar diretório se não existir
            import os
            save_dir = os.path.dirname(sys.executable)
            
            # Abrir diálogo para salvar
            filename = filedialog.asksaveasfilename(
                title="Salvar XML - GEEEE",
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml")],
                initialfile=f"{self.filename.get()}.xml",
                initialdir=save_dir
            )
            
            if filename:
                # Garantir que o diretório existe
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(xml_str)
                messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso! \n\n{filename}")
                
        except PermissionError:
            messagebox.showerror("Erro", "Erro de permissão! \n\nVerifique se o arquivo não está sendo usado por outro programa.")
        except FileNotFoundError:
            messagebox.showerror("Erro", "Caminho não encontrado! \n\nTente salvar em outro local.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado ao salvar XML! \n\n{str(e)}")
    
    def generate_xml_string(self):
        """Gera a string XML (método separado para reutilização)"""
        # Criar estrutura XML
        root = ET.Element("panel")
        
        # Settings
        settings = ET.SubElement(root, "settings")
        
        inhibit = ET.SubElement(settings, "inhibit")
        inhibit.set("bit", self.inhibit_bit.get() if self.inhibit_bit.get() else "")
        
        location = ET.SubElement(settings, "location")
        location.set("number", self.location_number.get() if self.location_number.get() else "")

        
        firstkey = ET.SubElement(settings, "firstkey")
        firstkey.set("bit", self.firstkey_bit.get() if self.firstkey_bit.get() else "")
        
        numberbits = ET.SubElement(settings, "numberbits")
        numberbits.set("number", self.numberbits.get() if self.numberbits.get() else "")

        
        # Separar sinais por terminação A e B
        signals_b_and_others = [s for s in self.signals if not s['name'].endswith('A')]
        signals_a = [s for s in self.signals if s['name'].endswith('A')]

        # Sinais (terminados em B e outros que não terminam em A)
        if signals_b_and_others:
            signals_elem = ET.SubElement(root, "signals")
            
            for signal in signals_b_and_others:
                signal_elem = ET.SubElement(signals_elem, "signal")
                signal_elem.set("name", signal['name'])
                
                # Controles
                controls = ET.SubElement(signal_elem, "controls")
                
                abrir = ET.SubElement(controls, "item")
                abrir.set("name", "ABRIR")
                abrir.set("bit", signal.get('abrir_bit', ''))
                
                fechar = ET.SubElement(controls, "item")
                fechar.set("name", "FECHAR")
                fechar.set("bit", signal.get('fechar_bit', ''))
                
                # Indacações
                indications = ET.SubElement(signal_elem, "indications")
                
                green = ET.SubElement(indications, "green")
                green.set("bit", signal.get('green_bit', ''))
                
                yellow = ET.SubElement(indications, "yellow")
                yellow.set("bit", signal.get('yellow_bit', ''))
                
                red = ET.SubElement(indications, "red")
                red.set("bit", signal.get('red_bit', ''))
                
                blue = ET.SubElement(indications, "blue")
                blue.set("bit", signal.get('blue_bit', ''))

                flashred = ET.SubElement(indications, "flashred")
                flashred.set("bit", signal.get('flashred_bit', ''))
        
        # Signals2H (terminados em B)
        if signals_a:
            signals2h_elem = ET.SubElement(root, "signals2H")
            
            for signal in signals_a:
                signal2h_elem = ET.SubElement(signals2h_elem, "signal2H")
                signal2h_elem.set("name", signal['name'])
                
                # Controls
                controls = ET.SubElement(signal2h_elem, "controls")
                
                abrir = ET.SubElement(controls, "item")
                abrir.set("name", "ABRIR")
                abrir.set("bit", signal.get('abrir_bit', ''))
                
                fechar = ET.SubElement(controls, "item")
                fechar.set("name", "FECHAR")
                fechar.set("bit", signal.get('fechar_bit', ''))
                
                # Indicações
                indications = ET.SubElement(signal2h_elem, "indications")
                
                green = ET.SubElement(indications, "green")
                green.set("bit", signal.get('green_bit', ''))
                
                yellow = ET.SubElement(indications, "yellow")
                yellow.set("bit", signal.get('yellow_bit', ''))
                
                red = ET.SubElement(indications, "red")
                red.set("bit", signal.get('red_bit', ''))
                
                blue = ET.SubElement(indications, "blue")
                blue.set("bit", signal.get('blue_bit', ''))

                flashred = ET.SubElement(indications, "flashred")
                flashred.set("bit", signal.get('flashred_bit', ''))

        # PBs (Chaves e Bloqueios)
        if self.switches or self.blocks or self.customs:
            pbs_elem = ET.SubElement(root, "PBs")
            
            # Chaves
            for switch in self.switches:
                pb_elem = ET.SubElement(pbs_elem, "PB")
                pb_elem.set("name", switch['name'])
                
                controls = ET.SubElement(pb_elem, "controls")
                
                normal = ET.SubElement(controls, "item")
                normal.set("name", "NORMAL")
                normal.set("bit", switch.get('normal_bit', ''))
                
                reverso = ET.SubElement(controls, "item")
                reverso.set("name", "REVERSO")
                reverso.set("bit", switch.get('reverso_bit', ''))
                
                bloquear = ET.SubElement(controls, "item")
                bloquear.set("name", "BLOQUEAR")
                bloquear.set("bit", switch.get('bloquear_bit', ''))
                
                desbloquear = ET.SubElement(controls, "item")
                desbloquear.set("name", "DESBLOQUEAR")
                desbloquear.set("bit", switch.get('desbloquear_bit', ''))
                
                indications = ET.SubElement(pb_elem, "indications")
            
            # Bloqueios
            for block in self.blocks:
                pb_elem = ET.SubElement(pbs_elem, "PB")
                pb_elem.set("name", block['name'])
                
                controls = ET.SubElement(pb_elem, "controls")
                
                bloquear = ET.SubElement(controls, "item")
                bloquear.set("name", "BLOQUEAR")
                bloquear.set("bit", block.get('bloquear_bit', ''))
                
                desbloquear = ET.SubElement(controls, "item")
                desbloquear.set("name", "DESBLOQUEAR")
                desbloquear.set("bit", block.get('desbloquear_bit', ''))
                
                indications = ET.SubElement(pb_elem, "indications")
                
                blue = ET.SubElement(indications, "blue")
                blue.set("bit", block.get('blue_bit', ''))
        
            for custom in self.customs:
                pb_elem = ET.SubElement(pbs_elem, "PB")
                pb_elem.set("name", custom['name'])

                controls = ET.SubElement(pb_elem, "controls")

                custom_control = ET.SubElement(controls, "item")
                custom_control.set("name", custom.get('name', ''))
                custom_control.set("bit", custom.get('custom_bit', ''))

        if self.warnings:
            warnings_elem = ET.SubElement(root, "warnings")
            for warning in self.warnings:
                warning_elem = ET.SubElement(warnings_elem, "item")
                warning_elem.set("bit", warning.get('ativar_bit', ''))
                warning_elem.set("descricao", warning.get('name', ''))
                warning_elem.set("som", warning.get('som', 'False'))
                warning_elem.set("estado_ativar", warning.get('estado_ativar', 'True'))
                warning_elem.set("condToOff", warning.get('desativar_bit', ''))
                warning_elem.set("estado_desativar", warning.get('estado_desativar', 'False'))

        # Converter para string formatada
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        
        # Gerar XML formatado corretamente
        xml_str = reparsed.toprettyxml(indent="\t", encoding=None)
        
        # Substituir a declaração XML padrão pela versão com encoding
        xml_str = xml_str.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="utf-8"?>')
        
        return xml_str
    
    def generate_xml(self):
        """Gera o XML e mostra na janela de preview"""
        try:
            # Verificar se há conteúdo para gerar
            if not self.signals and not self.switches and not self.blocks and not self.warnings:
                messagebox.showwarning("Aviso", "Adicione pelo menos um item antes de gerar o XML!")
                return
            
            xml_str = self.generate_xml_string()
            self.show_xml_result(xml_str)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar XML!\n\n{str(e)}")
    
    def show_xml_result(self, xml_str):
        result_window = tk.Toplevel(self.root)
        result_window.title("XML Gerado - GEEEE")
        result_window.geometry("700x600")
        result_window.configure(bg='#f0f0f0')
        
        # Header da janela
        header_frame = tk.Frame(result_window, bg='#1e3a5f', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                               text="📄 XML Gerado com Sucesso", 
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', 
                               bg='#1e3a5f')
        header_label.pack(pady=15)
        
        # Frame principal
        main_frame = ttk.Frame(result_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Text widget com estilo melhorado
        text_widget = tk.Text(main_frame, wrap=tk.NONE, font=('Consolas', 9),
                             relief='solid', bd=1, bg='white')
        scrollbar_v = ttk.Scrollbar(main_frame, orient="vertical", command=text_widget.yview)
        scrollbar_h = ttk.Scrollbar(main_frame, orient="horizontal", command=text_widget.xview)
        
        text_widget.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        text_widget.insert(tk.END, xml_str)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        scrollbar_h.grid(row=1, column=0, sticky="ew")
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Frame para botões
        button_frame = ttk.Frame(result_window)
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Centralizar botão
        center_frame = ttk.Frame(button_frame)
        center_frame.pack(anchor=tk.CENTER)
        
        # Botão para salvar com estilo
        save_btn = ttk.Button(center_frame, text="Salvar Como...", 
                             command=lambda: self.save_xml_from_text(xml_str),
                             style='Success.TButton')
        save_btn.pack()
    
    def save_xml_from_text(self, xml_str):
        """Salva o XML a partir do texto na janela de preview"""
        try:
            # Criar diretório se não existir
            import os
            save_dir = os.path.dirname(sys.executable)
            
            filename = filedialog.asksaveasfilename(
                title="Salvar XML",
                defaultextension=".xml",
                filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
                initialfile=f"{self.filename.get()}.xml",
                initialdir=save_dir
            )
            
            if filename:
                # Garantir que o diretório existe
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(xml_str)
                messagebox.showinfo("Sucesso", f"Arquivo salvo como:\n{filename}")

                
        except PermissionError:
            messagebox.showerror("Erro", "Erro de permissão! Verifique se o arquivo não está sendo usado por outro programa.")
        except FileNotFoundError:
            messagebox.showerror("Erro", "Caminho não encontrado! Tente salvar em outro local.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado ao salvar arquivo:\n{str(e)}")

    def pergunta_load_xml(self, lista_itens):
        tipo_itens = messagebox.askyesno("Gerenciamento de Elementos","Deseja tratar os elementos antes?")
        itens_unicos = set(lista_itens) 
        if tipo_itens:
            parent = self.root
            self.dialog = tk.Toplevel(parent)
            self.dialog.title("Escolha de Elementos - GEEEE")
            # Centralizar na tela
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
            self.dialog.geometry(f"+{x}+{y}")
            self.dialog.configure(bg="#f0f0f0")
            self.dialog.transient(parent)
            self.dialog.grab_set()

            header_frame = tk.Frame(self.dialog, bg='#f0f0f0', height=60)
            header_frame.pack(fill=tk.X)

            header_label = tk.Label(header_frame,
            text="Selecione os tipos de elementos a serem carregados",
            font=('Segoe UI', 11, 'bold'),
            bg="#f0f0f0")
            header_label.pack(pady=15)
            
            button_frame = tk.Frame(self.dialog, bg="#f0f0f0")
            button_frame.pack(pady=20)
            varSinais = tk.BooleanVar(value=True if 'sinais' in lista_itens else False)
            ttk.Checkbutton(button_frame, text="Sinais", onvalue=True, offvalue=False, variable=varSinais, state=(tk.DISABLED if 'sinais' not in lista_itens else tk.NORMAL)).pack(side=tk.LEFT, padx=5)
            varChaves = tk.BooleanVar(value=True if 'chaves' in lista_itens else False)
            ttk.Checkbutton(button_frame, text="Chaves", onvalue=True, offvalue=False, variable=varChaves, state=(tk.DISABLED if 'chaves' not in lista_itens else tk.NORMAL)).pack(side=tk.LEFT, padx=5)
            varBloqueios = tk.BooleanVar(value=True if 'bloqueios' in lista_itens else False)
            ttk.Checkbutton(button_frame, text="Bloqueios", onvalue=True, offvalue=False, variable=varBloqueios, state=(tk.DISABLED if 'bloqueios' not in lista_itens else tk.NORMAL)).pack(side=tk.LEFT, padx=5)
            varWarnings = tk.BooleanVar(value=True if 'warnings' in lista_itens else False)
            ttk.Checkbutton(button_frame, text="Warnings", onvalue=True, offvalue=False, variable=varWarnings, state=(tk.DISABLED if 'warnings' not in lista_itens else tk.NORMAL)).pack(side=tk.LEFT, padx=5)

            ttk.Separator(self.dialog, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
            
            botao_confirma_frame = ttk.Frame(self.dialog, padding=10)
            botao_confirma_frame.pack(fill=tk.X)
            ttk.Button(botao_confirma_frame, text="Confirmar", command=self.dialog.destroy, style='Success.TButton').pack()
            
            note_frame = ttk.Frame(self.dialog, padding=10)
            note_frame.pack()
            note_label = tk.Label(note_frame, text="""Apenas os elementos selecionados serão carregados.
Botões disponíveis de acordo com a presença dos itens no arquivo XML.""",
                                  font=('Segoe UI', 8),
                                  bg="#f0f0f0",
                                  fg="#666666")
            note_label.pack(anchor=tk.W)

            parent.wait_window(self.dialog)
            if not varSinais.get() and 'sinais' in itens_unicos:
                itens_unicos.discard('sinais')
            if not varChaves.get() and 'chaves' in itens_unicos:
                itens_unicos.discard('chaves')
            if not varBloqueios.get() and 'bloqueios' in itens_unicos:
                itens_unicos.discard('bloqueios')
            if not varWarnings.get() and 'warnings' in itens_unicos:
                itens_unicos.discard('warnings')
        return itens_unicos

    def load_xml_file(self):
        """Carrega um arquivo XML existente e preenche todos os campos"""
        try:
            # Abrir diálogo para selecionar arquivo
            filename = filedialog.askopenfilename(
                title="Carregar XML - GEEEE",
                filetypes=[("XML files", "*.xml")],
                initialdir=os.path.dirname(sys.executable)
            )
            
            if not filename:
                return  # Usuário cancelou

            # Confirmar se deseja sobrescrever dados existentes
            if self.signals or self.switches or self.blocks or self.warnings:
                response = messagebox.askyesno(
                    "Confirmar Carregamento", 
                    "Há dados não salvos que serão perdidos.\n\nDeseja continuar e carregar o arquivo XML?",
                    icon='warning'
                )
                if not response:
                    return
            
            # Carregar e fazer parsing do XML
            try:
                tree = ET.parse(filename)
                root = tree.getroot()
                
                # Limpar dados existentes
                self.clear_all(isLoad=True)

                # Extrair nome do arquivo (sem extensão)
                base_filename = os.path.splitext(os.path.basename(filename))[0]
                self.filename.set(base_filename)
                lista_itens = []
                lista_itens.append('sinais' if root.find('signals') is not None else '')
                pbs = root.find('PBs')
                if pbs is not None:
                    for pb_elem in pbs.findall('PB'):
                        pb_name = pb_elem.get('name', '')
                        lista_itens.append('chaves' if pb_name.startswith('SW') else '')
                        lista_itens.append('bloqueios' if pb_name.startswith('TB') else '')
                lista_itens.append('warnings' if root.find('warnings') is not None else '')


                # Perguntar ao usuário quais elementos deseja carregar
                tipo_itens = self.pergunta_load_xml(lista_itens)
                                
                # Carregar configurações (settings)
                settings = root.find('settings')
                if settings is not None:
                    # Inhibit bit
                    inhibit = settings.find('inhibit')
                    if inhibit is not None and inhibit.get('bit'):
                        self.inhibit_bit.set(inhibit.get('bit'))

                # Carregar configurações (settings)
                settings = root.find('settings')
                if settings is not None:
                    # Inhibit bit
                    inhibit = settings.find('inhibit')
                    if inhibit is not None and inhibit.get('bit'):
                        self.inhibit_bit.set(inhibit.get('bit'))
                    
                    # Location number
                    location = settings.find('location')
                    if location is not None and location.get('number'):
                        self.location_number.set(location.get('number'))
                    
                    # First key bit
                    firstkey = settings.find('firstkey')
                    if firstkey is not None and firstkey.get('bit'):
                        self.firstkey_bit.set(firstkey.get('bit'))
                    
                    # Number bits
                    numberbits = settings.find('numberbits')
                    if numberbits is not None and numberbits.get('number'):
                        self.numberbits.set(numberbits.get('number'))
                
                # Carregar sinais
                signals = root.find('signals')
                if signals is not None and 'sinais' in tipo_itens:
                    for signal_elem in signals.findall('signal'):
                        signal_data = {'name': signal_elem.get('name', '')}
                        
                        # Carregar controles dos sinais
                        controls = signal_elem.find('controls')
                        if controls is not None:
                            for item in controls.findall('item'):
                                item_name = item.get('name', '').lower()
                                if item_name == 'abrir':
                                    signal_data['abrir_bit'] = item.get('bit', '')
                                elif item_name == 'fechar':
                                    signal_data['fechar_bit'] = item.get('bit', '')
                        
                        # Carregar indicações dos sinais
                        indications = signal_elem.find('indications')
                        if indications is not None:
                            green = indications.find('green')
                            if green is not None:
                                signal_data['green_bit'] = green.get('bit', '')
                            
                            yellow = indications.find('yellow')
                            if yellow is not None:
                                signal_data['yellow_bit'] = yellow.get('bit', '')
                            
                            red = indications.find('red')
                            if red is not None:
                                signal_data['red_bit'] = red.get('bit', '')
                            
                            blue = indications.find('blue')
                            if blue is not None:
                                signal_data['blue_bit'] = blue.get('bit', '')

                            flashred = indications.find('flashred')
                            if flashred is not None:
                                signal_data['flashred_bit'] = flashred.get('bit', '')
                        
                        self.signals.append(signal_data)
                
                # Carregar signals2H (sinais duplos da seção B)
                signals2h = root.find('signals2H')
                if signals2h is not None and 'sinais' in tipo_itens:
                    for signal_elem in signals2h.findall('signal2H'):
                        signal_data = {'name': signal_elem.get('name', '')}
                        
                        # Carregar controles dos sinais
                        controls = signal_elem.find('controls')
                        if controls is not None:
                            for item in controls.findall('item'):
                                item_name = item.get('name', '').lower()
                                if item_name == 'abrir':
                                    signal_data['abrir_bit'] = item.get('bit', '')
                                elif item_name == 'fechar':
                                    signal_data['fechar_bit'] = item.get('bit', '')
                        
                        # Carregar indicações dos sinais
                        indications = signal_elem.find('indications')
                        if indications is not None:
                            green = indications.find('green')
                            if green is not None:
                                signal_data['green_bit'] = green.get('bit', '')
                            
                            yellow = indications.find('yellow')
                            if yellow is not None:
                                signal_data['yellow_bit'] = yellow.get('bit', '')
                            
                            red = indications.find('red')
                            if red is not None:
                                signal_data['red_bit'] = red.get('bit', '')
                            
                            blue = indications.find('blue')
                            if blue is not None:
                                signal_data['blue_bit'] = blue.get('bit', '')
                        
                            flashred = indications.find('flashred')
                            if flashred is not None:
                                signal_data['flashred_bit'] = flashred.get('bit', '')
                        
                        self.signals.append(signal_data)
                
                # Carregar PBs (chaves e bloqueios)
                pbs = root.find('PBs')
                if pbs is not None:
                    for pb_elem in pbs.findall('PB'):
                        pb_name = pb_elem.get('name', '')
                        
                        # Determinar o tipo baseado no nome (SW para chaves, TB para bloqueios)
                        if pb_name.startswith('SW') and 'chaves' in tipo_itens:  # Switch/Chave
                            switch_data = {'name': pb_name}
                            
                            # Carregar controles das chaves
                            controls = pb_elem.find('controls')
                            if controls is not None:
                                for item in controls.findall('item'):
                                    item_name = item.get('name', '').lower()
                                    if item_name == 'normal':
                                        switch_data['normal_bit'] = item.get('bit', '')
                                    elif item_name == 'reverso':
                                        switch_data['reverso_bit'] = item.get('bit', '')
                                    elif item_name == 'bloquear':
                                        switch_data['bloquear_bit'] = item.get('bit', '')
                                    elif item_name == 'desbloquear':
                                        switch_data['desbloquear_bit'] = item.get('bit', '')
                            
                            self.switches.append(switch_data)

                        elif pb_name.startswith('TB') and 'bloqueios' in tipo_itens:  # Track Block/Bloqueio
                            block_data = {'name': pb_name}
                            
                            # Carregar controles dos bloqueios
                            controls = pb_elem.find('controls')
                            if controls is not None:
                                for item in controls.findall('item'):
                                    item_name = item.get('name', '').lower()
                                    if item_name == 'bloquear':
                                        block_data['bloquear_bit'] = item.get('bit', '')
                                    elif item_name == 'desbloquear':
                                        block_data['desbloquear_bit'] = item.get('bit', '')
                            
                            # Carregar indicações dos bloqueios
                            indications = pb_elem.find('indications')
                            if indications is not None:
                                blue = indications.find('blue')
                                if blue is not None:
                                    block_data['blue_bit'] = blue.get('bit', '')
                            
                            self.blocks.append(block_data)
                
                # Carregar warnings
                warnings = root.find('warnings')
                if warnings is not None:
                    for warning_elem in warnings.findall('item'):
                        warning_data = {
                            'name': warning_elem.get('descricao', ''),
                            'ativar_bit': warning_elem.get('bit', ''),
                            'som': warning_elem.get('som', 'False'),
                            'estado_ativar': warning_elem.get('estado_ativar', 'True'),
                            'desativar_bit': warning_elem.get('condToOff', ''),
                            'estado_desativar': warning_elem.get('estado_desativar', 'False')
                        }
                        self.warnings.append(warning_data)

                # Reconstruir controle de bits únicos
                self.rebuild_bits_registry()
                
                # Atualizar todas as listas
                self.update_signals_list()
                self.update_switches_list()
                self.update_blocks_list()
                self.update_warnings_list()
                # Contar itens carregados
                total_items = len(self.signals) + len(self.switches) + len(self.blocks) + len(self.warnings)

                # Mostrar mensagem de sucesso
                success_msg = f"Arquivo carregado com sucesso!\n\n"
                success_msg += f"Arquivo: {os.path.basename(filename)}\n\n"
                if self.signals:
                    success_msg += f"Sinais: {len(self.signals)}\n"
                if self.switches:
                    success_msg += f"Chaves: {len(self.switches)}\n"
                if self.blocks:
                    success_msg += f"Bloqueios: {len(self.blocks)}\n"
                if self.warnings:
                    success_msg += f"Avisos: {len(self.warnings)}\n"
                success_msg += f"\nTotal de itens: {total_items}"
                
                messagebox.showinfo("Sucesso", success_msg)
                
            except ET.ParseError as e:
                messagebox.showerror("Erro de XML", f"Erro ao fazer parsing do arquivo XML!\n\nO arquivo pode estar corrompido ou mal formatado.\n\nDetalhes: {str(e)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro inesperado ao carregar XML!\n\n{str(e)}")
                
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo não encontrado! \n\nVerifique se o arquivo ainda existe no local especificado.")
        except PermissionError:
            messagebox.showerror("Erro", "Erro de permissão! \n\nVerifique se você tem permissão para ler o arquivo.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado ao carregar arquivo! \n\n{str(e)}")


class SignalDialog:
    def __init__(self, parent, include_bits=True):
        self.parent = parent
        self.result = None
        self.include_bits = True  # Sempre incluir bits
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Adicionar Sinal - GEEEE")
        self.dialog.geometry("550x500")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Registrar função de validação para bits no dialog
        self.vcmd = (self.dialog.register(self.validate_bit_input), '%P')
        
        self.create_widgets()
        
        # Centralizar na tela
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def validate_bit_input(self, value):
        """Valida entrada de bits: apenas números positivos ou zero"""
        if value == "":  # Permite campo vazio
            return True
        try:
            num = int(value)
            return num >= 0  # Permite apenas números >= 0
        except ValueError:
            return False  # Rejeita texto não numérico

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.dialog, bg='#1e3a5f', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                               text="Configurar Sinal", 
                               font=('Segoe UI', 11, 'bold'),
                               fg='white', 
                               bg='#1e3a5f')
        header_label.pack(pady=12)
        
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nome
        name_frame = ttk.Frame(frame)
        name_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(name_frame, text="Nome do Sinal:", 
                 font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var, width=30, 
                 style='Custom.TEntry', font=('Segoe UI', 10)).pack(fill=tk.X)
        
        # Separador - sempre mostrar bits
        sep = ttk.Separator(frame, orient='horizontal')
        sep.pack(fill=tk.X, pady=(10, 15))
        
        # Label para seção de bits
        ttk.Label(frame, text="Configuração de Bits",
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Grid para bits
        bits_frame = ttk.Frame(frame)
        bits_frame.pack(fill=tk.X)
        
        # Primeira linha
        row1 = ttk.Frame(bits_frame)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        # ABRIR
        abrir_frame = ttk.Frame(row1)
        abrir_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        abrir_label = tk.Label(abrir_frame, text="● Bit ABRIR:", font=('Segoe UI', 9, 'bold'))
        abrir_label.pack(anchor=tk.W)
        self.abrir_var = tk.StringVar()
        ttk.Entry(abrir_frame, textvariable=self.abrir_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # FECHAR
        fechar_frame = ttk.Frame(row1)
        fechar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        fechar_label = tk.Label(fechar_frame, text="● Bit FECHAR:", font=('Segoe UI', 9, 'bold'))
        fechar_label.pack(anchor=tk.W)
        self.fechar_var = tk.StringVar()
        ttk.Entry(fechar_frame, textvariable=self.fechar_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # Segunda linha
        row2 = ttk.Frame(bits_frame)
        row2.pack(fill=tk.X, pady=(0, 10))
        
        # GREEN
        green_frame = ttk.Frame(row2)
        green_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        green_label = tk.Label(green_frame, text="● Bit GREEN:", font=('Segoe UI', 9, 'bold'), 
                              fg='#00AA00')
        green_label.pack(anchor=tk.W)
        self.green_var = tk.StringVar()
        ttk.Entry(green_frame, textvariable=self.green_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # YELLOW
        yellow_frame = ttk.Frame(row2)
        yellow_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        yellow_label = tk.Label(yellow_frame, text="● Bit YELLOW:", font=('Segoe UI', 9, 'bold'), 
                               fg="#AFAF00")
        yellow_label.pack(anchor=tk.W)
        self.yellow_var = tk.StringVar()
        ttk.Entry(yellow_frame, textvariable=self.yellow_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # Terceira linha
        row3 = ttk.Frame(bits_frame)
        row3.pack(fill=tk.X)
        
        # RED
        red_frame = ttk.Frame(row3)
        red_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        red_label = tk.Label(red_frame, text="● Bit RED:", font=('Segoe UI', 9, 'bold'), 
                            fg='#CC0000') # Vermelho
        red_label.pack(anchor=tk.W)
        self.red_var = tk.StringVar()
        ttk.Entry(red_frame, textvariable=self.red_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # BLUE
        blue_frame = ttk.Frame(row3)
        blue_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        blue_label = tk.Label(blue_frame, text="● Bit BLUE:", font=('Segoe UI', 9, 'bold'), 
                             fg='#0066CC')  # Azul
        blue_label.pack(anchor=tk.W)
        self.blue_var = tk.StringVar()
        ttk.Entry(blue_frame, textvariable=self.blue_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        row4 = ttk.Frame(bits_frame)
        row4.pack(fill=tk.X, pady=(10, 0))

        # FLASHRED
        flashred_frame = ttk.Frame(row4)
        flashred_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        flashred_label = tk.Label(flashred_frame, text="● Bit FLASHRED:", font=('Segoe UI', 9, 'bold'), 
                                  fg='#CC0000')  # Vermelho
        flashred_label.pack(anchor=tk.W)
        self.flashred_var = tk.StringVar()
        ttk.Entry(flashred_frame, textvariable=self.flashred_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)

        # Botões
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=(25, 0))
        
        # Centralizar botões
        center_buttons = ttk.Frame(buttons_frame)
        center_buttons.pack(anchor=tk.CENTER)
        
        ttk.Button(center_buttons, text="OK", 
                  command=self.ok_clicked, style='Success.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(center_buttons, text="Cancelar", 
                  command=self.cancel_clicked, style='Primary.TButton').pack(side=tk.LEFT)
    
    def ok_clicked(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Aviso", "Nome do sinal é obrigatório!")
            return
        
        result = {"name": self.name_var.get().strip().upper()}
        
        # Sempre incluir bits
        result.update({
            "abrir_bit": self.abrir_var.get().strip(),
            "fechar_bit": self.fechar_var.get().strip(),
            "green_bit": self.green_var.get().strip(),
            "yellow_bit": self.yellow_var.get().strip(),
            "red_bit": self.red_var.get().strip(),
            "blue_bit": self.blue_var.get().strip()
        })
        
        self.result = result
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()


class SwitchDialog:
    def __init__(self, parent, include_bits=True):
        self.parent = parent
        self.result = None
        self.include_bits = True  # Sempre incluir bits
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Adicionar Chave - GEEEE")
        self.dialog.geometry("550x400")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Registrar função de validação para bits no dialog
        self.vcmd = (self.dialog.register(self.validate_bit_input), '%P')
        
        self.create_widgets()
        
        # Centralizar na tela
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def validate_bit_input(self, value):
        """Valida entrada de bits: apenas números positivos ou zero"""
        if value == "":  # Permite campo vazio
            return True
        try:
            num = int(value)
            return num >= 0  # Permite apenas números >= 0
        except ValueError:
            return False  # Rejeita texto não numérico
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.dialog, bg='#1e3a5f', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                               text="Configurar Chave", 
                               font=('Segoe UI', 11, 'bold'),
                               fg='white', 
                               bg='#1e3a5f')
        header_label.pack(pady=12)
        
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nome
        name_frame = ttk.Frame(frame)
        name_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(name_frame, text="Nome da Chave:", 
                 font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var, width=30, 
                 style='Custom.TEntry', font=('Segoe UI', 10)).pack(fill=tk.X)
        
        # Separador - sempre mostrar bits
        sep = ttk.Separator(frame, orient='horizontal')
        sep.pack(fill=tk.X, pady=(10, 15))
        
        # Label para seção de bits
        ttk.Label(frame, text="Configuração de Bits", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Grid para bits
        bits_frame = ttk.Frame(frame)
        bits_frame.pack(fill=tk.X)
        
        # Primeira linha
        row1 = ttk.Frame(bits_frame)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        # NORMAL
        normal_frame = ttk.Frame(row1)
        normal_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        normal_label = tk.Label(normal_frame, text="● Bit NORMAL:", font=('Segoe UI', 9, 'bold'))
        normal_label.pack(anchor=tk.W)
        self.normal_var = tk.StringVar()
        ttk.Entry(normal_frame, textvariable=self.normal_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # REVERSO
        reverso_frame = ttk.Frame(row1)
        reverso_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        reverso_label = tk.Label(reverso_frame, text="● Bit REVERSO:", font=('Segoe UI', 9, 'bold'))
        reverso_label.pack(anchor=tk.W)
        self.reverso_var = tk.StringVar()
        ttk.Entry(reverso_frame, textvariable=self.reverso_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # Segunda linha
        row2 = ttk.Frame(bits_frame)
        row2.pack(fill=tk.X)
        
        # BLOQUEAR
        bloquear_frame = ttk.Frame(row2)
        bloquear_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        bloquear_label = tk.Label(bloquear_frame, text="● Bit BLOQUEAR:", font=('Segoe UI', 9, 'bold'), 
                                 fg='#CC0000')
        bloquear_label.pack(anchor=tk.W)
        self.bloquear_var = tk.StringVar()
        ttk.Entry(bloquear_frame, textvariable=self.bloquear_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # DESBLOQUEAR
        desbloquear_frame = ttk.Frame(row2)
        desbloquear_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        desbloquear_label = tk.Label(desbloquear_frame, text="● Bit DESBLOQUEAR:", font=('Segoe UI', 9, 'bold'), 
                                    fg='#00AA00')
        desbloquear_label.pack(anchor=tk.W)
        self.desbloquear_var = tk.StringVar()
        ttk.Entry(desbloquear_frame, textvariable=self.desbloquear_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # Botões
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=(25, 0))
        
        # Centralizar botões
        center_buttons = ttk.Frame(buttons_frame)
        center_buttons.pack(anchor=tk.CENTER)
        
        ttk.Button(center_buttons, text="OK", 
                  command=self.ok_clicked, style='Success.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(center_buttons, text="Cancelar", 
                  command=self.cancel_clicked, style='Primary.TButton').pack(side=tk.LEFT)
    
    def ok_clicked(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Aviso", "Nome da chave é obrigatório!")
            return
        
        result = {"name": self.name_var.get().strip().upper()}
        
        # Sempre incluir bits
        result.update({
            "normal_bit": self.normal_var.get().strip(),
            "reverso_bit": self.reverso_var.get().strip(),
            "bloquear_bit": self.bloquear_var.get().strip(),
            "desbloquear_bit": self.desbloquear_var.get().strip()
        })
        
        self.result = result
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()

class BlockDialog:
    def __init__(self, parent, include_bits=True):
        self.parent = parent
        self.result = None
        self.include_bits = True  # Sempre incluir bits
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Adicionar Bloqueio - GEEEE")
        self.dialog.geometry("550x400")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Registrar função de validação para bits no dialog
        self.vcmd = (self.dialog.register(self.validate_bit_input), '%P')
        
        self.create_widgets()
        
        # Centralizar na tela
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def validate_bit_input(self, value):
        """Valida entrada de bits: apenas números positivos ou zero"""
        if value == "":  # Permite campo vazio
            return True
        try:
            num = int(value)
            return num >= 0  # Permite apenas números >= 0
        except ValueError:
            return False  # Rejeita texto não numérico

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.dialog, bg='#1e3a5f', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                               text="Configurar Bloqueio", 
                               font=('Segoe UI', 11, 'bold'),
                               fg='white', 
                               bg='#1e3a5f')
        header_label.pack(pady=12)
        
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nome
        name_frame = ttk.Frame(frame)
        name_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(name_frame, text="Nome do Bloqueio:", 
                 font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var, width=30, 
                 style='Custom.TEntry', font=('Segoe UI', 10)).pack(fill=tk.X)
        
        # Separador - sempre mostrar bits
        sep = ttk.Separator(frame, orient='horizontal')
        sep.pack(fill=tk.X, pady=(10, 15))
        
        # Label para seção de bits
        ttk.Label(frame, text="Configuração de Bits", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Grid para bits
        bits_frame = ttk.Frame(frame)
        bits_frame.pack(fill=tk.X)
        
        # Primeira linha
        row1 = ttk.Frame(bits_frame)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        # BLOQUEAR
        bloquear_frame = ttk.Frame(row1)
        bloquear_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        bloquear_label = tk.Label(bloquear_frame, text="● Bit BLOQUEAR:", font=('Segoe UI', 9, 'bold'), fg='#CC0000')
        bloquear_label.pack(anchor=tk.W)
        self.bloquear_var = tk.StringVar()
        ttk.Entry(bloquear_frame, textvariable=self.bloquear_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # DESBLOQUEAR
        desbloquear_frame = ttk.Frame(row1)
        desbloquear_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        desbloquear_label = tk.Label(desbloquear_frame, text="● Bit DESBLOQUEAR:", font=('Segoe UI', 9, 'bold'), fg='#00AA00')
        desbloquear_label.pack(anchor=tk.W)
        self.desbloquear_var = tk.StringVar()
        ttk.Entry(desbloquear_frame, textvariable=self.desbloquear_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # Segunda linha
        row2 = ttk.Frame(bits_frame)
        row2.pack(fill=tk.X)
        
        # BLUE
        blue_frame = ttk.Frame(row2)
        blue_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        blue_label = tk.Label(blue_frame, text="● Bit BLUE:", font=('Segoe UI', 9, 'bold'), 
                             fg='#0066CC')  # Azul
        blue_label.pack(anchor=tk.W)
        self.blue_var = tk.StringVar()
        ttk.Entry(blue_frame, textvariable=self.blue_var, width=15, style='Custom.TEntry', 
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # Botões
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=(25, 0))
        
        # Centralizar botões
        center_buttons = ttk.Frame(buttons_frame)
        center_buttons.pack(anchor=tk.CENTER)
        
        ttk.Button(center_buttons, text="OK", 
                  command=self.ok_clicked, style='Success.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(center_buttons, text="Cancelar", 
                  command=self.cancel_clicked, style='Primary.TButton').pack(side=tk.LEFT)

    def ok_clicked(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Aviso", "Nome do bloqueio é obrigatório!")
            return
        
        result = {"name": self.name_var.get().strip().upper()}
        
        # Sempre incluir bits
        result.update({
            "bloquear_bit": self.bloquear_var.get().strip(),
            "desbloquear_bit": self.desbloquear_var.get().strip(),
            "blue_bit": self.blue_var.get().strip()
        })
        
        self.result = result
        self.dialog.destroy()

    def cancel_clicked(self):
        self.dialog.destroy()

class WarningDialog:
    def __init__(self, parent, include_bits=True):
        self.parent = parent
        self.result = None
        self.include_bits = True  # Sempre incluir bits
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Adicionar Aviso - GEEEE")
        self.dialog.geometry("550x450")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Registrar função de validação para bits no dialog
        self.vcmd = (self.dialog.register(self.validate_bit_input), '%P')
        
        self.create_widgets()
        
        # Centralizar na tela
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def validate_bit_input(self, value):
        """Valida entrada de bits: apenas números positivos ou zero"""
        if value == "":  # Permite campo vazio
            return True
        try:
            num = int(value)
            return num >= 0  # Permite apenas números >= 0
        except ValueError:
            return False  # Rejeita texto não numérico

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.dialog, bg='#1e3a5f', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                               text="Configurar Aviso", 
                               font=('Segoe UI', 11, 'bold'),
                               fg='white', 
                               bg='#1e3a5f')
        header_label.pack(pady=12)
        
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nome
        name_frame = ttk.Frame(frame)
        name_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(name_frame, text="Descrição do Aviso:", 
                 font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var, width=30, 
                 style='Custom.TEntry', font=('Segoe UI', 10)).pack(fill=tk.X)
        
        # Separador - sempre mostrar bits
        sep = ttk.Separator(frame, orient='horizontal')
        sep.pack(fill=tk.X, pady=(10, 15))
        
        # Label para seção de bits
        ttk.Label(frame, text="Configuração de Bits", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Grid para bits
        bits_frame = ttk.Frame(frame)
        bits_frame.pack(fill=tk.X)
        
        # Primeira linha
        row1 = ttk.Frame(bits_frame)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        # ATIVAR
        ativar_frame = ttk.Frame(row1)
        ativar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ativar_label = tk.Label(ativar_frame, text="● Bit ATIVAR:", font=('Segoe UI', 9, 'bold'))
        ativar_label.pack(anchor=tk.W)
        self.ativar_var = tk.StringVar()
        ttk.Entry(ativar_frame, textvariable=self.ativar_var, style='Custom.TEntry', width=5,
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # ESTADO ATIVAR
        estado_ativar_frame = ttk.Frame(row1)
        estado_ativar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        estado_ativar_label = tk.Label(estado_ativar_frame, text="ESTADO PARA ATIVAR:", font=('Segoe UI', 9, 'bold'))
        estado_ativar_label.pack(anchor=tk.W)
        self.estado_ativar_var = tk.StringVar(value="True")
        tk.Checkbutton(estado_ativar_frame, text="ATIVO", variable=self.estado_ativar_var, onvalue="True", offvalue="False").pack(anchor=tk.W)
        
        # Segunda linha
        row2 = ttk.Frame(bits_frame)
        row2.pack(fill=tk.X)
        
        # DESATIVAR
        desativar_frame = ttk.Frame(row2)
        desativar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        desativar_label = tk.Label(desativar_frame, text="● Bit DESATIVAR:", font=('Segoe UI', 9, 'bold'))
        desativar_label.pack(anchor=tk.W)
        self.desativar_var = tk.StringVar()
        ttk.Entry(desativar_frame, textvariable=self.desativar_var, style='Custom.TEntry', width=5,
                 validate='key', validatecommand=self.vcmd).pack(fill=tk.X)
        
        # ESTADO DESATIVAR
        estado_desativar_frame = ttk.Frame(row2)
        estado_desativar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        estado_desativar_label = tk.Label(estado_desativar_frame, text="ESTADO PARA DESATIVAR:", font=('Segoe UI', 9, 'bold'))
        estado_desativar_label.pack(anchor=tk.W)
        self.estado_desativar_var = tk.StringVar(value="True")
        tk.Checkbutton(estado_desativar_frame, text="ATIVO", variable=self.estado_desativar_var, onvalue="True", offvalue="False").pack(anchor=tk.W)

        # Terceira linha
        row3 = ttk.Frame(bits_frame)
        row3.pack(anchor=tk.CENTER)

        estado_som = ttk.Frame(row3)
        estado_som.pack(side=tk.LEFT, fill=tk.X, expand=True)
        estado_som_label = tk.Label(estado_som, text="ESTADO PARA O SOM:", font=('Segoe UI', 9, 'bold'))
        estado_som_label.pack(anchor=tk.W)
        self.som_estado = tk.StringVar(value="True")
        tk.Checkbutton(estado_som, text="ATIVO", variable=self.som_estado, onvalue="True", offvalue="False").pack(anchor=tk.W)

        # Botões
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=(25, 0))
        
        # Centralizar botões
        center_buttons = ttk.Frame(buttons_frame)
        center_buttons.pack(anchor=tk.CENTER)
        
        ttk.Button(center_buttons, text="OK", 
                  command=self.ok_clicked, style='Success.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(center_buttons, text="Cancelar", 
                  command=self.cancel_clicked, style='Primary.TButton').pack(side=tk.LEFT)

    def ok_clicked(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Aviso", "Descrição do aviso é obrigatória!")
            return
        
        result = {"name": self.name_var.get().strip().upper()}
        
        # Sempre incluir bits
        result.update({
            "ativar_bit": self.ativar_var.get().strip(),
            "estado_ativar": self.estado_ativar_var.get(),
            "som": self.som_estado.get(),
            "desativar_bit": self.desativar_var.get().strip(),
            "estado_desativar": self.estado_desativar_var.get()
        })
        
        self.result = result
        self.dialog.destroy()

    def cancel_clicked(self):
        self.dialog.destroy()

class CustomDialog:
    def __init__(self, parent, include_bits=True):
        self.parent = parent
        self.result = None
        self.include_bits = True  # Sempre incluir bits
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Adicionar Opção Customizada - GEEEE")
        self.dialog.geometry("400x200")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Registrar função de validação para bits no dialog
        self.vcmd = (self.dialog.register(self.validate_bit_input), '%P')
        
        self.create_widgets()
        
        # Centralizar na tela
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def validate_bit_input(self, value):
        """Valida entrada de bits: apenas números positivos ou zero"""
        if value == "":  # Permite campo vazio
            return True
        try:
            num = int(value)
            return num >= 0  # Permite apenas números >= 0
        except ValueError:
            return False  # Rejeita texto não numérico

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.dialog, bg='#1e3a5f', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                               text="Configurar Opção Customizada", 
                               font=('Segoe UI', 11, 'bold'),
                               fg='white', 
                               bg='#1e3a5f')
        header_label.pack(pady=12)
        
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nome
        name_frame = ttk.Frame(frame)
        name_frame.pack(fill=tk.X, pady=(0, 15))

        fields_frame = ttk.Frame(name_frame)
        fields_frame.pack(fill=tk.X)

        self.name_var = tk.StringVar()
        ttk.Label(fields_frame, text="Nome da Opção:", font=('Segoe UI', 10)).grid(
            row=0, column=0, sticky=tk.W
        )
        ttk.Entry(
            fields_frame,
            textvariable=self.name_var,
            width=15,
            style='Custom.TEntry',
            font=('Segoe UI', 10),
        ).grid(row=0, column=1, sticky=tk.W, padx=(6, 18))

        self.bit_var = tk.StringVar()
        ttk.Label(fields_frame, text="Bit:", font=('Segoe UI', 10)).grid(
            row=0, column=2, sticky=tk.W
        )
        ttk.Entry(
            fields_frame,
            textvariable=self.bit_var,
            width=5,
            style='Custom.TEntry',
            font=('Segoe UI', 10),
            validatecommand=self.vcmd,
        ).grid(row=0, column=3, sticky=tk.W, padx=(6, 0))
        
        # Botões
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=(25, 0))
        
        # Centralizar botões
        center_buttons = ttk.Frame(buttons_frame)
        center_buttons.pack(anchor=tk.CENTER)
        
        ttk.Button(center_buttons, text="OK", 
                  command=self.ok_clicked, style='Success.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(center_buttons, text="Cancelar", 
                  command=self.cancel_clicked, style='Primary.TButton').pack(side=tk.LEFT)

    def ok_clicked(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Aviso", "Nome da opção é obrigatório!")
            return
        
        result = {"name": self.name_var.get().strip().upper()}
        
        # Sempre incluir bits
        result.update({
            "custom_bits": self.bit_var.get()
        })
        
        self.result = result
        self.dialog.destroy()

    def cancel_clicked(self):
        self.dialog.destroy()

if __name__ == "__main__":
    try:
        print("Iniciando aplicação...")
        root = tk.Tk()
        print("Janela principal criada...")
        app = XMLGenerator(root)
        print("Interface criada com sucesso! Iniciando loop principal...")
        root.mainloop()
    except Exception as e:
        print(f"Erro ao executar aplicação: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")
