"""
This module should contain any and every definitions in use to build the swagger UI,
so that one can update the swagger without touching any other files after the initial integration
"""
from twitcher.wps_restapi.utils import wps_restapi_base_path
from twitcher.status import status_values, STATUS_ACCEPTED
from twitcher.sort import sort_values, SORT_CREATED
from cornice import Service
from colander import *


API_TITLE = 'Twitcher REST API'


#########################################################################
# API endpoints
#########################################################################

api_frontpage_uri = '/'
api_swagger_ui_uri = '/api'
api_swagger_json_uri = '/json'
api_versions_uri = '/versions'

providers_uri = '/providers'
provider_uri = '/providers/{provider_id}'

provider_processes_uri = '/providers/{provider_id}/processes'
provider_process_uri = '/providers/{provider_id}/processes/{process_id}'

jobs_short_uri = '/jobs'
jobs_full_uri = '/providers/{provider_id}/processes/{process_id}/jobs'
job_full_uri = '/providers/{provider_id}/processes/{process_id}/jobs/{job_id}'
job_exceptions_uri = '/providers/{provider_id}/processes/{process_id}/jobs/{job_id}/exceptions'
job_short_uri = '/jobs/{job_id}'

results_full_uri = '/providers/{provider_id}/processes/{process_id}/jobs/{job_id}/results'
results_short_uri = '/jobs/{job_id}/results'
result_full_uri = '/providers/{provider_id}/processes/{process_id}/jobs/{job_id}/results/{result_id}'
result_short_uri = '/jobs/{job_id}/results/{result_id}'

exceptions_full_uri = '/providers/{provider_id}/processes/{process_id}/jobs/{job_id}/exceptions'
exceptions_short_uri = '/jobs/{job_id}/exceptions'

logs_full_uri = '/providers/{provider_id}/processes/{process_id}/jobs/{job_id}/logs'
logs_short_uri = '/jobs/{job_id}/logs'

#########################################################
# API tags
#########################################################

api_tag = 'API'
jobs_tag = 'Jobs'
provider_processes_tag = 'Provider Processes'
providers_tag = 'Providers'
getcapabilities_tag = 'GetCapabilities'
describeprocess_tag = 'DescribeProcess'
execute_tag = 'Execute'
dismiss_tag = 'Dismiss'
status_tag = 'Status'
results_tag = 'Results'
exceptions_tag = 'Exceptions'
logs_tag = 'Logs'

###############################################################################
# These "services" are wrappers that allow Cornice to generate the api's json
###############################################################################

api_frontpage_service = Service(name='api_frontpage', path=api_frontpage_uri)
api_swagger_ui_service = Service(name='api_swagger_ui', path=api_swagger_ui_uri)
api_swagger_json_service = Service(name='api_swagger_json', path=api_swagger_json_uri)
api_versions_service = Service(name='api_versions', path=api_versions_uri)

providers_service = Service(name='providers', path=providers_uri)
provider_service = Service(name='provider', path=provider_uri)

provider_processes_service = Service(name='provider_processes', path=provider_processes_uri)
provider_process_service = Service(name='provider_process', path=provider_process_uri)

jobs_short_service = Service(name='jobs_short', path=jobs_short_uri)
jobs_full_service = Service(name='jobs_full', path=jobs_full_uri)
job_full_service = Service(name='job_full', path=job_full_uri)
job_short_service = Service(name='job_short', path=job_short_uri)

results_full_service = Service(name='results_full', path=results_full_uri)
results_short_service = Service(name='results_short', path=results_short_uri)
result_full_service = Service(name='result_full', path=result_full_uri)
result_short_service = Service(name='result_short', path=result_short_uri)

exceptions_full_service = Service(name='exceptions_full', path=exceptions_full_uri)
exceptions_short_service = Service(name='exceptions_short', path=exceptions_short_uri)

logs_full_service = Service(name='logs_full', path=logs_full_uri)
logs_short_service = Service(name='logs_short', path=logs_short_uri)

#########################################################
# Path parameter definitions
#########################################################

provider_id = SchemaNode(String(), description='The provider id')
process_id = SchemaNode(String(), description='The process id')
job_id = SchemaNode(String(), description='The job id')
result_id = SchemaNode(String(), description='The result id')

