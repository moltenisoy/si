import sys
import os
import psutil
import json
import subprocess
from PyQt5 import QtCore, QtGui, QtWidgets

CONFIG_FILE = "config_monitor_thermal.ini"
CONFIG_JSON = "config.json"


class BandejaSistema(QtWidgets.QSystemTrayIcon):
    mostrar_configuracion = QtCore.pyqtSignal()
    cerrar_aplicacion = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Intentar usar 1.ico, si no existe usa icono por defecto
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1.ico")
        if os.path.exists(icon_path):
            icon = QtGui.QIcon(icon_path)
        else:
            icon = parent.windowIcon() if parent is not None else QtGui.QIcon()

        self.setIcon(icon)
        self.setToolTip("MONITOR TERMICO")

        menu = QtWidgets.QMenu()
        accion_config = menu.addAction("CONFIGURACION")
        accion_salir = menu.addAction("CERRAR")

        accion_config.triggered.connect(self.mostrar_configuracion)
        accion_salir.triggered.connect(self.cerrar_aplicacion)

        self.setContextMenu(menu)


class VentanaPrincipal(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MONITOR TERMICO")
        self.resize(800, 600)
        self.centrar_ventana()

        # Icono de la ventana
        self.setWindowIcon(QtGui.QIcon())

        # Listas de juegos y lista blanca (en memoria)
        self.lista_juegos = []
        self.lista_blanca = []

        self.optimusprime_process = None
        self.optimusprime_running = False

        self.iniciar_con_sistema = False
        self.cargar_configuracion()
        self.cargar_config_json()

        # Configurar estilo general
        self.aplicar_estilo()

        # Widget central con pestañas
        self.tab_widget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Crear pestañas
        self.crear_pestana_procesos()
        self.crear_pestana_listas()
        self.crear_pestana_interruptores()
        self.crear_pestana_termico()

        # Bandeja del sistema
        self.tray_icon = BandejaSistema(self)
        self.tray_icon.mostrar_configuracion.connect(self.mostrar_desde_bandeja)
        self.tray_icon.cerrar_aplicacion.connect(self.cerrar_desde_bandeja)
        self.tray_icon.show()

    # ---------------------- CONFIGURACIÓN Y ESTILO ---------------------- #

    def centrar_ventana(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def aplicar_estilo(self):
        # Paleta de colores
        palette = self.palette()
        fondo = QtGui.QColor(30, 0, 60)     # VIOLETA OSCURO
        texto_fucsia = QtGui.QColor(255, 0, 150)
        texto_blanco = QtGui.QColor(255, 255, 255)

        palette.setColor(QtGui.QPalette.Window, fondo)
        palette.setColor(QtGui.QPalette.Base, fondo.darker(120))
        palette.setColor(QtGui.QPalette.AlternateBase, fondo.darker(110))
        palette.setColor(QtGui.QPalette.WindowText, texto_blanco)
        palette.setColor(QtGui.QPalette.Text, texto_fucsia)
        palette.setColor(QtGui.QPalette.Button, fondo.darker(130))
        palette.setColor(QtGui.QPalette.ButtonText, texto_fucsia)
        palette.setColor(QtGui.QPalette.Highlight, texto_fucsia)
        palette.setColor(QtGui.QPalette.HighlightedText, texto_blanco)

        self.setPalette(palette)

        # Estilo con fucsia para bordes y texto, fondo violeta oscuro
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E003C;
            }
            QLabel {
                color: #FFFFFF;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 2px solid #FF0096;
            }
            QTabBar::tab {
                background: #1E003C;
                color: #FF0096;
                padding: 8px 16px;
                border: 1px solid #FF0096;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3A006E;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #3A006E;
                color: #FF0096;
                border: 2px solid #FF0096;
                border-radius: 4px;
                padding: 6px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5500A0;
            }
            QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QComboBox {
                background-color: #120022;
                color: #FF0096;
                border: 1px solid #FF0096;
            }
            QListWidget {
                background-color: #120022;
                color: #FF0096;
                border: 1px solid #FF0096;
            }
            QSlider::groove:horizontal {
                border: 1px solid #FF0096;
                height: 8px;
                background: #120022;
            }
            QSlider::handle:horizontal {
                background: #FF0096;
                border: 1px solid #FFFFFF;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QCheckBox {
                color: #FF0096;
                font-weight: bold;
            }
        """)

    def cargar_configuracion(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip().upper()
                        v = v.strip().upper()
                        if k == "INICIAR_CON_SISTEMA":
                            self.iniciar_con_sistema = (v == "SI")
        except Exception:
            pass

    def guardar_configuracion(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write("# CONFIGURACION MONITOR TERMICO\n")
                f.write("INICIAR_CON_SISTEMA={}\n".format("SI" if self.iniciar_con_sistema else "NO"))
        except Exception:
            pass

    def cargar_config_json(self):
        if os.path.exists(CONFIG_JSON):
            try:
                with open(CONFIG_JSON, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.lista_juegos = config.get("lista_juegos", [])
                    self.lista_blanca = config.get("lista_blanca", [])
                    self.actualizar_listas_tab2()
            except Exception:
                pass

    def guardar_config_json(self):
        try:
            config = {
                "lista_juegos": self.lista_juegos,
                "lista_blanca": self.lista_blanca
            }
            with open(CONFIG_JSON, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    # ---------------------- PESTAÑA 1: PROCESOS ---------------------- #

    def crear_pestana_procesos(self):
        pestaña = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(pestaña)

        titulo = QtWidgets.QLabel("LISTA DE PROCESOS DE USUARIO (ESTATICA)")
        titulo.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(titulo)

        self.lista_procesos_widget = QtWidgets.QListWidget()
        layout.addWidget(self.lista_procesos_widget)

        botones_layout = QtWidgets.QHBoxLayout()

        btn_refrescar = QtWidgets.QPushButton("REFRESCAR")
        btn_refrescar.clicked.connect(self.refrescar_procesos)
        botones_layout.addWidget(btn_refrescar)

        btn_agregar_juego = QtWidgets.QPushButton("AGREGAR A LISTA DE JUEGOS")
        btn_agregar_juego.clicked.connect(self.agregar_proceso_a_juegos)
        botones_layout.addWidget(btn_agregar_juego)

        btn_agregar_blanca = QtWidgets.QPushButton("AGREGAR A LISTA BLANCA")
        btn_agregar_blanca.clicked.connect(self.agregar_proceso_a_blanca)
        botones_layout.addWidget(btn_agregar_blanca)

        layout.addLayout(botones_layout)

        self.tab_widget.addTab(pestaña, "PROCESOS")

        # Cargar lista inicial
        self.refrescar_procesos()

    def obtener_usuario_actual(self):
        try:
            return psutil.Process().username()
        except Exception:
            return None

    def es_proceso_de_usuario(self, proc):
        usuario_actual = self.obtener_usuario_actual()
        try:
            u = proc.username()
            if usuario_actual is None:
                # Si no pudimos obtener usuario actual, filtramos por que no sea del sistema de forma muy simple
                return not ("SYSTEM" in u.upper() or "SERVICIO" in u.upper() or "SERVICE" in u.upper())
            else:
                # Mismo usuario
                return u == usuario_actual
        except Exception:
            return False

    def refrescar_procesos(self):
        self.lista_procesos_widget.clear()
        for proc in psutil.process_iter(attrs=["pid", "name", "username"]):
            if self.es_proceso_de_usuario(proc):
                info = proc.info
                nombre = info.get("name") or "DESCONOCIDO"
                pid = info.get("pid")
                usuario = info.get("username") or ""
                texto = f"{nombre.upper()} (PID {pid}) - {usuario.upper()}"
                item = QtWidgets.QListWidgetItem(texto)
                # Guardar datos crudos en el item
                item.setData(QtCore.Qt.UserRole, {"name": nombre, "pid": pid, "username": usuario})
                self.lista_procesos_widget.addItem(item)

    def obtener_proceso_seleccionado(self):
        item = self.lista_procesos_widget.currentItem()
        if item is None:
            QtWidgets.QMessageBox.warning(self, "ATENCION", "DEBE SELECCIONAR UN PROCESO.")
            return None
        data = item.data(QtCore.Qt.UserRole)
        return data

    def agregar_proceso_a_juegos(self):
        data = self.obtener_proceso_seleccionado()
        if not data:
            return
        nombre = data["name"]
        if nombre not in self.lista_juegos:
            self.lista_juegos.append(nombre)
            self.actualizar_listas_tab2()
            self.guardar_config_json()
        QtWidgets.QMessageBox.information(self, "LISTA DE JUEGOS", f"SE AGREGO {nombre.upper()} A LA LISTA DE JUEGOS.")

    def agregar_proceso_a_blanca(self):
        data = self.obtener_proceso_seleccionado()
        if not data:
            return
        nombre = data["name"]
        if nombre not in self.lista_blanca:
            self.lista_blanca.append(nombre)
            self.actualizar_listas_tab2()
            self.guardar_config_json()
        QtWidgets.QMessageBox.information(self, "LISTA BLANCA", f"SE AGREGO {nombre.upper()} A LA LISTA BLANCA.")

    # ---------------------- PESTAÑA 2: LISTAS ---------------------- #

    def crear_pestana_listas(self):
        pestaña = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(pestaña)

        # Lista de juegos
        cont_juegos = QtWidgets.QVBoxLayout()
        lbl_juegos = QtWidgets.QLabel("LISTA DE JUEGOS")
        lbl_juegos.setAlignment(QtCore.Qt.AlignCenter)
        cont_juegos.addWidget(lbl_juegos)

        self.lista_juegos_widget = QtWidgets.QListWidget()
        cont_juegos.addWidget(self.lista_juegos_widget)

        btn_quitar_juego = QtWidgets.QPushButton("QUITAR SELECCIONADO")
        btn_quitar_juego.clicked.connect(self.quitar_juego_seleccionado)
        cont_juegos.addWidget(btn_quitar_juego)

        # Lista blanca
        cont_blanca = QtWidgets.QVBoxLayout()
        lbl_blanca = QtWidgets.QLabel("LISTA BLANCA")
        lbl_blanca.setAlignment(QtCore.Qt.AlignCenter)
        cont_blanca.addWidget(lbl_blanca)

        self.lista_blanca_widget = QtWidgets.QListWidget()
        cont_blanca.addWidget(self.lista_blanca_widget)

        btn_quitar_blanca = QtWidgets.QPushButton("QUITAR SELECCIONADO")
        btn_quitar_blanca.clicked.connect(self.quitar_blanca_seleccionado)
        cont_blanca.addWidget(btn_quitar_blanca)

        layout.addLayout(cont_juegos)
        layout.addLayout(cont_blanca)

        self.tab_widget.addTab(pestaña, "LISTAS")

    def actualizar_listas_tab2(self):
        # Actualizar juegos
        self.lista_juegos_widget.clear()
        for j in self.lista_juegos:
            self.lista_juegos_widget.addItem(j.upper())

        # Actualizar lista blanca
        self.lista_blanca_widget.clear()
        for b in self.lista_blanca:
            self.lista_blanca_widget.addItem(b.upper())

    def quitar_juego_seleccionado(self):
        fila = self.lista_juegos_widget.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.warning(self, "ATENCION", "DEBE SELECCIONAR UN JUEGO.")
            return
        nombre = self.lista_juegos_widget.item(fila).text()
        self.lista_juegos.pop(fila)
        self.actualizar_listas_tab2()
        self.guardar_config_json()
        QtWidgets.QMessageBox.information(self, "LISTA DE JUEGOS", f"SE QUITO {nombre} DE LA LISTA DE JUEGOS.")

    def quitar_blanca_seleccionado(self):
        fila = self.lista_blanca_widget.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.warning(self, "ATENCION", "DEBE SELECCIONAR UN ELEMENTO.")
            return
        nombre = self.lista_blanca_widget.item(fila).text()
        self.lista_blanca.pop(fila)
        self.actualizar_listas_tab2()
        self.guardar_config_json()
        QtWidgets.QMessageBox.information(self, "LISTA BLANCA", f"SE QUITO {nombre} DE LA LISTA BLANCA.")

    # ---------------------- PESTAÑA 3: INTERRUPTORES + CONSOLA ---------------------- #

    def crear_pestana_interruptores(self):
        pestaña = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(pestaña)

        lbl_titulo = QtWidgets.QLabel("INTERRUPTORES DE FUNCIONES")
        lbl_titulo.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(lbl_titulo)

        self.interruptores = []
        grid = QtWidgets.QGridLayout()
        
        self.optimusprime_switch = QtWidgets.QCheckBox("OPTIMUSPRIME")
        self.optimusprime_switch.setChecked(False)
        self.optimusprime_switch.stateChanged.connect(self.toggle_optimusprime)
        self.interruptores.append(self.optimusprime_switch)
        grid.addWidget(self.optimusprime_switch, 0, 0)

        for i in range(1, 8):
            check = QtWidgets.QCheckBox(f"INTERRUPTOR {i + 1}")
            check.setChecked(False)
            check.stateChanged.connect(self.cambio_interruptor_color)
            self.interruptores.append(check)
            fila = i // 2
            col = i % 2
            grid.addWidget(check, fila, col)
        layout.addLayout(grid)

        lbl_consola = QtWidgets.QLabel("CONSOLA DE LOG OPTIMUSPRIME")
        lbl_consola.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(lbl_consola)

        self.consola_log = QtWidgets.QPlainTextEdit()
        self.consola_log.setReadOnly(True)
        self.consola_log.setPlainText("LOGS DE OPTIMUSPRIME SE MOSTRARAN AQUI.")
        layout.addWidget(self.consola_log)

        self.log_timer = QtCore.QTimer()
        self.log_timer.timeout.connect(self.actualizar_logs)
        self.log_timer.start(1000)

        self.tab_widget.addTab(pestaña, "INTERRUPTORES")

    def cambio_interruptor_color(self):
        sender = self.sender()
        if isinstance(sender, QtWidgets.QCheckBox):
            if sender.isChecked():
                sender.setStyleSheet("QCheckBox { color: #00FF00; font-weight: bold; }")
            else:
                sender.setStyleSheet("QCheckBox { color: #FF0096; font-weight: bold; }")

    def toggle_optimusprime(self):
        if self.optimusprime_switch.isChecked():
            self.iniciar_optimusprime()
        else:
            self.detener_optimusprime()
        self.cambio_interruptor_color()

    def iniciar_optimusprime(self):
        if self.optimusprime_running:
            return
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "optimusprime.py")
            if not os.path.exists(script_path):
                self.agregar_log("ERROR: NO SE ENCONTRO optimusprime.py")
                self.optimusprime_switch.setChecked(False)
                return
            
            self.optimusprime_process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            self.optimusprime_running = True
            self.agregar_log("OPTIMUSPRIME INICIADO")
        except Exception as e:
            self.agregar_log(f"ERROR AL INICIAR OPTIMUSPRIME: {str(e)}")
            self.optimusprime_switch.setChecked(False)

    def detener_optimusprime(self):
        if not self.optimusprime_running:
            return
        try:
            if self.optimusprime_process:
                self.optimusprime_process.terminate()
                try:
                    self.optimusprime_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.optimusprime_process.kill()
                self.optimusprime_process = None
            self.optimusprime_running = False
            self.agregar_log("OPTIMUSPRIME DETENIDO")
        except Exception as e:
            self.agregar_log(f"ERROR AL DETENER OPTIMUSPRIME: {str(e)}")

    def actualizar_logs(self):
        if self.optimusprime_running and self.optimusprime_process:
            try:
                if self.optimusprime_process.poll() is not None:
                    self.optimusprime_running = False
                    self.optimusprime_switch.setChecked(False)
                    self.agregar_log("OPTIMUSPRIME FINALIZADO")
                    return
                
                import select
                if hasattr(select, 'select'):
                    pass
            except Exception:
                pass

    def agregar_log(self, mensaje):
        timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.consola_log.appendPlainText(f"[{timestamp}] {mensaje}")

    # ---------------------- PESTAÑA 4: CONTROL TERMICO ---------------------- #

    def crear_pestana_termico(self):
        pestaña = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(pestaña)

        lbl_titulo = QtWidgets.QLabel("CONFIGURACION TERMICA (GRAFICA)")
        lbl_titulo.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(lbl_titulo)

        # Sliders 40 a 110
        self.slider_suave = self.crear_bloque_slider(
            "THERMAL THROTTLING SUAVE",
            layout
        )
        self.slider_agresivo = self.crear_bloque_slider(
            "THERMAL THROTTLING AGRESIVO",
            layout
        )
        self.slider_apagado = self.crear_bloque_slider(
            "APAGADO FORZADO",
            layout
        )

        # Checkbox iniciar con el sistema
        self.checkbox_inicio = QtWidgets.QCheckBox("INICIAR CON EL SISTEMA")
        self.checkbox_inicio.setChecked(self.iniciar_con_sistema)
        self.checkbox_inicio.stateChanged.connect(self.cambiar_inicio_sistema)
        layout.addWidget(self.checkbox_inicio)

        info_lbl = QtWidgets.QLabel(
            "POR AHORA SOLO COMO INTERFAZ GRAFICA. SE VINCULARA A UNA FUNCION FUTURA DE MONITOREO TERMICO."
        )
        info_lbl.setWordWrap(True)
        info_lbl.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info_lbl)

        self.tab_widget.addTab(pestaña, "TERMICO")

    def crear_bloque_slider(self, titulo, layout_padre):
        cont = QtWidgets.QVBoxLayout()

        lbl = QtWidgets.QLabel(titulo)
        lbl.setAlignment(QtCore.Qt.AlignLeft)
        cont.addWidget(lbl)

        sub = QtWidgets.QHBoxLayout()
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(40)
        slider.setMaximum(110)
        slider.setValue(80)

        valor_lbl = QtWidgets.QLabel(f"{slider.value()} °C")
        valor_lbl.setAlignment(QtCore.Qt.AlignRight)

        def actualizar_valor(v):
            valor_lbl.setText(f"{v} °C")

        slider.valueChanged.connect(actualizar_valor)

        sub.addWidget(slider)
        sub.addWidget(valor_lbl)
        cont.addLayout(sub)

        layout_padre.addLayout(cont)
        return slider

    def cambiar_inicio_sistema(self, estado):
        self.iniciar_con_sistema = (estado == QtCore.Qt.Checked)
        self.guardar_configuracion()
        # NO se modifica el registro ni el planificador, solo se informa
        if self.iniciar_con_sistema:
            QtWidgets.QMessageBox.information(
                self,
                "INICIAR CON EL SISTEMA",
                "LA OPCION DE INICIAR CON EL SISTEMA SE MARCO.\n"
                "EN UNA VERSION FUTURA SE VINCULARA AL REGISTRO O TAREAS PROGRAMADAS."
            )
        else:
            QtWidgets.QMessageBox.information(
                self,
                "INICIAR CON EL SISTEMA",
                "LA OPCION DE INICIAR CON EL SISTEMA SE DESMARCO."
            )

    # ---------------------- MANEJO DE CIERRE / BANDEJA ---------------------- #

    def closeEvent(self, event):
        # En lugar de cerrar, minimizar a bandeja
        event.ignore()
        self.ocultar_a_bandeja()

    def ocultar_a_bandeja(self):
        self.hide()
        self.tray_icon.showMessage(
            "MONITOR TERMICO",
            "LA APLICACION SIGUE EJECUTANDOSE EN LA BANDEJA DE SISTEMA.",
            QtWidgets.QSystemTrayIcon.Information,
            3000
        )

    def mostrar_desde_bandeja(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def cerrar_desde_bandeja(self):
        if self.optimusprime_running:
            self.detener_optimusprime()
        self.tray_icon.hide()
        QtWidgets.qApp.quit()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()