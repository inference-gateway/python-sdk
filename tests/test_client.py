import unittest
from unittest.mock import patch, Mock
from inference_gateway.client import InferenceGatewayClient


class TestInferenceGatewayClient(unittest.TestCase):
    def setUp(self):
        self.client = InferenceGatewayClient("http://localhost:8080")

    @patch('inference_gateway.client.requests.get')
    def test_list_models(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"models": ["model1", "model2"]}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        models = self.client.list_models()
        self.assertEqual(models, {"models": ["model1", "model2"]})

    @patch('inference_gateway.client.requests.post')
    def test_generate_content(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "Response": {"Content": "generated content"}}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        response = self.client.generate_content("provider", "model", "prompt")
        self.assertEqual(
            response, {"Response": {"Content": "generated content"}})


if __name__ == '__main__':
    unittest.main()
