"""Offline application-policy and HTTP contract checks; no model-quality claims."""

import io
import json
import unittest
from unittest.mock import patch

from route_ticket import build_request, call_api, select_queue


def choice_response(choice="billing", probability=0.95, confidence=0.2):
    return {"answers": [{
        "name": "department",
        "type": "choice",
        "choice": choice,
        "confidence": confidence,
        "probabilities": [
            {"value": value, "probability": (
                probability if value == choice else (1 - probability) / 3
            )}
            for value in ("billing", "product", "account", "other")
        ],
    }]}


class RoutingTests(unittest.TestCase):
    def test_selected_probability_controls_route_not_confidence(self):
        self.assertEqual(select_queue(choice_response()), {
            "queue": "billing", "reason": "selected",
        })
        self.assertEqual(select_queue(choice_response(probability=0.5, confidence=0.99)), {
            "queue": "review", "reason": "low_probability",
        })

    def test_threshold_boundary(self):
        self.assertEqual(select_queue(choice_response(probability=0.8))["queue"], "billing")
        self.assertEqual(select_queue(choice_response(probability=0.8), 0.9)["queue"], "review")

    def test_refusal_and_no_match_stay_distinct(self):
        self.assertEqual(select_queue({"answers": [{
            "name": "department", "type": "refusal",
        }]}), {"queue": "review", "reason": "refusal"})
        self.assertEqual(select_queue(choice_response(choice="other")), {
            "queue": "review", "reason": "no_match",
        })

    def test_lookup_uses_name(self):
        response = choice_response()
        response["answers"].insert(0, {"type": "predicate", "name": "unrelated", "probability": 0.9})
        self.assertEqual(select_queue(response)["queue"], "billing")

    def test_missing_duplicate_wrong_type_and_unknown_choice_are_errors(self):
        duplicate = choice_response()
        duplicate["answers"] *= 2
        for response in (
            {}, {"answers": []}, {"answers": [None]}, duplicate,
            {"answers": [{"name": "department", "type": "predicate", "probability": 0}]},
            {"answers": [{"name": "department", "type": "choice", "choice": "invented"}]},
        ):
            with self.subTest(response=response), self.assertRaises(ValueError):
                select_queue(response)

    def test_missing_duplicate_or_invalid_selected_probability_is_error(self):
        for probability in (None, True, -0.1, 1.1, float("nan"), float("inf")):
            response = choice_response()
            response["answers"][0]["probabilities"][0]["probability"] = probability
            with self.subTest(probability=probability), self.assertRaises(ValueError):
                select_queue(response)
        for distribution in ([], None, [None], [
            {"value": "billing", "probability": 0.9},
            {"value": "billing", "probability": 0.9},
        ]):
            response = choice_response()
            response["answers"][0]["probabilities"] = distribution
            with self.subTest(distribution=distribution), self.assertRaises(ValueError):
                select_queue(response)

    def test_invalid_threshold_is_error(self):
        for threshold in (-1, 2, float("nan"), float("inf"), True):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                select_queue(choice_response(), threshold)

    def test_http_request_preserves_payload_and_authentication(self):
        # The mock checks actual serialization without sending data to the API.
        response = io.BytesIO(json.dumps(choice_response()).encode())
        payload = build_request("An account access request.")
        with patch("route_ticket.urlopen", return_value=response) as send:
            self.assertEqual(call_api(payload, "example-key"), choice_response())
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.openai.com/v1/decisions")
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer example-key")
        self.assertEqual(json.loads(request.data), payload)
        self.assertEqual(send.call_args.kwargs["timeout"], 30)


if __name__ == "__main__":
    unittest.main()
