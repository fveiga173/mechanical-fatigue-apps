import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pdfkit

# O código permanece o mesmo até o final atual, onde agora adicionamos o botão para salvar em PDF

if st.button("Salvar relatório em PDF"):
    with open("relatorio_fadiga.html", "w") as f:
        f.write(f"""
        <h1>Relatório de Fadiga - Veiga FatigueCheck</h1>
        <p>Tipo de tubo: {tipo_tubo}</p>
        <p>Largura/Diâmetro: {largura} mm</p>
        <p>Espessura: {espessura} mm</p>
        <p>Largura do cordão: {largura_cordao} mm</p>
        <h2>Caso 1: Cadeira Inclinada</h2>
        <p>Tensão por momento: {sigma_momento:.1f} MPa</p>
        <p>Tensão admissível: {sigma_adm:.1f} MPa</p>
        <h2>Caso 2: Cadeira com 4 Apoios</h2>
        <p>Tensão axial: {sigma_axial:.1f} MPa</p>
        <p>Vida estimada: {N_ciclos:,.0f} ciclos</p>
        """)
    pdfkit.from_file("relatorio_fadiga.html", "relatorio_fadiga.pdf")
    with open("relatorio_fadiga.pdf", "rb") as pdf_file:
        st.download_button("Clique para baixar o relatório em PDF", data=pdf_file, file_name="relatorio_fadiga.pdf")
