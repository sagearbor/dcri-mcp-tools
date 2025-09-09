"""
Tests for Drug Accountability Reconciler Tool
"""

import pytest
from datetime import datetime, timedelta
from tools.drug_accountability_reconciler import run

class TestDrugAccountabilityReconciler:
    
    def test_successful_reconciliation(self):
        """Test successful drug accountability reconciliation"""
        current_date = datetime.now()
        input_data = {
            'drug_inventory': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50,
                    'lot_number': 'LOT123',
                    'expiry_date': (current_date + timedelta(days=365)).isoformat()
                }
            ],
            'drug_shipments': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 100,
                    'lot_number': 'LOT123',
                    'shipment_date': (current_date - timedelta(days=60)).isoformat(),
                    'shipment_id': 'SHIP001'
                }
            ],
            'drug_dispensing': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 45,
                    'lot_number': 'LOT123',
                    'dispensing_date': (current_date - timedelta(days=30)).isoformat()
                }
            ],
            'drug_returns': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 5,
                    'lot_number': 'LOT123',
                    'return_date': (current_date - timedelta(days=15)).isoformat(),
                    'disposition': 'returned'
                }
            ],
            'study_drug_info': {
                'DRUG001': {
                    'name': 'Study Drug A',
                    'lot_tracking_required': True,
                    'temperature_controlled': True
                }
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'reconciliation_data' in result
        
        recon_data = result['reconciliation_data']
        assert recon_data['overall_statistics']['total_sites'] == 1
        
        # Check site reconciliation
        site_recon = recon_data['site_reconciliation']['SITE001']
        assert site_recon['total_received'] == 100
        assert site_recon['total_dispensed'] == 45
        assert site_recon['total_returned'] == 5
        assert site_recon['expected_inventory'] == 50  # 100 - 45 - 5
        assert site_recon['actual_inventory'] == 50
        assert site_recon['inventory_variance'] == 0  # Perfect match
        assert site_recon['reconciliation_status'] == 'reconciled'
    
    def test_inventory_discrepancy_detection(self):
        """Test detection of inventory discrepancies"""
        current_date = datetime.now()
        input_data = {
            'drug_inventory': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 40,  # 10 units less than expected
                    'lot_number': 'LOT123'
                }
            ],
            'drug_shipments': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 100,
                    'lot_number': 'LOT123',
                    'shipment_date': (current_date - timedelta(days=60)).isoformat()
                }
            ],
            'drug_dispensing': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50,
                    'lot_number': 'LOT123',
                    'dispensing_date': (current_date - timedelta(days=30)).isoformat()
                }
            ],
            'study_drug_info': {
                'DRUG001': {
                    'name': 'Study Drug A'
                }
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        recon_data = result['reconciliation_data']
        
        # Should detect discrepancy
        assert len(recon_data['discrepancies']) > 0
        discrepancy = recon_data['discrepancies'][0]
        assert discrepancy['expected_inventory'] == 50  # 100 - 50
        assert discrepancy['actual_inventory'] == 40
        assert discrepancy['variance'] == -10  # Shortage
        assert discrepancy['variance_type'] == 'shortage'
        assert discrepancy['investigation_required'] is True
    
    def test_expiring_drug_alerts(self):
        """Test detection of expiring drugs"""
        current_date = datetime.now()
        input_data = {
            'drug_inventory': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50,
                    'lot_number': 'LOT123',
                    'expiry_date': (current_date + timedelta(days=20)).isoformat()  # Expires in 20 days
                }
            ],
            'drug_shipments': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50,
                    'lot_number': 'LOT123',
                    'shipment_date': (current_date - timedelta(days=30)).isoformat()
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        recon_data = result['reconciliation_data']
        
        # Should detect expiring drug alert
        assert len(recon_data['accountability_alerts']) > 0
        alert = next(a for a in recon_data['accountability_alerts'] if a['type'] == 'Drug Expiring Soon')
        assert alert['priority'] == 'urgent'
        assert alert['count'] == 1
    
    def test_temperature_excursion_tracking(self):
        """Test tracking of temperature excursions"""
        current_date = datetime.now()
        input_data = {
            'drug_inventory': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50,
                    'lot_number': 'LOT123'
                }
            ],
            'drug_shipments': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50,
                    'lot_number': 'LOT123',
                    'shipment_date': (current_date - timedelta(days=30)).isoformat(),
                    'temperature_excursion': True,
                    'excursion_details': 'Temperature exceeded 8°C for 2 hours during transport'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        recon_data = result['reconciliation_data']
        
        # Should track temperature excursion
        assert len(recon_data['accountability_alerts']) > 0
        temp_alert = next(a for a in recon_data['accountability_alerts'] if a['type'] == 'Temperature Excursion')
        assert temp_alert['priority'] == 'high'
    
    def test_multiple_sites_reconciliation(self):
        """Test reconciliation across multiple sites"""
        current_date = datetime.now()
        input_data = {
            'drug_inventory': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 30
                },
                {
                    'site_id': 'SITE002',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 25
                }
            ],
            'drug_shipments': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50,
                    'shipment_date': (current_date - timedelta(days=30)).isoformat()
                },
                {
                    'site_id': 'SITE002',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 40,
                    'shipment_date': (current_date - timedelta(days=25)).isoformat()
                }
            ],
            'drug_dispensing': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 20,
                    'dispensing_date': (current_date - timedelta(days=15)).isoformat()
                },
                {
                    'site_id': 'SITE002',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 15,
                    'dispensing_date': (current_date - timedelta(days=10)).isoformat()
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        recon_data = result['reconciliation_data']
        
        # Should reconcile both sites
        assert recon_data['overall_statistics']['total_sites'] == 2
        assert 'SITE001' in recon_data['site_reconciliation']
        assert 'SITE002' in recon_data['site_reconciliation']
        
        # Check individual site reconciliation
        site1 = recon_data['site_reconciliation']['SITE001']
        site2 = recon_data['site_reconciliation']['SITE002']
        
        assert site1['expected_inventory'] == 30  # 50 - 20
        assert site2['expected_inventory'] == 25  # 40 - 15
    
    def test_drug_destruction_tracking(self):
        """Test tracking of drug destruction"""
        current_date = datetime.now()
        input_data = {
            'drug_inventory': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 80
                }
            ],
            'drug_shipments': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 100,
                    'shipment_date': (current_date - timedelta(days=30)).isoformat()
                }
            ],
            'drug_dispensing': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 15,
                    'dispensing_date': (current_date - timedelta(days=15)).isoformat()
                }
            ],
            'drug_returns': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 5,
                    'return_date': (current_date - timedelta(days=10)).isoformat(),
                    'disposition': 'destroyed'  # Destruction
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        recon_data = result['reconciliation_data']
        
        # Should track destruction
        site_recon = recon_data['site_reconciliation']['SITE001']
        assert site_recon['total_destroyed'] == 5
        assert site_recon['expected_inventory'] == 80  # 100 - 15 - 5
    
    def test_discrepancy_severity_assessment(self):
        """Test severity assessment of discrepancies"""
        current_date = datetime.now()
        input_data = {
            'drug_inventory': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50  # Large discrepancy from expected 100
                }
            ],
            'drug_shipments': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 100,
                    'shipment_date': (current_date - timedelta(days=30)).isoformat()
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        recon_data = result['reconciliation_data']
        
        # Should assess as high severity due to large variance
        discrepancy = recon_data['discrepancies'][0]
        assert discrepancy['severity'] == 'critical'  # 50% variance
        assert discrepancy['investigation_required'] is True
    
    def test_lot_number_tracking(self):
        """Test lot number tracking across transactions"""
        current_date = datetime.now()
        input_data = {
            'drug_inventory': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50,
                    'lot_number': 'LOT123'
                }
            ],
            'drug_shipments': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50,
                    'lot_number': 'LOT123',
                    'shipment_date': (current_date - timedelta(days=30)).isoformat()
                }
            ],
            'drug_dispensing': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 0,  # No dispensing yet
                    'lot_number': 'LOT123',
                    'dispensing_date': (current_date - timedelta(days=15)).isoformat()
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        recon_data = result['reconciliation_data']
        
        # Should track lot numbers
        site_recon = recon_data['site_reconciliation']['SITE001']
        drug_product = site_recon['drug_products']['DRUG001']
        assert 'LOT123' in drug_product['lot_numbers']
    
    def test_recommendations_generation(self):
        """Test generation of recommendations"""
        current_date = datetime.now()
        input_data = {
            'drug_inventory': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 20,  # Major discrepancy
                    'lot_number': 'LOT123',
                    'expiry_date': (current_date + timedelta(days=10)).isoformat()  # Expiring soon
                }
            ],
            'drug_shipments': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 100,
                    'lot_number': 'LOT123',
                    'shipment_date': (current_date - timedelta(days=30)).isoformat(),
                    'temperature_excursion': True
                }
            ],
            'drug_dispensing': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 30,
                    'lot_number': 'LOT123',
                    'dispensing_date': (current_date - timedelta(days=15)).isoformat()
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        recon_data = result['reconciliation_data']
        
        # Should generate multiple recommendations
        recommendations = recon_data['recommendations']
        assert len(recommendations) > 0
        
        # Should include discrepancy recommendation
        assert any('discrepanc' in rec.lower() for rec in recommendations)
        
        # Should include expiring drug recommendation
        assert any('expiring' in rec.lower() for rec in recommendations)
    
    def test_empty_data_handling(self):
        """Test handling of empty data"""
        input_data = {
            'drug_inventory': [],
            'drug_shipments': []
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'No drug inventory or shipment data provided' in result['error']
    
    def test_reconciliation_period_filtering(self):
        """Test filtering by reconciliation period"""
        current_date = datetime.now()
        input_data = {
            'drug_inventory': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50
                }
            ],
            'drug_shipments': [
                {
                    'site_id': 'SITE001',
                    'drug_product_id': 'DRUG001',
                    'quantity_units': 50,
                    'shipment_date': (current_date - timedelta(days=120)).isoformat()  # Outside period
                }
            ],
            'reconciliation_period': 30  # Only last 30 days
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        recon_data = result['reconciliation_data']
        
        # Old shipment should not be included
        site_recon = recon_data['site_reconciliation']['SITE001']
        assert site_recon['total_received'] == 0