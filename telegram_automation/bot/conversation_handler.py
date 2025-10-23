"""
Conversation State Machine for Like4Like Bot
Handles negotiation, agreement, and execution tracking
"""
import asyncio
import logging
import re
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from database.models import (
    DatabaseConnection, Contact, Exchange, ConversationContext,
    ContactStatus, ExchangeStatus, ConversationState,
    calculate_reliability_score
)

logger = logging.getLogger(__name__)


class ConversationHandler:
    """
    Handles conversation flow and state transitions for like4like negotiations
    """
    
    def __init__(self, db: DatabaseConnection, telegram_client):
        self.db = db
        self.client = telegram_client
        
        # Response patterns for different scenarios
        self.positive_patterns = [
            r'\b(?:yes|yeah|yep|sure|ok|okay|sounds good|deal|agreed|let\'s do it|i\'m in)\b',
            r'\b(?:great|awesome|perfect|cool|nice|good)\b',
            r'👍|✅|🤝|💯'
        ]
        
        self.negative_patterns = [
            r'\b(?:no|nope|not interested|pass|decline|reject)\b',
            r'\b(?:sorry|can\'t|won\'t|unable)\b',
            r'👎|❌|🚫'
        ]
        
        self.negotiation_patterns = [
            r'(\d+)\s*(?:like|👍|❤️)',
            r'(\d+)\s*(?:sub|subscribe)',
            r'(\d+)\s*(?:comment|💬)',
            r'(\d+)\s*(?:minute|min|second|watch)'
        ]
    
    async def process_response(self, contact: Contact, conversation_state: ConversationContext, message_text: str):
        """
        Main entry point for processing conversation responses
        """
        try:
            logger.info(f"🔄 Processing response from {contact.username} in state {conversation_state.current_state}")
            
            # Get current exchange
            exchange = await self.db.get_exchange_by_id(conversation_state.exchange_id)
            if not exchange:
                logger.error(f"❌ Exchange {conversation_state.exchange_id} not found")
                return
            
            # Update conversation history
            if not exchange.conversation_history:
                exchange.conversation_history = []
            
            exchange.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'sender': 'them',
                'message': message_text,
                'state': conversation_state.current_state
            })
            
            # Process based on current state
            if conversation_state.current_state == ConversationState.WAITING_RESPONSE.value:
                await self.handle_initial_response(contact, conversation_state, exchange, message_text)
            
            elif conversation_state.current_state == ConversationState.NEGOTIATING_TERMS.value:
                await self.handle_negotiation_response(contact, conversation_state, exchange, message_text)
            
            elif conversation_state.current_state == ConversationState.WAITING_EXECUTION.value:
                await self.handle_execution_update(contact, conversation_state, exchange, message_text)
            
            elif conversation_state.current_state == ConversationState.VERIFYING_COMPLETION.value:
                await self.handle_verification_response(contact, conversation_state, exchange, message_text)
            
            else:
                logger.warning(f"⚠️  Unknown conversation state: {conversation_state.current_state}")
            
            # Save updated exchange
            await self.db.update_exchange(exchange)
            
        except Exception as e:
            logger.error(f"❌ Error processing conversation response: {e}")
    
    async def handle_initial_response(self, contact: Contact, conversation_state: ConversationContext, 
                                    exchange: Exchange, message_text: str):
        """Handle response to our initial DM offer"""
        
        response_type = self.classify_response(message_text)
        
        if response_type == 'positive':
            # They're interested!
            logger.info(f"✅ {contact.username} is interested in the exchange")
            
            # Move to agreed state if terms are clear, otherwise negotiate
            proposed_terms = conversation_state.context.get('proposed_terms', {})
            
            # Check if they mentioned different terms
            mentioned_terms = self.extract_terms_from_message(message_text)
            
            if mentioned_terms and self.terms_need_negotiation(proposed_terms, mentioned_terms):
                # They want different terms, start negotiation
                await self.start_negotiation(contact, conversation_state, exchange, mentioned_terms)
            else:
                # Terms are good, move to agreed
                await self.finalize_agreement(contact, conversation_state, exchange)
        
        elif response_type == 'negotiation':
            # They want to negotiate terms
            logger.info(f"🤝 {contact.username} wants to negotiate terms")
            
            mentioned_terms = self.extract_terms_from_message(message_text)
            await self.start_negotiation(contact, conversation_state, exchange, mentioned_terms)
        
        elif response_type == 'negative':
            # They're not interested
            logger.info(f"❌ {contact.username} declined the exchange")
            
            await self.handle_rejection(contact, conversation_state, exchange)
        
        else:
            # Unclear response, ask for clarification
            logger.info(f"❓ Unclear response from {contact.username}, asking for clarification")
            
            clarification_messages = [
                "Are you interested in doing a like4like exchange? Just let me know yes or no! 😊",
                "Would you like to support each other's music? I can help promote your video if you help with mine!",
                "I'm not sure I understand - are you up for a like4like exchange? 🤔"
            ]
            
            response = random.choice(clarification_messages)
            await self.send_response(contact.user_id, response)
            
            # Add to conversation history
            exchange.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'sender': 'us',
                'message': response,
                'state': conversation_state.current_state
            })
            
            # Extend timeout
            conversation_state.state_expires_at = datetime.now() + timedelta(hours=12)
            await self.db.update_conversation_state(conversation_state)
    
    async def start_negotiation(self, contact: Contact, conversation_state: ConversationContext,
                              exchange: Exchange, their_terms: Dict[str, int]):
        """Start terms negotiation"""
        
        # Update conversation state
        conversation_state.current_state = ConversationState.NEGOTIATING_TERMS.value
        conversation_state.context.update({
            'their_proposed_terms': their_terms,
            'negotiation_round': 1
        })
        conversation_state.state_expires_at = datetime.now() + timedelta(hours=12)
        
        # Evaluate their terms and respond
        our_terms = exchange.terms
        counter_terms = self.calculate_counter_terms(our_terms, their_terms)
        
        # Craft negotiation response
        if self.terms_are_acceptable(their_terms):
            # Accept their terms
            response = f"That works for me! So we'll do:\n"
            response += self.format_terms(their_terms)
            response += f"\n\nI'll go first and do my part on your video, then you can do yours on mine. Sound good? 🤝"
            
            # Update exchange terms
            exchange.terms = their_terms
            
            # Move to agreed state
            conversation_state.current_state = ConversationState.WAITING_EXECUTION.value
            conversation_state.context['agreed_terms'] = their_terms
            conversation_state.context['execution_order'] = 'us_first'
            
        else:
            # Counter with our terms
            response = f"How about this instead:\n"
            response += self.format_terms(counter_terms)
            response += f"\n\nDoes that work for you? 🤗"
            
            conversation_state.context['our_counter_terms'] = counter_terms
        
        await self.send_response(contact.user_id, response)
        
        # Add to conversation history
        exchange.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'sender': 'us',
            'message': response,
            'state': conversation_state.current_state
        })
        
        await self.db.update_conversation_state(conversation_state)
    
    async def handle_negotiation_response(self, contact: Contact, conversation_state: ConversationContext,
                                        exchange: Exchange, message_text: str):
        """Handle response during terms negotiation"""
        
        response_type = self.classify_response(message_text)
        
        if response_type == 'positive':
            # They agreed to our counter terms
            logger.info(f"✅ {contact.username} agreed to negotiated terms")
            
            counter_terms = conversation_state.context.get('our_counter_terms')
            if counter_terms:
                exchange.terms = counter_terms
            
            await self.finalize_agreement(contact, conversation_state, exchange)
        
        elif response_type == 'negotiation':
            # They want to negotiate further
            negotiation_round = conversation_state.context.get('negotiation_round', 1)
            
            if negotiation_round >= 3:
                # Too many rounds, suggest compromise
                response = "We've gone back and forth a few times. How about we meet in the middle? I'll do 5 likes and 1 sub, you do the same? 🤝"
                
                compromise_terms = {'likes': 5, 'subs': 1, 'comments': 0, 'watch_seconds': 60}
                exchange.terms = compromise_terms
                conversation_state.context['final_offer'] = True
                
            else:
                # Try one more negotiation
                mentioned_terms = self.extract_terms_from_message(message_text)
                counter_terms = self.calculate_counter_terms(exchange.terms, mentioned_terms)
                
                response = f"Okay, how about:\n"
                response += self.format_terms(counter_terms)
                response += f"\n\nFinal offer! 😊"
                
                exchange.terms = counter_terms
                conversation_state.context['negotiation_round'] = negotiation_round + 1
                conversation_state.context['final_offer'] = True
            
            await self.send_response(contact.user_id, response)
            
            # Add to conversation history
            exchange.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'sender': 'us',
                'message': response,
                'state': conversation_state.current_state
            })
        
        elif response_type == 'negative':
            # They don't want to negotiate further
            await self.handle_rejection(contact, conversation_state, exchange)
        
        await self.db.update_conversation_state(conversation_state)
    
    async def finalize_agreement(self, contact: Contact, conversation_state: ConversationContext, exchange: Exchange):
        """Finalize agreement and move to execution phase"""
        
        logger.info(f"🤝 Agreement finalized with {contact.username}")
        
        # Update exchange status
        exchange.status = ExchangeStatus.AGREED.value
        exchange.agreed_at = datetime.now()
        
        # Update conversation state
        conversation_state.current_state = ConversationState.WAITING_EXECUTION.value
        conversation_state.context.update({
            'agreed_terms': exchange.terms,
            'execution_order': 'us_first',
            'agreement_time': datetime.now().isoformat()
        })
        conversation_state.state_expires_at = datetime.now() + timedelta(hours=6)  # Shorter timeout for execution
        
        # Send confirmation message
        response = f"Perfect! Here's what we agreed on:\n"
        response += self.format_terms(exchange.terms)
        response += f"\n\nI'll go first and do my part on your video: {exchange.their_video_url}"
        response += f"\n\nOnce I'm done, I'll let you know and you can do your part on mine: {exchange.our_video_url}"
        response += f"\n\nStarting now! 🚀"
        
        await self.send_response(contact.user_id, response)
        
        # Add to conversation history
        exchange.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'sender': 'us',
            'message': response,
            'state': conversation_state.current_state
        })
        
        # Update contact status
        contact.status = ContactStatus.ACTIVE_SAVED.value
        contact.total_exchanges += 1
        await self.db.update_contact(contact)
        
        await self.db.update_conversation_state(conversation_state)
        
        # Trigger our YouTube execution (this would be handled by YouTube executor)
        await self.trigger_our_execution(exchange)
    
    async def trigger_our_execution(self, exchange: Exchange):
        """Trigger our YouTube execution (placeholder for YouTube executor integration)"""
        logger.info(f"🎬 Triggering YouTube execution for exchange {exchange.exchange_uuid}")
        
        # TODO: This will be handled by the YouTube executor
        # For now, simulate execution after a delay
        asyncio.create_task(self.simulate_our_execution(exchange))
    
    async def simulate_our_execution(self, exchange: Exchange):
        """Simulate our execution (temporary until YouTube executor is ready)"""
        # Wait a bit to simulate execution time
        await asyncio.sleep(random.randint(30, 120))
        
        # Mark our execution as completed
        exchange.our_execution_started_at = datetime.now() - timedelta(seconds=60)
        exchange.our_execution_completed_at = datetime.now()
        exchange.our_execution_results = {
            'like': True,
            'subscribe': exchange.terms.get('subs', 0) > 0,
            'comment': exchange.terms.get('comments', 0) > 0,
            'watch': True
        }
        exchange.status = ExchangeStatus.MY_TURN_DONE.value
        
        await self.db.update_exchange(exchange)
        
        # Notify contact that we completed our part
        await self.notify_our_execution_complete(exchange)
    
    async def notify_our_execution_complete(self, exchange: Exchange):
        """Notify contact that we completed our part"""
        contact = await self.db.get_contact_by_id(exchange.contact_id)
        if not contact:
            return
        
        completed_actions = []
        if exchange.our_execution_results.get('like'):
            completed_actions.append(f"{exchange.terms.get('likes', 0)} likes")
        if exchange.our_execution_results.get('subscribe'):
            completed_actions.append(f"{exchange.terms.get('subs', 0)} subs")
        if exchange.our_execution_results.get('comment'):
            completed_actions.append(f"{exchange.terms.get('comments', 0)} comments")
        
        response = f"Done! ✅ I just gave your video {', '.join(completed_actions)}."
        response += f"\n\nYour turn! Please do the same for my video: {exchange.our_video_url}"
        response += f"\n\nJust reply when you're done! 😊"
        
        await self.send_response(contact.user_id, response)
        
        # Update conversation state
        conversation_state = await self.db.get_conversation_state(contact.id)
        if conversation_state:
            conversation_state.current_state = ConversationState.VERIFYING_COMPLETION.value
            conversation_state.context.update({
                'our_execution_completed': True,
                'waiting_for_their_completion': True
            })
            conversation_state.state_expires_at = datetime.now() + timedelta(hours=12)
            
            # Add to conversation history
            if not exchange.conversation_history:
                exchange.conversation_history = []
            
            exchange.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'sender': 'us',
                'message': response,
                'state': conversation_state.current_state
            })
            
            await self.db.update_conversation_state(conversation_state)
            await self.db.update_exchange(exchange)
    
    async def handle_execution_update(self, contact: Contact, conversation_state: ConversationContext,
                                    exchange: Exchange, message_text: str):
        """Handle updates during execution phase"""
        
        # Check if they're saying they completed their part
        completion_indicators = [
            r'\b(?:done|finished|completed|did it|all set)\b',
            r'\b(?:liked|subscribed|commented)\b',
            r'✅|👍|💯'
        ]
        
        indicates_completion = any(re.search(pattern, message_text.lower()) for pattern in completion_indicators)
        
        if indicates_completion:
            logger.info(f"✅ {contact.username} says they completed their part")
            
            # Mark their execution as reported
            exchange.their_execution_verified_at = datetime.now()
            exchange.their_execution_results = {'reported_completed': True}
            exchange.status = ExchangeStatus.COMPLETED.value
            exchange.completed_at = datetime.now()
            
            # Update contact reliability
            contact.successful_exchanges += 1
            contact.reliability_score = calculate_reliability_score(
                contact.successful_exchanges,
                contact.total_exchanges,
                contact.failed_exchanges
            )
            contact.last_exchange_at = datetime.now()
            
            await self.db.update_contact(contact)
            
            # Thank them and mark as completed
            response = f"Awesome, thank you! 🎉 Great working with you!"
            response += f"\n\nFeel free to reach out anytime for more exchanges. I'll also let you know when I have new music! 🎵"
            
            await self.send_response(contact.user_id, response)
            
            # Add to conversation history
            exchange.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'sender': 'us',
                'message': response,
                'state': ConversationState.COMPLETED.value
            })
            
            # End conversation
            conversation_state.current_state = ConversationState.COMPLETED.value
            await self.db.update_conversation_state(conversation_state)
            await self.db.delete_conversation_state(contact.id)  # Clean up
            
            logger.info(f"🎉 Exchange {exchange.exchange_uuid} completed successfully!")
        
        else:
            # They might be asking for clarification or having issues
            response = f"No problem! Just do {self.format_terms(exchange.terms)} on my video: {exchange.our_video_url}"
            response += f"\n\nLet me know when you're done! 😊"
            
            await self.send_response(contact.user_id, response)
            
            # Add to conversation history
            exchange.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'sender': 'us',
                'message': response,
                'state': conversation_state.current_state
            })
    
    async def handle_verification_response(self, contact: Contact, conversation_state: ConversationContext,
                                         exchange: Exchange, message_text: str):
        """Handle response during verification phase"""
        # Similar to handle_execution_update but with different context
        await self.handle_execution_update(contact, conversation_state, exchange, message_text)
    
    async def handle_rejection(self, contact: Contact, conversation_state: ConversationContext, exchange: Exchange):
        """Handle when contact rejects the exchange"""
        
        logger.info(f"❌ {contact.username} rejected the exchange")
        
        # Update exchange status
        exchange.status = ExchangeStatus.FAILED.value
        exchange.completed_at = datetime.now()
        
        # Update contact
        contact.failed_exchanges += 1
        contact.reliability_score = calculate_reliability_score(
            contact.successful_exchanges,
            contact.total_exchanges + 1,
            contact.failed_exchanges
        )
        
        await self.db.update_contact(contact)
        
        # Send polite response
        responses = [
            "No worries! Thanks for letting me know. Feel free to reach out if you change your mind! 😊",
            "All good! Hit me up if you want to do exchanges in the future! 🎵",
            "No problem at all! Good luck with your music! 🚀"
        ]
        
        response = random.choice(responses)
        await self.send_response(contact.user_id, response)
        
        # Add to conversation history
        exchange.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'sender': 'us',
            'message': response,
            'state': ConversationState.FAILED.value
        })
        
        # End conversation
        conversation_state.current_state = ConversationState.FAILED.value
        await self.db.update_conversation_state(conversation_state)
        await self.db.delete_conversation_state(contact.id)
    
    def classify_response(self, message_text: str) -> str:
        """Classify response as positive, negative, negotiation, or unclear"""
        text_lower = message_text.lower()
        
        # Check for positive indicators
        positive_score = sum(1 for pattern in self.positive_patterns if re.search(pattern, text_lower))
        
        # Check for negative indicators
        negative_score = sum(1 for pattern in self.negative_patterns if re.search(pattern, text_lower))
        
        # Check for negotiation indicators (numbers, terms)
        negotiation_score = sum(1 for pattern in self.negotiation_patterns if re.search(pattern, text_lower))
        
        # Check for negotiation keywords
        negotiation_keywords = ['but', 'however', 'instead', 'what about', 'how about', 'prefer', 'better']
        negotiation_score += sum(1 for keyword in negotiation_keywords if keyword in text_lower)
        
        # Classify based on scores
        if positive_score > negative_score and positive_score > 0:
            if negotiation_score > 0:
                return 'negotiation'
            else:
                return 'positive'
        elif negative_score > positive_score and negative_score > 0:
            return 'negative'
        elif negotiation_score > 0:
            return 'negotiation'
        else:
            return 'unclear'
    
    def extract_terms_from_message(self, message_text: str) -> Dict[str, int]:
        """Extract terms (numbers) from message"""
        terms = {}
        text_lower = message_text.lower()
        
        # Extract likes
        likes_match = re.search(r'(\d+)\s*(?:like|👍|❤️)', text_lower)
        if likes_match:
            terms['likes'] = int(likes_match.group(1))
        
        # Extract subs
        subs_match = re.search(r'(\d+)\s*(?:sub|subscribe)', text_lower)
        if subs_match:
            terms['subs'] = int(subs_match.group(1))
        
        # Extract comments
        comments_match = re.search(r'(\d+)\s*(?:comment|💬)', text_lower)
        if comments_match:
            terms['comments'] = int(comments_match.group(1))
        
        # Extract watch time
        watch_match = re.search(r'(\d+)\s*(?:minute|min|second|watch)', text_lower)
        if watch_match:
            watch_time = int(watch_match.group(1))
            # Assume minutes if less than 10, otherwise seconds
            if watch_time < 10:
                watch_time *= 60
            terms['watch_seconds'] = watch_time
        
        return terms
    
    def terms_need_negotiation(self, our_terms: Dict[str, int], their_terms: Dict[str, int]) -> bool:
        """Check if terms need negotiation"""
        for key in ['likes', 'subs', 'comments']:
            our_value = our_terms.get(key, 0)
            their_value = their_terms.get(key, 0)
            
            # If they want significantly more than we offered
            if their_value > our_value * 1.5:
                return True
            
            # If they offer significantly less than we want
            if our_value > 0 and their_value < our_value * 0.5:
                return True
        
        return False
    
    def terms_are_acceptable(self, terms: Dict[str, int]) -> bool:
        """Check if terms are acceptable to us"""
        # Max limits we're willing to accept
        max_limits = {
            'likes': 10,
            'subs': 2,
            'comments': 3,
            'watch_seconds': 300  # 5 minutes
        }
        
        for key, value in terms.items():
            if value > max_limits.get(key, 0):
                return False
        
        return True
    
    def calculate_counter_terms(self, our_terms: Dict[str, int], their_terms: Dict[str, int]) -> Dict[str, int]:
        """Calculate counter offer terms"""
        counter = {}
        
        for key in ['likes', 'subs', 'comments', 'watch_seconds']:
            our_value = our_terms.get(key, 0)
            their_value = their_terms.get(key, 0)
            
            if their_value > our_value:
                # They want more, offer something in between
                counter[key] = min(their_value, our_value + max(1, (their_value - our_value) // 2))
            else:
                # Use our original terms
                counter[key] = our_value
        
        return counter
    
    def format_terms(self, terms: Dict[str, int]) -> str:
        """Format terms for display"""
        parts = []
        
        if terms.get('likes', 0) > 0:
            parts.append(f"• {terms['likes']} likes 👍")
        
        if terms.get('subs', 0) > 0:
            parts.append(f"• {terms['subs']} sub{'s' if terms['subs'] > 1 else ''} 📺")
        
        if terms.get('comments', 0) > 0:
            parts.append(f"• {terms['comments']} comment{'s' if terms['comments'] > 1 else ''} 💬")
        
        if terms.get('watch_seconds', 0) > 0:
            watch_minutes = terms['watch_seconds'] // 60
            if watch_minutes > 0:
                parts.append(f"• Watch {watch_minutes} minute{'s' if watch_minutes > 1 else ''} ⏱️")
            else:
                parts.append(f"• Watch {terms['watch_seconds']} seconds ⏱️")
        
        return '\n'.join(parts) if parts else '• Basic engagement'
    
    async def send_response(self, user_id: int, message: str):
        """Send response message to user"""
        try:
            await self.client.send_message(user_id, message)
        except Exception as e:
            logger.error(f"❌ Failed to send response to {user_id}: {e}")


# Integration with main bot
async def integrate_conversation_handler(bot_instance):
    """Integrate conversation handler with main bot"""
    conversation_handler = ConversationHandler(bot_instance.db, bot_instance.client)
    
    # Replace the placeholder method in the main bot
    async def process_conversation_response(contact, conversation_state, message_text):
        await conversation_handler.process_response(contact, conversation_state, message_text)
    
    # Monkey patch the method
    bot_instance.process_conversation_response = process_conversation_response
    
    return conversation_handler