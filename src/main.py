import sys
import random
import csp

# Get the day and time from domain's tuple
def getdaytime(element):
    return element[0]

# Get the day from the domain's tuple
def getday(element):
    return element[0][0]

# Get the time from domain's tuple
def gettime(element):
    return element[0][1]

# Get the room from domain's tuple
def getroom(element):
    return element[1]

# Get the course from variable's name
def getcourse(variable):
    return variable[0]

# Get the course type from the variable's name
def getctype(variable):
    return variable[1]

# Get the course's class number from the variable's name
def getctnumber(variable):
    return variable[2]

# Class that contains the method to check CSP constraints
class Analytics(object):
    # Initialization of constraints
    def __init__(self, Associations):
        self.associations = dict()
        for Association in Associations:
            if not Association[1] in self.associations.keys():
                self.associations[Association[1]] = set()
            self.associations[Association[1]].add(Association[0])

    # Verify if this two variable assignments are valid
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

# Problem class
class Problem(csp.CSP):
    def __init__(self, fh):
        self.variables = list()
        self.domains = dict()
        self.neighbors = dict()
        self.WeeklyClasses = list()
        self.TimeSlots = list()
        self.SlotPointer = 0
        self.Rooms = list()
        self.StudentClasses = list()
        self.Associations = list()
        # Read every line of the file
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
            # Creates neighbors
            for otherWeeklyClass in self.WeeklyClasses:
                otherWeeklyClass = ",".join(otherWeeklyClass)
                if otherWeeklyClass != WeeklyClass:
                    self.neighbors[WeeklyClass].append(otherWeeklyClass)
        return

    # Increase the domain to the next minimum value
    def iterate_domain(self):
        # Check if the domain is big enough
        if self.SlotPointer >= len(self.TimeSlots):
            return False
        # Increase domain by one time unit
        CurrentPointer = self.SlotPointer
        while (CurrentPointer < len(self.TimeSlots) and
            self.TimeSlots[CurrentPointer][1] == self.TimeSlots[self.SlotPointer][1]):
            for WeeklyClass in self.variables:
                for Room in self.Rooms:
                    self.domains[WeeklyClass].append((self.TimeSlots[CurrentPointer], Room))
            CurrentPointer += 1
        # Save pointer for next domain iteration
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
        # Create dictionary of associations
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

# Solve function
def solve(input_file, output_file):
    # Initialize
    p = Problem(input_file)
    result = set()
    # Increase domain and search for solution while it's not valid
    while(p.iterate_domain()):
        if not p.conditions():
            continue
        result = csp.backtracking_search(p,
            select_unassigned_variable = csp.mrv,
            order_domain_values = csp.lcv,
            inference = csp.forward_checking)
        if result:
            break
    # Save solution
    p.dump_solution(output_file,result)
