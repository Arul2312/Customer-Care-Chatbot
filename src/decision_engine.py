import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from config.config import LLMConfig
from src.mermaid_decision_tree import MermaidDecisionTree

class LLMDecisionEngine:
    """
    LLM-powered decision engine that follows the Mermaid decision tree step-by-step
    Uses JSON files for customer data, dynamically asks users about missing information
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=LLMConfig.OPENAI_API_KEY)
        self.model = LLMConfig.MODEL_NAME
        self.confidence_threshold = LLMConfig.CONFIDENCE_THRESHOLD
        
        # Use temperature settings from config
        self.extraction_temperature = LLMConfig.EXTRACTION_TEMPERATURE
        self.navigation_temperature = LLMConfig.NAVIGATION_TEMPERATURE
        self.question_temperature = LLMConfig.QUESTION_TEMPERATURE
        
        self.conversation_history = []
        self.extracted_info = {}
        self.current_state = "Start"
        self.decision_tree = MermaidDecisionTree()
        self.customer_data = {}
        self._last_navigation_result = {}
        
        print(f"LLM Decision Engine initialized")
        print(f"Model: {self.model}")
        print(f"Confidence threshold: {self.confidence_threshold}")
        print(f"Temperature settings - Extraction: {self.extraction_temperature}, Navigation: {self.navigation_temperature}, Questions: {self.question_temperature}")
    
    def load_customer_data(self, customer_file_path):
        """Load customer data from JSON file"""
        try:
            with open(customer_file_path, 'r') as f:
                self.customer_data = json.load(f)
            print(f"Customer data loaded: {self.customer_data.get('customer_id', 'Unknown')}")
            return True
        except FileNotFoundError:
            print(f"Customer data file not found: {customer_file_path}")
            # Use default customer data
            self.customer_data = {
                "customer_id": "UNKNOWN",
                "account_status": "good_standing",
                "loyalty_tier": "Gold",
                "fraud_flag": "No",
                "return_abuse": "No",
                "account_age_months": 12,
                "total_purchases": 50,
                "lifetime_value": 1000.0,
                "previous_returns": 3,
                "last_return_date": "2024-01-01",
                "region": "US",
                "customer_since": "2023-01-01"
            }
            return False
        except Exception as e:
            print(f"Error loading customer data: {str(e)}")
            return False
    
    def update_customer_data_for_test(self, test_case_name):
        """Update customer data based on test case requirements"""
        # Default customer data
        base_data = {
            "customer_id": "CUST_67890",
            "account_status": "good_standing",
            "loyalty_tier": "Gold",
            "fraud_flag": "No",
            "return_abuse": "No",
            "previous_returns": 8
        }
        
        # Modify based on test case
        if "Account Issue" in test_case_name:
            base_data["account_status"] = "not_good_standing"
        elif "Fraud Flag" in test_case_name:
            base_data["fraud_flag"] = "Yes"
        elif "Return Abuse" in test_case_name:
            base_data["return_abuse"] = "Yes"
        elif "Bronze" in test_case_name or "Silver" in test_case_name:
            base_data["loyalty_tier"] = "Bronze" if "Bronze" in test_case_name else "Silver"
        elif "Gold" in test_case_name:
            base_data["loyalty_tier"] = "Gold"
        
        self.customer_data = base_data
    
    def process_refund_request(self, user_request):
        """Process refund request following the Mermaid decision tree"""
        print(f"\n🔍 Processing: '{user_request}'")
        
        # Store the conversation
        self.conversation_history.append({
            'role': 'user',
            'content': user_request,
            'timestamp': datetime.now().isoformat()
        })
        
        # Extract information from user input
        self._extract_information_from_input(user_request)
        
        # Navigate decision tree
        result = self._navigate_decision_tree_with_llm()
        
        # Store the result for question generation
        self._last_navigation_result = result
        
        if result['status'] == 'NEED_INFO':
            # Generate dynamic question based on where we're stuck
            question = self._generate_missing_info_question()
            
            return {
                'status': 'NEED_INFO',
                'question': question,
                'stuck_at': result.get('stuck_at_node', 'unknown'),
                'missing_field': result.get('missing_field', 'unknown'),
                'context': result.get('context', '')
            }
        
        elif result['status'] == 'DECISION':
            return {
                'status': 'DECISION',
                'decision': result['decision'],
                'reason': result['reason'],
                'terminal_node': result.get('terminal_node', ''),
                'decision_path': result.get('decision_path', '')
            }
        
        else:
            return {
                'status': 'ERROR',
                'error': result.get('error', 'Unknown error occurred')
            }
    
    def _extract_information_from_input(self, user_input):
        """Extract information using LLM with comprehensive context"""
        
        # Get valid keywords from the Mermaid chart
        valid_keywords = self.decision_tree.get_valid_keywords()
        
        # Build comprehensive extraction prompt
        extraction_prompt = f"""
