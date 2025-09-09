"""
Tests for Translation Validator Tool
"""

import pytest
import json
from tools.translation_validator import run


class TestTranslationValidator:
    
    def test_basic_terminology_validation(self):
        """Test basic terminology validation"""
        source_text = "Please complete the informed consent form before participating in the clinical trial."
        translations = {
            'es': "Por favor complete el formulario de consentimiento informado antes de participar en el ensayo clínico.",
            'fr': "Veuillez remplir le formulaire de consentement éclairé avant de participer à l'essai clinique."
        }
        
        input_data = {
            'source_text': source_text,
            'translations': translations,
            'validation_type': 'terminology'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        validation_results = result['validation_results']
        
        assert 'language_scores' in validation_results
        assert 'es' in validation_results['language_scores']
        assert 'fr' in validation_results['language_scores']
        assert validation_results['overall_score'] > 0
    
    def test_structure_validation(self):
        """Test document structure validation"""
        source_text = """Title: Clinical Study Protocol
        
        Section 1: Introduction
        This is the introduction.
        
        Section 2: Objectives
        • Primary objective
        • Secondary objective
        
        1. First numbered item
        2. Second numbered item"""
        
        translations = {
            'es': """Título: Protocolo de Estudio Clínico
            
            Sección 1: Introducción
            Esta es la introducción.
            
            Sección 2: Objetivos
            • Objetivo primario
            • Objetivo secundario
            
            1. Primer elemento numerado
            2. Segundo elemento numerado"""
        }
        
        input_data = {
            'source_text': source_text,
            'translations': translations,
            'validation_type': 'structure'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        validation_results = result['validation_results']
        assert len(validation_results['issues_found']) == 0  # Should match structure
    
    def test_completeness_validation(self):
        """Test translation completeness validation"""
        source_text = "This is a comprehensive clinical study protocol document that contains detailed information about the study procedures, inclusion and exclusion criteria, and safety monitoring procedures."
        
        # Incomplete translation (much shorter)
        translations = {
            'es': "Protocolo de estudio.",
            'de': "Dies ist ein umfassendes klinisches Studienprotokoll-Dokument."
        }
        
        input_data = {
            'source_text': source_text,
            'translations': translations,
            'validation_type': 'completeness'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        validation_results = result['validation_results']
        
        # Should find completeness issues
        issues = validation_results['issues_found']
        completeness_issues = [i for i in issues if i['type'] in ['incomplete_translation', 'insufficient_content']]
        assert len(completeness_issues) > 0
        
        # Spanish should have low score due to incompleteness
        assert validation_results['language_scores']['es'] < 70
    
    def test_terminology_glossary_validation(self):
        """Test validation with terminology glossary"""
        source_text = "The adverse event was reported as a serious adverse event to the IRB."
        
        translations = {
            'es': "El evento adverso fue reportado como un evento adverso serio al IRB.",
            'fr': "L'événement indésirable a été signalé comme un événement indésirable grave au CEI."
        }
        
        glossary = {
            'adverse event': {
                'es': 'evento adverso',
                'fr': 'événement indésirable'
            },
            'serious adverse event': {
                'es': 'evento adverso grave',  # Note: translation uses 'serio' instead
                'fr': 'événement indésirable grave'
            },
            'IRB': {
                'es': 'CEI',  # Should use CEI, not IRB
                'fr': 'CEI'
            }
        }
        
        input_data = {
            'source_text': source_text,
            'translations': translations,
            'validation_type': 'terminology',
            'terminology_glossary': glossary
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        validation_results = result['validation_results']
        
        # Should find glossary inconsistencies
        issues = validation_results['issues_found']
        glossary_issues = [i for i in issues if i['type'] == 'glossary_inconsistency']
        assert len(glossary_issues) > 0
    
    def test_formatting_validation(self):
        """Test formatting consistency validation"""
        source_text = """<h1>Study Title</h1>
        <p>This study uses <strong>randomized</strong> design.</p>
        <ul>
        <li>Visit 1</li>
        <li>Visit 2</li>
        </ul>
        Contact: <a href="mailto:study@example.com">study@example.com</a>"""
        
        # Missing some HTML tags in translation
        translations = {
            'es': """<h1>Título del Estudio</h1>
            <p>Este estudio utiliza diseño randomizado.</p>
            <ul>
            <li>Visita 1</li>
            <li>Visita 2</li>
            </ul>
            Contacto: study@example.com"""  # Missing <a> tag
        }
        
        input_data = {
            'source_text': source_text,
            'translations': translations,
            'validation_type': 'all',
            'check_formatting': True
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        validation_results = result['validation_results']
        
        # Should find HTML tag mismatch
        issues = validation_results['issues_found']
        formatting_issues = [i for i in issues if i['type'] in ['html_tag_mismatch', 'missing_special_chars']]
        assert len(formatting_issues) > 0
    
    def test_medical_terms_only_mode(self):
        """Test validation focusing only on medical terms"""
        source_text = "The patient experienced an adverse event during the clinical trial. The study coordinator documented the event in the case report form."
        
        translations = {
            'es': "El paciente experimentó un evento adverso durante el ensayo clínico. El coordinador del estudio documentó el evento."
        }
        
        input_data = {
            'source_text': source_text,
            'translations': translations,
            'medical_terms_only': True,
            'validation_type': 'terminology'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        validation_results = result['validation_results']
        
        # Should focus on medical/clinical terms
        assert 'overall_score' in validation_results
        assert len(validation_results['recommendations']) > 0
    
    def test_severity_threshold_filtering(self):
        """Test filtering issues by severity threshold"""
        source_text = "Critical: This urgent clinical trial requires immediate adverse event reporting."
        
        translations = {
            'es': "Crítico: Este ensayo clínico urgente requiere.",  # Incomplete
            'fr': "Critique: Cet essai clinique urgent nécessite un rapport immédiat d'événement indésirable."
        }
        
        # Test with high severity threshold
        input_data = {
            'source_text': source_text,
            'translations': translations,
            'validation_type': 'all',
            'severity_threshold': 'high'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        validation_results = result['validation_results']
        
        # Should only show high severity issues
        high_severity_issues = [i for i in validation_results['issues_found'] if i.get('severity') == 'high']
        total_issues = len(validation_results['issues_found'])
        
        # All returned issues should be high severity (or the filter worked)
        assert total_issues == len(high_severity_issues) or total_issues == 0
    
    def test_multiple_languages_comprehensive(self):
        """Test comprehensive validation with multiple languages"""
        source_text = """Clinical Study Protocol Amendment #3
        
        Important Safety Update:
        New adverse events have been identified. All sites must:
        • Update safety monitoring procedures
        • Report events within 24 hours
        • Contact the medical monitor immediately
        
        For questions, contact: safety@clinicaltrial.com"""
        
        translations = {
            'es': """Enmienda del Protocolo de Estudio Clínico #3
            
            Actualización Importante de Seguridad:
            Se han identificado nuevos eventos adversos. Todos los sitios deben:
            • Actualizar procedimientos de monitoreo de seguridad
            • Reportar eventos dentro de 24 horas
            • Contactar al monitor médico inmediatamente
            
            Para preguntas, contactar: safety@clinicaltrial.com""",
            
            'de': """Klinisches Studienprotokoll Änderung #3
            
            Wichtiges Sicherheits-Update:
            Neue Nebenwirkungen wurden identifiziert. Alle Zentren müssen:
            • Sicherheitsüberwachungsverfahren aktualisieren
            • Ereignisse innerhalb von 24 Stunden melden
            • Sofort den medizinischen Monitor kontaktieren
            
            Für Fragen kontaktieren: safety@clinicaltrial.com""",
            
            'fr': """Amendement du Protocole d'Étude Clinique #3
            
            Mise à jour Importante de Sécurité:
            De nouveaux événements indésirables ont été identifiés. Tous les sites doivent:
            • Mettre à jour les procédures de surveillance de sécurité
            • Signaler les événements dans les 24 heures
            • Contacter immédiatement le moniteur médical
            
            Pour questions, contacter: safety@clinicaltrial.com"""
        }
        
        glossary = {
            'adverse events': {
                'es': 'eventos adversos',
                'de': 'unerwünschte Ereignisse',  # Note: translation uses 'Nebenwirkungen'
                'fr': 'événements indésirables'
            },
            'medical monitor': {
                'es': 'monitor médico',
                'de': 'medizinischer Monitor',
                'fr': 'moniteur médical'
            }
        }
        
        input_data = {
            'source_text': source_text,
            'translations': translations,
            'validation_type': 'all',
            'terminology_glossary': glossary,
            'check_formatting': True,
            'severity_threshold': 'medium'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        validation_results = result['validation_results']
        
        # Check comprehensive results
        assert len(validation_results['language_scores']) == 3
        assert 'es' in validation_results['language_scores']
        assert 'de' in validation_results['language_scores']
        assert 'fr' in validation_results['language_scores']
        
        # Check overall score calculation
        assert validation_results['overall_score'] > 0
        assert validation_results['overall_score'] <= 100
        
        # Check recommendations
        assert len(validation_results['recommendations']) > 0
        
        # Check summary
        summary = result['summary']
        assert summary['total_languages'] == 3
        assert summary['validation_type'] == 'all'
        assert 'overall_quality' in summary
    
    def test_error_handling_no_source_text(self):
        """Test error handling when no source text provided"""
        input_data = {
            'translations': {'es': 'Some translation'}
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'source_text is required' in result['error']
    
    def test_error_handling_no_translations(self):
        """Test error handling when no translations provided"""
        input_data = {
            'source_text': 'Some source text'
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'translations dictionary is required' in result['error']