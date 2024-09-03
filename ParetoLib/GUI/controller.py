"""
<Controller.py>
"""

from PyQt5.QtWidgets import QFileDialog

from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.CommandLanguage.Translation import translate, Translation, STLe1Pack
from ParetoLib.GUI.application_service import ApplicationService
from ParetoLib.GUI.controller_interface import ControllerInterface
from ParetoLib.GUI.window_interface import WindowInterface


class Controller(ControllerInterface):
    def __init__(self, application_service: ApplicationService, window: WindowInterface):
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
            self.window.show_message(title='Error', body=f"An exception occurred:\n{error_message}", is_error=True)
        translation = translate(stl_tree)
        if len(translation.errors) == 0:
            if should_show_message:
                self.window.show_message(title='Info', body='There is no error found', is_error=False)
        else:
            error_text = 'The follow errors have been detected: ' + '\n'
            error_text += '- ' + translation.errors[0]
            for i in range(1, len(translation.errors)):
                error_text += '\n' + '- ' + translation.errors[i]
            self.window.show_message(title='Error', body=error_text, is_error=True)
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
                self.application_service.run_stle(is_parametric, stle1_pack.program_file_path,
                                                  signal_filepath, stle1_pack.parameters_file_path)

    def load(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.window, "Select a .stle file", "",
                                                   "Files .stle (*.stle);;All the files (*)", options=options)

        if file_name:
            with open(file_name, 'r') as file:
                content = file.read()
                self.window.set_program(content)

    def save(self):
        # Retrieving the content of the textarea
        content = self.window.get_program()

        # Checking if the content is empty
        if not content:
            self.window.show_message("Error", "The STLe language field is empty.", False)
        else:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self.window, "Save as .stle", "",
                                                       "Files .ste (*.stle);;All the files (*)",
                                                       options=options)

            if file_name:
                with open(file_name, 'w') as file:
                    file.write(content)