from cx_Freeze import setup, Executable

# Arquivo principal do seu script
target = Executable(
    script="imagem.py",
    base="Win32GUI",  # Use "Win32GUI" para aplicativos sem janela de console
    # Caminho para o ícone do executável (opcional)

)

# Configurações do cx_Freeze
options = {
    'build_exe': {
        'includes': ['cv2', 'tkinter'],
        'packages': ['numpy'],
        # Outros arquivos que você deseja incluir

    }
}

# Cria o executável
setup(
    name="Trata_Imagem",
    version="1.0",
    description="Descrição do seu aplicativo",
    executables=[target],
    options=options
)