#########################################################
# Generic schemas
#########################################################


class JsonHeader(MappingSchema):
    content_type = SchemaNode(String(), example='application/json', default='application/json')
    content_type.name = 'Content-Type'


class HtmlHeader(MappingSchema):
    content_type = SchemaNode(String(), example='text/html', default='text/html')
    content_type.name = 'Content-Type'


class XmlHeader(MappingSchema):
    content_type = SchemaNode(String(), example='application/xml', default='application/xml')
    content_type.name = 'Content-Type'


# TODO:
# return XML when Accept=application/xml, add header=AcceptHeader() to 'request' MappingSchema (create for GETs)
# only HTTPExceptions >= 400 properly do it using tweens because of the formatter, HTTP 2xx/3xx are always JSON
# for how to generate doc with content-type specific responses (create the selector in swagger-ui), see:
#   https://github.com/Cornices/cornice.ext.swagger/blob/master/docs/source/tutorial.rst#extracting-produced-types-from-renderers
class AcceptHeader(MappingSchema):
    # 'default' is json since 'return HTTP*(json={})' are used
    Accept = SchemaNode(String(), missing=drop, default='application/json', validator=OneOf([
        'application/json',
        #'application/xml',
        #'text/html'
    ]))


class KeywordList(SequenceSchema):
    keyword = SchemaNode(String())


class MetadataObject(MappingSchema):
    role = SchemaNode(String(), missing=drop)
    href = SchemaNode(String(), missing=drop)


class MetadataList(SequenceSchema):
    metadata = MetadataObject()


class FormatObject(MappingSchema):
    mimeType = SchemaNode(String())
    schema = SchemaNode(String(), missing=drop)
    encoding = SchemaNode(String(), missing=drop)
    maximumMegabytes = SchemaNode(Integer(), missing=drop)
    default = SchemaNode(Boolean(), missing=drop, default=False)


class FormatList(SequenceSchema):
    format = FormatObject()


class LiteralDataDomainObject(MappingSchema):
    pass


class BaseTypeBody(MappingSchema):
    identifier = SchemaNode(String())
    title = SchemaNode(String(), missing=drop)
    abstract = SchemaNode(String(), missing=drop)
    keywords = KeywordList(missing=drop)
    metadata = MetadataList(missing=drop)
    formats = FormatList()
    minOccurs = SchemaNode(Integer(), missing=drop)
    maxOccurs = SchemaNode(Integer(), missing=drop)


class LiteralInputTypeBody(BaseTypeBody):
    LiteralDataDomain = LiteralDataDomainObject(missing=drop)


class ComplexInputTypeBody(BaseTypeBody):
    pass


class BoundingBoxInputTypeBody(BaseTypeBody):
    pass


class InputTypeBody(BaseTypeBody):
    # TODO: figure out how to do OneOf
    # item = MappingSchema(validator=OneOf([LiteralInputTypeBody, ComplexInputTypeBody, BoundingBoxInputTypeBody]))
    pass


class InputTypeList(SequenceSchema):
    input = InputTypeBody()


class OutputTypeBody(BaseTypeBody):
    pass


class OutputTypeList(SequenceSchema):
    output = OutputTypeBody()


JobControlOptionsEnum = SchemaNode(String(), validator=OneOf(['sync-execute', 'async-execute']), missing=drop)
OutputTransmissionEnum = SchemaNode(String(), validator=OneOf(['value', 'reference']), missing=drop)


class LaunchJobQuerystring(MappingSchema):
    sync_execute = SchemaNode(Boolean(), default=False, missing=drop)
    sync_execute.name = 'sync-execute'
    field_string = SchemaNode(String(), default=None, missing=drop,
                              description='Comma separated tags that can be used to filter jobs later')
    field_string.name = 'tags'


#########################################################
# These classes define each of the endpoints parameters
#########################################################


class FrontpageEndpoint(MappingSchema):
    header = AcceptHeader()


class VersionsEndpoint(MappingSchema):
    header = AcceptHeader()


class SwaggerJsonEndpoint(MappingSchema):
    header = AcceptHeader()


class ProviderEndpoint(MappingSchema):
    header = AcceptHeader()
    provider_id = provider_id


