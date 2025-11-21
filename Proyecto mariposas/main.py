# main.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import io
import folium
import webbrowser
from database import db
from CRUD_mariposas import abrir_crud_mariposas

#Mapa
def generar_mapa_y_abrir(lat, lon, nombre_cientifico):
    mapa = folium.Map(location=[lat, lon], zoom_start=8)
    folium.Marker([lat, lon], popup=nombre_cientifico).add_to(mapa)
    ruta_html = "mapa_mariposa.html"
    mapa.save(ruta_html)
    webbrowser.open(ruta_html)

#Ventana principal
def abrir_principal3(usuario):

    root = tk.Tk()
    root.title("Dashboard - Mariposas")
    root.geometry("950x650")
    root.configure(bg="#f3e5f5")

    #Encabezado
    encabezado = tk.Frame(root, bg="#7b1fa2", height=60)
    encabezado.pack(fill="x")

    tk.Label(encabezado,text=f"Usuario: {usuario.get('nombre')} (Rol: {usuario.get('rol')})",
    bg="#7b1fa2", fg="white", font=("Arial", 12, "bold")).pack(padx=10, pady=10, anchor="w")

    #Contenido
    contenido = tk.Frame(root, bg="#f3e5f5")
    contenido.pack(fill="both", expand=True, padx=10, pady=10)

    #Panel de la izquierda
    panel_izq = tk.Frame(contenido, width=300, bg="#e1bee7")
    panel_izq.pack(side="left", fill="y", padx=(0, 10))

    #Buscar
    tk.Label(panel_izq, text="Buscar especie:", bg="#e1bee7", font=("Arial", 10, "bold")).pack(pady=(5, 0))

    entry_buscar = tk.Entry(panel_izq, width=30)
    entry_buscar.pack(pady=5)

    tk.Label(panel_izq, text="Especies", bg="#e1bee7", font=("Arial", 12, "bold")).pack(pady=(10, 5))

    #Lista mariposas
    listbox = tk.Listbox(panel_izq, width=40, height=20)
    listbox.pack(padx=8, pady=6)

    especies = list(db.especies.find({}, {"nombre_cientifico": 1, "nombre_comun": 1}))
    for e in especies:
        display = f"{e.get('nombre_cientifico', '')} — {e.get('nombre_comun', '')}"
        listbox.insert(tk.END, display)

    #funcion buscar
    def buscar_especies():
        query = entry_buscar.get().strip().lower()
        listbox.delete(0, tk.END)

        filtro = {}
        if query:
            filtro = {"$or": [
                {"nombre_cientifico": {"$regex": query, "$options": "i"}},
                {"nombre_comun": {"$regex": query, "$options": "i"}}
            ]}

        resultados = list(db.especies.find(filtro, {"nombre_cientifico": 1, "nombre_comun": 1}))
        for e in resultados:
            display = f"{e.get('nombre_cientifico', '')} — {e.get('nombre_comun', '')}"
            listbox.insert(tk.END, display)

    tk.Button(panel_izq, text="Buscar", command=buscar_especies, bg="#6a1b9a", fg="white").pack(pady=(0, 10))

    #panel de la derecha
    panel_der = tk.Frame(contenido, bg="#ffffff")
    panel_der.pack(side="left", fill="both", expand=True)

    lbl_nombre = tk.Label(panel_der, text="Seleccione una especie", font=("Arial", 14, "bold"), bg="#ffffff")
    lbl_nombre.pack(anchor="nw", pady=(10, 0), padx=10)

    lbl_info = tk.Label(panel_der, text="", font=("Arial", 12),
                        bg="#ffffff", justify="left", wraplength=420)
    lbl_info.pack(anchor="nw", pady=6, padx=10)

    imagen_panel = tk.Label(panel_der, bg="#ffffff")
    imagen_panel.pack(padx=10, pady=10)

    #variables para navegar imagenes
    imagen_index = {"value": 0}
    imagenes_actuales = {"lista": []}

    #funcion cargar imagen
    def cargar_imagen_por_indice():

        if not imagenes_actuales["lista"]:
            imagen_panel.config(image="", text="Sin imagen disponible")
            return

        # proteger índice
        if imagen_index["value"] >= len(imagenes_actuales["lista"]):
            imagen_index["value"] = 0

        url = imagenes_actuales["lista"][imagen_index["value"]]

        try:
            # ruta local
            if (
                url.startswith("C:/") or url.startswith("D:/") or url.startswith("E:/")
                or url[1:3] == ":/" or "\\" in url
            ):
                local_path = url.replace("\\", "/")
                img = Image.open(local_path)

            else:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                img = Image.open(io.BytesIO(resp.content))

            img.thumbnail((350, 350))
            photo = ImageTk.PhotoImage(img)

            imagen_panel.config(image=photo, text="")
            imagen_panel.photo_ref = photo

        except Exception as e:
            imagen_panel.config(text=f"No se pudo cargar la imagen:\n{str(e)}", image="")

    # detalle especie
    def mostrar_detalle_event(evt=None):
        sel = listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        texto = listbox.get(idx)
        nombre_cientifico = texto.split(" — ")[0].strip()

        especie_doc = db.especies.find_one({"nombre_cientifico": nombre_cientifico})
        if not especie_doc:
            return

        nombre_com = especie_doc.get("nombre_comun", "-")
        familia = especie_doc.get("familia", "-")
        tipo = especie_doc.get("tipo_especie", "-")
        desc = especie_doc.get("descripcion", "-")
        car = especie_doc.get("caracteristicas_morfo", {})

        lbl_nombre.config(text=nombre_cientifico)
        lbl_info.config(
            text=f"Nombre común: {nombre_com}\n"
                 f"Familia: {familia}\n"
                 f"Tipo: {tipo}\n"
                 f"Descripción: {desc}\n"
                 f"Características: {car}"
        )

        # cargar lista de imágenes
        imagenes_actuales["lista"] = especie_doc.get("imagenes", []) or []
        imagen_index["value"] = 0

        if imagenes_actuales["lista"]:
            cargar_imagen_por_indice()
        else:
            imagen_panel.config(image="", text="Sin imagen disponible")

    listbox.bind("<<ListboxSelect>>", mostrar_detalle_event)

    # navegacion imagenes
    botones_img = tk.Frame(panel_der, bg="#ffffff")
    botones_img.pack()

    btn_atras = tk.Button(botones_img, text="◀ Atrás", bg="#7b1fa2", fg="white", command=lambda: cambiar_imagen(-1))
    btn_atras.pack(side="left", padx=10)

    btn_siguiente = tk.Button(botones_img, text="Siguiente ▶", bg="#7b1fa2", fg="white", command=lambda: cambiar_imagen(1))
    btn_siguiente.pack(side="left", padx=10)

    def cambiar_imagen(delta):
        if not imagenes_actuales["lista"]:
            return

        imagen_index["value"] += delta

        if imagen_index["value"] < 0:
            imagen_index["value"] = 0
        elif imagen_index["value"] >= len(imagenes_actuales["lista"]):
            imagen_index["value"] = len(imagenes_actuales["lista"]) - 1

        cargar_imagen_por_indice()

    # botones inferiores
    botones_frame = tk.Frame(panel_izq, bg="#e1bee7")
    botones_frame.pack(side="bottom", fill="x", pady=15)

    tk.Button(botones_frame, text="Ver mapa", bg="#c62828", fg="white").pack(
        side="left", padx=20)

    # CRUD solo para admin
    if usuario.get("rol") == "administrador":
        tk.Button(botones_frame, text="Administrar Mariposas",
        bg="#00796b", fg="white", command=abrir_crud_mariposas).pack(side="left", padx=10)

    # cargar primera especie de lista
    if especies:
        listbox.selection_set(0)
        mostrar_detalle_event()

    #salir
    def on_close():
        if messagebox.askokcancel("Salir", "¿Deseas cerrar la aplicación?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    test_user = db.usuarios.find_one() or {"nombre": "Invitado", "rol": "usuario"}
    abrir_principal3(test_user)
