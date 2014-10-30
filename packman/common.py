import logger
from common import do

import os

lgr = logger.init()


class Handler():
    """common class to handle files and directories
    """

    # def __init__(self, context):
    #     self.context = context

    def find_in_dir(self, dir, pattern, sudo=True):
        """
        finds file/s in a dir

        :param string dir: directory to look in
        :param string patten: what to look for
        :rtype: ``stdout`` `string` if found, else `None`
        """
        lgr.debug('looking for {0} in {1}'.format(pattern, dir))
        x = do('find {0} -iname "{1}" -exec echo {{}} \;'
               .format(dir, pattern), capture=True, sudo=sudo)
        return x.stdout if x.succeeded else None

    def is_dir(self, dir):
        """checks if a directory exists

        :param string dir: directory to check
        :rtype: `bool`
        """
        lgr.debug('checking if {0} exists'.format(dir))
        if os.path.isdir(dir):
            lgr.debug('{0} exists'.format(dir))
            return True
        else:
            lgr.debug('{0} does not exist'.format(dir))
            return False

    def is_file(self, file):
        """checks if a file exists

        :param string file: file to check
        :rtype: `bool`
        """
        lgr.debug('checking if {0} exists'.format(file))
        if os.path.isfile(file):
            lgr.debug('{0} exists'.format(file))
            return True
        else:
            lgr.debug('{0} does not exist'.format(file))
            return False

    def touch(self, file, sudo=True):
        """creates a file

        :param string file: file to touch
        """

        cmd = 'touch {0}'.format(file)
        lgr.debug('creating file {0}'.format(file))
        return do(cmd, sudo=sudo)

    def mkdir(self, dir, sudo=True):
        """creates (recursively) a directory

        :param string dir: directory to create
        """
        lgr.debug('creating directory {0}'.format(dir))
        return do('mkdir -p {0}'.format(dir), sudo=sudo) \
            if not os.path.isdir(dir) \
            else lgr.debug('directory already exists, skipping.')
        return False

    def rmdir(self, dir, sudo=True):
        """deletes a directory

        :param string dir: directory to remove
        """
        lgr.debug('attempting to remove directory {0}'.format(dir))
        return do('rm -rf {0}'.format(dir), sudo=sudo) \
            if os.path.isdir(dir) else lgr.debug('dir doesn\'t exist')
        return False

    # TODO: (IMPRV) handle multiple files differently
    def rm(self, file, sudo=True):
        """deletes a file or a set of files

        :param string file(s): file(s) to remove
        """
        lgr.debug('removing files {0}'.format(file))
        return do('rm {0}'.format(file), sudo=sudo) if os.path.isfile(file) \
            else lgr.debug('file(s) do(es)n\'t exist')
        return False

    def cp(self, src, dst, recurse=True, sudo=True):
        """copies (recuresively or not) files or directories

        :param string src: source to copy
        :param string dst: destination to copy to
        :param bool recurse: should the copying process be recursive?
        """
        lgr.debug('copying {0} to {1}'.format(src, dst))
        return do('cp -R {0} {1}'.format(src, dst), sudo=sudo) if recurse \
            else do('cp {0} {1}'.format(src, dst), sudo=sudo)

    def mv(self, src, dst, sudo=True):
        """moves files or directories

        :param string src: source to copy
        :param string dst: destination to copy to
        """
        lgr.debug('moving {0} to {1}'.format(src, dst))
        return do('mv {0} {1}'.format(src, dst), sudo=sudo)

    def tar(self, chdir, output_file, input_path, opts='zvf', sudo=True):
        """tars an input file or directory

        :param string chdir: change to this dir before archiving
        :param string output_file: tar output file path
        :param string input: input path to create tar from
        :param string opts: tar opts
        """
        lgr.debug('tar-ing {0}'.format(output_file))
        return do('tar -C {0} -c{1} {2} {3}'.format(
            chdir, opts, output_file, input_path), sudo=sudo)

    def untar(self, chdir, input_file, opts='zvf', strip=0, sudo=True):
        """untars a file

        :param string chdir: change to this dir before extracting
        :param string input_file: file to untar
        :param string opts: tar opts
        """
        lgr.debug('untar-ing {0}'.format(input_file))
        return do('tar -C {0} -x{1} {2} --strip={3}'.format(
            chdir, opts, input_file, strip), sudo=sudo)
