from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.CommandLanguage.Translation import translate


def check(window, should_show_message):
    stle2_program = window.get_program()
    stl_tree = parser.parse(stle2_program)
    translation = translate(stl_tree)
    if len(translation.errors) == 0:
        if should_show_message:
            window.show_message('There is no error found')
    else:
        error_text = 'The follow errors have been detected: ' + '\n'
        error_text += '- ' + translation.errors[0]
        for i in range(1, len(translation.errors) - 1):
            error_text += '\n' + '- ' + translation.errors[i]
        window.show_message(error_text)
    return len(translation.errors) == 0, translation


def check_run(window):
    no_error, translation = check(window, False)
    if no_error:
        for (stle1_program, param_filepath) in translation.pairs:
            window.set_param_filepath(param_filepath)
            window.run_stle()


def load(window):
    pass


def save(window):
    pass
