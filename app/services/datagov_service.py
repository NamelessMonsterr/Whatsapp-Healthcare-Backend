"""
Data.gov.in API Service for Healthcare Chatbot - WITH ODISHA SUPPORT
"""
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from app.config import settings

logger = logging.getLogger(__name__)

class DataGovService:
    """Service to interact with Data.gov.in APIs with Odisha support"""
    
    def __init__(self):
        self.api_key = settings.data_gov_api_key
        self.base_url = settings.data_gov_base_url
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Healthcare-Chatbot/1.0"
        }
        # Known working resource IDs
        self.resources = {
            "hospitals": "7d208ae4-5d5d-4ffb-a8a2-946981635255",
            "covid_state": "4cbfff34-7da0-4337-93c7-9e40ff039c19", 
            "covid_district": "1a8e305e-0486-4942-9b3d-9400b71f0a9d",
            "ayushman_hospitals": "8a7e7d5a-b37b-41d6-855f-9c6c6f3e7b3a"
        }
        logger.info("Data.gov.in Service initialized with Odisha support")
    
    def get_vaccination_centers(self, state: Optional[str] = None, 
                              district: Optional[str] = None, 
                              limit: int = 10) -> Dict[str, Any]:
        """
        Get vaccination centers with Odisha support
        
        Args:
            state: State name to filter
            district: District name to filter  
            limit: Number of results (max 1000)
            
        Returns:
            Dict with vaccination center data or error
        """
        try:
            logger.info(f"🏥 Finding vaccination centers - State: {state}, District: {district}")
            
            # ✅ USE MOCK DATA WITH ODISHA SUPPORT
            mock_centers = self._get_mock_vaccination_centers_with_odisha(state, district, limit)
            
            if mock_centers:
                logger.info(f"✅ Found {len(mock_centers)} mock vaccination centers")
                return {
                    "status": "success",
                    "records": mock_centers,
                    "count": len(mock_centers),
                    "source": "mock_data_with_odisha",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.warning("❌ No vaccination centers found")
                return {
                    "status": "error",
                    "error": "No vaccination centers found",
                    "records": [],
                    "count": 0,
                    "source": "none",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Error finding vaccination centers: {e}", exc_info=True)
            return self._get_fallback_vaccination_centers_with_odisha(state, district, limit)
    
    def _get_mock_vaccination_centers_with_odisha(self, state: str = None, district: str = None, 
                                               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get mock vaccination centers for development with Odisha support
        
        Args:
            state: State name
            district: District name
            limit: Number of results
            
        Returns:
            List of mock vaccination centers
        """
        # Mock vaccination centers data for Indian cities INCLUDING ODISHA
        mock_centers_data = {
            "Delhi": [
                {
                    "name": "AIIMS Delhi Vaccination Center",
                    "address": "Sri Aurobindo Marg, Ansari Nagar, South Delhi",
                    "type": "Government Hospital",
                    "phone": "011-26588500",
                    "timing": "9:00 AM - 5:00 PM (Mon-Sat)",
                    "vaccines": ["Covid-19", "Flu", "Hepatitis B", "MMR"],
                    "services": ["Routine Immunization", "Travel Vaccines", "Adult Vaccines"]
                },
                {
                    "name": "Delhi Government Hospital Vaccination Center",
                    "address": "Near Red Fort, Old Delhi",
                    "type": "Government Hospital",
                    "phone": "011-23273000",
                    "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG"],
                    "services": ["Child Immunization", "Adult Vaccines", "Seasonal Vaccines"]
                }
            ],
            "Mumbai": [
                {
                    "name": "Tata Memorial Hospital Vaccination Center",
                    "address": "Dr. E. Borges Road, Parel, Mumbai",
                    "type": "Government Cancer Hospital",
                    "phone": "022-24177000",
                    "timing": "9:00 AM - 5:00 PM (Mon-Fri)",
                    "vaccines": ["Covid-19", "HPV", "Hepatitis B", "Influenza"],
                    "services": ["Cancer Prevention Vaccines", "Routine Immunization", "Adult Vaccines"]
                },
                {
                    "name": "Lilavati Hospital Vaccination Center",
                    "address": "A-791, Bandra Reclamation, Mumbai",
                    "type": "Private Hospital",
                    "phone": "022-45888888",
                    "timing": "9:00 AM - 7:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Flu", "Hepatitis A", "Typhoid"],
                    "services": ["Travel Vaccines", "Corporate Vaccines", "Routine Immunization"]
                }
            ],
            "Bangalore": [
                {
                    "name": "Manipal Hospital Vaccination Center",
                    "address": "98, HAL Airport Road, Bangalore",
                    "type": "Private Hospital",
                    "phone": "080-48605555",
                    "timing": "9:00 AM - 7:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Flu", "Hepatitis B", "MMR"],
                    "services": ["Routine Immunization", "Travel Vaccines", "Adult Vaccines"]
                },
                {
                    "name": "Bangalore Government Hospital Vaccination Center",
                    "address": "Near Cubbon Park, Bangalore",
                    "type": "Government Hospital",
                    "phone": "080-22865555",
                    "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG"],
                    "services": ["Child Immunization", "Adult Vaccines", "Seasonal Vaccines"]
                }
            ],
            "Hyderabad": [
                {
                    "name": "Apollo Hospital Vaccination Center",
                    "address": "6th Floor, Apollo Hospital, Jubilee Hills, Hyderabad",
                    "type": "Private Hospital",
                    "phone": "040-23607777",
                    "timing": "9:00 AM - 7:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Flu", "Hepatitis B", "MMR"],
                    "services": ["Routine Immunization", "Travel Vaccines", "Adult Vaccines"]
                },
                {
                    "name": "Osmania General Hospital Vaccination Center",
                    "address": "Afzal Gunj, Hyderabad",
                    "type": "Government Hospital",
                    "phone": "040-24535000",
                    "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG"],
                    "services": ["Child Immunization", "Adult Vaccines", "Seasonal Vaccines"]
                }
            ],
            "Chennai": [
                {
                    "name": "Apollo Hospital Vaccination Center",
                    "address": "22, Greams Lane, Chennai",
                    "type": "Private Hospital",
                    "phone": "044-28293333",
                    "timing": "9:00 AM - 7:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Flu", "Hepatitis B", "MMR"],
                    "services": ["Routine Immunization", "Travel Vaccines", "Adult Vaccines"]
                },
                {
                    "name": "Government General Hospital Vaccination Center",
                    "address": "Pantheon Road, Chennai",
                    "type": "Government Hospital",
                    "phone": "044-25375000",
                    "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG"],
                    "services": ["Child Immunization", "Adult Vaccines", "Seasonal Vaccines"]
                }
            ],
            # ✅ ODISHA VACCINATION CENTERS ADDED:
            "Odisha": [
                {
                    "name": "SCB Medical College Vaccination Center",
                    "address": "Medical College Road, Cuttack, Odisha",
                    "type": "Government Hospital",
                    "phone": "0671-2321234",
                    "timing": "9:00 AM - 5:00 PM (Mon-Sat)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG", "MMR", "Hepatitis B"],
                    "services": ["Routine Immunization", "Child Vaccines", "Adult Vaccines"]
                },
                {
                    "name": "AIIMS Bhubaneswar Vaccination Center",
                    "address": "Sijua, Patrapada, Bhubaneswar, Odisha",
                    "type": "Government Hospital",
                    "phone": "0674-2475000",
                    "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Flu", "Hepatitis B", "Influenza"],
                    "services": ["Cancer Prevention Vaccines", "Routine Immunization", "Adult Vaccines"]
                },
                {
                    "name": "Kalinga Institute of Medical Sciences Vaccination Center",
                    "address": "KIIT Campus, Bhubaneswar, Odisha",
                    "type": "Private Hospital",
                    "phone": "0674-2475555",
                    "timing": "9:00 AM - 7:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Flu", "Hepatitis A", "Typhoid"],
                    "services": ["Travel Vaccines", "Corporate Vaccines", "Routine Immunization"]
                },
                {
                    "name": "Government Hospital Vaccination Center",
                    "address": "Near Lingaraj Temple, Bhubaneswar, Odisha",
                    "type": "Government Hospital",
                    "phone": "0674-2323456",
                    "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG"],
                    "services": ["Child Immunization", "Adult Vaccines", "Seasonal Vaccines"]
                },
                {
                    "name": "Rourkela General Hospital Vaccination Center",
                    "address": "Sector 20, Rourkela, Odisha",
                    "type": "Government Hospital",
                    "phone": "0661-2421234",
                    "timing": "9:00 AM - 5:00 PM (Mon-Sat)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG", "MMR"],
                    "services": ["Routine Immunization", "Child Vaccines", "Adult Vaccines"]
                }
            ],
            # Individual districts in Odisha
            "Cuttack": [
                {
                    "name": "SCB Medical College Vaccination Center",
                    "address": "Medical College Road, Cuttack, Odisha",
                    "type": "Government Hospital",
                    "phone": "0671-2321234",
                    "timing": "9:00 AM - 5:00 PM (Mon-Sat)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG", "MMR", "Hepatitis B"],
                    "services": ["Routine Immunization", "Child Vaccines", "Adult Vaccines"]
                },
                {
                    "name": "Cuttack District Hospital Vaccination Center",
                    "address": "Near Barabati Stadium, Cuttack, Odisha",
                    "type": "Government Hospital",
                    "phone": "0671-2345678",
                    "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG"],
                    "services": ["Child Immunization", "Adult Vaccines", "Seasonal Vaccines"]
                }
            ],
            "Bhubaneswar": [
                {
                    "name": "AIIMS Bhubaneswar Vaccination Center",
                    "address": "Sijua, Patrapada, Bhubaneswar, Odisha",
                    "type": "Government Hospital",
                    "phone": "0674-2475000",
                    "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Flu", "Hepatitis B", "Influenza"],
                    "services": ["Cancer Prevention Vaccines", "Routine Immunization", "Adult Vaccines"]
                },
                {
                    "name": "Government Hospital Vaccination Center",
                    "address": "Near Lingaraj Temple, Bhubaneswar, Odisha",
                    "type": "Government Hospital",
                    "phone": "0674-2323456",
                    "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG"],
                    "services": ["Child Immunization", "Adult Vaccines", "Seasonal Vaccines"]
                }
            ],
            "Rourkela": [
                {
                    "name": "Rourkela General Hospital Vaccination Center",
                    "address": "Sector 20, Rourkela, Odisha",
                    "type": "Government Hospital",
                    "phone": "0661-2421234",
                    "timing": "9:00 AM - 5:00 PM (Mon-Sat)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG", "MMR"],
                    "services": ["Routine Immunization", "Child Vaccines", "Adult Vaccines"]
                },
                {
                    "name": "Steel Plant Hospital Vaccination Center",
                    "address": "RSP Sector 20, Rourkela, Odisha",
                    "type": "Government Hospital",
                    "phone": "0661-2478901",
                    "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG"],
                    "services": ["Child Immunization", "Adult Vaccines", "Seasonal Vaccines"]
                }
            ],
            "Berhampur": [
                {
                    "name": "M.K.CG Hospital Vaccination Center",
                    "address": "Near Berhampur University, Berhampur, Odisha",
                    "type": "Government Hospital",
                    "phone": "0680-2221234",
                    "timing": "9:00 AM - 5:00 PM (Mon-Sat)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG", "MMR"],
                    "services": ["Routine Immunization", "Child Vaccines", "Adult Vaccines"]
                },
                {
                    "name": "Berhampur Medical College Vaccination Center",
                    "address": "Medical College Road, Berhampur, Odisha",
                    "type": "Government Hospital",
                    "phone": "0680-2345678",
                    "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG"],
                    "services": ["Child Immunization", "Adult Vaccines", "Seasonal Vaccines"]
                }
            ]
        }
        
        # Get centers for specified location
        if state and state in mock_centers_data:
            return mock_centers_data[state][:limit]
        elif district and district in mock_centers_data:
            return mock_centers_data[district][:limit]
        elif "odisha" in str(state).lower() or "orissa" in str(state).lower():
            return mock_centers_data["Odisha"][:limit]
        else:
            # Return centers from major cities
            all_centers = []
            for city_centers in mock_centers_data.values():
                all_centers.extend(city_centers)
            return all_centers[:limit]
    
    def _get_fallback_vaccination_centers_with_odisha(self, state: str = None, district: str = None, 
                                                   limit: int = 10) -> Dict[str, Any]:
        """
        Fallback vaccination centers with Odisha support
        
        Args:
            state: State name
            district: District name
            limit: Number of results
            
        Returns:
            Dict with fallback vaccination center data
        """
        fallback_centers = [
            {
                "name": "Government Hospital Vaccination Center",
                "address": f"{state or district or 'Your State'} Government Hospital",
                "type": "Government Facility",
                "phone": "1075",  # Government helpline
                "timing": "9:00 AM - 5:00 PM (Mon-Sat)",
                "vaccines": ["Covid-19", "Polio", "DPT", "BCG", "MMR", "Hepatitis B"],
                "services": ["Routine Immunization", "Child Vaccines", "Adult Vaccines"]
            },
            {
                "name": "Private Hospital Vaccination Center",
                "address": f"{state or district or 'Your State'} Private Hospital",
                "type": "Private Facility",
                "phone": "1075",  # Government helpline
                "timing": "9:00 AM - 7:00 PM (Mon-Sun)",
                "vaccines": ["Covid-19", "Flu", "Hepatitis A", "Typhoid"],
                "services": ["Travel Vaccines", "Corporate Vaccines", "Routine Immunization"]
            },
            {
                "name": "Community Health Center",
                "address": f"{district or state or 'Your District'} CHC",
                "type": "Government Facility",
                "phone": "1075",  # Government helpline
                "timing": "8:00 AM - 6:00 PM (Mon-Sun)",
                "vaccines": ["Covid-19", "Polio", "DPT", "BCG"],
                "services": ["Child Immunization", "Adult Vaccines", "Seasonal Vaccines"]
            }
        ]
        
        # Add Odisha-specific fallback if relevant
        if state and ("odisha" in state.lower() or "orissa" in state.lower()):
            odisha_fallback = [
                {
                    "name": "Odisha Government Hospital Vaccination Center",
                    "address": f"{district or 'Odisha'} Government Hospital",
                    "type": "Government Facility",
                    "phone": "0674-2345678",  # Odisha health helpline
                    "timing": "9:00 AM - 5:00 PM (Mon-Sat)",
                    "vaccines": ["Covid-19", "Polio", "DPT", "BCG", "MMR"],
                    "services": ["Routine Immunization", "Child Vaccines", "Adult Vaccines"]
                },
                {
                    "name": "Odisha Private Hospital Vaccination Center",
                    "address": f"{district or 'Odisha'} Private Hospital",
                    "type": "Private Facility",
                    "phone": "0674-2475000",  # AIIMS Bhubaneswar
                    "timing": "9:00 AM - 7:00 PM (Mon-Sun)",
                    "vaccines": ["Covid-19", "Flu", "Hepatitis A", "Typhoid"],
                    "services": ["Travel Vaccines", "Corporate Vaccines", "Routine Immunization"]
                }
            ]
            fallback_centers.extend(odisha_fallback)
        
        return {
            "status": "success",
            "records": fallback_centers[:limit],
            "count": min(len(fallback_centers), limit),
            "source": "fallback_with_odisha",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def search_health_facilities(self, query: str, location: str = None) -> Dict[str, Any]:
        """
        Search health facilities based on query with Odisha support
        
        Args:
            query: Search term (location, facility name, etc.)
            location: Specific location to search in
            
        Returns:
            Dict with search results
        """
        results = {
            "query": query,
            "location": location,
            "hospitals": [],
            "vaccination_centers": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Extract location from query if not provided
            if not location:
                location = self._extract_location_from_query(query)
            
            logger.info(f"🔍 Searching health facilities - Query: {query}, Location: {location}")
            
            # Search vaccination centers
            vaccination_data = self.get_vaccination_centers(
                state=location if location else None,
                limit=5
            )
            
            if vaccination_data.get('status') == 'success':
                results["vaccination_centers"] = vaccination_data["records"][:5]
                logger.info(f"✅ Found {len(results['vaccination_centers'])} vaccination centers")
            
            # Search hospitals
            hospital_data = self.get_hospitals_by_location(
                state=location if location else None,
                limit=5
            )
            
            if hospital_data.get('status') == 'success':
                results["hospitals"] = hospital_data["records"][:5]
                logger.info(f"✅ Found {len(results['hospitals'])} hospitals")
            
            logger.info(f"📊 Search completed - Total results: {len(results['vaccination_centers']) + len(results['hospitals'])}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in health facility search: {e}", exc_info=True)
            return {"error": str(e), "query": query, "location": location}
    
    def _extract_location_from_query(self, query: str) -> Optional[str]:
        """Extract location from query with Odisha support"""
        query_lower = query.lower()
        
        # Common Indian locations including Odisha
        locations = {
            "delhi": "Delhi",
            "mumbai": "Mumbai",
            "bangalore": "Bangalore",
            "hyderabad": "Hyderabad",
            "chennai": "Chennai",
            "kolkata": "Kolkata",
            "pune": "Pune",
            "ahmedabad": "Ahmedabad",
            "odisha": "Odisha",  # ✅ Added Odisha
            "orissa": "Odisha",  # ✅ Alternate spelling
            "bhubaneswar": "Bhubaneswar",  # ✅ Added Bhubaneswar
            "cuttack": "Cuttack",  # ✅ Added Cuttack
            "rourkela": "Rourkela",  # ✅ Added Rourkela
            "berhampur": "Berhampur",  # ✅ Added Berhampur
            "sambalpur": "Sambalpur",  # ✅ Added Sambalpur
            "balasore": "Balasore"  # ✅ Added Balasore
        }
        
        for keyword, location in locations.items():
            if keyword in query_lower:
                logger.info(f"📍 Location detected: {location} ({keyword})")
                return location
        
        return None
    
    def get_hospitals_by_location(self, state: Optional[str] = None, 
                                 district: Optional[str] = None, 
                                 limit: int = 10) -> Dict[str, Any]:
        """Get hospitals by location with fallback"""
        try:
            # Use mock data for now
            mock_hospitals = self._get_mock_hospitals(state, district, limit)
            
            return {
                "status": "success",
                "records": mock_hospitals,
                "count": len(mock_hospitals),
                "source": "mock_data",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting hospitals: {e}")
            return {"status": "error", "error": str(e)}
    
    def _get_mock_hospitals(self, state: str = None, district: str = None, 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """Get mock hospitals data"""
        mock_hospitals_data = {
            "Delhi": [
                {"name": "AIIMS Delhi", "address": "Sri Aurobindo Marg, New Delhi", "type": "Government"},
                {"name": "Fortis Hospital", "address": "B-22, Vasant Kunj, New Delhi", "type": "Private"}
            ],
            "Mumbai": [
                {"name": "Tata Memorial Hospital", "address": "Dr. E. Borges Road, Mumbai", "type": "Government"},
                {"name": "Lilavati Hospital", "address": "A-791, Bandra Reclamation, Mumbai", "type": "Private"}
            ],
            "Bangalore": [
                {"name": "Manipal Hospital", "address": "98, HAL Airport Road, Bangalore", "type": "Private"},
                {"name": "Apollo Hospital", "address": "154/11, Opposite Leela Palace, Bangalore", "type": "Private"}
            ],
            "Hyderabad": [
                {"name": "Apollo Hospital", "address": "6th Floor, Apollo Hospital, Jubilee Hills, Hyderabad", "type": "Private"},
                {"name": "Osmania General Hospital", "address": "Afzal Gunj, Hyderabad", "type": "Government"}
            ],
            "Chennai": [
                {"name": "Apollo Hospital", "address": "22, Greams Lane, Chennai", "type": "Private"},
                {"name": "Government General Hospital", "address": "Pantheon Road, Chennai", "type": "Government"}
            ],
            # ✅ ODISHA HOSPITALS ADDED:
            "Odisha": [
                {"name": "AIIMS Bhubaneswar", "address": "Sijua, Patrapada, Bhubaneswar, Odisha", "type": "Government"},
                {"name": "SCB Medical College", "address": "Medical College Road, Cuttack, Odisha", "type": "Government"},
                {"name": "Kalinga Institute of Medical Sciences", "address": "KIIT Campus, Bhubaneswar, Odisha", "type": "Private"},
                {"name": "Rourkela General Hospital", "address": "Sector 20, Rourkela, Odisha", "type": "Government"},
                {"name": "M.K.C.G. Medical College", "address": "Near Berhampur University, Berhampur, Odisha", "type": "Government"}
            ],
            "Bhubaneswar": [
                {"name": "AIIMS Bhubaneswar", "address": "Sijua, Patrapada, Bhubaneswar, Odisha", "type": "Government"},
                {"name": "Kalinga Institute of Medical Sciences", "address": "KIIT Campus, Bhubaneswar, Odisha", "type": "Private"},
                {"name": "Government Hospital", "address": "Near Lingaraj Temple, Bhubaneswar, Odisha", "type": "Government"}
            ],
            "Cuttack": [
                {"name": "SCB Medical College", "address": "Medical College Road, Cuttack, Odisha", "type": "Government"},
                {"name": "Cuttack District Hospital", "address": "Near Barabati Stadium, Cuttack, Odisha", "type": "Government"}
            ],
            "Rourkela": [
                {"name": "Rourkela General Hospital", "address": "Sector 20, Rourkela, Odisha", "type": "Government"},
                {"name": "Steel Plant Hospital", "address": "RSP Sector 20, Rourkela, Odisha", "type": "Government"}
            ],
            "Berhampur": [
                {"name": "M.K.C.G. Medical College", "address": "Near Berhampur University, Berhampur, Odisha", "type": "Government"},
                {"name": "Berhampur Medical College", "address": "Medical College Road, Berhampur, Odisha", "type": "Government"}
            ]
        }
        
        # Get hospitals for specified location
        if state and state in mock_hospitals_data:
            return mock_hospitals_data[state][:limit]
        elif district and district in mock_hospitals_data:
            return mock_hospitals_data[district][:limit]
        elif "odisha" in str(state).lower() or "orissa" in str(state).lower():
            return mock_hospitals_data["Odisha"][:limit]
        else:
            # Return hospitals from major cities
            all_hospitals = []
            for city_hospitals in mock_hospitals_data.values():
                all_hospitals.extend(city_hospitals)
            return all_hospitals[:limit]

# Create service instance
datagov_service = DataGovService()

# Test function
def test_odisha_support():
    """Test Odisha support in Data.gov service"""
    print("🧪 Testing Odisha Support in Data.gov Service")
    print("=" * 45)
    
    service = DataGovService()
    
    # Test Odisha vaccination centers
    print("\n1. Testing Odisha Vaccination Centers...")
    result = service.get_vaccination_centers("Odisha", limit=3)
    print(f"Status: {result['status']}")
    print(f"Records found: {result['count']}")
    if result['records']:
        print(f"First center: {result['records'][0]['name']}")
        print(f"Address: {result['records'][0]['address']}")
    
    # Test Bhubaneswar vaccination centers
    print("\n2. Testing Bhubaneswar Vaccination Centers...")
    result = service.get_vaccination_centers("Bhubaneswar", limit=2)
    print(f"Status: {result['status']}")
    print(f"Records found: {result['count']}")
    if result['records']:
        print(f"First center: {result['records'][0]['name']}")
        print(f"Address: {result['records'][0]['address']}")
    
    # Test Cuttack vaccination centers
    print("\n3. Testing Cuttack Vaccination Centers...")
    result = service.get_vaccination_centers("Cuttack", limit=2)
    print(f"Status: {result['status']}")
    print(f"Records found: {result['count']}")
    if result['records']:
        print(f"First center: {result['records'][0]['name']}")
        print(f"Address: {result['records'][0]['address']}")
    
    # Test location extraction
    print("\n4. Testing Location Extraction...")
    test_queries = [
        "Vaccination centers in Odisha",
        "Hospitals in Bhubaneswar", 
        "Medical facilities in Cuttack",
        "Health services in Rourkela",
        "Clinics in Berhampur"
    ]
    
    for query in test_queries:
        location = service._extract_location_from_query(query)
        print(f"  Query: {query}")
        print(f"  Location: {location}")
        print()
    
    print("\n🎉 Odisha support test completed!")

if __name__ == "__main__":
    test_odisha_support()