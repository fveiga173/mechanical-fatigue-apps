import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Título e descrição
st.title("Veiga FatigueCheck - Análise de resistência em cadeiras soldadas")
st.markdown("Este app realiza análises de resistência em cadeiras metálicas conforme a **ISO 7173**, com foco realista na falha por tração perpendicular na parede do tubo horizontal (onde realmente ocorre a falha), considerando aço SAE 1008 (Sut=310 MPa, Sy=201 MPa, Se=155 MPa). Utilize capturas de tela para registrar os resultados em PDF quando necessário.")

# Imagem
tente:
    diagramas = Image.open("A_pair_of_technical_engineering_diagrams_in_black_.png")
    st.image(diagramas, caption="Diagramas de análise: cadeira inclinada e cadeira em 4 apoios")
exceto:
    st.info("Imagem de diagramas não encontrada no diretório. Coloque a imagem no mesmo repositório para visualização.")

# Entradas
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])
largura = st.number_input("Largura (quadrado) ou diâmetro externo (redondo) do tubo (mm)", value=20.0)
espessuras_lista = [0.60, 0.75, 0.90, 1.06, 1.20, 1.50, 1.90]  # mm
espessura = st.selectbox("Selecione a espessura do tubo para visualização detalhada:", espessuras_lista, index=2)
largura_cordao = st.number_input("Largura do cordão de solda (mm)", value=6.0)

# Constantes
Sut = 310
Sy = 0.65 * Sut  # ≈ 201 MPa
Se = 0.5 * Sut    # 155 MPa
M = 114710  # Momento aplicado na cadeira inclinada
F_axial = 475  # N (carga axial por pé traseiro)

# Cálculos focados na parede do tubo horizontal, sem foco na falha do cordão de solda
if tipo_tubo == "Quadrado":
    I = (largura * largura**3) / 12 - ((largura - 2 * espessura) * (largura - 2 * espessura)**3) / 12
    c = largura / 2
else:  # Redondo
    d_interno = largura - 2 * espessura
    I = (np.pi / 64) * (largura**4 - d_interno**4)
    c = largura / 2

# Caso 1: cadeira inclinada
sigma_momento = M * c / I  # tensão na parede do tubo horizontal

# Caso 2: carga axial (mantém para fadiga)
A_solda = 2 * largura_cordao * espessura if tipo_tubo == "Quadrado" else np.pi * largura*1.3 * espessura
sigma_axial = F_axial / A_solda
N_ciclos = 1e6 * (sigma_axial / Sut) ** (-5)

# Resultados
st.subheader("Resultados")

st.markdown("**Caso 1: Cadeira Inclinada (Análise da parede do tubo)**")
st.write(f"Tensão por momento: {sigma_momento:.2f} MPa")
st.write(f"Limite de escoamento (Sy): {Sy:.2f} MPa")
st.write(f"Limite de ruptura (Sut): {Sut:.2f} MPa")

if sigma_momento < Sy:
    st.success("✅ A parede do tubo RESISTE ao momento aplicado (sem deformação permanente).")
elif Sy <= sigma_momento < Sut:
    st.warning("⚠️ A parede do tubo pode sofrer **deformação plástica**, mas não ruptura imediata.")
else:
    st.error("❌ A parede do tubo pode **romper sob o momento aplicado**.")

st.markdown("**Caso 2: Cadeira com 4 Apoios (Análise de Fadiga)**")
st.write(f"Tensão axial na solda: {sigma_axial:.2f} MPa")
st.write(f"Vida estimada: {N_ciclos:,.0f} ciclos")

if sigma_axial < Sy:
    st.success("✅ A solda RESISTE ao carregamento axial (sem deformação permanente).")
else:
    st.error("❌ A solda pode sofrer **deformação ou falha por fadiga** sob o carregamento axial.")


# Seção final: Análise Comparativa por Espessura (ajustada para tubo quadrado e redondo)

t.subheader("Análise Comparativa por Espessura (Parede do Tubo)")

sigma_momentos = []
sigma_axials = []

for esp in espessuras_lista:
    if tipo_tubo == "Quadrado":
        I = (largura * largura**3) / 12 - ((largura - 2 * esp) * (largura - 2 * esp)**3) / 12
        c = largura / 2
        A_parede = 2 * largura * esp
    else:
        d_interno = largura - 2 * esp
        I = (np.pi / 64) * (largura**4 - d_interno**4)
        c = largura / 2
        A_parede = np.pi * largura * esp

    sigma_m = M * c / I
    sigma_a = F_axial / A_parede

    sigma_momentos.append(sigma_m)
    sigma_axials.append(sigma_a)

st.write(f"Para a espessura selecionada de {espessura:.2f} mm:")
if tipo_tubo == "Quadrado":
    I_sel = (largura * largura**3) / 12 - ((largura - 2 * espessura) * (largura - 2 * espessura)**3) / 12
    c_sel = largura / 2
    A_sel = 2 * largura * espessura
else:
    d_interno_sel = largura - 2 * espessura
    I_sel = (np.pi / 64) * (largura**4 - d_interno_sel**4)
    c_sel = largura / 2
    A_sel = np.pi * largura * espessura

sigma_m_sel = M * c_sel / I_sel
sigma_a_sel = F_axial / A_sel

st.write(f"Tensão por momento (cadeira inclinada): {sigma_m_sel:.2f} MPa")
st.write(f"Tensão axial (cadeira com 4 apoios): {sigma_a_sel:.2f} MPa")

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(espessuras_lista, sigma_momentos, marker='o', label='σ Momento (MPa) - Cadeira Inclinada')
ax.plot(espessuras_lista, sigma_axials, marker='s', label='σ Axial (MPa) - Cadeira 4 Apoios')
ax.axhline(y=155, color='green', linestyle='--', label='Se = 155 MPa (Limite de Fadiga)')
ax.axhline(y=201, color='orange', linestyle='--', label='Sy = 201 MPa (Limite de Escoamento)')
ax.axhline(y=310, color='red', linestyle='--', label='Sut = 310 MPa (Limite de Ruptura)')

ax.set_xticks(espessuras_lista)
ax.set_xticklabels([f'{esp:.2f}' for esp in espessuras_lista])
ax.set_xlabel('Espessura do Tubo (mm)')
ax.set_ylabel('Tensão (MPa)')
ax.set_title('Comparação de Tensões em Função da Espessura (Parede do Tubo)')
ax.grid(True)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

st.pyplot(fig)
