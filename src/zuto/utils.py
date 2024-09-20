import toml
from functools import cache, lru_cache
import json
import os
import requests
import typing
import yaml
import re


@lru_cache(maxsize=4096)
def match_scope(scope: str, path: str) -> bool:
    """
    Match the path against the scope pattern using re.match.

    The function checks for patterns like:
    - */{some word}
    - {some word}/*
    - Multiple wildcards (*)
    - Starts with and ends with *
    """
    if scope == "*":
        return True

    # Escape special characters in the scope, except for *
    escaped_scope = re.escape(scope).replace(r"\*", ".*")

    # Handle starts with and ends with *
    if escaped_scope.startswith(".*"):
        escaped_scope = "^" + escaped_scope
    else:
        escaped_scope = "^" + escaped_scope

    if escaped_scope.endswith(".*"):
        escaped_scope = escaped_scope + "$"
    else:
        escaped_scope = escaped_scope + "$"

    # Use re.match to check if the path matches the scope pattern
    return bool(re.match(escaped_scope, path))


@cache
def resolve_string(string: str):
    if string.startswith("http"):
        res = requests.get(string)
        resjson = res.json()
        if not isinstance(resjson, dict | list):
            raise ValueError("invalid response")
        return resjson
    if os.path.exists(string):
        if string.endswith(".toml"):
            return toml.load(string)
        elif string.endswith(".json"):
            return json.load(string)
        elif string.endswith(".yaml"):
            return yaml.load(string)
        else:
            raise ValueError("invalid file type")


def resolve_special_var(string: str, env: dict):
    """
    Resolve special variables in a string

    Args:
        string (str): The input string containing special variables.
        env (dict): A dictionary containing environment variables and their values.
    """
    if "${" not in string:
        return string

    if string.startswith("${") and string.endswith("}"):
        stringStripped = string[2:-1].strip()
        res = resolve_string(stringStripped)
        if res:
            return res

    # if multiple ${
    result = string
    start = 0
    while True:
        start = result.find("${", start)
        if start == -1:
            break
        end = result.find("}", start)
        if end == -1:
            break
        var_name = result[start + 2 : end]
        if var_name in env:
            result = result[:start] + str(env[var_name]) + result[end + 1 :]
        else:
            start = end + 1
    return result


def resolve_dict(data: dict, env: dict):
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = resolve_special_var(value, env)
        elif isinstance(value, dict):
            data[key] = resolve_dict(value, env)
        elif isinstance(value, list):
            data[key] = resolve_list(value, env)
    return data


def resolve_list(data: list, env: dict):
    for i, item in enumerate(data):
        if isinstance(item, list) and all(isinstance(i, str) for i in item):
            data[i] = [resolve_special_var(i, env) for i in item]
        elif isinstance(item, list):
            data[i] = resolve_list(item, env)
        elif isinstance(item, dict):
            data[i] = resolve_dict(item, env)
        elif isinstance(item, str):
            data[i] = resolve_special_var(item, env)
        else:
            pass
    return data


def resolve_auto(data: typing.Any, env: dict):
    if isinstance(data, str):
        return resolve_special_var(data, env)
    elif isinstance(data, list):
        return resolve_list(data, env)
    elif isinstance(data, dict):
        return resolve_dict(data, env)
