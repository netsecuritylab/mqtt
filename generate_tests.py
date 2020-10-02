import pyradamsa, os

class GenerateTests():

    def __init__(self, pathTest):
        self.path = pathTest
        self.radamsa = pyradamsa.Radamsa()


    def buildTest(self, testNumber=1):
        files = os.listdir(self.path)
        if not os.path.isdir(path + "/fuzz_tests"):
            os.makedirs(path + "/fuzz_tests")
        for f in files:
            if os.path.isfile(path + f):
                with open(path + f, mode='rb') as c:
                    for i in range(0, testNumber):
                        with open(path + "/fuzz_tests/" + "fuzz_case_" + str(i) + ".txt", mode='wb') as w:
                            w.write(self.radamsa.fuzz(c.read(), max_mut=10))



if __name__ == "__main__":
    path = "./test_case/connect/"
    gTests = GenerateTests(path)

    gTests.buildTest(20)
