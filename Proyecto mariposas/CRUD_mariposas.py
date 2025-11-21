# crud_mariposas.py
import tkinter as tk
from tkinter import messagebox, ttk
from database import db
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def abrir_crud_mariposas():
    ventana = tk.Toplevel()
    ventana.title("Administrar Mariposas (CRUD)")
    ventana.geometry("1100x650")
    ventana.configure(bg="#ede7f6")

    #Título
    tk.Label(
        ventana, text="Gestión de Mariposas", bg="#7b1fa2",
        fg="white", font=("Arial", 16, "bold")
    ).pack(fill="x")

    #Tabla
    frame_tabla = tk.Frame(ventana, bg="#ede7f6")
    frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

    columnas = ("nombre_cientifico","nombre_comun","familia","tipo_especie")
    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=10)

    for col in columnas:
        tabla.heading(col, text=col.replace("_"," ").title())
        tabla.column(col, width=200)

    tabla.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Cargar especies
    def cargar_especies():
        tabla.delete(*tabla.get_children())
        especies = list(db.especies.find({},{
            "nombre_cientifico":1,"nombre_comun":1,"familia":1,"tipo_especie":1
        }))
        for esp in especies:
            tabla.insert("", "end", values=(
                esp.get("nombre_cientifico",""),
                esp.get("nombre_comun",""),
                esp.get("familia",""),
                esp.get("tipo_especie","")
            ))
    cargar_especies()


    frame_form = tk.Frame(ventana, bg="#d1c4e9")
    frame_form.pack(fill="x", padx=10, pady=10)

    
    left = tk.Frame(frame_form, bg="#d1c4e9")
    left.grid(row=0, column=0, padx=10, pady=5)

    campos = {
        "nombre_cientifico": tk.Entry(left, width=35),
        "nombre_comun": tk.Entry(left, width=35),
        "familia": tk.Entry(left, width=35),
        "tipo_especie": tk.Entry(left, width=35),
    }

    fila = 0
    for etiqueta, campo in campos.items():
        tk.Label(left, text=etiqueta.replace("_"," ").title(),
                 bg="#d1c4e9", font=("Arial", 11)).grid(row=fila, column=0,
                 padx=5, pady=4, sticky="e")
        campo.grid(row=fila, column=1, padx=5, pady=4)
        fila += 1

    right = tk.Frame(frame_form, bg="#d1c4e9")
    right.grid(row=0, column=1, padx=10, pady=5)

    # Descripción
    tk.Label(right, text="Descripción", bg="#d1c4e9", font=("Arial",11)).pack()
    txt_descripcion = tk.Text(right, width=40, height=4)
    txt_descripcion.pack(pady=5)

    # Características JSON
    tk.Label(right, text="Características (JSON)",
             bg="#d1c4e9", font=("Arial", 11)).pack()
    txt_caracteristicas = tk.Text(right, width=40, height=4)
    txt_caracteristicas.pack(pady=5)

    # Imágenes
    tk.Label(right, text="Imágenes (URLs separadas por coma o salto de línea)",
             bg="#d1c4e9", font=("Arial", 11)).pack()
    txt_imagenes = tk.Text(right, width=40, height=4)
    txt_imagenes.pack(pady=5)

    #Funciones
    def limpiar_campos():
        for campo in campos.values():
            campo.delete(0, tk.END)
        txt_descripcion.delete("1.0", tk.END)
        txt_caracteristicas.delete("1.0", tk.END)
        txt_imagenes.delete("1.0", tk.END)

    def crear_especie():
        datos = {k: v.get().strip() for k, v in campos.items()}
        datos["descripcion"] = txt_descripcion.get("1.0", tk.END).strip()

        # JSON características
        try:
            datos["caracteristicas_morfo"] = json.loads(
                txt_caracteristicas.get("1.0", tk.END).strip() or "{}"
            )
        except json.JSONDecodeError:
            messagebox.showerror("Error", "JSON inválido en características.")
            return

        # Lista de imágenes
        lista_imgs = [
            x.strip() for x in
            txt_imagenes.get("1.0", tk.END).replace("\n", ",").split(",")
            if x.strip()
        ]
        datos["imagenes"] = lista_imgs

        if not datos["nombre_cientifico"]:
            messagebox.showwarning("Faltan Datos", "Nombre científico obligatorio.")
            return

        db.especies.insert_one(datos)
        messagebox.showinfo("Éxito", "Mariposa agregada.")
        limpiar_campos()
        cargar_especies()

    def eliminar_especie():
        sel = tabla.selection()
        if not sel:
            return messagebox.showwarning("Error","Selecciona una mariposa")

        nombre = tabla.item(sel[0],"values")[0]
        if messagebox.askyesno("Confirmar",f"¿Eliminar '{nombre}'?"):
            db.especies.delete_one({"nombre_cientifico": nombre})
            cargar_especies()

    def editar_especie():
        sel = tabla.selection()
        if not sel:
            return messagebox.showwarning("Error","Selecciona una mariposa")

        nombre_original = tabla.item(sel[0], "values")[0]

        nuevos = {k: v.get().strip() for k,v in campos.items()}
        nuevos["descripcion"] = txt_descripcion.get("1.0", tk.END).strip()

        # JSON
        try:
            nuevos["caracteristicas_morfo"] = json.loads(
                txt_caracteristicas.get("1.0",tk.END).strip() or "{}"
            )
        except:
            return messagebox.showerror("Error","JSON inválido")

        # Imágenes
        lista_imgs = [
            x.strip() for x in
            txt_imagenes.get("1.0", tk.END).replace("\n", ",").split(",")
            if x.strip()
        ]
        nuevos["imagenes"] = lista_imgs

        db.especies.update_one({"nombre_cientifico": nombre_original},{"$set": nuevos})
        messagebox.showinfo("Éxito", "Mariposa editada.")
        limpiar_campos()
        cargar_especies()

    def exportar_pdf():
        try:
            especies = list(db.especies.find({}))

            if not especies:
                messagebox.showwarning("Sin datos", "No hay especies para exportar.")
                return

            archivo = "mariposas_exportadas.pdf"
            doc = SimpleDocTemplate(archivo, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph("<b>REPORTE DE ESPECIES DE MARIPOSAS</b>", styles["Title"]))
            story.append(Spacer(1, 20))

            for esp in especies:
                nombre = esp.get("nombre_cientifico", "")
                comun = esp.get("nombre_comun", "")
                familia = esp.get("familia", "")
                tipo = esp.get("tipo_especie", "")
                descripcion = esp.get("descripcion", "")
                caracteristicas = esp.get("caracteristicas_morfo", {})
                imagenes = esp.get("imagenes", [])

                texto = (
                    f"<b>Nombre Científico:</b> {nombre}<br/>"
                    f"<b>Nombre Común:</b> {comun}<br/>"
                    f"<b>Familia:</b> {familia}<br/>"
                    f"<b>Tipo:</b> {tipo}<br/>"
                    f"<b>Descripción:</b> {descripcion}<br/>"
                    f"<b>Características:</b> {json.dumps(caracteristicas)}<br/>"
                    f"<b>Imágenes:</b> {', '.join(imagenes)}<br/><br/>"
                )

                story.append(Paragraph(texto, styles["Normal"]))
                story.append(Spacer(1, 10))

            doc.build(story)

            messagebox.showinfo("Éxito", f"PDF exportado correctamente como:\n{archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el PDF:\n{str(e)}")

    #Botones CRUD
    frame_botones = tk.Frame(ventana, bg="#ede7f6")
    frame_botones.pack(pady=10)

    tk.Button(frame_botones, text="Agregar", bg="#00796b", fg="white",
              width=12, command=crear_especie).pack(side="left", padx=6)
    tk.Button(frame_botones, text="Editar", bg="#6a1b9a", fg="white",
              width=12, command=editar_especie).pack(side="left", padx=6)
    tk.Button(frame_botones, text="Eliminar", bg="#c62828", fg="white",
              width=12, command=eliminar_especie).pack(side="left", padx=6)
    tk.Button(frame_botones, text="Limpiar", bg="#5d4037", fg="white",
              width=12, command=limpiar_campos).pack(side="left", padx=6)
    tk.Button(frame_botones, text="Cerrar", bg="#616161", fg="white",
              width=12, command=ventana.destroy).pack(side="left", padx=6)
    tk.Button(frame_botones, text="Exportar PDF", bg="#283593", fg="white",
    command=exportar_pdf).pack(side="left", padx=10)

    #Selección en tabla
    def cargar_en_formulario(event):
        sel = tabla.selection()
        if not sel:
            return
        doc = db.especies.find_one({
            "nombre_cientifico": tabla.item(sel[0],"values")[0]
        })
        limpiar_campos()
        if doc:
            campos["nombre_cientifico"].insert(0, doc.get("nombre_cientifico",""))
            campos["nombre_comun"].insert(0, doc.get("nombre_comun",""))
            campos["familia"].insert(0, doc.get("familia",""))
            campos["tipo_especie"].insert(0, doc.get("tipo_especie",""))
            txt_descripcion.insert("1.0", doc.get("descripcion",""))
            txt_caracteristicas.insert("1.0", json.dumps(doc.get("caracteristicas_morfo",{}), indent=2))
            txt_imagenes.insert("1.0", "\n".join(doc.get("imagenes",[])))

    tabla.bind("<<TreeviewSelect>>", cargar_en_formulario)
