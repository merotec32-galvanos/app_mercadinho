import flet as ft
from fastapi import FastAPI
from flet_fastapi import FletApp
import os
import uvicorn
import urllib.parse
import base64
from database import carregar_dados, salvar_dados
from cliente import cliente

os.environ["FLET_SECRET_KEY"] = "mercadinho_familia_2026"
app = FastAPI()
def main(page: ft.Page):
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

    def excluir_produto(e, produto_obj):
        db = carregar_dados()
        nova_lista = [p for p in db if not (p['nome'] == produto_obj['nome'] and p['preco'] == produto_obj['preco'])]
        salvar_dados(nova_lista)
        page.pubsub.send_all("update")

    def renderizar_com_controles():
        renderizar_cliente() # Gera a lista padrão do cliente
        
        db_atual = carregar_dados()
        is_admin = page.route == "/admin" or page.route == "/"

        # 1. Filtro dos botões individuais de cada produto
        for idx, control in enumerate(lista_encarte.controls):
            if idx < len(db_atual):
                produto_ref = db_atual[idx]
                row_content = control.content # O Row dentro do Container
                
                if is_admin:
                    # Se for ADMIN, remove o botão de CHAT do cliente
                    if len(row_content.controls) > 2:
                        row_content.controls.pop()
                    
                    # Adiciona botão de APAGAR
                    row_content.controls.append(
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE, 
                            icon_color=ft.Colors.RED_400, 
                            on_click=lambda e, p=produto_ref: excluir_produto(e, p)
                        )
                    )
        
        # 2. Filtro do botão de "Produto Indisponível" ao final da lista
        if is_admin:
            # Se for ADMIN, remove o último controle (botão de indisponível)
            if len(lista_encarte.controls) > len(db_atual):
                lista_encarte.controls.pop()
                
        page.update()

    # Lógica de upload (Mantida conforme seus arquivos atuais)
    def resultado_arquivo(e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            txt_imagem_nome.value = file.name
            try:
                conteudo_bytes = page.read_file_picker_file(file.name)
                if conteudo_bytes:
                    img_previa.src_base64 = base64.b64encode(conteudo_bytes).decode("utf-8")
                    img_previa.visible = True
            except:
                img_previa.src = f"/{file.name}"
                img_previa.visible = True
            picker.upload([ft.FilePickerUploadFile(file.name, upload_url=page.get_upload_url(file.name, 600))])
            page.update()

    picker = ft.FilePicker(on_result=resultado_arquivo)
    page.overlay.append(picker)

    def postar_clique(e):
        if txt_nome.value:
            db = carregar_dados()
            novo = {"nome": txt_nome.value.upper(), "desc": txt_desc.value, "preco": txt_preco.value, 
                    "imagem": txt_imagem_nome.value if txt_imagem_nome.value != "Nenhuma foto selecionada" else ""}
            db.insert(0, novo) # NOVO EM PRIMEIRO LUGAR
            salvar_dados(db)
            txt_nome.value = ""; txt_desc.value = ""; txt_preco.value = ""
            txt_imagem_nome.value = "Nenhuma foto selecionada"; img_previa.visible = False
            page.pubsub.send_all("update")

    page.pubsub.subscribe(lambda _: renderizar_com_controles())

    def rota_mudou(route):
        page.controls.clear()
        page.add(ft.Container(
            ft.Text("MERCADINHO DA FAMÍLIA", size=24, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.GREEN_800, padding=20, alignment=ft.Alignment(0, 0)
        ))

        if page.route == "/admin" or page.route == "/":
            page.add(ft.ExpansionTile(
                title=ft.Text("PAINEL DE CADASTRO", weight=ft.FontWeight.BOLD),
                initially_expanded=True,
                controls=[ft.Container(ft.Column([
                    txt_nome, txt_desc, txt_preco,
                    ft.Row([
                        ft.ElevatedButton("FOTO", icon=ft.Icons.CAMERA_ALT, on_click=lambda _: page.run_thread(picker.pick_files)),
                        img_previa
                    ], alignment=ft.MainAxisAlignment.START),
                    txt_imagem_nome,
                    ft.ElevatedButton("POSTAR AGORA", bgcolor=ft.Colors.GREEN_800, color=ft.Colors.WHITE, on_click=postar_clique)
                ]), padding=15)]
            ))
        
        page.add(ft.Container(ft.Text("OFERTAS DO DIA", size=18, weight=ft.FontWeight.BOLD), padding=10))
        page.add(lista_encarte)
        renderizar_com_controles()

    page.on_route_change = rota_mudou
    page.go(page.route)

app.mount("/", FletApp(main))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
