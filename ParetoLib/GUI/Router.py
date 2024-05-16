
# <Router.py>

# Configuration using main arguments instead of environment variables
import ParetoLib.main as configuration


if configuration.DEBUG_MODE:
    from Tests.View.TranslationWildcard import translate
else:
    from ParetoLib.CommandLanguage.Translation import translate
