import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Título e descrição
st.title("Veiga FatigueCheck - Análise de resistência em cadeiras soldadas")
st.markdown("Este app realiza análises de fadiga em cadeiras metálicas conforme a **ISO 7173**, considerando dois casos com aço SAE 1008 (Sut=310 MPa, Se=155 MPa). Utilize capturas de tela para registrar os resultados em PDF quando necessário.")

# Imagem
try:
    diagramas = Image.open("A_pair_of_technical_engineering_diagrams_in_black_.png")
    st.image(diagramas, caption="Diagramas de análise: cadeira inclinada e cadeira em 4 apoios")
except:
    st.info("Imagem de diagramas não encontrada no diretório. Coloque a imagem no mesmo repositório para visualização.")

# Entradas
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])
largura = st.number_input("Largura (quadrado) ou diâmetro externo (redondo) do tubo (mm)", value=20.0)
espessura = st.number_input("Espessura do tubo (mm)", value=0.9)
largura_cordao = st.number_input("Largura do cordão de solda (mm)", value=6.0)

# Constantes
Sut = 310
Se = 0.5 * Sut
Sy = 0.65 * Sut
FS = 1
a_ciclo = 1e6
b_ciclo = 5
M = 114710  # Momento

# Cálculos gerais
if tipo_tubo == "Quadrado":
    I = (largura * largura**3) / 12 - ((largura - 2 * espessura) * (largura - 2 * espessura)**3) / 12
    c = largura / 2
    A_solda = 2 * largura_cordao * espessura
else:
    d_interno = largura - 2 * espessura
    I = (np.pi / 64) * (largura**4 - d_interno**4)
    c = largura / 2
    A_solda = np.pi * largura * espessura

# Caso 1: cadeira inclinada
sigma_momento = M * c / I
sigma_adm = Sy / FS

# Caso 2: carga axial
F_axial = 325
sigma_axial = F_axial / A_solda
N_ciclos = a_ciclo * (sigma_axial / Sut) ** (-b_ciclo)

# Resultados
st.subheader("Resultados")

st.markdown("**Caso 1: Cadeira Inclinada**")
st.write(f"Tensão por momento: {sigma_momento:.2f} MPa")
st.write(f"Tensão admissível (Limite de Escoamento): {sigma_adm:.2f} MPa")
if sigma_momento < sigma_adm:
    st.success("✅ A estrutura RESISTE ao carregamento com momento.")
else:
    st.error("❌ A estrutura NÃO RESISTE ao carregamento com momento.")

st.markdown("**Caso 2: Cadeira com 4 Apoios**")
st.write(f"Tensão axial: {sigma_axial:.2f} MPa")
st.write(f"Vida estimada: {N_ciclos:,.0f} ciclos")
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
