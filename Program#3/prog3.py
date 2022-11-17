"""
Course: CSC 560 - Database Systems Implementation, Fall 2022
Instructor: Dr. McCann

Assignment: Program #3 - Transaction Schedule Conflict Serializability
Due Date: Nov 17th, 2022, at the beginning of class

Author: Zirui Huang

Description:
    This script is related to ideas of a transaction of sometimes–conflicting operations, serial schedules of
transactions, schedules of interleaved transaction operations, conflict serializability, precedence
(a.k.a. serialization) graphs, and topological sorting. This assignment combines these ideas in two related but
distinct ways, respectively when the file specified in the argument is a .sch file or a .set file.

Data:
    The expected command–line arguments are given above with the descriptions of each task. To illustrate:
    Task 1’s execution is enabled via a path/filename command–line argument with a .sch extension, such as
(assuming Python3). For example:

    python3 prog3.py /home/johndoe/cs560/program3/data/2xact.sch

    Task 2’s execution is enabled via a sequence of three arguments: A path/filename of the .set file, a non–
negative integer, and a positive integer range a − b, where a ≤ b. For example:

    python3 prog3.py collection9.set 10000 1-1

Output:
    For Task 1, output the following, using an output format of your design:
    (a) A list of the IDs of the transactions in the schedule file, in ascending order by ID; and
    (b) either a message stating that the schedule is not conflict serializable and the IDs of the transactions in the
    detected cycle, or a message stating that the schedule is conflict serializable and a topological ordering of the
    conflict serializable schedule.
    For Task 2, output, again using an output format of your design,
    (a) the command–line arguments,
    (b) the quantity of schedules that were conflict serializable, and
    (c) the percentage of schedules that were conflict serializable.


Operational requirements: Python 3.8.10
External libraries: None

"""
import sys
import os
from collections import defaultdict
import random
import re

"""
Class "Graph" is used to represent a precedence graph described by a schedule S.
This graph consists of a pair G = (V, E), where V is a set of vertices and E is a set of edges. 
The set of vertices consists of all the transactions participating in the schedule. 
The set of edges consists of all edges T_i → T_j for which one of three conditions holds:
    1. T_i executes write(Q) before T_j executes read(Q).
    2. T_i executes read(Q) before T_j executes write(Q).
    3. T_i executes write(Q) before T_j executes write(Q).

reference: https://www.geeksforgeeks.org/detect-cycle-in-a-graph/
           https://www.geeksforgeeks.org/python-program-for-topological-sorting/
"""

class Graph:
    def __init__(self, vertices):
        """
        Class Graph Instructor.
        :param vertices: the maximum number of vertices in the graph
        """
        self.graph = defaultdict(list)
        self.V = vertices

    def addEdge(self, u, v):
        """
        This function is to add edge from vertex u to vertex v
        :param u: the end vertex that the new added edge is connected from
        :param v: the end vertex that the new added edge is connected to
        :return: None
        """
        if v not in self.graph[u]:
            self.graph[u].append(v)

    def deleteEdgesConnectedTo(self, v):
        """
        This function is to delete all edges connected with vertex v
        :param v: the related vertex
        :return: None
        """
        self.graph[v] = []
        for key, value in self.graph.items():
            self.graph[key] = [item for item in value if item != v]

    def isCyclicUtil(self, v, visited, recStack):
        """
        This function is to check if cycle(s) exists from vertex v
        :param v: vertex
        :param visited: flags if nodes are visited
        :param recStack: recursion stack
        :return: boolean value
        """

        # Mark current node as visited and adds to recursion stack
        visited[v] = True
        recStack[v] = True

        # Recur for all neighbours if any neighbour is visited and in recStack then graph is cyclic
        for neighbour in self.graph[v]:
            if visited[neighbour] == False:
                if self.isCyclicUtil(neighbour, visited, recStack) == True:
                    return True
            elif recStack[neighbour] == True:
                return True

        # The node needs to be popped from recursion stack before function ends
        recStack[v] = False
        return False

    # Returns true if graph is cyclic else false
    def isCyclic(self):
        """
        This function is to check if a graph has cycle(s)
        :return: boolean value
        """
        visited = [False] * (self.V + 1)
        recStack = [False] * (self.V + 1)
        for node in range(self.V):
            if visited[node] == False:
                if self.isCyclicUtil(node, visited, recStack) == True:
                    return True, node, visited, recStack
        return False, None, None, None

    # A recursive function used by topologicalSort
    def topologicalSortUtil(self, v, visited, stack):
        """
        This function is to get topological sorting from vertex v
        :param v: vertex
        :param visited: flags indicating if vertices are visited
        :param stack: recursion stack
        :return: boolean value
        """

        # Mark the current node as visited.
        visited[v] = True

        # Recur for all the vertices adjacent to this vertex
        for i in self.graph[v]:
            if visited[i] == False:
                self.topologicalSortUtil(i, visited, stack)

        # Push current vertex to stack which stores result
        stack.insert(0, v)

    # The function to do Topological Sort. It uses recursive topologicalSortUtil()
    def topologicalSort(self):
        """
        This function is to get the topological sorting of the graph
        :return: a list of vertices in topological sorting order
        """
        # Mark all the vertices as not visited
        visited = [False] * (self.V + 1)
        stack = []

        # Call the recursive helper function to store Topological
        # Sort starting from all vertices one by one
        for i in range(1, self.V + 1):
            if visited[i] == False:
                self.topologicalSortUtil(i, visited, stack)

        # Print contents of stack
        return stack


