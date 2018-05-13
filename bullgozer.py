__version__ = '0.0.1'
__author__ = 'Adam Benson'

'''
BullGozer The Destroyer

First a nomial disclaimer.  I wanted a kitchy name for this new tool whose only purpose is to seek and destroy
various file types. A Bulldozer of sorts that would plow through old junk and just get rid of it.  A "Destroyer of
Worlds", so to speak. Vishnu and Shiva came to mind, not entirely having a clear grasp of Hindu religious
characters, and then I was reminded of Gozer the Destroyer, and instantly BullGozer the Destroyer was born.

So, BullGozer is designed to search for old junk in a folder structure and delete it.  Very simple... brute force
seek and destroy. This first version will be rudimentary and fully text based, but future version may include a UI,
and may in fact, get tied into the RollOutMachine. Perhaps a "Launch BullGozer" button from the RolloutMachine's UI.

Config:
project_list: str('') - Comma delineated string for conversion to list. If not blank, Disbled_Projects is ignored.
Disabled_Projects: bool(True/False) - If True & project_list is empty, then only disabled shotgun projects are used
programs: A comma list of software to specifically filter for
'''

import os
import sys
import platform
import logging as logger
import ConfigParser
from shotgun_api3 import Shotgun
import time
from datetime import datetime, timedelta
from ui import bullgozer_ui as bgi
from PySide import QtGui, QtCore
import json as js
import re
import glob
import math

# -----------------------------------------------------
# Rebuilder
# -----------------------------------------------------
class rebuilder():
    """
    This class will rebuild UI and configuration issues
    """
    def check_root(self, root=None):
        new_root = root
        if root:
            if not os.path.exists(root):
                # This should open a small dialog to find a new path
                new_root = 'c:'
        return new_root

    def build_default_config_file(self):
        new_config_path = ''
        config_path = sys.path[0]
        config_path += '/bullgozer_setup.cfg'
        config_path = config_path.replace('\\', '/')

        raw_config = ConfigParser.RawConfigParser()

        log_path = '/tools/scripts/logs/'
        destroyer_path = '/tools/scripts/destroyers/'
        linux_drive = os.path.expanduser('~')
        mac_drive = os.path.expanduser('~')
        win_drive = os.path.expanduser('~')

        sg_key = 'Script Key Required for Shotgun Integration'
        sg_script = 'Shotgun Script name required for Shotgun Integration'
        sg_url = 'Shotgun Account Path: ex: account.shotgunstudio.com'

        caches = '.bgeo,.bgeo.sc,.ifd,.cachedat,.cachehdr,.mcx,.bif,.pdc,.mcc'
        search_folders = 'renders,playblasts'
        working_files = '.nk,.mb,.ma,.mud,.hip,.psd,.psb,.ztl'
        programs = 'maya,nuke,zbrush,mudbox,houdini,softimage,photoshop'
        keep_count = 5

        debug_logging = True

        Disabled_Projects = True
        project_list = ''
        folder_override = ''

        raw_config.add_section('Parameters')
        raw_config.set('Parameters', 'programs', programs)
        raw_config.set('Parameters', 'working_files', working_files)
        raw_config.set('Parameters', 'search_folders', search_folders)
        raw_config.set('Parameters', 'caches', caches)
        raw_config.set('Parameters', 'keep_count', keep_count)

        raw_config.add_section('Shotgun')
        raw_config.set('Shotgun', 'shotgun_key', sg_key)
        raw_config.set('Shotgun', 'shotgun_script_name', sg_script)
        raw_config.set('Shotgun', 'shotgun_url', sg_url)

        raw_config.add_section('BullGozer')
        raw_config.set('BullGozer', 'destroyer_path', destroyer_path)
        raw_config.set('BullGozer', 'log_path', log_path)
        raw_config.set('BullGozer', 'linux_drive', linux_drive)
        raw_config.set('BullGozer', 'mac_drive', mac_drive)
        raw_config.set('BullGozer', 'win_drive', win_drive)

        raw_config.add_section('Debugger')
        raw_config.set('Debugger', 'debug_logging', debug_logging)

        raw_config.add_section('Root')
        raw_config.set('Root', 'Disabled_Projects', Disabled_Projects)
        raw_config.set('Root', 'project_list', project_list)
        raw_config.set('Root', 'folder_override', folder_override)
        logger.info('All variables set')

        with open(config_path, 'wb') as config:
            logger.info('Writing the configuration file...')
            raw_config.write(config)

        return new_config_path

    def check_log_path(self, root=None, path=None):
        if root and path:
            log_path = root + path
            if not os.path.exists(log_path):
                os.makedirs(log_path)


