"""Version Control System for tracking revisions of edits

PPRE mainly uses Git for these changes.
"""

from cStringIO import StringIO
import os
import subprocess


class LogEntry(object):
    def __init__(self, version, date, message):
        self.version = version
        self.date = date
        self.message = message


class DiffEntry(object):
    def __init__(self, filename, changes):
        self.filename = filename
        self.changes = changes


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
        with open(os.path.join(self.directory, '.gitattributes'), 'w')\
                as attr_file:
            attr_file.write('[0-9] diff=narc\n')
            attr_file.write('*.narc diff=narc\n')
        self.call('add', '.')
        self.call('config', 'diff.narc.textconv', 'narcinfo')
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
                    entry.message = entry.message.rstrip('\n')
                    entries.append(entry)
                entry = LogEntry(line[7:], None, '')
            elif line[:4] == 'Date':
                entry.date = line[6:].strip()
            else:
                entry.message += line+'\n'
        return entries

    def diff(self, version='HEAD', new_version=None):
        """Get changes between version1 and version2

        Paramters
        ---------
        version : string
            Old version
        new_version : string or None
            New version. If None, new_version refers to the working tree

        Returns
        -------
        entries : list of DiffEntry
        """
        entries = []
        if new_version is not None:
            version += '..'+new_version
        lines = self.call('diff', version).split('\n')
        entry = None
        while lines:
            line = lines.pop(0)
            if line[:4] == 'diff':
                if entry:
                    entry.changes = entry.changes.rstrip('\n')
                    entries.append(entry)
                entry = DiffEntry('', '')
            elif line[:5] == 'index':
                continue
            elif line[:3] == '---':
                entry.filename = line[6:]
            elif line[:3] == '+++':
                continue
            else:
                entry.changes += line+'\n'
        return entries

    def call(self, command, *args):
        """Invokes the git command with the supplied arguments

        This is automatically invoked inside of the control directory

        Returns
        -------
        stdout : string
        """
        env = os.environ
        old_path = env['PATH']
        # For bin/narcinfo
        # TODO: Move to main/bootstrap
        env['PATH'] += ':'+os.path.join(os.path.dirname(__file__), 'bin')
        try:
            # Prefer cwd to --git-dir for consistency of commands.
            # Nothing should be ran outside of cwd anyways
            return subprocess.check_output(['git', command]+list(args),
                                           cwd=self.directory, env=env)
        finally:
            env['PATH'] = old_path