You are an expert information extractor for a refund decision system.

USER INPUT: "{user_input}"

CONVERSATION CONTEXT:
- Current extracted information: {json.dumps(self.extracted_info, indent=2)}
- Last question asked about: {self._last_navigation_result.get('missing_field', 'None')}
- Previous conversation: {json.dumps([msg['content'] for msg in self.conversation_history[-3:]], indent=2)}

YOUR TASK:
Extract relevant information from the user input and map it to the correct fields and values.

VALID FIELDS AND VALUES:
{json.dumps(valid_keywords, indent=2)}

EXTRACTION RULES:
1. Only use the exact field names and values from the valid keywords above
2. If the user is responding to a specific question, prioritize extracting that field
3. Use context clues to understand what the user means
4. Map natural language to the appropriate technical values
5. If user says "Yes" or "No", map it based on the context of what was asked

EXAMPLES OF CONTEXT-AWARE EXTRACTION:
- If asked about "return_window" and user says "Yes" or "within" → {{"return_window": "within"}}
- If asked about "return_window" and user says "No" or "expired" → {{"return_window": "expired"}}
- If asked about "late_return_eligible" and user says "Yes" → {{"late_return_eligible": "Yes"}}
- If asked about "delivered" and user says "No" or "not delivered" → {{"delivered": "No"}}
- If asked about "shipping_issue" and user says "Neither" or "not lost or delayed" → {{"shipping_issue": "Neither"}}
- If asked about "seller_type" and user says "third party" → {{"seller_type": "Third-party"}}
- If asked about "payment_method" and user says "credit card" → {{"payment_method": "CreditCard"}}
- "broken laptop" → {{"item_category": "Physical", "item_condition": "damaged"}}
- "it's not returnable" → {{"item_returnable": "No"}}
- "third party seller" → {{"seller_type": "Third-party"}}
- "used my credit card" → {{"payment_method": "CreditCard"}}
- "bought with gift card" → {{"payment_method": "GiftCard"}}
- "BNPL payment" → {{"payment_method": "BNPL"}}

IMPORTANT CONTEXT MAPPINGS:
- "Yes" to return window question means "within"
- "No" to return window question means "expired"
- "Yes" to eligibility questions means "Yes"
- "No" to eligibility questions means "No"
- "Neither" to shipping issue means "Neither"
- "Not delayed or lost" means "Neither"
- "broken", "damaged", "cracked" → "damaged"
- "doesn't work", "defective", "faulty" → "defective"
- "normal", "fine", "working" → "normal"
- "laptop", "phone", "book" → "Physical"
- "software", "app", "download" → "Digital"
- "food", "fresh produce" → "Perishable"
- "third party", "marketplace" → "Third-party"
- "in-house", "direct", "company" → "In-house"
- "credit card", "visa", "mastercard" → "CreditCard"
- "gift card", "store credit" → "GiftCard"
- "buy now pay later", "klarna", "afterpay" → "BNPL"
- "prepaid", "debit" → "Prepaid"

Return ONLY a JSON object with the extracted fields. If nothing can be extracted, return {{}}.

