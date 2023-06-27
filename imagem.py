import cv2
from tkinter import Tk, filedialog, Label, Button, Scale, messagebox, Frame
import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def process_image():
    # Abre uma janela para selecionar o arquivo de imagem
    root = Tk()
    # Exibir um alerta
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
            root = Tk()
            messagebox.showinfo(
                'Alerta', 'Selecione agora o valor do filtro, geralmente fica entre 100-180, depende se o fundo da imagem está muito escuro. Se tiver muito escuro, selecione um valor baixo')
            root.title('Filtro')
            largura = 600
            altura = 600
            # Obter a largura e altura da tela
            largura_tela = root.winfo_screenwidth()
            altura_tela = root.winfo_screenheight()

            # Calcular as coordenadas X e Y para centralizar a janela
            pos_x = int((largura_tela - largura) / 2)
            pos_y = int((altura_tela - altura) / 2)

            # Definir a geometria da janela
            root.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')

            label = Label(root, text='Selecione o valor do filtro:')
            label.pack()

            value_frame = Frame(root)
            value_frame.pack()

            threshold_value = Scale(
                value_frame, from_=80, to=200, orient='horizontal')
            threshold_value.pack(side='left')

            def increase_value():
                current_value = threshold_value.get()
                threshold_value.set(current_value + 1)

            def decrease_value():
                current_value = threshold_value.get()
                threshold_value.set(current_value - 1)

            button_decrease = Button(
                value_frame, text='-', command=decrease_value)
            button_decrease.pack(side='left')

            button_increase = Button(
                value_frame, text='+', command=increase_value)
            button_increase.pack(side='left')

            # Criar uma figura para o preview da imagem
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)

            # Criar um widget de canvas para exibir a figura
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas.get_tk_widget().pack()

            def update_preview(value):
                # Limiar da imagem e aplicação do filtro Gaussiano
                ret, limiar = cv2.threshold(
                    img, int(value), 255, cv2.THRESH_BINARY)
                blur = cv2.GaussianBlur(limiar, (5, 5), 0)

                # Aplicação do filtro de mediana
                m, n = blur.shape
                img_new1 = np.zeros([m, n])
                for i in range(1, m - 1):
                    for j in range(1, n - 1):
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

                # Atualizar o preview da imagem
                ax.imshow(img_new1, cmap='gray')
                canvas.draw()

            threshold_value.configure(command=update_preview)

            def apply_filters():
                # Obter o valor do limiar selecionado
                value = threshold_value.get()

                # Limiar da imagem e aplicação do filtro Gaussiano
                ret, limiar = cv2.threshold(
                    img, int(value), 255, cv2.THRESH_BINARY)
                blur = cv2.GaussianBlur(limiar, (5, 5), 0)

                # Aplicação do filtro de mediana
                m, n = blur.shape
                img_new1 = np.zeros([m, n])
                for i in range(1, m - 1):
                    for j in range(1, n - 1):
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

                # Salva a imagem no diretório de destino
                count = 1
                while True:
                    file_name = f'assinaturaTratada_{count}.bmp'
                    file_path = os.path.join(directory, file_name)
                    if not os.path.exists(file_path):
                        break
                    count += 1
                cv2.imwrite(file_path, img_new1)

                # Fechar a janela de controle de valor
                root.destroy()

                # Exibir o messagebox de confirmação
                result = messagebox.askquestion(
                    'Fechar Aplicação', 'Deseja fechar a aplicação?')
                if result == 'yes':
                    root.quit()
                    root.destroy()
                else:

                    process_image()
                    root.mainloop()

            button_apply_filters = Button(
                root, text='Confirmar', command=apply_filters)
            button_apply_filters.pack()

            # Inicializar o preview
            update_preview(threshold_value.get())

            root.mainloop()


process_image()
