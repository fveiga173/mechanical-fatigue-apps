import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pdfkit

# Configurações iniciais e descrição
st.title("Veiga FatigueCheck - Análise de Fadiga em Tubos de Cadeiras")

st.markdown("""
Este aplicativo realiza análises de fadiga em cadeiras metálicas conforme a **ISO 7173**, considerando:
- **Caso 1:** Cadeira inclinada (15°) com momento gerado por carga de 950 N distribuída.
- **Caso 2:** Cadeira com 4 apoios, carga total de 1300 N (325 N por pé).

Os tubos são considerados em **aço SAE 1008 (Sut = 310 MPa, Se = 155 MPa)**.
""")

# Inserção dos diagramas
diagramas = Image.open("/mnt/data/A_pair_of_technical_engineering_diagrams_in_black_.png")
st.image(diagramas, caption="Diagramas de análise: cadeira inclinada e cadeira em 4 apoios")


# Entradas
st.header("Entradas")
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])
if tipo_tubo == "Quadrado":
    largura = st.number_input("Largura do tubo (mm)", value=20.0)
else:
    largura = st.number_input("Diâmetro externo do tubo (mm)", value=25.4)
espessura = st.number_input("Espessura do tubo (mm)", value=0.9)
largura_cordao = st.number_input("Largura do cordão de solda (mm)", value=6.0)

# Constantes
Sut = 310
Se = 0.5 * Sut
FS = 1
a = 1e6
b = 5
M = 114710  # Momento fixo

# Cálculos para o tubo
if tipo_tubo == "Quadrado":
    b_dim = largura
    h = largura
    I = (b_dim * h**3) / 12 - ((b_dim - 2*espessura)*(h - 2*espessura)**3)/12
    c = h / 2
else:
    D = largura
    d = D - 2 * espessura
    I = (np.pi / 64) * (D**4 - d**4)
    c = D / 2

# Caso 1: Momento
sigma_momento = M * c / I
sigma_adm = Se / FS

# Caso 2: Axial
F_axial = 325
if tipo_tubo == "Quadrado":
    A_solda = 2 * largura_cordao * espessura
else:
    D = largura
    A_solda = np.pi * D * espessura
sigma_axial = F_axial / A_solda
N_ciclos = a * (sigma_axial / Sut)**(-b)

# Resultados organizados responsivamente
col1, col2 = st.columns(2)


with col1:
    st.subheader("Caso 1: Cadeira Inclinada")
    st.write(f"Tensão por momento: **{sigma_momento:.1f} MPa**")
    st.write(f"Tensão admissível (Goodman): **{sigma_adm:.1f} MPa**")
    if sigma_momento < sigma_adm:
        st.success("✅ A estrutura RESISTE ao carregamento com momento.")
    else:
        st.error("❌ A estrutura NÃO RESISTE ao carregamento com momento.")

with col2:
    st.subheader("Caso 2: Cadeira com 4 Apoios")
    st.write(f"Tensão axial: **{sigma_axial:.1f} MPa**")
    st.write(f"Vida estimada: **{N_ciclos:,.0f} ciclos**")
    if sigma_axial < sigma_adm:
        st.success("✅ A solda RESISTE ao carregamento axial.")
    else:
        st.error("❌ A solda NÃO RESISTE ao carregamento axial.")


# Gráfico de Goodman
st.subheader("Diagrama de Goodman")
fig, ax = plt.subplots()
sigma_a_vals = np.linspace(0, Sut, 500)
sigma_m_vals = Sut - (Sut / Se) * sigma_a_vals
ax.plot(sigma_a_vals, sigma_m_vals, label="Linha de Goodman", color="red")
ax.axhline(y=sigma_adm, color='green', linestyle='--', label="Tensão admissível")
ax.set_xlabel("Tensão Alternada (MPa)")
ax.set_ylabel("Tensão Média (MPa)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

if st.button("Salvar relatório em PDF"):
    with open("relatorio_fadiga.html", "w") as f:
        f.write(f"""
        <h1>Relatório de Fadiga - Veiga FatigueCheck</h1>
        <p>Tipo de tubo: {tipo_tubo}</p>
        <p>Largura/Diâmetro: {largura} mm</p>
        <p>Espessura: {espessura} mm</p>
        <p>Largura do cordão: {largura_cordao} mm</p>
        <h2>Caso 1: Cadeira Inclinada</h2>
        <p>Tensão por momento: {sigma_momento:.1f} MPa</p>
        <p>Tensão admissível: {sigma_adm:.1f} MPa</p>
        <h2>Caso 2: Cadeira com 4 Apoios</h2>
        <p>Tensão axial: {sigma_axial:.1f} MPa</p>
        <p>Vida estimada: {N_ciclos:,.0f} ciclos</p>
        """)
    pdfkit.from_file("relatorio_fadiga.html", "relatorio_fadiga.pdf")
    with open("relatorio_fadiga.pdf", "rb") as pdf_file:
        st.download_button("Clique para baixar o relatório em PDF", data=pdf_file, file_name="relatorio_fadiga.pdf")
