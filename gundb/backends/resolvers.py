import re

SCHEME_UID_PAT = "(?P<schema>.+?)://(?P<id>.+)"

def parse_schema_and_id(s):
    m = re.match(SCHEME_UID_PAT, s)
    if m:
        return m.groupdict()['schema'], int(m.groupdict()['id']) 
    return None, None

def is_root_soul(s):
    return "://" in s

def is_nested(s):
    return not is_root_soul(s)

def get_nested_soul_node(s, graph):
    return graph.get(s, {})

def filter_root_objects(graph):
    for kroot, rootnode in graph.items():
        if "://" in kroot:
            yield kroot, rootnode

ignore = ["_", ">", "#"]

def is_reference(d):
    return isinstance(d, dict) and '#' in d

def resolve_reference(ref, graph):
    assert(is_reference(ref))
    if not ref['#'] in graph:
        return {}
    resolved = graph[ref['#']].copy()
    for k, v in resolved.items():
        if not k in ignore and is_reference(v):
            resolved[k] = resolve_reference(v, graph)
    return resolved

def resolve_v(val, graph):
    if is_reference(val):
        return resolve_reference(val, graph)
    else:
        return val

def copy(root, graph):
    return {k: resolve_v(v, graph) for k, v in graph.items() if k not in ignore}

def search(k, graph):
    def dfs(graph):
        for key, val in graph.items():
            if key in ignore or not isinstance(val, dict):
                continue
            if val.get('#') == k:
                return [key]
            else:
                try_child = dfs(val)
                if try_child:
                    return [key] + try_child
        return []
    return dfs(graph)

def traverse(soul, graph):
    for key in graph.keys():
        val = graph[key]
        if type(val) != dict:
            continue
        if '#' in val and val['#'] == soul:
            return key, graph, key
        else:
            try_child = traverse(soul, val)
            if try_child[0]:
                return key, try_child[1], try_child[2]
    return None, None, None
