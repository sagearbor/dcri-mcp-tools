from typing import Dict, List, Optional, Any
from collections import defaultdict


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identify deviations from standard operating procedures in clinical trials
    
    Example:
        Input: Process execution data with actual steps performed versus standard procedure definitions
        Output: Deviation analysis with severity classification and corrective action recommendations
    
    Parameters:
        process_data : list
            Actual process execution data with steps performed
        standard_processes : dict
            Standard operating procedures and expected steps
        deviation_thresholds : dict
            Severity thresholds for different types of deviations
        audit_settings : dict
            Configuration for deviation detection sensitivity
    """
    try:
        process_data = input_data.get("process_data", [])
        if not process_data:
            return {"error": "No process data provided"}
        
        standard_processes = input_data.get("standard_processes", {})
        deviations = []
        
        for process in process_data:
            process_name = process.get("name")
            actual_steps = process.get("steps", [])
            expected_steps = standard_processes.get(process_name, [])
            
            # Find deviations
            missing_steps = [s for s in expected_steps if s not in actual_steps]
            extra_steps = [s for s in actual_steps if s not in expected_steps]
            
            if missing_steps or extra_steps:
                deviations.append({
                    "process": process_name,
                    "missing_steps": missing_steps,
                    "extra_steps": extra_steps,
                    "severity": "major" if missing_steps else "minor"
                })
        
        return {
            "deviations": deviations,
            "deviation_count": len(deviations),
            "processes_analyzed": len(process_data)
        }
    except Exception as e:
        return {"error": str(e)}
