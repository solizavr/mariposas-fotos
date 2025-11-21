import tkinter as tk
from tkinter import messagebox
from database import db
from main import abrir_principal3

def validar_usuario():
    correo = entry_correo.get().strip()
    contrasena = entry_contrasena.get().strip()

    if not correo or not contrasena:
        messagebox.showwarning("Campos vacíos", "Por favor ingresa tu correo y contraseña.")
        return

    usuario = db.usuarios.find_one({"correo": correo, "password": contrasena})

    if usuario:
        messagebox.showinfo("Inicio de sesión exitoso",
                            f"Bienvenido, {usuario['nombre']} (Rol: {usuario['rol']})")
        ventana.destroy()  # cerrar ventana login
        abrir_principal3(usuario)
    else:
        messagebox.showerror("Error", "Usuario no encontrado o credenciales incorrectas.")

# UI
ventana = tk.Tk()
ventana.title("Inicio de sesión - MariposasDB")
ventana.geometry("400x250")
ventana.configure(bg="#e0f7fa")

tk.Label(ventana, text="Correo:", font=("Arial", 12), bg="#e0f7fa").pack(pady=(30, 5))
entry_correo = tk.Entry(ventana, width=35)
entry_correo.pack(pady=5)

tk.Label(ventana, text="Contraseña:", font=("Arial", 12), bg="#e0f7fa").pack(pady=5)
entry_contrasena = tk.Entry(ventana, width=35, show="*")
entry_contrasena.pack(pady=5)

tk.Button(ventana, text="Iniciar sesión", font=("Arial", 12, "bold"),
          bg="#00796b", fg="white", command=validar_usuario).pack(pady=20)

ventana.mainloop()
