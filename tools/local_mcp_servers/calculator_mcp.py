#!/usr/bin/env python3

"""
Calculator MCP Server
A comprehensive calculator with basic arithmetic, scientific functions, and unit conversions.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional, Union
import math
import json
import re

# Create the MCP server
mcp = FastMCP("Calculator")

@mcp.tool()
def basic_calculation(expression: str) -> dict:
    """
    Perform basic arithmetic calculations.
    
    Args:
        expression: Mathematical expression as string (e.g., "2 + 3 * 4", "10 / 2")
        
    Returns:
        Dictionary containing result and calculation details
    """
    try:
        # Clean the expression and validate
        expression = expression.replace(' ', '')
        
        # Basic validation - only allow safe characters
        if not re.match(r'^[0-9+\-*/().\s]+$', expression):
            return {
                "success": False,
                "error": "Invalid characters in expression. Only numbers, +, -, *, /, (, ) are allowed.",
                "result": None
            }
        
        # Evaluate the expression
        result = eval(expression)
        
        return {
            "success": True,
            "result": result,
            "expression": expression,
            "type": "basic_calculation"
        }
    except ZeroDivisionError:
        return {
            "success": False,
            "error": "Division by zero",
            "result": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Calculation error: {str(e)}",
            "result": None
        }

@mcp.tool()
def scientific_function(function: str, value: float) -> dict:
    """
    Perform scientific mathematical functions.
    
    Args:
        function: Function name (sin, cos, tan, log, ln, sqrt, exp, abs, floor, ceil)
        value: Input value for the function
        
    Returns:
        Dictionary containing result and function details
    """
    try:
        functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log10,
            'ln': math.log,
            'sqrt': math.sqrt,
            'exp': math.exp,
            'abs': abs,
            'floor': math.floor,
            'ceil': math.ceil,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan
        }
        
        if function not in functions:
            return {
                "success": False,
                "error": f"Unknown function: {function}. Available functions: {list(functions.keys())}",
                "result": None
            }
        
        # Handle special cases
        if function in ['log', 'ln'] and value <= 0:
            return {
                "success": False,
                "error": "Logarithm of non-positive number is undefined",
                "result": None
            }
        
        if function == 'sqrt' and value < 0:
            return {
                "success": False,
                "error": "Square root of negative number is undefined",
                "result": None
            }
        
        result = functions[function](value)
        
        return {
            "success": True,
            "result": result,
            "function": function,
            "input": value,
            "type": "scientific_function"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Function error: {str(e)}",
            "result": None
        }

@mcp.tool()
def unit_conversion(value: float, from_unit: str, to_unit: str) -> dict:
    """
    Convert between different units of measurement.
    
    Args:
        value: The value to convert
        from_unit: Source unit (m, km, cm, mm, ft, in, yd, mi, kg, g, lb, oz, l, ml, gal, qt, pt, c, f, k, c)
        to_unit: Target unit
        
    Returns:
        Dictionary containing converted value and conversion details
    """
    try:
        # Conversion factors
        conversions = {
            # Length
            'm': 1.0,
            'km': 1000.0,
            'cm': 0.01,
            'mm': 0.001,
            'ft': 0.3048,
            'in': 0.0254,
            'yd': 0.9144,
            'mi': 1609.344,
            
            # Weight/Mass
            'kg': 1.0,
            'g': 0.001,
            'lb': 0.45359237,
            'oz': 0.028349523125,
            
            # Volume
            'l': 1.0,
            'ml': 0.001,
            'gal': 3.78541,
            'qt': 0.946353,
            'pt': 0.473176,
            'c': 0.236588,
            
            # Temperature (special handling)
            'c': 'celsius',
            'f': 'fahrenheit',
            'k': 'kelvin'
        }
        
        # Check if units are valid
        if from_unit not in conversions or to_unit not in conversions:
            return {
                "success": False,
                "error": f"Invalid unit. Available units: {list(conversions.keys())}",
                "result": None
            }
        
        # Handle temperature conversions
        if from_unit in ['c', 'f', 'k'] or to_unit in ['c', 'f', 'k']:
            result = convert_temperature(value, from_unit, to_unit)
        else:
            # Standard conversion
            base_value = value * conversions[from_unit]
            result = base_value / conversions[to_unit]
        
        return {
            "success": True,
            "result": result,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "original_value": value,
            "type": "unit_conversion"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Conversion error: {str(e)}",
            "result": None
        }

def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Helper function for temperature conversions."""
    # Convert to Celsius first
    if from_unit == 'f':
        celsius = (value - 32) * 5/9
    elif from_unit == 'k':
        celsius = value - 273.15
    else:  # from_unit == 'c'
        celsius = value
    
    # Convert from Celsius to target unit
    if to_unit == 'f':
        return celsius * 9/5 + 32
    elif to_unit == 'k':
        return celsius + 273.15
    else:  # to_unit == 'c'
        return celsius

@mcp.tool()
def percentage_calculation(value: float, percentage: float, operation: str = "of") -> dict:
    """
    Calculate percentages and percentage changes.
    
    Args:
        value: Base value
        percentage: Percentage value
        operation: Type of calculation ("of", "increase", "decrease", "change")
        
    Returns:
        Dictionary containing result and calculation details
    """
    try:
        if operation == "of":
            result = value * (percentage / 100)
        elif operation == "increase":
            result = value * (1 + percentage / 100)
        elif operation == "decrease":
            result = value * (1 - percentage / 100)
        elif operation == "change":
            result = ((percentage - value) / value) * 100
        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}. Available operations: of, increase, decrease, change",
                "result": None
            }
        
        return {
            "success": True,
            "result": result,
            "base_value": value,
            "percentage": percentage,
            "operation": operation,
            "type": "percentage_calculation"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Percentage calculation error: {str(e)}",
            "result": None
        }

@mcp.tool()
def statistics_calculation(values: List[float], operation: str = "mean") -> dict:
    """
    Perform statistical calculations on a list of numbers.
    
    Args:
        values: List of numerical values
        operation: Statistical operation ("mean", "median", "mode", "sum", "min", "max", "range", "std")
        
    Returns:
        Dictionary containing result and statistical details
    """
    try:
        if not values:
            return {
                "success": False,
                "error": "Empty list provided",
                "result": None
            }
        
        if operation == "mean":
            result = sum(values) / len(values)
        elif operation == "median":
            sorted_values = sorted(values)
            n = len(sorted_values)
            if n % 2 == 0:
                result = (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
            else:
                result = sorted_values[n//2]
        elif operation == "mode":
            from collections import Counter
            counter = Counter(values)
            result = counter.most_common(1)[0][0]
        elif operation == "sum":
            result = sum(values)
        elif operation == "min":
            result = min(values)
        elif operation == "max":
            result = max(values)
        elif operation == "range":
            result = max(values) - min(values)
        elif operation == "std":
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            result = math.sqrt(variance)
        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}. Available operations: mean, median, mode, sum, min, max, range, std",
                "result": None
            }
        
        return {
            "success": True,
            "result": result,
            "operation": operation,
            "count": len(values),
            "values": values,
            "type": "statistics_calculation"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Statistics calculation error: {str(e)}",
            "result": None
        }

if __name__ == "__main__":
    mcp.run() 