class ProcessEndpoint(MappingSchema):
    header = AcceptHeader()
    provider_id = provider_id
    process_id = process_id


class FullJobEndpoint(MappingSchema):
    header = AcceptHeader()
    provider_id = provider_id
    process_id = process_id
    job_id = job_id


class ShortJobEndpoint(MappingSchema):
    header = AcceptHeader()
    job_id = job_id


class FullResultsEndpoint(MappingSchema):
    header = AcceptHeader()
    provider_id = provider_id
    process_id = process_id
    job_id = job_id


class ShortResultsEndpoint(MappingSchema):
    header = AcceptHeader()
    provider_id = provider_id
    process_id = process_id
    job_id = job_id


class FullResultEndpoint(MappingSchema):
    header = AcceptHeader()
    provider_id = provider_id
    process_id = process_id
    job_id = job_id
    result_id = result_id


class ShortResultEndpoint(MappingSchema):
    header = AcceptHeader()
    job_id = job_id
    result_id = result_id


class FullExceptionsEndpoint(MappingSchema):
    header = AcceptHeader()
    provider_id = provider_id
    process_id = process_id
    job_id = job_id


class ShortExceptionsEndpoint(MappingSchema):
    header = AcceptHeader()
    job_id = job_id


class FullLogsEndpoint(MappingSchema):
    header = AcceptHeader()
    provider_id = provider_id
    process_id = process_id
    job_id = job_id


class ShortLogsEndpoint(MappingSchema):
    header = AcceptHeader()
    job_id = job_id


##################################################################
# These classes define schemas for requests that feature a body
##################################################################


class CreateProviderRequestBody(MappingSchema):
    id = SchemaNode(String())
    url = SchemaNode(String())
    public = SchemaNode(Boolean())


class JobInput(MappingSchema):
    id = SchemaNode(String())
    value = SchemaNode(String())
    type = SchemaNode(String())


class JobOutput(MappingSchema):
    id = SchemaNode(String())
    type = SchemaNode(String())


class JobInputList(SequenceSchema):
    item = JobInput()


class JobOutputList(SequenceSchema):
    item = JobOutput()


class ProviderSummarySchema(MappingSchema):
    """WPS provider summary definition."""
    id = SchemaNode(String())
    url = SchemaNode(String())
    title = SchemaNode(String())
    abstract = SchemaNode(String())
    public = SchemaNode(Boolean())


class ProviderCapabilitiesSchema(MappingSchema):
    """WPS provider capabilities."""
    id = SchemaNode(String())
    url = SchemaNode(String())
    title = SchemaNode(String())
    abstract = SchemaNode(String())
    contact = SchemaNode(String())
    type = SchemaNode(String())


class ProcessSummarySchema(MappingSchema):
    """WPS process definition."""
    identifier = SchemaNode(String())
    title = SchemaNode(String())
    abstract = SchemaNode(String())
    keywords = KeywordList(missing=drop)
    metadata = MetadataList(missing=drop)
    executeEndpoint = SchemaNode(String(), missing=drop)    # URL


class ProcessListSchema(SequenceSchema):
    process = ProcessSummarySchema(missing=drop)


class ProviderSummaryProcessesSchema(ProviderSummarySchema):
    processes = ProcessListSchema()


class ProviderProcessListSchema(SequenceSchema):
    provider = ProviderSummaryProcessesSchema(missing=drop)


class ProcessDetailSchema(MappingSchema):
    identifier = SchemaNode(String())
    title = SchemaNode(String(), missing=drop)
    abstract = SchemaNode(String(), missing=drop)
    keywords = KeywordList(missing=drop)
    metadata = MetadataList(missing=drop)
    inputs = InputTypeList(missing=drop)
    outputs = OutputTypeList(missing=drop)
    version = SchemaNode(String(), missing=drop)
    jobControlOptions = JobControlOptionsEnum
    outputTransmission = OutputTransmissionEnum
    executeEndpoint = SchemaNode(String(), missing=drop)    # URL


class ProcessOutputDescriptionSchema(MappingSchema):
    """WPS process output definition."""
    dataType = SchemaNode(String())
    defaultValue = SchemaNode(Mapping())
    id = SchemaNode(String())
    abstract = SchemaNode(String())
    title = SchemaNode(String())