def task_one(filename):
    """
    This function conducts the task 1 and does the following:
    1. Read the schedule from the schedule file
    2. Construct the precedence graph described by the schedule
    3. Check the graph for cycle(s) to determine whether or not the schedule is conflict serializable
    4. If the schedule is conflict serializable, topologically sort the graph to produce a serializability order of
       the schedule's transactions
    5. Report a list of the IDs of the transactions in the schedule file, in ascending order by ID; and either a
       message stating that the schedule is not conflict serializable and the IDs of the transactions participating
       in the detected cycle, or a message stating that the schedule is conflict serializable and a topological
       ordering of the conflict serializable schedule.
    :param filename: the path to the .sch file
    :return: None
    """
    # 1. Read the schedule from the schedule file
    lines = open(filename, 'r').readlines()
    lines = [line.strip() for line in lines]
    # The operation must match the pattern <op><id><space(s)><item>
    #   where, <op> is one of r, w, or c
    #          <id> is an integer that identifies the transaction executing <op>
    #          <item> is a single upper-case letter representing the DB item being read or written
    #                 (and is absent if <op> is c)
    #          <space(s)> are one or more spaces (also absent when <op> is c)
    pattern = re.compile("^[rwcRWC][0-9]+[ ]*[a-zA-Z]*$")
    lines = [line for line in lines if pattern.match(line)]
    transactions = set([int(line.split()[0][1:]) for line in lines])  # Extract all the transactions in schedule file
    print("Schedule involves the following transactions: [%s]" % (','.join(str(item) for item in transactions)))

    # 2. Construct the precedence graph described by the schedule
    g = Graph(max(transactions))  # initialize the graph with the number of vertices
    last_commit = defaultdict(int, {k: -1 for k in transactions})  # a dict to record the operation where each transaction commits last time, initialized as -1
    not_commit = transactions.copy()  # a set to record the transaction not committed yet
    # Iterate through the operations
    for i in range(len(lines)):
        line = lines[i]
        op = line[0]
        transaction = int(line.split()[0][1:])
        # If the operation is "commit"
        if op == 'c':
            # remove all the edges connected to this transaction from graph
            g.deleteEdgesConnectedTo(transaction)
            # record this operation as the place where last commit happens
            last_commit[transaction] = i
            # remove this transaction from the not-committed transaction set
            if transaction in not_commit:
                not_commit.remove(transaction)
        # If the operation is either "read" or "write"
        else:
            # put this transaction back to the non-committed transaction set
            if transaction not in not_commit:
                not_commit.add(transaction)
            # extract the DB item being operated on
            variable = line.split()[1]
            # search the previous operations that operations on the same DB item
            for j in range(i):
                line_prev = lines[j]
                op_prev = line_prev[0]
                transaction_prev = int(line_prev.split()[0][1:])
                # If this previous operation has committed, continue
                if j <= last_commit[transaction_prev]:
                    continue
                # If this previous operation is "commit", continue
                if op_prev == 'c':
                    continue
                variable_prev = line_prev.split()[1]
                # If this previous operation operates on the same DB item but belongs to different transaction
                if variable_prev == variable and transaction_prev != transaction:
                    # If the current operation is "write", then any previous eligible operation could crate an edge
                    if op == 'w':
                        g.addEdge(transaction_prev, transaction)
                    # If the current operation is "read", then only previous eligible "write" operation could create an edge
                    elif op == 'r':
                        if op_prev == 'w':
                            g.addEdge(transaction_prev, transaction)
        # Check if the current graph has cycle(s), and if yes, what nodes are in the cycle(s) (stored in recStack)
        iscyclic, _, _, recStack = g.isCyclic()
        # If the current graph has cycle(s), print out the IDs of the transactions participating in the detected cycle
        if iscyclic:
            print("Instruction %d (%s) crated a conflict cycle." % (i+1, line))
            transactions_cycles = []
            for index, item in enumerate(recStack):
                if item:
                    transactions_cycles += [str(index)]
            print("These are the transactions participating in cycles: [%s]" % ','.join(transactions_cycles))
            return
    # If the graph doesn't has cycle(s) until the end, which means the schedule is conflict serializable, and print out
    # a topological ordering of the conflict serializable schedule
    print("The schedule is conflict serializable.")
    stack = g.topologicalSort()
    stack = [str(item) for item in stack]
    ordering = []
    for ts in transactions:
        if ts not in not_commit:
            ordering += [str(ts)]
    for item in stack:
        if item not in ordering and int(item) in transactions:
            ordering += [item]
    print("The transactions can be serializable to this order: [%s]" % ','.join(ordering))


