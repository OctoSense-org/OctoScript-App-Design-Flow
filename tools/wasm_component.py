"""What a WebAssembly function file is, what it imports and what it exports.

The same answer `hub component-info` prints (App Hub), for when no such hub
is at hand: `kind` (`component`, OctoSense ADR 0014, or `module`, ADR 0011),
`imports`, and `exports` with each function's parameters and result written
as WIT writes them (records, variants and enums by their shape). `tools/octo
wasm` uses it. Python 3.9+, no third-party packages.

It reads the binary format and does not validate it: App Hub's gate and the
host's `wasm` service do. A component's import and export names come from its
top-level import (10) and export (11) sections; each exported function's type
from the type (7), alias (6) and canon (8) sections that build the component's
type and function index spaces. A core module's come from its type (1),
import (2), function (3) and export (7) sections.
"""

COMPONENT_PREAMBLE = b"\0asm\x0d\x00\x01\x00"
MODULE_PREAMBLE = b"\0asm\x01\x00\x00\x00"

# The WASI packages a component may import, each scoped to its app by the
# host (ADR 0014); the same list as App Hub's ALLOWED_COMPONENT_IMPORTS.
# wasi:filesystem needs the manifest's `storage` capability.
ALLOWED_IMPORTS = ("wasi:cli/", "wasi:clocks/", "wasi:filesystem/", "wasi:io/", "wasi:random/")
FILESYSTEM = "wasi:filesystem/"

PRIMITIVES = {
    0x7f: "bool", 0x7e: "s8", 0x7d: "u8", 0x7c: "s16", 0x7b: "u16", 0x7a: "s32",
    0x79: "u32", 0x78: "s64", 0x77: "u64", 0x76: "f32", 0x75: "f64", 0x74: "char",
    0x73: "string", 0x64: "error-context",
}
CORE_TYPES = {0x7f: "i32", 0x7e: "i64", 0x7d: "f32", 0x7c: "f64", 0x7b: "v128", 0x70: "funcref", 0x6f: "externref"}


class ReadError(ValueError):
    """The bytes are not what this reader understands."""


class Reader:
    def __init__(self, data, pos=0, end=None):
        self.data = data
        self.pos = pos
        self.end = len(data) if end is None else end

    def done(self):
        return self.pos >= self.end

    def peek(self):
        if self.pos >= self.end:
            raise ReadError("unexpected end of the file")
        return self.data[self.pos]

    def byte(self):
        value = self.peek()
        self.pos += 1
        return value

    def take(self, n):
        if n > self.end - self.pos:
            raise ReadError("unexpected end of the file")
        value = self.data[self.pos:self.pos + n]
        self.pos += n
        return value

    def uleb(self, bits=32):
        result = shift = 0
        while True:
            b = self.byte()
            result |= (b & 0x7f) << shift
            shift += 7
            if not b & 0x80:
                break
            if shift >= bits + 7:
                raise ReadError("an integer is too long")
        if result >> bits:
            raise ReadError("an integer is out of range")
        return result

    def u32(self):
        return self.uleb(32)

    def s33(self):
        result = shift = 0
        while True:
            b = self.byte()
            result |= (b & 0x7f) << shift
            shift += 7
            if not b & 0x80:
                break
            if shift > 35:
                raise ReadError("an integer is too long")
        if b & 0x40:
            result -= 1 << shift
        return result

    def string(self):
        raw = self.take(self.u32())
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            raise ReadError("a name is not UTF-8")

    def flag(self):
        value = self.byte()
        if value not in (0, 1):
            raise ReadError(f"expected 0 or 1, found {value:#x}")
        return value == 1


def sections(data, preamble):
    """(id, Reader over its contents) for each top-level section."""
    r = Reader(data, len(preamble))
    while not r.done():
        sid = r.byte()
        size = r.u32()
        if size > r.end - r.pos:
            raise ReadError(f"section {sid} runs past the end of the file")
        yield sid, Reader(data, r.pos, r.pos + size)
        r.pos += size


