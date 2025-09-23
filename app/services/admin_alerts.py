"""
Admin Broadcast Alert Service - Send mass alerts for outbreaks and emergencies
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio

from app.services.whatsapp import whatsapp_service
from app.core.database import DatabaseManager, get_db_context
from app.config import settings

logger = logging.getLogger(__name__)

class AdminAlertService:
    """Service for sending administrative broadcast alerts"""
    
    def __init__(self):
        self.whatsapp = whatsapp_service
        self.db_manager = DatabaseManager()
        logger.info("Admin Alert Service initialized")
    
    async def send_broadcast_alert(self, alert_message: str, alert_type: str = "info", 
                                 target_users: Optional[List[str]] = None,
                                 target_regions: Optional[List[str]] = None,
                                 priority: str = "normal") -> Dict[str, Any]:
        """
        Send broadcast alert to users
        
        Args:
            alert_message: The alert message to send
            alert_type: Type of alert (outbreak, emergency, info, warning)
            target_users: Specific users to target (None = all users)
            target_regions: Specific regions to target (None = all regions)
            priority: Priority level (high, normal, low)
            
        Returns:
            Dict with broadcast results
        """
        try:
            logger.info(f"📢 Broadcasting {alert_type} alert - Priority: {priority}")
            logger.info(f"Message: {alert_message}")
            
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
        Send disease outbreak alert
        
        Args:
            disease: Disease name
            region: Affected region
            symptoms: List of symptoms to watch for
            precautions: List of preventive measures
            severity: Severity level (low, moderate, high, critical)
            
        Returns:
            Dict with alert results
        """
        try:
            logger.info(f"🦠 Sending outbreak alert for {disease} in {region}")
            
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
                f"• Local Health Authority: [Contact Info]\n"
                f"• Hospital Hotline: [Phone Number]\n"
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
        Send emergency alert (natural disaster, accident, etc.)
        
        Args:
            emergency_type: Type of emergency
            region: Affected region
            affected_areas: Specific affected areas
            safety_instructions: Safety instructions to follow
            contact_info: Emergency contact information
            
        Returns:
            Dict with alert results
        """
        try:
            logger.info(f"🚨 Sending emergency alert for {emergency_type} in {region}")
            
            # Create emergency alert message
            area_list = "\n".join([f"• {area}" for area in affected_areas])
            instruction_list = "\n".join([f"• {instruction}" for instruction in safety_instructions])
            contact_list = "\n".join([f"• {key}: {value}" for key, value in contact_info.items()])
            
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
        Send general health advisory
        
        Args:
            topic: Advisory topic
            recommendations: Health recommendations
            target_audience: Target audience (general, elderly, children, etc.)
            
        Returns:
            Dict with advisory results
        """
        try:
            logger.info(f"ℹ️  Sending health advisory on {topic}")
            
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
    
    async def _get_target_users(self, target_users: Optional[List[str]] = None,
                              target_regions: Optional[List[str]] = None) -> List[str]:
        """Get list of target users based on criteria"""
        try:
            with get_db_context() as db:
                if target_users:
                    # Specific users targeted
                    return target_users
                
                elif target_regions:
                    # Users in specific regions
                    users = self.db_manager.get_users_by_regions(db, target_regions)
                    return [user.phone_number for user in users]
                
                else:
                    # All users
                    users = self.db_manager.get_all_users(db)
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
            
            for i in range(0, len(phone_numbers), batch_size):
                batch = phone_numbers[i:i + batch_size]
                logger.info(f"Sending batch {i//batch_size + 1} of {len(phone_numbers)//batch_size + 1}")
                
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
                if i + batch_size < len(phone_numbers):
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
            with get_db_context() as db:
                # Log broadcast in database (you'll need to implement this in your models)
                logger.info(f"Broadcast logged - Type: {alert_type}, Users: {user_count}, Success: {results['success']}")
                
        except Exception as e:
            logger.error(f"Error logging broadcast: {e}", exc_info=True)
    
    async def get_broadcast_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get broadcast alert history"""
        try:
            # This would retrieve from database
            logger.info("Retrieving broadcast history...")
            
            return {
                "success": True,
                "history": [],
                "total": 0,
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

# Create service instance
admin_alert_service = AdminAlertService()

# Test function
async def test_admin_alerts():
    """Test admin alert service"""
    print("🧪 Testing Admin Alert Service")
    print("=" * 35)
    
    # Test broadcast alert
    print("\n1. Testing Broadcast Alert...")
    result = await admin_alert_service.send_broadcast_alert(
        alert_message="This is a test broadcast message to all users",
        alert_type="info",
        priority="normal"
    )
    print(f"Broadcast result: {result}")
    
    # Test outbreak alert
    print("\n2. Testing Outbreak Alert...")
    result = await admin_alert_service.send_outbreak_alert(
        disease="Dengue",
        region="Delhi",
        symptoms=["High fever", "Severe headache", "Joint pain", "Rash"],
        precautions=["Use mosquito repellent", "Wear long sleeves", "Eliminate standing water", "Seek medical care early"],
        severity="moderate"
    )
    print(f"Outbreak result: {result}")
    
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
    print(f"Emergency result: {result}")
    
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
    print(f"Advisory result: {result}")
    
    print("\n🎉 Admin Alert Service testing completed!")

if __name__ == "__main__":
    asyncio.run(test_admin_alerts())