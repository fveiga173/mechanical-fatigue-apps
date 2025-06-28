import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("🔧 Fadiga — Tubo Quadrado (20×20×0.9mm)")

# Entradas
M = st.number_input("Momento Fletor (N·mm)", value=5000.0)
Sut = st.number_input("Sut (MPa)", value=310.0)
Se = st.number_input("Se estimado (MPa)", value=0.5 * Sut)
n = st.number_input("Fator de Segurança", value=1.0)

# Geometria
lado = 20.0
esp = 0.9
I = (lado**4 - (lado - 2*esp)**4) / 12  # momento de inércia aproximado
c = lado / 2

# Cálculos
sigma_n = M * c / I
sigma_adm = (Se * Sut) / (n * (Sut - Se))

st.subheader("📊 Resultados – Tubo Quadrado")
st.write(f"Tensão normal: **{sigma_n:.2f} MPa**")
st.write(f"Tensão admissível (Goodman): **{sigma_adm:.2f} MPa**")
if sigma_n <= sigma_adm:
    st.success("✅ Projeto aprovado")
else:
    st.error("❌ Projeto reprovado")

# Gráfico de Goodman
sigma_a = np.linspace(0, Sut, 100)
sigma_m = Se * (1 - sigma_a / Sut)
plt.figure()
plt.plot(sigma_a, sigma_m, label='Envelope Goodman')
plt.axhline(sigma_n, color='r', linestyle='--', label='Tensão Normal')
plt.xlabel("Tensão Alternada (MPa)")
plt.ylabel("Tensão Média (MPa)")
plt.legend()
st.pyplot(plt)