def describe(data):
    """`hub component-info`'s answer as a dict: kind, imports, exports. A
    component whose function types this reader cannot follow still has its
    imports and export names, and `unresolved` says why its parameters are
    missing."""
    if data.startswith(COMPONENT_PREAMBLE):
        return describe_component(data)
    if data.startswith(MODULE_PREAMBLE):
        return describe_module(data)
    raise ReadError("not a WebAssembly core module or component")


# ------------------------------------------------------------------ component
def extern_name(r):
    """An import or export name (`importname'` / `exportname'`)."""
    tag = r.byte()
    if tag in (0x00, 0x01):  # 0x01: older binaries' interface-name marker
        return r.string()
    if tag != 0x02:
        raise ReadError(f"unknown name encoding {tag:#x}")
    name = r.string()
    implements = suffix = None
    for _ in range(r.u32()):
        option = r.byte()
        value = r.string()
        if option == 0x00:
            implements = value
        elif option == 0x01:
            suffix = value
        elif option != 0x02:
            raise ReadError(f"unknown name option {option:#x}")
    if suffix and not implements and "@" in name:
        name += suffix
    return name


def sort(r):
    """A sort: 'core' (with its core sort), 'func', 'value', 'type', 'component' or 'instance'."""
    b = r.byte()
    if b == 0x00:
        r.byte()
        return "core"
    names = {0x01: "func", 0x02: "value", 0x03: "type", 0x04: "component", 0x05: "instance"}
    if b not in names:
        raise ReadError(f"unknown sort {b:#x}")
    return names[b]


def valtype(r):
    b = r.peek()
    if b in PRIMITIVES:
        r.byte()
        return ("prim", PRIMITIVES[b])
    index = r.s33()
    if index < 0:
        raise ReadError(f"unknown value type {b:#x}")
    return ("idx", index)


def optional_valtype(r):
    return valtype(r) if r.flag() else None


def externdesc(r):
    b = r.byte()
    if b == 0x00:
        if r.byte() != 0x11:
            raise ReadError("unknown core extern kind")
        return ("module", r.u32())
    if b == 0x01:
        return ("func", r.u32())
    if b == 0x02:
        bound = r.byte()
        if bound == 0x00:
            return ("value", r.u32())
        if bound == 0x01:
            return ("value", valtype(r))
        raise ReadError("unknown value bound")
    if b == 0x03:
        bound = r.byte()
        if bound == 0x00:
            return ("type-eq", r.u32())
        if bound == 0x01:
            return ("type-sub",)
        raise ReadError("unknown type bound")
    if b == 0x04:
        return ("component", r.u32())
    if b == 0x05:
        return ("instance", r.u32())
    raise ReadError(f"unknown extern kind {b:#x}")


def alias(r):
    """(sort, target): target is ('export', instance, name), ('core-export', …) or ('outer', count, index)."""
    kind = sort(r)
    target = r.byte()
    if target == 0x00:
        return kind, ("export", r.u32(), r.string())
    if target == 0x01:
        return kind, ("core-export", r.u32(), r.string())
    if target == 0x02:
        return kind, ("outer", r.u32(), r.u32())
    raise ReadError(f"unknown alias target {target:#x}")


def declarations(r, component):
    """Skips an instance or component type's declarations."""
    for _ in range(r.u32()):
        tag = r.byte()
        if tag == 0x01:
            deftype(r)
        elif tag == 0x02:
            alias(r)
        elif tag == 0x04 or (tag == 0x03 and component):
            extern_name(r)
            externdesc(r)
        else:
            raise ReadError(f"unsupported declaration {tag:#x} in an instance or component type")


