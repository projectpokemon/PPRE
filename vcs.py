"""Version Control System for tracking revisions of edits

PPRE mainly uses Git for these changes.
"""

from collections import namedtuple
from cStringIO import StringIO
import subprocess


LogEntry = namedtuple('LogEntry', 'version date message')


class GitControl(object):
    """Git controller

    Files get added when init() is called on the directory. All files
    that were changed are automatically committed during commit.

    """
    def __init__(self, directory):
        self.directory = directory

    def init(self):
        """Initialize new repository and add all files in it"""
        self.call('init')
        self.call('add', '.')
        self.commit('Initialized repository')

    def commit(self, message):
        """Commits all files automatically with a message

        Parameters
        ----------
        message : string
            Commit message
        """
        self.call('commit', '-a', '-m', message)

    def log(self):
        """Get the log of all changes

        Returns
        -------
        entries : list of LogEntry
        """
        entries = []
        lines = self.call('log').split('\n')
        entry = None
        while lines:
            line = lines.pop(0)
            if not line.strip():
                continue
            if line[:6] == 'commit':
                if entry:
                    entries.append(entry)
                entry = LogEntry(line[7:], None, '')
            elif line[:4] == 'date':
                entry.date = line[6:].strip()
            else:
                entry.message += line+'\n'  # TODO: Strip last \n
        return entries

    def call(self, *args):
        """Invokes the git command with the supplied arguments

        This is automatically invoked inside of the control directory

        Returns
        -------
        stdout : string
        """
        # Prefer cwd to --git-dir for consistency of commands.
        # Nothing should be ran outside of cwd anyways
        with StringIO() as stdout:
            subprocess.call(self.command+args, cwd=self.directory,
                            stdout=stdout)
            return stdout.getvalue()
