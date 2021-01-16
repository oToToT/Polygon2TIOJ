import requests
from urllib.parse import urljoin, urlparse

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

    def update_problem(self, problem_id, problem):
        problem_edit_get_url = urljoin(self.host, '/problems/%d/edit' % problem_id)
        problem_edit_post_url = urljoin(self.host, '/problems/%d' % problem_id)
        rel = self.session.get(problem_edit_get_url)
        soup = BeautifulSoup(rel.text, 'html.parser')
        inputs = soup.find('form').find_all('input')
        
        if problem.problem_type == 0:
            rel = self.session.post(problem_edit_post_url, data = {
                inputs[0].attrs['name']: inputs[0].attrs['value'],
                inputs[1].attrs['name']: inputs[1].attrs['value'],
                inputs[2].attrs['name']: inputs[2].attrs['value'],
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
        elif problem.problem_type == 1:
            rel = self.session.post(problem_edit_post_url, data = {
                inputs[0].attrs['name']: inputs[0].attrs['value'],
                inputs[1].attrs['name']: inputs[1].attrs['value'],
                inputs[2].attrs['name']: inputs[2].attrs['value'],
                'problem[name]': problem.name,
                'problem[visible_state]': 2,
                'problem[problem_type]': problem.problem_type,
                'problem[description]': problem.description,
                'problem[input]': problem.input,
                'problem[output]': problem.output,
                'problem[example_input]': problem.example_input,
                'problem[example_output]': problem.example_output,
                'problem[hint]': problem.hint,
                'problem[source]': problem.source,
                'problem[sjcode]': problem.sjcode
            })
        else:
            raise NotImplementedError
        return

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
        if problem.problem_type == 0:
            pass
        elif problem.problem_type == 1:
            self.update_problem(problem_id, problem)
        else:
            raise NotImplementedError("problem type other than 0, 1 is not supported")
        return problem_id

    def remove_tests(self, problem_id):
        upload_test_get_url = urljoin(self.host, '/problems/%d/testdata/new' % problem_id)
        upload_test_post_url = urljoin(self.host, '/problems/%d/testdata' % problem_id)
        
        cnt = 0
        while True:
            rel = self.session.get(upload_test_post_url)
            soup = BeautifulSoup(rel.text, 'html.parser')
            csrf = soup.find('meta', {'name': 'csrf-token'}).get('content')
            tbody = soup.find('table').find('tbody')
            tds = tbody.find_all('td')
            if len(tds) == 0:
                break
            delete_url = urljoin(self.host, tds[6].find_all('a')[1].get('href'))
            self.session.post(delete_url, data = {
                '_method': 'delete',
                'authenticity_token': csrf
            })
            cnt += 1
        return cnt

    def upload_tests(self, problem_id, problem, remove_all = True):
        upload_test_get_url = urljoin(self.host, '/problems/%d/testdata/new' % problem_id)
        upload_test_post_url = urljoin(self.host, '/problems/%d/testdata' % problem_id)

        if remove_all:
            while True:
                rel = self.session.get(upload_test_post_url)
                soup = BeautifulSoup(rel.text, 'html.parser')
                csrf = soup.find('meta', {'name': 'csrf-token'}).get('content')
                tbody = soup.find('table').find('tbody')
                tds = tbody.find_all('td')
                if len(tds) == 0:
                    break
                delete_url = urljoin(self.host, tds[6].find_all('a')[1].get('href'))
                self.session.post(delete_url, data = {
                    '_method': 'delete',
                    'authenticity_token': csrf
                })

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
