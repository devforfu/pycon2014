import time
import threading


def follow(thefile):
    thefile.seek(0, 2)  # go to the end of the file
    count = 0

    while True:
        line = thefile.readline()
        if not line:
            if count > 50: break
            time.sleep(0.1)
            count += 1
            continue
        count = 0
        yield line

    print 'Stop following...'


lock = threading.Lock()
def server():
    import random
    decoder = {200: 'OK', 404: 'NOT FOUND', 503: 'BAD REQUEST'}
    messages = [200, 200, 404, 503, 200]
    for _ in range(20):
        code = random.choice(messages)
        with lock:
            with open('log', 'a') as f:
                f.write('[%s] %s' % (code, decoder[code]))
        time.sleep(1.0)
    print('Server work ended...')


if __name__ == '__main__':
    server_thread = threading.Thread(target=server, args=())
    server_thread.start()
    time.sleep(0.1)
    logfile = open('log')
    for line in follow(logfile):
        print line
    server_thread.join()
    print('The end!')

