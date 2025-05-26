from inference_gateway import InferenceGatewayClient

# Initialize client
client = InferenceGatewayClient("http://localhost:8080")

# List available MCP tools works when MCP_ENABLE and MCP_EXPOSE are set on the gateway
tools = client.list_tools()
print("Available tools:", tools)
