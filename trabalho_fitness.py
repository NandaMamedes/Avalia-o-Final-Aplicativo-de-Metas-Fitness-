# Avaliação Final - POO

# Tema:

# 4. Aplicativo de Metas Fitness

# Objetivo: Crie uma aplicação que monitore exercícios e dietas.

# ● Classes: Usuario, Exercicio, Dieta.
# ● Features: calcular calorias, progresso semanal, etc
# ● Extra: Dashboard com gráficos

# python -m streamlit run trabalho_fitness.py

import re
import hashlib
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# Momento Banco de Dados SQLite - Fernanda

# Criação do Banco de Dados

def conectar_banco():
    return sqlite3.connect("fitness.db")

# Tabelas do Banco de Dados

def criar_tabelas():
    with conectar_banco() as conexao:
        cursor = conexao.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Cadastros (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Email TEXT NOT NULL,
                Senha TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Usuarios (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Cadastro_ID INTEGER,
                Nome TEXT NOT NULL,
                Idade INTEGER,
                Sexo TEXT NOT NULL,
                Altura TEXT NOT NULL,
                Peso REAL,
                Objetivo TEXT NOT NULL,
                Nivel_Atividade TEXT NOT NULL,
                Metas TEXT NOT NULL,
                FOREIGN KEY (Cadastro_ID) REFERENCES Cadastros(ID)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Exercicios (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Usuario_ID INTEGER,
                Nome_Exercicio TEXT NOT NULL,
                Tipo_Exercicio TEXT NOT NULL,
                Duracao INTEGER NOT NULL,
                Intensidade TEXT NOT NULL,
                Calorias_Queimadas REAL,
                Data_Exercicio TEXT NOT NULL,
                FOREIGN KEY (Usuario_ID) REFERENCES Usuarios(ID)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Dietas (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Usuario_ID INTEGER,
                Nome_Dieta TEXT NOT NULL,
                Tipo_Dieta TEXT NOT NULL,
                Calorias_Diarias REAL,
                Macronutrientes TEXT NOT NULL,
                Data_Dieta TEXT NOT NULL,
                FOREIGN KEY (Usuario_ID) REFERENCES Usuarios(ID)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Historico_Peso (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Usuario_ID INTEGER,
                Nome_Usuario TEXT NOT NULL,
                Peso REAL NOT NULL,
                Data_Peso TEXT NOT NULL,
                FOREIGN KEY (Usuario_ID) REFERENCES Usuarios(ID)
        )
    ''')

# Camuflar senha do usuario no banco de dados

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Validar email no sistema de login

def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Classes

class Usuario:
    def __init__(self, cadastro_id, nome, idade, sexo, altura, peso, objetivo, nivel_atividade, metas):
        self.cadastro_id = cadastro_id
        self.nome = nome
        self.idade = idade
        self.sexo = sexo
        self.altura = altura
        self.peso = peso
        self.objetivo = objetivo
        self.nivel_atividade = nivel_atividade
        self.metas = metas

    def calcular_imc(self):
        try:
            altura_m = float(self.altura)
            imc = round(self.peso / (altura_m ** 2), 2)
            return imc
        except:
            return None

class Exercicio:
    def __init__(self, usuario_id, nome_exercicio, tipo_exercicio, duracao, intensidade):
        self.usuario_id = usuario_id
        self.nome_exercicio = nome_exercicio
        self.tipo_exercicio = tipo_exercicio
        self.duracao = duracao
        self.intensidade = intensidade
        self.calorias_queimadas = 0

    def calcular_calorias_queimadas(self, peso):
        met_values = {"Leve": 3.0, "Moderada": 5.0, "Intensa": 8.0}
        met_intensidade = met_values.get(self.intensidade, 5.0)
        tempo_em_horas = self.duracao / 60
        self.calorias_queimadas = round(met_intensidade * peso * tempo_em_horas, 2)
        return self.calorias_queimadas

    def novo_peso_exercicio(self):
        try:
            with conectar_banco() as conexao:
                cursor = conexao.cursor()
                cursor.execute("SELECT Peso FROM Usuarios WHERE ID = ?", (self.usuario_id,))
                peso_atual = cursor.fetchone()
                if peso_atual:
                    novo_peso = peso_atual[0] - (self.calorias_queimadas / 7700)
                    return round(novo_peso, 2)
        except Exception as erro:
            print(f"Erro ao calcular novo peso: {erro}")
            return None

class Dieta:
    def __init__(self, usuario_id, nome_dieta, tipo_dieta, calorias_diarias, macronutrientes, objetivo):
        self.usuario_id = usuario_id
        self.nome_dieta = nome_dieta
        self.tipo_dieta = tipo_dieta
        self.calorias_diarias = calorias_diarias or self.calcular_calorias_diarias()
        self.macronutrientes = macronutrientes
        self.objetivo = objetivo

    def calcular_calorias_diarias(self):
        try:
            # Ganhar massa
            if self.objetivo == "Ganhar massa muscular":
                return {"Proteínas": 2000, "Carboidratos": 1800, "Gorduras": 2200}.get(self.macronutrientes, 2200)
            # Perder gordura
            elif self.objetivo == "Perder gordura":
                return {"Proteínas": 1500, "Carboidratos": 1300, "Gorduras": 1800}.get(self.macronutrientes, 1300)     
            # Manter forma
            elif self.objetivo == "Manter forma":
                return {"Proteínas": 1350, "Carboidratos": 1800, "Gorduras": 1500}.get(self.macronutrientes, 1500)
                
        except Exception as erro:
            print(f"Erro ao calcular calorias diárias: {erro}")
            return None

    def novo_peso_dieta(self, calorias):
        try:
            with conectar_banco() as conexao:
                cursor = conexao.cursor()
                cursor.execute("SELECT Peso FROM Usuarios WHERE ID = ?", (self.usuario_id,))
                peso_atual = cursor.fetchone()
                if peso_atual:
                    if self.objetivo == "Ganhar massa muscular":
                        novo_peso = peso_atual[0] + (calorias / 7700)
                    elif self.objetivo == "Perder gordura":
                        novo_peso = peso_atual[0] - (calorias / 7700)
                    elif self.objetivo == "Manter forma":
                        novo_peso = peso_atual[0] + (calorias / 7700) - (calorias / 5500)
                    return round(novo_peso, 2)
        except Exception as erro:
            print(f"Erro ao calcular novo peso: {erro}")
            return None
        

# Momento Dashboard ou Métricas - Jucilene

def analise_dados(id_usuario):
    with conectar_banco() as conexao:
        tab1, tab2 = st.tabs(["📜 Tabelas com Informações do Usuário", "📈 Gráficos dos Exercícios/Dietas"])
        
        with tab1:
            # Tabelas com informações do Usuário

            modo_tabelas = st.radio("Escolha Tipo de Tabela:", ["Histórico de Exercícios", "Histórico de Dietas", "Histórico de Peso"], horizontal=True)

            if modo_tabelas == "Histórico de Exercícios":
                df_exercicios = pd.read_sql("SELECT * FROM Exercicios WHERE Usuario_ID = ?", conectar_banco(), params=(id_usuario,))
                st.subheader("Histórico de Exercícios")
                st.dataframe(df_exercicios if not df_exercicios.empty else pd.DataFrame(["Sem exercícios registrados."]))

            elif modo_tabelas == "Histórico de Dietas":
                df_dietas = pd.read_sql("SELECT * FROM Dietas WHERE Usuario_ID = ?", conectar_banco(), params=(id_usuario,))
                st.subheader("Histórico de Dietas")
                st.dataframe(df_dietas if not df_dietas.empty else pd.DataFrame(["Sem dietas registradas."]))

            elif modo_tabelas == "Histórico de Peso":
                df_historico = pd.read_sql("SELECT * FROM Historico_Peso WHERE Usuario_ID = ?", conectar_banco(), params=(id_usuario,))
                st.subheader("Histórico de Peso")
                st.dataframe(df_historico if not df_historico.empty else pd.DataFrame(["Nenhuma informação inserida ainda."]))
            
        with tab2:
            modo_graficos = st.radio("Escolha Tipo de Gráfico:", ["Evolução do Peso", "Tipos de Exercícios mais escolhidos", "Tipos de Dietas mais escolhidos", "Macronutrientes mais consumidos"], horizontal=True)
            
            if modo_graficos == "Evolução do Peso":
                # Gráfico de Linha - Evolução do Peso
                
                df_linha_tempo = pd.read_sql_query(
                    "SELECT Data_Peso, Peso FROM Historico_Peso WHERE Usuario_ID = ? ORDER BY Data_Peso",conexao,params=(id_usuario,))
                
                if df_linha_tempo.empty:
                    st.info("📭 Nenhum dado de peso registrado no histórico ainda.")
                    return
                
                df_linha_tempo["Data_Peso"] = pd.to_datetime(df_linha_tempo["Data_Peso"], dayfirst=True, errors="coerce")
                
                df_linha_tempo = df_linha_tempo.sort_values(by="Data_Peso")
                
                fig = px.line(
                    df_linha_tempo,
                    x="Data_Peso",
                    y="Peso",
                    title="Evolução do Peso",
                    markers=True
                    )
                
                fig.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Peso (kg)",
                    hovermode="x unified",
                    template="plotly_white"
                    )
                
                st.plotly_chart(fig, use_container_width=True)
            
            elif modo_graficos == "Tipos de Exercícios mais escolhidos":
                # Gráficos de Pizza - Tipo de Exercicios mais escolhidos
                
                df_tipos_exercicios = pd.read_sql_query(
                    """
                    SELECT Tipo_Exercicio, COUNT(*) AS Quantidade
                    FROM Exercicios
                    WHERE Usuario_ID = ?
                    GROUP BY Tipo_Exercicio
                    """,
                    conexao,
                    params=(id_usuario,)
                    )
                
                if df_tipos_exercicios.empty:
                    st.info("📭 Nenhuma atividade de exercício registrada no histórico ainda.")
                else:
                    fig = px.pie(
                        df_tipos_exercicios,
                        values='Quantidade',
                        names='Tipo_Exercicio',
                        title='Distribuição dos Tipos de Exercício Realizados'
                        )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)

            elif modo_graficos == "Tipos de Dietas mais escolhidos":
                # Gráficos de Treemap - Tipo de Dietas mais escolhidos
                
                df_tipos_dietas = pd.read_sql_query(
                    """
                    SELECT Tipo_Dieta, COUNT(*) AS Quantidade
                    FROM Dietas
                    WHERE Usuario_ID = ?
                    GROUP BY Tipo_Dieta
                    """,
                    conexao,
                    params=(id_usuario,)
                    )
                
                if df_tipos_dietas.empty:
                    st.info("📭 Nenhuma atividade de dieta registrado no histórico ainda.")
                else:
                    fig = px.treemap(
                        df_tipos_dietas,
                        path=['Tipo_Dieta'],
                        values='Quantidade',
                        title='Distribuição dos Tipos de Dietas Realizadas',
                        )
                    st.plotly_chart(fig, use_container_width=True)

            elif modo_graficos == "Macronutrientes mais consumidos":
                # Gráfico de Barras - Macronutrientes mais consumidos
                
                df_macronutrientes = pd.read_sql_query(
                    """
                    SELECT Macronutrientes, COUNT(*) AS Quantidade
                    FROM Dietas
                    WHERE Usuario_ID = ?
                    GROUP BY Macronutrientes
                    """,
                    conexao,
                    params=(id_usuario,)
                    )
                
                if df_macronutrientes.empty:
                    st.info("📭 Nenhuma atividade de dieta registrado no histórico ainda.")
                else:
                    fig = px.bar(
                        df_macronutrientes,
                        x="Quantidade",
                        y="Macronutrientes",
                        orientation='h',
                        title="Macronutrientes mais consumidos",
                        labels={'Quantidade': 'Número de vezes consumido', 'Macronutrientes': 'Macronutriente'},
                        text_auto='.0f'
                        )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)


def sistema_exercicio(id_usuario, peso):
    st.header("🏋️ Registro de Exercício")
    nome_ex = st.text_input("Nome do exercício")
    tipo_ex = st.selectbox("Tipo", ["Cardio", "Força", "Flexibilidade", "Outro"])
    duracao = st.number_input("Duração (minutos)", 1, 300)
    intensidade = st.selectbox("Intensidade", ["Leve", "Moderada", "Intensa"])
    data = st.date_input("Data do exercício")
    exercicio = Exercicio(id_usuario, nome_ex, tipo_ex, duracao, intensidade)
    calorias = exercicio.calcular_calorias_queimadas(peso)

    if st.button("Salvar Exercício"):
        if not nome_ex:
            st.warning("Preencha todos os campos obrigatórios!")
        else:
            with conectar_banco() as conexao:
                cursor = conexao.cursor()
                cursor.execute('''
                    INSERT INTO Exercicios (Usuario_ID, Nome_Exercicio, Tipo_Exercicio, Duracao, Intensidade, Calorias_Queimadas, Data_Exercicio)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (id_usuario, nome_ex, tipo_ex, duracao, intensidade, calorias, data.strftime("%d/%m/%Y")))
                st.success("✅ Exercício registrado!")
                novo_peso = exercicio.novo_peso_exercicio()
                    
                if novo_peso:
                    cursor.execute("UPDATE Usuarios SET Peso = ? WHERE ID = ?", (novo_peso, id_usuario))

                    cursor.execute("SELECT Nome FROM Usuarios WHERE ID = ?", (id_usuario,))
                    nome_usuario = cursor.fetchone()[0]

                    cursor.execute("INSERT INTO Historico_Peso (Usuario_ID, Nome_Usuario, Peso, Data_Peso) VALUES (?, ?, ?, ?)", (id_usuario, nome_usuario, novo_peso, data))
                    conexao.commit()
                    st.rerun()


def sistema_dieta(id_usuario, objetivo):
    st.header("🥗 Registro de Dieta")
    nome_dieta = st.text_input("Nome da dieta")
    tipo_dieta = st.selectbox("Tipo", ["Low Carb", "Cetogênica", "Vegana", "Vegetariana"])
    macronutrientes = st.selectbox("Macronutrientes", ["Proteínas", "Carboidratos", "Gorduras"])
    data = st.date_input("Data da dieta")
    dieta = Dieta(id_usuario, nome_dieta, tipo_dieta, None, macronutrientes, objetivo)
    calorias = dieta.calcular_calorias_diarias()

    if calorias:
        st.info(f"Calorias diárias estimadas: {calorias}")

    if st.button("Salvar Dieta"):
        if not nome_dieta:
            st.warning("Preencha todos os campo!")
        else:
            with conectar_banco() as conexao:
                cursor = conexao.cursor()
                cursor.execute('''
                    INSERT INTO Dietas (Usuario_ID, Nome_Dieta, Tipo_Dieta, Calorias_Diarias, Macronutrientes, Data_Dieta)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (id_usuario, nome_dieta, tipo_dieta, calorias, macronutrientes, data.strftime("%d/%m/%Y")))
                    
                st.success("✅ Dieta registrada!")
                novo_peso = dieta.novo_peso_dieta(calorias)
        
                if novo_peso:
                    cursor.execute("UPDATE Usuarios SET Peso = ? WHERE ID = ?", (novo_peso, id_usuario))

                    cursor.execute("SELECT Nome FROM Usuarios WHERE ID = ?", (id_usuario,))
                    nome_usuario = cursor.fetchone()[0]

                    cursor.execute("INSERT INTO Historico_Peso (Usuario_ID, Nome_Usuario, Peso, Data_Peso) VALUES (?, ?, ?, ?)", (id_usuario, nome_usuario, novo_peso, data))
                    conexao.commit()
                    st.rerun()


def sistema(email):
    with conectar_banco() as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT ID FROM Cadastros WHERE Email = ?", (email,))
        cadastro = cursor.fetchone()

        if not cadastro:
            st.error("Cadastro não encontrado.")
            return

        cadastro_id = cadastro[0]
        cursor.execute('''SELECT ID, Nome, Idade, Sexo, Altura, Peso, Objetivo, Nivel_Atividade, Metas
                          FROM Usuarios WHERE Cadastro_ID = ?''', (cadastro_id,))
        usuario = cursor.fetchone()

    if usuario:
        id_usuario, nome, idade, sexo, altura, peso, objetivo, nivel_atividade, metas = usuario
        usuario_obj = Usuario(cadastro_id, nome, idade, sexo, altura, peso, objetivo, nivel_atividade, metas)
        st.subheader(f"Olá, {nome}!")
        st.metric("Seu IMC", usuario_obj.calcular_imc())
        st.markdown("---")

        st.subheader("Registrar Atividade")
        modo = st.radio("Escolha:", ["Exercício", "Dieta"], horizontal=True)
        if modo == "Exercício":
            sistema_exercicio(id_usuario, peso)
        elif modo == "Dieta":
            sistema_dieta(id_usuario, objetivo)

        analise_dados(id_usuario)

    else:
        st.subheader("👤 Cadastro de Informações Pessoais")
        nome = st.text_input("Nome")
        idade = st.number_input("Idade:", min_value=0, max_value=120, value=25)
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
        altura = st.slider("Altura (m)", 1.0, 2.5, 1.70)
        peso = st.slider("Peso (kg)", 30.0, 200.0, 70.0)
        objetivo = st.selectbox("Objetivo", ["Ganhar massa muscular", "Perder gordura", "Manter forma"])
        nivel_atividade = st.selectbox("Atividade Física", ["Sedentário", "Moderado", "Ativo"])
        metas = st.text_input("Metas pessoais")

        if st.button("Salvar Informações"):
            if not nome or not metas:
                st.warning("Preencha todos os campos obrigatórios!")
            else:
                with conectar_banco() as conexao:
                    cursor = conexao.cursor()
                    cursor.execute('''
                        INSERT INTO Usuarios (Cadastro_ID, Nome, Idade, Sexo, Altura, Peso, Objetivo, Nivel_Atividade, Metas)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (cadastro_id, nome, idade, sexo, altura, peso, objetivo, nivel_atividade, metas))
                    st.success("✅ Informações salvas com sucesso!")

                    cursor.execute("SELECT last_insert_rowid()")
                    ultimo_id = cursor.fetchone()[0]

                    data_peso = datetime.now()

                    cursor.execute("INSERT INTO Historico_Peso (Usuario_ID, Nome_Usuario, Peso, Data_Peso) VALUES (?, ?, ?, ?)", (ultimo_id, nome, peso, data_peso.strftime("%d/%m/%Y")))
                    conexao.commit()
                    st.rerun()

    st.markdown("---")
    st.caption("Desenvolvido por Andrei, Fernanda e Jucilene. 🚀")
    return


# Momento Streamlit - Andrei
      
st.set_page_config("🏋️‍♀️ Metas Fitness", layout="wide")
st.title("🏋️ FitLife")
st.caption("Acompanhe sua rotina de exercícios e dieta.")
st.markdown("---")

criar_tabelas()

if "logado" not in st.session_state:
    st.session_state.logado = False
if "email_usuario" not in st.session_state:
    st.session_state.email_usuario = ""

if not st.session_state.logado:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔐 Login ou Cadastro")
        modo = st.radio("Modo", ["Login", "Cadastro"])
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar" if modo == "Login" else "Cadastrar"):
            if not email or not senha:
                st.warning("Preencha todos os campos.")
            elif not validar_email(email):
                st.warning("E-mail inválido.")
            else:
                with conectar_banco() as conexao:
                    cursor = conexao.cursor()
                    senha_hash = hash_senha(senha)
                    
                    if modo == "Login":
                        cursor.execute("SELECT ID FROM Cadastros WHERE Email = ? AND Senha = ?", (email, senha_hash))
                        usuario = cursor.fetchone()
                        if usuario:
                            st.session_state.logado = True
                            st.session_state.email_usuario = email
                            st.success("✅ Login realizado!")
                            st.rerun()
                        else:
                            st.error("E-mail ou senha incorretos.")
                    else:
                        cursor.execute("SELECT * FROM Cadastros WHERE Email = ?", (email,))
                        if cursor.fetchone():
                            st.warning("E-mail já cadastrado.")
                        else:
                            cursor.execute("INSERT INTO Cadastros (Email, Senha) VALUES (?, ?)", (email, senha_hash))
                            conexao.commit()
                            st.success("✅ Cadastro realizado!")
                            st.session_state.logado = True
                            st.session_state.email_usuario = email
                            st.rerun()
else:
    sistema(st.session_state.email_usuario)