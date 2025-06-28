import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Constantes de material (aço SAE 1008)
Sut = 310  # MPa
Se = 0.5 * Sut
FS = 1  # Fator de segurança

# Parâmetros para estimativa de ciclos (alto ciclo)
a = 1e6
b = 5

st.title("Análise de Fadiga em Tubos Soldados - Cadeira ISO 7173")

# Entrada do tipo de tubo
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])

# Entradas geométricas
if tipo_tubo == "Quadrado":
    largura = st.number_input("Largura do tubo (mm)", value=20.0)
else:
    largura = st.number_input("Diâmetro externo do tubo (mm)", value=25.4)

espessura = st.number_input("Espessura do tubo (mm)", value=0.9)
largura_cordao = st.number_input("Largura do cordão de solda (mm)", value=6.0)

# Cálculo da cadeira inclinada (momento)
M = 114710  # N·mm fixo

if tipo_tubo == "Quadrado":
    b = largura
    h = largura
    I = (b * h**3) / 12 - ((b - 2*espessura)*(h - 2*espessura)**3)/12
    c = h / 2
else:
    D = largura
    d = D - 2 * espessura
    I = (np.pi / 64) * (D**4 - d**4)
    c = D / 2

sigma_momento = M * c / I

# Tensão admissível (Goodman)
sigma_adm = Se / FS

# Cálculo da cadeira com 4 pés (força axial)
F_axial = 325  # N por solda
if tipo_tubo == "Quadrado":
    A_solda = 2 * largura_cordao * espessura
else:
    D = largura
    A_solda = np.pi * D * espessura

sigma_axial = F_axial / A_solda

# Estimativa de ciclos de fadiga
N_ciclos = a * (sigma_axial / Sut)**(-b)

# Resultados
st.subheader("Resultados: Cadeira Inclinada (com momento)")
st.write(f"Momento fletor: {M:,.0f} N·mm")
st.write(f"Tensão normal por flexão: {sigma_momento:.1f} MPa")
st.write(f"Tensão admissível (Goodman): {sigma_adm:.1f} MPa")

if sigma_momento < sigma_adm:
    st.success("✅ A estrutura RESISTE ao carregamento com momento.")
else:
    st.error("❌ A estrutura NÃO RESISTE ao carregamento com momento.")

st.subheader("Resultados: Cadeira com 4 pés (força axial)")
st.write(f"Tensão axial na solda: {sigma_axial:.1f} MPa")
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
ax.set_title("Diagrama de Goodman")
ax.grid(True)
ax.legend()

st.pyplot(fig)
