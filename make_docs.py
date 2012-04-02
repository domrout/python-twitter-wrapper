#!/usr/bin/env python

"""Generates markdown documentation for YAML API specification."""

import twitterwrapper, yaml,re 

DOCUMENT_YAML = "twitterwrapper/api.yaml"
OUTPUT_API_LOCATION = "API.markdown"
OUTPUT_MODEL_LOCATION = "MODELS.markdown"

API_DOC_BASE = "https://dev.twitter.com/docs/api/1"

with open(DOCUMENT_YAML) as f:
	api_spec = yaml.load(f.read())

def make_doc_url(url, post):
	if post:
		return "%s/post/%s" % (API_DOC_BASE, url)
	else:
		return "%s/get/%s" % (API_DOC_BASE, url)


def escape_markdown(s):
	return re.sub(r"([_])", r"\\\1", s)
def remove_matches(s):	
	return re.sub(r"\%\(([a-z]+)\)s", r":\1", s)

def output_endpoint(f, endpoint, content, nesting = 2, path_to=["api"], model = None):
	path_to = path_to + [escape_markdown(endpoint)]
	if "model" in content:
		model = content["model"] 
		if model == "None":
			model = None

	if "url" in content:
		print >> f, "#" * nesting + ".".join(path_to[1:])

		post = True if "post" in content and content["post"] else False

		content["url"] = remove_matches(content["url"])
		doc_url = make_doc_url(content["url"], post)
		if post:		
			print >> f, "[POST %s](%s)" % (escape_markdown(content["url"]), doc_url)
		else:
			print >> f, "[GET %s](%s)" % (escape_markdown(content["url"]), doc_url)

		print >> f, ""

		if "doc" in content:
			print >> f, escape_markdown(content["doc"])
			print >> f, ""

		if "example_params" in content:
			display_params = content["example_params"]
		elif "default_param" in content:
			display_params = content["default_param"]
		else:
			display_params = ""

		display_params = escape_markdown(display_params)
		print >> f, "Example use: %s(%s)" %(".".join(path_to), display_params)
		print >> f, ""

		if model: 
			print >> f, "Returns **%s** object" % model

	else:
		print >> f, "#" * nesting + escape_markdown(endpoint)

		if "doc" in content:
			print >> f, escape_markdown(content["doc"])
			print >> f, ""

	if "contains" in content:		
		for k, v in content["contains"].iteritems():
			output_endpoint(f, k, v, 
				nesting = nesting + 1, 
				path_to=path_to,
				model=model)


with open(OUTPUT_API_LOCATION, "w") as f:
	print >> f, """#API calls"""
	print >> f, """API calls are as detailed at 
		[https://dev.twitter.com/docs/api](https://dev.twitter.com/docs/api)"""
	print >> f, ""
	for endpoint, content in sorted(api_spec.items()):
		# Ignore classes at first.
		if not re.match(r"[A-Z].*", endpoint):
			output_endpoint(f, endpoint, content)

with open(OUTPUT_MODEL_LOCATION, "w") as f:
	print >> f, """#Model objects"""
	print >> f, """This calls, detailed at
		[https://dev.twitter.com/docs/api](https://dev.twitter.com/docs/api)
		will be available for use inside objects returned by the API."""
	print >> f, ""
	for model, content in sorted(api_spec.items()):
		# Ignore classes at first.

		if re.match(r"[A-Z].*", model):
			print >> f, "##%s" % model

			for endpoint, endpoint_content in sorted(content.items()):
				output_endpoint(f, endpoint, endpoint_content, path_to=[model.lower()], nesting=3)