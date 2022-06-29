################################################################################
#   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    ConfigView  ##
################################################################################
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from src.View.SignInView import SignIn
from src.View.ChangeUsersView import ChangeUsersView
'''
    - Ventana de Configuración para el Usuario
    - En ella se podrá:
        · Cambiar el Tema de la Aplicación

     @parent: UserView
     @children:
'''


class ConfigView(QMainWindow):

    def __init__(view, parent=QMainWindow):

        super().__init__(parent)
        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/ConfigWindow.ui", view)

        # Carga del Combobox de selección de Tema
        view.cbTema.addItems(['Blue', 'Light'])

        if view.parent().id_usuario[0] == 5:
            view.gpAdmin.show()



        else:
            view.gpAdmin.hide()
            view.setFixedHeight(170)



        # Conexión de los eventos de botones clickados a la lógica de los controladores
        view.buttonAplicar.clicked.connect(view.applyChanges)
        view.buttonNewUser.clicked.connect(view.register)
        view.buttonResetPass.clicked.connect(view.showResetPass)

    def showResetPass(self):
        ch = ChangeUsersView(self)
        ch.show()


    def applyChanges(view):

        # Captura del Tema seleccionado
        tema = view.cbTema.currentText()

        if tema == 'Blue':
            view.parent().setStyleSheet("""
                                            * {
                        	                background-color: rgb(0, 73, 107)
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
            view.parent().theme = 'Blue'
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
        view.parent().updatePieChart(view.parent().currentCarteraReal)
        view.close()

    def register(self):
        conf = SignIn(self)
        conf.show()