def deftype(r):
    b = r.byte()
    if b == 0x3f:  # resource (rep i32), with an optional destructor
        r.byte()
        if r.flag():
            r.u32()
        return ("resource",)
    if b in (0x40, 0x43):  # function, synchronous or async
        params = [(r.string(), valtype(r)) for _ in range(r.u32())]
        kind = r.byte()
        if kind == 0x00:
            result = valtype(r)
        elif kind == 0x01 and r.byte() == 0x00:
            result = None
        else:
            raise ReadError("unknown function result encoding")
        return ("func", params, result)
    if b in (0x41, 0x42):
        declarations(r, component=b == 0x41)
        return ("component",) if b == 0x41 else ("instance",)
    if b in PRIMITIVES:
        return ("prim", PRIMITIVES[b])
    if b == 0x72:
        return ("record", [(r.string(), valtype(r)) for _ in range(r.u32())])
    if b == 0x71:
        cases = []
        for _ in range(r.u32()):
            name, ty = r.string(), optional_valtype(r)
            if r.byte() != 0x00:
                raise ReadError("a variant case's refinement is not supported")
            cases.append((name, ty))
        return ("variant", cases)
    if b == 0x70:
        return ("list", valtype(r))
    if b == 0x67:
        return ("list", valtype(r), r.u32())
    if b == 0x63:
        return ("map", valtype(r), valtype(r))
    if b == 0x6f:
        return ("tuple", [valtype(r) for _ in range(r.u32())])
    if b == 0x6e:
        return ("flags", [r.string() for _ in range(r.u32())])
    if b == 0x6d:
        return ("enum", [r.string() for _ in range(r.u32())])
    if b == 0x6b:
        return ("option", valtype(r))
    if b == 0x6a:
        return ("result", optional_valtype(r), optional_valtype(r))
    if b in (0x69, 0x68):
        return ("handle", r.u32())
    if b in (0x66, 0x65):
        return ("async", optional_valtype(r))
    raise ReadError(f"unknown type {b:#x}")


def canon_options(r):
    for _ in range(r.u32()):
        option = r.byte()
        if option in (0x03, 0x04, 0x05, 0x07, 0x08):
            r.u32()
        elif option not in (0x00, 0x01, 0x02, 0x06, 0x09):
            raise ReadError(f"unknown canonical option {option:#x}")


def canon(r):
    """The type index of a lifted function, or None for the other canonical
    built-ins, which make core functions."""
    op = r.byte()
    if op == 0x00:
        if r.byte() != 0x00:
            raise ReadError("unknown lift encoding")
        r.u32()
        canon_options(r)
        return r.u32()
    if op == 0x01:
        if r.byte() != 0x00:
            raise ReadError("unknown lower encoding")
        r.u32()
        canon_options(r)
        return None
    if op in (0x02, 0x03, 0x04, 0x0e, 0x13, 0x14, 0x15, 0x1a, 0x1b, 0x2e, 0x2f, 0x40):
        r.u32()
        return None
    if op in (0x05, 0x0d, 0x1e, 0x1f, 0x22, 0x23, 0x24, 0x25, 0x26, 0x28, 0x42):
        return None
    if op in (0x0f, 0x10, 0x16, 0x17):
        r.u32()
        canon_options(r)
        return None
    if op in (0x11, 0x12, 0x18, 0x19):
        r.u32()
        r.byte()
        return None
    if op in (0x1c, 0x1d):
        canon_options(r)
        return None
    if op in (0x27, 0x41):
        r.u32()
        r.u32()
        return None
    # Async task and thread built-ins: a synchronous component has none.
    raise ReadError(f"unsupported canonical function {op:#x}")


def component_names(data):
    """The top-level import names (but `(type (eq …))` ones, a name for a
    type the component already has, which reaches nothing) and the function
    and instance export names, in order."""
    imports, exports = [], []
    for sid, r in sections(data, COMPONENT_PREAMBLE):
        if sid == 10:
            for _ in range(r.u32()):
                name = extern_name(r)
                if externdesc(r)[0] != "type-eq":
                    imports.append(name)
        elif sid == 11:
            for _ in range(r.u32()):
                name = extern_name(r)
                kind = sort(r)
                r.u32()
                if r.flag():
                    externdesc(r)
                if kind in ("func", "instance"):
                    exports.append((name, kind))
    return imports, exports


