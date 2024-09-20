import unittest

def gen_graph(name, spec, **kwargs):
    # Create a list of strings in the format key=value
    kwargstr_list = [f"{key}={value}" for key, value in kwargs.items()]
    
    # Join the list into a single string with a comma and space separator
    kwargstr = ", ".join(kwargstr_list)
    
    # Return kwargstr for testing purposes
    return kwargstr

class TestGenGraph(unittest.TestCase):
    def test_single_kwarg(self):
        result = gen_graph('bobsagent', None, checkpointer='memory')
        self.assertEqual(result, "checkpointer=memory")

    def test_multiple_kwargs(self):
        result = gen_graph('bobsagent', None, checkpointer='memory', retries=3)
        self.assertEqual(result, "checkpointer=memory, retries=3")

    def test_no_kwargs(self):
        result = gen_graph('bobsagent', None)
        self.assertEqual(result, "")

    def test_special_characters_in_values(self):
        result = gen_graph('bobsagent', None, path='/usr/local/bin', checkpointer='@memory')
        self.assertEqual(result, "path=/usr/local/bin, checkpointer=@memory")

if __name__ == '__main__':
    unittest.main()
