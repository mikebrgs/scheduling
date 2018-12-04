import sys

sys.path.insert(0, '/Users/mikebrgs/CurrentWork/tecnico/iasd/proj2/ext/aima-python/')
#sys.path.insert(0, '/Users/loure/Dropbox/Lourenço/Faculdade/5A1S/IASD/SchoolSchedule')
import csp

def getdaytime(element):
    return element[0]

def getday(element):
    return element[0][0]

def gettime(element):
    return element[0][1]

def getroom(element):
    return element[1]

def getcourse(variable):
    return variable[0]

def getctype(variable):
    return variable[1]

def getctnumber(variable):
    return variable[2]

class Analytics(object):
    def __init__(self, Associations):
        self.associations = dict()
        for Association in Associations:
            if not Association[1] in self.associations.keys():
                self.associations[Association[1]] = set()
            self.associations[Association[1]].add(Association[0])

    def verify(self, A, a, B, b):
        # Check if it's at the same time in the same classroom
        if (getday(a) == getday(b) and
            gettime(a) == gettime(b) and
            getroom(a) == getroom(b)):
            return False
        # Check if it's of the same course and type and in the same day
        A_ = A.split(",")
        B_ = B.split(",")
        if (getcourse(A_) == getcourse(B_) and
            getctype(A_) == getctype(B_) and
            getday(a) == getday(b)):
            return False
        # Check if it's at the same time and day and have different classes
        if (len(self.associations[getcourse(A_)] & self.associations[getcourse(B_)]) != 0 and
            getdaytime(a) == getdaytime(b)):
            return False
        return True

class Problem(csp.CSP):
    def __init__(self, fh):
        self.variables = list()
        self.domains = dict()
        self.neighbors = dict()
        # Read every line of the file
        self.WeeklyClasses = list()
        self.TimeSlots = list()
        self.SlotPointer = 0
        self.Rooms = list()
        self.StudentClasses = list()
        self.Associations = list()
        for line in fh:
            line = line.replace("\n","").split(" ")
            if line[0] == "W":
                for WeeklyClass in line[1:]:
                    self.WeeklyClasses.append(tuple(WeeklyClass.split(",")))
            if line[0] == "T":
                for TimeSlot in line[1:]:
                    self.TimeSlots.append(tuple(TimeSlot.split(",")))
            if line[0] == "R":
                for Room in line[1:]:
                    self.Rooms.append(Room)
            if line[0] == "S":
                for StudentClass in line[1:]:
                    self.StudentClasses.append(StudentClass)
            if line[0] == "A":
                for Association in line[1:]:
                    self.Associations.append(tuple(Association.split(",")))
        # Sort list to facilitate heurisitic (by time of the day)
        self.TimeSlots.sort(key = lambda var: int(var[1]))
        # Create elements for the problem
        for WeeklyClass in self.WeeklyClasses:
            WeeklyClass = ",".join(WeeklyClass)
            # Creates variables
            self.variables.append(WeeklyClass)
            self.domains[WeeklyClass] = list()
            self.neighbors[WeeklyClass] = list()
            # Creates domains
            # for TimeSlot in self.TimeSlots:
            #     for Room in self.Rooms:
            #         self.domains[WeeklyClass].append((TimeSlot, Room))
            # Creates neighbors
            for otherWeeklyClass in self.WeeklyClasses:
                otherWeeklyClass = ",".join(otherWeeklyClass)
                if otherWeeklyClass != WeeklyClass:
                    self.neighbors[WeeklyClass].append(otherWeeklyClass)
        return

    # Increase the domain to the next minimum value
    def iterate_domain(self):
        # Start at
        if self.SlotPointer >= len(self.TimeSlots):
            return False
        CurrentPointer = self.SlotPointer
        while (CurrentPointer < len(self.TimeSlots) and
            self.TimeSlots[CurrentPointer][1] == self.TimeSlots[self.SlotPointer][1]):
            for WeeklyClass in self.variables:
                for Room in self.Rooms:
                    self.domains[WeeklyClass].append((self.TimeSlots[CurrentPointer], Room))
            CurrentPointer += 1
        self.SlotPointer = CurrentPointer
        # Initialize problem
        super().__init__(self.variables, self.domains, self.neighbors, Analytics(self.Associations).verify)
        return True

    # Write the solution to an external file
    def dump_solution(self, fh, result):
        output = ""
        if len(result) == 0:
            output = "None"
        else:
            for WeeklyClass, Assignment in result.items():
                output = (output + WeeklyClass + " " + ",".join(Assignment[0]) + " " +
                    Assignment[1] + "\n")
        fh.write(output)
        return

    # Checks if the domain is large enough
    def conditions(self):
        associations = dict()
        for Association in self.Associations:
            if not Association[0] in associations.keys():
                associations[Association[0]] = set()
            associations[Association[0]].add(Association[1])
        MostClasses = 0
        # Checks if we have enough slots for the biggest class
        for Class in associations.keys():
            ThisClass = 0
            for WeeklyClass in self.WeeklyClasses:
                if WeeklyClass[0] in associations[Class]:
                    ThisClass += 1
            if ThisClass > MostClasses:
                MostClasses = ThisClass
        if (len(self.TimeSlots[0:self.SlotPointer]) < MostClasses):
            return False
        # See if we have enough rooms and time slots
        if (len(self.TimeSlots[0:self.SlotPointer])*len(self.Rooms) <
            len(self.WeeklyClasses)):
            return False
        return True

        
def solve(input_file, output_file):
    p = Problem(input_file)
    domain_state = True
    result = set()
    while(p.iterate_domain()):
        if not p.conditions():
            continue
        result = csp.backtracking_search(p,
            select_unassigned_variable = csp.mrv,
            order_domain_values = csp.lcv,
            inference = csp.forward_checking)
        if result:
            break
            # result = csp.backtracking_search(p,
            #     select_unassigned_variable = csp.mrv,
            #     order_domain_values = csp.lcv,
            #     inference = csp.forward_checking)
    # while(not p.conditions()):
    #     domain_state = p.iterate_domain()
    # while(domain_state or len(result)==0):
    #     result = csp.backtracking_search(p,
    #             select_unassigned_variable = csp.mrv,
    #             order_domain_values = csp.lcv,
    #             inference = csp.forward_checking)
    #     domain_state = p.iterate_domain()
    p.dump_solution(output_file,result)