JobStatusEnum = SchemaNode(
    String(),
    default=None,
    validator=OneOf(status_values),
    example=STATUS_ACCEPTED)
JobSortEnum = SchemaNode(
    String(),
    missing=drop,
    default=SORT_CREATED,
    validator=OneOf(sort_values),
    example=SORT_CREATED)


class GetJobsQueries(MappingSchema):
    detail = SchemaNode(Boolean(), description="Provide job details instead of IDs.", default=False, example=True)
    page = SchemaNode(Integer(), missing=drop, default=0)
    limit = SchemaNode(Integer(), missing=drop, default=10)
    status = JobStatusEnum
    process = SchemaNode(String(), missing=drop, default=None)
    provider = SchemaNode(String(), missing=drop, default=None)
    sort = JobSortEnum
    tags = SchemaNode(String(), missing=drop, default=None,
                      description='Comma-separated values of tags assigned to jobs')


class GetJobsRequest(MappingSchema):
    header = AcceptHeader()
    querystring = GetJobsQueries()


class SingleJobStatusSchema(MappingSchema):
    status = JobStatusEnum
    message = SchemaNode(String(), example='Job {}.'.format(STATUS_ACCEPTED))
    progress = SchemaNode(Integer(), example=0)
    exceptions = SchemaNode(String(), missing=drop,
                            example='http://twitcher/providers/my-wps/processes/my-process/jobs/my-job/exceptions')
    outputs = SchemaNode(String(), missing=drop,
                         example='http://twitcher/providers/my-wps/processes/my-process/jobs/my-job/outputs')
    logs = SchemaNode(String(), missing=drop,
                      example='http://twitcher/providers/my-wps/processes/my-process/jobs/my-job/logs')


class JobListSchema(SequenceSchema):
    job = SchemaNode(String(), description='Job ID.')


class GetAllJobsSchema(MappingSchema):
    count = SchemaNode(Integer())
    jobs = JobListSchema()
    limit = SchemaNode(Integer())
    page = SchemaNode(Integer())


class DismissedJobSchema(MappingSchema):
    status = JobStatusEnum
    message = SchemaNode(String(), example='Job dismissed.')
    progress = SchemaNode(Integer(), example=0)


class SupportedValues(MappingSchema):
    pass


class DefaultValues(MappingSchema):
    pass


class ProcessInputDescriptionSchema(MappingSchema):
    minOccurs = SchemaNode(Integer())
    maxOccurs = SchemaNode(Integer())
    title = SchemaNode(String())
    dataType = SchemaNode(String())
    abstract = SchemaNode(String())
    id = SchemaNode(String())
    defaultValue = SequenceSchema(DefaultValues())
    supportedValues = SequenceSchema(SupportedValues())


class ProcessDescriptionSchema(MappingSchema):
    outputs = SequenceSchema(ProcessOutputDescriptionSchema())
    inputs = SequenceSchema(ProcessInputDescriptionSchema())
    description = SchemaNode(String())
    id = SchemaNode(String())
    label = SchemaNode(String())


class ProvidersSchema(SequenceSchema):
    providers_service = ProviderSummarySchema()


class ProcessesSchema(SequenceSchema):
    provider_processes_service = ProcessDetailSchema()


class JobOutputSchema(MappingSchema):
    ID = SchemaNode(String())
    value = SchemaNode(String())


class JobOutputsSchema(SequenceSchema):
    output = JobOutputSchema()


class ExceptionTextList(SequenceSchema):
    text = SchemaNode(String())


class ExceptionSchema(MappingSchema):
    Code = SchemaNode(String())
    Locator = SchemaNode(String())
    Text = ExceptionTextList()


class ExceptionsOutputSchema(SequenceSchema):
    exceptions = ExceptionSchema()


class LogsOutputSchema(MappingSchema):
    pass


class FrontpageParameterSchema(MappingSchema):
    name = SchemaNode(String(), example='api')
    enabled = SchemaNode(Boolean(), example=True)
    url = SchemaNode(String(), example='https://localhost:5000')
    doc = SchemaNode(String(), example='https://localhost:5000/api', missing=drop)


