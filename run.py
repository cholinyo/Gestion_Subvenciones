from app import create_app

app = create_app()  # Puedes pasar otra configuración si lo deseas

if __name__ == '__main__':
    app.run()
