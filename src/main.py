import sys

sys.path.insert(0, '/Users/mikebrgs/CurrentWork/tecnico/iasd/proj2/ext/aima-python/')
import csp

class Constraint(object):
    def __init__(self, Associations):
        self.associations = dict()
        for Association in Associations:
            if not Association[1] in self.associations.keys():
                self.associations[Association[1]] = set()
            self.associations[Association[1]].add(Association[0])
    
    def verify(self, A, a, B, b):
        if a[0][0] == b[0][0] and a[0][1] == b[0][1] and a[1] == b[1]:
            return False
        A_ = A.split(",")
        B_ = B.split(",")
        if A_[0] == B_[0] and A_[1] == B_[1] and a[0][0] == b[0][0]:
            return False
        if (len(self.associations[A_[0]] & self.associations[B_[0]]) != 0 and
            a[0] == b[0]):
            return False
        return True

class Problem(csp.CSP):
    def __init__(self, fh):
        variables = list()
        domains = dict()
        neighbors = dict()
        constraints = None
        # Read every line of the file
        WeeklyClasses = list()
        TimeSlots = list()
        Rooms = list()
        StudentClasses = list()
        Associations = list()
        for line in fh:
            line = line.replace("\n","").split(" ")
            if line[0] == "W":
                for WeeklyClass in line[1:]:
                    WeeklyClasses.append(tuple(WeeklyClass.split(",")))
            if line[0] == "T":
                for TimeSlot in line[1:]:
                    TimeSlots.append(tuple(TimeSlot.split(",")))
            if line[0] == "R":
                for Room in line[1:]:
                    Rooms.append(Room)
            if line[0] == "S":
                for StudentClass in line[1:]:
                    StudentClasses.append(StudentClass)
            if line[0] == "A":
                for Association in line[1:]:
                    Associations.append(tuple(Association.split(",")))
        # Create elements for the problem
        for WeeklyClass in WeeklyClasses:
            WeeklyClass = ",".join(WeeklyClass)
            # Creates variables
            variables.append(WeeklyClass)
            domains[WeeklyClass] = list()
            neighbors[WeeklyClass] = list()
            # Creates domains
            for TimeSlot in TimeSlots:
                for Room in Rooms:
                    domains[WeeklyClass].append((TimeSlot, Room))
            # Creates neighbors
            for otherWeeklyClass in WeeklyClasses:
                otherWeeklyClass = ",".join(otherWeeklyClass)
                if otherWeeklyClass != WeeklyClass:
                    neighbors[WeeklyClass].append(otherWeeklyClass)
        # Create constraints
        super().__init__(variables, domains, neighbors, Constraint(Associations).verify)

    def dump_solution(self, fh, result):
        output = ""
        for WeeklyClass, Assignment in result.items():
            output = (output + WeeklyClass + " " + ",".join(Assignment[0]) + " " +
                ",".join(Assignment[1]) + "\n")
        output = output[:-1]
        fh.write(output)
        return
        
def solve(input_file, output_file):
    p = Problem(input_file)
    result = csp.backtracking_search(p)
    p.dump_solution(output_file, result)