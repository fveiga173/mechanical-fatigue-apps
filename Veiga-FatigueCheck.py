import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Título e descrição
st.title("Veiga FatigueCheck - Ensaio ISO 7173 Simplificado")
st.markdown("Este app prevê se a cadeira resiste ao ensaio ISO 7173, calculando se **deforma (Sy), se rompe (Sut) e se resiste a 50.000 ciclos (Se)** sob as cargas padronizadas:")
st.markdown("- **1300 N no assento (325 N por pé).**\n- **560 N no encosto (280 N por pé traseiro).**")

# Entradas
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])
largura = st.number_input("Largura (quadrado) ou diâmetro externo (redondo) do tubo (mm)", value=20.0)
espessuras_lista = [0.60, 0.75, 0.90, 1.06, 1.20, 1.50, 1.90]
espessura = st.selectbox("Selecione a espessura do tubo para análise:", espessuras_lista, index=2)

# Constantes
Sut = 310  # MPa
Sy = 0.65 * Sut  # 201 MPa
Se = 0.5 * Sut   # 155 MPa
n_ciclos_teste = 50000

# Cálculo da carga axial total corrigida
F_vertical = 325  # N por pé (assento)
F_horizontal = 280  # N por pé traseiro (encosto)
F_axial_total = F_vertical + F_horizontal  # N

# Área resistente
if tipo_tubo == "Quadrado":
    A_resistente = 2 * largura * espessura  # mm²
else:
    A_resistente = np.pi * largura * espessura  # mm²

# Conversão para m² para cálculo de tensão (1 mm² = 1e-6 m²)
A_resistente_m2 = A_resistente * 1e-6

# Cálculo da tensão axial em MPa
sigma_axial = F_axial_total / A_resistente_m2 / 1e6  # MPa

# Estimativa de vida em ciclos por Lei de Basquin simplificada
a_basquin = 1e6  # 1.000.000 ciclos a Se
b_basquin = 5
n_estimado = a_basquin * (sigma_axial / Sut) ** (-b_basquin)

# Resultados
st.subheader("Resultados do Ensaio ISO 7173")
st.write(f"Carga axial total aplicada por pé traseiro: {F_axial_total} N")
st.write(f"Área resistente calculada: {A_resistente:.2f} mm²")
st.write(f"Tensão axial calculada: {sigma_axial:.2f} MPa")
st.write(f"Limite de escoamento (Sy): {Sy:.0f} MPa")
st.write(f"Limite de ruptura (Sut): {Sut:.0f} MPa")
st.write(f"Limite de fadiga (Se): {Se:.0f} MPa")

if sigma_axial < Sy:
    st.success("✅ A cadeira **NÃO deforma permanentemente** no ensaio.")
elif Sy <= sigma_axial < Sut:
    st.warning("⚠️ A cadeira pode sofrer **deformação plástica**, mas não ruptura imediata.")
else:
    st.error("❌ A cadeira pode **romper** sob as cargas do ensaio.")

# Verificação de fadiga
if n_estimado > n_ciclos_teste:
    st.success(f"✅ Resiste ao ensaio de fadiga de {n_ciclos_teste:,} ciclos.")
else:
    st.error(f"❌ NÃO resiste ao ensaio de fadiga de {n_ciclos_teste:,} ciclos.")

# Gráfico comparativo
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(['σ Calculada', 'Se', 'Sy', 'Sut'], [sigma_axial, Se, Sy, Sut], color=['blue', 'green', 'orange', 'red'])
ax.set_ylabel('Tensão (MPa)')
ax.set_title('Comparação de Tensões no Ensaio ISO 7173')
ax.grid(True, axis='y')

st.pyplot(fig)
