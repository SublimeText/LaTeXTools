from subprocess import Popen, PIPE

def kpsewhich(filename, file_format=None):
    try:
        if file_format is None or type(file_format) != type(''):
            p = Popen(['kpsewhich', filename], stdout=PIPE, stdin=PIPE)
        else:
            p = Popen(['kpsewhich', '-format=%s' % (file_format), filename], stdout=PIPE, stdin=PIPE)
        path = p.communicate()[0].rstrip()
        if p.returncode == 0:
            return path
    except OSError:
        # i.e., kpsewhich cannot be found
        pass
    return None
