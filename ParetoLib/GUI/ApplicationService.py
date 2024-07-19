
# <ApplicationService.py>

from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.GUI.Router import translate

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from pathlib import Path

# DEBUG
from ParetoLib.CommandLanguage.Translation import Translation, STLe1Pack


class AppService:
    def __init__(self, window):
        self.window = window

    def check(self, should_show_message):
        stle2_program = self.window.get_program()
        stl_tree = None
        try:
            stl_tree = parser.parse(stle2_program)
        except Exception as e:
            error_message = str(e)
            QMessageBox.critical(None, "Error", f"Ocurrió un error: {error_message}")
            self.window.show_message('Error', f"Ocurrió un error:\n{error_message}")
        translation = translate(stl_tree)
        if len(translation.errors) == 0:
            if should_show_message:
                self.window.show_message('Info', 'There is no error found')
        else:
            error_text = 'The follow errors have been detected: ' + '\n'
            error_text += '- ' + translation.errors[0]
            for i in range(1, len(translation.errors)):
                error_text += '\n' + '- ' + translation.errors[i]
            self.window.show_message('Error', error_text)
        return len(translation.errors) == 0, translation

    def convertPath(self, filename):
        # os.path.join('Language', 'language_examples', name)
        current = Path(".")
        filepath = current / filename
        return filepath.resolve().absolute()

    def check_run(self):
        # ORIGINAL
        # no_error, translation = self.check(False)

        # DEBUG
        no_error = True
        translation = Translation()
        print(self.convertPath('Test_Output_STLe1.txt'))
        program_file_path = self.convertPath('Test_Output_STLe1.txt')
        parameters_file_path = self.convertPath('Test_Output_STLe1.txt')
        sTLe1Pack = STLe1Pack(program_file_path, parameters_file_path)
        translation.add_stle1_pack(self, sTLe1Pack)

        translation.stle1_packs
        if no_error:
            for stle1_pack in translation.stle1_packs:
                is_parametric = (stle1_pack.parameters_file_path is None)
                self.window.setParemetric(is_parametric)
                self.window.set_param_filepath(stle1_pack.parameters_file_path)
                self.window.run_stle(stle1_pack.program_file_path)

    def load(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.window, "Selecciona un archivo .stle", "",
                                                   "Archivos .stle (*.stle);;Todos los archivos (*)", options=options)

        if file_name:
            with open(file_name, 'r') as file:
                content = file.read()
                self.window.textarea.setPlainText(content)

    def save(self):
        # Obtención del contenido del textarea
        content = self.window.textarea.toPlainText()

        # Verificación de si el contenido está vacío
        if not content:
            self.window.show_message("Error", "El campo de lenguaje STLe está vacío.")
        else:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self.window, "Guardar como .stle", "",
                                                       "Archivos .ste (*.stle);;Todos los archivos (*)",
                                                       options=options)

            if file_name:
                with open(file_name, 'w') as file:
                    file.write(content)
