# Avaliação Final - POO

# python -m streamlit run trabalho_fitness.py

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

def conectar_banco():
    return sqlite3.connect("fitness.db")

def criar_tabelas():
    # Momento Banco de Dados SQLite - Fernanda
    
    # Manter tabela Cadastros para Login e manter atributos da tabela Usuarios (ID até Peso)

    conexao = conectar_banco()
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
            Alimentos_Permitidos TEXT NOT NULL,
            Alimentos_Proibidos TEXT NOT NULL,
            Data_Dieta TEXT NOT NULL,
            FOREIGN KEY (Usuario_ID) REFERENCES Usuarios(ID)
        )
    ''')

    conexao.commit()
    conexao.close()


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


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
        

class Exercicio(Usuario):
    def __init__(self, nome_exercicio, tipo_exercicio, duracao, intensidade):
        self.nome_exercicio = nome_exercicio
        self.tipo_exercicio = tipo_exercicio
        self.duracao = duracao
        self.intensidade = intensidade
        self.calorias_queimadas = 0

    def calcular_calorias_queimadas(self, peso):
        met_values = {
            "Leve": 3.0,
            "Moderada": 5.0,
            "Intensa": 8.0
        }
        met = met_values.get(self.intensidade, 5.0)
        tempo_em_horas = self.duracao / 60
        self.calorias_queimadas = round(met * peso * tempo_em_horas, 2)
        return self.calorias_queimadas
    
    def novo_peso_exercicio(self):
        try:
            conexao = conectar_banco()
            cursor = conexao.cursor()
            cursor.execute("SELECT Peso FROM Usuarios WHERE Cadastro_ID = ?", (self.cadastro_id,))
            peso_atual = cursor.fetchone()
            if peso_atual:
                calorias_queimadas = pd.read_sql("SELECT SUM(Calorias_Quimadas) FROM Exercicios WHERE Usuario_ID = (SELECT ID FROM Usuarios WHERE Calorias_Queimadas = ?)", calorias_queimadas, params=( self.cadastro_id,))
                if calorias_queimadas is not None:
                    novo_peso = peso_atual - (self.calorias_queimadas / 7700)
                    return round(novo_peso, 2)
        except Exception as erro:
            print(f"Erro ao calcular novo peso: {erro}")
            return None
    
    @staticmethod
    def listar_por_usuario(usuario_id):
        conexao = conectar_banco()
        df_exercicios = pd.read_sql("SELECT * FROM Exercicios WHERE Usuario_ID = ?", conexao, params=(usuario_id,))
        conexao.close()
        return df_exercicios


class Dieta(Usuario):
    def __init__(self, usuario_id, nome_dieta, tipo_dieta, calorias_diarias, macronutrientes, alimentos_permitidos, alimentos_proibidos):
        self.usuario_id = usuario_id
        self.nome_dieta = nome_dieta
        self.tipo_dieta = tipo_dieta
        self.calorias_diarias = calorias_diarias
        self.macronutrientes = macronutrientes
        self.alimentos_permitidos = alimentos_permitidos
        self.alimentos_proibidos = alimentos_proibidos

    def calcular_calorias_diarias(self):
        try:
            if self.objetivo == "Ganhar massa muscular":
                if self.macronutrientes == "Proteínas":
                    self.calorias_diarias = 1500
                elif self.macronutrientes == "Carboidratos":
                    self.calorias_diarias = 2000
                elif self.macronutrientes == "Gorduras":
                    self.calorias_diarias = 1800
                elif self.macronutrientes == "Balanceado":
                    self.calorias_diarias = 2200
                return self.calorias_diarias
            elif self.objetivo == "Perder gordura":
                if self.macronutrientes == "Proteínas":
                    self.calorias_diarias = 1200
                elif self.macronutrientes == "Carboidratos":
                    self.macronutrientes = 1500
                elif self.macronutrientes == "Gorduras":
                    self.calorias_diarias = 1300
                elif self.macronutrientes == "Balanceado":
                    self.calorias_diarias = 1600
                return self.calorias_diarias
            elif self.objetivo == "Manter forma":
                if self.macronutrientes == "Proteínas":
                    self.calorias_diarias = 1350
                elif self.macronutrientes == "Carboidratos":
                    self.calorias_diarias = 1800
                elif self.macronutrientes == "Gorduras":
                    self.calorias_diarias = 1500
                elif self.macronutrientes == "Balanceado":
                    self.calorias_diarias = 1900
                return self.calorias_diarias
        except Exception as erro:
            print(f"Erro ao calcular calorias diárias: {erro}")
            return None

    def novo_peso_dieta(self):
        try:
            conexao = conectar_banco()
            cursor = conexao.cursor()
            cursor.execute("SELECT Peso FROM Usuarios WHERE Cadastro_ID = ?", (self.cadastro_id,))
            peso_atual = cursor.fetchone()
            if peso_atual:
                calorias = self.calorias_diarias
                if calorias is not None:
                    novo_peso = peso_atual + (calorias / 7700)
                    return round(novo_peso, 2)
        except Exception as erro:
            print(f"Erro ao calcular novo peso: {erro}")
            return None


    @staticmethod
    def listar_por_usuario(usuario_id):
        conexao = conectar_banco()
        df_dietas = pd.read_sql("SELECT * FROM Dietas WHERE Usuario_ID = ?", conexao, params=(usuario_id,))
        conexao.close()
        return df_dietas


def sistema(email):
    conexao = conectar_banco()
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
        st.subheader(f"Olá, {nome}!")
        st.markdown("---")
        st.header("📊 Seus últimos resultados")

        # Momento Dashboard ou Métricas - Jucilene

        df_exercicios = pd.read_sql("SELECT * FROM Exercicios WHERE Usuario_ID = ?", conectar_banco(), params=(id_usuario,))
        if df_exercicios.empty:
            st.warning("Nenhum resultado dos seus exercícios ainda!")
        else:
            st.dataframe(df_exercicios)

        df_dietas = pd.read_sql("SELECT * FROM Dietas WHERE Usuario_ID = ?", conectar_banco(), params=(id_usuario,))
        if df_dietas.empty:
            st.warning("Nenhum resultado das suas dietas ainda!")
        else:
            st.dataframe(df_dietas)

        usuario = Usuario(cadastro_id, nome, idade, sexo, altura, peso, objetivo, nivel_atividade, metas)

        

    else:
        st.subheader("👤 Informações Pessoais")
        nome = st.text_input("Nome", placeholder="Digite seu nome aqui")
        idade = st.number_input("Idade:", min_value=0, max_value=120, value=25)
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
        altura = st.slider("Altura (em metros):", 1.0, 2.5, 1.70)
        peso = st.slider("Peso (em kg):", 30.0, 200.0, 70.0)
        objetivo = st.selectbox("Objetivo:", ["Ganhar massa muscular", "Perder gordura", "Manter forma"])
        nivel_atividade = st.selectbox("Nível de atividade física:", ["Sedentário", "Moderado", "Ativo"])
        metas = st.text_input("Descreva suas metas:")

        if st.button("Salvar Informações"):
            if not nome or not metas:
                st.warning("Preencha todos os campos obrigatórios.")
            else:
                conexao = conectar_banco()
                cursor = conexao.cursor()
                cursor.execute('''
                    INSERT INTO Usuarios (Cadastro_ID, Nome, Idade, Sexo, Altura, Peso, Objetivo, Nivel_Atividade, Metas)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (cadastro_id, nome, idade, sexo, altura, peso, objetivo, nivel_atividade, metas))
                conexao.commit()
                conexao.close()
                st.success("✅ Informações salvas!")
                st.rerun()

    st.markdown("---")
    st.subheader("Registrar atividade")
    modo = st.radio("Categoria:", ["Exercício", "Dieta"], horizontal=True)

    if modo == "Exercício":
        st.header("🏋️ Registro de Exercício")
        nome_ex = st.text_input("Nome do exercício")
        tipo_ex = st.selectbox("Tipo", ["Cardio", "Força", "Flexibilidade", "Outro"])
        duracao = st.number_input("Duração (min)", 1, 300)
        intensidade = st.selectbox("Intensidade", ["Leve", "Moderada", "Intensa"])
        data = st.date_input("Data do exercício")
        exercicio = Exercicio(nome_ex, tipo_ex, duracao, intensidade)
        calorias = exercicio.calcular_calorias_queimadas(peso)

        if st.button("Salvar Exercício"):
            conexao = conectar_banco()
            cursor = conexao.cursor()
            cursor.execute('''
                INSERT INTO Exercicios (Usuario_ID, Nome_Exercicio, Tipo_Exercicio, Duracao, Intensidade, Calorias_Queimadas, Data_Exercicio)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (cadastro_id, nome_ex, tipo_ex, duracao, intensidade, calorias, data.strftime("%d/%m/%Y")))
            conexao.commit()
            st.success("✅ Exercício registrado!")

            novo_peso = exercicio.novo_peso_exercicio()

            if novo_peso is not None:
                cursor.execute('''
                    UPDATE Usuarios SET Peso = ? WHERE Cadastro_ID = ?)
                    ''', (novo_peso, cadastro_id))
                conexao.commit()
                conexao.close()
            else:
                st.error("Erro ao calcular novo peso após exercício.")

    elif modo == "Dieta":
        st.header("🥗 Registro de Dieta")
        nome_dieta = st.text_input("Nome da dieta")
        tipo_dieta = st.selectbox("Tipo", ["Low Carb", "Cetogênica", "Vegana", "Outro"])
        macronutrientes = st.selectbox("Macronutrientes", ["Proteínas", "Carboidratos", "Gorduras", "Balanceado"])
        alimentos_permitidos = st.text_area("Alimentos permitidos")
        alimentos_proibidos = st.text_area("Alimentos proibidos")
        data = st.date_input("Data da dieta")
        calorias = 0
        dieta = Dieta(nome_dieta, tipo_dieta, calorias, macronutrientes, alimentos_permitidos, alimentos_proibidos)
        calorias = dieta.calcular_calorias_diarias()

        if calorias is None:
            st.error("Erro ao calcular calorias diárias. Verifique os dados da dieta.")
        else:
            st.write(f"Calorias diárias estimadas: {calorias}")

        if st.button("Salvar Dieta"):
            conexao = conectar_banco()
            cursor = conexao.cursor()
            cursor.execute('''
                INSERT INTO Dietas (Usuario_ID, Nome_Dieta, Tipo_Dieta, Calorias_Diarias, Macronutrientes, Alimentos_Permitidos, Alimentos_Proibidos, Data_Dieta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (cadastro_id, nome_dieta, tipo_dieta, calorias, macronutrientes, alimentos_permitidos, alimentos_proibidos, data.strftime("%d/%m/%Y")))
            conexao.commit()
            st.success("✅ Dieta registrada!")

            novo_peso = dieta.novo_peso_dieta()

            if novo_peso is not None:
                cursor.execute('''
                    UPDATE Usuarios SET Peso = ? WHERE Cadastro_ID = ?)
                    ''', (novo_peso, cadastro_id))
                conexao.commit()
                conexao.close()
            else:
                st.error("Erro ao calcular novo peso após dieta.")

    st.markdown("---")
    st.caption("Desenvolvido por Andrei, Fernanda e Jucilene. 🚀")
                

