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

# Gráfico para visualização rápida
fig, ax = plt.subplots(figsize=(6, 4))
ax.axhline(Sut, color='red', linestyle='--', label=f'Sut = {Sut} MPa')
ax.axhline(Sy, color='orange', linestyle='--', label=f'Sy = {Sy:.0f} MPa')
ax.axhline(sigma_fadiga_admissivel, color='green', linestyle='--', label=f'Se(50k ciclos) = {sigma_fadiga_admissivel:.0f} MPa')
ax.bar(['Tensão Total'], [sigma_total], color='blue', label=f'Tensão Calculada = {sigma_total:.1f} MPa')
ax.set_ylabel('Tensão (MPa)')
ax.set_title('Comparação de Tensões no Ensaio ISO 7173')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
ax.grid(True)

st.pyplot(fig)
