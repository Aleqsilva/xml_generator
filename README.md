# XML Generator — Control Panel Configurator

> Ferramenta desktop para parametrização *No-Code*, mapeamento de I/O de bits e geração automatizada de esquemas XML para painéis de controle ferroviários.

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter%20Pure-blue?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)
[![Role](https://img.shields.io/badge/Focus-Reliability%20%26%20Field%20Safety-red?style=for-the-badge)](#)

---

<img width="901" height="927" alt="image" src="https://github.com/user-attachments/assets/b4634d5c-d474-4d4c-95a6-e0fcc3ccd0d9" />

## Sobre o Projeto

O **XML Generator** foi o primeiro software desenvolvido durante minha atuação na MRS Logística. O objetivo foi resolver gargalos operacionais e erros recorrentes na configuração de painéis de controle em campo.

Os painéis de controle dependiam de arquivos XML externos extensos e propensos a falhas manuais. Em operações de campo, técnicos muitas vezes precisavam alterar parâmetros sem ter domínio da estrutura do código XML, criando riscos de paradas ou comportamentos imprevistos. 

Esta aplicação elimina a necessidade de edição direta de código, fornecendo uma interface visual onde o usuário atribui diretamente bits e propriedades aos elementos da via.

---

## Problema vs. Solução

| Cenário Anterior (Manual) | Solução com XML Generator |
| :--- | :--- |
| Edição manual de arquivos XML complexos em campo. | Interface visual *No-Code* para adição de elementos. |
| Alto risco de conflito/duplicação de bits de controle. | Motor de validação automática que impede atribuições duplicadas. |
| Dependência de programadores para alterar configurações. | Autonomia total para a equipe técnica de campo. |
| Incerteza na atribuição de estados de sinais e chaves. | Mapeamento explícito de estados (Verde/Vermelho, Normal/Reverso). |

---

## Principais Funcionalidades

* **Mapeamento de Sinais e Chaves de Via:**
  * Configuração de estados de sinalização (ex.: bits para acionamento de Verde, Vermelho, Azul, etc.).
  * Atribuição de estados para AMVs/Chaves (Posição Normal, Posição Reversa e Bloqueios).
* **Separação Lógica de I/O de Bits:**
  * **Bits de Comando:** Atribuição de acionamentos e ordens enviadas ao sistema.
  * **Bits de Interação/Status:** Atribuição de retornos e mudanças de estado recebidas do campo.
* **Validação Preventiva de Interferência:**
  * Checagem em tempo real de campos e valores permitidos.
  * Impedimento estrito de bits duplicados para evitar sobreposição ou interferência de sinais.
* **Geração Automática de XML:** Exportação da estrutura válida pronta para consumo pelo painel de controle executável.

---

## Engenharia e Arquitetura

Como projeto inicial do ecossistema de ferramentas desenvolvidas, o **XML Generator** serviu como prova de conceito (PoC) para o tratamento de estruturas complexas e parsing de dados, abrindo caminho para soluções posteriores mais avançadas (como o *Praxis*).

### Destaques Técnicos:
* **Interface 100% Nativa (Pure Tkinter):** Desenvolvimento completo da interface visual utilizando apenas recursos nativos do Python, garantindo uma aplicação leve e sem dependências externas.
* **Parsing & Serialização XML:** Tratamento e validação de nós XML para garantir total compatibilidade com o software leitor do painel.
* **Mecanismo Anti-Colisão de Bits:** Algoritmo simples e eficiente para verificar se um mesmo bit está sendo utilizado simultaneamente por mais de uma função.

---

<img width="1196" height="934" alt="image" src="https://github.com/user-attachments/assets/d98e8cb9-8d15-4c6e-8967-d0b21b7573b5" />


## Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **GUI:** Tkinter / TTK (Biblioteca padrão do Python)
* **Manipulação de Dados/XML:** `xml.etree.ElementTree`
* **Estruturas de Validação:** Dicionários e Conjuntos (`set`) para verificação O(1) de duplicidade de bits.

---

## Como Executar

```bash
# 1. Clonar o repositório
git clone https://github.com/Aleqsilva/xml_generator

# 2. Entrar na pasta do projeto
cd xml_generator

# 3. Executar o projeto
python xml_generator.py
