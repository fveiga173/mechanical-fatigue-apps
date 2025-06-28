import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from fpdf import FPDF
import io

# Título e descrição
st.title("Veiga FatigueCheck - Análise de Fadiga em Tubos de Cadeiras")
st.markdown("""
Este app realiza análises de fadiga em cadeiras metálicas conforme a **ISO 7173**, considerando:
- **Caso 1:** Cadeira inclinada (15°) com carga de 950 N (475 N por tubo).
- **Caso 2:** Cadeira com 4 apoios, carga total de 1300 N (325 N por pé).

Utiliza **aço SAE 1008 (Sut = 310 MPa, Se = 155 MPa)**.
""")

# Diagramas
diagramas = Image.open("/mnt/data/A_pair_of_technical_engineering_diagrams_in_black_.png")
st.image(diagramas, caption="Diagramas de análise: cadeira inclinada e cadeira em 4 apoios")

# Entradas
st.header("Entradas")
tipo_tubo = st.selectbox("Tipo de tubo", ["Quadrado", "Redondo"])
if tipo_tubo == "Quadrado":
    largura = st.number_input("Largura do tubo (mm)", value=20.0)
else:
    largura = st.number_input("Diâmetro externo do tubo (mm)", value=25.4)
espessura = st.number_input("Espessura do tubo (mm)", value=0.9)
largura_cordao = st.number_input("Largura do cordão de solda (mm)", value=6.0)

# Constantes
Sut = 310
Se = 0.5 * Sut
FS = 1
a_ciclo = 1e6
b_ciclo = 5
M = 114710  # Momento

# Cálculos
d = largura - 2 * espessura if tipo_tubo == "Redondo" else largura - 2 * espessura
if tipo_tubo == "Quadrado":
    I = (largura * largura**3) / 12 - ((largura - 2 * espessura) * (largura - 2 * espessura)**3) / 12
    c = largura / 2
else:
    I = (np.pi / 64) * (largura**4 - d**4)
    c = largura / 2

sigma_momento = M * c / I
sigma_adm = Se / FS

F_axial = 325
A_solda = (2 * largura_cordao * espessura) if tipo_tubo == "Quadrado" else np.pi * largura * espessura
sigma_axial = F_axial / A_solda
N_ciclos = a_ciclo * (sigma_axial / Sut) ** (-b_ciclo)

# Resultados organizados
col1, col2 = st.columns(2)
with col1:
    st.subheader("Caso 1: Cadeira Inclinada")
    st.write(f"Tensão por momento: **{sigma_momento:.1f} MPa**")
    st.write(f"Tensão admissível (Goodman): **{sigma_adm:.1f} MPa**")
    st.success("✅ Resiste.") if sigma_momento < sigma_adm else st.error("❌ Não resiste.")
with col2:
    st.subheader("Caso 2: Cadeira com 4 Apoios")
    st.write(f"Tensão axial: **{sigma_axial:.1f} MPa**")
    st.write(f"Vida estimada: **{N_ciclos:,.0f} ciclos**")
    st.success("✅ Resiste.") if sigma_axial < sigma_adm else st.error("❌ Não resiste.")

# Gráfico de Goodman
st.subheader("Diagrama de Goodman")
fig, ax = plt.subplots()
sigma_a_vals = np.linspace(0, Sut, 500)
sigma_m_vals = Sut - (Sut / Se) * sigma_a_vals
ax.plot(sigma_a_vals, sigma_m_vals, label="Linha de Goodman", color="red")
ax.axhline(y=sigma_adm, color='green', linestyle='--', label="Tensão admissível")
ax.set_xlabel("Tensão Alternada (MPa)")
ax.set_ylabel("Tensão Média (MPa)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Gerar PDF
if st.button("Salvar relatório em PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Fadiga - Veiga FatigueCheck", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 8, txt=f"""
Tipo de tubo: {tipo_tubo}
Largura/Diâmetro: {largura} mm
Espessura: {espessura} mm
Largura do cordão: {largura_cordao} mm

Caso 1: Cadeira Inclinada
Tensão por momento: {sigma_momento:.1f} MPa
Tensão admissível: {sigma_adm:.1f} MPa
Resultado: {'Resiste' if sigma_momento < sigma_adm else 'Não resiste'}

Caso 2: Cadeira com 4 Apoios
Tensão axial: {sigma_axial:.1f} MPa
Vida estimada: {N_ciclos:,.0f} ciclos
Resultado: {'Resiste' if sigma_axial < sigma_adm else 'Não resiste'}
""")
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    st.download_button(label="Clique para baixar o relatório em PDF", data=pdf_bytes, file_name="relatorio_fadiga.pdf", mime="application/pdf")
