import math
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SettlementCalculator:
    """Tool for immediate settlement calculation: settlement = load / Young's modulus"""
    
    @staticmethod
    def calculate(load: float, youngs_modulus: float) -> Dict[str, Any]:
        """
        Calculate immediate settlement
        Args:
            load: Applied load (kN/m² or similar units)
            youngs_modulus: Young's modulus of soil (kN/m² or similar units)
        Returns:
            Dict with settlement value and metadata
        """
        try:
            if youngs_modulus <= 0:
                raise ValueError("Young's modulus must be positive")
            if load < 0:
                raise ValueError("Load cannot be negative")
            
            settlement = load / youngs_modulus
            
            return {
                "settlement": settlement,
                "units": "same as load units / modulus units",
                "formula": "settlement = load / Young's_modulus",
                "inputs": {
                    "load": load,
                    "youngs_modulus": youngs_modulus
                }
            }
        except Exception as e:
            logger.error(f"Settlement calculation error: {str(e)}")
            raise

class TerzaghiBearingCapacity:
    """Tool for Terzaghi bearing capacity analysis (cohesionless soils)"""
    
    # Bearing capacity factors lookup table
    BEARING_CAPACITY_FACTORS = {
        0: {"Nq": 1.0, "Nr": 0.0},
        5: {"Nq": 1.6, "Nr": 0.1},
        10: {"Nq": 2.5, "Nr": 0.4},
        15: {"Nq": 3.9, "Nr": 1.2},
        20: {"Nq": 6.4, "Nr": 2.9},
        25: {"Nq": 10.7, "Nr": 6.8},
        30: {"Nq": 18.4, "Nr": 15.1},
        32: {"Nq": 23.2, "Nr": 20.8},
        34: {"Nq": 29.4, "Nr": 28.8},
        35: {"Nq": 33.3, "Nr": 33.9},
        36: {"Nq": 37.8, "Nr": 40.1},
        38: {"Nq": 48.9, "Nr": 56.3},
        40: {"Nq": 64.2, "Nr": 79.5},
        42: {"Nq": 85.4, "Nr": 113.0},
        45: {"Nq": 134.9, "Nr": 200.8}
    }
    
    @staticmethod
    def _interpolate_factors(friction_angle: float) -> Dict[str, float]:
        """Interpolate bearing capacity factors for given friction angle"""
        angles = sorted(TerzaghiBearingCapacity.BEARING_CAPACITY_FACTORS.keys())
        
        if friction_angle <= angles[0]:
            return TerzaghiBearingCapacity.BEARING_CAPACITY_FACTORS[angles[0]]
        elif friction_angle >= angles[-1]:
            return TerzaghiBearingCapacity.BEARING_CAPACITY_FACTORS[angles[-1]]
        
        # Linear interpolation
        for i in range(len(angles) - 1):
            if angles[i] <= friction_angle <= angles[i + 1]:
                lower = TerzaghiBearingCapacity.BEARING_CAPACITY_FACTORS[angles[i]]
                upper = TerzaghiBearingCapacity.BEARING_CAPACITY_FACTORS[angles[i + 1]]
                
                ratio = (friction_angle - angles[i]) / (angles[i + 1] - angles[i])
                
                return {
                    "Nq": lower["Nq"] + ratio * (upper["Nq"] - lower["Nq"]),
                    "Nr": lower["Nr"] + ratio * (upper["Nr"] - lower["Nr"])
                }
    
    @staticmethod
    def calculate(B: float, gamma: float, Df: float, friction_angle: float) -> Dict[str, Any]:
        """
        Calculate ultimate bearing capacity using Terzaghi's equation
        Args:
            B: Diameter/width of footing (m)
            gamma: Unit weight of soil (kN/m³)
            Df: Depth of footing (m)
            friction_angle: Friction angle in degrees
        Returns:
            Dict with bearing capacity and calculation details
        """
        try:
            if any(x <= 0 for x in [B, gamma, Df]):
                raise ValueError("B, gamma, and Df must be positive")
            if not 0 <= friction_angle <= 45:
                raise ValueError("Friction angle must be between 0 and 45 degrees")
            
            factors = TerzaghiBearingCapacity._interpolate_factors(friction_angle)
            Nq = factors["Nq"]
            Nr = factors["Nr"]
            
            # Terzaghi equation: q_ult = γ*Df*Nq + 0.5*γ*B*Nr
            term1 = gamma * Df * Nq
            term2 = 0.5 * gamma * B * Nr
            q_ult = term1 + term2
            
            return {
                "ultimate_bearing_capacity": q_ult,
                "units": "kN/m² (assuming gamma in kN/m³)",
                "formula": "q_ult = γ*Df*Nq + 0.5*γ*B*Nr",
                "inputs": {
                    "B": B,
                    "gamma": gamma,
                    "Df": Df,
                    "friction_angle": friction_angle
                },
                "factors": {
                    "Nq": round(Nq, 2),
                    "Nr": round(Nr, 2)
                },
                "calculation_breakdown": {
                    "depth_term": round(term1, 2),
                    "width_term": round(term2, 2),
                    "total": round(q_ult, 2)
                }
            }
        except Exception as e:
            logger.error(f"Bearing capacity calculation error: {str(e)}")
            raise