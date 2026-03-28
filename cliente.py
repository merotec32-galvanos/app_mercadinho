import flet as ft
import urllib.parse
from database import carregar_dados

def cliente(page: ft.Page, lista_encarte):
    # Função para o cliente pedir produtos não listados
    def fazer_pedido_indisponivel(e):
        msg = "Olá! Não encontrei o produto que procurava no encarte. Vocês têm disponível?"
        msg_encoded = urllib.parse.quote(msg)
        page.launch_url(f"https://wa.me/+5521977787707?text={msg_encoded}")

    def renderizar_encarte_cliente():
        lista_encarte.controls.clear()
        db_produtos = carregar_dados()
        
        for p in db_produtos:
            img_src = f"/{p['imagem']}" if p.get("imagem") else None
            
            card = ft.Container(
                content=ft.Row([
                    ft.Image(src=img_src, width=100, height=100, fit=ft.ImageFit.COVER, border_radius=8) if img_src else ft.Icon(ft.Icons.SHOPPING_BASKET_ROUNDED, size=40, color=ft.Colors.GREEN_600),
                    ft.Column([
                        ft.Text(p["nome"], size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(p["desc"], size=18),
                        ft.Text(f"R$ {p['preco']}", size=18, color=ft.Colors.GREEN_800, weight=ft.FontWeight.BOLD),
                    ], expand=True),
                    # Botão de Chat (Sempre criado, mas controlado pelo servidor)
                    ft.IconButton(
                        ft.Icons.CHAT_OUTLINED, 
                        icon_color=ft.Colors.GREEN_600,
                        data="btn_chat", # Identificador para o servidor
                        on_click=lambda e, p=p: page.run_thread(
                            lambda: page.launch_url(f"https://wa.me/+5521977787707?text={urllib.parse.quote('Olá, poderia entregar ' + p['nome'] + ' R$'+p['preco']+' ?')}"))
                    )
                ]),
                padding=10, border=ft.border.all(1, ft.Colors.GREY_200), border_radius=10
            )
            lista_encarte.controls.append(card)
        
        # Botão final (Controlado pelo servidor através do ID 'btn_indisponivel')
        lista_encarte.controls.append(
            ft.Container(
                key="btn_indisponivel",
                content=ft.ElevatedButton(
                    "Não encontrou o que procurava? Clique aqui",
                    icon=ft.Icons.SEND_ROUNDED,
                    on_click=fazer_pedido_indisponivel,
                    bgcolor=ft.Colors.GREEN_800,
                    color=ft.Colors.WHITE
                ),
                padding=20,
                alignment=ft.alignment.center
            )
        )
        page.update()

    return renderizar_encarte_cliente
