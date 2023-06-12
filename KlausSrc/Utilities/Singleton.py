import logging
import os
import sys
import tempfile
import __main__

try:
    import lib_programname
except ImportError:
    lib_programname = None

if sys.platform != "win32":
    import fcntl


class SingletonException(Exception):
    def __init__(self, message="Another instance is already running", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class Singleton:
    def __init__(self, lockfile=""):
        self.initialized = False

        if lockfile:  # if lockfile specified, set it
            self.lockfile = lockfile
        else:
            if lib_programname:
                self.basename = os.path.splitext(os.path.basename(lib_programname.get_path_executed_script()))[0]
            else:  # if the lib_programname can't be imported for some reason, just set to whatever __main__.__file__ is
                self.basename = os.path.splitext(os.path.basename(__main__.__file__))[0]
            self.lockfile = self.basename+".lock"

        logging.debug(f"Lockfile: {self.lockfile}")

    def __enter__(self):
        if sys.platform == "win32":
            try:
                if os.path.exists(self.lockfile) and os.path.isfile(self.lockfile):
                        os.remove(self.lockfile)
                # create file if it doesn't exist but error if it does
                self.fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL)
            except PermissionError as e:
                logging.error("Another instance is running, quitting")
                raise SingletonException from None
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                raise
        else:
            try:
                self.file = open(self.lockfile, "w")
                fcntl.lockf(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)  # try to acquire exlusive, nonblocking lock
            except IOError as e:
                logging.warning("Another instance is running, quitting")
                raise SingletonException
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                raise

        self.initialized = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        if not self.initialized:
            return

        if exc_val is not None:
            if exc_val.code == 0: #SystemExit 0, which is normal system exit
                pass
            else:
                logging.warning(f"Error encountered: Type:{exc_type}, val:{exc_val}, tb:{exc_tb}")

        try:
            if sys.platform == "win32":
                if hasattr(self, 'fd'):  # checks if a file descriptor has been made
                    os.close(self.fd)
                    os.remove(self.lockfile)
            else:
                fcntl.lockf(self.file, fcntl.LOCK_UN)  # unlocks
                if os.path.exists(self.lockfile) and os.path.isfile(self.lockfile):
                    os.remove(self.lockfile)
        except Exception as e:
            logging.warning("Error encountered while unlocking:{e}")
            sys.exit(-1)  # unclean exit
