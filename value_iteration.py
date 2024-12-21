import numpy as np
from solution import Solution


class ValueIteration(Solution):
    def __init__(self, env, gamma=0.9, theta=1e-10, terminal_state=None):
        self.env = env
        self.gamma = gamma
        self.theta = theta
        self.terminal_state = terminal_state
        
        if not terminal_state:
            self.terminal_state = env.nS - 1        
        
        self.V = np.zeros(env.nS)
        self.pi = np.zeros(env.nS)
    
    def reward(self, state, action, next_state):
        step_cost = -0.1
        
        if next_state == self.terminal_state:
            return 10
        
        transmission = self.env.P[state][action][0]
        is_hole = transmission[3]
        
        if not is_hole:
             return step_cost
        
        return transmission[2]
    
    def probability(self, state, action, next_state):
        if self.env.is_hardmode:
            probs = {
                0: {0: 0.5, 1: 0.25, 3: 0.25},  # UP
                1: {0: 0.25, 1: 0.5, 2: 0.25},  # RIGHT
                2: {1: 0.25, 2: 0.5, 3: 0.25},  # DOWN
                3: {0: 0.25, 2: 0.25, 3: 0.5}   # LEFT
            }
            
            total_prob = 0
            for possible_action, prob in probs[action].items():
                transition = self.env.P[state][possible_action][0]
                possible_next_state = transition[1]
                
                if possible_next_state == next_state:
                    total_prob += prob
            
            return total_prob
        
        else:
            transition = self.env.P[state][action][0]
            return 1. if transition[1] == next_state else 0.
    
    def Q(self, state, action):
        expected_reward = 0
        for next_state in range(self.env.nS):
            p = self.probability(state, action, next_state)
            r = self.reward(state, action, next_state)
            expected_reward += p * (r + self.gamma * self.V[next_state])
        
        return expected_reward

    def value_iteration(self):
        while True:
            # Compute the new expected utility (V)
            new_V = np.zeros(self.env.nS)
            
            for state in range(self.env.nS):
                if state == self.terminal_state:
                    new_V[state] = 0
                    continue
                
                else:
                    new_V[state] = max(self.Q(state, action) for action in range(self.env.nA))
            
            # Check for convergence
            if np.max(np.abs(self.V - new_V)) < self.theta:
                break
            
            self.V = new_V
    
    def calc_optimal_policy(self):
            action_names = {0: 'UP', 1: 'RIGHT', 2: 'DOWN', 3: 'LEFT'}
            
            for state in range(self.env.nS):
                if state == self.terminal_state:
                    self.pi[state] = None
                    continue
                    
                else:
                    self.pi[state] = np.argmax([self.Q(state, action) for action in range(self.env.nA)])
            
            policy_grid = np.array(self.pi).reshape(self.env.shape)
            policy_grid = np.vectorize(action_names.get)(policy_grid)
            
            print("Optimal Policy:")
            for row in policy_grid:
                print(" ".join(f"{action:5}" for action in row))
        
                
    
    def solve(self):
        self.value_iteration()
        self.calc_optimal_policy()
        
        return self.pi