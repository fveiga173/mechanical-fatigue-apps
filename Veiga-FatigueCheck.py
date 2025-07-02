import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Título e descrição
st.title("Veiga FatigueCheck - Ensaio ISO 7173")
st.markdown("""
Este app verifica **deformação, ruptura e resistência a ciclos definidos** no ensaio de cadeiras metálicas conforme a **ISO 7173**, 
considerando **o momento real do tubo horizontal + encosto**.
""")

# Imagem
try:
    diagramas = Image.open("A_pair_of_technical_engineering_diagrams_in_black_.png")
    st.image(diagramas)
except:
    st.info("Imagem de diagramas não encontrada no diretório. Coloque a imagem no mesmo repositório para visualização.")

# Entradas
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])
largura = st.number_input("Largura (quadrado) ou diâmetro externo (redondo) do tubo horizontal (mm)", value=22.22)
espessuras_lista = [0.60, 0.75, 0.90, 1.06, 1.20, 1.50, 1.90]
espessura = st.selectbox("Espessura da parede do tubo vertical (mm):", espessuras_lista, index=2)
N_lista = [12500, 25000, 50000, 100000, 200000]
N_desejado = st.selectbox("Número de Ciclos:", N_lista, index=2)

# Constantes materiais e do ensaio
Sut = 310  # Limite de Ruptura em MPa
Sy = 0.65 * Sut  # Limite de escoamento em MPa
Se = 0.5 * Sut  # Limite de fadiga em MPa (ciclo de vida infinito)
a_ciclo = 1e6  # Parametros para posterior calculo do ciclo de vida no N desejado
b_ciclo = 5    # Parametros para posterior calculo do ciclo de vida no N desejado

# Cargas do ensaio ISO 7173
F_vertical_per_foot = 237.5  # N por pé (assento)
F_horizontal = 165  # N por pé traseiro (encosto)

# Momento gerado pelo tubo horizontal fixo:
q = 950  # N/m (475 N distribuídos em 0.5 m)
L = 0.5  # m
M_fixo_horizontal = (q * L**2) / 12  # Nm
M_fixo_horizontal_Nmm = M_fixo_horizontal * 1000  # Nmm

# Momento gerado pela força horizontal do encosto:
altura_encosto = 750  # mm
altura_assento = 450  # mm
braço_momento_encosto = (altura_encosto - altura_assento) / 1000  # m
M_encosto = F_horizontal * braço_momento_encosto  # Nm
M_encosto_Nmm = M_encosto * 1000  # Nmm

# Momento total na junta:
M_total = M_fixo_horizontal_Nmm + M_encosto_Nmm  # Nmm

# Área resistente:
if tipo_tubo == 'Quadrado':
    A_resistente = largura * espessura  # mm²
else:
    # Para tubo redondo, área da parede: A = π * (D_ext^2 - D_int^2) / 4
    D_ext = largura  # onde 'largura' aqui é o diâmetro externo
    D_int = D_ext - 2 * espessura
    A_resistente = ((np.pi * (D_ext**2 - D_int**2)) / 4)/2  # mm²


# Braço de alavanca:
d = largura / 2  # mm

# Tensão por momento:
sigma_total = M_total / (A_resistente * d)  # MPa


# Cálculo da tensão de fadiga:
sigma_fadiga_admissivel = Se * (a_ciclo / N_desejado) ** (1 / b_ciclo)

# Resultados
st.subheader("Resultados do Ensaio ISO 7173")
st.write(f"Momento do tubo horizontal: {M_fixo_horizontal:.2f} Nm")
st.write(f"Momento da força do encosto: {M_encosto:.2f} Nm")
st.write(f"Área resistente considerada: {A_resistente:.1f} mm²")
st.write(f"Tensão por momento resultante na parede do tubo (tração): {sigma_total:.2f} MPa")
st.write(f"**Ciclos desejados:** {N_desejado:,}")
st.write(f"Tensão de fadiga admissível para os ciclos: {sigma_fadiga_admissivel:.2f} MPa")

