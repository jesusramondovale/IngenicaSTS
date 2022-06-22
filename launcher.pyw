# -*- coding: utf-8 -*-
import sys, os
from PyQt5.QtWidgets import *
# Importamos el objeto de Interfaz MainView (la vista + lógica de programación de la ventana LogIn)
from src.View.MainView import MainView

import ctypes

myappid = u'IngenicaSTS.Software.GestorETF.v7'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

'''
 - Clase principal de lanzamiento, el hilo de ejecución comienza aquí.
 - Lanza la ventana principal de la aplicación (Acceso : Log In)
 - No recibe ningún parámetro 
'''
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Crea una instancia de objeto MainView (la vista del Log In)
    myapp = MainView(app)

    # Visualiza en pantalla la interfaz de usuario LogIn
    myapp.show()

    sys.exit(app.exec_()) #  <----- Bucle donde reside el hilo principal del GUI
