import sys
import copy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for key, value in self.domains.items():
            temp = []
            for ele in value:
                if key.length != len(ele):
                    temp.append(ele)
            
            for elem in temp:
                self.domains[key].remove(elem)         
                       
 
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        #get overlap between two variables
        olap = self.crossword.overlaps[x, y]
        t = False
        
        if olap == None:
            return False
        
        xwords = copy.deepcopy(self.domains[x])
        ywords =  copy.deepcopy(self.domains[y])
        
        if olap is not None:
            p, q = olap
            
        for ele in xwords:
            overlap = True        
            for val in ywords:
                if ele[p] == val[q] and val != ele:
                    overlap = False
                        
            if overlap:
                self.domains[x].remove(ele)
                t = True
            
        return t                
                                   

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
    
        if arcs == None:
            arcs = []
            for var in self.crossword.overlaps.keys():
                arcs.append(var)
            que = arcs    
        else:
            que = arcs    
            
        while len(que) != 0:
            for ele in que:
                que.pop(que.index(ele))
                if self.revise(ele[0], ele[1]):
                    if len(self.domains[ele[0]]) == 0:
                        return False
                    else:
                        for element in self.crossword.neighbors(ele[0]):
                            if element == ele[1]:
                                continue
                            else:
                                que.append((element,ele[0]))         
                else:
                    continue        
        return True   
                
                
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for ele in self.crossword.variables:
            if ele not in assignment.keys():
                return False
            if len(assignment[ele]) == 0:
                return False
            if assignment[ele] is None:
                return False
            if assignment[ele] not in self.crossword.words:
                return False
    
        return True    
            
  
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check uniqueness
        temp = []
        for key in assignment:
            if assignment[key] not in temp:
                temp.append(assignment[key])
            else:
                return False
            
            if len(assignment[key]) != key.length:
                return False
           
            for ele in assignment:
                if key != ele:
                    if assignment[key] == assignment[ele]:
                        return False
                    
                    olap = self.crossword.overlaps[key, ele]
                    if olap is not None:
                        x, y = olap
                        if assignment[key][x] != assignment[ele][y]:
                            return False
           
        return True
                     
                     
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # create a dict of closest neghbours
        close_neighbours = {key: self.domains[key] for key in self.crossword.neighbors(var) - assignment}
        
        # create dic to keep track of counts
        counts = dict()
        
        for val in self.domains[var]:
            counts[val] = 0
            for ele in close_neighbours:
                for word in self.domains[ele]:
                    if self.crossword.overlaps[var, ele] is not None:
                        i, j = self.crossword.overlaps[var, ele]
                        if val[i] != word[j]:
                            counts[val] += 1
        
        result = sorted(counts.items(), key=lambda a: a[1]) 
        return result
                           

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        counts = {key: len(self.domains[key]) for key in self.crossword.variables - set(assignment)}
        
        temp = min(counts.values())
        result = [key for key in counts if counts[key] == temp]
        
        if len(result) == 1:
            return result[0]
        else:
            neighbour_count = {key:len(self.crossword.neighbors(key)) for key in result}
            temp_n = max(neighbour_count.values())
            f_result = [key for key in neighbour_count if neighbour_count[key] == temp_n]
            return f_result[0]
        
     
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        for ele in self.domains[var]:
            new_assignment = assignment.copy()
            new_assignment[var] = ele
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None        
            
            
def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
