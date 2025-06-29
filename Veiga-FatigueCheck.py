import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Título e descrição
st.title("Veiga FatigueCheck - Ensaio ISO 7173 (Ajustado)")
st.markdown("""
Este app verifica **deformação, ruptura e resistência a 50.000 ciclos** no ensaio de cadeiras metálicas conforme a **ISO 7173**, 
calculando a tensão real de tração na parede do tubo traseiro causada pela solda e a compressão do assento.
""")

# Entradas
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])
largura = st.number_input("Largura (quadrado) ou diâmetro externo (redondo) do tubo horizontal (mm)", value=22.22)
espessuras_lista = [0.60, 0.75, 0.90, 1.06, 1.20, 1.50, 1.90]
espessura = st.selectbox("Espessura da parede do tubo vertical (mm):", espessuras_lista, index=2)
altura_encosto = st.number_input("Altura do centro do encosto (mm)", value=750)
N__lista = [12.500, 25.000, 50.000, 100.000, 200.000]
N_desejado = st.selectbox("Número de Ciclos:", N_lista, index=3)

# Constantes materiais e do ensaio
Sut = 310  # MPa
Sy = 0.65 * Sut  # 201 MPa
Se = 0.5 * Sut  # 155 MPa
a_ciclo = 1e6
b_ciclo = 5

# Cargas do ensaio ISO 7173
F_vertical = 330/2  # N por pé (assento)
F_horizontal = 950/4  # N por pé traseiro (encosto)


# Cálculo do momento gerado pelo encosto
M = F_horizontal * altura_encosto  # N.mm

# Área resistente real: largura do tubo horizontal x espessura do tubo vertical
A_resistente = largura * espessura  # mm²

# Braço de alavanca aproximado como metade da largura
d = largura / 2  # mm

# Tensão por momento
sigma_momento = M / (A_resistente * d)  # MPa

# Tensão de compressão pelo assento
sigma_compressao = F_vertical / A_resistente  # MPa

# Tensão total: tração (momento) - compressão
sigma_total = sigma_momento - sigma_compressao  # MPa

# Verificação de fadiga para 50.000 ciclos

sigma_fadiga_admissivel = Se * (a_ciclo / N_desejado) ** (1 / b_ciclo)

# Resultados
st.subheader("Resultados do Ensaio ISO 7173 (Corrigido)")
st.write(f"Área resistente considerada: {A_resistente:.1f} mm²")
st.write(f"Tensão por momento (tração): {sigma_momento:.2f} MPa")
st.write(f"Tensão por compressão: {sigma_compressao:.2f} MPa")
st.write(f"**Tensão total resultante na parede do tubo:** {sigma_total:.2f} MPa")
st.write(f"**Ciclos desejados** {N_desejado:.0f}")
st.write(f"Tensão de fadiga admissível para os ciclos: {sigma_fadiga_admissivel:.2f} MPa")

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

st.subheader("📊 Comparação por Espessura no Ensaio ISO 7173 (Corrigido)")

sigma_totais = []

for esp in espessuras_lista:
    A_resistente_esp = largura * esp
    sigma_momento_esp = M / (A_resistente_esp * d)
    sigma_compressao_esp = F_vertical / A_resistente_esp
    sigma_total_esp = sigma_momento_esp - sigma_compressao_esp
    sigma_totais.append(sigma_total_esp)

# Cores para destaque da espessura selecionada
cores = ['skyblue' if esp != espessura else 'orange' for esp in espessuras_lista]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(
    [str(e) for e in espessuras_lista],
    sigma_totais,
    color=cores
)

# Linhas de referência
ax.axhline(Sut, color='red', linestyle='--', label=f'Sut = {Sut} MPa (Ruptura)')
ax.axhline(Sy, color='orange', linestyle='--', label=f'Sy = {Sy:.0f} MPa (Deformação)')
ax.axhline(sigma_fadiga_admissivel, color='green', linestyle='--',
           label=f'Se (50k ciclos) = {sigma_fadiga_admissivel:.0f} MPa (Fadiga)')

# Anotações em cada barra
for bar, sigma in zip(bars, sigma_totais):
    height = bar.get_height()
    ax.annotate(f"{sigma:.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha='center', va='bottom')

ax.set_xlabel("Espessura da Parede do Tubo (mm)")
ax.set_ylabel("Tensão Total (MPa)")
ax.set_title("Tensão Total x Espessura - Ensaio ISO 7173 (Corrigido)")
ax.grid(True, axis='y')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)

st.pyplot(fig)

# Comentário interpretativo
st.info("""
✅ **Como interpretar:**
- Cada barra mostra a tensão total para cada espessura do tubo vertical.
- A barra **laranja** é a espessura selecionada pelo usuário.
- Se a barra estiver **abaixo de Sy (linha laranja)**, não ocorre deformação.
- Se entre **Sy e Sut (linha vermelha)**, pode ocorrer deformação permanente.
- Se **acima de Sut**, pode ocorrer ruptura sob carga estática.
- Se abaixo da linha verde (Se 50k ciclos), resiste ao ensaio de fadiga.
""")
