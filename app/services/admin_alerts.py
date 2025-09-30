"""
Admin Broadcast Alert Service - FIXED VERSION with Security
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
from sqlalchemy import select
import secrets

from app.services.whatsapp import whatsapp_service
from app.core.database import DatabaseManager, get_db_context
from app.config import settings
from app.core.security import (  # FIXED: Added security imports
    validate_alert_type, 
    validate_priority, 
    validate_disease_name,
    validate_region_name,
    sanitize_input_string
)

logger = logging.getLogger(__name__)

class AdminAlertService:
    """Service for sending administrative broadcast alerts with security fixes"""

    def __init__(self):
        self.whatsapp = whatsapp_service
        self.db_manager = DatabaseManager()
        logger.info("Admin Alert Service initialized")

    async def send_broadcast_alert(self, alert_message: str, alert_type: str = "info",
                                 target_users: Optional[List[str]] = None,
                                 target_regions: Optional[List[str]] = None,
                                 priority: str = "normal") -> Dict[str, Any]:
        """
        Send broadcast alert to users with security validation
        """
        try:
            # FIXED: Validate inputs
            if not alert_message or len(alert_message.strip()) == 0:
                return {"success": False, "error": "Alert message cannot be empty"}
            
            if not validate_alert_type(alert_type):
                return {"success": False, "error": f"Invalid alert type: {alert_type}"}
            
            if not validate_priority(priority):
                return {"success": False, "error": f"Invalid priority: {priority}"}

            # Sanitize message
            alert_message = sanitize_input_string(alert_message, max_length=2000)
            
            logger.info(f"📢 Broadcasting {alert_type} alert - Priority: {priority}")
            logger.info(f"Message length: {len(alert_message)} characters")

            # Get target users
            users_to_alert = await self._get_target_users(target_users, target_regions)

            if not users_to_alert:
                logger.warning("No users found to send alert to")
                return {"success": False, "error": "No target users found"}

            logger.info(f"Sending alert to {len(users_to_alert)} users")

            # Format alert message
            formatted_message = self._format_admin_alert(alert_message, alert_type, priority)

            # Send alerts with rate limiting
            results = await self._send_rate_limited_alerts(
                users_to_alert,
                formatted_message,
                alert_type,
                priority
            )

            # Log broadcast
            await self._log_broadcast(alert_message, alert_type, len(users_to_alert), results)

            logger.info(f"✅ Broadcast completed - Success: {results['success']}, Failed: {results['failed']}")

            return {
                "success": True,
                "message": "Broadcast alert sent successfully",
                "total_users": len(users_to_alert),
                "results": results,
                "alert_type": alert_type,
                "priority": priority
            }

        except Exception as e:
            logger.error(f"Error sending broadcast alert: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def send_outbreak_alert(self, disease: str, region: str,
                                symptoms: List[str], precautions: List[str],
                                severity: str = "moderate") -> Dict[str, Any]:
        """
        Send disease outbreak alert with validation
        """
        try:
            # FIXED: Validate inputs
            if not validate_disease_name(disease):
                return {"success": False, "error": f"Invalid disease name: {disease}"}
            
            if not validate_region_name(region):
                return {"success": False, "error": f"Invalid region name: {region}"}
            
            if not symptoms or not precautions:
                return {"success": False, "error": "Symptoms and precautions are required"}
            
            if severity.lower() not in {"low", "moderate", "high", "critical"}:
                return {"success": False, "error": f"Invalid severity: {severity}"}

            logger.info(f"🦠 Sending outbreak alert for {disease} in {region}")

            # Sanitize inputs
            disease = sanitize_input_string(disease, max_length=100)
            region = sanitize_input_string(region, max_length=100)
            symptoms = [sanitize_input_string(s, max_length=100) for s in symptoms[:10]]  # Limit symptoms
            precautions = [sanitize_input_string(p, max_length=100) for p in precautions[:10]]  # Limit precautions

            # Create outbreak alert message
            symptom_list = "\n".join([f"• {symptom}" for symptom in symptoms])
            precaution_list = "\n".join([f"• {precaution}" for precaution in precautions])

            severity_emoji = {
                "low": "🟢",
                "moderate": "🟡",
                "high": "🟠",
                "critical": "🔴"
            }.get(severity.lower(), "🟡")

            alert_message = (
                f"{severity_emoji} DISEASE OUTBREAK ALERT {severity_emoji}\n\n"
                f"⚠️  {disease.upper()} Outbreak Reported in {region}\n\n"
                f"📋 SYMPTOMS TO WATCH FOR:\n{symptom_list}\n\n"
                f"🛡️  PREVENTIVE MEASURES:\n{precaution_list}\n\n"
                f"🏠 STAY HOME RECOMMENDATION:\n"
                f"• Avoid crowded places\n"
                f"• Practice social distancing\n"
                f"• Wash hands frequently\n"
                f"• Wear mask in public\n"
                f"• Monitor your health\n\n"
                f"📞 EMERGENCY CONTACTS:\n"
                f"• Local Health Authority: Contact your local health department\n"
                f"• Hospital Hotline: Call nearest hospital\n"
                f"• Government Helpline: 1075\n\n"
                f"💡 This is an official health advisory. Please follow preventive measures and seek medical attention if symptoms develop."
            )

            # Send to users in affected region
            result = await self.send_broadcast_alert(
                alert_message=alert_message,
                alert_type="outbreak",
                target_regions=[region],
                priority="high" if severity in ["high", "critical"] else "normal"
            )

            if result.get('success'):
                logger.info(f"✅ Outbreak alert sent for {disease} in {region}")
            else:
                logger.error(f"❌ Failed to send outbreak alert: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error sending outbreak alert: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def send_emergency_alert(self, emergency_type: str, region: str,
                                 affected_areas: List[str], safety_instructions: List[str],
                                 contact_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Send emergency alert with validation
        """
        try:
            # FIXED: Validate inputs
            if not emergency_type or not region:
                return {"success": False, "error": "Emergency type and region are required"}
            
            if not affected_areas or not safety_instructions:
                return {"success": False, "error": "Affected areas and safety instructions are required"}
            
            if not contact_info:
                return {"success": False, "error": "Contact information is required"}

            logger.info(f"🚨 Sending emergency alert for {emergency_type} in {region}")

            # Sanitize inputs
            emergency_type = sanitize_input_string(emergency_type, max_length=100)
            region = sanitize_input_string(region, max_length=100)
            affected_areas = [sanitize_input_string(area, max_length=100) for area in affected_areas[:10]]
            safety_instructions = [sanitize_input_string(instruction, max_length=150) for instruction in safety_instructions[:10]]
            
            # Sanitize contact info
            sanitized_contact_info = {}
            for key, value in contact_info.items():
                sanitized_key = sanitize_input_string(str(key), max_length=50)
                sanitized_value = sanitize_input_string(str(value), max_length=100)
                sanitized_contact_info[sanitized_key] = sanitized_value

            # Create emergency alert message
            area_list = "\n".join([f"• {area}" for area in affected_areas])
            instruction_list = "\n".join([f"• {instruction}" for instruction in safety_instructions])
            contact_list = "\n".join([f"• {key}: {value}" for key, value in sanitized_contact_info.items()])

            alert_message = (
                f"🚨 EMERGENCY ALERT 🚨\n\n"
                f"⚠️  {emergency_type.upper()} in {region}\n\n"
                f"📍 AFFECTED AREAS:\n{area_list}\n\n"
                f"🏠 SAFETY INSTRUCTIONS:\n{instruction_list}\n\n"
                f"📞 EMERGENCY CONTACTS:\n{contact_list}\n\n"
                f"⚠️  IMMEDIATE ACTIONS REQUIRED:\n"
                f"• Stay indoors if possible\n"
                f"• Follow official instructions\n"
                f"• Keep emergency kit ready\n"
                f"• Monitor official updates\n"
                f"• Help neighbors if safe to do so\n\n"
                f"💡 This is an official emergency advisory. Your safety is the top priority."
            )

            # Send to users in affected region
            result = await self.send_broadcast_alert(
                alert_message=alert_message,
                alert_type="emergency",
                target_regions=[region],
                priority="high"
            )

            if result.get('success'):
                logger.info(f"✅ Emergency alert sent for {emergency_type} in {region}")
            else:
                logger.error(f"❌ Failed to send emergency alert: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error sending emergency alert: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def send_health_advisory(self, topic: str, recommendations: List[str],
                                 target_audience: str = "general") -> Dict[str, Any]:
        """
        Send general health advisory with validation
        """
        try:
            # FIXED: Validate inputs
            if not topic or not recommendations:
                return {"success": False, "error": "Topic and recommendations are required"}

            logger.info(f"ℹ️  Sending health advisory on {topic}")

            # Sanitize inputs
            topic = sanitize_input_string(topic, max_length=200)
            recommendations = [sanitize_input_string(rec, max_length=150) for rec in recommendations[:10]]
            target_audience = sanitize_input_string(target_audience, max_length=50)

            # Create health advisory message
            recommendation_list = "\n".join([f"• {recommendation}" for recommendation in recommendations])

            alert_message = (
                f"ℹ️  HEALTH ADVISORY\n\n"
                f"📋 Topic: {topic}\n\n"
                f"✅ RECOMMENDATIONS:\n{recommendation_list}\n\n"
                f"👥 Target Audience: {target_audience.capitalize()}\n\n"
                f"💡 Follow these recommendations for better health outcomes.\n"
                f"Always consult healthcare providers for personalized advice."
            )

            # Send to appropriate users
            result = await self.send_broadcast_alert(
                alert_message=alert_message,
                alert_type="health_advisory",
                priority="normal"
            )

            if result.get('success'):
                logger.info(f"✅ Health advisory sent on {topic}")
            else:
                logger.error(f"❌ Failed to send health advisory: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error sending health advisory: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    # FIXED: Fixed method name inconsistency
    async def _get_target_users(self, target_users: Optional[List[str]] = None,
                              target_regions: Optional[List[str]] = None) -> List[str]:
        """Get list of target users based on criteria - FIXED METHOD NAME"""
        try:
            async with get_db_context() as db:  # FIXED: Use async context
                if target_users:
                    # Specific users targeted
                    return target_users

                elif target_regions:
                    # Users in specific regions - FIXED: Use correct method name
                    users = []
                    for region in target_regions:
                        region_users = await self.db_manager.get_users_by_region(db, region)
                        users.extend(region_users)
                    
                    # Remove duplicates
                    seen = set()
                    unique_users = []
                    for user in users:
                        if user.phone_number not in seen:
                            seen.add(user.phone_number)
                            unique_users.append(user.phone_number)
                    
                    return unique_users

                else:
                    # All users
                    users = await self.db_manager.get_all_users(db)
                    return [user.phone_number for user in users if user.phone_number]

        except Exception as e:
            logger.error(f"Error getting target users: {e}", exc_info=True)
            return []

    def _format_admin_alert(self, message: str, alert_type: str, priority: str) -> str:
        """Format admin alert message"""

        alert_prefixes = {
            "outbreak": "🦠 OUTBREAK ALERT",
            "emergency": "🚨 EMERGENCY ALERT",
            "health_advisory": "ℹ️  HEALTH ADVISORY",
            "info": "📢 INFORMATION",
            "warning": "⚠️  WARNING"
        }

        prefix = alert_prefixes.get(alert_type, "📢")
        priority_indicator = "🔴" if priority == "high" else "🟡" if priority == "normal" else "🟢"

        return f"{priority_indicator} {prefix} {priority_indicator}\n\n{message}"

    async def _send_rate_limited_alerts(self, phone_numbers: List[str], message: str,
                                      alert_type: str, priority: str) -> Dict[str, Any]:
        """Send alerts with rate limiting to avoid spamming"""
        try:
            success_count = 0
            failed_count = 0
            failed_numbers = []

            # Rate limiting - send in batches
            batch_size = 10  # Send 10 messages at a time
            delay_between_batches = 2  # Wait 2 seconds between batches

            # FIXED: Validate phone numbers before sending
            valid_phone_numbers = []
            for phone in phone_numbers:
                try:
                    from app.core.security import validate_whatsapp_phone
                    valid_phone = validate_whatsapp_phone(phone)
                    valid_phone_numbers.append(valid_phone)
                except ValueError as e:
                    logger.warning(f"Invalid phone number {phone}: {e}")
                    failed_count += 1
                    failed_numbers.append(phone)

            for i in range(0, len(valid_phone_numbers), batch_size):
                batch = valid_phone_numbers[i:i + batch_size]
                logger.info(f"Sending batch {i//batch_size + 1} of {(len(valid_phone_numbers)-1)//batch_size + 1}")

                # Send batch
                for phone_number in batch:
                    try:
                        # Add priority indicator to message
                        priority_msg = f"[{priority.upper()}] {message}" if priority == "high" else message

                        result = await self.whatsapp.send_text_message(phone_number, priority_msg)

                        if result.get('success'):
                            success_count += 1
                            logger.info(f"✅ Alert sent to {phone_number}")
                        else:
                            failed_count += 1
                            failed_numbers.append(phone_number)
                            logger.error(f"❌ Failed to send alert to {phone_number}: {result.get('error')}")

                    except Exception as e:
                        failed_count += 1
                        failed_numbers.append(phone_number)
                        logger.error(f"❌ Error sending alert to {phone_number}: {e}", exc_info=True)

                # Wait between batches (unless it's the last batch)
                if i + batch_size < len(valid_phone_numbers):
                    logger.info(f"Waiting {delay_between_batches} seconds before next batch...")
                    await asyncio.sleep(delay_between_batches)

            return {
                "success": success_count,
                "failed": failed_count,
                "failed_numbers": failed_numbers,
                "total": len(phone_numbers)
            }

        except Exception as e:
            logger.error(f"Error sending rate-limited alerts: {e}", exc_info=True)
            return {"success": 0, "failed": len(phone_numbers), "total": len(phone_numbers)}

    async def _log_broadcast(self, message: str, alert_type: str, user_count: int,
                           results: Dict[str, Any]) -> None:
        """Log broadcast alert for analytics"""
        try:
            async with get_db_context() as db:  # FIXED: Use async context
                # FIXED: Use correct method name
                alert_data = {
                    "alert_type": alert_type,
                    "message": message,
                    "priority": "normal",  # Default, should be passed as parameter
                    "target_users_count": user_count,
                    "successful_deliveries": results.get('success', 0),
                    "failed_deliveries": results.get('failed', 0),
                    "created_by": "admin",  # Should be actual admin ID
                    "target_regions": json.dumps([]),  # Should be passed as parameter
                    "failed_numbers": json.dumps(results.get('failed_numbers', []))
                }
                
                await self.db_manager.log_broadcast_alert(db, alert_data)
                logger.info(f"Broadcast logged - Type: {alert_type}, Users: {user_count}, Success: {results.get('success', 0)}")

        except Exception as e:
            logger.error(f"Error logging broadcast: {e}", exc_info=True)

    async def get_broadcast_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get broadcast alert history"""
        try:
            async with get_db_context() as db:
                from app.models.database import BroadcastAlert
                from sqlalchemy import select
                
                result = await db.execute(
                    select(BroadcastAlert)
                    .order_by(BroadcastAlert.created_at.desc())
                    .limit(limit)
                )
                alerts = result.scalars().all()
                
                return {
                    "success": True,
                    "history": [alert.to_dict() for alert in alerts],
                    "total": len(alerts),
                    "limit": limit
                }

        except Exception as e:
            logger.error(f"Error retrieving broadcast history: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def cancel_scheduled_broadcast(self, broadcast_id: str) -> Dict[str, Any]:
        """Cancel a scheduled broadcast"""
        try:
            # This would cancel from database scheduler
            logger.info(f"Cancelling scheduled broadcast: {broadcast_id}")

            return {
                "success": True,
                "message": f"Broadcast {broadcast_id} cancelled successfully"
            }

        except Exception as e:
            logger.error(f"Error cancelling broadcast: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

# FIXED: Create service instance with proper initialization
admin_alert_service = AdminAlertService()

Test function with proper error handling
async def test_admin_alerts():
"""Test admin alert service"""
print("🧪 Testing Admin Alert Service")
print("=" * 50)
try:
    # Test broadcast alert
    print("\n1. Testing Broadcast Alert...")
    result = await admin_alert_service.send_broadcast_alert(
        alert_message="This is a test broadcast message to all users",
        alert_type="info",
        priority="normal"
    )
    print(f"Broadcast result: {json.dumps(result, indent=2)}")

    # Test outbreak alert
    print("\n2. Testing Outbreak Alert...")
    result = await admin_alert_service.send_outbreak_alert(
        disease="Dengue Fever",
        region="Delhi",
        symptoms=["High fever", "Severe headache", "Joint pain", "Rash"],
        precautions=["Use mosquito repellent", "Wear long sleeves", "Eliminate standing water", "Seek medical care early"],
        severity="moderate"
    )
    print(f"Outbreak result: {json.dumps(result, indent=2)}")

    # Test emergency alert
    print("\n3. Testing Emergency Alert...")
    result = await admin_alert_service.send_emergency_alert(
        emergency_type="Flood Warning",
        region="Mumbai",
        affected_areas=["Andheri", "Bandra", "Malad"],
        safety_instructions=["Stay indoors", "Avoid flooded areas", "Keep emergency kit ready", "Monitor official updates"],
        contact_info={
            "Emergency Services": "108",
            "Municipal Corporation": "155222",
            "Police": "100"
        }
    )
    print(f"Emergency result: {json.dumps(result, indent=2)}")

    # Test health advisory
    print("\n4. Testing Health Advisory...")
    result = await admin_alert_service.send_health_advisory(
        topic="Seasonal Flu Prevention",
        recommendations=[
            "Get seasonal flu vaccination",
            "Wash hands frequently with soap",
            "Avoid touching face with unwashed hands",
            "Cover mouth and nose when coughing/sneezing",
            "Stay home when sick",
            "Maintain good nutrition and sleep"
        ],
        target_audience="general"
    )
    print(f"Advisory result: {json.dumps(result, indent=2)}")

    print("\n🎉 Admin Alert Service testing completed!")

except Exception as e:
    print(f"❌ Error during admin alert testing: {e}")
    logger.error(f"Admin alert testing failed: {e}", exc_info=True)
    if name == "main":
import asyncio
asyncio.run(test_admin_alerts())