# ---------------------------------------------------
# Initial Setup
# ---------------------------------------------------
prelog = 'Initial setup running\n'
rebuild = rebuilder()
sys_path = sys.path
config_name = 'bullgozer_setup.cfg'
try:
    config_path = [f for f in sys_path if os.path.isfile(f + '/' + config_name)][0] + '/' + config_name
    config_path = config_path.replace('\\', '/')
    prelog += 'Configuration file found: %s\n' % config_path
except IndexError:
    prelog += 'Configuration file not found.  A new configuration file will be created.\n'
    config_path = None

if not config_path:
    # Eventually, this will kill shit.  There must be a contingency if the configuration file isn't found.
    config_path = rebuild.build_default_config_file()
    prelog += 'Configuration file created.\n'

config_file = ConfigParser.ConfigParser()
config_file.read(config_path)
prelog += 'Configuration file opened.\n'

cfg_win_drive = config_file.get('BullGozer', 'win_drive')
cfg_mac_drive = config_file.get('BullGozer', 'mac_drive')
cfg_linux_drive = config_file.get('BullGozer', 'linux_drive')
cfg_log_path = config_file.get('BullGozer', 'log_path')
cfg_shotgun_url = config_file.get('Shotgun', 'shotgun_url')
cfg_shotgun_script = config_file.get('Shotgun', 'shotgun_script_name')
cfg_shotgun_key = config_file.get('Shotgun', 'shotgun_key')
cfg_caches = config_file.get('Parameters', 'caches')
cfg_search_folders = config_file.get('Parameters', 'search_folders')
cfg_working_files = config_file.get('Parameters', 'working_files')
cfg_programs = config_file.get('Parameters', 'programs')
cfg_debug_logging = config_file.get('Debugger', 'debug_logging')
cfg_disabled_projects = config_file.get('Root', 'Disabled_Projects')
cfg_project_list = config_file.get('Root', 'project_list')
cfg_keep_count = config_file.get('Parameters', 'keep_count')
cfg_folder_override = config_file.get('Root', 'folder_override')
cfg_destroyer_path = config_file.get('BullGozer', 'destroyer_path')
prelog += 'Configuration variables set.\n'

osSystem = platform.system()
if osSystem == 'Windows':
    root_drive = cfg_win_drive
    root_drive = root_drive.replace('\\', '/')
    prelog += 'Operating System: %s\n' % cfg_win_drive
elif osSystem == 'Darwin':
    root_drive = cfg_mac_drive
    prelog += 'Operating System: %s\n' % cfg_mac_drive
else:
    root_drive = cfg_linux_drive
    prelog += 'Operating System: %s\n' % cfg_linux_drive

# root_drive = rebuild.check_root(root=root_drive)
prelog += 'Root drive set: %s\n' % root_drive

rebuild.check_log_path(root=root_drive, path=cfg_log_path)

logDate = str(time.strftime('%m%d%y'))
logTime = str(time.strftime('%H%M%S'))
logfile = "%s%sbullgozer_%s%s.log" % (root_drive, cfg_log_path, logDate, logTime)

shotgun_conf = {
    'url': 'https://%s' % cfg_shotgun_url,
    'name': cfg_shotgun_script,
    'key': cfg_shotgun_key
}


# ----------------------------------------------------------------------------------------------
# Setup Logging System
# ----------------------------------------------------------------------------------------------
def init_log(filename="BullGozer.log"):
    if cfg_debug_logging == 'True':
        level = logger.DEBUG
    else:
        level = logger.INFO
    try:
        logger.basicConfig(level=level, filename=filename, filemode='w+')
    except IOError, e:
        raise e
    return logger

logger = init_log(logfile)

logger.debug(prelog)
logger.info('BullGozer Started...')


