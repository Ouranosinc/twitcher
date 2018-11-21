import json
from collections import deque
from copy import deepcopy
import unittest
import os
from pprint import pformat
import urlparse

import pytest
from mock import mock
from pyramid import testing
from pyramid.testing import DummyRequest
from pywps.inout.inputs import LiteralInput

import twitcher
from twitcher.processes.constants import START_DATE, END_DATE, AOI
from twitcher.datatype import Process
from twitcher.processes import opensearch
from twitcher.store import DB_MEMORY, MemoryProcessStore
from twitcher.utils import get_any_id
from twitcher.wps_restapi.processes import processes

OSDD_URL = "http://geo.spacebel.be/opensearch/description.xml"

COLLECTION_IDS = {
    "sentinel2": "EOP:IPT:Sentinel2",
    "probav": "EOP:VITO:PROBAV_P_V001",
    # "deimos": "DE2_PS3_L1C",
}


def assert_json_equals(json1, json2):
    def ordered_json(obj):
        if isinstance(obj, dict):
            return sorted((unicode(k), ordered_json(v)) for k, v in obj.items())
        elif isinstance(obj, list):
            return sorted(ordered_json(x) for x in obj)
        else:
            return unicode(obj)

    json1_lines = pformat(ordered_json(json1)).split("\n")
    json2_lines = pformat(ordered_json(json2)).split("\n")
    for line1, line2 in zip(json1_lines, json2_lines):
        assert line1 == line2


def get_test_file(*args):
    return os.path.join(os.path.dirname(__file__), *args)


def load_json_test_file(filename):
    return json.load(open(get_test_file("json_examples", filename)))


def make_request(**kw):
    request = DummyRequest(**kw)
    if request.registry.settings is None:
        request.registry.settings = {}
    request.registry.settings["twitcher.url"] = "localhost"
    request.registry.settings["twitcher.wps_path"] = "/ows/wps"
    request.registry.settings["twitcher.db_factory"] = DB_MEMORY
    return request


