import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Título e descrição
st.title("Veiga FatigueCheck - Análise de resistência em cadeiras soldadas")
st.markdown("Este app realiza análises de resistência em cadeiras metálicas conforme a **ISO 7173**, considerando dois casos com aço SAE 1008 (Sut=310 MPa, Sy=201 MPa, Se=155 MPa). Utilize capturas de tela para registrar os resultados em PDF quando necessário.")

# Imagem
try:
    diagramas = Image.open("A_pair_of_technical_engineering_diagrams_in_black_.png")
    st.image(diagramas, caption="Diagramas de análise: cadeira inclinada e cadeira em 4 apoios")
except:
    st.info("Imagem de diagramas não encontrada no diretório. Coloque a imagem no mesmo repositório para visualização.")

# Entradas
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])
largura = st.number_input("Largura (quadrado) ou diâmetro externo (redondo) do tubo (mm)", value=20.0)
espessuras_lista = [0.60, 0.75, 0.90, 1.06, 1.20, 1.50, 1.90]  # mm
espessura = st.selectbox("Selecione a espessura do tubo para visualização detalhada:", espessuras_lista, index=2)
largura_cordao = st.number_input("Largura do cordão de solda (mm)", value=6.0)

# Constantes
Sut = 310
Sy = 0.65 * Sut  # ≈ 201,5 MPa
Se = 0.5 * Sut   # 155 MPa
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

# Caso 2: carga axial
F_axial = 325
sigma_axial = F_axial / A_solda
N_ciclos = a_ciclo * (sigma_axial / Sut) ** (-b_ciclo)

# Resultados
st.subheader("Resultados")

st.markdown("**Caso 1: Cadeira Inclinada**")
st.write(f"Tensão por momento: {sigma_momento:.2f} MPa")
st.write(f"Limite de escoamento (Sy): {Sy:.2f} MPa")
st.write(f"Limite de ruptura (Sut): {Sut:.2f} MPa")

if sigma_momento < Sy:
    st.success("✅ A estrutura RESISTE ao carregamento com momento (sem deformação permanente).")
elif Sy <= sigma_momento < Sut:
    st.warning("⚠️ A estrutura NÃO RESISTE ao carregamento sem deformação permanente. Pode ocorrer **deformação plástica**, mas não ruptura imediata.")
else:
    st.error("❌ A estrutura NÃO RESISTE ao carregamento. **Pode ocorrer ruptura total.**")

st.markdown("**Caso 2: Cadeira com 4 Apoios**")
st.write(f"Tensão axial: {sigma_axial:.2f} MPa")
st.write(f"Vida estimada: {N_ciclos:,.0f} ciclos")

if sigma_axial < Sy:
    st.success("✅ A solda RESISTE ao carregamento axial (sem deformação permanente).")
else:
    st.error("❌ A solda NÃO RESISTE ao carregamento axial, podendo ocorrer **deformação permanente ou ruptura em ciclos.**")

# Seção final: Análise Comparativa por Espessura (ajustada)

st.subheader("Análise Comparativa por Espessura")

sigma_momentos = []
sigma_axials = []

for esp in espessuras_lista:
    I = (largura_tubo * largura_tubo ** 3) / 12 - ((largura_tubo - 2 * esp) * (largura_tubo - 2 * esp) ** 3) / 12
    c = largura_tubo / 2
    sigma_m = M * c / I
    sigma_momentos.append(sigma_m)
    A_solda = 2 * largura_cordao * esp
    sigma_a = F_axial / A_solda
    sigma_axials.append(sigma_a)

st.write(f"Para a espessura selecionada de {espessura:.2f} mm:")
I_sel = (largura_tubo * largura_tubo ** 3) / 12 - ((largura_tubo - 2 * espessura) * (largura_tubo - 2 * espessura) ** 3) / 12
c_sel = largura_tubo / 2
sigma_m_sel = M * c_sel / I_sel
A_solda_sel = 2 * largura_cordao * espessura
sigma_a_sel = F_axial / A_solda_sel
st.write(f"Tensão por momento (cadeira inclinada): {sigma_m_sel:.2f} MPa")
st.write(f"Tensão axial (cadeira com 4 apoios): {sigma_a_sel:.2f} MPa")

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(espessuras_lista, sigma_momentos, marker='o', label='σ Momento (MPa) - Cadeira Inclinada')
ax.plot(espessuras_lista, sigma_axials, marker='s', label='σ Axial (MPa) - Cadeira 4 Apoios')
ax.axhline(y=155, color='green', linestyle='--', label='Se = 155 MPa (Limite de Fadiga)')
ax.axhline(y=201, color='orange', linestyle='--', label='Sy = 201 MPa (Limite de Escoamento)')
ax.axhline(y=310, color='red', linestyle='--', label='Sut = 310 MPa (Limite de Ruptura)')

# Ajuste do eixo x para mostrar exatamente os valores
ax.set_xticks(espessuras_lista)
ax.set_xticklabels([f'{esp:.2f}' for esp in espessuras_lista])

ax.set_xlabel('Espessura do Tubo (mm)')
ax.set_ylabel('Tensão (MPa)')
ax.set_title('Comparação de Tensões em Função da Espessura')
ax.grid(True)

# Legenda fora do gráfico, abaixo
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

st.pyplot(fig)