# -----------------------------------------------------
# Signal Generator
# -----------------------------------------------------
class gozer_signal(QtCore.QObject):
    log_sig = QtCore.Signal(str)
    oh_shit_sig = QtCore.Signal(bool)
    files_sig = QtCore.Signal(list)
    file_sig = QtCore.Signal(str)
    folders_sig = QtCore.Signal(list)
    project_sig = QtCore.Signal(dict)
    log_dict_sig = QtCore.Signal(dict)
    roots_sig = QtCore.Signal(str)

    log_sig_debug = QtCore.Signal(str)
    files_sig_debug = QtCore.Signal(list)
    file_sig_debug = QtCore.Signal(str)
    folders_sig_debug = QtCore.Signal(list)
    log_dict_sig_debug = QtCore.Signal(dict)
    roots_sig_debug = QtCore.Signal(str)


# -----------------------------------------------------
# Threads
# -----------------------------------------------------
class gozer_output_stream(logger.StreamHandler):
    """
    rom_output_stream ports the logger to the UI output window
    """
    def emit(self, record):
        self.edit.appendPlainText(self.format(record))


class gozer_engine(QtCore.QThread):
    def __init__(self, parent=None):
        logger.debug('Gozer Engine Thread Initialized...')
        QtCore.QThread.__init__(self, parent)
        # super(gozer_engine, self).__init__(parent)
        self.sg = Shotgun(shotgun_conf['url'], shotgun_conf['name'], shotgun_conf['key'])

        # Globals
        self.signals = gozer_signal()
        self.caches = cfg_caches.split(',')
        self.working_files = cfg_working_files.split(',')
        self.search_folders = cfg_search_folders.split(',')
        self.programs = cfg_programs.split(',')
        self.disabled_projects = bool(cfg_disabled_projects)
        self.project_list = cfg_project_list.split(',')
        self.keep_count = int(cfg_keep_count)
        self.folder_override = cfg_folder_override
        self.destroyer_path = cfg_destroyer_path

        # Signals
        self.oh_shit_sig = self.signals.oh_shit_sig.connect(self.kill)

        # Storage Variables
        self.catalog = {}
        self.oh_shit = True

    def run(self, *args, **kwargs):
        self.seek()

    # def run(self):
    #     search_results = self.seek()

    def kill(self):
        self.oh_shit = False

    # --------------------------------------------------------------------------------------------------
    # Get Projects
    # --------------------------------------------------------------------------------------------------
    def get_projects(self):
        """
        get_projects returns a dictionary of projects organized by variables in the configuration
        :return: projects: dict[tank_name] = id
        """
        # logger.debug('get_projects has begun.')
        count = len(self.project_list)
        projects = {}
        if self.disabled_projects == 'True':
            disabled_projects = True
        else:
            disabled_projects = False
        if count > 1:
            project_list = self.project_list
        else:
            if not self.project_list[0]:
                project_list = None
            else:
                project_list = self.project_list

        # Need to add the Folder Override
        if disabled_projects and not project_list:
            # Here we start with anything not enabled on Shotgun.
            # logger.info('Only disabled projects is checked, and no project list is given.')
            # logger.debug('disabled TRUE')
            # logger.debug('project list: %s' % project_list)
            filters = [
                ['sg_status', 'is_not', 'active']
            ]
            fields = [
                'id',
                'tank_name'
            ]
        elif not disabled_projects and not project_list:
            # logger.debug('disabled FALSE')
            # logger.debug('project list: %s' % self.project_list)
            # logger.info('All projects will be searched')
            filters = []
            fields = [
                'id',
                'tank_name'
            ]
        elif project_list:
            # This search may have some issues.  Don't know if I can really search for multiple tank_names.
            # Works find for single projects.
            # logger.debug('disabled %s' % self.disabled_projects)
            # logger.debug('project list: %s' % self.project_list)
            # logger.info('A project list has been defined.  Only listed projects will be used.')
            filters = []
            for project in self.project_list:
                filters.append(['tank_name', 'is', project])
            fields = [
                'id',
                'tank_name'
            ]

        sg_projects = self.sg.find('Project', filters, fields)
        for proj in sg_projects:
            projects[proj['tank_name']] = proj['id']

        return projects

    def seek(self):
        """
        seek creates a file that must be loaded into the destory?
        The idea here is that you would run the seek, which would output a log, and also create a compressed
        list of items to be destroyed.  Sequences might be truncated to single lines, instead of listing every frame.
        the destroy file would be a json database of files and file paths to be erased.  Once approved, we would run
        destroy to activate the final process.
        :param root: The root drive for all futher processes
        :param projects: A dictionary of shotgun projects in {tank_name: id} form.
        :return: destroy_file: The file with an approved list of things to delete.
        """
        # logger.info('Begin seeking...')
        root = root_drive
        destroyer = {}
        while self.oh_shit:
            try:
                projects = self.get_projects()
            except Exception, e:
                self.signals.log_sig_debug.emit('Get Projects done fucked\' up! %s' % e)
            if root and projects:
                self.signals.log_sig_debug.emit('Root and Project are True')
                for project in projects:
                    if project:
                        path = root + '/' + project
                        if os.path.exists(path):
                            walk = os.walk(path)
                            for roots, dirs, files in walk:
                                roots = roots.replace('\\', '/')
                                self.signals.log_sig_debug.emit('-' * 125)
                                self.signals.roots_sig.emit('Search root: %s' % roots)

                                # Send to the
                                self.catalog[roots] = self.catalog_files(root=roots, files=files, project=project)

                                # Kill switch
                                if not self.oh_shit:
                                    break
                    destroyer[project] = self.catalog
                    # Kill Switch
                    if not self.oh_shit:
                        break

                self.oh_shit = False
                self.signals.log_sig.emit('=' * 125)

                # Build Report

                self.signals.log_sig.emit('REPORT:')
                grand_total = 0.0
                for _root, catalog in self.catalog.items():
                    self.signals.log_sig.emit('-' * 120)
                    self.signals.log_sig.emit('ROOT: %s' % _root)
                    caches = catalog['caches']
                    for x in caches:
                        if x['file']:
                            self.signals.log_sig.emit('CACHES:')
                            self.signals.log_sig.emit('%s | TOTAL FRAMES: %s | FRAME RANGE: %s' % (x['file'],
                                                                                                   x['total_frames'],
                                                                                                   x['frame_range']))
                            size = x['total_size']
                            size = float(size)
                            grand_total += size
                            get_total = self.file_size(size)
                            size = get_total['total']
                            size_label = get_total['label']
                            self.signals.log_sig.emit('Total Size: %f%s' % (size, size_label))
                    working_files = catalog['working_files']
                    for entry in working_files:
                        keep = entry['keep']
                        destroy = entry['destroy']
                        totals = entry['total_size']
                        totals = float(totals)
                        get_total = self.file_size(totals)
                        grand_total += totals
                        totals = get_total['total']
                        size_label = get_total['label']
                        self.signals.log_sig.emit('KEEP:')
                        for x in keep:
                            self.signals.log_sig.emit('%s' % x)

                        self.signals.log_sig.emit('DESTROY:')
                        for x in destroy:
                            self.signals.log_sig.emit('%s' % x)

                        self.signals.log_sig.emit('TOTALS: %f%s' % (totals, size_label))
                get_total = self.file_size(grand_total)
                grand_total = get_total['total']
                size_label = get_total['label']
                self.signals.log_sig.emit('GRAND TOTAL: %f%s' % (grand_total, size_label))
                self.build_destroyer(destroyer=destroyer)

    def build_destroyer(self, destroyer=None):
        if destroyer:
            destroyer_name = 'destroyer_%s%s.json' % (logDate, logTime)
            dpath = root_drive + cfg_destroyer_path
            if not os.path.isdir(dpath):
                os.makedirs(dpath)
            dpath += destroyer_name
            build = js.dumps(destroyer, sort_keys=True, indent=4, separators=(',', ': '))
            json_destroyer = open(dpath, 'w')
            json_destroyer.write(build)

    def file_size(self, amount=0):
        data = {}
        convert = str(int(amount))
        count = len(convert)
        if count > 3 and count <=6:
            base = 1024
            exponent = 1
            size_label = 'Kb'
        elif count > 6 and count <= 9:
            base = 1024
            exponent = 2
            size_label = 'Mb'
        elif count > 9 and count <= 12:
            base = 1024
            exponent = 2
            size_label = 'Gb'
        elif count > 12:
            base = 1024
            exponent = 2
            size_label = 'Tb'
        else:
            base = 1
            size_label = 'b'
            exponent = 1
        total = (amount/math.pow(base, exponent))
        data = {'total': total, 'label': size_label}
        return data

    def catalog_files(self, root=None, files=None, project=None):
        caches = []
        working_files = []
        if root and files:
            root = root.replace('\\', '/')
            for filename in files:
                self.signals.file_sig_debug.emit(filename)
                self.signals.log_sig_debug.emit('Checking for cache files...')
                check_path = root + '/' + filename
                check_path = check_path.replace('\\', '/')
                for ext in self.caches:
                    if str(filename).endswith(ext):
                        self.signals.log_sig_debug.emit('Cache Found!: %s' % filename)
                        sequence = self.get_sequence(filepath=check_path)
                        if sequence:
                            if sequence not in caches:
                                caches.append(sequence)
                for ext in self.working_files:
                    if str(filename).endswith(ext):
                        self.signals.log_sig.emit('Working file %s found! %s' % (ext, filename))
                        # Perhaps here is where I should check for existing entries in the dictionary
                        versions = self.get_versions(check_path)
                        if versions:
                            if versions not in working_files:
                                working_files.append(versions)
                        # Do something with the data
                # Kill switch
                if not self.oh_shit:
                    break
        return {'caches':caches, 'working_files': working_files, 'project': project}

    def get_sequence(self, filepath=None):
        sequence = None
        total_size = 0.0
        if filepath:
            try:
                path = os.path.dirname(filepath)
                path = path.replace('\\', '/')
                filename = os.path.basename(filepath)
                seqNum = re.findall(r'\d+', filename)[-1]
                seqPad = len(seqNum)
                splitname = filename.split(seqNum)
                basename = splitname[0]
                ext = splitname[-1]
                globname = basename
                for i in range(0, seqPad):
                    globname += '?'
                matched_names = glob.glob(path + '/' + globname + ext)
                matched_names = sorted(matched_names)
                for f in matched_names:
                    total_size += os.stat(f).st_size
                packed_name = globname.replace('?', '#') + ext
                frame_count = len(matched_names)
                seq_list = []
                for seq in matched_names:
                    get_nums = re.findall(r'\d+', seq)[-1]
                    seq_list.append(get_nums)
                frame_range = '[%s:%s]' % (seq_list[0], seq_list[-1])
                sequence = {'file': packed_name, 'padding': seqPad, 'total_frames': frame_count,
                            'frame_range': frame_range, 'total_size': total_size}
                return sequence
            except IndexError, e:
                pass
        return sequence

    def get_versions(self, filepath=None):
        vers = None
        all_versions = []
        keep = {}
        destroy = {}
        total_size = 0.0

        self.signals.log_sig_debug.emit('Getting Version Info...')
        if filepath:
            filepath = filepath.replace('\\', '/')
            try:
                path = os.path.dirname(filepath)
                filename = os.path.basename(filepath)
                versionNum = re.findall(r'\d+', filename)[-1]
                versionPad = len(versionNum)
                splitname = filename.split(versionNum)
                basename = splitname[0]
                ext = splitname[-1]
                globname = basename
                for i in range(0, versionPad):
                    globname += '?'
                versions = glob.glob(path + '/' + globname + ext)
                versions = sorted(versions)
                self.signals.log_sig_debug.emit('Discovered versions: %s' % versions)
                packed_name = globname.replace('?', '#') + ext
                self.signals.log_sig_debug.emit('Packed name: %s' % packed_name)
                version_count = len(versions)
                self.signals.log_sig_debug.emit('Version count: %s' % version_count)
                keep_count = version_count - self.keep_count + 1
                self.signals.log_sig_debug.emit('KEEP COUNT: %s' % keep_count)
                if version_count > keep_count:
                    self.signals.log_sig_debug.emit('Version Count: %s  Keep Count: %s' % (version_count, keep_count))
                    for v in versions:
                        get_version_nums = re.findall(r'\d+', v)[-1]
                        all_versions.append(get_version_nums)
                    self.signals.log_sig_debug.emit('All Versions: %s' % all_versions)
                    desc_versions = sorted(all_versions, reverse=True)
                    self.signals.log_sig_debug.emit('desc_version::: %s' % desc_versions)
                    # This needs to have the system from my notes.
                    while version_count >= keep_count:
                        vcount = version_count - 1
                        version_count -= 1
                        current = versions[vcount]
                        self.signals.log_sig_debug.emit('CURRENT: Current Version: %s' % current)
                        if os.path.exists(current):
                            keep[current] = os.stat(current).st_size
                            all_versions.remove(all_versions[vcount])
                            self.signals.log_sig_debug.emit('KEEP: %s Added to Keep' % current)
                            self.signals.log_sig_debug.emit('SIZE: %s' % os.stat(current).st_size)
                    for v in all_versions:
                        current = versions[all_versions.index(v)]
                        destroy[current] = os.stat(current).st_size
                        total_size += os.stat(current).st_size
                else:
                    for v in versions:
                        keep[v] = os.stat(v).st_size
                        self.signals.log_sig_debug.emit('KEEP: %s Added to Keep' % v)
                        self.signals.log_sig_debug.emit('SIZE: %s' % os.stat(v).st_size)
                return {'keep': keep, 'destroy': destroy, 'total_size': total_size}
            except IndexError, e:
                pass
        return {'keep': keep, 'destroy': destroy, 'total_size': total_size}

