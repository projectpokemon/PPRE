"""Temporary bootstrap for PPRE5"""

import sys

import ppre.session
import ppre.ui.home


def start(ui_type='GUI'):
    if ui_type == 'GUI':
        import ppre.gui
        session = ppre.session.Session(sys.argv)
        ui = ppre.gui.Interface(session)
        home = ppre.ui.home.HomeUserInterface(ui, session)
        home.show()
        session.app.exec_()
    elif ui_type == 'CLI':
        import ppre.cli
        session = ppre.session.Session(sys.argv)
        ui = ppre.cli.Interface(session)
        home = ppre.ui.home.HomeUserInterface(ui, session)
        home.show()
    elif ui_type == 'API':
        import ppre.api
        ui = ppre.api.Interface()
    else:
        raise ValueError('Unsupported UI Type: {0}'.format(ui_type))

if __name__ == '__main__':
    if '--cli' in sys.argv:
        start('CLI')
    elif '--api' in sys.argv:
        start('API')
    else:
        start('GUI')
