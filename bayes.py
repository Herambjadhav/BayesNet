import sys
from decimal import Decimal

nodeOrder = []

# build bayes network
def buildBayesNet(lines):
    bayesNet = {}
    node = {}
    prob = {}
    for line in lines:
        line = line.strip('\n')
        # re-initialze for new node
        if line == '***':
            node = {}
            prob = {}

        # initialize new node and its parents
        elif line[0].isalpha():
            vars = line.split('|')
            key = vars[0].strip(' ')
            bayesNet[key] = node
            nodeOrder.append(key)
            parents = []
            if len(vars) > 1:
                parentArr = vars[1].lstrip(' ').split(' ')
                for parent in parentArr:
                    parents.append(parent)
            node['parents'] = parents
            node['prob'] = prob

        # create list of probabilities
        else:
            probability = line.split(' ')
            binaryString = ""
            if len(probability) > 1:
                for p in probability[1:]:
                    if p == '+':
                        binaryString += '0'
                    else:
                        binaryString += '1'
                index1 = '0'+binaryString
                index2 = '1'+binaryString
                prob[index1] = float(probability[0])
                prob[index2] = float(1 - Decimal(probability[0]))
            else:
                prob['0'] = float(probability[0])
                prob['1'] = float(1 - Decimal(probability[0]))

    return bayesNet

# formulate queries
def extractQueries(lines, numberOfQueries):
    queries = []
    for line in lines[1: numberOfQueries + 1]:
        # check for conditional probability
        query = {}
        line = line.strip('\n').strip('P(').replace(")", "").replace(" ", "")

        #print 'line = ', line
        if '|' in line:
            query['isConditional'] = True
            arr = line.split('|')

            # query vars
            variables = []

            arr1 = arr[0].split(',')
            for str in arr1:
                strArr = str.split('=')
                vals = {}
                vals['key'] = strArr[0]
                vals['value'] = strArr[1]
                variables.append(vals)

            # query evidence
            evidence = []

            arr2 = arr[1].split(',')
            for str in arr2:
                strArr = str.split('=')
                eviVals = {}
                eviVals['key'] = strArr[0]
                eviVals['value'] = strArr[1]
                evidence.append(eviVals)

            query['variables'] = variables
            query['evidence'] = evidence


        else:
            query['isConditional'] = False
            arr = line.split(',')

            # query vars
            variables = []

            for str in arr:
                strArr = str.split('=')
                vals = {}
                vals['key'] = strArr[0]
                vals['value'] = strArr[1]
                variables.append(vals)

            query['variables'] = variables

        queries.append(query)

    return queries

def calculateProbability(keyValueList, bayesNet):
    probablitiy = 1
    for key in nodeOrder:
        #print 'key : ', key
        binaryString = keyValueList[key]
        node = bayesNet[key]
        parents = node['parents']
        prob = node['prob']

        for parent in parents:
            binaryString += keyValueList[parent]

        probablitiy = probablitiy * prob[binaryString]
        #print 'probability : ', probablitiy

    return probablitiy

# enuerate-all
def enumerate_all(hiddenVarList, keyValueList, bayesNet):
    numberOfBits = len(hiddenVarList)
    n = pow(2, numberOfBits)
    # print n

    sum = 0
    for i in range(0, n):
        i = int(str(bin(i))[2:])
        bitList = list('{0:0{width}}'.format(i, width=numberOfBits))
        # print bitList

        counter = 0
        for key in hiddenVarList:
            keyValueList[key] = bitList[counter]
            counter += 1

        # print 'keyValueList: ', keyValueList

        sum = sum + calculateProbability(keyValueList, bayesNet)
        # print 'sum :  ', sum

    return sum

# enumerate-ask
def enumerate_ask(bayesNet, query):

    if query['isConditional']:
        # calculate probability of variables
        varList = []
        keyValueList = {}

        variables = query['variables']
        for val in variables:
            varList.append(val['key'])
            if val['value'] == '+':
                keyValueList[val['key']] = '0'
            else:
                keyValueList[val['key']] = '1'

        evidence = query['evidence']
        for val in evidence:
            varList.append(val['key'])
            if val['value'] == '+':
                keyValueList[val['key']] = '0'
            else:
                keyValueList[val['key']] = '1'

        #print varList
        hiddenVarList = list(set(nodeOrder) - set(varList))
        #print 'hidden variables : ', hiddenVarList

        conditionalProb = enumerate_all(hiddenVarList, keyValueList, bayesNet)
        #print 'conditionalProb : ', conditionalProb

        # calculate probability for evidence or alpha
        varList = []
        keyValueList = {}

        for val in evidence:
            varList.append(val['key'])
            if val['value'] == '+':
                keyValueList[val['key']] = '0'
            else:
                keyValueList[val['key']] = '1'

        hiddenVarList = list(set(nodeOrder) - set(varList))
        #print 'hidden variables : ', hiddenVarList

        evidenceProb = enumerate_all(hiddenVarList, keyValueList, bayesNet)
        #print 'evidenceProb : ', evidenceProb

        return conditionalProb/evidenceProb

    else:
        varList = []
        variables = query['variables']
        keyValueList = {}
        for val in variables:
            varList.append(val['key'])
            if val['value'] == '+':
                keyValueList[val['key']] = '0'
            else:
                keyValueList[val['key']] = '1'

        hiddenVarList = list(set(nodeOrder) - set(varList))
        #print 'hidden variables : ', hiddenVarList

        return enumerate_all(hiddenVarList, keyValueList, bayesNet)

    return 0


print 'Argument count : ', len(sys.argv)
# exit if file name is not provided as command line argument
if len(sys.argv) != 2:
    print 'Please input file name as command line argument'
    exit(0)

fileName = sys.argv[1]
print 'File name : ', sys.argv[1]

# read all lines of file
fileHandler = open(fileName,"r")
lines = fileHandler.readlines()
fileHandler.close()

numberOfQueries = int(lines[0])
print 'Number of Queries : ',numberOfQueries

# extract queries
queries = extractQueries(lines, numberOfQueries)

# create network
bayesNet = buildBayesNet(lines[numberOfQueries + 1:])
print 'Network : ', bayesNet

# for query in queries:
#     print 'Query : ', query

print 'nodeOrder = ', nodeOrder

# enumerate queries
fileHandler = open("output.txt","w")
for query in queries[:-1]:
    probablitiy = enumerate_ask(bayesNet, query)
    fileHandler.write("%s\n" % ('{0:.2f}'.format(round(probablitiy, 2))))
    #print 'probablitiy : ', '{0:.2f}'.format(round(probablitiy, 2))
    print 'probablitiy : ', probablitiy

probablitiy = enumerate_ask(bayesNet, queries[-1])
fileHandler.write("%s" % ('{0:.2f}'.format(round(probablitiy, 2))))
#print 'probablitiy : ', '{0:.2f}'.format(round(probablitiy, 2))
print 'probablitiy : ', probablitiy

fileHandler.close()