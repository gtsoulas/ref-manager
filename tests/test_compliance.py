from django.test import TestCase
from datetime import date, timedelta
from core.models import Output

class ComplianceTests(TestCase):
    def test_compliant_within_3_months(self):
        """Output deposited within 92 days is compliant."""
        output = Output(
            title="Test",
            acceptance_date=date(2024, 1, 1),
            deposit_date=date(2024, 3, 1),  # 60 days
        )
        is_compliant, msg = output.check_oa_compliance()
        self.assertTrue(is_compliant)
    
    def test_non_compliant_exceeds_3_months(self):
        """Output deposited after 92 days is non-compliant."""
        output = Output(
            title="Test",
            acceptance_date=date(2024, 1, 1),
            deposit_date=date(2024, 6, 1),  # ~150 days
        )
        is_compliant, msg = output.check_oa_compliance()
        self.assertFalse(is_compliant)
    
    def test_missing_dates_unknown(self):
        """Missing dates returns None for compliance."""
        output = Output(title="Test")
        is_compliant, msg = output.check_oa_compliance()
        self.assertIsNone(is_compliant)


class DOIFetchTests(TestCase):
    def test_fetch_valid_doi(self):
        """Test fetching metadata for a known DOI."""
        from django.test import Client
        client = Client()
        client.login(username='testuser', password='testpass')
        
        response = client.get('/outputs/fetch-doi/', {
            'doi': '10.1038/nature12373'  # Famous Higgs paper
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('title', data.get('data', {}))