JSON OUTPUT:
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": extraction_prompt}],
                temperature=self.extraction_temperature,
                max_tokens=300
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up the response - remove markdown formatting
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Parse and validate against Mermaid chart keywords
            try:
                new_info = json.loads(response_text)
                for key, value in new_info.items():
                    # Handle array values (fix the LLM returning arrays)
                    if isinstance(value, list) and len(value) > 0:
                        value = value[0]  # Take first element if array
                    
                    if key in valid_keywords and value in valid_keywords[key]:
                        # Update the extracted info (allow overwriting)
                        self.extracted_info[key] = value
                        print(f"✅ Extracted: {key} = {value}")
                        
            except json.JSONDecodeError:
                print(f"🔄 Using fallback extraction")
                self._fallback_extraction(user_input)
                
        except Exception as e:
            print(f"🔄 Using fallback extraction")
            self._fallback_extraction(user_input)
    
    def _fallback_extraction(self, user_input):
        """Fallback extraction using simple pattern matching"""
        
        user_lower = user_input.lower().strip()
        
        # Get the field we're expecting based on last question
        expected_field = self._last_navigation_result.get('missing_field')
        
        if expected_field:
            # Simple Yes/No mapping
            if expected_field in ['item_returnable', 'late_return_eligible', 'delivered', 'in_house_policy', 'third_party_policy', 'bnpl_policy', 'gift_card_policy']:
                if any(word in user_lower for word in ['yes', 'yeah', 'yep', 'sure', 'correct', 'right', 'true', 'eligible']):
                    self.extracted_info[expected_field] = "Yes"
                    print(f"✅ Extracted: {expected_field} = Yes")
                elif any(word in user_lower for word in ['no', 'nah', 'nope', 'not', 'false', 'wrong', 'ineligible']):
                    self.extracted_info[expected_field] = "No"
                    print(f"✅ Extracted: {expected_field} = No")
            
            # Return window mapping
            elif expected_field == 'return_window':
                if any(word in user_lower for word in ['yes', 'within', 'inside', 'valid', 'before']):
                    self.extracted_info[expected_field] = "within"
                    print(f"✅ Extracted: {expected_field} = within")
                elif any(word in user_lower for word in ['no', 'expired', 'past', 'late', 'outside', 'beyond']):
                    self.extracted_info[expected_field] = "expired"
                    print(f"✅ Extracted: {expected_field} = expired")
            
            # Shipping issue mapping
            elif expected_field == 'shipping_issue':
                if 'lost' in user_lower:
                    self.extracted_info[expected_field] = "Lost"
                    print(f"✅ Extracted: {expected_field} = Lost")
                elif 'delayed' in user_lower:
                    self.extracted_info[expected_field] = "Delayed"
                    print(f"✅ Extracted: {expected_field} = Delayed")
                elif any(word in user_lower for word in ['neither', 'not lost', 'not delayed', 'none']):
                    self.extracted_info[expected_field] = "Neither"
                    print(f"✅ Extracted: {expected_field} = Neither")
            
            # Seller type mapping
            elif expected_field == 'seller_type':
                if any(word in user_lower for word in ['third party', 'marketplace', 'external', 'third-party']):
                    self.extracted_info[expected_field] = "Third-party"
                    print(f"✅ Extracted: {expected_field} = Third-party")
                elif any(word in user_lower for word in ['in-house', 'direct', 'company', 'our company']):
                    self.extracted_info[expected_field] = "In-house"
                    print(f"✅ Extracted: {expected_field} = In-house")
            
            # Payment method mapping
            elif expected_field == 'payment_method':
                if any(word in user_lower for word in ['credit card', 'visa', 'mastercard', 'amex']):
                    self.extracted_info[expected_field] = "CreditCard"
                    print(f"✅ Extracted: {expected_field} = CreditCard")
                elif any(word in user_lower for word in ['gift card', 'store credit', 'voucher']):
                    self.extracted_info[expected_field] = "GiftCard"
                    print(f"✅ Extracted: {expected_field} = GiftCard")
                elif any(word in user_lower for word in ['bnpl', 'klarna', 'afterpay', 'buy now pay later']):
                    self.extracted_info[expected_field] = "BNPL"
                    print(f"✅ Extracted: {expected_field} = BNPL")
                elif any(word in user_lower for word in ['prepaid', 'debit', 'debit card']):
                    self.extracted_info[expected_field] = "Prepaid"
                    print(f"✅ Extracted: {expected_field} = Prepaid")
    
    def _validate_keyword(self, field, value):
        """Validate extracted keywords against Mermaid chart"""
        valid_keywords = self.decision_tree.get_valid_keywords()
        
        if field in valid_keywords:
            return value in valid_keywords[field]
        else:
            return False
    
    def _navigate_decision_tree_with_llm(self):
        """Navigate using LLM with comprehensive decision tree understanding"""
        
        flowchart = self.decision_tree.get_refund_decision_flowchart()
        
        # Create comprehensive navigation prompt
        navigation_prompt = f"""
    You are a decision tree navigator for a refund processing system. You MUST follow the flowchart step-by-step without skipping any nodes.

    DECISION TREE FLOWCHART:
    {flowchart}

    CUSTOMER DATA:
    {json.dumps(self.customer_data, indent=2)}

    CURRENT EXTRACTED INFORMATION:
    {json.dumps(self.extracted_info, indent=2)}

    CRITICAL NAVIGATION RULES:
    1. NEVER skip any nodes in the flowchart
    2. NEVER make assumptions about missing data
    3. ALWAYS follow the exact conditional paths
    4. Check for IMMEDIATE TERMINAL CONDITIONS first
    5. Follow the branching logic exactly as shown in the flowchart

    IMMEDIATE TERMINAL CONDITIONS (Check these FIRST):
    - If account_status != "good_standing" → DECISION: RefundDenied1
    - If fraud_flag = "Yes" → DECISION: RefundDenied2
    - If return_abuse = "Yes" → DECISION: ManualReview
    - If item_category = "Perishable" → DECISION: RefundDenied3
    - If item_category = "Digital" → DECISION: RefundDenied4
    - If item_returnable = "No" → DECISION: RefundDenied5

    STEP-BY-STEP NAVIGATION WITH CONDITIONAL LOGIC:

    STEP 1: Check account_status
    - Current: {self.customer_data.get('account_status', 'MISSING')}
    - If NOT "good_standing" → DECISION: RefundDenied1
    - If "good_standing" → Continue to STEP 2

    STEP 2: Check loyalty_tier  
    - Current: {self.customer_data.get('loyalty_tier', 'MISSING')}
    - If "Bronze" or "Silver" → Continue to STEP 4
    - If "Gold" → Continue to STEP 3

    STEP 3: Check fraud_flag (ONLY for Gold customers)
    - Current: {self.customer_data.get('fraud_flag', 'MISSING')}
    - If "Yes" → DECISION: RefundDenied2
    - If "No" → Continue to STEP 4

    STEP 4: Check return_abuse
    - Current: {self.customer_data.get('return_abuse', 'MISSING')}
    - If "Yes" → DECISION: ManualReview
    - If "No" → Continue to STEP 5

    STEP 5: Check item_category ⚠️ CRITICAL TERMINAL CHECK
    - Current: {self.extracted_info.get('item_category', 'MISSING')}
    - If "Perishable" → DECISION: RefundDenied3 (IMMEDIATE TERMINAL)
    - If "Digital" → DECISION: RefundDenied4 (IMMEDIATE TERMINAL)
    - If "Physical" → Continue to STEP 6
    - If MISSING → NEED_INFO: item_category

    STEP 6: Check item_returnable ⚠️ CRITICAL TERMINAL CHECK
    - Current: {self.extracted_info.get('item_returnable', 'MISSING')}
    - If "No" → DECISION: RefundDenied5 (IMMEDIATE TERMINAL)
    - If "Yes" → Continue to STEP 7
    - If MISSING → NEED_INFO: item_returnable

    STEP 7: Check item_condition
    - Current: {self.extracted_info.get('item_condition', 'MISSING')}
    - If "damaged" OR "defective" → SKIP to STEP 11 (go directly to Delivered)
    - If "normal" → Continue to STEP 8
    - If MISSING → NEED_INFO: item_condition

    STEP 8: Check return_window (ONLY for normal condition items)
    - Current: {self.extracted_info.get('return_window', 'MISSING')}
    - If "expired" → Continue to STEP 9
    - If "within" → SKIP to STEP 11 (go directly to Delivered)
    - If MISSING → NEED_INFO: return_window

    STEP 9: Check late_return_eligible (ONLY if return_window = "expired")
    - Current: {self.extracted_info.get('late_return_eligible', 'MISSING')}
    - If "No" → DECISION: RefundDenied6
    - If "Yes" → DECISION: PartialRefund
    - If MISSING → NEED_INFO: late_return_eligible

    STEP 10: This step is skipped - handled by STEP 9

    STEP 11: Check delivered
    - Current: {self.extracted_info.get('delivered', 'MISSING')}
    - If "No" → Continue to STEP 12
    - If "Yes" → Continue to STEP 13
    - If MISSING → NEED_INFO: delivered

    STEP 12: Check shipping_issue (ONLY if delivered = "No")
    - Current: {self.extracted_info.get('shipping_issue', 'MISSING')}
    - If "Lost" → DECISION: RefundApprovedLost
    - If "Delayed" → DECISION: ManualReview2
    - If "Neither" → DECISION: RefundDenied7
    - If MISSING → NEED_INFO: shipping_issue

    STEP 13: Check seller_type (ONLY if delivered = "Yes")
    - Current: {self.extracted_info.get('seller_type', 'MISSING')}
    - If "In-house" → Continue to STEP 14
    - If "Third-party" → Continue to STEP 15
    - If MISSING → NEED_INFO: seller_type

    STEP 14: Check in_house_policy (ONLY if seller_type = "In-house")
    - Current: {self.extracted_info.get('in_house_policy', 'MISSING')}
    - If "No" → DECISION: RefundDenied8
    - If "Yes" → Continue to STEP 16
    - If MISSING → NEED_INFO: in_house_policy

    STEP 15: Check third_party_policy (ONLY if seller_type = "Third-party")
    - Current: {self.extracted_info.get('third_party_policy', 'MISSING')}
    - If "No" → DECISION: RefundDenied9
    - If "Yes" → Continue to STEP 16
    - If MISSING → NEED_INFO: third_party_policy

    STEP 16: Check payment_method
    - Current: {self.extracted_info.get('payment_method', 'MISSING')}
    - If "BNPL" → Continue to STEP 17
    - If "GiftCard" → Continue to STEP 18
    - If "CreditCard" OR "Prepaid" → DECISION: RefundApproved
    - If MISSING → NEED_INFO: payment_method

    STEP 17: Check bnpl_policy (ONLY if payment_method = "BNPL")
    - Current: {self.extracted_info.get('bnpl_policy', 'MISSING')}
    - If "No" → DECISION: RefundDenied10
    - If "Yes" → DECISION: RefundApproved
    - If MISSING → NEED_INFO: bnpl_policy

    STEP 18: Check gift_card_policy (ONLY if payment_method = "GiftCard")
    - Current: {self.extracted_info.get('gift_card_policy', 'MISSING')}
    - If "No" → DECISION: RefundDenied11
    - If "Yes" → DECISION: RefundApproved
    - If MISSING → NEED_INFO: gift_card_policy

    CURRENT SITUATION ANALYSIS:
    Based on the current data, here's where we are:

    1. account_status = "{self.customer_data.get('account_status', 'MISSING')}" ✅
    2. loyalty_tier = "{self.customer_data.get('loyalty_tier', 'MISSING')}" ✅
    3. fraud_flag = "{self.customer_data.get('fraud_flag', 'MISSING')}" ✅
    4. return_abuse = "{self.customer_data.get('return_abuse', 'MISSING')}" ✅
    5. item_category = "{self.extracted_info.get('item_category', 'MISSING')}"
    6. item_returnable = "{self.extracted_info.get('item_returnable', 'MISSING')}"
    7. item_condition = "{self.extracted_info.get('item_condition', 'MISSING')}"

    ⚠️ CRITICAL TERMINAL CONDITION CHECKS:
    - If item_category = "Digital" → IMMEDIATE DECISION: RefundDenied4
    - If item_category = "Perishable" → IMMEDIATE DECISION: RefundDenied3
    - If item_returnable = "No" → IMMEDIATE DECISION: RefundDenied5

    CRITICAL LOGIC CHECK:
    - item_condition = "{self.extracted_info.get('item_condition', 'MISSING')}"
    - If item_condition is "damaged" or "defective" → SKIP return_window check, go directly to delivered
    - If item_condition is "normal" → Check return_window
    - return_window = "{self.extracted_info.get('return_window', 'MISSING')}"
    - If return_window is "within" → SKIP late_return_eligible, go directly to delivered
    - If return_window is "expired" → Check late_return_eligible

    IMPORTANT: 
    - DO NOT ask for item_returnable if item_category = "Digital" (immediate RefundDenied4)
    - DO NOT ask for item_returnable if item_category = "Perishable" (immediate RefundDenied3)
    - DO NOT ask for late_return_eligible if return_window = "within"
    - DO NOT ask for return_window if item_condition = "damaged" or "defective"
    - DO NOT ask for shipping_issue if delivered = "Yes"
    - DO NOT ask for seller policies if the other seller type is chosen

    YOUR TASK:
    1. First check for IMMEDIATE TERMINAL CONDITIONS
    2. If no immediate terminal conditions, find the next step in the sequence that needs information
    3. Start from STEP 1 and work through each step following the conditional logic

    RESPONSE FORMAT:
    If you need more information:
    {{
    "status": "NEED_INFO",
    "stuck_at_node": "NodeName",
    "missing_field": "field_name",
    "context": "Clear explanation of why this information is needed and current step number"
    }}

    If you can make a final decision:
    {{
    "status": "DECISION",
    "decision": "ExactDecisionName",
    "reason": "Clear explanation based on the exact path taken",
    "terminal_node": "ExactTerminalNodeName",
    "decision_path": "Complete path with step numbers"
    }}

    NAVIGATE NOW:
    """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": navigation_prompt}],
                temperature=self.navigation_temperature,
                max_tokens=800
            )
            
            response_text = response.choices[0].message.content.strip()
            
            return self._parse_navigation_response(response_text)
                
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': f'Navigation error: {str(e)}'
            }
    
    def _parse_navigation_response(self, response_text):
        """Parse the LLM navigation response with enhanced JSON extraction"""
        try:
            # Remove any markdown formatting
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Try to find JSON content using multiple approaches
            import re
            
            # Approach 1: Look for JSON blocks more aggressively
            json_patterns = [
                r'\{[^{}]*?"status"[^{}]*?"NEED_INFO"[^{}]*?\}',  # NEED_INFO pattern
                r'\{[^{}]*?"status"[^{}]*?"DECISION"[^{}]*?\}',   # DECISION pattern
                r'\{[^{}]*?"status"[^{}]*?\}',                    # Any status pattern
                r'\{(?:[^{}]|{[^{}]*})*\}',                       # Nested JSON
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    try:
                        # Clean the match
                        clean_match = match.strip()
                        result = json.loads(clean_match)
                        if 'status' in result and result['status'] in ['NEED_INFO', 'DECISION']:
                            return result
                    except json.JSONDecodeError:
                        continue
            
            # Approach 2: Look for JSON content line by line
            lines = response_text.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('{') and '"status"' in line:
                    # Try to get the complete JSON from this line and potentially next lines
                    json_content = line.strip()
                    j = i + 1
                    while j < len(lines) and not json_content.endswith('}'):
                        json_content += lines[j].strip()
                        j += 1
                    
                    try:
                        result = json.loads(json_content)
                        if 'status' in result:
                            return result
                    except json.JSONDecodeError:
                        continue
            
            # Approach 3: Manual extraction based on keywords
            print(f"🔄 Using manual extraction")
            
            # Look for specific field mentions
            field_patterns = {
                'item_returnable': r'item_returnable|returnable',
                'item_condition': r'item_condition|condition',
                'delivered': r'delivered',
                'seller_type': r'seller_type|seller',
                'payment_method': r'payment_method|payment',
                'shipping_issue': r'shipping_issue|shipping',
                'return_window': r'return_window|window',
                'late_return_eligible': r'late_return_eligible|late',
                'in_house_policy': r'in_house_policy|in-house',
                'third_party_policy': r'third_party_policy|third-party',
                'bnpl_policy': r'bnpl_policy|bnpl',
                'gift_card_policy': r'gift_card_policy|gift'
            }
            
            for field, pattern in field_patterns.items():
                if re.search(pattern, response_text, re.IGNORECASE):
                    return {
                        'status': 'NEED_INFO',
                        'stuck_at_node': 'ItemEligible',
                        'missing_field': field,
                        'context': f'Manual extraction found reference to {field}'
                    }
            
            # Final fallback
            return {
                'status': 'ERROR',
                'error': f'Could not parse navigation response'
            }
                
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': f'Parsing error: {str(e)}'
            }
    
    def _generate_missing_info_question(self):
        """Generate questions using LLM based on missing information"""
        
        # Get the last navigation result
        last_navigation = self._last_navigation_result
        missing_field = last_navigation.get('missing_field', 'unknown')
        context = last_navigation.get('context', '')
        stuck_at_node = last_navigation.get('stuck_at_node', 'unknown')
        
        # Get valid values for the missing field
        valid_keywords = self.decision_tree.get_valid_keywords()
        valid_values = valid_keywords.get(missing_field, [])
        
        # Create a focused question generation prompt
        question_prompt = f"""You are a customer service assistant helping with refund requests.

    CRITICAL INFORMATION:
    - The customer said: "{self.conversation_history[-1]['content'] if self.conversation_history else 'N/A'}"
    - We extracted so far: {json.dumps(self.extracted_info, indent=2)}
    - We are stuck because we need: {missing_field}
    - The decision tree requires this specific field to continue processing

    FIELD NEEDED: {missing_field}
    VALID VALUES: {valid_values}

    CONTEXT: {context}

    YOUR TASK:
    Generate a clear, friendly question to ask the customer for the missing field: {missing_field}

    EXAMPLES FOR REFERENCE:
    - For "item_returnable": "Is this item marked as returnable on the product page or receipt? Please specify: Yes or No."
    - For "return_window": "Is your return request within the time window specified in our policy? Please specify: within or expired."
    - For "late_return_eligible": "Are you eligible for a partial refund due to
    - For "item_condition": "What is the condition of the item? Please specify: damaged, defective, or normal."
    - For "delivered": "Has the item been delivered to you? Please specify: Yes or No."
    - For "seller_type": "Who was the seller for this item? Please specify: In-house or Third-party."
    - For "payment_method": "What payment method did you use? Please specify: CreditCard, GiftCard, BNPL, or Prepaid."
    - For "shipping_issue": "What is the shipping status? Please specify: Lost, Delayed, or Neither."
    - For "return_window": "Is your return request within the time window? Please specify: within or expired."
    - For "in_house_policy": "Does this return meet our in-house policy requirements? Please specify: Yes or No."
    - For "third_party_policy": "Does the third-party seller's policy allow this refund? Please specify: Yes or No."
    - For "bnpl_policy": "Does your Buy Now Pay Later provider allow refunds? Please specify: Yes or No."
    - For "gift_card_policy": "Do the gift card terms allow refunds? Please specify: Yes or No."

    REQUIREMENTS:
    1. Be conversational and friendly
    2. Ask specifically for the field: {missing_field}
    3. Provide the exact valid options: {valid_values}
    4. Be clear about what information is needed
    5. Use natural language that a customer would understand

    GENERATE A QUESTION FOR: {missing_field}

    Return only the question, no additional text or formatting:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a customer service assistant. Generate clear, specific questions for refund processing. Return only the question text."},
                    {"role": "user", "content": question_prompt}
                ],
                temperature=self.question_temperature,
                max_tokens=150
            )
            
            question = response.choices[0].message.content.strip()
            
            # Clean up the question
            if question.startswith('"') and question.endswith('"'):
                question = question[1:-1]
            
            # Validate that the question is about the right field
            if missing_field.lower() not in question.lower():
                # Use fallback with specific field
                fallback_questions = {
                    'item_returnable': "Is this item marked as returnable? Please specify: Yes or No.",
                    'item_condition': "What is the condition of the item? Please specify: damaged, defective, or normal.",
                    'delivered': "Has the item been delivered to you? Please specify: Yes or No.",
                    'seller_type': "Who was the seller for this item? Please specify: In-house or Third-party.",
                    'payment_method': "What payment method did you use? Please specify: CreditCard, GiftCard, BNPL, or Prepaid.",
                    'shipping_issue': "What is the shipping status? Please specify: Lost, Delayed, or Neither.",
                    'return_window': "Is your return request within the time window? Please specify: within or expired.",
                    'late_return_eligible': "Are you eligible for a partial refund due to late return? Please specify: Yes or No.",
                    'in_house_policy': "Does this return meet our in-house policy requirements? Please specify: Yes or No.",
                    'third_party_policy': "Does the third-party seller's policy allow this refund? Please specify: Yes or No.",
                    'bnpl_policy': "Does your Buy Now Pay Later provider allow refunds? Please specify: Yes or No.",
                    'gift_card_policy': "Do the gift card terms allow refunds? Please specify: Yes or No."
                }
                
                if missing_field in fallback_questions:
                    question = fallback_questions[missing_field]
                    print(f"🔄 Using fallback question")
            
            return question
            
        except Exception as e:
            print(f"🔄 Using fallback question")
            
            # Fallback to simple questions
            fallback_questions = {
                'item_returnable': "Is this item marked as returnable? Please specify: Yes or No.",
                'item_condition': "What is the condition of the item? Please specify: damaged, defective, or normal.",
                'delivered': "Has the item been delivered to you? Please specify: Yes or No.",
                'seller_type': "Who was the seller for this item? Please specify: In-house or Third-party.",
                'payment_method': "What payment method did you use? Please specify: CreditCard, GiftCard, BNPL, or Prepaid.",
                'shipping_issue': "What is the shipping status? Please specify: Lost, Delayed, or Neither.",
                'return_window': "Is your return request within the time window? Please specify: within or expired.",
                'late_return_eligible': "Are you eligible for a partial refund due to late return? Please specify: Yes or No.",
                'in_house_policy': "Does this return meet our in-house policy requirements? Please specify: Yes or No.",
                'third_party_policy': "Does the third-party seller's policy allow this refund? Please specify: Yes or No.",
                'bnpl_policy': "Does your Buy Now Pay Later provider allow refunds? Please specify: Yes or No.",
                'gift_card_policy': "Do the gift card terms allow refunds? Please specify: Yes or No."
            }
            
            return fallback_questions.get(missing_field, f"I need more information about {missing_field} to process your refund request.")
        
    def continue_conversation(self, user_response):
        """Continue the conversation with additional user input"""
        print(f"\n🔄 Continuing conversation with: '{user_response}'")
        
        # Store the conversation
        self.conversation_history.append({
            'role': 'user',
            'content': user_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Extract new information using LLM
        self._extract_information_from_input(user_response)
        
        # Navigate the decision tree again with updated information
        result = self._navigate_decision_tree_with_llm()
        
        # Store the result for question generation
        self._last_navigation_result = result
        
        if result['status'] == 'NEED_INFO':
            question = self._generate_missing_info_question()
            
            return {
                'status': 'NEED_INFO',
                'question': question,
                'stuck_at': result.get('stuck_at_node', 'unknown'),
                'missing_field': result.get('missing_field', 'unknown'),
                'context': result.get('context', '')
            }
        
        elif result['status'] == 'DECISION':
            return {
                'status': 'DECISION',
                'decision': result['decision'],
                'reason': result['reason'],
                'terminal_node': result.get('terminal_node', ''),
                'decision_path': result.get('decision_path', '')
            }
        
        else:
            return {
                'status': 'ERROR',
                'error': result.get('error', 'Unknown error occurred')
            }
    
    def reset_conversation(self):
        """Reset the conversation state"""
        self.conversation_history = []
        self.extracted_info = {}
        self.current_state = "Start"
        self._last_navigation_result = {}
    
    def get_conversation_status(self):
        """Get the current conversation status"""
        return {
            'turns': len(self.conversation_history),
            'extracted_info': self.extracted_info,
            'current_state': self.current_state,
            'customer_id': self.customer_data.get('customer_id', 'Unknown')
        }
    
    def export_conversation(self, filename=None):
        """Export conversation history to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
        
        conversation_data = {
            'customer_data': self.customer_data,
            'extracted_info': self.extracted_info,
            'conversation_history': self.conversation_history,
            'final_state': self.current_state,
            'export_timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(conversation_data, f, indent=2)
            print(f"📁 Conversation exported to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error exporting conversation: {str(e)}")
            return None