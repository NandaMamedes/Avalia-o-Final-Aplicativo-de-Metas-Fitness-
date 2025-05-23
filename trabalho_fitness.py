print('oi')
print('oi')

# Avaliação Final - POO

# Tema:

# 4. Aplicativo de Metas Fitness

# Objetivo: Crie uma aplicação que monitore exercícios e dietas.

# ● Classes: Usuario, Exercicio, Dieta.
# ● Features: calcular calorias, progresso semanal, etc
# ● Extra: Dashboard com gráficos

import hashlib
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

def conectar_banco():
    return sqlite3.connect("BD_Fitness.db")

def criar_tabelas():
    conexao_fitness = conectar_banco()
    cursor_fitness = conexao_fitness.cursor()

    cursor_fitness.execute('''
        CREATE TABLE IF NOT EXISTS Cadastros (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Email TEXT NOT NULL,
            Senha TEXT NOT NULL
        )
    ''')
    
    cursor_fitness.execute('''
        CREATE TABLE IF NOT EXISTS Usuarios (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Cadastro_ID INTEGER,
            Nome TEXT NOT NULL,
            Email_Cadastro TEXT NOT NULL,
            Idade INTEGER,
            Sexo TEXT NOT NULL,
            Altura TEXT NOT NULL,
            Peso REAL,
            Objetivo TEXT NOT NULL,
            Nivel_Atividade TEXT NOT NULL,
            Metas TEXT NOT NULL,
            FOREIGN KEY (Cadastro_ID) REFERENCES Cadastros (ID)
            FOREIGN KEY (Email_Cadastro) REFERENCES Cadastros (Email)
        )
    ''')

    cursor_fitness.execute('''
        CREATE TABLE IF NOT EXISTS Exercicios (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Usuario_ID INTEGER,
            Nome_Exercicio TEXT NOT NULL,
            Tipo_Exercicio TEXT NOT NULL,
            Duracao TEXT NOT NULL,
            Intensidade TEXT NOT NULL,
            Calorias_Queimadas REAL,
            FOREIGN KEY (Usuario_ID) REFERENCES Usuarios (ID)
        )
    ''')

    cursor_fitness.execute('''
        CREATE TABLE IF NOT EXISTS Dietas (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Usuario_ID INTEGER,
            Nome_Dieta TEXT NOT NULL,
            Tipo_Dieta TEXT NOT NULL,
            Calorias_Diarias REAL,
            FOREIGN KEY (Usuario_ID) REFERENCES Usuarios(ID)
        )
    ''')

    conexao_fitness.commit()
    conexao_fitness.close()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

class Usuario:
    def __init__(self, nome_usuario, email, idade, sexo, altura, peso, objetivo, nivel_atividade, metas):
        self.nome_usuario = nome_usuario
        self.email = email
        self.idade = idade
        self.sexo = sexo
        self.altura = altura
        self.peso = peso
        self.objetivo = objetivo
        self.nivel_atividade = nivel_atividade
        self.metas = metas
        
    def cadastrar_usuario(self):
        pass
    
    def atualizar_perfil(self):
        pass
    
    def definir_meta(self):
        pass
    
    def visualizar_progresso(self):
        pass
    
    def receber_notificacao(self):
        pass
    
    
class Exercicio:
    def __init__(self, nome_exercicio, tipo_exercicio , duracao, intensidade, calorias_queimadas):
        self.nome_exercicio = nome_exercicio
        self.tipo_exercicio = tipo_exercicio
        self.duracao = duracao
        self.intensidade = intensidade
        self.calorias_queimadas = calorias_queimadas
    
    def cadastrar_exercicio(self):
        pass
    
    def visualizar_exercicio(self):
        pass
    
    def realizar_exercicio(self):
        pass
    
    def calcular_calorias_queimadas(self):
        pass
    
        
class Dieta:
    def __init__(self, nome_dieta, tipo_dieta, calorias_diarias, macronutrientes, alimentos_permitidos, alimentos_proibidos):
        self.nome_dieta = nome_dieta
        self.tipo_dieta = tipo_dieta
        self.calorias_diarias = []
        self.macronutrientes = {}
        self.alimentos_permitidos = []
        self.alimentos_proibidos = []
        
    def cadastrar_dieta(self):
        pass
    
    def visualizar_dieta(self):
        pass
    
    def seguir_dieta(self):
        pass
    
    def calcular_calorias_diarias(self):
        pass