class FrontpageParameters(SequenceSchema):
    param = FrontpageParameterSchema()


class FrontpageSchema(MappingSchema):
    message = SchemaNode(String(), default='Twitcher Information', example='Twitcher Information')
    configuration = SchemaNode(String(), default='default', example='default')
    parameters = FrontpageParameters()


class AdapterDescriptionSchema(MappingSchema):
    name = SchemaNode(String(), description="Name of the loaded Twitcher adapter.", missing=drop, example='default')
    version = SchemaNode(String(), description="Version of the loaded Twitcher adapter.", missing=drop, example='0.3.0')


class VersionsSpecSchema(MappingSchema):
    twitcher = SchemaNode(String(), description="Twitcher version string.", example='0.3.0')
    adapter = AdapterDescriptionSchema()


class VersionsSchema(MappingSchema):
    version = VersionsSpecSchema()


#################################
# Local Processes schemas
#################################


class ProcessOfferingBody(MappingSchema):
    process = ProcessDetailSchema()


class PackageBody(MappingSchema):
    workflow = SchemaNode(String(), description="Workflow file content.")  # TODO: maybe binary?


class ExecutionUnitBody(MappingSchema):
    package = PackageBody(missing=drop)
    reference = SchemaNode(String(), missing=drop)


class ProfileExtensionBody(MappingSchema):
    # TODO: Complete schema as needed
    pass


class DeploymentProfileBody(MappingSchema):
    deploymentProfileName = SchemaNode(String(), description="Name of the deployment profile.")
    executionUnit = ExecutionUnitBody(missing=drop)
    profileExtension = ProfileExtensionBody(missing=drop)


class DeleteProcessRequestSchema(MappingSchema):
    header = AcceptHeader()
    body = MappingSchema(default={})


class PostProcessRequestBody(MappingSchema):
    processOffering = ProcessOfferingBody()
    deploymentProfile = DeploymentProfileBody()


class PostProcessRequest(MappingSchema):
    header = AcceptHeader()
    body = PostProcessRequestBody()


#################################
# Provider Processes schemas
#################################


class GetProviders(MappingSchema):
    header = AcceptHeader()


class PostProvider(MappingSchema):
    header = AcceptHeader()
    body = CreateProviderRequestBody()


class GetProviderProcesses(MappingSchema):
    header = AcceptHeader()


class GetProviderProcess(MappingSchema):
    header = AcceptHeader()


class PostProviderProcessJobRequestBody(MappingSchema):
    inputs = JobInputList()
    # outputs = JobOutputList()


class PostProviderProcessJobRequest(MappingSchema):
    """Launching a new process request definition."""
    header = AcceptHeader()
    querystring = LaunchJobQuerystring()
    body = PostProviderProcessJobRequestBody()


#################################
# Responses schemas
#################################


class OkGetFrontpageSchema(MappingSchema):
    header = JsonHeader()
    body = FrontpageSchema()


class OkGetSwaggerJSONSchema(MappingSchema):
    header = JsonHeader()
    body = MappingSchema(default={}, description="")


class OkGetSwaggerUISchema(MappingSchema):
    header = HtmlHeader()


class OkGetVersionsSchema(MappingSchema):
    header = JsonHeader()
    body = VersionsSchema()


class OkGetProvidersSchema(MappingSchema):
    header = JsonHeader()
    body = ProvidersSchema()


class OkGetProviderCapabilitiesSchema(MappingSchema):
    header = JsonHeader()
    body = ProviderCapabilitiesSchema()


class NoContentDeleteProviderSchema(MappingSchema):
    header = JsonHeader()
    body = MappingSchema(default={})


class OkGetProviderProcessesSchema(MappingSchema):
    header = JsonHeader()
    body = ProcessesSchema()


class OkGetProcessesBodySchema(MappingSchema):
    processes = ProcessListSchema()
    providers = ProviderProcessListSchema(missing=drop)


class OkGetProcessesSchema(MappingSchema):
    header = JsonHeader()
    body = OkGetProcessesBodySchema()


class OkPostProcessesSchema(MappingSchema):
    header = JsonHeader()
    body = ProcessDetailSchema()


