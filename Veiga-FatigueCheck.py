import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Título e descrição
st.title("Veiga FatigueCheck - Ensaio ISO 7173")
st.markdown("""
Este app verifica **deformação, ruptura e resistência a 50.000 ciclos** no ensaio de cadeiras metálicas conforme a **ISO 7173**, 
calculando a tensão de tração na parede do tubo traseiro gerada pelo momento do encosto e a compressão do assento.
""")

# Entradas
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])
largura = st.number_input("Largura (quadrado) ou diâmetro externo (redondo) do tubo (mm)", value=22.22)
espessuras_lista = [0.60, 0.75, 0.90, 1.06, 1.20, 1.50, 1.90]
espessura = st.selectbox("Selecione a espessura da parede do tubo (mm):", espessuras_lista, index=2)

# Constantes materiais e do ensaio
Sut = 310  # MPa
Sy = 0.65 * Sut  # 201 MPa
Se = 0.5 * Sut  # 155 MPa
FS = 1
a_ciclo = 1e6
b_ciclo = 5

# Cargas do ensaio ISO 7173
F_vertical = 325  # N por pé (assento)
F_horizontal = 280  # N por pé traseiro (encosto)
altura_encosto = 450  # mm (altura da aplicação da força horizontal)

# Cálculo do momento gerado pelo encosto
M = F_horizontal * altura_encosto  # N.mm

# Cálculo da área resistente na parede do tubo traseiro:
if tipo_tubo == "Quadrado":
    perimetro_solda = 2 * largura  # apenas superior e inferior
else:
    perimetro_solda = np.pi * largura  # solda total

# Área efetiva onde a força se distribui (espessura da parede vezes perímetro)
A_resistente = perimetro_solda * espessura  # mm²

# Cálculo da tensão gerada pelo momento (traciona metade superior da parede)
# Considera distribuição linear simplificada:
sigma_momento = M / (A_resistente * (largura / 2))  # MPa

# Cálculo da tensão de compressão pelo peso da pessoa:
sigma_compressao = F_vertical / A_resistente  # MPa

# Tensão total = tração (momento) - compressão
sigma_total = sigma_momento - sigma_compressao  # MPa

# Verificação de fadiga para 50.000 ciclos
# Estimativa simplificada usando a curva de fadiga:
N_desejado = 50000
sigma_fadiga_admissivel = Se * (a_ciclo / N_desejado) ** (1 / b_ciclo)

# Resultados
st.subheader("Resultados do Ensaio ISO 7173")
st.write(f"Tensão por momento (tração): {sigma_momento:.2f} MPa")
st.write(f"Tensão por compressão: {sigma_compressao:.2f} MPa")
st.write(f"**Tensão total resultante na parede do tubo:** {sigma_total:.2f} MPa")
st.write(f"Tensão de fadiga admissível para 50.000 ciclos: {sigma_fadiga_admissivel:.2f} MPa")

# Análises
if sigma_total < Sy:
    st.success("✅ **APROVADO**: Não ocorre deformação permanente (Sy).")
elif Sy <= sigma_total < Sut:
    st.warning("⚠️ **ATENÇÃO**: Pode ocorrer deformação permanente, mas não ruptura imediata (entre Sy e Sut).")
else:
    st.error("❌ **FALHA**: Pode ocorrer ruptura sob carga estática (acima de Sut).")

if sigma_total < sigma_fadiga_admissivel:
    st.success("✅ Resiste ao ensaio de fadiga de 50.000 ciclos.")
else:
    st.error("❌ Pode falhar antes de 50.000 ciclos no ensaio de fadiga.")

# ============================
# COMPARAÇÃO POR ESPESSURA
# ============================

st.subheader("📊 Comparação por Espessura no Ensaio ISO 7173")

espessuras_lista = [0.60, 0.75, 0.90, 1.06, 1.20, 1.50, 1.90]  # mm
sigma_totais = []

for esp in espessuras_lista:
    if tipo_tubo == "Quadrado":
        perimetro_solda = 2 * largura  # apenas superior e inferior
    else:
        perimetro_solda = np.pi * largura  # solda total

    A_resistente = perimetro_solda * esp  # mm²
    sigma_momento = M / (A_resistente * (largura / 2))  # MPa
    sigma_compressao = F_vertical / A_resistente  # MPa
    sigma_total = sigma_momento - sigma_compressao  # MPa
    sigma_totais.append(sigma_total)

# Definir cores destacando a espessura selecionada
cores = ['skyblue' if esp != espessura else 'orange' for esp in espessuras_lista]

# Gráfico de barras
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(
    [str(e) for e in espessuras_lista],
    sigma_totais,
    color=cores,
    label='Tensão Total (MPa)'
)

# Linhas de referência
ax.axhline(Sut, color='red', linestyle='--', label=f'Sut = {Sut} MPa (Ruptura)')
ax.axhline(Sy, color='orange', linestyle='--', label=f'Sy = {Sy:.0f} MPa (Deformação)')
ax.axhline(sigma_fadiga_admissivel, color='green', linestyle='--',
           label=f'Se (50k ciclos) = {sigma_fadiga_admissivel:.0f} MPa (Fadiga)')

# Anotação em cada barra
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
st.info("""
✅ **Como interpretar:**
- Cada barra representa a tensão total para cada espessura.
- A barra **laranja** é a espessura selecionada pelo usuário.
- Se a barra estiver **abaixo de Sy (linha laranja)**, não ocorre deformação.
- Se entre **Sy e Sut (linha vermelha)**, pode ocorrer deformação permanente.
- Se **acima de Sut**, pode ocorrer ruptura sob carga estática.
- Se abaixo da linha verde (Se 50k ciclos), resiste ao ensaio de fadiga.
""")
