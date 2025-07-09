import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# ========================
# Título e descrição
# ========================
st.title("Checagem de quebra e fadiga em cadeiras - Baseado na ISO 7173")

st.markdown("""
Este app verifica **deformação, ruptura e resistência a ciclos definidos** no ensaio de cadeiras metálicas conforme a **ISO 7173**, 
considerando **o momento real do tubo horizontal + tubo do encosto**.
""")

st.markdown("""
Felipe Veiga - 01 de julho de 2025
""")

# ========================
# Imagem
# ========================
try:
    diagramas = Image.open("A_pair_of_technical_engineering_diagrams_in_black_.png")
    st.image(diagramas)
except:
    st.info("Imagem de diagramas não encontrada no diretório. Coloque a imagem no mesmo repositório para visualização.")

# ========================
# Entradas
# ========================
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])

largura = st.number_input(
    "Largura (quadrado) ou diâmetro externo (redondo) do tubo horizontal (mm)",    value = 20)

espessuras_lista = [0.60, 0.75, 0.90, 1.06, 1.20, 1.50, 1.90]
espessura = st.selectbox(    "Espessura da parede do tubo vertical (mm):",    espessuras_lista,    index = 2)

N_lista = [5_000, 12_500, 25_000, 50_000, 100_000, 200_000]
N_desejado = st.selectbox(    "Número de Ciclos:",    N_lista,    index = 2)

# ========================
# Constantes materiais e do ensaio
# ========================
Sut = 310                     # MPa
Sy = 0.65 * Sut               # MPa
Se = 0.5 * Sut                # MPa
a_ciclo = 1e6
b_ciclo = 5

# ========================
# Cargas do ensaio ISO 7173
# ========================
F_vertical_per_foot = 237.5   # N
F_horizontal = 165            # N

# ========================
# Momento gerado pelo tubo horizontal fixo
# ========================
q = 950                       # N/m
L = 0.5                       # m

M_fixo_horizontal = (q * L ** 2) / 12
M_fixo_horizontal_Nmm = M_fixo_horizontal * 1_000

# ========================
# Momento gerado pela força horizontal do encosto
# ========================
altura_encosto = 750          # mm
altura_assento = 450          # mm

braço_momento_encosto = (altura_encosto - altura_assento) / 1_000
M_encosto = F_horizontal * braço_momento_encosto
M_encosto_Nmm = M_encosto * 1_000

# ========================
# Momento total na junta
# ========================
M_total = M_fixo_horizontal_Nmm + M_encosto_Nmm

# ========================
# Tensão na garganta da solda
# ========================
if tipo_tubo == 'Quadrado':
    I_quadrado = largura * (largura ** 2) / 2
    sigma_total = (M_total * largura / 2) / (0.707 * espessura * I_quadrado)
else:
    I_redondo = (largura**2/6)*(3*largura+largura)
    sigma_total = (M_total * largura / 2) / (0.707 * espessura * I_redondo)

# ========================
# Cálculo da tensão de fadiga
# ========================
sigma_fadiga_admissivel = Se * (a_ciclo / N_desejado) ** (1 / b_ciclo)

# ========================
# Resultados
# ========================
st.subheader("Resultados do Ensaio ISO 7173")

st.write(f"Momento do tubo horizontal: {M_fixo_horizontal:.2f} Nm")
st.write(f"Momento da força do encosto: {M_encosto:.2f} Nm")
st.write(f"Tensão na garganta da solda: {sigma_total:.2f} MPa")
st.write(f"**Ciclos desejados:** {N_desejado:,}")
st.write(f"Tensão de fadiga admissível para os ciclos: {sigma_fadiga_admissivel:.2f} MPa")

# ========================
# Análises
# ========================
if sigma_total < Sy:
    st.success("✅ **APROVADO**: Não ocorre deformação permanente (Sy).")
elif Sy <= sigma_total < Sut:
    st.warning("⚠️ **ATENÇÃO**: Pode ocorrer deformação permanente, mas não ruptura imediata (entre Sy e Sut).")
