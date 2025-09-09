import pytest
from tools.data_trend_analyzer import run


def test_data_trend_analyzer_basic():
    """Test basic trend analysis functionality."""
    input_data = {
        "data": "subject_id,age,weight,temperature\n001,25,70,98.6\n002,35,75,99.2\n003,45,80,101.5\n004,55,85,97.8\n005,65,90,98.9",
        "analysis_fields": ["age", "weight", "temperature"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "trend_analysis" in result
    assert len(result["trend_analysis"]) == 3
    assert "statistics" in result
    
    # Check that each field has been analyzed
    assert "age" in result["trend_analysis"]
    assert "weight" in result["trend_analysis"]
    assert "temperature" in result["trend_analysis"]
    
    # Check age analysis
    age_analysis = result["trend_analysis"]["age"]
    assert age_analysis["valid_values"] == 5
    assert "statistics" in age_analysis
    assert "trend" in age_analysis
    
    # Check statistics
    assert result["statistics"]["total_records"] == 5
    assert result["statistics"]["fields_analyzed"] == 3


def test_data_trend_analyzer_auto_detect_fields():
    """Test automatic detection of numeric fields."""
    input_data = {
        "data": "subject_id,age,weight,site,temperature\n001,25,70,Site A,98.6\n002,35,75,Site B,99.2\n003,45,80,Site A,101.5",
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    # Should auto-detect age, weight, temperature (not site which is text)
    assert len(result["trend_analysis"]) >= 3
    assert "age" in result["trend_analysis"]
    assert "weight" in result["trend_analysis"]
    assert "temperature" in result["trend_analysis"]
    # Site should not be analyzed as it's not numeric
    assert "site" not in result["trend_analysis"]


def test_data_trend_analyzer_outlier_detection():
    """Test outlier detection functionality."""
    input_data = {
        "data": "subject_id,age\n001,25\n002,30\n003,28\n004,32\n005,150\n006,29",
        "analysis_fields": ["age"],
        "sensitivity": "high"  # More sensitive to outliers
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["outliers"]) > 0
    
    # Should detect age 150 as an outlier
    outlier = result["outliers"][0]
    assert outlier["field"] == "age"
    assert outlier["value"] == 150.0
    assert outlier["type"] == "statistical_outlier"
    assert "z_score" in outlier


def test_data_trend_analyzer_trend_detection():
    """Test trend pattern detection."""
    input_data = {
        "data": "subject_id,increasing_values,decreasing_values,stable_values\n001,10,100,50\n002,20,90,50\n003,30,80,50\n004,40,70,50\n005,50,60,50",
        "analysis_fields": ["increasing_values", "decreasing_values", "stable_values"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    # Check increasing trend
    increasing_trend = result["trend_analysis"]["increasing_values"]["trend"]
    assert increasing_trend["pattern"] == "increasing"
    assert increasing_trend["strength"] > 0
    
    # Check decreasing trend
    decreasing_trend = result["trend_analysis"]["decreasing_values"]["trend"]
    assert decreasing_trend["pattern"] == "decreasing"
    assert decreasing_trend["strength"] > 0
    
    # Check stable trend
    stable_trend = result["trend_analysis"]["stable_values"]["trend"]
    assert stable_trend["pattern"] == "stable"


def test_data_trend_analyzer_correlations():
    """Test correlation detection between fields."""
    input_data = {
        "data": "subject_id,height,weight\n001,160,50\n002,170,60\n003,180,70\n004,190,80\n005,200,90",
        "analysis_fields": ["height", "weight"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "patterns" in result
    assert "correlations" in result["patterns"]
    
    # Height and weight should be strongly correlated
    correlations = result["patterns"]["correlations"]
    assert len(correlations) > 0
    correlation = correlations[0]
    assert correlation["field1"] == "height"
    assert correlation["field2"] == "weight"
    assert abs(correlation["correlation"]) > 0.9  # Should be very strong correlation
    assert correlation["strength"] == "strong"


def test_data_trend_analyzer_distribution_analysis():
    """Test distribution analysis functionality."""
    input_data = {
        "data": "subject_id,normal_dist,uniform_dist\n001,50,10\n002,52,20\n003,48,30\n004,51,40\n005,49,50\n006,50,60",
        "analysis_fields": ["normal_dist", "uniform_dist"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    # Check distribution analysis
    normal_analysis = result["trend_analysis"]["normal_dist"]["distribution_analysis"]
    assert "quartiles" in normal_analysis
    assert "skewness" in normal_analysis
    assert "distribution_type" in normal_analysis
    
    uniform_analysis = result["trend_analysis"]["uniform_dist"]["distribution_analysis"]
    assert uniform_analysis["distribution_type"] == "approximately_uniform"


def test_data_trend_analyzer_sensitivity_levels():
    """Test different sensitivity levels."""
    # Data with mild outlier
    data = "subject_id,value\n001,10\n002,12\n003,11\n004,13\n005,20"
    
    # High sensitivity should detect more outliers
    high_sensitivity = run({
        "data": data,
        "analysis_fields": ["value"],
        "sensitivity": "high"
    })
    
    # Low sensitivity should detect fewer outliers
    low_sensitivity = run({
        "data": data,
        "analysis_fields": ["value"],
        "sensitivity": "low"
    })
    
    assert high_sensitivity["success"] == True
    assert low_sensitivity["success"] == True
    
    # High sensitivity should detect more anomalies/outliers
    high_anomalies = len(high_sensitivity["anomalies_detected"]) + len(high_sensitivity["outliers"])
    low_anomalies = len(low_sensitivity["anomalies_detected"]) + len(low_sensitivity["outliers"])
    
    assert high_anomalies >= low_anomalies


def test_data_trend_analyzer_temporal_patterns():
    """Test temporal pattern analysis."""
    input_data = {
        "data": "subject_id,date,score\n001,2024-01-01,10\n002,2024-01-02,15\n003,2024-01-03,20\n004,2024-01-04,25\n005,2024-01-05,30",
        "analysis_fields": ["score"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "patterns" in result
    
    # Should detect temporal pattern if date field is recognized
    if result["patterns"]["temporal_patterns"]:
        temporal_pattern = result["patterns"]["temporal_patterns"][0]
        assert "date_field" in temporal_pattern
        assert "temporal_trends" in temporal_pattern


def test_data_trend_analyzer_mixed_data_types():
    """Test handling of mixed data types."""
    input_data = {
        "data": "subject_id,numeric_field,text_field,mixed_field\n001,10,text1,15\n002,20,text2,abc\n003,30,text3,25",
        "analysis_fields": ["numeric_field", "mixed_field"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    # Numeric field should be fully analyzed
    numeric_analysis = result["trend_analysis"]["numeric_field"]
    assert numeric_analysis["valid_values"] == 3
    
    # Mixed field should have fewer valid values due to non-numeric data
    mixed_analysis = result["trend_analysis"]["mixed_field"]
    assert mixed_analysis["valid_values"] < 3  # Should skip the 'abc' value


def test_data_trend_analyzer_insufficient_data():
    """Test handling of insufficient data."""
    input_data = {
        "data": "subject_id,value\n001,10\n002,20",  # Only 2 records
        "analysis_fields": ["value"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    # Should still process but with limited analysis
    value_analysis = result["trend_analysis"]["value"]
    assert value_analysis["valid_values"] == 2


def test_data_trend_analyzer_empty_data():
    """Test handling of empty data."""
    input_data = {
        "data": "",
        "analysis_fields": ["value"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert result["trend_analysis"] == {}
    assert result["anomalies_detected"] == []
    assert result["outliers"] == []


def test_data_trend_analyzer_no_numeric_fields():
    """Test handling when no numeric fields are found."""
    input_data = {
        "data": "subject_id,text1,text2\n001,abc,def\n002,ghi,jkl\n003,mno,pqr",
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    # Should have minimal analysis - might detect subject_id as numeric field
    # The auto-detection tries to find numeric fields
    assert len(result["trend_analysis"]) <= 1  # At most one field might be detected


def test_data_trend_analyzer_statistics_generation():
    """Test comprehensive statistics generation."""
    input_data = {
        "data": "subject_id,field1,field2,field3\n001,10,100,5\n002,20,90,15\n003,30,80,25\n004,40,70,35\n005,5000,60,45",  # field1 has extreme outlier
        "analysis_fields": ["field1", "field2", "field3"],
        "sensitivity": "high"  # Use high sensitivity to detect outliers
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    stats = result["statistics"]
    assert stats["total_records"] == 5
    assert stats["fields_analyzed"] == 3
    assert "total_outliers" in stats
    assert "total_anomalies" in stats
    assert "outlier_rate" in stats
    assert "data_quality_indicators" in stats
    
    # Should detect the outlier in field1
    assert stats["total_outliers"] > 0 or stats["total_anomalies"] > 0


def test_data_trend_analyzer_large_dataset():
    """Test performance with larger dataset."""
    # Create dataset with 50 records
    data_lines = ["subject_id,value1,value2"]
    for i in range(50):
        val1 = 50 + (i % 20) - 10  # Values around 50 with some variation
        val2 = 100 + (i * 2) % 30  # Increasing pattern with cycles
        data_lines.append(f"{i+1:03d},{val1},{val2}")
    
    input_data = {
        "data": "\n".join(data_lines),
        "analysis_fields": ["value1", "value2"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["statistics"]["total_records"] == 50
    assert result["statistics"]["fields_analyzed"] == 2
    
    # Should handle large dataset without issues
    assert "trend_analysis" in result
    assert len(result["trend_analysis"]) == 2


def test_data_trend_analyzer_edge_values():
    """Test handling of edge values (zeros, negatives, very large numbers)."""
    input_data = {
        "data": "subject_id,values\n001,0\n002,-50\n003,1000000\n004,10.5\n005,-10.7",
        "analysis_fields": ["values"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    values_analysis = result["trend_analysis"]["values"]
    assert values_analysis["valid_values"] == 5
    
    # Should handle negative, zero, and very large values
    stats = values_analysis["statistics"]
    assert "min" in stats
    assert "max" in stats
    assert stats["min"] < 0  # Should include negative values
    assert stats["max"] > 100000  # Should include large values


def test_data_trend_analyzer_decimal_precision():
    """Test handling of decimal values with various precisions."""
    input_data = {
        "data": "subject_id,precise_values\n001,1.23456\n002,2.7\n003,3.14159\n004,4.0\n005,5.999",
        "analysis_fields": ["precise_values"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    analysis = result["trend_analysis"]["precise_values"]
    assert analysis["valid_values"] == 5
    
    # Statistics should be rounded appropriately
    assert "statistics" in analysis
    stats = analysis["statistics"]
    assert isinstance(stats["mean"], (int, float))
    assert isinstance(stats["std_dev"], (int, float))


def test_data_trend_analyzer_variable_pattern():
    """Test detection of variable/random patterns."""
    input_data = {
        "data": "subject_id,random_values\n001,10\n002,5\n003,20\n004,3\n005,15\n006,8\n007,18",
        "analysis_fields": ["random_values"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    trend = result["trend_analysis"]["random_values"]["trend"]
    # Should detect variable pattern due to up-and-down values
    assert trend["pattern"] in ["variable", "stable"]


def test_data_trend_analyzer_identical_values():
    """Test handling of identical values."""
    input_data = {
        "data": "subject_id,constant_values\n001,42\n002,42\n003,42\n004,42\n005,42",
        "analysis_fields": ["constant_values"],
        "sensitivity": "medium"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    analysis = result["trend_analysis"]["constant_values"]
    assert analysis["statistics"]["std_dev"] == 0.0
    assert analysis["trend"]["pattern"] == "stable"
    assert len(result["outliers"]) == 0  # No outliers in constant values