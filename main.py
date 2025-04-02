import heapq

class KR:
    def __init__(self, graph):
        self.graph = graph
    
    def heuristic(self, node, goals):
        return min(abs(node.x - goal.x) + abs(node.y - goal.y) for goal in goals)
    
    def a_star(self, start_index, scopeNodes, n):
        open_set = []
        step_count = 0
    
        heapq.heappush(open_set, (0, self.graph.nodes[start_index]))
        
        g = {node: float('inf') for node in self.graph.nodes.values()}
        g[self.graph.nodes[start_index]] = 0
        
        # estimated total cost
        f = {node: float('inf') for node in self.graph.nodes.values()}
        f[self.graph.nodes[start_index]] = self.heuristic(self.graph.nodes[start_index], 
                                                        [self.graph.nodes[goal] for goal in scopeNodes])
        
        while open_set:    
            _, current = heapq.heappop(open_set)
            
            if current.index in scopeNodes:
                # TODO
                pass
            
            for neighbor, cost in self.graph.get_neighbors(current):
                score = g[current] + cost
                
                if score < g[neighbor]:
                    g[neighbor] = score
                    f[neighbor] = score + self.heuristic(neighbor,
                                                        [self.graph.nodes[goal] for goal in scopeNodes])

                    if neighbor not in [item[1] for item in open_set]:
                        heapq.heappush(open_set, (f[neighbor], neighbor))
                        
            step_count += 1
            if step_count == n:
                return open_set
        
        return None

    
    def IDA_star(self, start_index, scopeNodes, n):
        start_node = self.graph.nodes[start_index]
        
        threshold = self.heuristic(start_node, [self.graph.nodes[goal] for goal in scopeNodes])
        
        while True:
            result, next_threshold = self._dfs(start_node, scopeNodes, 0, threshold, n, [])
            if result is not None:
                return result
            if next_threshold == float('inf'):
                return None
            threshold = next_threshold
            
    
    def _dfs(self, current, scopeNodes, g, threshold, n, path):
        path.append(current.index)
        f = g + self.heuristic(current, [self.graph.nodes[goal] for goal in scopeNodes])
        
        if f > threshold:
            path.pop()
            return None, f
        
        if current.index in scopeNodes:
            return path, None
        
        min_threshold = float('inf')
        for neighbor, cost in self.graph.get_neighbors(current):
            if neighbor.index not in path: 
                result, next_threshold = self._dfs(neighbor, scopeNodes, g + cost, threshold, n, path)
                if result is not None:
                    return result, None
                min_threshold = min(min_threshold, next_threshold)

        path.pop()
        return None, min_threshold
    

class Node:
    def __init__(self, index, x, y):
        self.index = index
        self.x = x
        self.y = y
        
    def __lt__(self, other):
        return self.index < other.index


class Graph:
    def __init__(self, edges, coordinates):
        self.edges = edges
        self.nodes = {}
    
        for node_index, (x, y) in coordinates.items():
            self.nodes[node_index] = Node(node_index, x, y)
            
        self.adj_list = {node: [] for node in self.nodes}
        for node1, node2, cost in edges:
            self.adj_list[node1].append((self.nodes[node2], cost))
            self.adj_list[node2].append((self.nodes[node1], cost))
            
            
    def get_neighbors(self, node):
        return self.adj_list.get(node.index, [])


edges = [[1, 2, 3], [2, 3, 3], [1, 10, 3], [10, 22, 3], [22, 23, 3], [23, 24, 3], [24, 15, 3],
        [15, 3, 3], [10, 11, 1], [11, 12, 1], [14, 15, 1], [14, 13, 1], [2, 5, 1], [5, 8, 1],
        [17, 20, 1], [20, 23, 1], [4, 5, 2], [5, 6, 2], [19, 20, 2], [20, 21, 2], 
        [4, 11, 2], [11, 19, 2], [6, 14, 2], [14, 21, 2], [7, 8, 1], [8, 9, 1],
        [9, 13, 1], [13, 18, 1], [18, 17, 1], [17, 16, 1], [16, 12, 1], [12, 7, 1]]


coordinates = {
    1: (0, 0), 2: (0, 3), 3: (0, 6), 4: (1, 1), 5: (3, 1), 6: (5, 1), 7: (2, 2), 8: (3, 2),
    9: (4, 2), 10: (0, 3), 11: (1, 3), 12: (2, 3), 13: (4, 3), 14: (5, 3), 
    15: (6, 3), 16: (2, 4), 17: (3, 4), 18: (4, 4), 19: (1, 5), 20: (3, 5),
    21: (4, 5), 22: (0, 6), 23: (3, 6), 24: (6, 6)
}

graph = Graph(edges, coordinates)
kr = KR(graph)

# n = 1
# open_set = kr.a_star(12, [1, 20], n)
# indexes = [item[1].index for item in open_set]
# print(sorted(indexes))

start_index = 12
goal_indices = [1, 20]
path = kr.IDA_star(start_index, goal_indices, n = 1)
if path:
    print("Path found:", path)
else:
    print("No path found.")
