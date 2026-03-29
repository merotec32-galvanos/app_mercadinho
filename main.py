import flet as ft
import flet_fastapi
from fastapi import FastAPI
import os
import uvicorn
import base64
from database import carregar_dados, salvar_novo_produto, deletar_produto_db
from cliente import cliente

app = FastAPI()
os.environ["FLET_SECRET_KEY"] = "mercadinho_familia_2026"
base_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(base_dir, "assets")
# 1. A função principal agora é assíncrona
async def main(page: ft.Page):
    page.title = "Mercadinho Digital"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ALWAYS
    
    txt_nome = ft.TextField(label="Nome do Produto")
    txt_desc = ft.TextField(label="Descrição")
    txt_preco = ft.TextField(label="Preço")
    txt_imagem_nome = ft.Text("Nenhuma foto selecionada", size=12, italic=True)
    img_previa = ft.Image(src="", width=120, height=120, fit=ft.ImageFit.COVER, border_radius=8, visible=False)
    
    lista_encarte = ft.Column(spacing=10)
    renderizar_cliente = cliente(page, lista_encarte)

    # Função de exclusão assíncrona
    async def excluir_produto(e, produto_id):
        deletar_produto_db(produto_id)
        page.pubsub.send_all("update")
        lista_encarte.controls.clear()
        await renderizar_com_controles()
        await page.update_async()

    # Função de renderização assíncrona para evitar NotImplementedError
    async def renderizar_com_controles():
        await renderizar_cliente() # Gera a lista base
        
        db_atual = carregar_dados()
        is_admin = page.route == "/admin" or page.route == "/"

        for idx, control in enumerate(lista_encarte.controls):
            if idx < len(db_atual):
                produto_ref = db_atual[idx]
                row_content = control.content
                
                if is_admin:
                    if len(row_content.controls) > 2:
                        row_content.controls.pop()
                    
                    row_content.controls.append(
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE, 
                            icon_color=ft.colors.RED_400, 
                            # Passamos produto_ref['id'] em vez de nome e preço
                            on_click=lambda e, p_id=produto_ref['id']: page.run_task(excluir_produto, e, p_id)
                        )
                    )
        
        if is_admin:
            if len(lista_encarte.controls) > len(db_atual):
                lista_encarte.controls.pop()
                
        await page.update_async() # <--- Uso obrigatório no FastAPI

    async def resultado_arquivo(e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            txt_imagem_nome.value = file.name
            img_previa.src = f"/{file.name}"
            img_previa.visible = True
            await page.update_async()

    picker = ft.FilePicker(on_result=resultado_arquivo)
    page.overlay.append(picker)
    await page.update_async()

    async def postar_clique(e):
        if txt_nome.value:
            # 1. Pega os valores diretamente dos campos de texto
            nome = txt_nome.value.upper()
            desc = txt_desc.value
            preco = txt_preco.value
            imagem = txt_imagem_nome.value if txt_imagem_nome.value != "Nenhuma foto selecionada" else ""
            
            # 2. Chama a função do database.py passando os 4 argumentos
            salvar_novo_produto(nome, desc, preco, imagem)
            
            # 3. Limpa a interface
            txt_nome.value = ""
            txt_desc.value = ""
            txt_preco.value = ""
            txt_imagem_nome.value = "Nenhuma foto selecionada"
            img_previa.visible = False
            
            # 4. Notifica todos e renderiza a nova lista
            page.pubsub.send_all("update")
            await renderizar_com_controles() 
            await page.update_async()

    page.pubsub.subscribe(lambda _: page.run_task(renderizar_com_controles))

    async def rota_mudou(e):
        page = e.page
        page.controls.clear() # Limpa a tela

        # 1. Em vez de page.add, use page.controls.append
        page.controls.append(ft.Container(
            ft.Text("MERCADINHO DA FAMÍLIA", size=24, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=ft.colors.GREEN_800, padding=20, alignment=ft.Alignment(0, 0)
        ))

        if page.route == "/admin" or page.route == "/":
            page.controls.append(ft.ExpansionTile(
                title=ft.Text("PAINEL DE CADASTRO", weight=ft.FontWeight.BOLD),
                initially_expanded=True,
                controls=[ft.Container(ft.Column([
                    txt_nome, txt_desc, txt_preco,
                    ft.Row([
                        ft.ElevatedButton(
                        "FOTO", 
                        icon=ft.icons.CAMERA_ALT, 
                        on_click=lambda _: page.run_task(picker.pick_files_async) # <--- Uso correto do run_task
                        ),
                        img_previa
                    ], alignment=ft.MainAxisAlignment.START),
                    txt_imagem_nome,
                    ft.ElevatedButton("POSTAR AGORA", bgcolor=ft.colors.GREEN_800, color=ft.colors.WHITE, on_click=postar_clique)
                ]), padding=15)]
            ))
        
        page.controls.append(ft.Container(ft.Text("OFERTAS DO DIA", size=18, weight=ft.FontWeight.BOLD), padding=10))
        page.controls.append(lista_encarte)

        # 2. Agora sim, atualiza a tela de forma assíncrona
        await page.update_async() 
        await renderizar_com_controles()

    page.on_route_change = rota_mudou
    await page.go_async(page.route) # <--- Inicialização assíncrona

# 2. Montagem correta para o FastAPI
app.mount("/", flet_fastapi.app(main, assets_dir=assets_path))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) # Use 0.0.0.0 para o Render