# ----------------------------------------------------------------------------------------------
# Start BullGozer
# ----------------------------------------------------------------------------------------------
class bullgozer(QtGui.QWidget):
    """
    The Main BullGozer UI setup.
    """
    def __init__(self, parent=None):
        # Preliminary things
        QtGui.QWidget.__init__(self, parent)
        self.gozer_engine = gozer_engine()

        self.ui = bgi.Ui_Form()
        self.ui.setupUi(self)

        self.gozer_stream = gozer_output_stream()
        self.gozer_stream.edit = self.ui.output_log
        logger.getLogger().addHandler(self.gozer_stream)

        # Connect Logger Signals
        self.gozer_engine.signals.files_sig.connect(self.update_log)
        self.gozer_engine.signals.file_sig.connect(self.update_log)
        self.gozer_engine.signals.folders_sig.connect(self.update_log)
        self.gozer_engine.signals.roots_sig.connect(self.update_log)
        self.gozer_engine.signals.log_sig.connect(self.update_log)
        self.gozer_engine.signals.files_sig_debug.connect(self.update_log_debug)
        self.gozer_engine.signals.file_sig_debug.connect(self.update_log_debug)
        self.gozer_engine.signals.folders_sig_debug.connect(self.update_log_debug)
        self.gozer_engine.signals.roots_sig_debug.connect(self.update_log_debug)
        self.gozer_engine.signals.log_sig_debug.connect(self.update_log_debug)
        self.gozer_engine.signals.log_dict_sig_debug.connect(self.update_log_debug)
        self.gozer_engine.signals.log_dict_sig.connect(self.update_log)

        self.ui.seek_btn.clicked.connect(self.start_seeking)
        self.ui.oh_shit_btn.clicked.connect(self.oh_shit)

    def update_log(self, message=None):
        if message:
            logger.info(message)

    def update_log_debug(self, message=None):
        if message:
            logger.debug(message)

    def oh_shit(self):
        # These could both be replaced with signals, thus eliminating the direct call
        # self.gozer_engine.oh_shit = True
        if self.gozer_engine.isRunning():
            self.gozer_engine.oh_shit = False
            self.gozer_engine.quit()

    def start_seeking(self):
        if not self.gozer_engine.isRunning():
            self.gozer_engine.oh_shit = True
            # self.signal.load_sig.emit('clicked()')
            self.gozer_engine.start()
            logger.info('Search Initiated!')


if __name__=='__main__':
    # Set up the app
    app = QtGui.QApplication(sys.argv)
    # Run ts_main hidden
    window = bullgozer()
    window.show()
    # window.hide()
    sys.exit(app.exec_())
