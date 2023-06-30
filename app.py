import cv2
import streamlit as st
import os
import numpy as np
import base64

# Configurações do Streamlit
st.set_page_config(page_title='Tratamento de Assinatura',
                   page_icon='img/icone.ico')

# Importa o arquivo CSS


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Chama a função para aplicar o estilo
local_css('style.css')

# código JavaScript para controlar o clique do botão de download
st.markdown(
    """
    <script>
    const downloadButton = document.getElementById('download-button');
    downloadButton.addEventListener('click', function() {
        downloadButton.classList.add('btn-clicked');
    });
    </script>
    """,
    unsafe_allow_html=True
)


def process_image():
    # Exibe um alerta para recortar a imagem antes de usar o programa
    st.image('img/logo.png')
    st.info('Recorte a imagem antes de usar o programa')

    # Texto para o seletor de arquivos
    st.subheader("Selecione o arquivo de imagem:")

    # Abre uma janela para selecionar o arquivo de imagem
    file_path = st.file_uploader('Arraste e solte o arquivo aqui ou clique para selecionar', type=[
                                 'jpeg', 'jpg', 'png', 'bmp'], key='file_uploader')

    # Condição se o arquivo é selecionado
    if file_path is not None:

        # Carrega a imagem
        image1 = cv2.imdecode(np.frombuffer(
            file_path.read(), np.uint8), cv2.IMREAD_COLOR)

        # Converte as cores da imagem para uma escala de cinza
        img = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

        # Cria um controle deslizante para selecionar o valor do limiar
        threshold_value = st.slider('Selecione o valor do filtro:', 80, 250)

        # Aplica o filtro limiar no preview de acordo com o valor do slider
        ret, limiar = cv2.threshold(
            img, threshold_value, 255, cv2.THRESH_BINARY)
        img_new1 = limiar.astype(np.uint8)

        # Exibe o preview da imagem
        st.image(img_new1, caption='Preview', width=500)

        # Botão para aplicar os filtros e fazer o download da imagem tratada
        if st.button('Aplicar filtros'):
            # Aplica o limiar e o filtro de blur na imagem final
            ret, limiar = cv2.threshold(
                img, threshold_value, 255, cv2.THRESH_BINARY)
            blur = cv2.GaussianBlur(limiar, (5, 5), 0)

            # Aplica o filtro de mediana
            img_new1 = cv2.medianBlur(blur, 3)

            # Encontra os contornos na imagem tratada, que fica na cor preta
            contours, _ = cv2.findContours(
                img_new1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Encontra o maior contorno
            max_contour = max(contours, key=cv2.contourArea)

            # Calcula o retângulo delimitador do contorno
            x, y, w, h = cv2.boundingRect(max_contour)

            # Recorta a imagem tratada usando as coordenadas do retângulo delimitador, pra tirar a borda preta
            img_new1 = img_new1[y:y + h, x:x + w]

            # Redimensiona a imagem enquanto o tamanho for maior que 1MB
            max_file_size = 1024 * 1024  # 1MB
            file_size = cv2.imencode('.bmp', img_new1)[
                1].tobytes().__sizeof__()
            while file_size > max_file_size:
                # Redimensiona a imagem pela metade
                img_new1 = cv2.resize(img_new1, None, fx=0.5, fy=0.5)
                file_size = cv2.imencode('.bmp', img_new1)[
                    1].tobytes().__sizeof__()

            # Salva a imagem tratada como um arquivo temporário
            temp_file_path = 'assinaturaTratada_temp.bmp'
            cv2.imwrite(temp_file_path, img_new1)

            # Faz a leitura do arquivo temporário
            with open(temp_file_path, 'rb') as file:
                file_bytes = file.read()

            # Codifica os bytes do arquivo em base64
            b64 = base64.b64encode(file_bytes).decode()

            # Cria o link para download
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="arquivo_tratado.bmp" class="btn-download clicked">Baixar arquivo</a>'

            # Exibe o botão de download
            st.markdown(href, unsafe_allow_html=True)

            # Remove o arquivo temporário
            os.remove(temp_file_path)

    else:
        st.warning('Nenhum arquivo selecionado.')


# Chama a função para processar a imagem
process_image()
