import pyradamsa, os

class GenerateTests():

    def __init__(self, pathTest):
        self.path = pathTest
        self.radamsa = pyradamsa.Radamsa()


    def buildTest(self, testNumber=1, writeToFiles=False):
        files = os.listdir(self.path)
        if not os.path.isdir(self.path + "/fuzz_tests"):
            os.makedirs(self.path + "/fuzz_tests")

        tests = []
        for f in files:
            if os.path.isfile(self.path + f):
                with open(self.path + f, mode='rb') as c:
                    for i in range(0, testNumber):
                        data = self.radamsa.fuzz(c.read(), max_mut=10)
                        if writeToFiles:
                            with open(self.path + "/fuzz_tests/" + "fuzz_case_" + str(i) + ".txt", mode='wb') as w:
                                w.write(data)
                        
                        tests.append(data)
        return tests


if __name__ == "__main__":
    path = "./test_case/connect/"
    gTests = GenerateTests(path)

    gTests.buildTest(20)
