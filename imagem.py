import cv2
from tkinter import Tk, filedialog, Label, Button, Scale, messagebox, Frame
import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from screeninfo import get_monitors
from concurrent.futures import ThreadPoolExecutor

root = Tk()


def get_main_monitor():
    # Obtém a posição do monitor principal
    for monitor in get_monitors():
        if monitor.is_primary:
            return monitor

    # Se não houver um monitor principal, retorna o primeiro monitor da lista
    if len(get_monitors()) > 0:
        return get_monitors()[0]

    # Se não houver nenhum monitor, retorna None
    return None


def process_image():
    # Abre uma janela para selecionar o arquivo de imagem

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Exibir um alerta para recortar a imagem antes de usar o programa
    messagebox.showinfo('Alerta', 'Recorte a imagem antes de usar o programa')
    root.title('Selecionar arquivo de imagem')
    root.withdraw()
    file_path = filedialog.askopenfilename(
        filetypes=[('Image Files', ('*.jpeg', '*.jpg', '*.png', '*.bmp'))])

    if file_path:
        # Carrega a imagem
        image1 = cv2.imread(file_path)

        # Converte para escala de cinza
        img = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

        # Abre uma janela para selecionar o diretório de destino
        root.title('Selecionar pasta de destino')
        root.withdraw()
        directory = filedialog.askdirectory()

        if directory:
            # Cria um controle deslizante para selecionar o valor do limiar
            threshold_root = Tk()
            messagebox.showinfo(
                'Alerta', 'Selecione agora o valor do filtro, geralmente fica entre 100-180, depende se o fundo da imagem está muito escuro. Se tiver muito escuro, selecione um valor baixo')
            threshold_root.title('Filtro')
            largura = 600
            altura = 600
            # Puxa a largura e altura da tela
            largura_tela = threshold_root.winfo_screenwidth()
            altura_tela = threshold_root.winfo_screenheight()

            # Calcular as coordenadas X e Y para centralizar a janela na tela do usuário
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
                value_frame, from_=80, to=200, orient='horizontal')
            threshold_value.pack(side='left')

            # Botão de aumentar o valor
            def increase_value():
                current_value = threshold_value.get()
                threshold_value.set(current_value + 1)

            # Botão para diminuir o valor
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
                # Limiar da imagem e aplicação do filtro Gaussiano
                ret, limiar = cv2.threshold(
                    img, int(value), 255, cv2.THRESH_BINARY)
                blur = cv2.GaussianBlur(limiar, (5, 5), 0)

                # Aplicação do filtro de mediana
                m, n = blur.shape
                img_new1 = np.zeros([m, n])
                border_size = 1  # Tamanho da borda

                for i in range(border_size, m - border_size):
                    for j in range(border_size, n - border_size):
                        temp = [blur[i - 1, j - 1],
                                blur[i - 1, j],
                                blur[i - 1, j + 1],
                                blur[i, j - 1],
                                blur[i, j],
                                blur[i, j + 1],
                                blur[i + 1, j - 1],
                                blur[i + 1, j],
                                blur[i + 1, j + 1]]
                        temp = sorted(temp)
                        img_new1[i, j] = temp[4]

                img_new1 = img_new1.astype(np.uint8)

                # Atualiza o preview da imagem no widget
                ax.imshow(img_new1, cmap='gray')
                canvas.draw()

            threshold_value.configure(command=update_preview)

            def apply_filters():
                # Obtém o valor do limiar selecionado
                value = threshold_value.get()

                # Limiar da imagem e aplicação do filtro Gaussiano
                ret, limiar = cv2.threshold(
                    img, int(value), 255, cv2.THRESH_BINARY)
                blur = cv2.GaussianBlur(limiar, (5, 5), 0)

                # Aplicação do filtro de mediana
                img_new1 = cv2.medianBlur(blur, 3)

                # Encontra os contornos na imagem tratada
                contours, _ = cv2.findContours(
                    img_new1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Encontra o maior contorno
                max_contour = max(contours, key=cv2.contourArea)

                # Calcula o retângulo delimitador do contorno
                x, y, w, h = cv2.boundingRect(max_contour)

                # Recorta a imagem tratada usando as coordenadas do retângulo delimitador
                img_new1 = img_new1[y:y + h, x:x + w]

                # Salva a imagem no diretório de destino
                count = 1
                while True:
                    file_name = f'assinaturaTratada_{count}.bmp'
                    file_path = os.path.join(directory, file_name)
                    if not os.path.exists(file_path):
                        break
                    count += 1
                cv2.imwrite(file_path, img_new1)

                # Fecha a janela de controle de valor
                threshold_root.quit()

                # Exibe uma caixa de diálogo para confirmar o fechamento da aplicação
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

            # Inicia o loop principal da aplicação
            threshold_root.mainloop()
        else:
            messagebox.showwarning(
                'Aviso', 'Nenhum diretório de destino selecionado.')
    else:
        messagebox.showwarning('Aviso', 'Nenhum arquivo selecionado.')


# Chama a função para processar a imagem
process_image()
