################################################################################
#   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    ConfigView  ##
################################################################################
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

'''
    - Ventana de Configuración para el Usuario
    - En ella se podrá:
        · Cambiar el Tema de la Aplicación

     @parent: UserView
     @children:
'''

class ConfigView(QMainWindow):

    def __init__(view , parent=QMainWindow):

        super().__init__(parent)
        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/ConfigWindow.ui", view)

        # Carga del Combobox de selección de Tema
        view.cbTema.addItems(['Dark', 'Light'])

        # Conexión de los eventos de botones clickados a la lógica de los controladores
        view.buttonAplicar.clicked.connect(view.applyChanges)

    def applyChanges(view):

        # Captura del Tema seleccionado
        tema = view.cbTema.currentText()

        if tema == 'Dark':
            view.parent().setStyleSheet("""
                                            * {
                        	                background-color: rgb(34, 34, 34)
                                            }

                                            QLabel {
                                                color: rgb(255, 255, 255);

                                            }

                                            QLineEdit {
                                                border:  2px solid rgb(98, 98, 98);
                                                border-radius: 15px;
                                                color: rgb(255, 255, 255);
                                                background-color: rgb(151, 151, 151)
                                            }
                                            QLineEdit:hover{
                                                border: 2px solid rgb(48,50,62);
                                            }

                                            QLineEdit:focus {

                                                border : 2px solid rgb(48,50,62)

                                            }


                                            QPushButton {

                                                border-radius: 10px;
            	                                background-color: rgb(240, 240, 240);
            	                                color:rgb(0, 0, 0)
            	                                

                                            }

                                            QPushButton:hover {
                                                background-color: rgb(0, 0, 0);
                                                color: rgb(255, 255, 255)
                                            }
                                            
                                            QPushButton:checked {
                                                background-color: rgb(0, 0, 0);
                                                color: rgb(255, 255, 255)
                                            }

                                    """)
            view.parent().theme = 'Dark'
        if tema == 'Light':
            view.parent().setStyleSheet("""
                                * {
            	                background-color: rgb(151, 151, 151)
                                }

                                QLabel {
                                    color: rgb(255, 255, 255);

                                }

                                QLineEdit {
                                    border:  2px solid rgb(98, 98, 98);
                                    border-radius: 15px;
                                    color: rgb(255, 255, 255);
                                    background-color: rgb(151, 151, 151)
                                }
                                QLineEdit:hover{
                                    border: 2px solid rgb(48,50,62);
                                }

                                QLineEdit:focus {

                                    border : 2px solid rgb(48,50,62)

                                }


                                QPushButton {

                                    border-radius: 10px;
	                                background-color: rgb(84, 84, 84);
	                                color:rgb(255, 255, 255)

                                }

                                QPushButton:hover {
                                    background-color: rgb(0, 85,124);
                                    color: rgb(255, 255, 255)
                                }
                                QPushButton:checked {
                                    background-color: rgb(0, 85,124);
                                    color: rgb(255, 255, 255)
                                }

                        """)
            view.parent().theme = 'Light'

        view.parent().updateGraph(None, view.parent().isins_selected)
        view.close()

