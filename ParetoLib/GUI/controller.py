"""
<Controller.py>
"""

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.CommandLanguage.Translation import translate, Translation, STLe1Pack


class Controller:
    def __init__(self, window, application_service):
        self.window = window
        self.application_service = application_service
        self.window.set_controller(self)

    def check(self, should_show_message, stle2_program):
        stl_tree = None
        try:
            # Raise some exceptions
            stl_tree = parser.parse(stle2_program)
        except Exception as e:
            error_message = str(e)
            QMessageBox.critical(self.window, "Error", f"An error occurred: {error_message}")
            self.window.show_message('Error', f"An error occurred:\n{error_message}")
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

    @staticmethod
    def _mytest_check(no_error):
        translation = Translation()
        program_file_path = 'Test_Output_STLe1.txt'
        parameters_file_path = 'Test_Output_STLe1.txt'
        sTLe1Pack = STLe1Pack(program_file_path, parameters_file_path)
        translation.add_stle1_pack(sTLe1Pack)
        return no_error, translation

    def check_run(self, stle2_program, signal_filepath):
        """
        stle2_filepath :: str
        signal_filepath :: str
        """
        no_error, translation = self.check(False, stle2_program)
        if no_error:
            for stle1_pack in translation.stle1_packs:
                is_parametric = False
                if stle1_pack.parameters_file_path:
                    is_parametric = True
                self.application_service.run_stle(self, is_parametric, stle1_pack.program_file_path,
                                                  signal_filepath, stle1_pack.parameters_file_path)

    def load(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.window, "Select a .stle file", "",
                                                   "Files .stle (*.stle);;All the files (*)", options=options)

        if file_name:
            with open(file_name, 'r') as file:
                content = file.read()
                self.window.textarea.setPlainText(content)

    def save(self):
        # Retrieving the content of the textarea
        content = self.window.textarea.toPlainText()

        # Checking if the content is empty
        if not content:
            self.window.show_message("Error", "The STLe language field is empty.")
        else:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self.window, "Save as .stle", "",
                                                       "Files .ste (*.stle);;All the files (*)",
                                                       options=options)

            if file_name:
                with open(file_name, 'w') as file:
                    file.write(content)
