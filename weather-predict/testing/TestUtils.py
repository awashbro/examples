
def outResult(testResult, outString):

    if (testResult):
        print "\033[92m\033[1m[OK]\033[0m " + outString
        fails = 0
    else:
        print "\033[91m\033[1m[FAILED]\033[0m " + outString
        fails = 1

    return fails
