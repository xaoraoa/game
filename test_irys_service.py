#!/usr/bin/env python3

import asyncio
import json

async def test_irys_service():
    """Test the Node.js Irys service communication"""
    try:
        request_data = {
            "action": "upload",
            "data": {"test": "data", "player": "0x1234567890123456789012345678901234567890"},
            "tags": [{"name": "Test", "value": "true"}]
        }
        
        print("🔍 Testing Node.js Irys service communication...")
        print(f"Request: {json.dumps(request_data, indent=2)}")
        
        # Start the Node.js process
        process = await asyncio.create_subprocess_exec(
            'node', 'irys_service.js',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd='/app/backend'
        )
        
        # Send request and get response
        stdout, stderr = await process.communicate(input=json.dumps(request_data).encode())
        
        print(f"Return code: {process.returncode}")
        print(f"STDERR: {stderr.decode()}")
        print(f"STDOUT: {stdout.decode()}")
        
        if process.returncode != 0:
            print(f"❌ Node.js process error: {stderr.decode()}")
            return {"success": False, "error": "Node.js process failed"}
        
        # Parse response - get the last line which should be JSON
        output_lines = stdout.decode().strip().split('\n')
        print(f"Output lines: {output_lines}")
        
        json_line = output_lines[-1]  # Last line should be the JSON response
        print(f"JSON line: {json_line}")
        
        response = json.loads(json_line)
        print(f"✅ Parsed response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        print(f"❌ Error calling Irys service: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_irys_service())
    print(f"\nFinal result: {result}")