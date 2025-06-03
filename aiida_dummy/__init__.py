import random
from aiida.orm import Int, Code
from aiida.engine import ExitCode, CalcJob, WorkChain
from aiida.parsers import Parser
from aiida.common import exceptions, CalcInfo, CodeInfo


__version__ = '0.0.1'


class DummyWorkChain(WorkChain):

    @classmethod
    def define(cls, spec):
        super().define(spec)

        spec.input('code', valid_type=Code, required=True)
        spec.input('foobar', valid_type=Int, required=True)

        spec.outline(cls.start, cls.inspect, cls.finalize)

        spec.output('foobar', valid_type=Int)

    def start(self):

        self.report('DummyWorkChain started...')

        for i in range(1, 4):
            future_calc = self.submit(DummyCalc, **{'dummy': Int(self.inputs.foobar * i), 'code': self.inputs.code})
            key = f'workchain_{i}'
            self.to_context(**{key: future_calc})

    def inspect(self):
        for i in range(1, 4):
            key = f'workchain_{i}'
            assert self.ctx[key].is_finished_ok

    def finalize(self):
        self.ctx.foobar = Int(random.randint(1, 100))
        self.out("foobar", self.ctx.foobar)
        self.report('DummyWorkChain finished...')


class DummyParser(Parser):

    def __init__(self, node):

        super().__init__(node)
        if not issubclass(node.process_class, DummyCalc):
            raise exceptions.ParsingError("Can only parse DummyCalc")

    def parse(self, **kwargs):

        try:
            folder = self.retrieved
        except exceptions.NotExistent:
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        self.logger.warning('Parsing dummy output %s', str(kwargs))
        self.logger.warning('Folder is %s', folder)

        self.out('dummy', Int(42))

        return ExitCode(0)


class DummyCalc(CalcJob):

    INPUTS = ["1.input", "2.input", "3.input"]

    @classmethod
    def define(cls, spec):

        super().define(spec)

        spec.input("metadata.options.parser_name", valid_type=str, default="aiida_dummy")
        spec.input("metadata.options.resources",
            valid_type=dict,
            default={"num_machines": 1, "num_mpiprocs_per_machine": 1}
        )
        spec.input("metadata.options.input_filename", valid_type=str, default="1.input")
        spec.input("metadata.options.output_filename", valid_type=str, default="1.input.out")
        spec.input("metadata.options.withmpi", valid_type=bool, default=False)

        spec.input("dummy", valid_type=Int, default=lambda: Int(42), help="Dummy input") # this is cached
        spec.output("dummy", valid_type=Int, help="Dummy output")

    def prepare_for_submission(self, folder):

        codeinfo = CodeInfo()
        codeinfo.cmdline_params = DummyCalc.INPUTS[:]
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.output_filename

        self.logger.warning(str(self.inputs))

        calcinfo = CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.retrieve_list = [('*.out', '.', 0)]

        # copy all
        #calc_info.local_copy_list = [(self.inputs.folder.uuid, '.', None)] # what we write in the folder
        #calc_info.remote_copy_list = [(self.inputs.folder.uuid, '.', None)] # what to copy from remote folder

        for item in DummyCalc.INPUTS:
            with open(folder.get_abs_path(item), 'w') as f:
                f.write( f"{self.inputs.dummy.value}\n" * 7 )

        return calcinfo
