def custom_popen(cmd):
    """Disconnect cmd from parent fds, read only from stdout."""

    # needed for py2exe
    creationflags = 0
    if sys.platform == 'win32':
        creationflags = 0x08000000 # CREATE_NO_WINDOW

    # run command
    p = Popen(cmd, bufsize = 0, stdout = PIPE, stdin = PIPE, stderr = STDOUT,
              creationflags = creationflags)
    return p