# Análises
if sigma_total < Sy:
    st.success("✅ **APROVADO**: Não ocorre deformação permanente (Sy).")
elif Sy <= sigma_total < Sut:
    st.warning("⚠️ **ATENÇÃO**: Pode ocorrer deformação permanente, mas não ruptura imediata (entre Sy e Sut).")
else:
    st.error("❌ **FALHA**: Pode ocorrer ruptura sob carga estática (acima de Sut).")

if sigma_fadiga_admissivel > Sut:
    if sigma_total < Sut:
        st.success(f"✅ A tensão de fadiga admissível calculada ({sigma_fadiga_admissivel:.2f} MPa) excede o limite de ruptura ({Sut} MPa), mas como a tensão aplicada ({sigma_total:.2f} MPa) está abaixo de {Sut} MPa, o componente **NÃO ROMPE e RESISTE** ao ensaio de {N_desejado:,} ciclos.")
    else:
        st.error(f"❌ A tensão de fadiga admissível calculada ({sigma_fadiga_admissivel:.2f} MPa) excede o limite de ruptura ({Sut} MPa), e a tensão aplicada ({sigma_total:.2f} MPa) também excede, indicando ROMPIMENTO sob carga estática antes de {N_desejado:,} ciclos.")
elif sigma_total < sigma_fadiga_admissivel:
    st.success(f"✅ Resiste ao ensaio de fadiga de {N_desejado:,} ciclos.")
else:
    st.error(f"❌ Pode falhar antes de {N_desejado:,} ciclos no ensaio de fadiga.")

# ============================
# COMPARAÇÃO POR ESPESSURA
# ============================
st.subheader("📊 Comparação por Espessura no Ensaio ISO 7173")

sigma_totais = []

for esp in espessuras_lista:
    if tipo_tubo == 'Quadrado':
        A_resistente = largura * esp  # Corrigir aqui para usar 'esp' do loop
    else:
        D_ext = largura
        D_int = D_ext - 2 * esp  # Corrigir aqui para usar 'esp' do loop
        A_resistente = ((np.pi * (D_ext**2 - D_int**2)) / 4)/2  # mm²

    d = largura / 2  # mm
    sigma_total = M_total / (A_resistente * d)

   
    sigma_totais.append(sigma_total)
    
cores = ['skyblue' if esp != espessura else 'orange' for esp in espessuras_lista]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(
    [str(e) for e in espessuras_lista],
    sigma_totais,
    color=cores
)

ax.axhline(Sut, color='red', linestyle='--', label=f'Sut = {Sut} MPa (Ruptura)')
ax.axhline(Sy, color='orange', linestyle='--', label=f'Sy = {Sy:.0f} MPa (Deformação)')
ax.axhline(sigma_fadiga_admissivel, color='green', linestyle='--',
           label=f'Se ({N_desejado:,} ciclos) = {sigma_fadiga_admissivel:.0f} MPa (Fadiga)')

for bar, sigma in zip(bars, sigma_totais):
    height = bar.get_height()
    ax.annotate(f"{sigma:.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha='center', va='bottom')

ax.set_xlabel("Espessura da Parede do Tubo (mm)")
ax.set_ylabel("Tensão Total (MPa)")
ax.set_title("Tensão Total x Espessura - Ensaio ISO 7173")
ax.grid(True, axis='y')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

st.pyplot(fig)

# Comentário interpretativo
st.info(f"""
✅ **Como interpretar:**
- Cada barra mostra a tensão total para cada espessura do tubo vertical.
- A barra **laranja** é a espessura selecionada pelo usuário.
- Se a barra estiver **abaixo de Sy (linha laranja)**, não ocorre deformação.
- Se entre **Sy e Sut (linha vermelha)**, pode ocorrer deformação permanente.
- Se **acima de Sut**, pode ocorrer ruptura sob carga estática.
- Se abaixo da linha verde (Se para {N_desejado:,} ciclos), resiste ao ensaio de fadiga.
""")
