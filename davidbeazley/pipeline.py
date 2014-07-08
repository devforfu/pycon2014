import time
import threading
from follow import follow, server


def grep(pattern, lines):
    for line in lines:
        if pattern in line:
            yield line


if __name__ == '__main__':
    server_thread = threading.Thread(target=server, args=())
    server_thread.start()
    time.sleep(0.1)

    # Set up a processing pipeline (something like: tail -f | grep)
    logfile = open('log')
    loglines = follow(logfile)
    pylines = grep('python', loglines)

    for line in pylines:
        print(line)

    print('The End!')