class WpsHandleEOITestCase(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()


@pytest.fixture
def memory_store():
    hello = twitcher.processes.wps_hello.Hello()
    store = MemoryProcessStore([hello])
    return store


@pytest.fixture
def dummy_payload():
    return {
        "processDescription": {
            "process": {
                "identifier": "workflow_stacker_sfs_id",
                "title": "Application StackCreation followed by SFS dynamically added by POST /processes",
                "owsContext": {
                    "offering": {
                        "code": "http://www.opengis.net/eoc/applicationContext/cwl",
                        "content": {
                            "href": "http://some.host/applications/cwl/multisensor_ndvi.cwl"
                        },
                    }
                },
            }
        }
    }


@pytest.fixture
def opensearch_payload():
    js = load_json_test_file("opensearch_deploy.json")
    return js


@pytest.fixture
def opensearch_process():
    opensearch_process = Process(load_json_test_file("opensearch_process.json"))
    return opensearch_process


@pytest.fixture
def memory_store_with_opensearch_process(memory_store, opensearch_process):
    memory_store.save_process(opensearch_process)
    return memory_store


def test_transform_execute_parameters_wps(opensearch_process):
    def make_input(id_, value):
        input_ = LiteralInput(id_, "", data_type="string")
        input_.data = value
        return input_

    def make_deque(id_, value):
        input_ = make_input(id_, value)
        return id_, deque([input_])

    inputs = dict(
        [
            make_deque(START_DATE, "2018-01-30T00:00:00.000Z"),
            make_deque(END_DATE, "2018-01-31T23:59:59.999Z"),
            make_deque(
                AOI,
                "POLYGON ((100.4 15.3, 104.6 15.3, 104.6 19.3, 100.4 19.3, 100.4 15.3))",
            ),
            make_deque("files", "EOP:IPT:Sentinel2"),
            make_deque("output_file_type", "GEOTIFF"),
            make_deque("output_name", "stack_result.tif"),
        ]
    )

    mocked_query = ["file:///something.SAFE"]
    files_inputs = [make_input("files", "opensearch" + m) for m in mocked_query]

    expected = dict(
        [
            make_deque("output_file_type", "GEOTIFF"),
            make_deque("output_name", "stack_result.tif"),
            ("files", deque(files_inputs)),
        ]
    )

    with mock.patch.object(
        opensearch.OpenSearchQuery, "query_datasets", return_value=mocked_query
    ):
        eo_image_source_info = make_eo_image_source_info("files", "EOP:IPT:Sentinel2")
        transformed = opensearch.query_eo_images_from_wps_inputs(
            inputs, eo_image_source_info
        )

    def compare(items):
        return sorted([(k, [v.data for v in values]) for k, values in items.items()])

    assert compare(transformed) == compare(expected)


def test_load_wkt():
    data = [
        ("POLYGON ((100 15, 104 15, 104 19, 100 19, 100 15))", "100.0,15.0,104.0,19.0"),
        (
            "LINESTRING (100 15, 104 15, 104 19, 100 19, 100 15)",
            "100.0,15.0,104.0,19.0",
        ),
        ("LINESTRING (100 15, 104 19)", "100.0,15.0,104.0,19.0"),
        ("MULTIPOINT ((10 10), (40 30), (20 20), (30 10))", "10.0,10.0,40.0,30.0"),
        ("POINT (30 10)", "30.0,10.0,30.0,10.0"),
    ]
    for wkt, expected in data:
        assert opensearch.load_wkt(wkt) == expected


@mock.patch("twitcher.wps_restapi.processes.processes.processstore_factory")
def test_deploy_opensearch(processstore_factory, opensearch_payload):
    # given
    initial_payload = deepcopy(opensearch_payload)
    request = make_request(json=opensearch_payload, method="POST")
    process_id = get_any_id(opensearch_payload["processDescription"]["process"])

    store = MemoryProcessStore()
    processstore_factory.return_value = store
    # when
    response = processes.add_local_process(request)

    # then
    assert response.code == 200
    assert response.json["deploymentDone"]
    process = store.fetch_by_id(process_id)
    assert process
    assert process.package
    assert process.payload
    assert_json_equals(process.payload, initial_payload)


def test_handle_EOI_unique_aoi_unique_toi():
    inputs = load_json_test_file("eoimage_inputs_example.json")
    expected = load_json_test_file("eoimage_unique_aoi_unique_toi.json")
    output = twitcher.processes.opensearch.EOImageDescribeProcessHandler(
        inputs
    ).to_opensearch(unique_aoi=True, unique_toi=True)
    assert_json_equals(output, expected)


def test_handle_EOI_unique_aoi_non_unique_toi():
    inputs = load_json_test_file("eoimage_inputs_example.json")
    expected = load_json_test_file("eoimage_unique_aoi_non_unique_toi.json")
    output = twitcher.processes.opensearch.EOImageDescribeProcessHandler(
        inputs
    ).to_opensearch(unique_aoi=True, unique_toi=False)
    assert_json_equals(output, expected)


def test_handle_EOI_non_unique_aoi_unique_toi():
    inputs = load_json_test_file("eoimage_inputs_example.json")
    expected = load_json_test_file("eoimage_non_unique_aoi_unique_toi.json")
    output = twitcher.processes.opensearch.EOImageDescribeProcessHandler(
        inputs
    ).to_opensearch(unique_aoi=False, unique_toi=True)
    assert_json_equals(output, expected)


def test_get_additional_parameters():
    data = {
        "additionalParameters": [
            {
                "role": "http://www.opengis.net/eoc/applicationContext",
                "parameters": [
                    {"name": "UniqueAOI", "values": ["true"]},
                    {"name": "UniqueTOI", "values": ["true"]},
                ],
            }
        ]
    }
    params = twitcher.processes.opensearch.get_additional_parameters(data)
    assert ("UniqueAOI", ["true"]) in params
    assert ("UniqueTOI", ["true"]) in params


@pytest.mark.online
def test_get_template_urls():
    all_fields = set()
    for name, collection_id in COLLECTION_IDS.items():
        o = opensearch.OpenSearchQuery(collection_id, osdd_url=OSDD_URL)
        template = o.get_template_url()
        params = urlparse.parse_qsl(urlparse.urlparse(template).query)
        param_names = list(sorted(p[0] for p in params))
        if all_fields:
            all_fields = all_fields.intersection(param_names)
        else:
            all_fields.update(param_names)

    fields_in_all_queries = list(sorted(all_fields))
    expected = [
        "bbox",
        "endDate",
        "geometry",
        "httpAccept",
        "lat",
        "lon",
        "maximumRecords",
        "name",
        "parentIdentifier",
        "radius",
        "startDate",
        "startRecord",
        "uid",
    ]
    assert not set(expected) - set(fields_in_all_queries)


def inputs_unique_aoi_toi(files_id):
    return {
        AOI: deque([LiteralInput(AOI, "Area", data_type="string")]),
        START_DATE: deque(
            [LiteralInput(START_DATE, "Start Date", data_type="string")]
        ),
        END_DATE: deque([LiteralInput(END_DATE, "End Date", data_type="string")]),
        files_id: deque(
            [LiteralInput(files_id, "Collection of the data.", data_type="string")]
        ),
    }


def inputs_non_unique_aoi_toi(files_id):
    def make_specific(name):
        return opensearch._make_specific_identifier(name, files_id)

    end_date, start_date, aoi = map(make_specific, [END_DATE, START_DATE, AOI])
    return {
        aoi: deque([LiteralInput(aoi, "Area", data_type="string")]),
        start_date: deque([LiteralInput(start_date, "Area", data_type="string")]),
        end_date: deque([LiteralInput(end_date, "Area", data_type="string")]),
        files_id: deque(
            [LiteralInput(files_id, "Collection of the data.", data_type="string")]
        ),
    }


def query_param_names(unique_aoi_toi, identifier):
    end_date, start_date, aoi = END_DATE, START_DATE, AOI
    if not unique_aoi_toi:
        end_date = opensearch._make_specific_identifier(end_date, identifier)
        start_date = opensearch._make_specific_identifier(start_date, identifier)
        aoi = opensearch._make_specific_identifier(aoi, identifier)
    return end_date, start_date, aoi


def sentinel2_inputs(unique_aoi_toi=True):
    sentinel_id = "image-sentinel2"
    end_date, start_date, aoi = query_param_names(unique_aoi_toi, sentinel_id)
    if unique_aoi_toi:
        inputs = inputs_unique_aoi_toi(sentinel_id)
    else:
        inputs = inputs_non_unique_aoi_toi(sentinel_id)

    inputs[sentinel_id][0].data = "EOP:IPT:Sentinel2"
    inputs[end_date][0].data = u"2018-01-31T23:59:59.999Z"
    inputs[start_date][0].data = u"2018-01-30T00:00:00.000Z"
    inputs[aoi][0].data = u"POLYGON ((100 15, 104 15, 104 19, 100 19, 100 15))"

    eo_image_source_info = make_eo_image_source_info(sentinel_id, "EOP:IPT:Sentinel2")
    return inputs, eo_image_source_info


def probav_inputs(unique_aoi_toi=True):
    probav_id = "image-probav"
    end_date, start_date, aoi = query_param_names(unique_aoi_toi, probav_id)
    if unique_aoi_toi:
        inputs = inputs_unique_aoi_toi(probav_id)
    else:
        inputs = inputs_non_unique_aoi_toi(probav_id)

    inputs[probav_id][0].data = "EOP:VITO:PROBAV_P_V001"
    inputs[end_date][0].data = u"2018-01-31T23:59:59.999Z"
    inputs[start_date][0].data = u"2018-01-30T00:00:00.000Z"
    inputs[aoi][0].data = u"POLYGON ((100 15, 104 15, 104 19, 100 19, 100 15))"

    eo_image_source_info = make_eo_image_source_info(
        probav_id, "EOP:VITO:PROBAV_P_V001"
    )

    return inputs, eo_image_source_info


def make_eo_image_source_info(name, collection_id):
    return {
        name: {
            "collection_id": collection_id,
            "accept_schemes": ["http", "https"],
            "rootdir": "",
            "ades": "http://localhost:5001",
            "osdd_url": "http://geo.spacebel.be/opensearch/description.xml",
        }
    }


def deimos_inputs(unique_aoi_toi=True):
    deimos_id = "image-deimos"
    end_date, start_date, aoi = query_param_names(unique_aoi_toi, deimos_id)
    inputs = inputs_unique_aoi_toi(deimos_id)

    inputs[deimos_id][0].data = "DE2_PS3_L1C"
    inputs[start_date][0].data = u"2008-01-01T00:00:00Z"
    inputs[end_date][0].data = u"2009-01-01T00:00:00Z"
    inputs[aoi][0].data = u"MULTIPOINT ((-117 32), (-115 34))"

    eo_image_source_info = make_eo_image_source_info(deimos_id, "DE2_PS3_L1C")
    return inputs, eo_image_source_info


@pytest.mark.online
def test_query_sentinel2():
    inputs, eo_image_source_info = sentinel2_inputs()

    data = opensearch.query_eo_images_from_wps_inputs(inputs, eo_image_source_info)

    assert 15 == len(data["image-sentinel2"])


@pytest.mark.online
def test_query_probav():
    inputs, eo_image_source_info = probav_inputs()

    data = opensearch.query_eo_images_from_wps_inputs(inputs, eo_image_source_info)

    assert 3 == len(data["image-probav"])


@pytest.mark.skip(reason="The server is not implemented yet.")
@pytest.mark.online
def test_query_deimos():
    inputs, eo_image_source_info = deimos_inputs()

    data = opensearch.query_eo_images_from_wps_inputs(inputs, eo_image_source_info)

    assert 999 == len(data["image-deimos"])


@pytest.mark.online
def test_query_non_unique():
    inputs_s2, eo_image_source_info_s2 = sentinel2_inputs(unique_aoi_toi=False)
    inputs_probav, eo_image_source_info_probav = probav_inputs(unique_aoi_toi=False)

    inputs = inputs_s2
    inputs.update(inputs_probav)

    eo_image_source_info = eo_image_source_info_s2
    eo_image_source_info.update(eo_image_source_info_probav)

    data = opensearch.query_eo_images_from_wps_inputs(inputs, eo_image_source_info)

    assert len(data["image-sentinel2"]) == 15
    assert len(data["image-probav"]) == 3