import unittest, yaml, twitterwrapper, os
from functools import partial
from attrdict import AttrDict
class DummyConnection:
    """Replaces some of the methods of the connection object for testing purposes"""
    def __init__(self):
        self.response = AttrDict(
            {
            "status_code": 200, 
            "headers": {
                "X-Rate-Limit-Remaining": 100
            },
            "json": lambda: {}})

    def get(self, url, **other_params):
        self.lastUrl = url
        self.lastParams = other_params

        return self.get_result()

    def post(self, url, **other_params):
        self.lastUrl = url
        self.lastParams = other_params

        return self.get_result()

    def PrefixURL(self, url):
        return url

    def _BuildUrl(self, url):
        return url

    def set_result(self, result):
        response = AttrDict()
        response["status_code"] = 200
        response["headers"] = {
                "X-Rate-Limit-Remaining": 100
            }

        response["json"] = lambda: result
        self.response = response

    def get_result(self):
        return self.response

    def is_url(self, url):
        return self.lastUrl== twitterwrapper.Api.BASE_URL + "/" + url + ".json"

class ApiMethodTests(unittest.TestCase):
    API_FILE = "tests/fixtures/api.yaml"
    FIXTURE_FILE = "tests/fixtures/base.yaml"

    def setUp(self):
        with open(self.API_FILE) as f:
            specification = yaml.load(f)

        self.dummy = DummyConnection()

        self.api = twitterwrapper.Api(specification=specification, connection=self.dummy)

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
    API_FILE = "tests/fixtures/yaml_loading_tests.yaml" 

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
        self.assertTrue("data" in self.dummy.lastParams)
        self.assertTrue("def_param" in self.dummy.lastParams["data"])
        self.assertTrue("some_param" in self.dummy.lastParams["data"])

        self.assertEqual(self.dummy.lastParams["data"]["some_param"], 0)

        child(1, some_param=0)
        # Check that the child wasn't still set as POST
        self.assertFalse("data" in self.dummy.lastParams)
        self.assertTrue("params" in self.dummy.lastParams)
        # Also check that default parameter wasn't still set.
        self.assertFalse("def_param" in self.dummy.lastParams["params"])
        self.assertTrue("some_param" in self.dummy.lastParams["params"])
        self.assertEqual(self.dummy.lastParams["params"]["some_param"], 0)

    def test_dont_inherit_url(self):
        self.api.not_inheriting_url()
        self.assertRaises(TypeError, self.api.not_inheriting_url.descendent)

class RequestTests(ApiMethodTests):
    """Tests the ability to correctly form and make requests"""
    API_FILE = "tests/fixtures/request_tests.yaml" 

    def test_basic(self):
        self.api.basic()
        self.assertUrl("basic")
        self.assertEquals(self.dummy.lastParams["params"], dict())
        self.assertFalse("data" in self.dummy.lastParams)

    def test_basic_post(self):
        self.api.post_basic()
        self.assertUrl("post_basic")

        self.assertEquals(self.dummy.lastParams["data"], dict())
        self.assertFalse("params" in self.dummy.lastParams)

    def test_extra_params(self):
        self.api.basic(param="hello")
        self.assertUrl("basic")

        self.assertEquals(
            self.dummy.lastParams["params"], 
            {"param":"hello"})

    def test_extra_params_post(self):
        self.api.post_basic(param="hello")
        self.assertUrl("post_basic")
        
        self.assertEquals(
            self.dummy.lastParams["data"], 
            {"param":"hello"})

    def test_url_matching(self):
        self.api.url_with_matches(a="what", b="hello")
        self.assertUrl("match/what/this/hello")

    def test_callable_parent(self):
        self.api.callable_parent()
        self.assertUrl("callable_parent")

        self.api.callable_parent.child()
        self.assertUrl("child")


    def test_not_callable_parent(self):      
        self.assertRaises(TypeError, self.api.not_callable_parent)
        self.api.not_callable_parent.child()
        self.assertUrl("child")

    def test_plural_singular_results(self): 
        self.dummy.set_result(self.fixture["status"])

        self.assertTrue(isinstance(self.api.test_status(), twitterwrapper.models.Status))

        self.dummy.set_result(self.fixture["many_statuses"])
        result = self.api.test_status()
        self.assertTrue(isinstance(result, list))
        # Every returned tweet should have the right type
        for s in result:
            self.assertTrue(isinstance(s, twitterwrapper.models.Status))

    def test_default_param_id(self):
        self.api.with_default_param_id(1234)
        self.assertUrl("with_default_param_id")
        self.assertEquals(
            self.dummy.lastParams["params"], 
            {"id":1234}
        )

    def test_default_param_other(self):
        self.api.with_default_param("boxesofbeans")

        self.assertUrl("with_default_param")
        self.assertEquals(
            self.dummy.lastParams["params"], 
            {"def_param":"boxesofbeans"}
        )

    def test_default_param_in_url(self):
        self.api.with_default_param_in_url("boxesofbeans")
        
        self.assertUrl("with_default_param/boxesofbeans")
        # IT would be nice to remove params that were used in the URL.
        # But doing so would heavily complicate the YAML syntax for the API:
        # self.assertEquals(self.dummy.lastParams["params"], dict())

class ModelBlessingTests(ApiMethodTests):
    """Tests that models are blessed properly."""
    API_FILE = "tests/fixtures/model_blessing_tests.yaml" 

    def setUp(self):
        ApiMethodTests.setUp(self)

        # Use a status object for the return value.
        self.dummy.set_result(self.fixture["status"])
        self.status = self.api.test_status()

    def test_attachment_shallow(self):
        self.status.shallow_call()
        self.assertUrl("shallow_call")

        # Shouldn't be supplying any extra data at this point.
        self.assertEquals(self.dummy.lastParams["params"], dict())
        self.assertFalse("data" in self.dummy.lastParams)

    def test_attachment_deep(self):
        self.status.deep_call_parent.deep_call_child()
        self.assertUrl("deep_call_child")    

    def test_container_id_shallow(self):
        self.status.post_with_container_id()
        self.assertUrl("post_with_container_id")
        self.assertEqual(self.dummy.lastParams["data"]["status_id"], self.status.id)

        self.status.get_with_container_id()
        self.assertUrl("get_with_container_id")
        self.assertEqual(self.dummy.lastParams["params"]["status_id"], self.status.id)

    def test_container_id_deep(self):
        self.status.deep_call_parent.deep_post_with_container_id()
        self.assertUrl("deep_post_with_container_id")
        self.assertEqual(self.dummy.lastParams["data"]["status_id"], self.status.id)

        self.status.deep_call_parent.deep_get_with_container_id()
        self.assertUrl("deep_get_with_container_id")
        self.assertEqual(self.dummy.lastParams["params"]["status_id"], self.status.id)

    def test_id_in_url(self):
        self.status.should_insert_id()
        self.assertUrl("should_insert_id/%s" % self.status.id)


    def test_other_in_url(self):
        self.status.should_insert_text()
        self.assertUrl("should_insert_text/%s" % self.status.text)


if __name__ == '__main__':
    loader = unittest.TestLoader()

    suite = loader.loadTestsFromTestCase(YAMLLoadingTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = loader.loadTestsFromTestCase(RequestTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

    suite = loader.loadTestsFromTestCase(ModelBlessingTests)
    unittest.TextTestRunner(verbosity=2).run(suite)


