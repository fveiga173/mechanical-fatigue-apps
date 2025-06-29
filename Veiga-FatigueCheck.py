import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Título e descrição
st.title("Veiga FatigueCheck - Ensaio ISO 7173 (Ajustado)")
st.markdown("Este app calcula se a cadeira resiste ao ensaio ISO 7173 considerando corretamente os sentidos das forças:")
st.markdown("- **1300 N no assento (compressão vertical nos pés).**\n- **560 N no encosto (gera momento de tração/compressão nas paredes opostas dos tubos traseiros).**\n- **Verifica se deforma (Sy), se rompe (Sut) e se resiste a 50.000 ciclos (Se).**")

# Entradas
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])
largura = st.number_input("Largura (quadrado) ou diâmetro externo (redondo) do tubo (mm)", value=20.0)
espessuras_lista = [0.60, 0.75, 0.90, 1.06, 1.20, 1.50, 1.90]
espessura = st.selectbox("Selecione a espessura do tubo para análise:", espessuras_lista, index=2)
altura_assento = st.number_input("Altura do assento em relação ao chão (mm)", value=450.0)

# Constantes
Sut = 310  # MPa
Sy = 0.65 * Sut  # 201 MPa
Se = 0.5 * Sut   # 155 MPa
n_ciclos_teste = 50000

# Forças do ensaio
F_vertical = 325  # N por pé (compressão)
F_horizontal = 280  # N por pé traseiro (gera momento)

d = altura_assento / 1000  # m
M = F_horizontal * d  # N.m -> momento gerado pelo encosto

# Área resistente e momento de inércia
if tipo_tubo == "Quadrado":
    A_resistente = 2 * largura * espessura  # mm²
    I = (largura * largura ** 3) / 12 - ((largura - 2 * espessura) * (largura - 2 * espessura) ** 3) / 12  # mm⁴
    c = largura / 2  # mm
else:
    A_resistente = np.pi * largura * espessura  # mm²
    d_interno = largura - 2 * espessura
    I = (np.pi / 64) * (largura ** 4 - d_interno ** 4)  # mm⁴
    c = largura / 2  # mm

# Cálculo da tensão de compressão axial
sigma_axial = F_vertical / A_resistente  # N/mm² = MPa

# Cálculo da tensão de tração/perfil devido ao momento
sigma_momento = (M * 1000) * c / I  # N.mm * mm / mm⁴ = MPa

# Tensão equivalente máxima (em uma das paredes)
sigma_total = sigma_momento - sigma_axial  # tensão de tração - compressão

# Estimativa de vida em ciclos
n_estimado = 1e6 * (abs(sigma_total) / Sut) ** (-5)

# Resultados
st.subheader("Resultados do Ensaio ISO 7173")
st.write(f"Tensão de compressão axial: {sigma_axial:.2f} MPa")
st.write(f"Tensão de tração devido ao momento: {sigma_momento:.2f} MPa")
st.write(f"Tensão total (tracao - compressao): {sigma_total:.2f} MPa")
st.write(f"Limite de escoamento (Sy): {Sy:.0f} MPa")
st.write(f"Limite de ruptura (Sut): {Sut:.0f} MPa")
st.write(f"Limite de fadiga (Se): {Se:.0f} MPa")

if abs(sigma_total) < Sy:
    st.success("✅ A cadeira NÃO deforma permanentemente no ensaio.")
elif Sy <= abs(sigma_total) < Sut:
    st.warning("⚠️ A cadeira pode sofrer DEFORMAÇÃO PLÁSTICA, mas não ruptura imediata.")
else:
    st.error("❌ A cadeira pode ROMPER sob as cargas do ensaio.")

# Verificação de fadiga
if n_estimado > n_ciclos_teste:
    st.success(f"✅ Resiste ao ensaio de fadiga de {n_ciclos_teste:,} ciclos.")
else:
    st.error(f"❌ NÃO resiste ao ensaio de fadiga de {n_ciclos_teste:,} ciclos.")

# Gráfico comparativo
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(['σ Total', 'Se', 'Sy', 'Sut'], [abs(sigma_total), Se, Sy, Sut], color=['blue', 'green', 'orange', 'red'])
ax.set_ylabel('Tensão (MPa)')
ax.set_title('Comparação de Tensões - Ensaio ISO 7173')
ax.grid(True, axis='y')
st.pyplot(fig)
