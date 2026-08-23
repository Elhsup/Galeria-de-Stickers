import os
import json
import subprocess
from datetime import datetime

# =======================================================
# RADAR DE DIRECTORIO RAIZ
# =======================================================
def encontrar_raiz_repo():
    ruta_actual = os.getcwd()
    while ruta_actual != os.path.dirname(ruta_actual):
        if os.path.isdir(os.path.join(ruta_actual, ".git")):
            return ruta_actual
        ruta_actual = os.path.dirname(ruta_actual)
    return os.getcwd()

REPO_ROOT = encontrar_raiz_repo()
MANIFEST_PATH = os.path.join(REPO_ROOT, "manifest.json")
CATALOGO_DIR = os.path.join(REPO_ROOT, "catalogo")

def load_manifest() -> dict:
    if not os.path.exists(MANIFEST_PATH):
        print(f"[AVISO] No se encontro la base de datos en {MANIFEST_PATH}.")
        return {"items": []}
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"items": []}

def build_category_blocks(items, category_path):
    category_items = [item for item in items if item.get("categoria") == category_path]
    if not category_items:
        return "_Aun no hay emojis registrados en esta categoria. ¡Sube el primero!_\n"

    md = ""
    for item in category_items:
        url = item.get("url_raw", "")
        slug = item.get("id", "")
        titulo_display = item.get("titulo", slug.replace("-", " ").capitalize())
        alt = item.get("alt", slug)
        tags_list = item.get("tags", [])
        tags_str = ", ".join([f"`{t}`" for t in tags_list]) if tags_list else "_Ninguno_"
        
        html_30 = f'<img src="{url}" width="30" alt="{alt}">'
        html_50 = f'<img src="{url}" width="50" alt="{alt}">'
        html_100 = f'<img src="{url}" width="100" alt="{alt}">'

        md += f"### {titulo_display} (`{slug}`)\n\n"
        md += f"**Etiquetas:** {tags_str}\n\n"
        md += f"| Vista Previa |\n"
        md += f"| :---: |\n"
        md += f"| <img src=\"{url}\" width=\"50\" alt=\"{alt}\"> |\n\n"
        
        md += f"**Tamaño 30px (Mini):**\n\n"
        md += f"```html\n"
        md += f"{html_30}\n"
        md += f"```\n\n"
        md += f"**Tamaño 50px (Medio):**\n\n"
        md += f"```html\n"
        md += f"{html_50}\n"
        md += f"```\n\n"
        md += f"**Tamaño 100px (Grande):**\n\n"
        md += f"```html\n"
        md += f"{html_100}\n"
        md += f"```\n\n"
        md += "---\n\n"

    return md

def subir_a_github():
    print("\n--- ¿Quieres subir los cambios del catalogo a GitHub ahora mismo? ---")
    respuesta = input("Escribe 's' para Si, o presiona Enter para omitir: ").strip().lower()
    if respuesta == 's':
        print("[INFO] Ejecutando Git Add, Commit y Push...")
        try:
            subprocess.run(["git", "add", "."], cwd=REPO_ROOT, check=True)
            subprocess.run(["git", "commit", "-m", "Actualizacion dinamica y limpia del catalogo de stickers"], cwd=REPO_ROOT, check=True)
            subprocess.run(["git", "push"], cwd=REPO_ROOT, check=True)
            print("[EXITO] ¡Los cambios se han subido a GitHub con exito!")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Hubo un problema al intentar subir a GitHub: {e}")
    else:
        print("[GUARDADO LOCAL] Subida a Git omitida.")

def main():
    print("========================================================")
    print("   === ACTUALIZADOR DINAMICO DE CATALOGO ===")
    print("========================================================\n")
    print(f"[INFO] Raiz detectada en: {REPO_ROOT}\n")

    manifest = load_manifest()
    items = manifest.get("items", [])
    total_emojis = len(items)

    # Descubrir dinamicamente todas las categorias unicas que existan en el JSON
    categorias_detectadas = sorted(list(set(item.get("categoria") for item in items if item.get("categoria"))))
    
    # Si por alguna razon el manifest esta vacio, definimos las por defecto
    if not categorias_detectadas:
        categorias_detectadas = [
            "estaticos/memes",
            "estaticos/programacion",
            "estaticos/reacciones",
            "animados/memes-gif",
            "animados/reacciones-gif"
        ]

    conteos = {cat: 0 for cat in categorias_detectadas}
    for item in items:
        cat = item.get("categoria")
        if cat in conteos:
            conteos[cat] += 1

    # Generar de forma dinamica los archivos usando os.path.join para evitar cruces de barras
    for cat_path in categorias_detectadas:
        partes_cat = cat_path.split("/")
        file_path = os.path.join(CATALOGO_DIR, *partes_cat) + ".md"
        
        # BLINDAJE: Crea la carpeta contenedora exacta antes de escribir
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        cant_items = conteos[cat_path]
        titulo_seccion = cat_path.replace("/", " - ").title()
        
        md_content = f"# {titulo_seccion}\n\n"
        md_content += f"Seccion oficial para elementos de tipo: `{cat_path}`.\n\n"
        md_content += f"Actualmente hay **{cant_items}** elemento{'s' if cant_items != 1 else ''} en esta seccion.\n\n"
        md_content += "---\n\n"
        md_content += build_category_blocks(items, cat_path)
        md_content += "\n"
        md_content += "[ Volver al Indice del Catalogo](../README.md) | [ Volver al Inicio del Repositorio](../../README.md)\n"

        print(f"[DEBUG] Generando archivo dinamico en -> {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)

    # Generar el README principal del catalogo de forma dinamica
    readme_path = os.path.join(CATALOGO_DIR, "README.md")
    os.makedirs(os.path.dirname(readme_path), exist_ok=True)

    links_markdown = ""
    for cat_path in categorias_detectadas:
        nombre_amigable = cat_path.replace("/", " / ").title()
        links_markdown += f"*   **[{nombre_amigable}]({cat_path}.md)** ({conteos[cat_path]} elementos)\n"

    index_content = f"""# Catalogo Oficial de Emojis y Stickers

¡Bienvenido al catalogo oficial del proyecto! Aqui tienes la vitrina completa organizada de forma dinamica. 
Haz clic en el boton de copiar del bloque HTML que prefieras y pegalo en tu perfil.

---

## Categorias y Secciones

{links_markdown}

---

## Resumen del Proyecto
*   **Total de Elementos Registrados:** {total_emojis}
*   **Ultima actualizacion:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

[ Volver al Inicio del Repositorio](../README.md)
"""

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(index_content)

    print("[OK] ¡Catalogo dinamico generado y organizado a la perfección!\n")
    subir_a_github()

if __name__ == "__main__":
    main()