"""Retained owned-selection behavior on reference and unactivated routes."""

import json

from callback_selection import observe_owned_child_failure

if __name__ == "__main__":
    print(json.dumps(observe_owned_child_failure(), indent=2, sort_keys=True))