def sistema(usuario_id, email):
    conexao_fitness = conectar_banco()
    cursor_fitness = conexao_fitness.cursor()
                    
    cursor_fitness.execute(
    "SELECT Cadastro_ID, Nome, Email_Cadastro, Idade, Sexo, Altura, Peso, Objetivo, Nivel_Atividade, Metas FROM Usuarios WHERE Email = ?",
    (email,)
    )
    usuario = cursor_fitness.fetchone()
    
    if usuario:
        id_usuario, nome, email, idade, sexo, altura, peso, objetivo, nivel_atividade, metas = usuario
        st.subheader(f"Olá, {nome}!")
        st.markdown("---")
        st.header("📊 Seus últimos resultados")
        st.markdown("---")
        
        conexao_fitness = conectar_banco()
        cursor_fitness = conexao_fitness.cursor()
        
        df_exercicios = pd.read_sql("SELECT * FROM Exercicios WHERE UsuarioID = ?", conexao_fitness, params=(id_usuario,))
        df_dietas = pd.read_sql("SELECT * FROM Dietas WHERE UsuarioID = ?", conexao_fitness, params=(id_usuario,))
        
    else:
        st.subheader("Informações Pessoais")
        nome = st.text_input("Digite seu nome:", placeholder="Seu nome aqui")
        idade = st.number_input("Idade:", min_value=0, max_value=120, value=25)
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
        altura = st.slider("Altura (em metros):", 1.0, 2.5, 1.70)
        peso = st.slider("Peso (em Quilogramas):", 1.0, 2.5, 65)
        objetivo = st.selectbox("Objetivo", ["Ganhar massa muscular", "Perder massa"])
        nivel_atividade = st.selectbox("Nível de Atividade", ["Ativo", "Moderado", "Sedentario"])
        metas = st.text_input("Metas específicas")
        data_referencia = st.date_input("🗕️ Data de referência dos dados")
        mes_ano = data_referencia.strftime("%m/%Y")
        
        if st.button("Continuar"):
            st.subheader("Realizar Exercício ou Dieta:")
            modo = st.radio("", ["Exercício", "Dieta"], horizontal=True)
            if modo == "Exercício":
                st.subheader("🧾 Pagamento com Boleto")
            cpf = st.text_input("CPF do Sacado", placeholder="xxx.xxx.xxx-xx")
            nome = st.text_input("Nome do Sacado")
            vencimento = st.text_input("Data de Vencimento (DD/MM/AAAA)")
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor", min_value=0.01, step=0.01)

            if st.button("🧾 Gerar Boleto"):
                st.subheader("2 - Informações Financeiras")
            renda_mensal = st.number_input("Renda mensal (R$):", min_value=0.0, step=0.01)
            gastos_moradia = st.number_input("Gastos com moradia (R$):", min_value=0.0, step=0.01)
            gastos_alimentacao = st.number_input("Gastos com alimentação (R$):", min_value=0.0, step=0.01)
            gastos_contas = st.number_input("Gastos com contas básicas (R$):", min_value=0.0, step=0.01)
            gastos_transporte = st.number_input("Gastos com transporte (R$):", min_value=0.0, step=0.01)
            gastos_saude = st.number_input("Gastos com saúde (R$):", min_value=0.0, step=0.01)
            gastos_lazer = st.number_input("Gastos com lazer (R$):", min_value=0.0, step=0.01)
            tem_dividas = st.checkbox("Possui dívidas?")
        
        
        
            
def validar_email(email):
    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "E-mail inválido"
    return True, ""


st.set_page_config(page_title="🏋️‍♂️ Metas Fitness", layout="wide")
st.title("Fitness MaMaJu")
st.caption("Aplicativo de monitoramento de exercícios e dietas.")
st.markdown("---")

criar_tabelas()

