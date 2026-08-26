#!/usr/bin/env python3
"""
emoji_cli.py (Versión Mejorada y Continua)
Genera la etiqueta HTML <img src="..." width="..."> desde URLs o imágenes locales.
No se cierra solo y permite procesar múltiples emojis de forma continua.
"""

import os
from pathlib import Path
import re

ASSETS_DIR = Path("assets/emojis")

def list_local_images():
    if not ASSETS_DIR.exists():
        return []
    exts = (".png", ".jpg", ".jpeg", ".webp", ".gif")
    files = [p for p in ASSETS_DIR.iterdir() if p.suffix.lower() in exts and p.is_file()]
    return sorted(files)

def ask_choice(prompt, choices):
    while True:
        r = input(prompt).strip()
        if r in choices:
            return r
        print("Opción no válida. Elige:", ", ".join(choices))

def es_link_valido(texto):
    """Verifica de forma sencilla si parece un enlace web y una imagen."""
    texto = texto.strip()
    # Comprueba que empiece por http y termine en una extensión de imagen común o parezca un link
    patron = r'^https?://.+'
    if re.match(patron, texto):
        return True
    return False

def main():
    print("========================================================")
    print("       EMOJI HTML GENERATOR - MODO CONTINUO V2.0       ")
    print("========================================================")
    print("Escribe 'salir' cuando quieras cerrar la aplicación.\n")

    # Bucle infinito para que la app no se cierre sola nunca
    while True:
        print("-" * 50)
        local = list_local_images()
        src = ""

        if local:
            print("Imágenes encontradas en assets/emojis/:")
            for i, p in enumerate(local, start=1):
                print(f" [{i}] {p.name}")
            print(" [0] Usar URL externa")
            print(" [s] Salir de la app")
            
            eleccion = input("Elige una opción: ").strip().lower()
            
            if eleccion == 's' or eleccion == 'salir':
                print("\n[INFO] ¡Cerrando la aplicación. Hasta luego!")
                break
            elif eleccion.isdigit() and 1 <= int(eleccion) <= len(local):
                src = f"https://raw.githubusercontent.com/Elhsup/Ideas_de_programacion/main/{local[int(eleccion)-1].as_posix()}"
                print(f"[INFO] Usando imagen local -> {src}")
            elif eleccion == '0':
                while True:
                    url_input = input("Pega la URL completa de la imagen (o escribe 'volver'): ").strip()
                    if url_input.lower() == 'volver':
                        break
                    if es_link_valido(url_input):
                        src = url_input
                        break
                    print("[ADVERTENCIA] Enlace no válido. Debe empezar con http:// o https://")
                if src == "":
                    continue # Regresa al menú principal si decidió volver
            else:
                print("[ADVERTENCIA] Opción no válida. Inténtalo de nuevo.")
                continue
        else:
            url_input = input("Pega la URL completa de la imagen (o escribe 'salir'): ").strip()
            if url_input.lower() == 'salir':
                print("\n[INFO] ¡Cerrando la aplicación. Hasta luego!")
                break
            if es_link_valido(url_input):
                src = url_input
            else:
                print("[ADVERTENCIA] Eso no parece un enlace válido. Inténtalo de nuevo.")
                continue

        # Pedir texto alternativo (alt)
        alt = input("Texto alternativo (alt) [ej: gato feliz]: ").strip() or "emoji"
        
        # Elegir tamaño
        print("\nElige tamaño:")
        print(" 1) Mini (25px)")
        print(" 2) Mediano (50px)")
        print(" 3) Grande (100px)")
        size_choice = ask_choice("Tu opción (1/2/3): ", ["1","2","3"])
        size_map = {"1":"25", "2":"50", "3":"100"}
        width = size_map[size_choice]

        # Generar código HTML
        html = f'<img src="{src}" width="{width}" alt="{alt}">'
        print("\n=== Código HTML Generado ===")
        print(html)
        print("===========================")
        print("¡Cópialo y pégalo en tu README.md! Listo para el siguiente.\n")

if __name__ == "__main__":
    main()