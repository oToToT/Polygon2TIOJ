#! /usr/bin/env python3
import argparse
import zipfile
import tempfile
import requests
from bs4 import BeautifulSoup
from getpass import getpass
from urllib.parse import urljoin, urlparse

class Problem:
    def __init__(self):
        # currently only support batch judge
        self.name = ''
        self.description = ''
        self.problem_type = 0
        self.input = ''
        self.output = ''
        self.example_input = ''
        self.example_output = ''
        self.hint = ''
        self.source = ''
        self.time_limit = 1000
        self.memory_limit = 65536
        self.output_limit = 65536
        self.tests = []
        return

    def fromPolygon(self, z):
        def mathjaxify(s):
            # ugly way to process mathjax
            # only support inline mathjax
            while s.count('$$$') >= 2:
                s = s.replace('$$$', '$', 2)
            return s

        meta_xml = z.open('problem.xml', 'r')
        meta = BeautifulSoup(meta_xml.read(), 'lxml')
        meta_xml.close()
        
        self.name = meta.find('name').get('value')
        self.time_limit = int(meta.find('time-limit').text)
        self.memory_limit = int(meta.find('memory-limit').text)

        statement_html_xml = meta.find('statement', {'type': 'text/html'})
        statement_charset = statement_html_xml.get('charset')
        statement_html_path = statement_html_xml.get('path')
        statement_html = z.open(statement_html_path, 'r')
        statement = BeautifulSoup(statement_html.read(), 'html.parser')
        statement_html.close()
        
        # process descrpition
        self.description = statement.find('div', {'class': 'legend'}).encode_contents()
        self.description = self.description.decode(statement_charset)
        self.description = mathjaxify(self.description)

        # process input
        input_spec = statement.find('div', {'class': 'input-specification'})
        input_spec.find('div', {'class': 'section-title'}).extract()
        input_spec.find('p').extract()
        self.input = input_spec.encode_contents()
        self.input = self.input.decode(statement_charset)
        self.input = mathjaxify(self.input)
        
        # process output
        output_spec = statement.find('div', {'class': 'output-specification'})
        output_spec.find('div', {'class': 'section-title'}).extract()
        output_spec.find('p').extract()
        self.output = output_spec.encode_contents()
        self.output = self.output.decode(statement_charset)
        self.output = mathjaxify(self.output)

        # process hint
        note = statement.find('div', {'class': 'note'})
        note.find('div', {'class': 'section-title'}).extract()
        note.find('p').extract()
        self.hint = note.encode_contents()
        self.hint = self.hint.decode(statement_charset)
        self.hint = mathjaxify(self.hint)

        # process sample_input, sample_output
        sample_tests = statement.find('div', {'class': 'sample-tests'})
        example_inputs = statement.find_all('div', {'class': 'input'})
        example_outputs = statement.find_all('div', {'class': 'output'})
        if len(example_inputs) == 1:
            self.example_input = example_inputs[0].find('pre', {'class': 'content'}).text
        else:
            cnt = 1
            for ex in example_inputs:
                self.example_input += 'Sample Input #%d\n' % cnt
                self.example_input += ex.find('pre', {'class': 'content'}).text + '\n\n'
                cnt += 1
        self.example_input = self.example_input.strip()
        if len(example_outputs) == 1:
            self.example_output = example_outputs[0].find('pre', {'class': 'content'}).text
        else:
            cnt = 1
            for ex in example_outputs:
                self.example_output += 'Sample Output #%d\n' % cnt
                self.example_output += ex.find('pre', {'class': 'content'}).text + '\n\n'
                cnt += 1
        self.example_output = self.example_output.strip()
        
        # process tests
        test_count = int(meta.find('test-count').text)
        input_pattern = meta.find('input-path-pattern').text
        output_pattern = meta.find('answer-path-pattern').text
        for i in range(1, test_count + 1):
            inp = z.open(input_pattern % i, 'r')
            inp_tmp = tempfile.TemporaryFile()
            inp_tmp.write(inp.read())
            inp_tmp.seek(0)
            inp.close()

            out = z.open(output_pattern % i,'r')
            out_tmp = tempfile.TemporaryFile()
            out_tmp.write(out.read())
            out_tmp.seek(0)
            out.close()

            self.tests.append((inp_tmp, out_tmp))
        return

    def __del__(self):
        # Not sure auto closing
        for inp, out in self.tests:
            inp.close()
            out.close()

