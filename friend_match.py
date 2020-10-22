import csv
from functools import partial
import spacy

print('Loading spacey default model')
nlp = spacy.load("en_core_web_lg")
print('Done')

def process_text(text):
    doc = nlp(text.lower())
    result = []
    for token in doc:
        if token.text in nlp.Defaults.stop_words:
            continue
        if token.is_punct:
            continue
        if token.lemma_ == '-PRON-':
            continue
        result.append(token.lemma_)
    return " ".join(result)


def calculate_similarity(text1, text2):
    base = nlp(process_text(text1))
    compare = nlp(process_text(text2))
    return base.similarity(compare)


class Student:

    class Attribute():
        def __init__(self, name='', index=0, data=None, custom_rule=None, threshold_lower=0.45, threshold_upper=0.90, comparison_method='exact'):
            self.name = name
            self.index = index

            if data is None:
                self.value = []
            else:
                self.value = data

            if comparison_method == 'exact':
                self.get_attr_comparison_score = partial(
                    self.get_attr_comparison_score_with_custom_rule, custom_rule)
            elif comparison_method == 'spacey':
                self.get_attr_comparison_score = partial(
                    self.get_attr_spacey_comparison_with_thresholds, threshold_lower, threshold_upper)
            else:
                print("invalid comparison method selected")
                raise

        def get_attr_spacey_comparison_with_thresholds(self, threshold_lower, threshold_upper, attr2):
            attr1 = self
            if len(attr1.value) > len(attr2.value):
                attr2, attr1 = attr1, attr2
            total_score = []
            for each_attr1_val in attr1.value:
                scores = [0]
                for each_attr2_val in attr2.value:
                    similarity = calculate_similarity(
                        each_attr1_val, each_attr2_val)
                    print('attr1.val: ' + each_attr1_val + ', attr2_val ' + each_attr2_val + ' similarity: ' + str(similarity))
                    if threshold_lower < similarity and similarity < threshold_upper:
                        # don't break, maybe something more similar is coming
                        print('similarity resolved to 0.5')
                        scores.append(0.5)
                    elif similarity > threshold_upper:
                        # can't get better than this, so break
                        print('similarity resolved to 1')
                        scores.append(1)
                        break
                    else:
                        print('similarity resolved to 0')
                total_score.append(max(scores))
            print(attr1.value)
            print(total_score)
            return sum(total_score)

        def get_attr_comparison_score_with_custom_rule(self, custom_rule, attr2):
            attr1 = self
            if len(attr1.value) > len(attr2.value):
                attr2, attr1 = attr1, attr2
            if custom_rule is None:
                return sum([(1 if each_val in attr2.value else 0) for each_val in attr1.value])
            else:
                return custom_rule(attr1, attr2)

        def load_value_and_return_attribute(self, data, delimiter=''):
            self.value = data.split(delimiter)

    def __init__(self):
        self.user_info_attributes = {
            'name': Student.Attribute('name', 0),
            'email': Student.Attribute('email', 1),
            'location': Student.Attribute('location', 2),
            'meetup_options': Student.Attribute('meetup_options', 3)
        }

        self.pre_defined_attributes = [
            Student.Attribute('discussion_topics', 4),
            Student.Attribute('qualities_in_friend', 5),
            Student.Attribute('morning_or_night_person', 6),
            Student.Attribute('planning_type', 7),
            Student.Attribute('diet_pref', 8, custom_rule=lambda attr1, attr2: (
                1 if attr1.value[0] == attr2.value[0]
                else 0.5 if attr1.value[0] == 'Yes' and attr2.value[0] == 'I eat vegetarian/vegan often but do also eat meat'
                else 0.5 if attr1.value[0] == 'I eat vegetarian/vegan often but do also eat meat' and attr2.value[0] == 'Yes'
                else 0
            )),
            Student.Attribute('ghosts', 9, custom_rule=lambda attr1, attr2: (
                1 if attr1.value[0] == attr2.value[0]
                else 0.5 if attr1.value[0] == 'Yes' and attr2.value[0] == 'Unsure'
                else 0.5 if attr1.value[0] == 'Unsure' and attr2.value[0] == 'Yes'
                else 0)),
            Student.Attribute('traits', 10)
        ]

        self.user_defined_attributes = [
            Student.Attribute('tv_shows', 11, threshold_lower=0.80, threshold_upper=0.95, comparison_method='spacey'),
            Student.Attribute('musical_artists', 12, threshold_lower=0.85, threshold_upper=0.95, comparison_method='spacey'),
            Student.Attribute('fav_food', 13, threshold_lower=0.60, threshold_upper=0.90, comparison_method='spacey'),
            Student.Attribute('free_time', 14, threshold_lower=0.50, threshold_upper=0.90, comparison_method='spacey'),
            Student.Attribute('dream_living', 15, threshold_lower=0.80, threshold_upper=0.90, comparison_method='spacey')
        ]

    def __str__(self):
        str = ''
        str = str + (repr(self)) + '\n'
        str = str + ('UserInfo Attributes:') + '\n'
        for (key, each_attr) in self.user_info_attributes.items():
            str = str + \
                (f'index: {each_attr.index}, name: {each_attr.name}, value: {each_attr.value}') + '\n'
        str = str + ('Predefined Attributes:') + '\n'
        for each_attr in self.pre_defined_attributes:
            str = str + \
                (f'index: {each_attr.index}, name: {each_attr.name}, value: {each_attr.value}') + '\n'
        str = str + ('Userdefined Attributes:') + '\n'
        for each_attr in self.user_defined_attributes:
            str = str + \
                (f'index: {each_attr.index}, name: {each_attr.name}, value: {each_attr.value}') + '\n'
        return str

    def can_meet(self, second_student):
        meet_score = self.user_info_attributes['meetup_options'].get_attr_comparison_score(
            second_student.user_info_attributes['meetup_options'])
        return meet_score > 0

    def friendship_score_from_predefined_attributes(self, second_student):
        first_student = self
        score = 0
        if first_student.can_meet(second_student):
            for (first_student_attr, second_student_attr) in zip(first_student.pre_defined_attributes, second_student.pre_defined_attributes):
                score = score + \
                    first_student_attr.get_attr_comparison_score(
                        second_student_attr)
        return score
    
    def friendship_score_from_userdefined_attributes(self, second_student):
        first_student = self
        score = 0
        if first_student.can_meet(second_student):
            for (first_student_attr, second_student_attr) in zip(first_student.user_defined_attributes, second_student.user_defined_attributes):
                score = score + \
                    first_student_attr.get_attr_comparison_score(
                        second_student_attr)
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
                    for each_attr in new_student.user_info_attributes.values():
                        each_attr.load_value_and_return_attribute(
                            data=row[each_attr.index], delimiter=',')
                    for each_attr in new_student.pre_defined_attributes:
                        each_attr.load_value_and_return_attribute(
                            data=row[each_attr.index], delimiter=',')
                    for each_attr in new_student.user_defined_attributes:
                        each_attr.load_value_and_return_attribute(
                            data=row[each_attr.index], delimiter=',')
                    student_list.append(new_student)
                else:
                    header_list = row
                line_count += 1
            print(f'Processed {line_count} lines.')
            return (header_list, student_list)


def main():

    (header_list, student_list) = Student.load_master_list('master_list.csv')
    print(student_list[27].friendship_score_from_userdefined_attributes(
        student_list[26]))
    print(student_list[27])
    print(student_list[26])


if __name__ == "__main__":
    main()
