# python -m streamlit run teste_sistema.py

import re
import hashlib
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

def conectar_banco():
    return sqlite3.connect("fitness.db")

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

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

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
        met = met_values.get(self.intensidade, 5.0)
        tempo_em_horas = self.duracao / 60
        self.calorias_queimadas = round(met * peso * tempo_em_horas, 2)
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
        self.calorias_diarias = calorias_diarias
        self.macronutrientes = macronutrientes
        self.objetivo = objetivo

    def calcular_calorias_diarias(self):
        try:
            if self.objetivo == "Ganhar massa muscular":
                return {"Proteínas": 1500, "Carboidratos": 2000, "Gorduras": 1800, "Balanceado": 2200}.get(self.macronutrientes, 2000)
            elif self.objetivo == "Perder gordura":
                return {"Proteínas": 1200, "Carboidratos": 1500, "Gorduras": 1300, "Balanceado": 1600}.get(self.macronutrientes, 1500)
            elif self.objetivo == "Manter forma":
                return {"Proteínas": 1350, "Carboidratos": 1800, "Gorduras": 1500, "Balanceado": 1900}.get(self.macronutrientes, 1800)
        except Exception as erro:
            print(f"Erro ao calcular calorias diárias: {erro}")
            return None

    def novo_peso_dieta(self):
        try:
            with conectar_banco() as conexao:
                cursor = conexao.cursor()
                cursor.execute("SELECT Peso FROM Usuarios WHERE ID = ?", (self.usuario_id,))
                peso_atual = cursor.fetchone()
                if peso_atual:
                    novo_peso = peso_atual[0] + (self.calorias_diarias / 7700)
                    return round(novo_peso, 2)
        except Exception as erro:
            print(f"Erro ao calcular novo peso: {erro}")
            return None

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

        tab1, tab2 = st.tabs(["Tabelas com Informações do Usuário", "Gráficos dos Exercícios/Dietas"])

        with tab1:
            df_exercicios = pd.read_sql("SELECT * FROM Exercicios WHERE Usuario_ID = ?", conectar_banco(), params=(id_usuario,))
            st.subheader("📈 Histórico de Exercícios")
            st.dataframe(df_exercicios if not df_exercicios.empty else pd.DataFrame(["Sem exercícios registrados."]))
            st.markdown("---")
            
            df_dietas = pd.read_sql("SELECT * FROM Dietas WHERE Usuario_ID = ?", conectar_banco(), params=(id_usuario,))
            st.subheader("🥗 Histórico de Dietas")
            st.dataframe(df_dietas if not df_dietas.empty else pd.DataFrame(["Sem dietas registradas."]))
            st.markdown("---")
            
            df_historico = pd.read_sql("SELECT * FROM Historico_Peso WHERE Usuario_ID = ?", conectar_banco(), params=(id_usuario,))
            st.subheader("📜 Histórico de Peso")
            st.dataframe(df_historico if not df_historico.empty else pd.DataFrame(["Nenhuma informação inserida ainda."]))
            st.markdown("---")

        with tab2:
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
                title="📈 Evolução do Peso",
                markers=True
                )
            
            fig.update_layout(
                xaxis_title="Data",
                yaxis_title="Peso (kg)",
                hovermode="x unified",
                template="plotly_white"
                )
            
            st.plotly_chart(fig, use_container_width=True)

            df_tipos_exercicios = pd.read_sql_query(
                "SELECT Tipo_Exercicio FROM Exercicios WHERE Usuario_ID = ?", conexao, params=(id_usuario,))
            
            if df_tipos_exercicios.empty:
                st.info("📭 Nenhuma atividade de exercício registrado no histórico ainda.")
                return
            
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
                    title='🏋️ Distribuição dos Tipos de Exercício Realizados'
                    )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)

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
                    conexao.commit()
                    st.success("Informações salvas com sucesso!")

                    cursor.execute("SELECT last_insert_rowid()")
                    ultimo_id = cursor.fetchone()[0]

                    data_peso = datetime.now()

                    cursor.execute("INSERT INTO Historico_Peso (Usuario_ID, Nome_Usuario, Peso, Data_Peso) VALUES (?, ?, ?, ?)", (ultimo_id, nome, peso, data_peso.strftime("%d/%m/%Y")))
                    st.rerun()
                    return

    st.markdown("---")
    st.subheader("Registrar Atividade")
    modo = st.radio("Escolha:", ["Exercício", "Dieta"], horizontal=True)

    if modo == "Exercício":
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
                    novo_peso = exercicio.novo_peso_exercicio()
                    
                    if novo_peso:
                        cursor.execute("UPDATE Usuarios SET Peso = ? WHERE ID = ?", (novo_peso, id_usuario))

                        cursor.execute("SELECT Nome FROM Usuarios WHERE ID = ?", (id_usuario,))
                        nome_usuario = cursor.fetchone()[0]

                        cursor.execute("INSERT INTO Historico_Peso (Usuario_ID, Nome_Usuario, Peso, Data_Peso) VALUES (?, ?, ?, ?)", (id_usuario, nome_usuario, novo_peso, data))
                        conexao.commit()
                        st.success("✅ Exercício registrado!")

    elif modo == "Dieta":
        st.header("🥗 Registro de Dieta")
        nome_dieta = st.text_input("Nome da dieta")
        tipo_dieta = st.selectbox("Tipo", ["Low Carb", "Cetogênica", "Vegana", "Outro"])
        macronutrientes = st.selectbox("Macronutrientes", ["Proteínas", "Carboidratos", "Gorduras", "Balanceado"])
        data = st.date_input("Data da dieta")
        dieta = Dieta(id_usuario, nome_dieta, tipo_dieta, 0, macronutrientes, objetivo)
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
                    
                    novo_peso = dieta.novo_peso_dieta()
        
                    if novo_peso:
                        cursor.execute("UPDATE Usuarios SET Peso = ? WHERE ID = ?", (novo_peso, id_usuario))

                        cursor.execute("SELECT Nome FROM Usuarios WHERE ID = ?", (id_usuario,))
                        nome_usuario = cursor.fetchone()[0]

                        cursor.execute("INSERT INTO Historico_Peso (Usuario_ID, Nome_Usuario, Peso, Data_Peso) VALUES (?, ?, ?, ?)", (id_usuario, nome_usuario, novo_peso, data))
                        conexao.commit()
                        st.success("✅ Dieta registrada!")

    st.markdown("---")
    st.caption("Desenvolvido por Andrei, Fernanda e Jucilene. 🚀")

# Interface principal
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
