import flet as ft
import urllib.parse
from database import carregar_dados

def cliente(page: ft.Page, lista_encarte):
    # Função para o cliente pedir produtos não listados (agora assíncrona)
    async def fazer_pedido_indisponivel(e):
        msg = "Olá! Não encontrei o produto que procurava no encarte. Vocês têm disponível?"
        msg_encoded = urllib.parse.quote(msg)
        await page.launch_url_async(f"https://wa.me/+5521977787707?text={msg_encoded}")

    # Transformada em ASSÍNCRONA para funcionar no FastAPI/Render
    async def renderizar_encarte_cliente():
        lista_encarte.controls.clear()
        db_produtos = carregar_dados()
        
        for p in db_produtos:
            img_nome = p.get("imagem", "").strip("/")
            img_src = img_nome if img_nome else None
            
            msg=f"Olá, poderia entregar {p['nome']} R${p['preco']} ?"
            
            card = ft.Container(
                content=ft.Row([
                    ft.Image(
                            # Usa src_base64 para ler o texto longo que vem do banco de dados
                            src=p.get("imagem", ""), 
                            width=100, 
                            height=100, 
                            fit=ft.ImageFit.COVER, 
                            border_radius=8
                        ) if p.get("imagem") else ft.Icon(ft.icons.SHOPPING_BASKET_ROUNDED, size=40, color=ft.colors.GREEN_600),
                    ft.Column([
                        ft.Text(p["nome"], size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(p["desc"], size=18),
                        ft.Text(f"R$ {p['preco']}", size=18, color=ft.colors.GREEN_800, weight=ft.FontWeight.BOLD),
                    ], expand=True),
                    ft.IconButton(
                        ft.icons.CHAT_OUTLINED, 
                        icon_color=ft.colors.GREEN_600,
                        data="btn_chat",
                        # Chamada de URL agora é assíncrona
                        on_click=lambda e, p=p: page.launch_url_async(f"https://wa.me/+5521977787707?text={msg}")
                    )
                ]),
                padding=10, border=ft.border.all(1, ft.colors.GREY_200), border_radius=10
            )
            lista_encarte.controls.append(card)
        
        lista_encarte.controls.append(
            ft.Container(
                key="btn_indisponivel",
                content=ft.ElevatedButton(
                    "Não encontrou o que procurava? Clique aqui",
                    icon=ft.icons.SEND_ROUNDED,
                    on_click=fazer_pedido_indisponivel,
                    bgcolor=ft.colors.GREEN_800,
                    color=ft.colors.WHITE
                ),
                padding=20,
                alignment=ft.alignment.center
            )
        )
        # OBRIGATÓRIO: Update assíncrono para o FastAPI
        await page.update_async() 

    return renderizar_encarte_cliente
