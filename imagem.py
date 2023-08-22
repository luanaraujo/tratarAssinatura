import cv2
import tkinter as tk
from tkinter import filedialog, Label, Button, Scale, messagebox, Frame
import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


root = tk.Tk()
root.withdraw()

# Define o caminho para o arquivo de ícone (.ico)
icon_path = 'img/icone.ico'

# Altera o ícone do programa
root.iconbitmap(icon_path)


def process_image():

    # Exibe um alerta para recortar a imagem antes de usar o programa
    messagebox.showinfo('Alerta', 'Recorte a imagem antes de usar o programa')
    root.title('Selecionar arquivo de imagem')
    root.withdraw()
    file_path = filedialog.askopenfilename(
        filetypes=[('Image Files', ('*.jpeg', '*.jpg', '*.png', '*.bmp'))])

    # Condição se o arquivo é selecionado
    if file_path:
        # Carrega a imagem
        file_path = os.path.normpath(file_path)
        image1 = cv2.imread(file_path)

        # Converte as cores da imagem para uma escala de cinza
        img = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

        # Abre uma janela para selecionar o diretório de destino
        root.title('Selecionar pasta de destino')
        root.withdraw()
        directory = filedialog.askdirectory()

        # Condição se a pasta de destino é selecionada
        if directory:
            # Cria um controle deslizante para selecionar o valor do limiar
            threshold_root = tk.Tk()
            threshold_root.withdraw()
            messagebox.showinfo(
                'Alerta', 'Selecione agora o valor do filtro, geralmente fica entre 100-180, depende se o fundo da imagem está muito escuro. Se tiver muito escuro, selecione um valor baixo')
            # Cria uma nova janela
            threshold_root = tk.Tk()
            threshold_root.title('Filtro')
            threshold_root.iconbitmap(icon_path)

            largura = 600
            altura = 600

            # Puxa a largura e altura da tela
            largura_tela = threshold_root.winfo_screenwidth()
            altura_tela = threshold_root.winfo_screenheight()

            # Calcula as coordenadas X e Y para centralizar a janela na tela do usuário
            pos_x = int((largura_tela - largura) / 2)
            pos_y = int((altura_tela - altura) / 2)

            # Define a geometria da janela
            threshold_root.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')

            # Cria a tela de seleção do valor do filtro
            label = Label(threshold_root, text='Selecione o valor do filtro:')
            label.pack()

            value_frame = Frame(threshold_root)
            value_frame.pack()

            # Define o valor do filtro pelo seletor ou nos botões e guarda o valor na variável, para ser usado mais tarde na finalização
            threshold_value = Scale(
                value_frame, from_=80, to=250, orient='horizontal')
            threshold_value.pack(side='left')

            # Botão de aumentar o valor do filtro
            def increase_value():
                current_value = threshold_value.get()
                threshold_value.set(current_value + 1)

            # Botão para diminuir o valor do filtro
            def decrease_value():
                current_value = threshold_value.get()
                threshold_value.set(current_value - 1)

            # Parâmetros do botão de diminuir o valor
            button_decrease = Button(
                value_frame, text='-', command=decrease_value)
            button_decrease.pack(side='left')

            # Parâmetros do botão para aumentar o valor
            button_increase = Button(
                value_frame, text='+', command=increase_value)
            button_increase.pack(side='left')

            # Cria uma imagem para o preview do resultado
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)

            # Cria um widget de canvas para exibir a imagem
            canvas = FigureCanvasTkAgg(fig, master=threshold_root)
            canvas.get_tk_widget().pack()

            # Função para atualizar o preview de acordo com o valor de filtro selecionado
            def update_preview(value):
                # Aplica o filtro limiar no preview de acordo com o valor do slider
                ret, limiar = cv2.threshold(
                    img, int(value), 255, cv2.THRESH_BINARY)

                img_new1 = limiar.astype(np.uint8)

                # Atualiza o preview da imagem no widget
                ax.imshow(img_new1, cmap='gray')
                canvas.draw()

            threshold_value.configure(command=update_preview)

            def apply_filters():
                # Puxa o valor do limiar selecionado
                value = threshold_value.get()

                # Aplica o limiar e o filtro de blur na imagem final
                ret, limiar = cv2.threshold(
                    img, int(value), 255, cv2.THRESH_BINARY)
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

                # Salva a imagem, fazendo um count pra não substituir, caso trate e salve mais de uma na mesma pasta
                count = 1
                while True:
                    file_name = f'assinaturaTratada_{count}.bmp'
                    file_path = os.path.join(directory, file_name)
                    if not os.path.exists(file_path):
                        break
                    count += 1

                # Salva a imagem original
                cv2.imwrite(file_path, img_new1)

                # Verifica o tamanho do arquivo, que deve ser menor ou igual a 1Mb
                file_size = os.path.getsize(file_path)
                max_file_size = 1024 * 1024  # 1MB

                # Redimensiona a imagem enquanto o tamanho for maior que 1MB
                while file_size > max_file_size:
                    # Redimensiona a imagem pela metade
                    img_new1 = cv2.resize(img_new1, None, fx=0.5, fy=0.5)

                    # Salva a imagem com o mesmo nome, substituindo o arquivo anterior
                    cv2.imwrite(file_path, img_new1)

                    # Atualiza o tamanho do arquivo
                    file_size = os.path.getsize(file_path)

                # Fecha a janela de controle de valor
                threshold_root.quit()

                # Mostra uma caixa de dialogo pra confirmar a saída do programa
                result = messagebox.askquestion(
                    'Finalizar', 'Deseja fechar o programa?')

                if result == 'yes':
                    root.quit()
                else:
                    process_image()

            # Botão para aplicar os filtros e finalizar a aplicação
            apply_button = Button(
                threshold_root, text='Aplicar', command=apply_filters)
            apply_button.pack()

            # Encerra o programa ao clicar no X da tela de filtro
            threshold_root.protocol("WM_DELETE_WINDOW", threshold_root.quit)

            # Inicia o loop principal da aplicação, se o usuário quiser tratar mais uma imagem
            threshold_root.mainloop()

        # Aviso quando o usuário fecha a janela de seleção da pasta destino
        else:
            messagebox.showwarning(
                'Aviso', 'Nenhum diretório de destino selecionado.')
            root.quit()

    # Aviso quando o usuário fecha a janela de seleção da imagem a ser tratada
    else:
        messagebox.showwarning('Aviso', 'Nenhum arquivo selecionado.')
        root.quit()


# Chama a função para processar a imagem
process_image()
