import sys
import os
from collections import defaultdict


# https://www.geeksforgeeks.org/detect-cycle-in-a-graph/
class Graph:
    def __init__(self, vertices):
        self.graph = defaultdict(list)
        self.V = vertices

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def deleteVertice(self, v):
        del self.graph[v]
        for key, value in self.graph.items():
            self.graph[key] = [item for item in value if item != v]

    def isCyclicUtil(self, v, visited, recStack):

        # Mark current node as visited and
        # adds to recursion stack
        visited[v] = True
        recStack[v] = True

        # Recur for all neighbours
        # if any neighbour is visited and in
        # recStack then graph is cyclic
        for neighbour in self.graph[v]:
            if visited[neighbour] == False:
                if self.isCyclicUtil(neighbour, visited, recStack) == True:
                    return True
            elif recStack[neighbour] == True:
                return True

        # The node needs to be popped from
        # recursion stack before function ends
        recStack[v] = False
        return False

    # Returns true if graph is cyclic else false
    def isCyclic(self):
        visited = [False] * (self.V + 1)
        recStack = [False] * (self.V + 1)
        for node in range(self.V):
            if visited[node] == False:
                if self.isCyclicUtil(node, visited, recStack) == True:
                    return True
        return False


def task_one(filename):
    # 1. Read the schedule from the schedule file
    lines = open(filename, 'r').readlines()
    lines = [line.strip() for line in lines]
    transactions = set([int(line.split()[0][1:]) for line in lines])
    print("Schedule involveds the following transactions: [%s]" % (','.join(str(item) for item in transactions)))

    # 2. Construct the precedence graph described by the schedule
    g = Graph(len(transactions))
    last_commit = defaultdict(int, {k: -1 for k in transactions})
    uncommit = transactions
    for i in range(len(lines)):
        line = lines[i]
        op = line[0]
        transaction = int(line.split()[0][1:])
        if op == 'c':
            # remove from graph
            g.deleteVertice(transaction)
            last_commit[transaction] = i
            if transaction in uncommit:
                uncommit.remove(transaction)
        else:
            if transaction not in uncommit and op == 'w':
                uncommit.add(transaction)
            variable = line.split()[1]
            for j in range(i):
                line_prev = lines[j]
                op_prev = line_prev[0]
                transaction_prev = int(line_prev.split()[0][1:])
                if op_prev == 'c':
                    continue
                variable_prev = line_prev.split()[1]
                if variable_prev == variable and transaction_prev != transaction and last_commit[transaction_prev] < j:
                    if op == 'w':
                        g.addEdge(transaction_prev, transaction)
                    elif op == 'r':
                        if op_prev == 'w':
                            g.addEdge(transaction_prev, transaction)
        if g.isCyclic() == 1:
            print("Instruction %d (%s) crated a conflict cycle." % (i+1, line))
            print("These are the transactions participating in cycles: ")
            break
    print("The schedule is conflict serializable.")
    print("The remaining uncommitted transactions are serializable to this order: []")





    return 0


def task_two(filename, number, lowerbound, upperbound):
    return 0


if __name__ == '__main__':
    fn = sys.argv[1]
    if os.path.exists(fn):
        if fn.endswith('.sch'):
            task_one(fn)
        elif fn.endswith('.set'):
            num = int(sys.argv[2])
            lb = int(sys.argv[3].split('-')[0])
            ub = int(sys.argv[3].split('-')[1])
            task_two(fn, num, lb, ub)
    else:
        print("File does not exist!")