def component_signatures(data):
    """{export name: (params, result)} for the exported functions, from the
    component's type and function index spaces."""
    types = []  # ("def", deftype) | ("ref", index) | ("opaque",)
    funcs = []  # a function type's index, or None when not followed
    found = {}
    for sid, r in sections(data, COMPONENT_PREAMBLE):
        if sid == 7:
            for _ in range(r.u32()):
                types.append(("def", deftype(r)))
        elif sid == 6:
            for _ in range(r.u32()):
                kind, _target = alias(r)
                if kind == "type":
                    types.append(("opaque",))
                elif kind == "func":
                    funcs.append(None)
        elif sid == 8:
            for _ in range(r.u32()):
                lifted = canon(r)
                if lifted is not None:
                    funcs.append(lifted)
        elif sid == 10:
            for _ in range(r.u32()):
                extern_name(r)
                desc = externdesc(r)
                if desc[0] == "func":
                    funcs.append(desc[1])
                elif desc[0] == "type-eq":
                    types.append(("ref", desc[1]))
                elif desc[0] == "type-sub":
                    types.append(("opaque",))
        elif sid == 11:
            for _ in range(r.u32()):
                name = extern_name(r)
                kind = sort(r)
                index = r.u32()
                desc = externdesc(r) if r.flag() else None
                if kind == "func":
                    if desc and desc[0] == "func":
                        func_type = desc[1]
                    elif index < len(funcs):
                        func_type = funcs[index]
                    else:
                        raise ReadError(f"export {name!r} names function {index}, which is not defined")
                    funcs.append(func_type)
                    found[name] = func_type
                elif kind == "type":
                    types.append(("ref", desc[1] if desc and desc[0] == "type-eq" else index))
    return {name: function_type(types, index) for name, index in found.items()}


def resolve(types, index):
    for _ in range(len(types) + 1):
        if index is None or index >= len(types):
            return None
        entry = types[index]
        if entry[0] == "ref":
            index = entry[1]
            continue
        return entry[1] if entry[0] == "def" else None
    return None


def function_type(types, index):
    ty = resolve(types, index)
    if ty is None or ty[0] != "func":
        return None
    params = [[name, wit(types, t)] for name, t in ty[1]]
    return params, (wit(types, ty[2]) if ty[2] is not None else None)


def wit(types, vt, depth=0):
    """A value type as WIT writes it, as `hub component-info` and OctoSense's
    `wasm.functions` show it: records, variants and enums by their shape;
    a resource handle, a future, a stream or a map is `resource`."""
    if vt[0] == "prim":
        return vt[1]
    ty = resolve(types, vt[1])
    if ty is None or depth > 64:
        return "resource"
    sub = lambda t: wit(types, t, depth + 1)  # noqa: E731
    kind = ty[0]
    if kind == "prim":
        return ty[1]
    if kind == "record":
        return "record { " + ", ".join(f"{n}: {sub(t)}" for n, t in ty[1]) + " }"
    if kind == "variant":
        return "variant { " + ", ".join(f"{n}({sub(t)})" if t else n for n, t in ty[1]) + " }"
    if kind == "list":
        return f"list<{sub(ty[1])}>"
    if kind == "tuple":
        return "tuple<" + ", ".join(sub(t) for t in ty[1]) + ">"
    if kind == "flags":
        return "flags { " + ", ".join(ty[1]) + " }"
    if kind == "enum":
        return "enum { " + ", ".join(ty[1]) + " }"
    if kind == "option":
        return f"option<{sub(ty[1])}>"
    if kind == "result":
        ok, err = ty[1], ty[2]
        if ok and err:
            return f"result<{sub(ok)}, {sub(err)}>"
        if ok:
            return f"result<{sub(ok)}>"
        if err:
            return f"result<_, {sub(err)}>"
        return "result"
    return "resource"


def describe_component(data):
    imports, names = component_names(data)
    unresolved = None
    try:
        signatures = component_signatures(data)
    except ReadError as error:
        signatures, unresolved = {}, str(error)
    exports = []
    for name, kind in names:
        signature = signatures.get(name) if kind == "func" else None
        if signature is None and unresolved is None:
            unresolved = (f"{name} is an exported interface; octo's reader lists only a world's own functions"
                          if kind == "instance" else f"the type of {name} could not be followed")
        params, result = signature if signature else (None, None)
        exports.append({"name": name, "params": params, "result": result})
    exports.sort(key=lambda e: e["name"])
    info = {"kind": "component", "imports": imports, "exports": exports}
    if unresolved:
        info["unresolved"] = unresolved
    return info


