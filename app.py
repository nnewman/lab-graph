import datetime
from uuid import uuid4

from flask import Flask, jsonify, request
from marshmallow import Schema, fields, validate, ValidationError
from neomodel import (
    StructuredNode, UniqueIdProperty, RelationshipTo, RelationshipFrom,
    ZeroOrMore, DateTimeProperty, ZeroOrOne, config, DoesNotExist
)


config.DATABASE_URL = "bolt://neo4j:password@127.0.0.1:7687"
app = Flask(__name__)
app.config['DEBUG'] = True


class Sample(StructuredNode):
    uid = UniqueIdProperty()
    processes = RelationshipFrom(
        'Process', 'PROCESSES', cardinality=ZeroOrMore
    )
    split_process_source = RelationshipTo(
        'SplitSample', 'SPLITS', cardinality=ZeroOrMore
    )
    split_process_targets = RelationshipFrom(
        'SplitSample', 'SPLITS', cardinality=ZeroOrMore
    )


class Process(StructuredNode):
    uid = UniqueIdProperty()
    samples = RelationshipTo('Sample', 'SAMPLES', cardinality=ZeroOrMore)


class SplitSample(StructuredNode):
    uid = UniqueIdProperty()
    timestamp = DateTimeProperty()
    original_sample = RelationshipFrom(
        'Sample', 'SOURCE', cardinality=ZeroOrOne
    )
    target_samples = RelationshipTo(
        'Sample', 'TARGETS', cardinality=ZeroOrMore
    )


class BaseSchema(Schema):
    uid = fields.UUID(required=True, allow_none=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if kwargs.get('strict') is None:
            self.strict = True


class SampleSchema(BaseSchema):
    pass


class ProcessSchema(BaseSchema):
    samples = fields.Nested(SampleSchema, many=True)


class SplitSampleSchema(BaseSchema):
    timestamp = fields.DateTime(required=True, allow_none=False)
    original_sample = fields.Nested(
        SampleSchema, required=True, allow_none=False
    )
    target_count = fields.Integer(
        required=True, allow_none=False, validate=validate.Range(min=2), load_only=True
    )
    target_samples = fields.Nested(SampleSchema, many=True, dump_only=True)


class SplitSampleDumpSchema(SplitSampleSchema):
    # Neomodel returns the `ZeroOrOne` as an iterable
    original_sample = fields.Nested(SampleSchema, many=True)


@app.errorhandler(ValidationError)
def handle_validation_error(exc):
    return jsonify(message=exc.args[0])


@app.errorhandler(DoesNotExist)
def handle_does_not_exist(exc):
    return jsonify(message=exc.args[0])


@app.route('/samples')
def get_samples():
    schema = SampleSchema()
    return jsonify(schema.dump(Sample.nodes.all(), many=True).data)


@app.route('/samples', methods=['POST'])
def create_sample():
    schema = SampleSchema()
    data = request.get_json(silent=True)
    data['uid'] = str(uuid4())
    serialized_data = schema.load(data).data
    sample = Sample(**serialized_data).save()
    return jsonify(schema.dump(sample).data)


@app.route('/processes')
def get_processes():
    schema = ProcessSchema()
    return jsonify(schema.dump(Process.nodes.all(), many=True).data)


@app.route('/processes', methods=['POST'])
def create_process():
    schema = ProcessSchema()
    data = request.get_json(silent=True)
    data['uid'] = str(uuid4())
    serialized_data = schema.load(data).data
    _samples = serialized_data.pop('samples', []) or []
    process = Process(**serialized_data).save()
    for _sample in _samples:
        sample = Sample.nodes.get(uid=_sample['uid'])
        process.samples.connect(sample)
        sample.processes.connect(process)
    process.refresh()
    return jsonify(schema.dump(process).data)


@app.route('/split', methods=['POST'])
def split_sample():
    schema = SplitSampleSchema()
    data = request.get_json(silent=True)
    data['uid'] = str(uuid4())
    data['timestamp'] = datetime.datetime.now().isoformat()
    serialized_data = schema.load(data).data
    source_sample = serialized_data.pop('original_sample')
    target_count = serialized_data.pop('target_count')
    split_process = SplitSample(**serialized_data).save()
    source = Sample.nodes.get(uid=str(source_sample['uid']))
    source.split_process_source.connect(split_process)
    split_process.original_sample.connect(source)
    for idx in range(target_count - 1):
        new_sample = Sample(uid=str(uuid4())).save()
        for process in source.processes.all():
            process.samples.connect(new_sample)
            new_sample.processes.connect(process)
        split_process.target_samples.connect(new_sample)
    split_process.refresh()
    dump_data = SplitSampleDumpSchema().dump(split_process).data
    dump_data['original_sample'] = dump_data['original_sample'][0]
    return jsonify(dump_data)


if __name__ == '__main__':
    app.run()