class TIOJ:
    def __init__(self, host):
        self.host = host
        self.session = requests.Session()

    def login(self, username, password):
        sign_in_url = urljoin(self.host, '/users/sign_in')

        rel = self.session.get(sign_in_url)
        soup = BeautifulSoup(rel.text, "html.parser")
        inputs = soup.find('form').find_all('input')
        rel = self.session.post(sign_in_url, data = {
            inputs[0].attrs['name']: inputs[0].attrs['value'],
            inputs[1].attrs['name']: inputs[1].attrs['value'],
            'user[username]': username,
            'user[password]': password,
            'user[remember_me]': '1',
            'commit': 'Sign in'
        })
        return '/users/sign_out' in rel.text

    def create_problem(self, problem):
        # create invisible problem
        problem_new_get_url = urljoin(self.host, '/problems/new')
        problem_new_post_url = urljoin(self.host, '/problems')

        rel = self.session.get(problem_new_get_url)
        soup = BeautifulSoup(rel.text, 'html.parser')
        inputs = soup.find('form').find_all('input')
        rel = self.session.post(problem_new_post_url, data = {
            inputs[0].attrs['name']: inputs[0].attrs['value'],
            inputs[1].attrs['name']: inputs[1].attrs['value'],
            'problem[name]': problem.name,
            'problem[visible_state]': 2,
            'problem[problem_type]': problem.problem_type,
            'problem[description]': problem.description,
            'problem[input]': problem.input,
            'problem[output]': problem.output,
            'problem[example_input]': problem.example_input,
            'problem[example_output]': problem.example_output,
            'problem[hint]': problem.hint,
            'problem[source]': problem.source
        })
        problem_id = int(urlparse(rel.url).path.split('/')[-1])
        return problem_id

    def upload_tests(self, problem_id, problem):
        upload_test_get_url = urljoin(self.host, '/problems/%d/testdata/new' % problem_id)
        upload_test_post_url = urljoin(self.host, '/problems/%d/testdata' % problem_id)

        for inp, out in problem.tests:
            rel = self.session.get(upload_test_get_url)
            soup = BeautifulSoup(rel.text, "html.parser")
            inputs = soup.find('form').find_all('input')

            rel = self.session.post(upload_test_post_url, data = {
                inputs[0].attrs['name']: inputs[0].attrs['value'],
                inputs[1].attrs['name']: inputs[1].attrs['value'],
                'testdatum[limit_attributes][time]': problem.time_limit,
                'testdatum[limit_attributes][memory]': problem.memory_limit,
                'testdatum[limit_attributes][output]': problem.output_limit,
                'testdatum[problem_id]': problem_id,
                'commit': 'Create Testdatum'
            }, files = {
                'testdatum[test_input]': inp,
                'testdatum[test_output]': out
            })
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str)
    parser.add_argument('--url', type=str, default='https://tioji.ck.tp.edu.tw/')
    args = parser.parse_args()

    problem_zip = zipfile.ZipFile(args.filename, 'r')
    prob = Problem()
    prob.fromPolygon(problem_zip)
    problem_zip.close()

    tioj = TIOJ(args.url)
    while True:
        username = input('Username: ')
        password = getpass('Password: ')
        if tioj.login(username, password):
            print('Login OK.')
            break
        print('Login Failed!')
    problem_id = tioj.create_problem(prob)
    print('Invisible problem %d created.' % problem_id)
    print('Uploading %d tests..' % len(prob.tests))
    tioj.upload_tests(problem_id, prob)
    print('Done.')
