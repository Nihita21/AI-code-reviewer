// A small snippet with a few real problems, so a first-time visitor can see a review.
export const SAMPLE_CODE = `import os
import json


def load_users(path, cache={}):
    try:
        with open(path) as handle:
            data = json.load(handle)
    except Exception:
        pass

    for user in data:
        cache[user["id"]] = user
    return cache


def passes_rule(user):
    return eval(user["rule"])
`;
