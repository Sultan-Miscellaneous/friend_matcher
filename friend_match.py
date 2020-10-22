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
    t1 = process_text(text1)
    t2 = process_text(text2)
    if(t1 != '' and t2 != ''):
        base = nlp(t1)
        compare = nlp(t2)
        return base.similarity(compare)
    else:
        return 0


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
            if len(attr1.value) == 0 or len(attr2.value) == 0:
                return 0
            if len(attr1.value) > len(attr2.value):
                attr2, attr1 = attr1, attr2
                
            total_score = []
            for each_attr1_val in attr1.value:
                scores = [0]
                for each_attr2_val in attr2.value:
                    similarity = calculate_similarity(
                        each_attr1_val, each_attr2_val)
                    # print('attr1.val: ' + each_attr1_val + ', attr2_val ' +
                    #       each_attr2_val + ' similarity: ' + str(similarity))
                    if threshold_lower < similarity and similarity < threshold_upper:
                        # don't break, maybe something more similar is coming
                        # print('similarity resolved to 0.5')
                        scores.append(0.5)
                    elif similarity > threshold_upper:
                        # can't get better than this, so break
                        # print('similarity resolved to 1')
                        scores.append(1)
                        break
                # else:
                #     print('similarity resolved to 0')
                total_score.append(max(scores))
            # print(attr1.value)
            # print(total_score)
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
            'name': Student.Attribute(name='name', index=0),
            'email': Student.Attribute(name='email', index=1),
            'location': Student.Attribute(name='location', index=2),
            'meetup_options': Student.Attribute(name='meetup_options', index=3)
        }

        self.pre_defined_attributes = [
            Student.Attribute(name='discussion_topics', index=4, comparison_method='exact' ),
            Student.Attribute(name='qualities_in_friend', index=5, comparison_method='exact' ),
            Student.Attribute(name='morning_or_night_person', index=6, comparison_method='exact' ),
            Student.Attribute(name='planning_type', index=7, comparison_method='exact' ),
            Student.Attribute(name='diet_pref', index=8, comparison_method='exact', custom_rule=lambda attr1, attr2: ( 
                1 if attr1.value[0] == attr2.value[0]
                else 0.5 if attr1.value[0] == 'Yes' and attr2.value[0] == 'I eat vegetarian/vegan often but do also eat meat'
                else 0.5 if attr1.value[0] == 'I eat vegetarian/vegan often but do also eat meat' and attr2.value[0] == 'Yes'
                else 0
            )),
            Student.Attribute(name='ghosts', index=9, comparison_method='exact', custom_rule=lambda attr1, attr2: ( 
                1 if attr1.value[0] == attr2.value[0]
                else 0.5 if attr1.value[0] == 'Yes' and attr2.value[0] == 'Unsure'
                else 0.5 if attr1.value[0] == 'Unsure' and attr2.value[0] == 'Yes'
                else 0)),
            Student.Attribute(name='traits', index=10, comparison_method='exact' )
        ]

        self.user_defined_attributes = [
            Student.Attribute(name='tv_shows', index=11, threshold_lower=0.80,
                              threshold_upper=0.95, comparison_method='spacey'),
            Student.Attribute(name='musical_artists', index=12, threshold_lower=0.85,
                              threshold_upper=0.95, comparison_method='spacey'),
            Student.Attribute(name='fav_food', index=13, threshold_lower=0.60,
                              threshold_upper=0.90, comparison_method='spacey'),
            Student.Attribute(name='free_time', index=14, threshold_lower=0.50,
                              threshold_upper=0.90, comparison_method='spacey'),
            Student.Attribute(name='dream_living', index=15, threshold_lower=0.80,
                              threshold_upper=0.90, comparison_method='spacey')
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
            print('Comparing Target To: ' + second_student.user_info_attributes['name'].value[0])
            for (first_student_attr, second_student_attr) in zip(first_student.pre_defined_attributes, second_student.pre_defined_attributes):
                score = score + \
                    first_student_attr.get_attr_comparison_score(
                        second_student_attr)
        return score

    def friendship_score_from_userdefined_attributes(self, second_student):
        first_student = self
        scores = [0]*len(first_student.user_defined_attributes)
        if first_student.can_meet(second_student):
            print('Comparing Target To: ' + second_student.user_info_attributes['name'].value[0])
            scores = [
                first_student_attr.get_attr_comparison_score(
                    second_student_attr)
                for (first_student_attr, second_student_attr) in zip(first_student.user_defined_attributes, second_student.user_defined_attributes)
                if len(first_student_attr.value) > 0 and len(second_student_attr.value) > 0
            ]
        return scores

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
            print(f'Loaded {line_count} Students.')
            return (header_list, student_list)


def load_target_student_name(filename):
    with open(filename, 'r') as target_student_file:
        return target_student_file.read().strip()


def load_student_names_from_candidate_list(filename):
    with open(filename, 'r') as candidate_file:
        return [name.strip() for name in candidate_file if name != '']

class Tracking_writer:
    def __init__(self, output_file):
        self.writer = csv.writer(output_file)
        self.rows_written = 0
    def writerow(self, list):
        self.writer.writerow(list)
        self.rows_written = self.rows_written + 1


def write_output_to_csv(filename, target_student, candidate_students, predef_scores, userdef_scores):
    with open(filename, 'w') as output_file:
        writer = Tracking_writer(output_file)
        newline = ['']
        user_info_headers = [
            header for header in target_student.user_info_attributes.keys()]
        target_info_values = [','.join(attribute.value)
                              for attribute in target_student.user_info_attributes.values()]
        candidate_info_values = [
            [
                ','.join(attribute.value) for attribute in candidate.user_info_attributes.values()
            ] for candidate in candidate_students
        ]

        def addnewline(count):
            for i in range(0, count):
                writer.writerow(newline)

        writer.writerow(['Matching The Following Target:'])
        writer.writerow(user_info_headers)
        writer.writerow(target_info_values)
        addnewline(2)
        writer.writerow(['With the Following Candidates'])
        writer.writerow(user_info_headers)
        for row in candidate_info_values:
            writer.writerow(row)
        addnewline(4)
        writer.writerow(
            ['Scores for user defined responses to the following questions:'])
        score_eval_header = ['name']
        userdef_questions = [
            attribute.name for attribute in target_student.user_defined_attributes
        ]
        for each_question in userdef_questions:
            score_eval_header.append('Target response ' + each_question)
            score_eval_header.append('Candidate response ' + each_question)
            score_eval_header.append('Suggested Score ')
            
        score_eval_header.append('Base Score')
        score_eval_header.append('Total Score')
        writer.writerow(score_eval_header)
        
        for (candidate, candidate_predef_score, candidate_userdef_scores) in zip(candidate_students, predef_scores, userdef_scores):
            row_index = 0
            candidate_data = [candidate.user_info_attributes['name'].value[0]]
            attr_score_index = []
            for (target_attribute, candidate_attribute, userdef_score) in zip(
                target_student.user_defined_attributes, candidate.user_defined_attributes, candidate_userdef_scores
            ):
                row_index = row_index + 1
                candidate_data.append(','.join(target_attribute.value))
                row_index = row_index + 1
                candidate_data.append(','.join(candidate_attribute.value))
                row_index = row_index + 1
                attr_score_index.append(row_index)
                candidate_data.append(userdef_score)
                
            candidate_data.append(candidate_predef_score)
            row_index = row_index + 1
            attr_score_index.append(row_index)
            suggested_score_cells = list(map(lambda x: chr(ord('A')+x)+str(writer.rows_written+1), attr_score_index))
            sum_equation = '=' + '+'.join(suggested_score_cells)
            candidate_data.append(sum_equation)
            writer.writerow(candidate_data)


def main():
    (header_list, student_list) = Student.load_master_list('master_list.csv')
    target_name = load_target_student_name('target.txt')
    
    print('Target Student Specified: ' + target_name)

    candidate_names = load_student_names_from_candidate_list(
        'candidate_list.txt')

    print('Candidate Students Specified: ' + '\n'.join(candidate_names))

    try:
        target_student = list(filter(
            lambda student: target_name in student.user_info_attributes['name'].value, student_list))[0]
    except:
        print('ERROR: Invalid input files specified, check and make target_student file has a valid students')
        raise
    
    candidate_students = list(filter(
        lambda student: student.user_info_attributes['name'].value[0] in candidate_names, student_list))
    
    if(len(candidate_students) > 0):
        print('Evaluating friendship score from predefined attribute list')
        candidate_scores_from_predefined_attributes = [
            target_student.friendship_score_from_predefined_attributes(
                candidate)
            for candidate in candidate_students
        ]
        print('Evaluating friendship score from userdefined attribute list')
        candidate_scores_from_userdefined_attributes = [
            target_student.friendship_score_from_userdefined_attributes(
                candidate)
            for candidate in candidate_students
        ]
        print('Writing final scores to output csv file')
        write_output_to_csv('scores.csv', target_student, candidate_students,
                            candidate_scores_from_predefined_attributes, candidate_scores_from_userdefined_attributes)
    else:
        print('ERROR: Invalid input files specified, check and make sure candidate_list file has valid students')
        raise


if __name__ == "__main__":
    main()
