"""Bounded JSON arithmetic interpreter; never evaluates Python or repo programs."""
import json
import math
import re

OPS = ("add", "subtract", "multiply", "divide", "exp", "greater", "table_max", "table_min", "table_sum", "table_average")
CONSTANTS = {"const_"+str(value): float(value) for value in (1,2,3,4,5,6,7,8,9,10,100,1000,10000,100000,1000000,10000000,1000000000)}
CONSTANTS["const_m1"] = -1.
NUMERIC = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
COMMON = "Solve the financial question using the original evidence. Preserve the requested calculation and its scale; do not invent values. "
DIRECT = 'Return only one JSON object with exactly the key "answer": a finite JSON number, a numeric string optionally ending in %, or "yes"/"no". A percent string is converted to a decimal fraction; plain numbers are not rescaled.\n'
DSL = (
    'Return only one JSON object with exactly the key "program": an array of one to five steps. '
    'Each step is [operation, argument1, argument2]. Operations: add, subtract, multiply, divide, exp, greater, '
    'table_max, table_min, table_sum, table_average. Arithmetic arguments are JSON numbers, numeric strings '
    '(commas allowed; % means divide by100), declared constant names, or "#i" for an earlier zero-based step. '
    'greater returns "yes" or "no". Table operations use the exact unique first-column row label as argument1 '
    'and "none" as argument2, aggregating that row\'s remaining numeric cells; unknown/duplicate row labels are invalid. '
    'Table cells remove $ and any suffix beginning with (, then parse numerically. '
    'All values must be finite with absolute magnitude <=1e100; exp exponent absolute value <=100. '
    'The last step is the answer, rounded to five decimals with no gold-dependent scale adjustment. '
    'Constants: ' + ', '.join(CONSTANTS) + '. No code, extra keys, or explanation.\n'
)


def prompt(public, arm):
    assert set(public) == {"question", "pre_text", "table", "post_text"}
    assert arm in ("direct_scalar", "restricted_dsl")
    return COMMON + (DIRECT if arm == "direct_scalar" else DSL) + json.dumps(public, ensure_ascii=False, separators=(",", ":"))


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def number(value):
    if type(value) not in (int, float, str):
        raise ValueError("numeric primitive required")
    if isinstance(value, str):
        if value in CONSTANTS:
            return CONSTANTS[value]
        cleaned = value.strip().replace(",", "")
        percent = cleaned.endswith("%")
        cleaned = cleaned[:-1] if percent else cleaned
        if not re.fullmatch(NUMERIC, cleaned):
            raise ValueError("invalid numeric literal")
        value = float(cleaned) / (100 if percent else 1)
    value = float(value)
    if not math.isfinite(value) or abs(value) > 1e100:
        raise ValueError("numeric magnitude/finite bound")
    return value


def source_numbers(public):
    values = set(CONSTANTS.values())
    texts = public["pre_text"] + public["post_text"] + [cell for row in public["table"] for cell in row]
    for text in texts:
        for match in re.finditer(r"[+-]?(?:\d[\d,]*(?:\.\d*)?|\.\d+)%?", text):
            try:
                values.add(number(match.group()))
            except ValueError:
                pass
    return values


def evaluate(text, arm, public):
    try:
        obj = json.loads(text, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
        if not isinstance(obj, dict):
            raise ValueError("JSON object required")
        if arm == "direct_scalar":
            if set(obj) != {"answer"}:
                raise ValueError("exact answer key required")
            value = obj["answer"]
            value = value if type(value) is str and value in ("yes", "no") else round(number(value), 5)
            return {"status": "valid", "value": value, "reason": None, "source_operand_value_presence": None}
        if arm != "restricted_dsl" or set(obj) != {"program"}:
            raise ValueError("exact program key required")
        steps = obj["program"]
        if not isinstance(steps, list) or not 1 <= len(steps) <= 5:
            raise ValueError("one to five steps required")
        previous, presence = [], []
        source = source_numbers(public)

        def argument(value):
            if type(value) is str and re.fullmatch(r"#\d+", value):
                index = int(value[1:])
                if index >= len(previous):
                    raise ValueError("only earlier references allowed")
                return number(previous[index])
            numeric = number(value)
            presence.append(numeric in source)
            return numeric

        for step in steps:
            if not isinstance(step, list) or len(step) != 3 or step[0] not in OPS:
                raise ValueError("invalid typed operation")
            op, a, b = step
            if op.startswith("table_"):
                matches = [row for row in public["table"] if row[0] == a]
                if type(a) is not str or b != "none" or len(matches) != 1:
                    raise ValueError("unique public row label and none required")
                values = [number(cell.replace("$", "").strip().split("(")[0].strip()) for cell in matches[0][1:]]
                if not values:
                    raise ValueError("empty numeric table row")
                value = max(values) if op == "table_max" else min(values) if op == "table_min" else sum(values)
                if op == "table_average":
                    value /= len(values)
                presence.append(True)
            else:
                a, b = argument(a), argument(b)
                if op == "add": value = a+b
                elif op == "subtract": value = a-b
                elif op == "multiply": value = a*b
                elif op == "divide": value = a/b
                elif op == "greater": value = "yes" if a>b else "no"
                else:
                    if abs(b)>100: raise ValueError("exponent bound")
                    value = math.pow(a,b)
            if type(value) is not str:
                value = number(value)
            previous.append(value)
        value = previous[-1]
        return {"status": "valid", "value": value if type(value) is str else round(value,5), "reason": None,
                "source_operand_value_presence": all(presence), "source_presence_not_identity_or_faithfulness": True,
                "steps": len(steps)}
    except (ValueError, TypeError, KeyError, IndexError, ZeroDivisionError, OverflowError) as error:
        return {"status": "invalid", "value": None, "reason": f"{type(error).__name__}: {error}", "source_operand_value_presence": None}
