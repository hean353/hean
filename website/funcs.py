class CheckGradeRequirements:
    def __init__(self):
        self.programmes = []
        self.users = []
        self.grades = {
            "A": 12,
            "A-": 11,
            "B+": 10,
            "B": 9,
            "B-": 8,
            "C+": 7,
            "C": 6,
            "C-": 5,
            "D+": 4,
            "D": 3,
            "D-": 2,
            "E": 1,
        }

    def print_qualified_programs(self, programs_array):
        for program in programs_array:
            print(f"{program}\n")
        print()

    def top_view(self):
        qualified_programs = []
        try:
            for program in self.programmes:
                minimum_subject_grade_requirements = program.get("minimum_subject_requirements")
                reqs = [minimum_subject_grade_requirements]
                if self.check_requirements(reqs):
                    qualified_programs.append(program)
        except Exception as e:
            print(f"Error in top_view: {e}")
        return qualified_programs

    def check_requirements(self, requirements):
        try:
            for requirement in requirements:
                if not requirement:
                    return True
                count = 0
                for subject, grade in requirement.items():
                    if "/" in subject:
                        subjects = subject.split("/")
                        for sub in subjects:
                            if self.compare_grades(sub, grade):
                                count += 1
                                break
                    else:
                        if self.compare_grades(subject, grade):
                            count += 1
                if count != len(requirement):
                    return False
            return True
        except Exception as e:
            print(f"Error in check_requirements: {e}")
            return False

    def compare_grades(self, subject_name, required_grade):
        try:
            for subjects in self.users:
                for subject, grade in subjects.items():
                    if subject.startswith(subject_name.lower()):
                        return self.grades.get(grade, 0) >= self.grades.get(required_grade, 0)
        except Exception as e:
            print(f"Error in compare_grades: {e}")
        return False
