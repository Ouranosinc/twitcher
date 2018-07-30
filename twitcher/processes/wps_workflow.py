import os

from pywps import Process, LiteralInput, LiteralOutput

import logging
LOGGER = logging.getLogger("PYWPS")


class Workflow(Process):
    def __init__(self):
        inputs = [
            LiteralInput('name', 'process.title', data_type='string')]
        outputs = [
            LiteralOutput('output', 'Output response',
                          data_type='string')]

        super(Process, self).__init__(
            self._handler,
            identifier='workflow',
            title='Run a workflow',
            version='1.0',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        response.update_status("Launching workflow ...", 0)
        LOGGER.debug("HOME=%s, Current Dir=%s", os.environ.get('HOME'), os.path.abspath(os.curdir))
        response.outputs['output'].data = 'Workflow: {}'.format(request.inputs['name'][0].data)
        return response