# ---------------------------------------------------------------- core module
def core_valtype(r):
    b = r.byte()
    if b not in CORE_TYPES:
        raise ReadError(f"unsupported core value type {b:#x}")
    return CORE_TYPES[b]


def limits(r):
    flags = r.byte()
    if flags & ~0x0f:
        raise ReadError("unknown limits")
    bits = 64 if flags & 0x04 else 32
    r.uleb(bits)
    if flags & 0x01:
        r.uleb(bits)
    if flags & 0x08:
        r.u32()


def describe_module(data):
    """A core module's imports (`module.name`) and exported functions with
    their core types: parameters `p0`, `p1`, …."""
    imports, exports = [], []
    signatures, func_types = [], []
    unresolved = None
    for sid, r in sections(data, MODULE_PREAMBLE):
        try:
            if sid == 1:
                for _ in range(r.u32()):
                    if r.byte() != 0x60:
                        raise ReadError("a type other than a plain function type")
                    params = [core_valtype(r) for _ in range(r.u32())]
                    results = [core_valtype(r) for _ in range(r.u32())]
                    signatures.append((params, results))
            elif sid == 2:
                for _ in range(r.u32()):
                    module, name = r.string(), r.string()
                    imports.append(f"{module}.{name}")
                    kind = r.byte()
                    if kind == 0x00:
                        func_types.append(r.u32())
                    elif kind == 0x01:
                        if r.byte() not in (0x70, 0x6f):
                            raise ReadError("a table of an unsupported reference type")
                        limits(r)
                    elif kind == 0x02:
                        limits(r)
                    elif kind == 0x03:
                        core_valtype(r)
                        r.flag()
                    elif kind == 0x04:
                        r.byte()
                        r.u32()
                    else:
                        raise ReadError(f"unknown import kind {kind:#x}")
            elif sid == 3:
                func_types.extend(r.u32() for _ in range(r.u32()))
            elif sid == 7:
                for _ in range(r.u32()):
                    name, kind, index = r.string(), r.byte(), r.u32()
                    if kind == 0x00:
                        exports.append((name, index))
        except ReadError as error:
            if sid in (2, 7):
                raise
            unresolved = str(error)
    described = []
    for name, index in exports:
        params = result = None
        if unresolved is None and index < len(func_types) and func_types[index] < len(signatures):
            ps, rs = signatures[func_types[index]]
            params = [[f"p{i}", t] for i, t in enumerate(ps)]
            result = None if not rs else rs[0] if len(rs) == 1 else "(" + ", ".join(rs) + ")"
        described.append({"name": name, "params": params, "result": result})
    info = {"kind": "module", "imports": imports, "exports": described}
    if unresolved:
        info["unresolved"] = unresolved
    return info


# ------------------------------------------------------------------- policies
def refused_imports(imports):
    """The imports no host gives a component: anything outside ALLOWED_IMPORTS."""
    return [name for name in imports if not name.startswith(ALLOWED_IMPORTS)]


def uses_files(imports):
    return any(name.startswith(FILESYSTEM) for name in imports)


def reach(imports):
    """What a component reaches, in App Hub's words for its reviewers."""
    has = lambda prefix: any(name.startswith(prefix) for name in imports)  # noqa: E731
    reaches = []
    if has("wasi:clocks/"):
        reaches.append("the clock")
    if has("wasi:random/"):
        reaches.append("random numbers")
    if uses_files(imports):
        reaches.append("files in its app folder")
    nothing_else = "no network or other app" if uses_files(imports) else "no files, network or other app"
    if not reaches:
        return "nothing but its input"
    if len(reaches) == 1:
        return f"{reaches[0]}, but {nothing_else}"
    return f"{', '.join(reaches[:-1])} and {reaches[-1]}, but {nothing_else}"
