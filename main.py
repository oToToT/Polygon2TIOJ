#! /usr/bin/env python3
import tioj
import problem
import argparse
from getpass import getpass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, nargs='+', help='polygon problem zip')
    parser.add_argument('--update', action='store_true', help='only update package')
    parser.add_argument('--remove_tests', action='store_true', help='remove tests')
    parser.add_argument('--url', type=str, default='https://tioj.ck.tp.edu.tw/', help='TIOJ url')
    args = parser.parse_args()
    
    tioj = TIOJ(args.url)
    while True:
        username = input('Username: ')
        password = getpass('Password: ')
        if tioj.login(username, password):
            print('Login OK.')
            break
        print('Login Failed!')

    if args.remove_tests:
        for filename in args.filename:
            cnt = tioj.remove_tests(int(filename))
            print('successfully removed %d problems.' % cnt)
    elif args.update:
        for filename, problem_id in [args.filename]:
            problem_id = int(problem_id)
            problem_zip = zipfile.ZipFile(filename, 'r')
            prob = Problem()
            prob.fromPolygon(problem_zip)
            problem_zip.close()
            print('Processing %s..' % prob.name)
            tioj.update_problem(problem_id, prob)
            print('Invisible problem %d created.' % problem_id)
            print('Uploading %d tests..' % len(prob.tests))
            tioj.upload_tests(problem_id, prob)
            print('%d tests uploaded' % len(prob.tests))
            print('Done.')
    else:
        for filename in args.filename:
            problem_zip = zipfile.ZipFile(filename, 'r')
            prob = Problem()
            prob.fromPolygon(problem_zip)
            problem_zip.close()
            print('Processing %s..' % prob.name)
            problem_id = tioj.create_problem(prob)
            print('Invisible problem %d created.' % problem_id)
            print('Uploading %d tests..' % len(prob.tests))
            tioj.upload_tests(problem_id, prob)
            print('%d tests uploaded' % len(prob.tests))
            print('Done.')
