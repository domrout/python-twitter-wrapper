import twitterwrapper, unittest, yaml
from functools import partial

class DummyConnection:
    """Replaces some of the methods of the connection object for testing purposes"""
    def __init__(self, connection):
        self.connection = connection
        self.result = dict()
        self.register()

    def register(self):
        self.true_fetch = self.connection.FetchUrl
        self.true_prefix = self.connection.PrefixURL
        self.true_build = self.connection._BuildUrl

        self.connection.FetchUrl = self.FetchUrl
        self.connection.PrefixURL = self.PrefixUrl
        self.connection._BuildUrl = self._BuildUrl

    def unregister(self):
        self.connection.FetchUrl = self.true_fetch
        self.connection.PrefixURL = self.PrefixUrl
        self.connection._BuildUrl = self._BuildUrl

    def FetchUrl(self, url, **other_params):
        self.lastUrl = url
        self.lastParams = other_params

        return self.get_result()

    def PrefixUrl(self, url):
        return url

    def _BuildUrl(self, url):
        return url

    def set_result(self, result):
        self.result = result

    def get_result(self):
        return self.result

    def is_url(self, url):
        return self.lastUrl == url

class ApiMethodTests(unittest.TestCase):
    API_FILE = "fixtures/api.yaml"
    FIXTURE_FILE = "fixtures/base.yaml"

    def setUp(self):
        with open(self.API_FILE) as f:
            specification = yaml.load(f)

        self.api = twitterwrapper.Api(specification=specification)

        self.dummy = DummyConnection(self.api._connection)
        self._load_fixture(self.FIXTURE_FILE)

    def _load_fixture(self, fixture):
        with open(fixture) as f:
            self.fixture = yaml.load(f)

        return self.fixture

    def assertUrl(self, url):
        self.assertTrue(self.dummy.is_url(url))

    def assertInstanceOf(self, a, t):
        self.assertTrue(isinstance(a, t))
        
class YAMLLoadingTests(ApiMethodTests):
    """Tests the loading and correct use of the API spec files"""
    API_FILE = "fixtures/yaml_loading_api.yaml" # I'm so certain this wouldn't work in another language.

    def test_shallow_loading(self):
        self.assertTrue(hasattr(self.api, 'shallow_method'))
        self.api.shallow_method()

        self.assertUrl("tests/shallow_method")

    def test_nested_loading(self):
        parent = self.api.nested_methods

        parent.nested_1() # Make the actual call - ensures tests are less brittle
        self.assertUrl("tests/nested_1")

        parent.nested_2() 
        self.assertUrl("tests/nested_2")

        parent.nested_3() 
        self.assertUrl("tests/nested_3")

    def test_very_nested_loading(self):
        parent = self.api.very_nested_methods
        parent.nested_1.very_nested()
        self.assertUrl("tests/very_nested")

        parent.nested_2.very_nested()
        self.assertUrl("tests/very_nested_2")

    def test_inherit_model(self):
        self.assertInstanceOf(self.api.inherited_model(), twitterwrapper.models.Status)
        self.assertInstanceOf(self.api.inherited_model.descendent(), twitterwrapper.models.Status)

    def test_overwrite_model(self):
        self.assertInstanceOf(self.api.not_inherited_model(), twitterwrapper.models.Status)
        self.assertInstanceOf(self.api.not_inherited_model.descendent(), twitterwrapper.models.User)

        self.assertInstanceOf(self.api.not_inherited_model(), twitterwrapper.models.Status)
        self.assertInstanceOf(self.api.not_inherited_model.emancipated_descendent(), dict)

    def test_inherit_doc(self):
        self.assertEqual(self.api.inherited_model.__doc__, 'HELLOBEAR')
        self.assertEqual(self.api.inherited_model.descendent.__doc__, "HELLOBEAR")

    def test_dont_inherit_others(self):
        # This might not be easy!
        parent = self.api.not_inheriting_others
        child = parent.descendent

        parent(1, some_param=0)
        parent_url = self.dummy.lastUrl

        # Assert that the last request was as described
        self.assertTrue("post_data" in self.dummy.lastParams)
        self.assertTrue("def_param" in self.dummy.lastParams["post_data"])
        self.assertTrue("some_param" in self.dummy.lastParams["post_data"])

        self.assertEqual(self.dummy.lastParams["post_data"]["some_param"], 0)

        child(1, some_param=0)
        # Check that the child wasn't still set as POST
        self.assertFalse("post_data" in self.dummy.lastParams)
        self.assertTrue("parameters" in self.dummy.lastParams)
        # Also check that default parameter wasn't still set.
        self.assertFalse("def_param" in self.dummy.lastParams["parameters"])
        self.assertTrue("some_param" in self.dummy.lastParams["parameters"])
        self.assertEqual(self.dummy.lastParams["parameters"]["some_param"], 0)

    def test_dont_inherit_url(self):
        self.api.not_inheriting_url()
        self.assertRaises(TypeError, self.api.not_inheriting_url.descendent)






    # def test_callable(self):
    #     self.api.basic.basic_call()
    #     #self.assertTrue(isinstance(result, twitterwrapper.models.Status))

    # def test_result(self):
    #     self.dummy.set_result(self.fixture["status"])
    #     result = self.api.basic.basic_call()

    #     self.assertTrue(isinstance(result, twitterwrapper.models.Status))

    #     self.assertEqual(result.text, self.fixture["status"]["text"])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(YAMLLoadingTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

