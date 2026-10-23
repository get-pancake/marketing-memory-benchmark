"""Transport-only tests with explicit response stubs; no model inference."""
import io
import json
import unittest
from unittest.mock import patch

from prototype.run import ModelClient, messages


class ModelClientTests(unittest.TestCase):
    def setUp(self):
        self.config = {"base_url": "http://127.0.0.1:8080/v1", "model": "unit-test-stub",
                       "max_output_tokens": 100, "temperature": 0, "seed": 4}

    def test_transport_payload_and_response_receipt(self):
        response = {"id": "stub-only", "model": "unit-test-stub", "usage": {"prompt_tokens": 12, "completion_tokens": 4},
                    "choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}]}
        def respond(request, timeout):
            body = json.loads(request.data)
            self.assertEqual(body["seed"], 4)
            self.assertEqual(body["max_tokens"], 100)
            self.assertEqual(request.full_url, "http://127.0.0.1:8080/v1/chat/completions")
            return io.BytesIO(json.dumps(response).encode())
        with patch("urllib.request.urlopen", side_effect=respond):
            client = ModelClient(self.config)
            self.assertEqual(client.reserve([]), 0)
            result = client.complete([])
        self.assertEqual(result["response_model"], "unit-test-stub")
        self.assertEqual(result["usage"]["prompt_tokens"], 12)
        self.assertIsNone(result["billed_cost_usd"])

    def test_remote_spending_cap_is_checked_before_send(self):
        config = dict(self.config, base_url="https://example.com/v1", api_key_env="RESEARCH_TEST_KEY",
                      input_usd_per_million=1, output_usd_per_million=1, max_spend_usd=.000001,
                      authorization_reference="unit-test only", price_source="synthetic test rate")
        with patch.dict("os.environ", {"RESEARCH_TEST_KEY": "synthetic-unit-test-value"}):
            client = ModelClient(config)
            with self.assertRaises(ValueError):
                client.reserve([{"role": "user", "content": "test"}])

    def test_missing_response_never_falls_back_to_policy_reference(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("simulated timeout")):
            with self.assertRaises(TimeoutError):
                ModelClient(self.config).complete([])

    def test_invalid_endpoint_and_negative_cap(self):
        for config in (dict(self.config, base_url="http://example.com/v1"),
                       dict(self.config, base_url="https://user:password@example.com/v1"),
                       dict(self.config, max_output_tokens=-1)):
            with self.subTest(config=config):
                with self.assertRaises(ValueError):
                    ModelClient(config)


if __name__ == "__main__":
    unittest.main()
