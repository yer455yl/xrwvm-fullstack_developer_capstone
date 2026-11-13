import unittest
from app import app
class SentimentTests(unittest.TestCase):
    def test_polarity(self):
        client=app.test_client()
        for text,expected in [('Excellent friendly service. I love this car!','positive'),('Terrible service. I hate this dealership.','negative'),('The car is blue.','neutral')]:
            with self.subTest(text=text):
                self.assertEqual(client.get('/analyze/'+text).json['sentiment'],expected)
