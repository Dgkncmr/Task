import sys
import time
import threading
from threading import Lock
from enum import Enum, auto
from random import *

SleepTime = 0.5
randomVectorSize = 10000
randomLimit = 1000
SleepTimeMutex = Lock()


class ThreadSafeQueue():
    def __init__(self, name, maxSize):
        self.__mutex = Lock()
        self.__name = name
        self.__maxSize = maxSize
        self.__ownList = list()

    def getName(self):
        try:
            name = str()
            name = self.__name
            return name
        except:
            return ""

    def getMaxSize(self):
        try:
            maxSize = int()
            self.__mutex.acquire()
            maxSize = self.__maxSize
            self.__mutex.release()
            return maxSize
        except:
            return 0

    def appendList(self, newList):
        try:
            if self.getSize() < self.getMaxSize():
                self.__mutex.acquire()
                self.__ownList.append(newList)
                self.__mutex.release()
            else:
                print(self.getName(), "Queue Reach Max Size, Append Error")
        except:
            pass

    def popElement(self):
        try:
            if self.getSize() > 0:
                newListe = list()
                self.__mutex.acquire()
                newListe = self.__ownList.pop().copy()
                self.__mutex.release()
                return newListe
            else:
                return list()
        except:
            return list()

    def getSize(self):
        try:
            currentLength = int()
            self.__mutex.acquire()
            currentLength = len(self.__ownList)
            self.__mutex.release()
            return currentLength
        except:
            return 0


class SORT_TYPE(Enum):
    BUBBLE = auto()
    SELECTION = auto()
    QUICK = auto()


class ifSortEngine():
    def __init__(self, SORT_TYPE, mInputQueue):
        self.__isOk = False
        if isinstance(mInputQueue, ThreadSafeQueue):
            self.__mInputQueue = mInputQueue
            self.__isOk = True
        else:
            print("Err: Input list is empty!")
        self.__SORT_TYPE = SORT_TYPE
        self.__memberThread = threading.Thread(target=self.__process)

    def Start(self):
        if self.__isOk:
            self.__memberThread.start()
        else:
            print("Thread can not start. Input list empty")

    def __process(self):
        while True:
            try:
                newList = self.__mInputQueue.popElement()
                if self.__SORT_TYPE == SORT_TYPE.QUICK:
                    quickSortStartTime = time.time()
                    self.__quickSort(newList, 0, len(newList) - 1)
                    quickSortEndTime = time.time()
                    print("QuickSort :: ", quickSortEndTime - quickSortStartTime)
                elif self.__SORT_TYPE == SORT_TYPE.BUBBLE:
                    bubbleSortStartTime = time.time()
                    self.__bubbleSort(newList)
                    bubbleSortEndTime = time.time()
                    print("Bubble :: ", bubbleSortEndTime - bubbleSortStartTime)

                elif self.__SORT_TYPE == SORT_TYPE.SELECTION:
                    selectionSortStartTime = time.time()
                    self.__selectionSort(newList)
                    selectionSortEndTime = time.time()
                    print("Selection :: ", selectionSortEndTime - selectionSortStartTime)
                else:
                    print("UNKNOWN TYPE")
            except IndexError:
                pass

    def __bubbleSort(self, sortList):
        for i in range(0, len(sortList) - 1):
            for j in range(0, len(sortList) - 1):
                if sortList[j] > sortList[i]:
                    sortList[j - 1], sortList[j] = sortList[j], sortList[j - 1]
        return sortList

    def __selectionSort(self, sortList):
        for i in range(0, len(sortList) - 1):
            minIndex = i
            for j in range(i + 1, len(sortList)):
                if sortList[j] < sortList[minIndex]:
                    minIndex = j
            sortList[minIndex], sortList[i] = sortList[i], sortList[minIndex]
        return sortList

    def __quickSort(self, sortList, low, high):
        if low < high:
            index = self.__partition(sortList, low, high)
            self.__quickSort(sortList, low, index - 1)
            self.__quickSort(sortList, index + 1, high)
        return sortList

    def __partition(self, sortList, low, high):
        pivot = sortList[high]
        i = low - 1
        for j in range(low, high):
            if sortList[j] < pivot:
                i += 1
                (sortList[i], sortList[j]) = (sortList[j], sortList[i])
        (sortList[i + 1], sortList[high]) = (sortList[high], sortList[i + 1])
        return i + 1


def startObserver(*outputList):
    isAllAvailable = True
    for i in outputList:
        if not isinstance(i, ThreadSafeQueue):
            isAllAvailable = False
    if isAllAvailable:
        observerThread = threading.Thread(target=Observe, args=(outputList,))
        observerThread.start()
        print("Start Observe Thread")


def Observe(*outputList):
    global SleepTime
    sizeList = list()

    while True:
        for i in outputList:
            print(i.getName(), "Size :: ", i.getSize())
            sizeList.append(i.getSize())
        if analyseFps(sizeList):
            SleepTimeMutex.acquire()
            SleepTime += 0.1
            print("New sleep time :: ", SleepTime)
            SleepTimeMutex.release()
        else:
            SleepTimeMutex.acquire()
            SleepTime -= 0.1
            print("New sleep time :: ", SleepTime)
            SleepTimeMutex.release()

        print("---------------------")
        time.sleep(1)


def analyseFps(sizeList):
    if max(sizeList) > 0:
        return True
    else:
        return False


def startRandomGenerator(*outputlist):
    isAllAvailable = True
    for i in outputlist:
        if not isinstance(i, ThreadSafeQueue):
            isAllAvailable = False
    if isAllAvailable:
        print("Start Generate Random Vector Thread")
        generateRandomVectorThread = threading.Thread(target=generateRandomVector,
                                                      args=(outputlist,))
        generateRandomVectorThread.start()


def generateRandomVector(*outputList):
    while True:
        for i in range(0, randomLimit):
            value = randint(1, randomVectorSize)
            randomList.append(value)

        for choosenList in outputList:
            choosenList.appendList(randomList)

        global SleepTimeMutex
        memberSleepTime = float()
        SleepTimeMutex.acquire()
        memberSleepTime = SleepTime
        SleepTimeMutex.release()
        time.sleep(memberSleepTime)


if __name__ == "__main__":
    bubbleSortQueue = ThreadSafeQueue("Bubble", 500)
    quickSortQueue = ThreadSafeQueue("Quick", 500)
    selectionSortQueue = ThreadSafeQueue("Selection", 500)
    startObserver(bubbleSortQueue, quickSortQueue, selectionSortQueue)
    startRandomGenerator(bubbleSortQueue, quickSortQueue, selectionSortQueue)

    bubbleSort = ifSortEngine(SORT_TYPE.BUBBLE, bubbleSortQueue)
    quickSort = ifSortEngine(SORT_TYPE.QUICK, quickSortQueue)
    selectionSort = ifSortEngine(SORT_TYPE.SELECTION, selectionSortQueue)

    bubbleSort.Start()
    quickSort.Start()
    selectionSort.Start()
