class MermaidDecisionTree:
    """
    Mermaid decision tree for refund processing
    Provides the flowchart structure for LLM navigation
    """
    
    def __init__(self):
        self.flowchart = self._create_decision_flowchart()
        self.decision_nodes = self._extract_decision_nodes()
        self.valid_keywords = self._extract_valid_keywords()
    
    def _create_decision_flowchart(self):
        """Create the complete Mermaid flowchart for refund decisions"""
        return """
        graph TD
          Start([Start])

          Start --> CustStatus{Is customer account in good standing?}
          CustStatus -- No --> RefundDenied1([Refund Denied: Account issue])
          CustStatus -- Yes --> LoyaltyTier{Customer loyalty tier?}

          LoyaltyTier -- Bronze --> ReturnHistory
          LoyaltyTier -- Silver --> ReturnHistory
          LoyaltyTier -- Gold --> FraudCheck{Is there a fraud flag on the account?}

          FraudCheck -- Yes --> RefundDenied2([Refund Denied: Fraud flag])
          FraudCheck -- No --> ReturnHistory

          ReturnHistory{Has customer abused returns?} 
          ReturnHistory -- Yes --> ManualReview([Manual Review Required])
          ReturnHistory -- No --> ItemCategory{What is the item category?}

          ItemCategory -- Perishable --> RefundDenied3([Refund Denied: Perishable items not returnable])
          ItemCategory -- Digital --> RefundDenied4([Refund Denied: Digital goods not refundable])
          ItemCategory -- Physical --> ItemEligible{Is item marked as returnable?}

          ItemEligible -- No --> RefundDenied5([Refund Denied: Non-returnable item])
          ItemEligible -- Yes --> ItemCondition{Is item damaged or defective?}

          ItemCondition -- Yes --> SellerType
          ItemCondition -- No --> ReturnWindow

          ReturnWindow{Is return request within time window?}
          ReturnWindow -- No --> ReturnLate{Eligible for partial refund due to late return?}
          ReturnWindow -- Yes --> Delivered

          ReturnLate -- No --> RefundDenied6([Refund Denied: Return window expired])
          ReturnLate -- Yes --> PartialRefund([Partial Refund Approved])

          Delivered{Has the item been delivered?}
          Delivered -- No --> ShippingIssue{Is item lost or delayed?}
          Delivered -- Yes --> SellerType

          ShippingIssue -- Lost --> RefundApprovedLost([Refund Approved: Lost in transit])
          ShippingIssue -- Delayed --> ManualReview2([Manual Review: Shipping delayed])
          ShippingIssue -- Neither --> RefundDenied7([Refund Denied: Delivery pending])

          SellerType{Is the seller third-party or in-house?}
          SellerType -- In-house --> InHousePolicy{Meets in-house return policy?}
          SellerType -- Third-party --> ThirdPartyPolicy{Third-party refund policy allows this?}

          InHousePolicy -- No --> RefundDenied8([Refund Denied: In-house policy])
          InHousePolicy -- Yes --> PaymentMethod

          ThirdPartyPolicy -- No --> RefundDenied9([Refund Denied: Third-party restriction])
          ThirdPartyPolicy -- Yes --> PaymentMethod

          PaymentMethod{Payment method used?}
          PaymentMethod -- BNPL --> BNPLPolicy{BNPL provider allows refund?}
          PaymentMethod -- CreditCard --> RefundApproved
          PaymentMethod -- Prepaid --> RefundApproved
          PaymentMethod -- GiftCard --> GiftCardPolicy{Gift card terms allow refund?}

          BNPLPolicy -- No --> RefundDenied10([Refund Denied: BNPL terms restrict refunds])
          BNPLPolicy -- Yes --> RefundApproved

          GiftCardPolicy -- No --> PartialRefund2([Partial Refund to Gift Card Balance])
          GiftCardPolicy -- Yes --> RefundApproved

          ManualReview --> FinalDecision1{Manual Review Outcome}
          FinalDecision1 -- Approve --> RefundApproved
          FinalDecision1 -- Deny --> RefundDenied11([Refund Denied after manual review])

          ManualReview2 --> FinalDecision2{Shipping Review Outcome}
          FinalDecision2 -- Approve --> RefundApproved
          FinalDecision2 -- Deny --> RefundDenied12([Refund Denied: Shipping delay insufficient])
        """
    
    def _extract_decision_nodes(self):
        """Extract decision nodes from the flowchart"""
        return [
            'CustStatus',
            'LoyaltyTier',
            'FraudCheck',
            'ReturnHistory',
            'ItemCategory',
            'ItemEligible',
            'ItemCondition',
            'ReturnWindow',
            'ReturnLate',
            'Delivered',
            'ShippingIssue',
            'SellerType',
            'InHousePolicy',
            'ThirdPartyPolicy',
            'PaymentMethod',
            'BNPLPolicy',
            'GiftCardPolicy',
            'FinalDecision1',
            'FinalDecision2'
        ]
    
    def _extract_valid_keywords(self):
        """Extract valid keywords from the Mermaid chart"""
        return {
            'account_status': ['good_standing', 'not_good_standing'],
            'loyalty_tier': ['Bronze', 'Silver', 'Gold'],
            'fraud_flag': ['Yes', 'No'],
            'return_abuse': ['Yes', 'No'],
            'item_category': ['Perishable', 'Digital', 'Physical'],
            'item_returnable': ['Yes', 'No'],
            'item_condition': ['damaged', 'defective', 'normal'],
            'return_window': ['within', 'expired'],
            'late_return_eligible': ['Yes', 'No'],
            'delivered': ['Yes', 'No'],
            'shipping_issue': ['Lost', 'Delayed', 'Neither'],
            'seller_type': ['In-house', 'Third-party'],
            'in_house_policy': ['Yes', 'No'],
            'third_party_policy': ['Yes', 'No'],
            'payment_method': ['BNPL', 'CreditCard', 'Prepaid', 'GiftCard'],
            'bnpl_policy': ['Yes', 'No'],
            'gift_card_policy': ['Yes', 'No'],
            'manual_review_outcome': ['Approve', 'Deny'],
            'shipping_review_outcome': ['Approve', 'Deny']
        }
    
    def get_refund_decision_flowchart(self):
        """Return the complete flowchart"""
        return self.flowchart
    
    def get_decision_nodes(self):
        """Return list of decision nodes"""
        return self.decision_nodes
    
    def get_valid_keywords(self):
        """Return valid keywords for each field"""
        return self.valid_keywords
    
    def get_terminal_nodes(self):
        """Return terminal decision nodes"""
        return [
            'RefundDenied1', 'RefundDenied2', 'RefundDenied3', 'RefundDenied4',
            'RefundDenied5', 'RefundDenied6', 'RefundDenied7', 'RefundDenied8',
            'RefundDenied9', 'RefundDenied10', 'RefundDenied11', 'RefundDenied12',
            'RefundApproved', 'RefundApprovedLost', 'PartialRefund', 'PartialRefund2',
            'ManualReview', 'ManualReview2'
        ]
    
    def get_decision_paths(self):
        """Return all possible decision paths"""
        return {
            'account_issue': ['Start', 'CustStatus', 'RefundDenied1'],
            'fraud_flag': ['Start', 'CustStatus', 'LoyaltyTier', 'FraudCheck', 'RefundDenied2'],
            'return_abuse': ['Start', 'CustStatus', 'LoyaltyTier', 'ReturnHistory', 'ManualReview'],
            'perishable': ['Start', 'CustStatus', 'LoyaltyTier', 'ReturnHistory', 'ItemCategory', 'RefundDenied3'],
            'digital': ['Start', 'CustStatus', 'LoyaltyTier', 'ReturnHistory', 'ItemCategory', 'RefundDenied4'],
            'non_returnable': ['Start', 'CustStatus', 'LoyaltyTier', 'ReturnHistory', 'ItemCategory', 'ItemEligible', 'RefundDenied5'],
            'approved': ['Start', 'CustStatus', 'LoyaltyTier', 'ReturnHistory', 'ItemCategory', 'ItemEligible', 'ItemCondition', 'ReturnWindow', 'Delivered', 'SellerType', 'InHousePolicy', 'PaymentMethod', 'RefundApproved']
        }
    
    def validate_decision_path(self, path):
        """Validate if a decision path is valid"""
        valid_paths = self.get_decision_paths()
        return path in valid_paths.values()