from django.test import TestCase
from audio.utils.modif_ds import *
from audio.utils.reader import *


class UtilsTest(TestCase):
    def test_dictlist_to_listdict(self):
        expected_res = {"col1": [12, 334, 555, 66], "col2": ["ab", "cc"], "col3": [3333.00],
                        "col4": [1, "a", "bc", 33.0, 66, "66"]}
        test_res = dictlist_to_listdict(
            [{'col1': 12, 'col2': 'ab', 'col3': 3333.0, 'col4': 1}, {'col1': 334, 'col2': 'cc', 'col4': 'a'},
             {'col1': 555, 'col4': 'bc'}, {'col1': 66, 'col4': 33.0}, {'col4': 66}, {'col4': '66'}])
        self.assertEquals(test_res, expected_res)

    def test_listdict_to_dictlist(self):
        input_dict = {"col1": [12, 334, 555, 66], "col2": ["ab", "cc"], "col3": [3333.00],
                      "col4": [1, "a", "bc", 33.0, 66, "66"]}
        compact_res = [{'col1': 12, 'col2': 'ab', 'col3': 3333.0, 'col4': 1},
                       {'col1': 334, 'col2': 'cc', 'col4': 'a'},
                       {'col1': 555, 'col4': 'bc'}, {'col1': 66, 'col4': 33.0}, {'col4': 66}, {'col4': '66'}]
        extended_res = [{'col1': 12, 'col2': 'ab', 'col3': 3333.0, 'col4': 1},
                        {'col1': 334, 'col2': 'cc', 'col3': '', 'col4': 'a'},
                        {'col1': 555, 'col2': '', 'col3': '', 'col4': 'bc'},
                        {'col1': 66, 'col2': '', 'col3': '', 'col4': 33.0},
                        {'col1': '', 'col2': '', 'col3': '', 'col4': 66},
                        {'col1': '', 'col2': '', 'col3': '', 'col4': '66'}]
        self.assertRaisesMessage(Exception, "No such an option", listdict_to_dictlist, input_dict, "eded")
        self.assertEquals(compact_res, listdict_to_dictlist(input_dict, "compact"))
        self.assertEquals(extended_res, listdict_to_dictlist(input_dict, "extended"))

    def test_read_from_csv(self):
        _expected_res = {'choreo_vid': [' g3DlYedzfjg', ' Zx1n1R_OQs0', ' RHTqzSSl5qU', ' jWhyc6UQ9ss', ' jSrxXduIz1U',
                                        ' CM5VSP1QWXg', ' -rFsYxFhWlE', ' l7AQwT8Jzz4', ' -v7rQFM8FxY', ' v4CILLmw6EE',
                                        ' P3EgWidZthc', ' QDqlB8M25DQ', ' k98iZjftvKQ', ' S8fvgFDQKvk', ' GwCiHS9_3-Y',
                                        ' bU_YcfG1Hdk'],
                         'choreo_url': ['https://www.youtube.com/watch?v=g3DlYedzfjg',
                                        'https://www.youtube.com/watch?v=Zx1n1R_OQs0',
                                        'https://www.youtube.com/watch?v=RHTqzSSl5qU',
                                        'https://www.youtube.com/watch?v=jWhyc6UQ9ss',
                                        'https://www.youtube.com/watch?v=jSrxXduIz1U',
                                        'https://www.youtube.com/watch?v=CM5VSP1QWXg',
                                        'https://www.youtube.com/watch?v=-rFsYxFhWlE',
                                        'https://www.youtube.com/watch?v=l7AQwT8Jzz4',
                                        'https://www.youtube.com/watch?v=-v7rQFM8FxY',
                                        'https://www.youtube.com/watch?v=v4CILLmw6EE',
                                        'https://www.youtube.com/watch?v=P3EgWidZthc',
                                        'https://www.youtube.com/watch?v=QDqlB8M25DQ',
                                        'https://www.youtube.com/watch?v=k98iZjftvKQ',
                                        'https://www.youtube.com/watch?v=S8fvgFDQKvk',
                                        'https://www.youtube.com/watch?v=GwCiHS9_3-Y',
                                        'https://www.youtube.com/watch?v=bU_YcfG1Hdk'],
                         'start': ['0', '2', '8', '0', '0', '4', '5', '7', '8', '0', '15', '0', '0', '8', ' ', ' '],
                         'end': ['40', '79', '86', '60', '53', '42', '68', '85', '63', '116', '48', '73', '72', '65',
                                 '60', '29']}
        self.assertEquals(_expected_res, CsvReader(test_path + "test.csv").read(
            **{'col1': 'choreo_vid', 'col2': 'choreo_url', 'col3': 'start', 'col4': 'end'}))