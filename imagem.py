import cv2
from tkinter import Tk, filedialog, Label, Button, Scale, messagebox
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def process_image():
    # Abre uma janela para selecionar o arquivo de imagem
    root = Tk()
    # Exibir um alerta
    messagebox.showinfo('Alerta', 'Recorte a imagem antes de usar o programa')
    root.withdraw()
    file_path = filedialog.askopenfilename(
        filetypes=[('Image Files', ('*.jpeg', '*.jpg', '*.png', '*.bmp'))])

    if file_path:
        # Carrega a imagem
        image1 = cv2.imread(file_path)

        # Converte para escala de cinza
        img = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

        # Abre uma janela para selecionar o diretório de destino
        root = Tk()
        root.withdraw()
        directory = filedialog.askdirectory()

        if directory:
            # Cria um controle deslizante para selecionar o valor do limiar
            root = Tk()
            messagebox.showinfo(
                'Alerta', 'Selecione agora o valor do limiar, geralmente fica entre 120-180, depende se o fundo da imagem está muito escuro. Se tiver muito escuro, selecione um valor baixo')
            root.title('Limiar')
            largura = 600
            altura = 400
            # Obter a largura e altura da tela
            largura_tela = root.winfo_screenwidth()
            altura_tela = root.winfo_screenheight()

            # Calcular as coordenadas X e Y para centralizar a janela
            pos_x = int((largura_tela - largura) / 2)
            pos_y = int((altura_tela - altura) / 2)

            # Definir a geometria da janela
            root.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')

            label = Label(root, text='Selecione o valor do limiar:')
            label.pack()

            threshold_value = Scale(
                root, from_=80, to=200, orient='horizontal')
            threshold_value.pack()

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
                for i in range(1, m-1):
                    for j in range(1, n-1):
                        temp = [blur[i-1, j-1],
                                blur[i-1, j],
                                blur[i-1, j + 1],
                                blur[i, j-1],
                                blur[i, j],
                                blur[i, j + 1],
                                blur[i + 1, j-1],
                                blur[i + 1, j],
                                blur[i + 1, j + 1]]
                        temp = sorted(temp)
                        img_new1[i, j] = temp[4]
                img_new1 = img_new1.astype(np.uint8)

                # Atualizar o preview da imagem
                ax.imshow(img_new1, cmap='gray')
                canvas.draw()

            def apply_filters():
                # Obter o valor do limiar selecionado
                valor_limiar = threshold_value.get()

                # Limiar da imagem e aplicação do filtro Gaussiano
                ret, limiar = cv2.threshold(
                    img, valor_limiar, 255, cv2.THRESH_BINARY)
                blur = cv2.GaussianBlur(limiar, (5, 5), 0)

                # Aplicação do filtro de mediana
                m, n = blur.shape
                img_new1 = np.zeros([m, n])
                for i in range(1, m-1):
                    for j in range(1, n-1):
                        temp = [blur[i-1, j-1],
                                blur[i-1, j],
                                blur[i-1, j + 1],
                                blur[i, j-1],
                                blur[i, j],
                                blur[i, j + 1],
                                blur[i + 1, j-1],
                                blur[i + 1, j],
                                blur[i + 1, j + 1]]
                        temp = sorted(temp)
                        img_new1[i, j] = temp[4]
                img_new1 = img_new1.astype(np.uint8)

                # Salva a imagem no diretório de destino
                cv2.imwrite(directory + '/assinaturaTratada.bmp', img_new1)

                # Fecha a janela de controle deslizante
                root.destroy()

            threshold_value.config(command=update_preview)
            button = Button(root, text='Aplicar Filtros',
                            command=apply_filters)
            button.pack()

            # Inicializar o preview com o valor inicial do seletor
            update_preview(threshold_value.get())

            root.mainloop()


process_image()
