from bs4 import BeautifulSoup
import re
import zipfile
import tempfile

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
        self.sjcode = ''
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
       
        self.problem_type = 1
        self.name = meta.find('name').get('value')
        self.time_limit = int(meta.find('time-limit').text)
        self.memory_limit = int(meta.find('memory-limit').text) // 1024

        # replace testlib to support TIOJ
        checker_path = meta.find('checker').find('source').get('path')
        checker = z.open(checker_path, 'r')
        self.sjcode = checker.read().decode('ascii')
        checker.close()
        # testlib = open('testlib.h', 'r')
        # testlib_code = testlib.read()
        # testlib.close()
        # sj_list = re.split(r'#[ ]*include[ ]*"testlib.h"', self.sjcode)
        # if len(sj_list) == 1:
            # pass
        # elif len(sj_list) == 2:
            # sj_list.insert(0, testlib_code)
        # else:
            # raise NotImplementedError('Parse Filed!!!')
        # self.sjcode = ''.join(sj_list)
        
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
        if input_spec:
            input_spec.find('div', {'class': 'section-title'}).extract()
            input_spec.find('p').extract()
            self.input = input_spec.encode_contents()
            self.input = self.input.decode(statement_charset)
            self.input = mathjaxify(self.input)
        
        # process output
        output_spec = statement.find('div', {'class': 'output-specification'})
        if output_spec:
            output_spec.find('div', {'class': 'section-title'}).extract()
            output_spec.find('p').extract()
            self.output = output_spec.encode_contents()
            self.output = self.output.decode(statement_charset)
            self.output = mathjaxify(self.output)

        # process hint
        note = statement.find('div', {'class': 'note'})
        if note:
            note.find('div', {'class': 'section-title'}).extract()
            note.find('p').extract()
            self.hint = note.encode_contents()
            self.hint = self.hint.decode(statement_charset)
            self.hint = mathjaxify(self.hint)

        # process sample_input, sample_output
        sample_tests = statement.find('div', {'class': 'sample-tests'})
        if sample_tests:
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
