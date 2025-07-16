import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from PIL import Image

# Configuração inicial
st.set_page_config(layout="wide")
st.title("Simulador de Vibração Veicular MDOF")
st.markdown("Modelo com carga na caçamba, chassi, motorista e eixos com molas.")

# Mostra imagem
image = Image.open("modelo.png")
st.image(image, caption="Esquema do modelo físico", use_column_width=True)

# Entradas
st.sidebar.header("Parâmetros do Sistema")

m1 = st.sidebar.number_input("Massa da carga (m1)", 10.0, 100.0, 25.0)
m2 = st.sidebar.number_input("Massa do chassi (m2)", 10.0, 100.0, 50.0)
m3 = st.sidebar.number_input("Massa do motorista (m3)", 5.0, 50.0, 10.0)
m4 = st.sidebar.number_input("Massa do eixo dianteiro (m4)", 5.0, 50.0, 10.0)
m5 = st.sidebar.number_input("Massa do eixo traseiro (m5)", 5.0, 50.0, 10.0)

k1 = st.sidebar.number_input("Rigidez k1", 100.0, 10000.0, 1000.0)
k2 = st.sidebar.number_input("Rigidez k2", 100.0, 10000.0, 1000.0)
k3 = st.sidebar.number_input("Rigidez k3 (assento)", 100.0, 10000.0, 1000.0)
k4 = st.sidebar.number_input("Rigidez k4 (chassi-eixo dianteiro)", 100.0, 10000.0, 1000.0)
k5 = st.sidebar.number_input("Rigidez k5 (pneus dianteiros)", 100.0, 10000.0, 1000.0)
k6 = st.sidebar.number_input("Rigidez k6 (chassi-eixo traseiro)", 100.0, 10000.0, 1000.0)
k7 = st.sidebar.number_input("Rigidez k7 (pneus traseiros)", 100.0, 10000.0, 1000.0)

a = st.sidebar.number_input("Distância a", 0.01, 1.0, 0.1)
b = st.sidebar.number_input("Distância b", 0.01, 1.0, 0.1)
c = st.sidebar.number_input("Distância c", 0.01, 1.0, 0.1)
d = st.sidebar.number_input("Distância d", 0.01, 1.0, 0.1)
e = st.sidebar.number_input("Distância e", 0.01, 1.0, 0.1)
f = st.sidebar.number_input("Distância f", 0.01, 1.0, 0.1)
g = st.sidebar.number_input("Distância g", 0.01, 1.0, 0.1)

if st.sidebar.button("Calcular e Simular"):

    # Variáveis simbólicas
    symbs = sp.symbols('a b c d e f g k1 k2 k3 k4 k5 k6 k7 m1 m2 m3 m4 m5 I1 I2')
    vals = [a, b, c, d, e, f, g, k1, k2, k3, k4, k5, k6, k7, m1, m2, m3, m4, m5,
            (1/3)*m1*a**2, (1/3)*m2*b**2]
    subs = dict(zip(symbs, vals))

    # Importa as equações do modelo simbólico (usa teu código que gera M e K)
    from sympy import symbols, zeros, expand, collect
    xg2, tet2, xg1, tet1, x3, x4, x5 = symbols('xg2 tet2 xg1 tet1 x3 x4 x5')
    ag2, ate2, ag1, ate1, a3, a4, a5 = symbols('ag2 ate2 ag1 ate1 a3 a4 a5')
    xf = xg2 - a * tet2
    xh = xg2 + b * tet2
    xa = xg1 + c * tet1
    xb = xg1 + d * tet1
    xc = xg1 + e * tet1
    xd = xg1 + f * tet1
    xe = xg1 - g * tet1
    FM1 = k1 * (xf - xc)
    FM2 = k2 * (xh - xd)
    FM3 = k3 * xe
    FM4 = k4 * (xb - x4)
    FM5 = k5 * x4
    FM6 = k6 * (xa - x5)
    FM7 = k7 * x5
    eq1 = -FM6 + FM1 + FM2 + FM3 - FM4 - m2 * ag2
    eq2 = -FM6*c + FM1*a + FM2*b - FM3*g - (1/3)*m2*b**2 * ate2
    eq3 = -FM1 - FM2 - m1 * ag1
    eq4 = -FM1*a + FM2*b - (1/3)*m1*a**2 * ate1
    eq5 = -FM3 - m3 * a3
    eq6 = FM4 - FM5 - m4 * a4
    eq7 = FM6 - FM7 - m5 * a5

    VAR_D = [xg2, tet2, xg1, tet1, x3, x4, x5]
    VAR_A = [ag2, ate2, ag1, ate1, a3, a4, a5]

    EQ = [eq1, eq2, eq3, eq4, eq5, eq6, eq7]
    EQ = [-expand(eq) for eq in EQ]
    for i in range(7):
        for j in range(7):
            EQ[i] = collect(EQ[i], VAR_D[j])

    Mmat = zeros(7)
    Kmat = zeros(7)
    for i in range(7):
        Mmat[i, i] = EQ[i].coeff(VAR_A[i], 1)
        for j in range(7):
            Kmat[i, j] = EQ[i].coeff(VAR_D[j], 1)

    Mnum = np.array(Mmat.subs(subs).evalf().tolist(), dtype=float)
    Knum = np.array(Kmat.subs(subs).evalf().tolist(), dtype=float)

    A = np.linalg.pinv(Mnum) @ Knum
    VAL, VET = np.linalg.eig(A)
    wn = np.sqrt(np.abs(VAL))
    fn = wn / (2 * np.pi)
    valid = wn > 1e-5
    wn, fn = wn[valid], fn[valid]
    VET = VET[:, valid]

    st.subheader("Frequências Naturais (Hz)")
    st.write(fn)

    # Resposta em vibração livre
    t = np.linspace(0, 5, 5000)
    X0 = np.linspace(0.01, 0.05, VET.shape[0]).reshape(-1, 1)
    V0 = np.linspace(1, 5, VET.shape[0]).reshape(-1, 1)
    freq_inv = np.diag(np.where(wn != 0, 1 / wn, 0))
    Mdiag = VET.T @ Mnum @ VET
    VETn = VET / np.sqrt(np.diag(Mdiag))[np.newaxis, :]
    MAT1 = VETn.T @ Mnum @ X0
    MAT2 = freq_inv @ VETn.T @ Mnum @ V0
    Cs = np.cos(np.outer(wn, t))
    Sn = np.sin(np.outer(wn, t))
    response = VETn @ (Cs * MAT1 + Sn * MAT2)

    st.subheader("Resposta em Vibração Livre")
    fig, ax = plt.subplots(figsize=(10, 4))
    for i in range(response.shape[0]):
        ax.plot(t, response[i], label=f'x{i+1}')
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Deslocamento (m)")
    ax.legend()
    ax.grid()
    st.pyplot(fig)