class OkGetProcessBodySchema(MappingSchema):
    header = JsonHeader()
    process = ProcessDetailSchema()


class OkGetProcessSchema(MappingSchema):
    header = JsonHeader()
    body = OkGetProcessBodySchema()


class OkDeleteProcessBodySchema(MappingSchema):
    deploymentDone = SchemaNode(String(), default='success', example='success')
    id = SchemaNode(String(), example='workflow')


class OkDeleteProcessSchema(MappingSchema):
    header = JsonHeader()
    body = OkDeleteProcessBodySchema()


class OkGetProviderProcessDescription(MappingSchema):
    header = JsonHeader()
    body = ProcessDescriptionSchema()


class CreatedPostProvider(MappingSchema):
    header = JsonHeader()
    body = ProviderSummarySchema()


class CreatedLaunchJobHeader(JsonHeader):
    Location = SchemaNode(String(), description='Location URL of the created job execution status.')


class CreatedLaunchJobResponse(MappingSchema):
    header = CreatedLaunchJobHeader()
    body = SingleJobStatusSchema()


class OkGetAllJobsResponse(MappingSchema):
    header = JsonHeader()
    body = GetAllJobsSchema()


class OkDismissJobResponse(MappingSchema):
    header = JsonHeader()
    body = DismissedJobSchema()


class OkGetSingleJobStatusResponse(MappingSchema):
    header = JsonHeader()
    body = SingleJobStatusSchema()


class OkGetSingleJobOutputsResponse(MappingSchema):
    header = JsonHeader()
    body = JobOutputsSchema()


class OkGetSingleOutputResponse(MappingSchema):
    header = JsonHeader()
    body = JobOutputSchema()


class OkGetExceptionsResponse(MappingSchema):
    header = JsonHeader()
    body = ExceptionsOutputSchema()


class OkGetLogsResponse(MappingSchema):
    header = JsonHeader()
    body = LogsOutputSchema()


get_api_frontpage_responses = {
    '200': OkGetFrontpageSchema(description='success')
}
get_api_swagger_json_responses = {
    '200': OkGetSwaggerJSONSchema(description='success')
}
get_api_swagger_ui_responses = {
    '200': OkGetSwaggerUISchema(description='success')
}
get_api_versions_responses = {
    '200': OkGetVersionsSchema(description='success')
}
get_processes_responses = {
    '200': OkGetProcessesSchema(description='success')
}
post_processes_responses = {
    '200': OkPostProcessesSchema(description='success')
}
get_process_responses = {
    '200': OkGetProcessSchema(description='success')
}
delete_process_responses = {
    '200': OkDeleteProcessSchema(description='success')
}
get_all_providers_responses = {
    '200': OkGetProvidersSchema(description='success')
}
get_one_provider_responses = {
    '200': OkGetProviderCapabilitiesSchema(description='success')
}
delete_provider_responses = {
    '204': NoContentDeleteProviderSchema(description='success')
}
get_provider_processes_responses = {
    '200': OkGetProviderProcessesSchema(description='success')
}
get_provider_process_description_responses = {
    '200': OkGetProviderProcessDescription(description='success')
}
post_provider_responses = {
    '201': CreatedPostProvider(description='success')
}
post_provider_process_job_responses = {
    '201': CreatedLaunchJobResponse(description='success')
}
get_all_jobs_responses = {
    '200': OkGetAllJobsResponse(description='success')
}
get_single_job_status_responses = {
    '200': OkGetSingleJobStatusResponse(description='success')
}
delete_job_responses = {
    '200': OkDismissJobResponse(description='success')
}
get_job_results_responses = {
    '200': OkGetSingleJobOutputsResponse(description='success')
}
get_single_result_responses = {
    '200': OkGetSingleOutputResponse(description='success')
}
get_exceptions_responses = {
    '200': OkGetExceptionsResponse(description='success')
}
get_logs_responses = {
    '200': OkGetLogsResponse(description='success')
}

#################################################################
# Utility methods
#################################################################


def service_api_route_info(service_api, settings):
    api_base = wps_restapi_base_path(settings)
    return {'name': service_api.name, 'pattern': '{base}{path}'.format(base=api_base, path=service_api.path)}
