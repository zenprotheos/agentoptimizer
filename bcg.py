#!/usr/bin/env python3

"""
Simple BMI Calculator MCP Server
A basic MCP server that provides BMI calculation functionality for testing MCP integration.
"""

from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("bcg")

@mcp.tool()
def calculate_bmi(height_cm: float, weight_kg: float) -> dict:
    """
    Calculate BMI (Body Mass Index) given height and weight.
    
    Args:
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
        
    Returns:
        Dictionary containing BMI value and category
    """
    if height_cm <= 0 or weight_kg <= 0:
        return {
            "error": "Height and weight must be positive numbers",
            "bmi": None,
            "category": None
        }
    
    # Convert height to meters
    height_m = height_cm / 100
    
    # Calculate BMI
    bmi = weight_kg / (height_m ** 2)
    
    # Determine BMI category
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return {
        "bmi": round(bmi, 2),
        "category": category,
        "height_cm": height_cm,
        "weight_kg": weight_kg
    }

@mcp.tool()
def bmi_category_info(category: str) -> dict:
    """
    Get information about a BMI category.
    
    Args:
        category: BMI category name
        
    Returns:
        Dictionary with category information
    """
    categories = {
        "underweight": {
            "range": "Below 18.5",
            "description": "Below normal weight",
            "recommendations": "Consider consulting a healthcare provider about healthy weight gain"
        },
        "normal": {
            "range": "18.5 - 24.9",
            "description": "Normal weight",
            "recommendations": "Maintain current weight through healthy diet and exercise"
        },
        "overweight": {
            "range": "25 - 29.9",
            "description": "Above normal weight",
            "recommendations": "Consider weight loss through diet and exercise"
        },
        "obese": {
            "range": "30 and above",
            "description": "Significantly above normal weight",
            "recommendations": "Consult a healthcare provider for weight management strategies"
        }
    }
    
    category_key = category.lower().replace(" ", "").replace("weight", "")
    if category_key == "normalweight":
        category_key = "normal"
    
    if category_key in categories:
        return {
            "category": category,
            "info": categories[category_key]
        }
    else:
        return {
            "error": f"Unknown BMI category: {category}",
            "available_categories": list(categories.keys())
        }

if __name__ == "__main__":
    mcp.run() 