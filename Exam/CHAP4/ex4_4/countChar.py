#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from myThread import MyThread as Thread
import os


def countChar(file, char, start, step):
    with open(file) as f:
        f.seek(start)
        txt = f.read(step)
    return txt.count(char)


def main():
    file = input("filePath:")
    char = input("Char:")
    nThread = int(input("Number of threads:"))

    file_size = os.path.getsize(file)
    step = file_size // nThread

    threads = []

    for i in range(nThread):
        threads.append(Thread(countChar, (file, char, 0+i*step, step)))

    for i in range(nThread):
        threads[i].start()

    for i in range(nThread):
        threads[i].join()

    result = 0

    for i in range(nThread):
        result += threads[i].getResult()

    print("count :", result)

if __name__ == '__main__':
    main()
