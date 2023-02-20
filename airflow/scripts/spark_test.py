from pyspark import SparkContext
logFilepath = "file:////home/hduser/wordcount.txt"  
sc = SparkContext("local", "first app")
logData = sc.textFile(logFilepath).cache()
numAs = logData.filter(lambda s: 'a' in s).count()
numBs = logData.filter(lambda s: 'b' in s).count()
print("Lines with a: %i, lines with b: %i" % (numAs, numBs))