# if "logado" not in st.session_state:
#     st.session_state.logado = False
#     st.session_state.usuario_id = None
#     st.session_state.email = ""

# if not st.session_state.logado:
#     st.subheader("🔐 Login ou Cadastro")
#     col1, col2 = st.columns(2)

#     with col1:
#         modo = st.radio("Modo", ["Login", "Cadastro"])
#         email = st.text_input("E-mail")
#         senha = st.text_input("Senha", type="password")
#         if modo == "Login":
#             if st.button("Confirmar"):
#                 if not email or not senha:
#                     st.warning("Preencha todos os campos.")
#                 else:
#                     conexao_fitness = conectar_banco()
#                     cursor_fitness = conexao_fitness.cursor()
#                     senha_hash = hash_senha(senha)
                    
#                     email_valido, mensagem_email = validar_email(email)
                    
#                     if not email_valido:
#                         st.error(mensagem_email)
#                     else:
#                         cursor_fitness.execute("SELECT ID FROM Cadastros WHERE Email = ? AND Senha = ?", (email, senha_hash))
#                         usuario = cursor_fitness.fetchone()
#                         if usuario:
#                             st.session_state.logado = True
#                             st.session_state.usuario_id = usuario[0]
#                             st.session_state.email = email
#                             st.success("Login realizado com sucesso.")
#                             st.rerun()
#                         else:
#                             st.error("Usuário ou senha inválidos.")
#         elif modo == "Cadastro":
            
        
        
        
if "logado" not in st.session_state:
    st.session_state.logado = False
if "email_usuario" not in st.session_state:
    st.session_state.email_usuario = ""
if "senha_usuario" not in st.session_state:
    st.session_state.senha_usuario = ""
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None

if not st.session_state.logado:
    st.subheader("🔐 Login ou Cadastro")
    col1, col2 = st.columns(2)
    
    with col1:
        modo = st.radio("Modo", ["Login", "Cadastro"])
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        
        if modo == "Fazer Login":
            if st.button("Entrar"):
                if not email or not senha:
                    st.warning("⚠️ Preencha todos os campos.")
                else:
                    conexao_fitness = conectar_banco()
                    cursor_fitness = conexao_fitness.cursor()
                    
                    cursor_fitness.execute(
                        "SELECT ID FROM Cadastros WHERE Email = ? AND Senha = ?",
                        (email, senha)
                        )
                    usuario = cursor_fitness.fetchone()
                    
                    if usuario:
                        st.session_state.logado = True
                        st.session_state.email_usuario = email
                        st.session_state.senha_usuario = senha
                        st.session_state.usuario_id = usuario[0]
                        st.success("✅ Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ E-mail ou senha incorretos.")
        
        elif modo == "Cadastro":
            if senha and not senha.isalnum():
                st.warning("⚠️ A senha deve conter apenas letras e números.")
            elif st.button("Cadastrar"):
                if not email or not senha:
                    st.warning("⚠️ Preencha todos os campos.")
                else:
                    conexao_fitness = conectar_banco()
                    cursor_fitness = conexao_fitness.cursor()
                    senha_hash = hash_senha(senha)
                    
                    email_valido, mensagem_email = validar_email(email)
                    
                    if not email_valido:
                        st.error(mensagem_email)
                    else:
                        cursor_fitness.execute("SELECT * FROM Cadastros WHERE Email = ?", (email,))
                        if cursor_fitness.fetchone():
                            st.warning("E-mail já cadastrado.")
                        else:
                            cursor_fitness.execute("INSERT INTO Cadastros (Email, Senha) VALUES (?, ?)",(email, senha_hash))
                            conexao_fitness.commit()
                            
                            cursor_fitness.execute("SELECT ID FROM Cadastros WHERE Email = ?", (email,))
                            novo_usuario = cursor_fitness.fetchone()
                            
                            st.session_state.logado = True
                            st.session_state.email_usuario = email
                            st.session_state.senha_usuario = senha
                            st.session_state.usuario_id = novo_usuario[0]
                            st.success("✅ Cadastro realizado com sucesso!")
                            st.rerun()
                        
else:
    sistema(st.session_state.usuario_id, st.session_state.email_usuario)