def validar_email(email):
    return "@" in email and "." in email.split("@")[-1]

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
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None

if not st.session_state.logado:
    st.subheader("🔐 Login ou Cadastro")
    modo = st.radio("Modo", ["Login", "Cadastro"])
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if modo == "Login":
        if st.button("Entrar"):
            if not email or not senha:
                st.warning("Preencha todos os campos.")
            else:
                conexao = conectar_banco()
                cursor = conexao.cursor()
                senha_hash = hash_senha(senha)
                cursor.execute("SELECT ID FROM Cadastros WHERE Email = ? AND Senha = ?", (email, senha_hash))
                usuario = cursor.fetchone()
                if usuario:
                    st.session_state.logado = True
                    st.session_state.email_usuario = email
                    st.session_state.usuario_id = usuario[0]
                    st.success("✅ Login realizado!")
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos.")

    elif modo == "Cadastro":
        if st.button("Cadastrar"):
            if not email or not senha:
                st.warning("Preencha todos os campos.")
            elif not validar_email(email):
                st.warning("E-mail inválido.")
            else:
                conexao = conectar_banco()
                cursor = conexao.cursor()
                cursor.execute("SELECT * FROM Cadastros WHERE Email = ?", (email,))
                if cursor.fetchone():
                    st.warning("E-mail já cadastrado.")
                else:
                    senha_hash = hash_senha(senha)
                    cursor.execute("INSERT INTO Cadastros (Email, Senha) VALUES (?, ?)", (email, senha_hash))
                    conexao.commit()
                    cursor.execute("SELECT ID FROM Cadastros WHERE Email = ?", (email,))
                    novo_usuario = cursor.fetchone()
                    st.session_state.logado = True
                    st.session_state.email_usuario = email
                    st.session_state.usuario_id = novo_usuario[0]
                    st.success("✅ Cadastro realizado!")
                    st.rerun()

else:
    sistema(st.session_state.email_usuario)

# st.subheader(f"Tendências Temporais de Vendas Globais ({intervalo_anos[0]} - {intervalo_anos[1]})")

# df_temporal = df_filtrado.groupby('Year')['Global_Sales'].sum().reset_index()

# fig = px.line(
#     df_temporal,
#     x='Year', 
#     y='Global_Sales', 
#     labels={'Global_Sales': 'Vendas Globais (milhões)', 'Year': 'Ano'},
#     markers=True
# )

# fig.add_hline(y=df_temporal['Global_Sales'].mean(), line_dash="dash", line_color="green",
#               annotation_text="Média Global", annotation_position="bottom right")

# st.plotly_chart(fig, use_container_width=True)