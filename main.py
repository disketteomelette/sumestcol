import sys, PyPDF2
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QLabel, QPlainTextEdit, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MainWindow(QMainWindow) :
    def __init__ (self) :
        super().__init__()
        self.setWindowTitle("sumestcol · github.com/disketteomelette")
        self.setGeometry(100, 100, 1300, 800)

        self.margin_target = "100000"

        self.drag_label = QLabel("Arrastra los dos PDFs de 'Estadísticas de colaboradores' aquí", self)
        self.drag_label.setGeometry(23, 42, 560, 30)
        self.drag_label.setAlignment(Qt.AlignLeft)

        self.result_text = QPlainTextEdit(self)
        self.result_text.setGeometry(20, 70, 300, 300)

        self.drag_label2 = QLabel("Resultados de la suma", self)
        self.drag_label2.setGeometry(23, 400, 560, 30)
        self.drag_label2.setAlignment(Qt.AlignLeft)

        self.result_text2 = QPlainTextEdit(self)
        self.result_text2.setGeometry(20, 430, 300, 300)

        self.setAcceptDrops(True)

        self.drag_label3 = QLabel("Aquí se calcularán las sumas totales y objetivos", self)
        self.drag_label3.setGeometry(23, 750, 560, 30)
        self.drag_label3.setAlignment(Qt.AlignLeft)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedSize(600, 700)
        self.canvas.move(200, 150)

        layout = QHBoxLayout()
        layout.addWidget(self.canvas)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def dragEnterEvent (self, event: QDragEnterEvent) :
        if event.mimeData().hasUrls() :
            event.acceptProposedAction()

    def dropEvent (self, event: QDropEvent) :
        file_paths = [url.toLocalFile() for url in event.mimeData().urls()]

        for file_path in file_paths :
            if not file_path.lower().endswith('.pdf') :
                self.result_text.setPlainText("Error: Solo se permiten archivos PDF")
                return

        if len(file_paths) != 2 :
            self.result_text.setPlainText(
                "ERROR: Debes arrastrar a la vez los dos PDFs de estadísticas de colaboradores.")
            return

        total_lines = []
        for file_path in file_paths :
            with open(file_path, 'rb') as file :
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages :
                    text = page.extract_text()
                    lines = text.split('\n')
                    for i, line in enumerate(lines) :
                        if " Total:" in line :
                            total_group = line.split(' ')[0]
                            for j in range(i + 1, min(i + 4, len(lines))) :
                                total_group += ";" + lines[j].strip()
                            total_lines.append(total_group)

        result_text = "\n".join(total_lines)
        original_text = result_text

        modified_text = original_text.replace("€", "")
        self.result_text.setPlainText(modified_text)

        identificadores = []
        lineascompletas = modified_text.split(sep="\n")

        for elemento in lineascompletas :
            identificador = elemento.split(sep=";")[0]
            if identificador not in identificadores :
                identificadores.append(identificador)

        resultadosfinales = ""
        for identificador in identificadores :
            coincidencias = []

            for linea in lineascompletas :
                if identificador in linea :
                    coincidencias.append(linea)

            if coincidencias :
                cantidad_elementos = len(coincidencias)
                if cantidad_elementos == 1 :
                    apasar = str(coincidencias).replace("'", "").replace("[", "").replace("]", "").replace(".",
                                                                                                           "").replace(
                        ",", ".") + "\n"
                    apasar = apasar.replace(",", ".").replace(" ", "")
                    resultadosfinales = resultadosfinales + apasar
                else :
                    suma1 = 0.0
                    suma2 = 0.0
                    concat = ""
                    contador = 0
                    for coincidencia in coincidencias :
                        primerdato = str(coincidencia.split(sep=";")[1]).replace(".", "")
                        primerdato = float(primerdato.replace(",", "."))
                        segundodato = str(coincidencia.split(sep=";")[2]).replace(".", "")
                        segundodato = float(segundodato.replace(",", "."))
                        preconcat = concat
                        concat = preconcat + "/" + str(coincidencia.split(sep=";")[3])
                        presuma1 = suma1
                        presuma2 = suma2
                        suma1 = round(presuma1 + primerdato, 2)
                        suma2 = round(presuma2 + segundodato, 2)
                        contador += 1
                        if contador == cantidad_elementos :
                            concat = concat[1 :].replace(",", ".").replace(" ", "")
                            lineasumada = str(identificador) + ";" + str(suma1) + ";" + str(suma2) + ";" + str(concat)
                            resultadosfinales = resultadosfinales + str(lineasumada) + "\n"

            else :
                print(f"* DEBUG * No se encontraron coincidencias para el identificador {identificador}.")

        self.result_text2.setPlainText(str(resultadosfinales))
        text = self.result_text2.toPlainText()
        lines = text.splitlines()
        categories = []
        values = []
        for line in lines :
            categories.append(line.split(sep=";")[0])
            values.append(line.split(sep=";")[2])

        ax = self.figure.add_subplot()
        categories = []
        values = []
        for line in lines :
            line_data = line.split(";")
            categories.append(line_data[0])
            values.append(float(line_data[2]))

        ax.bar(categories, values)
        ax.set_title('Margen')
        ax.set_position([0.2, 0.2, 0.6, 0.6])
        self.canvas.draw()

        totalmargen = totalfacturacion = totalobjetivo = 0.0

        for line in lines :
            datofact = float(line.split(sep=";")[1])
            totalfacturacion += datofact
            datomarg = float(line.split(sep=";")[2])
            totalmargen += datomarg

        totalobjetivo = totalmargen - float(self.margin_target)
        self.drag_label3.setText("Facturacion: " + str(totalfacturacion) + " € - Margen: " + str(
            totalmargen) + " € \n" + "Sobra/falta objetivo margen: " + str(totalobjetivo) + " €")


if __name__ == "__main__" :
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
