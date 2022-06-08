from unittest import result
import clock_cli
from rich import print

date_shift_tests = [
    {'TEST':([2022, 2,22], [2022, 2,22]), 'RESULT':0,  'TEXT':'same date returns 0'},
    {'TEST':([2022, 2,22], [2022, 2,23]), 'RESULT':1,  'TEXT':'one day shifted'},
    {'TEST':([2022, 1,31], [2022, 2, 1]), 'RESULT':1,  'TEXT':'month turns over'},
    {'TEST':([2022, 1,31], [2022, 2,10]), 'RESULT':10, 'TEXT':'month turns over and some days'},
    {'TEST':([2022, 5,31], [2022, 7, 1]), 'RESULT':31,  'TEXT':'multiple months'},
    {'TEST':([2020, 2,28], [2020, 3, 1]), 'RESULT':2,  'TEXT':'leap month turns over'},
    {'TEST':([2022,12,31], [2023, 1, 1]), 'RESULT':1,  'TEXT':'year turns over'},
    {'TEST':([2022, 2,22], [2023, 2,22]), 'RESULT':365,  'TEXT':'entire year'},
    {'TEST':([2020, 2,20], [2021, 2,20]), 'RESULT':366,  'TEXT':'entire leap year'},
]

error_count = 0
for t in date_shift_tests:
    test_result = clock_cli.calculate_date_shift(t['TEST'][0], t['TEST'][1])
    # try:
    #     test_result = clock_cli.calculate_date_shift(t['TEST'][0], t['TEST'][1])
    # except:
    #     test_result = 'ERROR'
    text = t['TEXT']
    res = t['RESULT']
    print(f'{text}:\n{test_result} should equal \n{res}: {test_result==res}')
    if test_result != res:
        error_count += 1
if error_count > 0:
    print(f'you failed {error_count} out of {len(date_shift_tests)} tests.')
else:
    print('You passed all tests!')