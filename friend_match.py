import csv
from functools import partial


class Student:

    class Attribute():

        def get_attr_compare_score(self, attr2):
            attr1 = self
            if len(attr1.value) > len(attr2.value):
                attr2, attr1 = attr1, attr2
            return sum([(1 if each_val in attr2.value else 0) for each_val in attr1.value])

        def __init__(self, name='', index=0, data=None, comparison_method=None):
            self.name = name
            self.index = index

            if data is None:
                self.value = []
            else:
                self.value = data

            if comparison_method is None:
                self.attr_comparison_score = partial(
                    self.get_attr_compare_score)
            else:
                self.attr_comparison_score = comparison_method

        def load_value_and_return_attribute(self, data, delimiter=''):
            self.value = data.split(delimiter)

    def __init__(self):
        self.pre_defined_attributes = [
            Student.Attribute('name', 0),
            Student.Attribute('email', 1),
            Student.Attribute('location', 2),
            Student.Attribute('meetup_options', 3),
            Student.Attribute('discussion_topics', 4),
            Student.Attribute('qualities_in_friend', 5),
            Student.Attribute('morning_or_night_person', 6),
            Student.Attribute('planning_type', 7),
            Student.Attribute('diet_pref', 8),
            Student.Attribute('ghosts', 9),
            Student.Attribute('traits', 10)
        ]

        self.user_defined_attributes = [
            Student.Attribute('tv_shows', 11),
            Student.Attribute('musical_artists', 12),
            Student.Attribute('fav_food', 13),
            Student.Attribute('free_time', 14),
            Student.Attribute('dream_living', 15)
        ]

    def __str__(self):
        str = ''
        str = str + (repr(self)) + '\n'
        str = str + ('Predefined Attributes:') + '\n'
        for each_attr in self.pre_defined_attributes:
            str = str + \
                (f'index: {each_attr.index}, name: {each_attr.name}, value: {each_attr.value}') + '\n'
        str = str + ('Userdefined Attributes:') + '\n'
        for each_attr in self.user_defined_attributes:
            str = str + \
                (f'index: {each_attr.index}, name: {each_attr.name}, value: {each_attr.value}') + '\n'
        return str

    @staticmethod
    def friendship_score_from_predefined_attributes(first_student, second_student):
        score = 0
        for (first_student_attr, second_student_attr) in zip(first_student.pre_defined_attributes, second_student.pre_defined_attributes):
            score = score + \
                first_student_attr.attr_comparison_score(second_student_attr)
        return score

    @classmethod
    def load_master_list(cls, filename):
        with open(filename, 'r') as master_list_file:
            csv_reader = csv.reader(master_list_file, delimiter=',')
            line_count = 0
            student_list = []
            header_list = []
            for row in csv_reader:
                if line_count > 0:
                    new_student = Student()
                    for each_attr in new_student.pre_defined_attributes:
                        each_attr.load_value_and_return_attribute(data=row[each_attr.index], delimiter=',')
                    for each_attr in new_student.user_defined_attributes:
                        each_attr.load_value_and_return_attribute(data=row[each_attr.index], delimiter=',')
                    student_list.append(new_student)
                else:
                    header_list = row
                line_count += 1
            print(f'Processed {line_count} lines.')
            return (header_list, student_list)


def main():
    (header_list, student_list) = Student.load_master_list('master_list.csv')
    print(Student.friendship_score_from_predefined_attributes(
        student_list[0], student_list[1]))


if __name__ == "__main__":
    main()