def task_two(filename, number, lowerbound, upperbound):
    """
    This function conducts the task 2 and does the following:
    1. Read the collection of transactions from the schedule file
    2. Loop for a number of times equal to the non–negative integer:
        (a) Create a legal schedule of the transactions by creating a random interleaving of the operations of
            the transactions
        (b) Determine whether or not the schedule is conflict serializable
    3. Report the command–line arguments, the quantity of schedules that were conflict serializable, and the
       percentage of schedules that were conflict serializable.
    :param filename: the path to the .set file
    :param number: the number of tries
    :param lowerbound: the lower bound of the number of operations to be included
    :param upperbound: the upper bound of the number of operations to be included
    :return: None
    """
    # Print out the command–line arguments
    print("%s %d %d-%d" % (filename, number, lowerbound, upperbound))
    # When the number of tries is 0, no experiments are conducted thus no results.
    if number == 0:
        print("The number of tries is 0. No results to print.")
        return

    # 1. Read the schedule from the schedule file
    lines = open(filename, 'r').readlines()
    lines = [line.strip() for line in lines]
    # The operation must match the pattern <op><id><space(s)><item>
    #   where, <op> is one of r, w, or c
    #          <id> is an integer that identifies the transaction executing <op>
    #          <item> is a single upper-case letter representing the DB item being read or written
    #                 (and is absent if <op> is c)
    #          <space(s)> are one or more spaces (also absent when <op> is c)
    pattern = re.compile("^[rwcRWC][0-9]+[ ]*[a-zA-Z]*$")
    lines = [line for line in lines if pattern.match(line)]
    transactions = set([int(line.split()[0][1:]) for line in lines])
    print("Schedule involves the following transactions: [%s]" % (','.join(str(item) for item in transactions)))

    lines_by_transaction = [[] for _ in range(len(transactions) + 1)]
    for line in lines:
        lines_by_transaction[int(line.split(' ')[0][1:])] += [line]

    res = 0
    for _ in range(number):
        new_lines = []
        lines_by_transaction_start = [0 for _ in range(len(transactions) + 1)]
        transactions_available = transactions.copy()
        while True:
            if len(transactions_available) == 0:
                break
            ts = random.sample(transactions_available, 1)[0]
            num = random.randint(lowerbound, upperbound)
            line_start = lines_by_transaction_start[ts]
            line_end = min(lines_by_transaction_start[ts] + num - 1, len(lines_by_transaction[ts]) - 1)
            new_lines += [lines_by_transaction[ts][line_start: (line_end + 1)]]
            if line_end == len(lines_by_transaction[ts]) - 1:
                transactions_available.remove(ts)
            else:
                lines_by_transaction_start[ts] = line_end + 1
        new_lines = [item for sublist in new_lines for item in sublist]

        conflict_serializable = True
        g = Graph(max(transactions))  # initialize the graph with the number of vertices
        last_commit = defaultdict(int, {k: -1 for k in transactions})  # a dict to record the operation where each transaction commits last time, initialized as -1
        not_commit = transactions.copy()  # a set to record the transaction not committed yet
        # Iterate through the operations
        for i in range(len(new_lines)):
            line = new_lines[i]
            op = line[0]
            transaction = int(line.split()[0][1:])
            # If the operation is "commit"
            if op == 'c':
                # remove all the edges connected to this transaction from graph
                g.deleteEdgesConnectedTo(transaction)
                # record this operation as the place where last commit happens
                last_commit[transaction] = i
                # remove this transaction from the not-committed transaction set
                if transaction in not_commit:
                    not_commit.remove(transaction)
            # If the operation is either "read" or "write"
            else:
                # put this transaction back to the non-committed transaction set
                if transaction not in not_commit:
                    not_commit.add(transaction)
                # extract the DB item being operated on
                variable = line.split()[1]
                # search the previous operations that operations on the same DB item
                for j in range(i):
                    line_prev = new_lines[j]
                    op_prev = line_prev[0]
                    transaction_prev = int(line_prev.split()[0][1:])
                    # If this previous operation has committed, continue
                    if j <= last_commit[transaction_prev]:
                        continue
                    # If this previous operation is "commit", continue
                    if op_prev == 'c':
                        continue
                    variable_prev = line_prev.split()[1]
                    # If this previous operation operates on the same DB item but belongs to different transaction
                    if variable_prev == variable and transaction_prev != transaction:
                        # If the current operation is "write", then any previous eligible operation could crate an edge
                        if op == 'w':
                            g.addEdge(transaction_prev, transaction)
                        # If the current operation is "read", then only previous eligible "write" operation could create an edge
                        elif op == 'r':
                            if op_prev == 'w':
                                g.addEdge(transaction_prev, transaction)
            # Check if the current graph has cycle(s), and if yes, what nodes are in the cycle(s) (stored in recStack)
            iscyclic, _, _, recStack = g.isCyclic()
            # If the current graph has cycle(s), record this try as not conflict serializable
            if iscyclic:
                conflict_serializable = False
                break
        # If the graph doesn't has cycle(s) until the end, which means the schedule is conflict serializable, then
        # increase the variable "res" by 1
        if conflict_serializable:
            res += 1

    # Print out the quantity of schedules that were conflict serializable, and the percentage of schedules that were
    # conflict serializable.
    print("%d out of %d schedules for the transactions were conflict serializable" % (res, number))
    print("%.1f%% conflict serializable rate" % (res * 100 / number))


if __name__ == '__main__':
    try:
        fn = sys.argv[1]
        # Check if the path/filename exists
        if os.path.exists(fn):
            # task 1
            if fn.endswith('.sch'):
                task_one(fn)
            # task 2
            elif fn.endswith('.set'):
                num = int(sys.argv[2])
                if num < 0:
                    print("The second argument should be a non-negative integer!")
                    sys.exit()
                lb = int(sys.argv[3].split('-')[0])
                if lb <= 0:
                    print("The lower bound should be a positive integer!")
                    sys.exit()
                ub = int(sys.argv[3].split('-')[1])
                if ub <= 0:
                    print("The lower bound should be a positive integer!")
                    sys.exit()
                if lb > ub:
                    print("The lower bound should be smaller than or equal to the upper bound!")
                    sys.exit()
                task_two(fn, num, lb, ub)
            else:
                print("Only .sch or .set file is accepted.")
        else:
            print("File does not exist!")
    except IndexError:
        print("The arguments entered are incorrect!")