else:
    st.error("❌ **FALHA**: Pode ocorrer ruptura sob carga estática (acima de Sut).")

if sigma_fadiga_admissivel > Sut:
    if sigma_total < Sut:
        st.success(f"✅ A tensão de fadiga admissível calculada ({sigma_fadiga_admissivel:.2f} MPa) excede o limite de ruptura ({Sut} MPa), "
            f"mas como a tensão aplicada ({sigma_total:.2f} MPa) está abaixo de {Sut} MPa, o componente **NÃO ROMPE e RESISTE** "
            f"ao ensaio de {N_desejado:,} ciclos.")
    else:
        st.error(f"❌ A tensão de fadiga admissível calculada ({sigma_fadiga_admissivel:.2f} MPa) excede o limite de ruptura ({Sut} MPa), "
            f"e a tensão aplicada ({sigma_total:.2f} MPa) também excede, indicando ROMPIMENTO sob carga estática antes de {N_desejado:,} ciclos.")

elif sigma_total < sigma_fadiga_admissivel:
    st.success(f"✅ Resiste ao ensaio de fadiga de {N_desejado:,} ciclos.")

else:
    st.error(f"❌ Pode falhar antes de {N_desejado:,} ciclos no ensaio de fadiga.")

# ========================
# Comparação por espessura
# ========================

st.subheader("📊 Comparação por Espessura no Ensaio ISO 7173")

sigma_totais = []

for esp in espessuras_lista:
    if tipo_tubo == 'Quadrado':
        I_quadrado = largura * (largura ** 2) / 2
        sigma_total_esp = (M_total * largura / 2) / (0.707 * esp * I_quadrado)
    else:
        I_redondo = np.pi * (largura / 2) ** 3
        sigma_total_esp = (M_total * largura / 2) / (0.707 * esp * I_redondo)
    sigma_totais.append(sigma_total_esp)

cores = [    'skyblue' if esp != espessura else 'orange'
    for esp in espessuras_lista]

fig, ax = plt.subplots(figsize = (8, 5))

bars = ax.bar([str(e) for e in espessuras_lista],    sigma_totais,    color = cores)

ax.axhline(Sut, color = 'red', linestyle = '--', label = f'Sut = {Sut} MPa (Ruptura)')
ax.axhline(Sy, color = 'orange', linestyle = '--', label = f'Sy = {Sy:.0f} MPa (Deformação)')
ax.axhline(sigma_fadiga_admissivel, color = 'green', linestyle = '--', label = f'Se ({N_desejado:,} ciclos) = {sigma_fadiga_admissivel:.0f} MPa (Fadiga)')

for bar, sigma in zip(bars, sigma_totais):
    height = bar.get_height()
    ax.annotate(f"{sigma:.0f}", xy = (bar.get_x() + bar.get_width() / 2, height), xytext = (0, 5), textcoords = "offset points", ha = 'center', va = 'bottom')

ax.set_xlabel("Espessura da Parede do Tubo (mm)")
ax.set_ylabel("Tensão Total (MPa)")
ax.set_title("Tensão Total x Espessura - Ensaio ISO 7173")
ax.grid(True, axis = 'y')
ax.legend(loc = 'upper center', bbox_to_anchor = (0.5, -0.15), ncol = 2)

st.pyplot(fig)

# ========================
# Comentário interpretativo
# ========================
st.info(f"""
✅ **Como interpretar:**
- Cada barra mostra a tensão total para cada espessura do tubo vertical.
- A barra **laranja** é a espessura selecionada pelo usuário.
- Se a barra estiver **abaixo de Sy (linha laranja)**, não ocorre deformação.
- Se entre **Sy e Sut (linha vermelha)**, pode ocorrer deformação permanente.
- Se **acima de Sut**, pode ocorrer ruptura sob carga estática.
- Se abaixo da linha verde (Se para {N_desejado:,} ciclos), resiste ao ensaio de fadiga.""")
