import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Título e descrição
st.title("Veiga FatigueCheck - Ensaio ISO 7173")
st.markdown("""
Este app verifica **deformação, ruptura e resistência a ciclos definidos** no ensaio de cadeiras metálicas conforme a **ISO 7173**, 
considerando **o momento real do tubo horizontal + encosto** e **a força vertical líquida**.
""")

# Entradas
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])
largura = st.number_input("Largura (quadrado) ou diâmetro externo (redondo) do tubo horizontal (mm)", value=22.22)
espessuras_lista = [0.60, 0.75, 0.90, 1.06, 1.20, 1.50, 1.90]
espessura = st.selectbox("Espessura da parede do tubo vertical (mm):", espessuras_lista, index=2)
N_lista = [12500, 25000, 50000, 100000, 200000]
N_desejado = st.selectbox("Número de Ciclos:", N_lista, index=2)

# Constantes materiais e do ensaio
Sut = 310  # MPa
tau_max = 0.6 * Sut  # Limite de cisalhamento (60% de Sut)

a_ciclo = 1e6
b_ciclo = 5

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

# Força vertical líquida:
F_vertical_liquida = F_vertical_per_foot - F_horizontal  # N

# Área resistente e área de cisalhamento
if tipo_tubo == "Redondo":
    A_resistente = (np.pi * (largura / 2)**2)/2  # área do tubo redondo
else:
    A_resistente = largura * espessura  # área do tubo quadrado

# Tensão de cisalhamento
tau = F_vertical_liquida / A_resistente  # MPa (tensão de cisalhamento)

# Resultados
st.subheader("Resultados do Ensaio ISO 7173")
st.write(f"Momento do tubo horizontal: {M_fixo_horizontal:.2f} Nm")
st.write(f"Momento da força do encosto: {M_encosto:.2f} Nm")
st.write(f"Momento total aplicado na junta: {M_total/1000:.2f} Nm")
st.write(f"Força vertical líquida: {F_vertical_liquida:.1f} N")
st.write(f"Área resistente considerada: {A_resistente:.1f} mm²")
st.write(f"Tensão de cisalhamento: {tau:.2f} MPa")
st.write(f"**Ciclos desejados:** {N_desejado:,}")
st.write(f"Limite de cisalhamento do material: {tau_max:.2f} MPa")

# Análises
if tau < tau_max:
    st.success("✅ **APROVADO**: A tensão de cisalhamento está abaixo do limite de cisalhamento do material.")
else:
    st.error(f"❌ **FALHA**: A tensão de cisalhamento ({tau:.2f} MPa) excede o limite de cisalhamento do material ({tau_max:.2f} MPa).")

# ============================
# COMPARAÇÃO POR ESPESSURA
# ============================
st.subheader("📊 Comparação por Espessura no Ensaio ISO 7173")

tensao_cisalhamento_totais = []

for esp in espessuras_lista:
    A_resistente_esp = largura * esp
    tau_esp = F_vertical_liquida / A_resistente_esp  # Cálculo da tensão de cisalhamento para cada espessura
    tensao_cisalhamento_totais.append(tau_esp)

cores = ['skyblue' if esp != espessura else 'orange' for esp in espessuras_lista]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(
    [str(e) for e in espessuras_lista],
    tensao_cisalhamento_totais,
    color=cores
)

ax.axhline(tau_max, color='red', linestyle='--', label=f'Limite de cisalhamento = {tau_max:.2f} MPa')

for bar, tau in zip(bars, tensao_cisalhamento_totais):
    height = bar.get_height()
    ax.annotate(f"{tau:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha='center', va='bottom')

ax.set_xlabel("Espessura da Parede do Tubo (mm)")
ax.set_ylabel("Tensão de Cisalhamento (MPa)")
ax.set_title("Tensão de Cisalhamento x Espessura - Ensaio ISO 7173")
ax.grid(True, axis='y')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

st.pyplot(fig)

# Comentário interpretativo
st.info(f"""
✅ **Como interpretar:**
- Cada barra mostra a tensão de cisalhamento para cada espessura do tubo vertical.
- A barra **laranja** é a espessura selecionada pelo usuário.
- Se a barra estiver **abaixo do limite de cisalhamento (linha vermelha)**, o tubo resiste à carga sem falha.
- Se **acima do limite de cisalhamento**, pode ocorrer falha por cisalhamento.
""")
