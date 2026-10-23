"""Identical public JSON contract for each provider's native structured output."""
import json

def schema_from_messages(messages):
    task=json.loads(messages[1]['content'])
    slots=list(task['common_requirements'])
    for action in task['catalog']:
        slots.extend(r.split('=',1)[0] for r in action['additional_requirements'])
    slots=list(dict.fromkeys(slots))
    labels=[row[0] for row in task['evidence']]
    binding={'anyOf':[{'type':'string','enum':labels},{'type':'null'}]} if labels else {'type':'null'}
    return {'type':'object','properties':{
        'support':{'type':'object','properties':{slot:binding for slot in slots},'required':slots,'additionalProperties':False},
        'status':{'type':'string','enum':['recommend','request_evidence']},
        'template':{'anyOf':[{'type':'string','enum':[a['id'] for a in task['catalog']]},{'type':'null'}]},
        'missing':{'type':'array','items':{'type':'string'}},
        'explanation':{'type':'string'}},
        'required':['support','status','template','missing','explanation'],'additionalProperties':False}

def add_format(body,provider,messages):
    schema=schema_from_messages(messages)
    if provider=='openai':body['text']={'format':{'type':'json_schema','name':'marketing_recommendation','strict':True,'schema':schema}}
    elif provider=='anthropic':body['output_config']={'format':{'type':'json_schema','schema':schema}}
    else:raise ValueError('unsupported provider')
    return body
