import json
import os
import tempfile
import unittest
from har_inspector.parser import HarParser


class TestHarParser(unittest.TestCase):
    
    def setUp(self):
        # Create a sample HAR file for testing
        self.har_data = {
            "log": {
                "version": "1.2",
                "creator": {"name": "Test", "version": "1.0"},
                "entries": [
                    {
                        "request": {
                            "method": "GET",
                            "url": "https://api.example.com/v1/users",
                            "headers": [
                                {"name": "Accept", "value": "application/json"}
                            ],
                            "queryString": [
                                {"name": "page", "value": "1"}
                            ]
                        },
                        "response": {
                            "status": 200,
                            "bodySize": 1024
                        },
                        "time": 150
                    },
                    {
                        "request": {
                            "method": "POST",
                            "url": "https://example.com/login",
                            "headers": [
                                {"name": "Content-Type", "value": "application/json"}
                            ],
                            "postData": {
                                "mimeType": "application/json",
                                "text": "{\"username\":\"test\",\"password\":\"test123\"}"
                            }
                        },
                        "response": {
                            "status": 200,
                            "bodySize": 512
                        },
                        "time": 200
                    }
                ]
            }
        }
        
        # Create a temporary HAR file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.har_file_path = os.path.join(self.temp_dir.name, "test.har")
        
        with open(self.har_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.har_data, f)
            
        self.parser = HarParser(self.har_file_path)
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_load_har_file(self):
        self.assertEqual(self.parser.har_data, self.har_data)
        
    def test_get_endpoints(self):
        endpoints = self.parser.get_endpoints()
        self.assertEqual(len(endpoints), 2)
        self.assertEqual(endpoints[0]['method'], 'GET')
        self.assertEqual(endpoints[0]['domain'], 'api.example.com')
        self.assertEqual(endpoints[0]['path'], '/v1/users')
        
    def test_filter_by_domain(self):
        endpoints = self.parser.get_endpoints(domain='api.example.com')
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0]['domain'], 'api.example.com')
        
    def test_filter_by_method(self):
        endpoints = self.parser.get_endpoints(method='POST')
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0]['method'], 'POST')
        
    def test_get_api_endpoints(self):
        endpoints = self.parser.get_api_endpoints()
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0]['domain'], 'api.example.com')
        
    def test_get_unique_domains(self):
        domains = self.parser.get_unique_domains()
        self.assertEqual(len(domains), 2)
        self.assertIn('api.example.com', domains)
        self.assertIn('example.com', domains)
        
    def test_export_to_json(self):
        endpoints = self.parser.get_endpoints()
        output_file = os.path.join(self.temp_dir.name, "output.json")
        
        self.parser.export_endpoints(endpoints, output_file)
        
        # Check if file exists
        self.assertTrue(os.path.exists(output_file))
        
        # Check if content is correct
        with open(output_file, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
            
        self.assertEqual(len(exported_data), 2)
        self.assertEqual(exported_data[0]['domain'], 'api.example.com')
        self.assertEqual(exported_data[1]['method'], 'POST')
        
    def test_export_to_csv(self):
        endpoints = self.parser.get_endpoints()
        output_file = os.path.join(self.temp_dir.name, "output.csv")
        
        self.parser.export_endpoints(endpoints, output_file)
        
        # Check if file exists
        self.assertTrue(os.path.exists(output_file))
        
        # Check if content is correct (basic check)
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn('url,method,protocol,domain,path,status_code,response_size,time', content)
        self.assertIn('api.example.com', content)
        self.assertIn('example.com/login', content)
        
    def test_invalid_har_file(self):
        invalid_file = os.path.join(self.temp_dir.name, "invalid.har")
        
        with open(invalid_file, 'w', encoding='utf-8') as f:
            f.write("This is not a valid JSON file")
            
        with self.assertRaises(ValueError):
            HarParser(invalid_file)
            
    def test_nonexistent_har_file(self):
        nonexistent_file = os.path.join(self.temp_dir.name, "nonexistent.har")
        
        with self.assertRaises(FileNotFoundError):
            HarParser(nonexistent_file)
            
    def test_empty_har_file(self):
        empty_file = os.path.join(self.temp_dir.name, "empty.har")
        
        with open(empty_file, 'w', encoding='utf-8') as f:
            f.write("{}")
            
        parser = HarParser(empty_file)
        endpoints = parser.get_endpoints()
        
        self.assertEqual(len(endpoints), 0)


if __name__ == '__main__':
    unittest.main()
