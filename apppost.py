import flet as ft

def main(page: ft.Page):
    # O endereço do seu PC no Rio de Janeiro
    URL_SERVIDOR = "http://192.168.1.10:8550/admin"
    
    # Configurações da página para parecer um app nativo
    page.title = "Painel Mercadinho"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Cria um WebView que ocupa a tela toda
    webview = ft.WebView(
        URL_SERVIDOR,
        expand=True,
        on_page_started=lambda _: print("Carregando Painel..."),
    )
    
    page.add(webview)

if __name__ == "__main__":
    ft.app(target=main)